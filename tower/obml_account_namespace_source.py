"""Tower-side *source namespace* check for the OBML account export proposal.

A correctly signed OB namespace export says only that an appropriately
provisioned OB source named a canonical mission account. It never authenticates
the human owner, Tower session/step-up/revocation, actual broker account,
options permission, capital truth, or Manual Live production approval.

No endpoint, configured key, default replay cache, service or paid dependency.
Tower caller MUST supply trusted key material and durable atomic consume_once.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import hashlib
import hmac
import json
import re
from typing import Callable

from web.ob_account_identity_truth import resolve_account_identity, SCHEMA_VERSION

SOURCE_SCHEMA = "OB_TOWER_ACCOUNT_IDENTITY_EXPORT_V1"
RECEIPT_SCHEMA = "TOWER_OBML_OB_ACCOUNT_NAMESPACE_SOURCE_RECEIPT_V1"
ISSUER = "observatory-account-identity"
AUDIENCE = "tower-obml-account-check"
PREFIX = "obai1"
MAX_TTL_SECONDS = 60
MAX_TOKEN_CHARS = 4096
_KEYS = frozenset((
    "schema_version", "source_schema_version", "issuer", "audience",
    "account_key", "account_identity_fingerprint", "namespace_authority",
    "account_class", "capital_truth_class", "nonce",
    "issued_at_epoch", "expires_at_epoch",
    "owner_authentication_asserted", "broker_account_verified",
    "real_capital_verified", "manual_live_granted",
))
_FORBIDDEN_FLAGS = (
    "owner_authentication_asserted", "broker_account_verified",
    "real_capital_verified", "manual_live_granted",
)
_NONCE = re.compile(r"[0-9a-f]{32}")
_B64 = re.compile(r"[A-Za-z0-9_-]+")
ConsumeNonce = Callable[[str, str, int], bool]


class NamespaceSourceRefused(ValueError):
    """Generic denial: do not echo source token, signature or key."""


@dataclass(frozen=True)
class NamespaceSourceReceipt:
    authority: str
    source_authority: str
    account_key: str
    account_identity_fingerprint: str
    issuer: str
    audience: str
    issued_at_epoch: int
    expires_at_epoch: int
    signature_verified_with_trusted_injected_key: bool
    one_time_nonce_consumed_by_caller_store: bool
    owner_authentication_verified: bool
    tower_session_verified: bool
    tower_permission_verified: bool
    tower_step_up_verified: bool
    tower_revocation_verified: bool
    broker_account_verified: bool
    real_capital_verified: bool
    manual_live_granted: bool
    broker_order_api_authorized: bool
    capital_movement_authorized: bool


def _deny() -> None:
    raise NamespaceSourceRefused("OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED")


def _decode_segment(value: str) -> bytes:
    if not value or not _B64.fullmatch(value) or "=" in value:
        _deny()
    try:
        decoded = base64.b64decode(
            value + "=" * (-len(value) % 4), altchars=b"-_", validate=True,
        )
    except (ValueError, TypeError) as exc:
        raise NamespaceSourceRefused("OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED") from exc
    if base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=") != value:
        _deny()
    return decoded


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            _deny()
        value[key] = item
    return value


def verify_ob_account_namespace_source(
    token: str, *, now_epoch: int, verification_key: str | bytes,
    consume_once: ConsumeNonce,
) -> NamespaceSourceReceipt:
    """Verify source namespace plus injected atomic replay consumption only.

    consume_once(account_key, nonce, expiry) must atomically record a fresh
    nonce in a durable shared Tower store and return exactly True on first use.
    It must reject duplicates and outages. NEVER implement as a per-process set
    for multi-worker hosted Tower. This result is NOT owner clearance.
    """
    if (
        not isinstance(token, str) or not token or len(token) > MAX_TOKEN_CHARS
        or token != token.strip() or token.count(".") != 2
        or type(now_epoch) is not int or now_epoch <= 0
        or not callable(consume_once)
    ):
        _deny()
    if isinstance(verification_key, str):
        verification_key = verification_key.encode("utf-8")
    if not isinstance(verification_key, bytes) or len(verification_key) < 32:
        _deny()
    prefix, payload64, mac64 = token.split(".")
    if prefix != PREFIX:
        _deny()
    raw_payload = _decode_segment(payload64)
    provided_mac = _decode_segment(mac64)
    if len(provided_mac) != hashlib.sha256().digest_size or not 0 < len(raw_payload) <= 2048:
        _deny()
    signing_input = (prefix + "." + payload64).encode("ascii")
    expected = hmac.new(verification_key, signing_input, hashlib.sha256).digest()
    # Authenticate bytes BEFORE interpreting any untrusted JSON.
    if not hmac.compare_digest(provided_mac, expected):
        _deny()
    try:
        claims = json.loads(raw_payload.decode("utf-8"), object_pairs_hook=_unique_object,
                            parse_constant=lambda _x: _deny())
    except (UnicodeError, ValueError, TypeError) as exc:
        raise NamespaceSourceRefused("OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED") from exc
    if not isinstance(claims, dict) or set(claims) != _KEYS:
        _deny()
    if any(claims.get(flag) is not False for flag in _FORBIDDEN_FLAGS):
        _deny()
    if (
        claims.get("schema_version") != SOURCE_SCHEMA
        or claims.get("source_schema_version") != SCHEMA_VERSION
        or claims.get("issuer") != ISSUER or claims.get("audience") != AUDIENCE
        or claims.get("account_class") != "MISSION_ACCOUNT"
        or claims.get("capital_truth_class") != "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
    ):
        _deny()
    account_key = claims.get("account_key")
    if not isinstance(account_key, str) or not account_key or account_key.strip() != account_key:
        _deny()
    identity = resolve_account_identity(account_key)
    if (
        identity.get("known") is not True or identity.get("account_key") != account_key
        or identity.get("account_class") != "MISSION_ACCOUNT"
        or identity.get("identity_fingerprint") != claims.get("account_identity_fingerprint")
        or identity.get("namespace_authority") != claims.get("namespace_authority")
        or identity.get("capital_truth_class") != claims.get("capital_truth_class")
    ):
        _deny()
    issued = claims.get("issued_at_epoch")
    expires = claims.get("expires_at_epoch")
    nonce = claims.get("nonce")
    if (
        type(issued) is not int or type(expires) is not int
        or issued <= 0 or not 0 < expires - issued <= MAX_TTL_SECONDS
        or not issued <= now_epoch < expires
        or not isinstance(nonce, str) or not _NONCE.fullmatch(nonce)
    ):
        _deny()
    try:
        consumed = consume_once(account_key, nonce, expires)
    except Exception as exc:
        raise NamespaceSourceRefused("OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED") from exc
    if consumed is not True:
        _deny()
    return NamespaceSourceReceipt(
        authority=RECEIPT_SCHEMA, source_authority=SOURCE_SCHEMA,
        account_key=account_key, account_identity_fingerprint=identity["identity_fingerprint"],
        issuer=ISSUER, audience=AUDIENCE,
        issued_at_epoch=issued, expires_at_epoch=expires,
        signature_verified_with_trusted_injected_key=True,
        one_time_nonce_consumed_by_caller_store=True,
        owner_authentication_verified=False, tower_session_verified=False,
        tower_permission_verified=False, tower_step_up_verified=False,
        tower_revocation_verified=False, broker_account_verified=False,
        real_capital_verified=False, manual_live_granted=False,
        broker_order_api_authorized=False, capital_movement_authorized=False,
    )


def namespace_source_contract() -> dict[str, object]:
    return {
        "authority": RECEIPT_SCHEMA, "source_schema": SOURCE_SCHEMA,
        "source_only": True, "max_token_chars": MAX_TOKEN_CHARS,
        "max_ttl_seconds": MAX_TTL_SECONDS,
        "trusted_server_side_key_injection_required": True,
        "atomic_durable_nonce_consumption_required": True,
        "default_nonce_store_provided": False, "public_route_registered": False,
        "production_secret_configured": False,
        "source_signature_is_owner_authentication": False,
        "source_signature_is_tower_permission": False,
        "source_signature_is_real_broker_or_capital_truth": False,
        "manual_live_grant": False, "broker_order_api": False,
        "capital_movement": False, "paid_services_provisioned": False,
    }
