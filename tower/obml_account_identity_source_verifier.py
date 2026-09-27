"""TWR-OBML011-015: independently verify signed OB mission-account namespace.

Not owner authentication, account entitlement, a brokerage attestation,
spendable money or Manual Live authorization. No HTTP route or environment
secret is supplied. A future authenticated server adapter must obtain
the actual current OB account fingerprint and independently prove Tower's
current owner/session, purpose-bound step-up and all trading safety gates.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import re
import sqlite3
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

EXPORT_SCHEMA = "OB_TOWER_ACCOUNT_IDENTITY_EXPORT_V1"
SOURCE_SCHEMA = "OB_ACCOUNT_IDENTITY_TRUTH_V1"
ISSUER = "observatory-account-identity"
AUDIENCE = "tower-obml-account-check"
NAMESPACE = "OB_OWNER_OPERATING_PROFILE_V1"
PREFIX = "obai1"
MAX_TTL_SECONDS = 60
MAX_TOKEN_LENGTH = 4096
FIELDS = frozenset({
    "schema_version", "source_schema_version", "issuer", "audience",
    "account_key", "account_identity_fingerprint", "namespace_authority",
    "account_class", "capital_truth_class", "nonce",
    "issued_at_epoch", "expires_at_epoch",
    "owner_authentication_asserted", "broker_account_verified",
    "real_capital_verified", "manual_live_granted",
})
TOKEN = re.compile(r"^obai1\.([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)$")
KEY = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
NONCE = re.compile(r"^[0-9a-f]{32}$")


class OBAccountSourceVerificationError(ValueError):
    """Redacted source-boundary refusal; never put token/secret in error."""


@dataclass(frozen=True)
class VerifiedOBAccountSource:
    claims: Mapping[str, Any]
    source_namespace_signature_verified: bool = True
    tower_owner_authenticated: bool = False
    broker_account_authenticated: bool = False
    capital_verified: bool = False
    manual_live_authorized: bool = False


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_DUPLICATE_FIELD")
        result[key] = value
    return result


def _decode(value: str) -> bytes:
    try:
        parsed = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        if base64.urlsafe_b64encode(parsed).decode("ascii").rstrip("=") != value:
            raise ValueError("noncanonical")
        return parsed
    except (ValueError, binascii.Error) as exc:
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_TOKEN_INVALID") from exc


def _secret(value: str | bytes) -> bytes:
    if isinstance(value, str):
        value = value.encode("utf-8")
    if not isinstance(value, bytes) or len(value) < 32:
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_SECRET_UNAVAILABLE")
    return value


def verify_signed_ob_account_source(
    token: str, *,
    shared_secret: str | bytes,
    expected_account_key: str,
    expected_current_fingerprint: str,
    now_epoch: int,
) -> VerifiedOBAccountSource:
    """HMAC first, strict claims next; never grants a Tower owner permission.

    Expected key/fingerprint MUST be fetched from an independent authenticated
    current OB source in a future adapter, not copied from client-token claims.
    Even if signed, the source only attests OB account namespace identity.
    """
    if not isinstance(token, str) or len(token) > MAX_TOKEN_LENGTH:
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_TOKEN_INVALID")
    match = TOKEN.fullmatch(token)
    if match is None:
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_TOKEN_INVALID")
    payload_b64, mac_b64 = match.groups()
    signing_input = (PREFIX + "." + payload_b64).encode("ascii")
    expected_mac = hmac.new(
        _secret(shared_secret), signing_input, hashlib.sha256
    ).digest()
    actual_mac = _decode(mac_b64)
    if not hmac.compare_digest(actual_mac, expected_mac):
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_SIGNATURE_INVALID")
    try:
        claims = json.loads(
            _decode(payload_b64).decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")),
        )
    except (ValueError, UnicodeDecodeError) as exc:
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_TOKEN_INVALID") from exc
    if not isinstance(claims, dict) or set(claims) != FIELDS:
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_FIELDS_INVALID")
    if any(claims.get(flag) is not False for flag in (
        "owner_authentication_asserted", "broker_account_verified",
        "real_capital_verified", "manual_live_granted",
    )):
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_CAPABILITY_INVALID")
    if (
        claims["schema_version"] != EXPORT_SCHEMA
        or claims["source_schema_version"] != SOURCE_SCHEMA
        or claims["issuer"] != ISSUER or claims["audience"] != AUDIENCE
        or claims["namespace_authority"] != NAMESPACE
        or claims["account_class"] != "MISSION_ACCOUNT"
        or claims["capital_truth_class"] != "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
        or type(now_epoch) is not int or now_epoch <= 0
    ):
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_SOURCE_INVALID")
    key = claims["account_key"]
    digest = claims["account_identity_fingerprint"]
    nonce = claims["nonce"]
    if (
        not isinstance(key, str) or KEY.fullmatch(key) is None or key == "proof_demo"
        or not isinstance(digest, str) or DIGEST.fullmatch(digest) is None
        or not isinstance(nonce, str) or NONCE.fullmatch(nonce) is None
        or not isinstance(expected_account_key, str)
        or not isinstance(expected_current_fingerprint, str)
        or KEY.fullmatch(expected_account_key) is None
        or DIGEST.fullmatch(expected_current_fingerprint) is None
        or key != expected_account_key or digest != expected_current_fingerprint
    ):
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_CURRENT_SOURCE_MISMATCH")
    issued = claims["issued_at_epoch"]
    expires = claims["expires_at_epoch"]
    if (
        type(issued) is not int or type(expires) is not int
        or issued <= 0 or issued > now_epoch + 5 or expires <= now_epoch
        or not 0 < expires - issued <= MAX_TTL_SECONDS
    ):
        raise OBAccountSourceVerificationError("ACCOUNT_EXPORT_EXPIRED_OR_INVALID")
    return VerifiedOBAccountSource(claims=MappingProxyType(claims))


def consume_signed_ob_account_source(
    db: sqlite3.Connection,
    token: str, *,
    shared_secret: str | bytes,
    expected_account_key: str,
    expected_current_fingerprint: str,
    now_epoch: int,
) -> bool:
    """Reverify actual signed bytes inside the public replay entrypoint.

    A caller-constructed VerifiedOBAccountSource wrapper cannot mutate the
    replay ledger. The future server adapter must derive expected account
    and CURRENT fingerprint independently from authenticated OB source.
    This method still grants no Tower person, brokerage or Manual Live role.
    """
    verified = verify_signed_ob_account_source(
        token, shared_secret=shared_secret,
        expected_account_key=expected_account_key,
        expected_current_fingerprint=expected_current_fingerprint,
        now_epoch=now_epoch,
    )
    if type(now_epoch) is not int or now_epoch >= verified.claims["expires_at_epoch"]:
        return False
    if not isinstance(db, sqlite3.Connection) or db.in_transaction:
        raise OBAccountSourceVerificationError("FRESH_SOURCE_LEDGER_REQUIRED")
    nonce_ref = (ISSUER + ":" + verified.claims["nonce"]).encode("utf-8")
    digest = hashlib.sha256(nonce_ref).hexdigest()
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "CREATE TABLE IF NOT EXISTS tower_obml_account_source_nonce "
            "(nonce_digest TEXT PRIMARY KEY, consumed_at_epoch INTEGER NOT NULL, "
            "expires_at_epoch INTEGER NOT NULL)"
        )
        db.execute(
            "INSERT INTO tower_obml_account_source_nonce VALUES (?,?,?)",
            (digest, now_epoch, verified.claims["expires_at_epoch"]),
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        db.rollback()
        return False
    except BaseException:
        db.rollback()
        raise


def describe_verified_source(
    token: str, *,
    shared_secret: str | bytes,
    expected_account_key: str,
    expected_current_fingerprint: str,
    now_epoch: int,
) -> dict[str, Any]:
    """Redacted status ONLY after independently revalidating original HMAC bytes.

    A public descriptor that trusts a caller-created VerifiedOBAccountSource
    wrapper could claim signature verification without checking any signature.
    This entrypoint requires raw signed bytes and rechecks expiry/current
    account binding every time. No replay ledger is consumed here; this
    remains an amount-free source summary, not a Tower/Manual Live grant.
    """
    verify_signed_ob_account_source(
        token,
        shared_secret=shared_secret,
        expected_account_key=expected_account_key,
        expected_current_fingerprint=expected_current_fingerprint,
        now_epoch=now_epoch,
    )
    return {
        "contract": EXPORT_SCHEMA,
        "state": "OB_ACCOUNT_NAMESPACE_SOURCE_ONLY",
        "source_identity_signature_verified": True,
        "current_tower_owner_authenticated": False,
        "tower_obml_permission_issued": False,
        "current_broker_account_verified": False,
        "capital_verified": False,
        "manual_live_authorized": False,
        "amounts_exposed": False,
        "token_exposed": False,
    }
