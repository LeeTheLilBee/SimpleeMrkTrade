"""Persistent Alpaca IEX WebSocket intake for owner-development OB.

Server-side only. The stream carries read-only market data into a bounded
in-memory cache and publishes Observatory invalidations. It grants no broker,
order, capital, candidate-admission, or trading-mode authority.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from threading import RLock, Thread

import websockets

ENDPOINT = "wss://stream.data.alpaca.markets/v2/iex"
SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")
MAX_SYMBOLS = 24
MAX_EVENTS_PER_SYMBOL = 12


def _now():
    return datetime.now(timezone.utc)


def _safe_symbols(symbols):
    out = []
    for raw in symbols or ():
        symbol = str(raw or "").strip().upper()
        if SYMBOL.fullmatch(symbol) and ".." not in symbol and symbol not in out:
            out.append(symbol)
        if len(out) >= MAX_SYMBOLS:
            break
    if not out:
        raise ValueError("ALPACA_STREAM_SYMBOL_HOLD")
    return tuple(out)


class AlpacaIEXStreamManager:
    def __init__(self):
        self._lock = RLock()
        self._thread = None
        self._stop = None
        self._sid = None
        self._credential = None
        self._symbols = tuple()
        self._active_symbols = tuple()
        self._state = "IDLE"
        self._last_event_at = None
        self._last_error = None
        self._events = {}
        self._hub = None

    def ensure(self, *, sid, credential, symbols, hub=None):
        if not isinstance(sid, str) or not sid.startswith("tower_session_"):
            raise ValueError("ALPACA_STREAM_OWNER_SESSION_HOLD")
        key_id = getattr(credential, "key_id", None)
        secret = getattr(credential, "value", None)
        probe = getattr(credential, "probe", None)
        if probe not in {"READ_ONLY_CHECK_PASSED", "HOSTED_ENV_CONFIGURED"}:
            raise ValueError("ALPACA_STREAM_CREDENTIAL_HOLD")
        if not isinstance(key_id, str) or not key_id or not isinstance(secret, str) or not secret:
            raise ValueError("ALPACA_STREAM_CREDENTIAL_HOLD")
        wanted = _safe_symbols(symbols)
        with self._lock:
            same_session = self._sid == sid
            self._sid = sid
            self._credential = (key_id, secret)
            self._symbols = wanted
            self._hub = hub
            thread_alive = self._thread is not None and self._thread.is_alive()
            if same_session and thread_alive:
                return self.status()
            if thread_alive and self._stop is not None:
                self._stop.set()
            self._stop = asyncio.Event()
            self._state = "STARTING"
            self._last_error = None
            self._thread = Thread(target=self._thread_main, name="ob-alpaca-iex-stream", daemon=True)
            self._thread.start()
            return self.status()

    def stop(self):
        with self._lock:
            if self._stop is not None:
                try:
                    self._stop.set()
                except Exception:
                    pass
            self._credential = None
            self._sid = None
            self._symbols = tuple()
            self._active_symbols = tuple()
            self._state = "STOPPED"

    def status(self):
        with self._lock:
            return {
                "schema": "OB_ALPACA_IEX_STREAM_STATUS_V1",
                "state": self._state,
                "endpoint": ENDPOINT,
                "symbols_requested": list(self._symbols),
                "symbols_active": list(self._active_symbols),
                "last_event_at": self._last_event_at,
                "last_error": self._last_error,
                "read_only": True,
                "provider_payload_exposed_to_browser": False,
                "broker_execution_authorized": False,
                "capital_authorized": False,
                "candidate_admitted": False,
                "may_change_trading_mode": False,
            }

    def snapshot(self, symbols=None):
        wanted = set(_safe_symbols(symbols)) if symbols else None
        with self._lock:
            rows = {}
            for symbol, bucket in self._events.items():
                if wanted is not None and symbol not in wanted:
                    continue
                rows[symbol] = {
                    kind: dict(value)
                    for kind, value in bucket.items()
                    if isinstance(value, dict)
                }
            return rows

    def _thread_main(self):
        try:
            asyncio.run(self._run())
        except Exception:
            with self._lock:
                self._state = "HOLD"
                self._last_error = "STREAM_RUNTIME_HOLD"

    async def _run(self):
        backoff = 1
        while True:
            with self._lock:
                stop = self._stop
                cred = self._credential
            if stop is None or stop.is_set() or cred is None:
                return
            try:
                async with websockets.connect(
                    ENDPOINT,
                    open_timeout=8,
                    close_timeout=4,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=1_000_000,
                ) as ws:
                    await ws.send(json.dumps({
                        "action": "auth",
                        "key": cred[0],
                        "secret": cred[1],
                    }, separators=(",", ":")))
                    auth = json.loads(await asyncio.wait_for(ws.recv(), timeout=8))
                    if not self._auth_ok(auth):
                        raise ValueError("ALPACA_STREAM_AUTH_HOLD")
                    await self._sync_subscriptions(ws, force=True)
                    with self._lock:
                        self._state = "STREAMING"
                        self._last_error = None
                    backoff = 1

                    while not stop.is_set():
                        await self._sync_subscriptions(ws)
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=2)
                        except asyncio.TimeoutError:
                            continue
                        self._ingest(raw)
            except Exception:
                with self._lock:
                    if stop.is_set():
                        return
                    self._state = "RECONNECTING"
                    self._last_error = "PROVIDER_STREAM_HOLD"
                await asyncio.sleep(min(backoff, 15))
                backoff = min(backoff * 2, 15)

    def _auth_ok(self, payload):
        if not isinstance(payload, list):
            return False
        for item in payload:
            if isinstance(item, dict) and item.get("T") == "success" and item.get("msg") == "authenticated":
                return True
        return False

    async def _sync_subscriptions(self, ws, force=False):
        with self._lock:
            wanted = self._symbols
            active = self._active_symbols
        if not force and wanted == active:
            return
        remove = [x for x in active if x not in wanted]
        add = [x for x in wanted if x not in active]
        if force:
            add = list(wanted)
            remove = []
        if remove:
            await ws.send(json.dumps({
                "action": "unsubscribe",
                "trades": remove,
                "quotes": remove,
                "bars": remove,
            }, separators=(",", ":")))
        if add:
            await ws.send(json.dumps({
                "action": "subscribe",
                "trades": add,
                "quotes": add,
                "bars": add,
            }, separators=(",", ":")))
        with self._lock:
            self._active_symbols = wanted

    def _ingest(self, raw):
        if not isinstance(raw, str) or len(raw) > 1_000_000:
            return
        try:
            payload = json.loads(raw)
        except ValueError:
            return
        if not isinstance(payload, list):
            return
        for event in payload[:128]:
            if not isinstance(event, dict):
                continue
            kind = event.get("T")
            symbol = str(event.get("S") or "").strip().upper()
            if kind not in {"t", "q", "b"} or not SYMBOL.fullmatch(symbol) or ".." in symbol:
                continue
            normalized = self._normalize(kind, symbol, event)
            digest = sha256(
                json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            with self._lock:
                bucket = self._events.setdefault(symbol, {})
                bucket[kind] = normalized
                if len(self._events) > MAX_SYMBOLS:
                    for stale in list(self._events)[:-MAX_SYMBOLS]:
                        self._events.pop(stale, None)
                self._last_event_at = normalized["timestamp"]
                hub = self._hub
            if hub is not None:
                try:
                    hub.observe_digest(
                        observation_key=f"alpaca_stream:{symbol}:{kind}",
                        digest=digest,
                        event_type="market_snapshot_changed",
                        source="alpaca_iex_stream",
                        snapshot_path="/ob/engine-feed-snapshot.json",
                        symbol=symbol,
                    )
                except Exception:
                    pass

    def _normalize(self, kind, symbol, event):
        ts = event.get("t") if isinstance(event.get("t"), str) else _now().isoformat()
        base = {
            "provider": "alpaca",
            "feed": "iex",
            "event_type": {"t": "trade", "q": "quote", "b": "bar"}[kind],
            "symbol": symbol,
            "timestamp": ts,
            "received_at": _now().isoformat(),
            "execution_grade_quote": False,
            "candidate_admitted": False,
            "broker_execution_authorized": False,
        }
        if kind == "t":
            base.update({"price": event.get("p"), "size": event.get("s")})
        elif kind == "q":
            bp, ap = event.get("bp"), event.get("ap")
            midpoint = None
            if isinstance(bp, (int, float)) and isinstance(ap, (int, float)) and bp > 0 and ap > 0:
                midpoint = (float(bp) + float(ap)) / 2.0
            base.update({
                "bid": bp,
                "bid_size": event.get("bs"),
                "ask": ap,
                "ask_size": event.get("as"),
                "midpoint": midpoint,
            })
        else:
            base.update({
                "open": event.get("o"),
                "high": event.get("h"),
                "low": event.get("l"),
                "close": event.get("c"),
                "volume": event.get("v"),
                "trade_count": event.get("n"),
                "vwap": event.get("vw"),
            })
        return base


_MANAGER = AlpacaIEXStreamManager()


def stream_manager():
    return _MANAGER
