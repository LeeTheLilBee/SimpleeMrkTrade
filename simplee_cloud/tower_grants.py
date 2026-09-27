"""SC004 proposed Tower-signed one-use Cloud capability verifier.

SOURCE CONTRACT ONLY: no Tower signing key, mTLS identity receiver, live service,
HTTP route, runtime permission grant, credential or production unlock exists.
Future middleware supplies opaque authenticated peer evidence and trusted Vault
canonical scope; neither may be sourced from client JSON. Ed25519 is provided
by the audited cryptography package.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sqlite3
import stat
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from .contracts import (
    AccessDenied, CloudError, StorageContext, valid_backup_ref,
    valid_object_ref, valid_sha256,
)

_SCHEMA = "simplee.cloud.tower-grant.v1"
_FIELDS = frozenset({
    "schema", "iss", "aud", "service", "entity_id", "request_id", "decision_ref",
    "purpose", "operation", "classification", "approval_ref", "step_up_ref",
    "object_ref", "ciphertext_sha256", "nonce", "iat", "exp",
})
_OPERATIONS = frozenset({
    "WRITE_CIPHERTEXT", "READ_CIPHERTEXT", "BACKUP_CIPHERTEXT",
    "VERIFY_BACKUP", "RECONCILE_WRITE",
})
_ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
_NONCE = re.compile(r"[0-9a-f]{32}\Z")
_KEY_ID = re.compile(r"[A-Za-z0-9_.:-]{1,64}\Z")


@dataclass(frozen=True)
class SignedTowerGrant:
    key_id: str
    payload: bytes
    signature: bytes


@dataclass(frozen=True)
class TrustedVaultScope:
    request_id: str
    entity_id: str
    purpose: str
    operation: str
    classification: str
    object_ref: str
    ciphertext_sha256: str


@dataclass(frozen=True)
class AuthorizedCloudInvocation:
    context: StorageContext
    object_ref: str
    ciphertext_sha256: str
    classification: str
    approval_ref: str
    step_up_ref: str


def _no_duplicates(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise AccessDenied("duplicate grant field")
        result[k] = v
    return result


def _claims(payload: bytes) -> dict:
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 4096:
        raise AccessDenied("invalid grant envelope size")
    try:
        claims = json.loads(payload.decode("utf-8"), object_pairs_hook=_no_duplicates)
        if not isinstance(claims, dict) or set(claims) != _FIELDS:
            raise AccessDenied("unexpected grant fields")
        canonical = json.dumps(
            claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
        if canonical != payload:
            raise AccessDenied("grant encoding not canonical")
        return claims
    except (TypeError, ValueError, UnicodeError) as exc:
        raise AccessDenied("malformed signed grant") from exc


class SQLiteNonceReplayStore:
    """Source-only unique nonce ledger; independent hardening remains required."""

    def __init__(self, path: Path, *, mode: str = "disabled"):
        if mode != "source_test":
            raise CloudError("live replay store disabled")
        self.path = Path(path)
        parent = self.path.parent
        if parent.is_symlink():
            raise CloudError("symlink nonce directory forbidden")
        parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not parent.is_dir() or stat.S_IMODE(parent.stat().st_mode) & 0o077:
            raise CloudError("nonce directory must be private")
        if self.path.is_symlink():
            raise CloudError("symlink replay database forbidden")
        flags = os.O_RDWR | os.O_CREAT
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(self.path, flags, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
                raise CloudError("nonce database must be private regular file")
        finally:
            os.close(fd)
        with closing(self._connection()) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS consumed("
                "nonce_tag TEXT PRIMARY KEY, expires_at INTEGER NOT NULL)"
            )

    def _connection(self):
        conn = sqlite3.connect(str(self.path), isolation_level=None, timeout=5)
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("PRAGMA journal_mode=DELETE")
        return conn

    def consume(self, key_id: str, nonce: str, expiry: int):
        tag = hashlib.sha256((key_id + ":" + nonce).encode()).hexdigest()
        with closing(self._connection()) as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("INSERT INTO consumed VALUES (?,?)", (tag, expiry))
                conn.commit()
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                raise AccessDenied("Tower grant already consumed") from exc
            except BaseException:
                conn.rollback()
                raise

    def count(self) -> int:
        with closing(self._connection()) as conn:
            return conn.execute("SELECT COUNT(*) FROM consumed").fetchone()[0]


class SourceOnlyTowerGrantVerifier:
    """Do not expose as a route or install a synthetic peer/revocation verifier."""

    def __init__(
        self, *, tower_public_keys: Mapping[str, bytes],
        peer_is_authenticated_vault: Callable[[object], bool],
        tower_decision_is_active: Callable[[str], bool],
        replay_store: SQLiteNonceReplayStore,
        now_epoch_seconds: Callable[[], int],
        mode: str = "disabled",
    ):
        if mode != "source_test":
            raise CloudError("live Tower capability verifier disabled")
        if not tower_public_keys or not isinstance(replay_store, SQLiteNonceReplayStore):
            raise CloudError("pinned Tower keys and durable replay state required")
        if not all(callable(x) for x in (
            peer_is_authenticated_vault, tower_decision_is_active, now_epoch_seconds
        )):
            raise CloudError("independent authority verification callbacks required")
        if not all(
            isinstance(k, str) and _KEY_ID.fullmatch(k) and
            isinstance(v, bytes) and len(v) == 32 for k, v in tower_public_keys.items()
        ):
            raise CloudError("invalid pinned Tower public-key registry")
        self._keys = dict(tower_public_keys)
        self._peer = peer_is_authenticated_vault
        self._active = tower_decision_is_active
        self._replay = replay_store
        self._now = now_epoch_seconds

    def verify_and_consume(
        self, *, grant: SignedTowerGrant, authenticated_transport_peer: object,
        expected: TrustedVaultScope,
    ) -> AuthorizedCloudInvocation:
        if not isinstance(grant, SignedTowerGrant) or not isinstance(expected, TrustedVaultScope):
            raise AccessDenied("trusted grant and scope required")
        if not isinstance(grant.key_id, str) or not _KEY_ID.fullmatch(grant.key_id):
            raise AccessDenied("invalid Tower signing key identity")
        key = self._keys.get(grant.key_id)
        if key is None or not isinstance(grant.payload, bytes) or not (
            1 <= len(grant.payload) <= 4096
        ) or not isinstance(grant.signature, bytes) or len(grant.signature) != 64:
            raise AccessDenied("unknown signer or malformed Tower signature")
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            from cryptography.exceptions import InvalidSignature
            Ed25519PublicKey.from_public_bytes(key).verify(grant.signature, grant.payload)
        except (ValueError, InvalidSignature) as exc:
            raise AccessDenied("Tower signature invalid") from exc
        doc = _claims(grant.payload)
        if (doc["schema"], doc["iss"], doc["aud"], doc["service"]) != (
            _SCHEMA, "tower", "simplee_sovereign_cloud", "archive_vault"
        ):
            raise AccessDenied("wrong Tower issuer, audience or caller")
        if doc["operation"] not in _OPERATIONS:
            raise AccessDenied("unsupported storage operation")
        for field in (
            "entity_id", "request_id", "decision_ref", "purpose",
            "classification", "approval_ref", "step_up_ref",
        ):
            if not isinstance(doc[field], str) or not _ID.fullmatch(doc[field]):
                raise AccessDenied("missing required Tower claim")
        if not isinstance(doc["nonce"], str) or not _NONCE.fullmatch(doc["nonce"]):
            raise AccessDenied("invalid one-use grant nonce")
        if not valid_sha256(doc["ciphertext_sha256"]):
            raise AccessDenied("invalid ciphertext digest")
        ref_ok = (
            valid_backup_ref(doc["object_ref"]) if doc["operation"] == "VERIFY_BACKUP"
            else valid_object_ref(doc["object_ref"])
        )
        if not ref_ok:
            raise AccessDenied("object reference does not match operation")
        iat, exp, now = doc["iat"], doc["exp"], self._now()
        if not all(type(x) is int for x in (iat, exp, now)) or (
            iat > now + 5 or exp <= now or exp <= iat or exp - iat > 120
        ):
            raise AccessDenied("grant expired, future-dated or overlong")
        for field in (
            "request_id", "entity_id", "purpose", "operation",
            "classification", "object_ref", "ciphertext_sha256",
        ):
            if doc[field] != getattr(expected, field):
                raise AccessDenied("signed grant differs from trusted Vault scope")
        try:
            peer_ok = self._peer(authenticated_transport_peer) is True
            active = self._active(doc["decision_ref"]) is True
        except Exception as exc:
            raise AccessDenied("peer or revocation verification unavailable") from exc
        if not peer_ok or not active:
            raise AccessDenied("unauthenticated Vault service or revoked decision")
        self._replay.consume(grant.key_id, doc["nonce"], exp)
        context = StorageContext(
            request_id=doc["request_id"], caller_service="archive_vault",
            tower_decision_ref=doc["decision_ref"], entity_id=doc["entity_id"],
            purpose=doc["purpose"], operation=doc["operation"],
        )
        return AuthorizedCloudInvocation(
            context=context, object_ref=doc["object_ref"],
            ciphertext_sha256=doc["ciphertext_sha256"],
            classification=doc["classification"], approval_ref=doc["approval_ref"],
            step_up_ref=doc["step_up_ref"],
        )
