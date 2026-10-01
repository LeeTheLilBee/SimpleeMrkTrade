"""SC038 source-only durable redacted entity↔namespace binding ledger.

Cloud operations may REQUIRE an enrolled stable mapping, but never enroll one.
Enrollment is a separate source-test preparation step representing future
independently authenticated Vault/Tower namespace-registry work.

Only HMAC(entity_id) tags and opaque 64-hex namespaces are persisted.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
import stat
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .contracts import AccessDenied, CloudError, IntegrityError

_NAMESPACE = re.compile(r"[0-9a-f]{64}\Z")
_TAG = re.compile(r"[0-9a-f]{64}\Z")
_GENESIS = "0" * 64


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


def _entity_tag(binding_key: bytes, entity_id: str) -> str:
    if not isinstance(binding_key, bytes) or len(binding_key) != 32:
        raise CloudError("approved 32-byte namespace binding secret required")
    if not isinstance(entity_id, str) or not entity_id:
        raise CloudError("missing canonical entity identity")
    return hmac.new(
        binding_key,
        b"simplee-cloud:namespace-binding:v1:" + entity_id.encode(),
        hashlib.sha256,
    ).hexdigest()


def _event_hash(
    seq: int, entity_tag: str, namespace: str, created_at: str,
    previous_hash: str,
) -> str:
    material = json.dumps(
        [seq, "NAMESPACE_BINDING_ENROLLED", entity_tag, namespace,
         created_at, previous_hash],
        separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return hashlib.sha256(material).hexdigest()


class SQLiteNamespaceBindingLedger:
    """Append-only SOURCE ledger; not a production namespace registry."""

    def __init__(
        self, path: Path, *, binding_key: bytes, mode: str = "disabled",
    ):
        if mode != "source_test":
            raise CloudError("live namespace binding registry disabled")
        if not isinstance(binding_key, bytes) or len(binding_key) != 32:
            raise CloudError("approved 32-byte namespace binding secret required")
        self.path = Path(path)
        self._binding_key = binding_key
        parent = self.path.parent
        if parent.is_symlink():
            raise CloudError("symlink namespace binding directory forbidden")
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not parent.is_dir() or stat.S_IMODE(parent.stat().st_mode) & 0o077:
            raise CloudError("namespace binding directory must be private")
        if self.path.is_symlink():
            raise CloudError("symlink namespace binding ledger forbidden")
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(self.path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
                raise CloudError("namespace binding ledger must be private regular file")
        finally:
            os.close(fd)
        self._schema()
        # Existing corrupted/legacy aliases fail at construction.
        with closing(self._connect()) as conn:
            self._verify(conn)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), isolation_level=None, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=FULL")
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

    def _schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS bindings (
                entity_tag TEXT PRIMARY KEY,
                namespace_digest TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS binding_events (
                seq INTEGER PRIMARY KEY,
                entity_tag TEXT NOT NULL,
                namespace_digest TEXT NOT NULL,
                created_at TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                event_hash TEXT NOT NULL
            )""")
            for table in ("bindings", "binding_events"):
                conn.execute(f"""CREATE TRIGGER IF NOT EXISTS {table}_block_update
                    BEFORE UPDATE ON {table}
                    BEGIN SELECT RAISE(ABORT, 'append-only namespace binding'); END""")
                conn.execute(f"""CREATE TRIGGER IF NOT EXISTS {table}_block_delete
                    BEFORE DELETE ON {table}
                    BEGIN SELECT RAISE(ABORT, 'append-only namespace binding'); END""")

    @staticmethod
    def _verify(conn: sqlite3.Connection) -> tuple[int, str]:
        seq = 0
        previous = _GENESIS
        event_rows = {}
        for row in conn.execute("SELECT * FROM binding_events ORDER BY seq"):
            seq += 1
            if (
                row["seq"] != seq or row["previous_hash"] != previous or
                not _TAG.fullmatch(row["entity_tag"]) or
                not _NAMESPACE.fullmatch(row["namespace_digest"])
            ):
                raise IntegrityError("namespace binding event sequence/shape mismatch")
            expected = _event_hash(
                row["seq"], row["entity_tag"], row["namespace_digest"],
                row["created_at"], previous,
            )
            if not hmac.compare_digest(row["event_hash"], expected):
                raise IntegrityError("namespace binding event integrity mismatch")
            key = (row["entity_tag"], row["namespace_digest"], row["created_at"])
            event_rows[key] = event_rows.get(key, 0) + 1
            previous = expected

        bindings = conn.execute("SELECT * FROM bindings").fetchall()
        expected_rows = {}
        for row in bindings:
            if (
                not _TAG.fullmatch(row["entity_tag"]) or
                not _NAMESPACE.fullmatch(row["namespace_digest"])
            ):
                raise IntegrityError("invalid namespace binding row")
            key = (row["entity_tag"], row["namespace_digest"], row["created_at"])
            expected_rows[key] = expected_rows.get(key, 0) + 1
        if event_rows != expected_rows:
            raise IntegrityError("namespace binding rows differ from audit events")
        return seq, previous

    def enroll_source_binding(self, *, entity_id: str, namespace: str) -> str:
        """Explicit source fixture/migration enrollment; NOT called by Cloud I/O."""
        if not isinstance(namespace, str) or _NAMESPACE.fullmatch(namespace) is None:
            raise CloudError("invalid stable namespace enrollment")
        tag = _entity_tag(self._binding_key, entity_id)
        with self._tx() as conn:
            by_entity = conn.execute(
                "SELECT namespace_digest FROM bindings WHERE entity_tag=?", (tag,),
            ).fetchone()
            if by_entity is not None:
                if by_entity["namespace_digest"] != namespace:
                    raise AccessDenied("stable namespace binding drift")
                return namespace
            by_namespace = conn.execute(
                "SELECT entity_tag FROM bindings WHERE namespace_digest=?",
                (namespace,),
            ).fetchone()
            if by_namespace is not None:
                raise AccessDenied("stable namespace already belongs to another entity")
            created = _now()
            last = conn.execute(
                "SELECT seq,event_hash FROM binding_events ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            next_seq = (last["seq"] + 1) if last is not None else 1
            previous = last["event_hash"] if last is not None else _GENESIS
            digest = _event_hash(next_seq, tag, namespace, created, previous)
            # Row and its audit commitment become visible in the SAME
            # transaction, so no intermediate uncommitted orphan is trusted.
            conn.execute(
                "INSERT INTO bindings VALUES(?,?,?)", (tag, namespace, created),
            )
            conn.execute(
                "INSERT INTO binding_events VALUES(?,?,?,?,?,?)",
                (next_seq, tag, namespace, created, previous, digest),
            )
            self._verify(conn)
            return namespace

    def require_binding(self, *, entity_id: str, namespace: str) -> str:
        """Verify exact pre-enrolled mapping before any Cloud provider access."""
        if not isinstance(namespace, str) or _NAMESPACE.fullmatch(namespace) is None:
            raise AccessDenied("invalid trusted stable namespace")
        tag = _entity_tag(self._binding_key, entity_id)
        with closing(self._connect()) as conn:
            self._verify(conn)
            row = conn.execute(
                "SELECT namespace_digest FROM bindings WHERE entity_tag=?", (tag,),
            ).fetchone()
            if row is not None:
                if row["namespace_digest"] != namespace:
                    raise AccessDenied("stable namespace binding mismatch")
                return namespace
            occupied = conn.execute(
                "SELECT entity_tag FROM bindings WHERE namespace_digest=?",
                (namespace,),
            ).fetchone()
            if occupied is not None:
                raise AccessDenied("stable namespace binding key/entity mismatch")
            raise AccessDenied("stable namespace not independently enrolled")

    def verify_chain(self) -> dict:
        with closing(self._connect()) as conn:
            seq, digest = self._verify(conn)
            count = conn.execute("SELECT COUNT(*) FROM bindings").fetchone()[0]
        return {
            "valid": True,
            "binding_count": count,
            "event_count": seq,
            "head_sha256": digest,
            "raw_entity_ids_persisted": False,
            "external_registry_certified": False,
            "binding_key_custody_certified": False,
            "production_authorized": False,
        }
