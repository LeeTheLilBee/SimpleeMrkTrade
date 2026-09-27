"""OBML011-015: amount-free canonical OB account namespace export for Tower.

Source-only wire compatibility. This is NOT an owner credential, a Tower
session attestation, a broker-account assertion, a capital/balance disclosure
or an OBML grant. No HTTP route or signing secret is configured by this module.
A future server-side private transport must authenticate its caller and make
the Tower receiver verify the HMAC and one-time nonce independently.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
from typing import Any, Mapping

from web.ob_account_identity_truth import resolve_account_identity, SCHEMA_VERSION

EXPORT_SCHEMA = "OB_TOWER_ACCOUNT_IDENTITY_EXPORT_V1"
ISSUER = "observatory-account-identity"
AUDIENCE = "tower-obml-account-check"
PREFIX = "obai1"
MAX_LIFETIME_SECONDS = 60
_KEYS = frozenset({
    "schema_version", "source_schema_version", "issuer", "audience",
    "account_key", "account_identity_fingerprint", "namespace_authority",
    "account_class", "capital_truth_class", "nonce",
    "issued_at_epoch", "expires_at_epoch",
    "owner_authentication_asserted", "broker_account_verified",
    "real_capital_verified", "manual_live_granted",
})
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_NONCE = re.compile(r"^[0-9a-f]{32}$")


class OBAccountIdentityExportError(ValueError):
    """Generic redacted source-export refusal."""


def _secret(value: str | bytes) -> bytes:
    if isinstance(value, str):
        value = value.encode("utf-8")
    if not isinstance(value, bytes) or len(value) < 32:
        raise OBAccountIdentityExportError("ACCOUNT_EXPORT_SECRET_NOT_CONFIGURED")
    return value


def _encode_source_export(
    claims: Mapping[str, Any], *, signing_secret: str | bytes
) -> str:
    """Internal canonical encoding; never treats arbitrary claims as identity."""
    if not isinstance(claims, Mapping) or set(claims) != _KEYS:
        raise OBAccountIdentityExportError("ACCOUNT_EXPORT_FIELDS_INVALID")
    if any(claims.get(flag) is not False for flag in (
        "owner_authentication_asserted", "broker_account_verified",
        "real_capital_verified", "manual_live_granted",
    )):
        raise OBAccountIdentityExportError("ACCOUNT_EXPORT_CAPABILITY_FORBIDDEN")
    if (
        claims.get("schema_version") != EXPORT_SCHEMA
        or claims.get("source_schema_version") != SCHEMA_VERSION
        or claims.get("issuer") != ISSUER
        or claims.get("audience") != AUDIENCE
        or claims.get("account_class") != "MISSION_ACCOUNT"
        or claims.get("capital_truth_class") != "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
        or not isinstance(claims.get("account_identity_fingerprint"), str)
        or _DIGEST.fullmatch(claims["account_identity_fingerprint"]) is None
        or not isinstance(claims.get("nonce"), str)
        or _NONCE.fullmatch(claims["nonce"]) is None
    ):
        raise OBAccountIdentityExportError("ACCOUNT_EXPORT_CLAIMS_INVALID")
    issue = claims.get("issued_at_epoch")
    expiry = claims.get("expires_at_epoch")
    if (type(issue) is not int or type(expiry) is not int
            or not 0 < expiry - issue <= MAX_LIFETIME_SECONDS):
        raise OBAccountIdentityExportError("ACCOUNT_EXPORT_TIME_INVALID")
    payload = json.dumps(
        dict(claims), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")
    p64 = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    head = PREFIX + "." + p64
    mac = hmac.new(_secret(signing_secret), head.encode("ascii"), hashlib.sha256).digest()
    return head + "." + base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")


def create_ob_account_identity_export(
    account_key: str, *, now_epoch: int, signing_secret: str | bytes
) -> str:
    """Export only an exact known non-demo mission account's namespace identity.

    A source-signed identity has no relationship to current Tower owner
    session/account entitlement, IBKR credentials, funds or Manual Live mode.
    """
    if not isinstance(account_key, str) or not account_key or account_key != account_key.strip():
        raise OBAccountIdentityExportError("EXACT_ACCOUNT_KEY_REQUIRED")
    if type(now_epoch) is not int or now_epoch <= 0:
        raise OBAccountIdentityExportError("ACCOUNT_EXPORT_TIME_INVALID")
    identity = resolve_account_identity(account_key)
    if (
        identity.get("known") is not True
        or identity.get("status") != "KNOWN"
        or identity.get("account_key") != account_key
        or identity.get("account_class") != "MISSION_ACCOUNT"
        or identity.get("capital_truth_class") != "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
    ):
        raise OBAccountIdentityExportError("LIVE_REVIEW_ACCOUNT_NAMESPACE_NOT_ACCEPTED")
    claims = {
        "schema_version": EXPORT_SCHEMA,
        "source_schema_version": SCHEMA_VERSION,
        "issuer": ISSUER, "audience": AUDIENCE,
        "account_key": account_key,
        "account_identity_fingerprint": identity["identity_fingerprint"],
        "namespace_authority": identity["namespace_authority"],
        "account_class": identity["account_class"],
        "capital_truth_class": identity["capital_truth_class"],
        "nonce": secrets.token_hex(16),
        "issued_at_epoch": now_epoch,
        "expires_at_epoch": now_epoch + MAX_LIFETIME_SECONDS,
        "owner_authentication_asserted": False,
        "broker_account_verified": False,
        "real_capital_verified": False,
        "manual_live_granted": False,
    }
    return _encode_source_export(claims, signing_secret=signing_secret)


def source_export_contract() -> dict[str, Any]:
    return {
        "schema_version": EXPORT_SCHEMA,
        "issuer": ISSUER, "audience": AUDIENCE, "token_prefix": PREFIX,
        "max_lifetime_seconds": MAX_LIFETIME_SECONDS,
        "account_namespace_source": SCHEMA_VERSION,
        "proof_demo_eligible_for_obml": False,
        "source_export_is_tower_owner_authentication": False,
        "source_export_is_broker_account_authentication": False,
        "source_export_is_capital_truth": False,
        "source_export_issues_manual_live_clearance": False,
        "signed_token_contains_balances": False,
        "public_endpoint_registered": False,
    }
