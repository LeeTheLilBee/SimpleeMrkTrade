"""Local single-host durable atomic nonce adapter for the accepted Tower source verifier.

The caller chooses an explicit durable local SQLite path and independently
owns its filesystem permissions/backup. This adapter supplies only the
`consume_once(account_key, nonce, expires_at_epoch)` callback expected by
`tower.obml_account_namespace_source.verify_ob_account_namespace_source`.
It does not verify a signature, configure a production key, authenticate an
owner/Tower session, grant Manual Live or provide multi-host shared storage.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3

SCHEMA_VERSION = "TOWER_OBML_LOCAL_SOURCE_NONCE_LEDGER_V1"
_ACCOUNT = re.compile(r"[a-z][a-z0-9_]{0,63}")
_NONCE = re.compile(r"[0-9a-f]{32}")
_CREATE = (
    "CREATE TABLE IF NOT EXISTS tower_obml_source_nonce_v1 "
    "(nonce_digest TEXT PRIMARY KEY, expires_at_epoch INTEGER NOT NULL)"
)
_INSERT = (
    "INSERT INTO tower_obml_source_nonce_v1 "
    "(nonce_digest, expires_at_epoch) VALUES (?, ?)"
)


class LocalSQLiteSourceNonceLedger:
    """Single-host source-only local adapter, *not* production approval."""

    def __init__(self, db_path: str | Path):
        if not isinstance(db_path, (str, Path)):
            raise ValueError("explicit absolute local SQLite path required")
        path = Path(db_path)
        if (
            not path.is_absolute() or not path.name or not path.parent.is_dir()
            or path.is_symlink() or path.parent.is_symlink()
            or str(db_path) in (":memory:", "") or str(db_path).startswith("file:")
        ):
            raise ValueError("explicit existing-parent local SQLite file required")
        self._path = path

    def consume_once(self, account_key: str, nonce: str, expires_at_epoch: int) -> bool:
        if (
            not isinstance(account_key, str) or _ACCOUNT.fullmatch(account_key) is None
            or not isinstance(nonce, str) or _NONCE.fullmatch(nonce) is None
            or type(expires_at_epoch) is not int or expires_at_epoch <= 0
            or self._path.is_symlink() or self._path.parent.is_symlink()
        ):
            return False
        # Persist only a namespaced digest, never raw source nonce/account.
        digest = hashlib.sha256(
            b"TOWER_OBML_SOURCE_NONCE_V1\0" + account_key.encode("ascii") +
            b"\0" + nonce.encode("ascii")
        ).hexdigest()
        conn: sqlite3.Connection | None = None
        try:
            conn = sqlite3.connect(str(self._path), timeout=5.0, isolation_level=None)
            # BEGIN IMMEDIATE serializes competing processes before uniqueness
            # check; PRIMARY KEY denies duplicates even after process restart.
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(_CREATE)
            conn.execute(_INSERT, (digest, expires_at_epoch))
            conn.commit()
            return True
        except sqlite3.Error:
            if conn is not None:
                try:
                    conn.rollback()
                except sqlite3.Error:
                    pass
            return False
        finally:
            if conn is not None:
                conn.close()


def local_nonce_ledger_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "consumes_canonical_receiver_callback": "consume_once(account_key, nonce, expires_at_epoch)",
        "atomic_sqlite_unique_nonce_digest": True,
        "persists_raw_nonce_or_account": False,
        "rejects_replay_after_process_restart_on_same_file": True,
        "explicit_local_path_required": True,
        "default_path_configured": False,
        "production_key_configured": False,
        "multi_host_shared_storage_certified": False,
        "ephemeral_container_disk_is_production_durable": False,
        "owner_authentication": False,
        "tower_session_or_step_up_verification": False,
        "manual_live_clearance": False,
        "broker_order_api": False,
        "capital_movement": False,
        "paid_service_provisioned": False,
    }
