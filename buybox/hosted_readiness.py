"""BBX011-015: source-only private hosted BuyBox configuration inspection.

No provider API, no disk creation, no paid resource, no server bind, no app
authorization. Paths and environment-shaped values are NOT proof that a
Render persistent disk, backup/recovery or security review actually exists.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit

from cryptography.fernet import Fernet

REQUIRED = (
    "BUYBOX_AUTH_MODE", "BUYBOX_PUBLIC_ORIGIN", "TOWER_PUBLIC_ORIGIN",
    "TOWER_BUYBOX_HANDOFF_SECRET", "BUYBOX_SECRET_KEY",
    "BUYBOX_DOCUMENT_KEY", "BUYBOX_DB_PATH", "BUYBOX_DOCS_DIR",
    "BUYBOX_DURABLE_MOUNT", "BUYBOX_SECURE_COOKIE",
)


def _origin(value: Any) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and host not in (None, "localhost", "127.0.0.1", "::1")
        and parsed.netloc
        and parsed.username is None
        and parsed.password is None
        and parsed.path == ""
        and parsed.query == ""
        and parsed.fragment == ""
        and value == "https://" + parsed.netloc
    )


def _private_path(path: Path) -> bool:
    return bool(
        path.is_dir()
        and not path.is_symlink()
        and stat.S_IMODE(path.stat().st_mode) & 0o077 == 0
    )


def inspect_private_hosted_config(
    config: Mapping[str, Any], *,
    is_mount: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    """Return reason codes only, never secret values or private file locations.

    An injected mount predicate is for synthetic tests; production must use
    real os.path.ismount and separate provider-side disk/backup inspection.
    """
    reasons: list[str] = []
    for key in REQUIRED:
        if not isinstance(config.get(key), str) or not config[key].strip():
            reasons.append("MISSING_" + key)
    if reasons:
        return {
            "status": "BLOCKED", "reason_codes": reasons,
            "configuration_checked": True, "provider_storage_proven": False,
            "backup_restore_proven": False, "tower_receiver_active": False,
            "may_serve_private_records": False, "secrets_exposed": False,
        }

    if config["BUYBOX_AUTH_MODE"] != "tower":
        reasons.append("TOWER_AUTH_MODE_REQUIRED")
    if config.get("BUYBOX_PASSWORD_HASH"):
        reasons.append("HOSTED_LOCAL_PASSWORD_FORBIDDEN")
    if config["BUYBOX_SECURE_COOKIE"] != "1":
        reasons.append("SECURE_SESSION_COOKIE_REQUIRED")
    if not _origin(config["BUYBOX_PUBLIC_ORIGIN"]):
        reasons.append("BUYBOX_PUBLIC_ORIGIN_INVALID")
    if not _origin(config["TOWER_PUBLIC_ORIGIN"]):
        reasons.append("TOWER_PUBLIC_ORIGIN_INVALID")
    if config["BUYBOX_PUBLIC_ORIGIN"] == config["TOWER_PUBLIC_ORIGIN"]:
        reasons.append("SEPARATE_TOWER_AND_BUYBOX_ORIGINS_REQUIRED")
    secret = config["TOWER_BUYBOX_HANDOFF_SECRET"]
    flask_key = config["BUYBOX_SECRET_KEY"]
    if len(secret.encode("utf-8")) < 32 or len(flask_key.encode("utf-8")) < 32:
        reasons.append("SEPARATE_STRONG_SESSION_AND_HANDOFF_KEYS_REQUIRED")
    if secret == flask_key or config["BUYBOX_DOCUMENT_KEY"] in (secret, flask_key):
        reasons.append("SECURITY_KEYS_MUST_BE_DISTINCT")
    try:
        Fernet(config["BUYBOX_DOCUMENT_KEY"].encode("ascii"))
    except (ValueError, TypeError, UnicodeError):
        reasons.append("DOCUMENT_KEY_INVALID")

    raw_mount = Path(config["BUYBOX_DURABLE_MOUNT"]).expanduser()
    raw_db = Path(config["BUYBOX_DB_PATH"]).expanduser()
    raw_docs = Path(config["BUYBOX_DOCS_DIR"]).expanduser()
    if (
        not all(p.is_absolute() for p in (raw_mount, raw_db, raw_docs))
        or raw_mount == Path("/")
        or any(".." in p.parts for p in (raw_mount, raw_db, raw_docs))
    ):
        reasons.append("ABSOLUTE_PRIVATE_MOUNT_AND_PATHS_REQUIRED")
    else:
        try:
            mount = raw_mount.resolve(strict=True)
            db_parent = raw_db.parent.resolve(strict=True)
            docs = raw_docs.resolve(strict=True)
            mount_predicate = os.path.ismount if is_mount is None else is_mount
            if not _private_path(raw_mount):
                reasons.append("PRIVATE_DURABLE_MOUNT_DIRECTORY_REQUIRED")
            if not mount_predicate(str(raw_mount)):
                reasons.append("REAL_MOUNT_NOT_VERIFIED")
            if not _private_path(raw_db.parent) or not _private_path(raw_docs):
                reasons.append("PRIVATE_DB_AND_DOCUMENT_DIRECTORIES_REQUIRED")
            if raw_db.exists() and (raw_db.is_symlink() or (
                stat.S_IMODE(raw_db.stat().st_mode) & 0o077
            )):
                reasons.append("EXISTING_DB_NOT_PRIVATE")
            if raw_mount.is_symlink() or raw_db.parent.is_symlink() or raw_docs.is_symlink():
                reasons.append("SYMLINKED_STORAGE_FORBIDDEN")
            if not db_parent.is_relative_to(mount) or not docs.is_relative_to(mount):
                reasons.append("DATABASE_AND_ORIGINALS_MUST_RESIDE_ON_MOUNT")
            if raw_db == raw_docs or raw_db.parent == raw_docs:
                reasons.append("DOCUMENTS_AND_DATABASE_PATHS_MUST_BE_SEPARATE")
        except (FileNotFoundError, PermissionError, OSError, ValueError):
            reasons.append("PRIVATE_HOSTED_STORAGE_UNAVAILABLE")
    return {
        "status": "BLOCKED" if reasons else "SOURCE_CONFIGURATION_VALID",
        "reason_codes": reasons,
        "configuration_checked": True,
        # Cannot prove provider durability/backups or release authorization via env.
        "provider_storage_proven": False,
        "backup_restore_proven": False,
        "tower_receiver_active": False,
        "may_serve_private_records": False,
        "secrets_exposed": False,
    }
