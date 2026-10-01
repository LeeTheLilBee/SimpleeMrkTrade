"""Soulaana bounded autonomous market-research loop for the hosted Dashboard.

The loop never invents symbols or trades. It uses the existing OB discovery universe
as a candidate pool, requests one bounded batch of Alpaca IEX snapshots, ranks only
*research attention* (not investment merit), and returns a compact source-backed
Dashboard projection.

Credential precedence:
1) current Tower session's temporary verified Alpaca pair
2) hosted environment secret pair for continuous operation across restarts

No credential is serialized into JSON, logs, HTML, or browser storage.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite, log10
import json
import os
from threading import RLock
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from engine.universe import get_universe

BASE = "https://data.alpaca.markets"
MAX_RESPONSE = 2_000_000
MAX_SYMBOLS = 60
CACHE_SECONDS = 45


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class HostedAlpacaCredential:
    key_id: str
    value: str
    probe: str = "HOSTED_ENV_CONFIGURED"


_lock = RLock()
_cache: dict[str, tuple[datetime, dict]] = {}


def _now():
    return datetime.now(timezone.utc)


def _credential_from_env():
    key_id = (os.environ.get("OB_ALPACA_API_KEY_ID") or "").strip()
    secret = (os.environ.get("OB_ALPACA_API_SECRET_KEY") or "").strip()
    if not key_id or not secret:
        return None
    return HostedAlpacaCredential(key_id=key_id, value=secret)


def resolve_credential(*, sid, temp_reader):
    item = None
    if isinstance(sid, str) and sid and callable(temp_reader):
        try:
            item = temp_reader(sid, "alpaca")
        except Exception:
            item = None
    if item is not None and getattr(item, "probe", None) == "READ_ONLY_CHECK_PASSED":
        return item, "TEMPORARY_TOWER_SESSION"
    hosted = _credential_from_env()
    if hosted is not None:
        return hosted, "HOSTED_ENV_SECRET"
    return None, "NOT_CONFIGURED"


def _headers(item):
    key_id = getattr(item, "key_id", None)
    secret = getattr(item, "value", None)
    if not isinstance(key_id, str) or not key_id or not isinstance(secret, str) or not secret:
        raise ValueError("ALPACA_CREDENTIAL_HOLD")
    return {
        "APCA-API-KEY-ID": key_id,
        "APCA-API-SECRET-KEY": secret,
        "Accept": "application/json",
    }


def _read_snapshots(symbols, *, item, opener=None):
    opener = opener or build_opener(_NoRedirect())
    symbols = [str(s).strip().upper() for s in symbols if str(s).strip()][:MAX_SYMBOLS]
    if not symbols:
        raise ValueError("ALPACA_SYMBOL_SET_HOLD")
    url = BASE + "/v2/stocks/snapshots?" + urlencode({
        "symbols": ",".join(symbols),
        "feed": "iex",
    })
    req = Request(url, headers=_headers(item), method="GET")
    try:
        with opener.open(req, timeout=10) as response:
            if response.status != 200 or response.geturl() != url:
                raise ValueError("ALPACA_RESPONSE_HOLD")
            raw = response.read(MAX_RESPONSE + 1)
    except HTTPError as exc:
        if exc.code == 401:
            raise ValueError("ALPACA_AUTH_REJECTED") from None
        if exc.code == 403:
            raise ValueError("ALPACA_ENTITLEMENT_HOLD") from None
        if exc.code == 429:
            raise ValueError("ALPACA_RATE_LIMITED") from None
        raise ValueError("ALPACA_PROVIDER_HOLD") from None
    except (URLError, OSError, TimeoutError):
        raise ValueError("ALPACA_NETWORK_HOLD") from None
    if len(raw) > MAX_RESPONSE:
        raise ValueError("ALPACA_RESPONSE_TOO_LARGE")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise ValueError("ALPACA_RESPONSE_PARSE_HOLD") from None
    if not isinstance(payload, dict):
        raise ValueError("ALPACA_RESPONSE_SHAPE_HOLD")
    return payload


def _num(value):
    if isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return out if isfinite(out) else None


def _score(symbol, snap):
    if not isinstance(snap, dict):
        return None
    quote = snap.get("latestQuote")
    daily = snap.get("dailyBar")
    prev = snap.get("prevDailyBar")
    minute = snap.get("minuteBar")
    if not all(isinstance(x, dict) for x in (quote, daily, prev, minute)):
        return None

    bid, ask = _num(quote.get("bp")), _num(quote.get("ap"))
    day_close, prev_close = _num(daily.get("c")), _num(prev.get("c"))
    day_open, day_high, day_low = _num(daily.get("o")), _num(daily.get("h")), _num(daily.get("l"))
    volume = _num(daily.get("v"))
    minute_close = _num(minute.get("c"))
    observed_at = quote.get("t") or minute.get("t") or daily.get("t")

    if not observed_at or not all(v is not None and v > 0 for v in (day_close, prev_close, day_open)):
        return None
    move_pct = (day_close / prev_close - 1.0) * 100.0
    intraday_pct = (day_close / day_open - 1.0) * 100.0

    spread_pct = None
    midpoint = None
    if bid and ask and bid > 0 and ask >= bid:
        midpoint = (bid + ask) / 2.0
        spread_pct = ((ask - bid) / midpoint) * 100.0 if midpoint else None

    # Attention score means "worth investigating", never "good investment".
    liquidity_component = log10(max(volume or 0.0, 1.0))
    spread_penalty = min(spread_pct or 3.0, 3.0)
    attention_score = abs(move_pct) * 2.0 + abs(intraday_pct) + liquidity_component - spread_penalty

    reasons = []
    if abs(move_pct) >= 2:
        reasons.append(f"session move {move_pct:+.2f}% vs prior close")
    if abs(intraday_pct) >= 1:
        reasons.append(f"intraday move {intraday_pct:+.2f}%")
    if volume is not None:
        reasons.append(f"IEX daily volume {int(volume):,}")
    if spread_pct is not None:
        reasons.append(f"IEX spread {spread_pct:.3f}%")

    return {
        "symbol": symbol,
        "source": "Alpaca IEX",
        "observed_at": observed_at,
        "daily_close": day_close,
        "previous_close": prev_close,
        "minute_close": minute_close,
        "bid": bid,
        "ask": ask,
        "midpoint": midpoint,
        "daily_high": day_high,
        "daily_low": day_low,
        "daily_volume": int(volume) if volume is not None and volume >= 0 else None,
        "move_pct": round(move_pct, 4),
        "intraday_pct": round(intraday_pct, 4),
        "spread_pct": round(spread_pct, 5) if spread_pct is not None else None,
        "attention_score": round(attention_score, 6),
        "research_reasons": reasons[:4],
    }


def _build_projection(rows, *, credential_source):
    now = _now()
    ranked = sorted(rows, key=lambda x: (-x["attention_score"], x["symbol"]))
    leaders = ranked[:6]
    glance = leaders[:3]
    source_times = [row["observed_at"] for row in leaders if row.get("observed_at")]

    warnings = [
        f"{row['symbol']} research attention · " + "; ".join(row["research_reasons"][:2])
        for row in leaders[:3]
    ]

    return {
        "version": "OBDATA011_SOULAANA_AUTONOMOUS_ALPACA_RESEARCH",
        "projection_status": "fresh",
        "market_data_state": "source_bound_research_scan",
        "source": "alpaca-iex-owner-development",
        "as_of": now.isoformat(),
        "source_observed_at": source_times,
        "source_identified": True,
        "timestamp_identified": True,
        "current_eligible": True,
        "display_eligible": True,
        "reason": (
            "Soulaana requested a bounded Alpaca IEX snapshot across OB's discovery universe "
            "and ranked research attention. Ranking is for investigation only, not a buy/sell recommendation."
        ),
        "market_health": {
            "state": "SOURCE_BOUND_RESEARCH",
            "label": "Alpaca IEX research scan",
            "symbols_checked": len(rows),
            "attention_symbols": len(leaders),
            "credential_source": credential_source,
            "coverage": "IEX venue-limited",
            "consolidated_nbbo": False,
        },
        "sectors": [],
        "symbols": [
            {
                "symbol": row["symbol"],
                "source": "Alpaca IEX",
                "observed_at": row["observed_at"],
                "move_pct": row["move_pct"],
                "attention_score": row["attention_score"],
                "research_reasons": row["research_reasons"],
            }
            for row in glance
        ],
        "signals": [],
        "watchlist": [row["symbol"] for row in leaders],
        "options": [],
        "options_projection": {},
        "research_contracts": [],
        "ranked_contracts": [],
        "positions": [],
        "positions_preview": [],
        "candidates": [],
        "candidates_preview": [],
        "manual_live_queue": [],
        "review_summary": {
            "count": len(leaders),
            "kind": "RESEARCH_ATTENTION",
            "items": [
                {"symbol": row["symbol"], "reasons": row["research_reasons"]}
                for row in leaders
            ],
        },
        "warnings": warnings,
        "soulaana": {
            "headline": (
                f"I checked {len(rows)} symbols and found {len(leaders)} worth a closer research look."
                if rows else "I could not establish a source-backed research scan."
            ),
            "meaning": (
                "These symbols moved to the front because of source-observed movement, liquidity "
                "and quote quality. That is attention, not a trade instruction."
            ),
            "next_step": (
                "Open a symbol to combine price context with filings, catalysts, macro context and options evidence."
            ),
        },
        "provider_boundary": {
            "authorized_feed_connected": True,
            "historical_seed_universe_quarantined_as_price_source": True,
            "discovery_universe_only": True,
            "iex_venue_limited": True,
            "sip_nbbo": False,
            "personal_owner_development_only": True,
            "commercial_redistribution_authorized": False,
            "status_only": False,
        },
        "tower_boundaries": {
            "private_beta_only": True,
            "no_broker_api": True,
            "no_order_submission": True,
            "no_capital_movement": True,
            "no_auto_execution": True,
            "live_auto_locked": True,
        },
    }


def autonomous_dashboard_projection(*, sid, temp_reader, opener=None, now=None):
    now = now or _now()
    cache_key = sid if isinstance(sid, str) and sid else "hosted"
    with _lock:
        cached = _cache.get(cache_key)
        if cached and (now - cached[0]).total_seconds() < CACHE_SECONDS:
            return cached[1]

    item, credential_source = resolve_credential(sid=sid, temp_reader=temp_reader)
    if item is None:
        raise ValueError("ALPACA_NOT_CONFIGURED")

    universe = [s for s in get_universe() if isinstance(s, str)][:MAX_SYMBOLS]
    snapshots = _read_snapshots(universe, item=item, opener=opener)
    rows = []
    for symbol in universe:
        row = _score(symbol, snapshots.get(symbol))
        if row is not None:
            rows.append(row)
    if not rows:
        raise ValueError("ALPACA_NO_SOURCE_BOUND_ROWS")

    projection = _build_projection(rows, credential_source=credential_source)
    with _lock:
        _cache[cache_key] = (now, projection)
    return projection
