"""SC002 source-only durable, append-only operational journal.

SQLite writes use BEGIN IMMEDIATE, synchronous=FULL, process-private paths and
database-level UPDATE/DELETE denial for intent/event/incident records.
SC007 and SC007B bind complete reservation and incident rows to event hashes. Earlier
source-only journals with unbound reservation/incident events are rejected, not silently upgraded.
A hash chain detects accidental/incomplete history changes, NOT malicious full
database rewrites; independent signed/offsite checkpoints remain a release gate.
No file body, plaintext, raw entity ID, Vault receipt or Tower credential is stored.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import stat
from collections import Counter
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .contracts import CloudError, IntegrityError, MAX_ENVELOPE_BYTES, valid_backup_ref, valid_object_ref, valid_sha256

_NAMESPACE = re.compile(r"[0-9a-f]{64}\Z")
_CODE = {"WRITE_UNCERTAIN", "RECONCILE_MISSING", "RECONCILE_CORRUPT",
         "REPLAY_INTEGRITY_FAILURE", "READ_INTEGRITY_FAILURE", "BACKUP_INTEGRITY_FAILURE", "AUDIT_SINK_FAILURE",
         "BACKUP_UNCERTAIN", "BACKUP_RECONCILE_MISSING", "BACKUP_RECONCILE_CORRUPT",
         "BACKUP_REPLAY_INTEGRITY_FAILURE",
         "PRIMARY_READ_BACKEND_ERROR", "PRIMARY_REPLAY_BACKEND_ERROR",
         "PRIMARY_RECONCILE_BACKEND_ERROR", "BACKUP_SOURCE_BACKEND_ERROR",
         "BACKUP_REPLAY_BACKEND_ERROR", "BACKUP_RECONCILE_BACKEND_ERROR",
         "BACKUP_VERIFY_BACKEND_ERROR"}
_STATES = {"WRITE_RESERVED", "WRITE_UNCERTAIN", "WRITE_ACKNOWLEDGED",
           "RECONCILE_PRESENT", "RECONCILE_MISSING", "RECONCILE_CORRUPT",
           "REPLAY_INTEGRITY_FAILURE"}
_BACKUP_STATES = {"BACKUP_RESERVED", "BACKUP_UNCERTAIN", "BACKUP_ACKNOWLEDGED",
                  "BACKUP_RECONCILE_PRESENT", "BACKUP_RECONCILE_MISSING",
                  "BACKUP_RECONCILE_CORRUPT", "BACKUP_REPLAY_INTEGRITY_FAILURE"}
_SAFE_EVENTS = {"read_intent", "read_verified", "backup_intent",
                "backup_acknowledged", "restore_verification_intent",
                "restore_copy_verified"}
_GENESIS = "0" * 64


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _request_tag(namespace: str, request_id: str) -> str:
    if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", request_id):
        raise CloudError("invalid internal request identity")
    return hashlib.sha256(("write:v1:" + namespace + ":" + request_id).encode()).hexdigest()


def _backup_tag(namespace: str, request_id: str) -> str:
    if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", request_id):
        raise CloudError("invalid backup request identity")
    return hashlib.sha256(("backup:v1:" + namespace + ":" + request_id).encode()).hexdigest()


def _reservation_hash(kind: str, values: tuple) -> str:
    """Bind the COMPLETE immutable reservation row into the event hash chain."""
    material = json.dumps([kind, *values], separators=(",", ":"), ensure_ascii=True).encode()
    return "reservation:v2:" + hashlib.sha256(material).hexdigest()


def _incident_hash(values: tuple) -> str:
    """Opaque digest of all immutable incident metadata, without raw fields."""
    material = json.dumps(["INCIDENT_RECORDED", *values], separators=(",", ":"), ensure_ascii=True).encode()
    return "incident:v2:" + hashlib.sha256(material).hexdigest()


def _hash_event(seq: int, kind: str, tag: str, scope: str, code: str, at: str, previous: str) -> str:
    material = json.dumps(
        [seq, kind, tag, scope, code, at, previous],
        separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return hashlib.sha256(material).hexdigest()


class SQLiteOperationalJournal:
    """Not production-authorized; record only opaque metadata from trusted code."""

    def __init__(self, path: Path, *, mode: str = "disabled"):
        if mode != "source_test":
            raise CloudError("operational journal runtime not production-approved")
        self.path = Path(path)
        parent = self.path.parent
        if parent.is_symlink():
            raise CloudError("symlink journal directory forbidden")
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not parent.is_dir() or stat.S_IMODE(parent.stat().st_mode) & 0o077:
            raise CloudError("journal directory must be private")
        if self.path.is_symlink():
            raise CloudError("symlink journal forbidden")
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(self.path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
                raise CloudError("journal file must be private regular file")
        finally:
            os.close(fd)
        self._schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), isolation_level=None, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("PRAGMA foreign_keys=ON")
        # DELETE journal mode rather than WAL avoids persistent sidecar logs.
        conn.execute("PRAGMA journal_mode=DELETE")
        return conn

    @contextmanager
    def _tx(self):
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            self._verify(conn)
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _schema(self):
        with closing(self._connect()) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS intents (
                request_tag TEXT PRIMARY KEY, namespace_digest TEXT NOT NULL,
                object_ref TEXT NOT NULL, ciphertext_sha256 TEXT NOT NULL,
                ciphertext_size INTEGER NOT NULL, created_at TEXT NOT NULL
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY, event_type TEXT NOT NULL,
                request_tag TEXT NOT NULL, namespace_digest TEXT NOT NULL,
                code TEXT NOT NULL, created_at TEXT NOT NULL,
                previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY, request_tag TEXT NOT NULL,
                incident_code TEXT NOT NULL, severity TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS backup_intents (
                request_tag TEXT PRIMARY KEY, namespace_digest TEXT NOT NULL,
                source_object_ref TEXT NOT NULL, source_ciphertext_sha256 TEXT NOT NULL,
                backup_ref TEXT NOT NULL, backup_sha256 TEXT NOT NULL,
                backup_size INTEGER NOT NULL, key_reference TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")
            # A physical ref belongs to one logical request inside ONE opaque
            # namespace. The same random ref may exist in another namespace.
            # Do not silently accept an existing source journal with aliases.
            try:
                conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS unique_primary_ref "
                    "ON intents(namespace_digest,object_ref)"
                )
                conn.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS unique_backup_ref "
                    "ON backup_intents(namespace_digest,backup_ref)"
                )
            except sqlite3.IntegrityError as exc:
                raise IntegrityError("existing journal has aliased physical references") from exc
            for table in ("intents", "events", "incidents", "backup_intents"):
                conn.execute(f"""CREATE TRIGGER IF NOT EXISTS {table}_block_update
                    BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT, 'append-only record'); END""")
                conn.execute(f"""CREATE TRIGGER IF NOT EXISTS {table}_block_delete
                    BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT, 'append-only record'); END""")

    @staticmethod
    def _verify(conn: sqlite3.Connection) -> tuple[int, str]:
        expected_seq, previous = 0, _GENESIS
        for row in conn.execute("SELECT * FROM events ORDER BY seq"):
            expected_seq += 1
            if row["seq"] != expected_seq or row["previous_hash"] != previous:
                raise IntegrityError("operational event sequence/chain mismatch")
            expected = _hash_event(
                row["seq"], row["event_type"], row["request_tag"],
                row["namespace_digest"], row["code"], row["created_at"], previous,
            )
            if row["event_hash"] != expected:
                raise IntegrityError("operational event integrity mismatch")
            previous = expected
        # Check uniqueness on every transaction even if an administrator has
        # bypassed/dropped the source-only SQLite unique index.
        for table, column in (
            ("intents", "object_ref"), ("backup_intents", "backup_ref"),
        ):
            aliases = conn.execute(
                "SELECT 1 FROM " + table + " GROUP BY namespace_digest," +
                column + " HAVING COUNT(*)>1 LIMIT 1"
            ).fetchone()
            if aliases is not None:
                raise IntegrityError("physical object reference reused by separate intents")
        # SC007: reservation metadata is now part of the immutable event
        # commitment, not merely an opaque request tag. Verify both directions
        # and demand exactly one reservation event per canonical intent.
        for table, event_type in (
            ("intents", "WRITE_RESERVED"), ("backup_intents", "BACKUP_RESERVED"),
        ):
            records = conn.execute("SELECT * FROM " + table).fetchall()
            count = conn.execute(
                "SELECT COUNT(*) FROM events WHERE event_type=?", (event_type,),
            ).fetchone()[0]
            if count != len(records):
                raise IntegrityError("missing or surplus reservation event/intent")
            for record in records:
                matches = conn.execute(
                    """SELECT code FROM events
                    WHERE event_type=? AND request_tag=? AND namespace_digest=?""",
                    (event_type, record["request_tag"], record["namespace_digest"]),
                ).fetchall()
                if len(matches) != 1 or matches[0]["code"] != _reservation_hash(
                    event_type, tuple(record)
                ):
                    raise IntegrityError("reserved ciphertext metadata differs from audit commitment")
        # SC007B: event count and immutable incident payloads must match in
        # BOTH directions. Several incidents may share a request tag, so use
        # a multiset rather than accepting a single matching event.
        records = conn.execute("SELECT * FROM incidents").fetchall()
        expected_incidents = Counter(
            (row["request_tag"], _incident_hash(tuple(row))) for row in records
        )
        actual_incidents = Counter(
            (row["request_tag"], row["code"])
            for row in conn.execute(
                "SELECT request_tag,code FROM events WHERE event_type='INCIDENT_RECORDED'"
            )
        )
        if actual_incidents != expected_incidents:
            raise IntegrityError("incident metadata differs from audit commitment")
        return expected_seq, previous

    def verify_chain(self) -> dict:
        with self._connect() as conn:
            seq, digest = self._verify(conn)
            return {"valid": True, "event_count": seq, "head_sha256": digest,
                    "external_checkpoint_certified": False}

    def checkpoint_head(self, event_count: int) -> str:
        """Return a fully verified hash-chain prefix, for independent signature proof."""
        if type(event_count) is not int or event_count < 0:
            raise IntegrityError("invalid checkpoint event count")
        with closing(self._connect()) as conn:
            total, _ = self._verify(conn)
            if event_count > total:
                raise IntegrityError("journal rollback or missing signed checkpoint history")
            if event_count == 0:
                return _GENESIS
            row = conn.execute(
                "SELECT event_hash FROM events WHERE seq=?", (event_count,)
            ).fetchone()
            if row is None:
                raise IntegrityError("missing checkpoint event")
            return row[0]

    def _append(self, conn: sqlite3.Connection, *, event: str, tag: str,
                scope: str, code: str = "-") -> None:
        prior = conn.execute("SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        seq = 1 if prior is None else prior["seq"] + 1
        prev = _GENESIS if prior is None else prior["event_hash"]
        at = _now()
        digest = _hash_event(seq, event, tag, scope, code, at, prev)
        conn.execute(
            """INSERT INTO events(seq,event_type,request_tag,namespace_digest,code,
               created_at,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)""",
            (seq, event, tag, scope, code, at, prev, digest),
        )

    @staticmethod
    def _state(conn: sqlite3.Connection, tag: str) -> str | None:
        for row in conn.execute("SELECT event_type FROM events WHERE request_tag=? ORDER BY seq DESC", (tag,)):
            if row["event_type"] in _STATES:
                return row["event_type"]
        return None

    @staticmethod
    def _backup_state(conn: sqlite3.Connection, tag: str) -> str | None:
        for row in conn.execute(
            "SELECT event_type FROM events WHERE request_tag=? ORDER BY seq DESC", (tag,)
        ):
            if row["event_type"] in _BACKUP_STATES:
                return row["event_type"]
        return None

    @staticmethod
    def _scope(scope: str) -> None:
        if not isinstance(scope, str) or not _NAMESPACE.fullmatch(scope):
            raise CloudError("invalid internal namespace digest")

    def reserve_write(self, *, namespace: str, request_id: str, object_ref: str,
                      digest: str, size: int) -> str:
        self._scope(namespace)
        if not valid_object_ref(object_ref) or not valid_sha256(digest) or (
            type(size) is not int or size < 33 or size > 25 * 1024 * 1024 + 64
        ):
            raise CloudError("invalid bounded write intent")
        tag = _request_tag(namespace, request_id)
        with self._tx() as conn:
            record = conn.execute("SELECT * FROM intents WHERE request_tag=?", (tag,)).fetchone()
            if record is not None:
                if (record["namespace_digest"], record["object_ref"],
                    record["ciphertext_sha256"], record["ciphertext_size"]) != (
                    namespace, object_ref, digest, size,
                ):
                    raise CloudError("idempotency conflict; new request required")
                return self._state(conn, tag) or "UNVERIFIED"
            if conn.execute(
                "SELECT 1 FROM intents WHERE namespace_digest=? AND object_ref=?",
                (namespace, object_ref),
            ).fetchone() is not None:
                raise CloudError("physical object reference already reserved to another request")
            values = (tag, namespace, object_ref, digest, size, _now())
            conn.execute("INSERT INTO intents VALUES(?,?,?,?,?,?)", values)
            self._append(
                conn, event="WRITE_RESERVED", tag=tag, scope=namespace,
                code=_reservation_hash("WRITE_RESERVED", values),
            )
            return "WRITE_RESERVED_NEW"

    def intent(self, *, namespace: str, request_id: str) -> dict:
        self._scope(namespace)
        tag = _request_tag(namespace, request_id)
        with self._connect() as conn:
            self._verify(conn)
            record = conn.execute("SELECT * FROM intents WHERE request_tag=?", (tag,)).fetchone()
            if record is None:
                raise CloudError("unknown write intent")
            return {"request_tag": tag, "namespace_digest": record["namespace_digest"],
                    "object_ref": record["object_ref"],
                    "ciphertext_sha256": record["ciphertext_sha256"],
                    "ciphertext_size": record["ciphertext_size"],
                    "state": self._state(conn, tag)}

    def backup_intent(self, *, namespace: str, request_id: str) -> dict | None:
        """Look up only canonical durable source-side backup reservation."""
        self._scope(namespace)
        tag = _backup_tag(namespace, request_id)
        with closing(self._connect()) as conn:
            self._verify(conn)
            row = conn.execute(
                "SELECT * FROM backup_intents WHERE request_tag=?", (tag,)
            ).fetchone()
            if row is None:
                return None
            return {
                **{k: row[k] for k in (
                    "namespace_digest", "source_object_ref",
                    "source_ciphertext_sha256", "backup_ref", "backup_sha256",
                    "backup_size", "key_reference",
                )},
                "state": self._backup_state(conn, tag),
            }

    def reserve_backup(self, *, namespace: str, request_id: str,
                       source_object_ref: str, source_digest: str,
                       backup_ref: str, backup_digest: str, backup_size: int,
                       key_reference: str) -> None:
        self._scope(namespace)
        if not (valid_object_ref(source_object_ref) and valid_sha256(source_digest)
                and valid_backup_ref(backup_ref) and valid_sha256(backup_digest)):
            raise CloudError("invalid bound backup refs or SHA")
        if type(backup_size) is not int or not 33 <= backup_size <= MAX_ENVELOPE_BYTES + 64:
            raise CloudError("invalid bounded backup size")
        if not isinstance(key_reference, str) or not re.fullmatch(
            r"[A-Za-z0-9_.:-]{1,128}", key_reference
        ):
            raise CloudError("invalid private backup key reference")
        tag = _backup_tag(namespace, request_id)
        with self._tx() as conn:
            if conn.execute(
                "SELECT 1 FROM backup_intents WHERE request_tag=?", (tag,)
            ).fetchone() is not None:
                raise CloudError("backup reservation already exists; reconcile, never re-PUT")
            if conn.execute(
                "SELECT 1 FROM backup_intents WHERE namespace_digest=? AND backup_ref=?",
                (namespace, backup_ref),
            ).fetchone() is not None:
                raise CloudError("physical backup reference already reserved to another request")
            values = (
                tag, namespace, source_object_ref, source_digest, backup_ref,
                backup_digest, backup_size, key_reference, _now(),
            )
            conn.execute("INSERT INTO backup_intents VALUES(?,?,?,?,?,?,?,?,?)", values)
            self._append(
                conn, event="BACKUP_RESERVED", tag=tag, scope=namespace,
                code=_reservation_hash("BACKUP_RESERVED", values),
            )

    def backup_transition(self, *, namespace: str, request_id: str, next_state: str):
        allowed = {
            "BACKUP_ACKNOWLEDGED": {"BACKUP_RESERVED"},
            "BACKUP_UNCERTAIN": {"BACKUP_RESERVED"},
            "BACKUP_RECONCILE_PRESENT": {"BACKUP_RESERVED", "BACKUP_UNCERTAIN"},
            "BACKUP_RECONCILE_MISSING": {"BACKUP_RESERVED", "BACKUP_UNCERTAIN"},
            "BACKUP_RECONCILE_CORRUPT": {"BACKUP_RESERVED", "BACKUP_UNCERTAIN"},
            "BACKUP_REPLAY_INTEGRITY_FAILURE": {
                "BACKUP_ACKNOWLEDGED", "BACKUP_RECONCILE_PRESENT",
            },
        }
        if next_state not in allowed:
            raise CloudError("unsupported backup state")
        self._scope(namespace)
        tag = _backup_tag(namespace, request_id)
        with self._tx() as conn:
            if conn.execute(
                "SELECT 1 FROM backup_intents WHERE request_tag=?", (tag,)
            ).fetchone() is None:
                raise CloudError("unknown backup reservation")
            state = self._backup_state(conn, tag)
            if state not in allowed[next_state]:
                raise CloudError("duplicate or forbidden backup transition")
            self._append(conn, event=next_state, tag=tag, scope=namespace)
            if next_state in _CODE:
                self._incident(conn, tag=tag, scope=namespace, code=next_state)

    def record_backup_reconcile_intent(self, *, namespace: str, request_id: str):
        self._scope(namespace)
        tag = _backup_tag(namespace, request_id)
        with self._tx() as conn:
            if self._backup_state(conn, tag) not in ("BACKUP_RESERVED", "BACKUP_UNCERTAIN"):
                raise CloudError("backup cannot be reconciled in current state")
            self._append(conn, event="BACKUP_RECONCILE_INTENT", tag=tag, scope=namespace)

    def _incident(self, conn: sqlite3.Connection, *, tag: str, scope: str, code: str):
        if code not in _CODE:
            raise CloudError("unknown incident code")
        values = (
            secrets.token_hex(16), tag, code,
            "critical" if "CORRUPT" in code or "INTEGRITY" in code else "warning", _now(),
        )
        conn.execute("INSERT INTO incidents VALUES(?,?,?,?,?)", values)
        self._append(
            conn, event="INCIDENT_RECORDED", tag=tag, scope=scope,
            code=_incident_hash(values),
        )

    def transition(self, *, namespace: str, request_id: str, next_state: str) -> None:
        allowed = {
            "WRITE_ACKNOWLEDGED": {"WRITE_RESERVED"},
            "WRITE_UNCERTAIN": {"WRITE_RESERVED"},
            "RECONCILE_PRESENT": {"WRITE_RESERVED", "WRITE_UNCERTAIN"},
            "RECONCILE_MISSING": {"WRITE_RESERVED", "WRITE_UNCERTAIN"},
            "RECONCILE_CORRUPT": {"WRITE_RESERVED", "WRITE_UNCERTAIN"},
            "REPLAY_INTEGRITY_FAILURE": {"WRITE_ACKNOWLEDGED", "RECONCILE_PRESENT"},
        }
        if next_state not in allowed:
            raise CloudError("unsupported write state transition")
        self._scope(namespace)
        tag = _request_tag(namespace, request_id)
        with self._tx() as conn:
            record = conn.execute("SELECT request_tag FROM intents WHERE request_tag=?", (tag,)).fetchone()
            if record is None:
                raise CloudError("cannot transition unknown intent")
            current = self._state(conn, tag)
            if current not in allowed[next_state]:
                raise CloudError("invalid or duplicate write transition")
            self._append(conn, event=next_state, tag=tag, scope=namespace)
            if next_state in _CODE:
                self._incident(conn, tag=tag, scope=namespace, code=next_state)

    def record_reconcile_intent(self, *, namespace: str, original_request_id: str) -> None:
        self._scope(namespace)
        tag = _request_tag(namespace, original_request_id)
        with self._tx() as conn:
            if self._state(conn, tag) not in ("WRITE_RESERVED", "WRITE_UNCERTAIN"):
                raise CloudError("only unresolved writes can be reconciled")
            self._append(conn, event="RECONCILE_INTENT", tag=tag, scope=namespace)

    def record_read_incident(self, *, namespace: str, request_id: str):
        self._scope(namespace)
        tag = _request_tag(namespace, request_id)
        with self._tx() as conn:
            self._incident(conn, tag=tag, scope=namespace, code="READ_INTEGRITY_FAILURE")

    def record_backend_incident(self, *, namespace: str, request_id: str,
                                code: str) -> None:
        """Opaque provider/outage metadata, never exception text or raw entity."""
        allowed = {
            "PRIMARY_READ_BACKEND_ERROR", "PRIMARY_REPLAY_BACKEND_ERROR",
            "PRIMARY_RECONCILE_BACKEND_ERROR", "BACKUP_SOURCE_BACKEND_ERROR",
            "BACKUP_REPLAY_BACKEND_ERROR", "BACKUP_RECONCILE_BACKEND_ERROR",
            "BACKUP_VERIFY_BACKEND_ERROR",
        }
        if code not in allowed:
            raise CloudError("unexpected backend incident classification")
        self._scope(namespace)
        tag = _request_tag(namespace, request_id)
        with self._tx() as conn:
            self._incident(conn, tag=tag, scope=namespace, code=code)

    def record_backup_incident(self, *, namespace: str, request_id: str):
        self._scope(namespace)
        tag = _request_tag(namespace, request_id)
        with self._tx() as conn:
            self._incident(conn, tag=tag, scope=namespace, code="BACKUP_INTEGRITY_FAILURE")

    def record_safe_event(self, event: dict) -> None:
        if not isinstance(event, dict) or set(event) != {
            "event", "request_id", "tower_decision_ref", "namespace_digest"
        } or event.get("event") not in _SAFE_EVENTS:
            raise CloudError("unexpected operational audit event shape")
        scope = event["namespace_digest"]
        self._scope(scope)
        # Tower decision ref is intentionally not persisted; validate shape only.
        ref = event["tower_decision_ref"]
        if not isinstance(ref, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", ref):
            raise CloudError("invalid decision reference")
        tag = _request_tag(scope, event["request_id"])
        with self._tx() as conn:
            self._append(conn, event=event["event"], tag=tag, scope=scope)

    @staticmethod
    def _source_backup_coverage(conn: sqlite3.Connection) -> dict:
        """Safe SOURCE journal-ACK coverage, never physical backup proof.

        Match namespace + exact immutable primary ref + SHA. Counts distinct
        acknowledged physical primary objects; an unresolved or corrupt backup
        reservation cannot make an original appear protected.
        """
        primary = set()
        for row in conn.execute(
            "SELECT request_tag,namespace_digest,object_ref,ciphertext_sha256 FROM intents"
        ):
            if SQLiteOperationalJournal._state(conn, row["request_tag"]) in (
                "WRITE_ACKNOWLEDGED", "RECONCILE_PRESENT",
            ):
                primary.add((
                    row["namespace_digest"], row["object_ref"],
                    row["ciphertext_sha256"],
                ))
        acknowledged = set()
        pending = set()
        for row in conn.execute(
            """SELECT request_tag,namespace_digest,source_object_ref,
                      source_ciphertext_sha256 FROM backup_intents"""
        ):
            key = (
                row["namespace_digest"], row["source_object_ref"],
                row["source_ciphertext_sha256"],
            )
            status = SQLiteOperationalJournal._backup_state(conn, row["request_tag"])
            if status in ("BACKUP_ACKNOWLEDGED", "BACKUP_RECONCILE_PRESENT"):
                acknowledged.add(key)
            elif status in ("BACKUP_RESERVED", "BACKUP_UNCERTAIN"):
                pending.add(key)
        uncovered = primary - acknowledged
        return {
            "status": "SOURCE_JOURNAL_ACK_ONLY",
            "acknowledged_primary_object_count": len(primary),
            "matched_backup_ack_count": len(primary & acknowledged),
            "uncovered_primary_object_count": len(uncovered),
            "uncovered_with_pending_backup_count": len(uncovered & pending),
            "uncovered_without_pending_backup_count": len(uncovered - pending),
            "actual_backup_bytes_reverified": False,
            "independent_failure_domain_certified": False,
            "vault_canonical_backup_receipt_verified": False,
            "production_authorized": False,
        }

    def source_backup_coverage(self) -> dict:
        """Verify audit chain before reporting cross-reservation coverage."""
        with closing(self._connect()) as conn:
            self._verify(conn)
            return self._source_backup_coverage(conn)

    def health(self) -> dict:
        with self._connect() as conn:
            seq, digest = self._verify(conn)
            states = {}
            for row in conn.execute("SELECT request_tag FROM intents"):
                state = self._state(conn, row["request_tag"]) or "UNVERIFIED"
                states[state] = states.get(state, 0) + 1
            backup_states = {}
            for row in conn.execute("SELECT request_tag FROM backup_intents"):
                state = self._backup_state(conn, row["request_tag"]) or "UNVERIFIED"
                backup_states[state] = backup_states.get(state, 0) + 1
            incidents = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
            backend_errors = conn.execute(
                "SELECT COUNT(*) FROM incidents WHERE incident_code LIKE '%_BACKEND_ERROR'"
            ).fetchone()[0]
            return {
                "status": "SOURCE_ONLY_NO_GO",
                "event_count": seq, "head_sha256": digest,
                "write_count": sum(states.values()),
                "pending_writes": states.get("WRITE_RESERVED", 0) + states.get("WRITE_UNCERTAIN", 0),
                "reconciled_present": states.get("RECONCILE_PRESENT", 0),
                "missing_or_corrupt": states.get("RECONCILE_MISSING", 0) +
                                      states.get("RECONCILE_CORRUPT", 0) +
                                      states.get("REPLAY_INTEGRITY_FAILURE", 0),
                "incident_count": incidents,
                "backend_error_events": backend_errors,
                "provider_incident_delivery_certified": False,
                "backup_count": sum(backup_states.values()),
                "pending_backups": backup_states.get("BACKUP_RESERVED", 0) +
                                   backup_states.get("BACKUP_UNCERTAIN", 0),
                "backup_missing_or_corrupt": backup_states.get("BACKUP_RECONCILE_MISSING", 0) +
                                             backup_states.get("BACKUP_RECONCILE_CORRUPT", 0) +
                                             backup_states.get("BACKUP_REPLAY_INTEGRITY_FAILURE", 0),
                "external_checkpoint_certified": False,
                "hosted_alert_delivery_certified": False,
            }
