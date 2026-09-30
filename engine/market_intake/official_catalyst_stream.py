"""Process-local, content-free WS invalidation hints for the official catalyst corridor.

Notifications are *never* provider payloads, quotes, orders, rights approvals or
candidate signals. An authorized client must recover complete current facts by
the same Tower-protected GET. One process only; restart changes the epoch.
"""
from __future__ import annotations

from collections import deque
from hashlib import sha256
import asyncio
import json
import secrets
from threading import RLock

SOURCES = ("federal_register", "cftc", "eia", "world_bank", "nws", "sec_edgar")


class OfficialCatalystEventHub:
    def __init__(self, *, history=64, client_budget=4, queue_size=8):
        if (type(history) is not int or not 8 <= history <= 128 or
                type(client_budget) is not int or not 1 <= client_budget <= 16 or
                type(queue_size) is not int or not 2 <= queue_size <= 32):
            raise ValueError("bounded process-only notification budgets required")
        self.epoch = secrets.token_hex(12)
        self._lock = RLock()
        self._events = deque(maxlen=history)
        self._latest = 0
        self._digest = None
        self._clients = {}
        # Local session-id denylist: closing/logout and new login revoke any
        # older owner research sockets on the same single-worker instance.
        # A distributed service would need a shared revocation store.
        self._revoked_sessions = set()
        self.client_budget = client_budget
        self.queue_size = queue_size

    def _projection(self, packet):
        if (not isinstance(packet, dict) or
                packet.get("schema") != "OB_OFFICIAL_CATALYST_RADAR_V1" or
                packet.get("prices_attached") is not False or
                packet.get("broker_execution_authorized") is not False):
            raise ValueError("STREAM_PACKET_HOLD")
        rows = packet.get("sources")
        if (not isinstance(rows, list) or len(rows) != len(SOURCES) or
                tuple(r.get("source") for r in rows) != SOURCES):
            raise ValueError("STREAM_PACKET_HOLD")
        # A complete source fingerprint detects replacement, rights revocation,
        # or a newly validated observation, but raw values/text never enter
        # history or the WebSocket. Ignore retrieval time and cache_hit.
        projection = []
        for row in rows:
            state = row.get("state")
            if (state not in {"SOURCE_BOUND", "NO_PUBLICATION", "REVIEW_HOLD",
                              "SOURCE_HOLD", "KEY_REQUIRED", "EXISTING_PROTECTED_CORRIDOR"}
                    or row.get("quote_eligible") is not False or
                    row.get("execution_authorized") is not False or
                    not isinstance(row.get("facts"), list) or len(row["facts"]) > 3):
                raise ValueError("STREAM_PACKET_HOLD")
            if row["source"] == "sec_edgar" and (state != "EXISTING_PROTECTED_CORRIDOR" or row["facts"]):
                raise ValueError("STREAM_PACKET_HOLD")
            if state != "SOURCE_BOUND" and row["facts"]:
                raise ValueError("STREAM_PACKET_HOLD")
            projection.append({
                "source": row["source"], "state": state,
                "facts": row["facts"],
                "ai_use_approved": row.get("ai_use_approved") is True,
            })
        return sha256(json.dumps(
            projection, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("utf-8")).hexdigest(), tuple(
            r["source"] for r in rows if r["state"] == "SOURCE_BOUND"
        )

    def observe(self, packet):
        """Called ONLY following a real owner-authorized snapshot GET."""
        digest, bound_sources = self._projection(packet)
        with self._lock:
            if self._digest == digest:
                return self.hint()
            self._digest = digest
            self._latest += 1
            notification = {
                "schema": "OB_CATALYST_STREAM_EVENT_V1",
                "type": "snapshot_changed",
                "epoch": self.epoch, "cursor": self._latest,
                "source_only": True, "needs_authenticated_snapshot": True,
                "live_market_feed": False, "candidate_admitted": False,
                "execution_authorized": False,
            }
            self._events.append(notification)
            for key, (loop, queue) in tuple(self._clients.items()):
                def deliver(q=queue, subscriber=key):
                    if q.full():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                        # A missed event must force an HTTP resync; never
                        # silently substitute an incomplete delta.
                        q.put_nowait({
                            "schema": "OB_CATALYST_STREAM_EVENT_V1",
                            "type": "resync_required", "epoch": self.epoch,
                            "cursor": notification["cursor"], "source_only": True,
                            "needs_authenticated_snapshot": True,
                            "live_market_feed": False, "candidate_admitted": False,
                            "execution_authorized": False,
                        })
                    else:
                        q.put_nowait(dict(notification))
                try:
                    loop.call_soon_threadsafe(deliver)
                except RuntimeError:
                    self._clients.pop(key, None)
            return self.hint()

    def hint(self, *, available=False):
        with self._lock:
            return {
                "schema": "OB_CATALYST_STREAM_HINT_V1",
                "available": available is True,
                "path": "/ob/research/catalysts/stream",
                "epoch": self.epoch, "cursor": self._latest,
                "research_invalidation_only": True,
                "provider_stream_attached": False, "live_market_feed": False,
                "broker_execution_authorized": False,
            }

    def subscribe(self, *, epoch, cursor, loop):
        if not isinstance(epoch, str) or not isinstance(cursor, int) or cursor < 0:
            raise ValueError("STREAM_CURSOR_HOLD")
        with self._lock:
            if len(self._clients) >= self.client_budget:
                raise ValueError("STREAM_CLIENT_BUDGET_HOLD")
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

    def _resync(self):
        return {
            "schema": "OB_CATALYST_STREAM_EVENT_V1", "type": "resync_required",
            "epoch": self.epoch, "cursor": self._latest, "source_only": True,
            "needs_authenticated_snapshot": True,
            "live_market_feed": False, "candidate_admitted": False,
            "execution_authorized": False,
        }

    def revoke_session(self, tower_session_id):
        if not isinstance(tower_session_id, str) or not tower_session_id:
            return
        # A fixed-size digest, never expose a session identifier on the wire.
        digest = sha256(tower_session_id.encode("utf-8")).hexdigest()
        with self._lock:
            self._revoked_sessions.add(digest)

    def session_revoked(self, tower_session_id):
        if not isinstance(tower_session_id, str) or not tower_session_id:
            return True
        digest = sha256(tower_session_id.encode("utf-8")).hexdigest()
        with self._lock:
            return digest in self._revoked_sessions

    def unsubscribe(self, key):
        with self._lock:
            self._clients.pop(key, None)
