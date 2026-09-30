"""Normalized internal event bus for Observatory market/intelligence invalidations.

This is the nervous-system layer, not a market-data entitlement or quote feed.
Producers publish only that protected authoritative state changed. Consumers must
re-read the exact Tower-protected snapshot route before using any data.

Native provider WebSockets may be bridged here later only after separate source,
commercial-use, display, retention and streaming-entitlement review. Until then
this hub carries no provider payload, quote value, option chain, order or capital
authority.
"""
from __future__ import annotations

import asyncio
from collections import deque
import re
import secrets
from threading import RLock

PATH = "/ob/market/stream"
SCHEMA = "OB_MARKET_STREAM_EVENT_V1"

_EVENT_TYPES = frozenset({
    "research_context_changed",
    "source_status_changed",
    "market_snapshot_changed",
    "scanner_context_changed",
    "candidate_context_changed",
})
_CHANNELS = {
    "research_context_changed": "research",
    "source_status_changed": "system",
    "market_snapshot_changed": "market",
    "scanner_context_changed": "scanner",
    "candidate_context_changed": "candidate",
}
_SNAPSHOT_PATHS = frozenset({
    "/ob/research/catalysts.json",
    "/ob/research/keyless.json",
    "/ob/research/providers.json",
    "/ob/data-desk/connections.json",
    "/ob/engine-feed-snapshot.json",
})
_SOURCE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")
_SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")


class MarketStreamHub:
    """Bounded process-local invalidation bus with cursor/replay semantics."""

    def __init__(self, *, history=128, client_budget=8, queue_size=16):
        if (
            type(history) is not int or not 8 <= history <= 256
            or type(client_budget) is not int or not 1 <= client_budget <= 16
            or type(queue_size) is not int or not 2 <= queue_size <= 64
        ):
            raise ValueError("bounded market stream budgets required")
        self.epoch = secrets.token_hex(12)
        self._lock = RLock()
        self._events = deque(maxlen=history)
        self._latest = 0
        self._clients = {}
        self.client_budget = client_budget
        self.queue_size = queue_size

    def hint(self, *, available=False):
        with self._lock:
            return {
                "schema": "OB_MARKET_STREAM_HINT_V1",
                "available": available is True,
                "path": PATH,
                "epoch": self.epoch,
                "cursor": self._latest,
                "normalized_invalidation_only": True,
                "provider_payload_attached": False,
                "live_quote_payload_attached": False,
                "broker_execution_authorized": False,
            }

    def publish_invalidation(
        self,
        *,
        event_type,
        source,
        snapshot_path,
        symbol=None,
    ):
        if event_type not in _EVENT_TYPES:
            raise ValueError("MARKET_STREAM_EVENT_TYPE_HOLD")
        if not isinstance(source, str) or not _SOURCE.fullmatch(source):
            raise ValueError("MARKET_STREAM_SOURCE_HOLD")
        if snapshot_path not in _SNAPSHOT_PATHS:
            raise ValueError("MARKET_STREAM_SNAPSHOT_PATH_HOLD")
        if symbol is not None:
            if not isinstance(symbol, str):
                raise ValueError("MARKET_STREAM_SYMBOL_HOLD")
            symbol = symbol.strip().upper()
            if not _SYMBOL.fullmatch(symbol) or ".." in symbol:
                raise ValueError("MARKET_STREAM_SYMBOL_HOLD")

        with self._lock:
            self._latest += 1
            event = {
                "schema": SCHEMA,
                "type": event_type,
                "channel": _CHANNELS[event_type],
                "epoch": self.epoch,
                "cursor": self._latest,
                "source": source,
                "symbol": symbol,
                "snapshot_path": snapshot_path,
                "needs_authenticated_snapshot": True,
                "content_attached": False,
                "provider_payload_attached": False,
                "provider_stream_attached": False,
                "live_quote_payload_attached": False,
                "current_quote_verified": False,
                "candidate_admitted": False,
                "execution_authorized": False,
            }
            self._events.append(event)
            for key, (loop, queue) in tuple(self._clients.items()):
                def deliver(q=queue):
                    if q.full():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                        q.put_nowait(self._resync())
                    else:
                        q.put_nowait(dict(event))
                try:
                    loop.call_soon_threadsafe(deliver)
                except RuntimeError:
                    self._clients.pop(key, None)
            return dict(event)

    def subscribe(self, *, epoch, cursor, loop):
        if not isinstance(epoch, str) or not isinstance(cursor, int) or cursor < 0:
            raise ValueError("MARKET_STREAM_CURSOR_HOLD")
        with self._lock:
            if len(self._clients) >= self.client_budget:
                raise ValueError("MARKET_STREAM_CLIENT_BUDGET_HOLD")
            queue = asyncio.Queue(maxsize=self.queue_size)
            key = secrets.token_hex(10)
            if epoch != self.epoch or cursor > self._latest:
                replay = [self._resync()]
            elif not self._events:
                replay = []
            elif cursor < self._events[0]["cursor"] - 1:
                replay = [self._resync()]
            else:
                replay = [dict(x) for x in self._events if x["cursor"] > cursor]
            self._clients[key] = (loop, queue)
            return key, queue, replay, self.hint()

    def unsubscribe(self, key):
        with self._lock:
            self._clients.pop(key, None)

    def _resync(self):
        return {
            "schema": SCHEMA,
            "type": "resync_required",
            "channel": "system",
            "epoch": self.epoch,
            "cursor": self._latest,
            "source": "market_stream_hub",
            "symbol": None,
            "snapshot_path": None,
            "needs_authenticated_snapshot": True,
            "content_attached": False,
            "provider_payload_attached": False,
            "provider_stream_attached": False,
            "live_quote_payload_attached": False,
            "current_quote_verified": False,
            "candidate_admitted": False,
            "execution_authorized": False,
        }
