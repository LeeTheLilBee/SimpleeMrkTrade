"""Single process-local event bus for The Observatory.

The event socket is a notification/coordination layer only. It never becomes a
market-data entitlement, source of truth, broker route, scanner authority or
capital authority. Data-bearing consumers re-read an exact protected Tower
snapshot after an event.

The hub also keeps a bounded, content-free lifecycle ledger. That ledger proves
which internal stages actually happened without copying provider values,
credentials, positions or order data into the event transport.
"""
from __future__ import annotations

import asyncio
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
import re
import secrets
from threading import RLock

PATH = "/ob/events/stream"
EVENT_SCHEMA = "OB_EVENT_STREAM_EVENT_V1"
HINT_SCHEMA = "OB_EVENT_STREAM_HINT_V1"
TRACE_SCHEMA = "OB_EVENT_TRACE_V1"

TRACE_STAGES = (
    "RECEIVED",
    "VALIDATED",
    "NORMALIZED",
    "PUBLISHED",
    "SCANNER_CONSUMED",
    "SIMULATION_CONSUMED",
    "SOULAANA_CONSUMED",
    "SOULAANA_INTERPRETED",
)
_PRODUCER_STAGES = TRACE_STAGES[:3]
_CONSUMER_STAGES = frozenset(TRACE_STAGES[4:])

_EVENT_CHANNELS = {
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
_OBSERVATION_KEY = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,95}$")
_SYMBOL = re.compile(r"^[A-Z][A-Z0-9.-]{0,15}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_CONSUMER = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,95}$")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


class ObservatoryEventHub:
    """Bounded single-worker event/replay bus for all OB internal changes."""

    def __init__(self, *, history=128, client_budget=8, queue_size=16):
        if (
            type(history) is not int or not 8 <= history <= 256
            or type(client_budget) is not int or not 1 <= client_budget <= 16
            or type(queue_size) is not int or not 2 <= queue_size <= 64
        ):
            raise ValueError("bounded Observatory event budgets required")
        self.epoch = secrets.token_hex(12)
        self._lock = RLock()
        self._events = deque(maxlen=history)
        self._latest = 0
        self._observed_digests = {}
        self._clients = {}
        self._revoked_sessions = set()
        self._trace_order = deque(maxlen=history)
        self._traces = {}
        self.client_budget = client_budget
        self.queue_size = queue_size

    def hint(self, *, available=False):
        with self._lock:
            return {
                "schema": HINT_SCHEMA,
                "available": available is True,
                "path": PATH,
                "epoch": self.epoch,
                "cursor": self._latest,
                "invalidation_only": True,
                "content_attached": False,
                "provider_payload_attached": False,
                "provider_stream_attached": False,
                "live_quote_payload_attached": False,
                "broker_execution_authorized": False,
            }

    def observe_digest(
        self,
        *,
        observation_key,
        digest,
        event_type,
        source,
        snapshot_path,
        symbol=None,
        producer_stages=(),
    ):
        """Publish once when a validated producer's deterministic digest changes."""
        self.observe_digest_event(
            observation_key=observation_key,
            digest=digest,
            event_type=event_type,
            source=source,
            snapshot_path=snapshot_path,
            symbol=symbol,
            producer_stages=producer_stages,
        )
        return self.hint()

    def observe_digest_event(
        self,
        *,
        observation_key,
        digest,
        event_type,
        source,
        snapshot_path,
        symbol=None,
        producer_stages=(),
    ):
        """Return the newly published event, or None when content is unchanged."""
        if (
            not isinstance(observation_key, str)
            or not _OBSERVATION_KEY.fullmatch(observation_key)
            or not isinstance(digest, str)
            or not _DIGEST.fullmatch(digest)
        ):
            raise ValueError("OBSERVATORY_EVENT_OBSERVATION_HOLD")
        producer_stages = self._validate_producer_stages(producer_stages)
        with self._lock:
            if self._observed_digests.get(observation_key) == digest:
                return None
            self._observed_digests[observation_key] = digest
        return self.publish_invalidation(
            event_type=event_type,
            source=source,
            snapshot_path=snapshot_path,
            symbol=symbol,
            producer_stages=producer_stages,
        )

    def publish_invalidation(
        self,
        *,
        event_type,
        source,
        snapshot_path,
        symbol=None,
        producer_stages=(),
    ):
        if event_type not in _EVENT_CHANNELS:
            raise ValueError("OBSERVATORY_EVENT_TYPE_HOLD")
        if not isinstance(source, str) or not _SOURCE.fullmatch(source):
            raise ValueError("OBSERVATORY_EVENT_SOURCE_HOLD")
        if snapshot_path not in _SNAPSHOT_PATHS:
            raise ValueError("OBSERVATORY_EVENT_SNAPSHOT_PATH_HOLD")
        producer_stages = self._validate_producer_stages(producer_stages)
        if symbol is not None:
            if not isinstance(symbol, str):
                raise ValueError("OBSERVATORY_EVENT_SYMBOL_HOLD")
            symbol = symbol.strip().upper()
            if not _SYMBOL.fullmatch(symbol) or ".." in symbol:
                raise ValueError("OBSERVATORY_EVENT_SYMBOL_HOLD")

        with self._lock:
            self._latest += 1
            event_id = f"{self.epoch}.{self._latest}"
            event = {
                "schema": EVENT_SCHEMA,
                "event_id": event_id,
                "type": event_type,
                "channel": _EVENT_CHANNELS[event_type],
                "epoch": self.epoch,
                "cursor": self._latest,
                "source": source,
                "symbol": symbol,
                "snapshot_path": snapshot_path,
                "needs_authenticated_snapshot": True,
                "trace_available": True,
                "content_attached": False,
                "provider_payload_attached": False,
                "provider_stream_attached": False,
                "live_quote_payload_attached": False,
                "current_quote_verified": False,
                "candidate_admitted": False,
                "execution_authorized": False,
            }
            self._events.append(event)
            self._begin_trace(event, producer_stages)
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

    def record_lifecycle(self, *, event_id, stage, consumer):
        """Record proof that one named internal consumer actually handled an event."""
        if stage not in _CONSUMER_STAGES:
            raise ValueError("OBSERVATORY_EVENT_TRACE_STAGE_HOLD")
        if not isinstance(consumer, str) or not _CONSUMER.fullmatch(consumer):
            raise ValueError("OBSERVATORY_EVENT_TRACE_CONSUMER_HOLD")
        with self._lock:
            trace = self._traces.get(event_id)
            if trace is None:
                raise ValueError("OBSERVATORY_EVENT_TRACE_EVENT_HOLD")
            if stage == "SOULAANA_INTERPRETED" and not trace["stages"]["SOULAANA_CONSUMED"]:
                raise ValueError("OBSERVATORY_EVENT_TRACE_ORDER_HOLD")
            self._mark_trace(trace, stage, consumer)
            return self._copy_trace(trace)

    def trace_snapshot(self, *, event_id=None, limit=24):
        """Return bounded status-only lifecycle proof; never source/provider content."""
        if type(limit) is not int or not 1 <= limit <= 64:
            raise ValueError("OBSERVATORY_EVENT_TRACE_LIMIT_HOLD")
        with self._lock:
            if event_id is not None:
                trace = self._traces.get(event_id)
                if trace is None:
                    raise ValueError("OBSERVATORY_EVENT_TRACE_EVENT_HOLD")
                traces = [self._copy_trace(trace)]
            else:
                ids = list(self._trace_order)[-limit:]
                traces = [self._copy_trace(self._traces[key]) for key in ids if key in self._traces]
            return {
                "schema": TRACE_SCHEMA,
                "epoch": self.epoch,
                "latest_cursor": self._latest,
                "traces": traces,
                "content_attached": False,
                "provider_payload_attached": False,
                "credentials_attached": False,
                "positions_attached": False,
                "orders_attached": False,
                "execution_authorized": False,
            }

    def subscribe(self, *, epoch, cursor, loop):
        if not isinstance(epoch, str) or not isinstance(cursor, int) or cursor < 0:
            raise ValueError("OBSERVATORY_EVENT_CURSOR_HOLD")
        with self._lock:
            if len(self._clients) >= self.client_budget:
                raise ValueError("OBSERVATORY_EVENT_CLIENT_BUDGET_HOLD")
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

    def revoke_session(self, tower_session_id):
        if not isinstance(tower_session_id, str) or not tower_session_id:
            return
        digest = sha256(tower_session_id.encode("utf-8")).hexdigest()
        with self._lock:
            self._revoked_sessions.add(digest)

    def session_revoked(self, tower_session_id):
        if not isinstance(tower_session_id, str) or not tower_session_id:
            return True
        digest = sha256(tower_session_id.encode("utf-8")).hexdigest()
        with self._lock:
            return digest in self._revoked_sessions

    def _validate_producer_stages(self, stages):
        if not isinstance(stages, (tuple, list)):
            raise ValueError("OBSERVATORY_EVENT_TRACE_STAGE_HOLD")
        stages = tuple(stages)
        if len(stages) > len(_PRODUCER_STAGES):
            raise ValueError("OBSERVATORY_EVENT_TRACE_STAGE_HOLD")
        if stages != _PRODUCER_STAGES[:len(stages)]:
            raise ValueError("OBSERVATORY_EVENT_TRACE_ORDER_HOLD")
        return stages

    def _begin_trace(self, event, producer_stages):
        if len(self._trace_order) == self._trace_order.maxlen:
            stale = self._trace_order[0]
            self._traces.pop(stale, None)
        trace = {
            "schema": TRACE_SCHEMA,
            "event_id": event["event_id"],
            "event_type": event["type"],
            "source": event["source"],
            "symbol": event["symbol"],
            "snapshot_path": event["snapshot_path"],
            "stages": {stage: False for stage in TRACE_STAGES},
            "receipts": [],
            "soulaana_complete": False,
        }
        for stage in producer_stages:
            self._mark_trace(trace, stage, "producer")
        self._mark_trace(trace, "PUBLISHED", "observatory_event_hub")
        self._trace_order.append(event["event_id"])
        self._traces[event["event_id"]] = trace

    def _mark_trace(self, trace, stage, consumer):
        if trace["stages"][stage]:
            return
        trace["stages"][stage] = True
        trace["receipts"].append({
            "stage": stage,
            "consumer": consumer,
            "observed_at": _now_iso(),
        })
        if len(trace["receipts"]) > 16:
            trace["receipts"] = trace["receipts"][-16:]
        trace["soulaana_complete"] = (
            trace["stages"]["SOULAANA_CONSUMED"]
            and trace["stages"]["SOULAANA_INTERPRETED"]
        )

    @staticmethod
    def _copy_trace(trace):
        return {
            "schema": trace["schema"],
            "event_id": trace["event_id"],
            "event_type": trace["event_type"],
            "source": trace["source"],
            "symbol": trace["symbol"],
            "snapshot_path": trace["snapshot_path"],
            "stages": dict(trace["stages"]),
            "receipts": [dict(row) for row in trace["receipts"]],
            "soulaana_complete": trace["soulaana_complete"],
        }

    def _resync(self):
        return {
            "schema": EVENT_SCHEMA,
            "type": "resync_required",
            "channel": "system",
            "epoch": self.epoch,
            "cursor": self._latest,
            "source": "observatory_event_hub",
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
