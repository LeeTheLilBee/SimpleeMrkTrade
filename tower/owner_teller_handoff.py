"""
TWR188/TWR189 — Secure one-time Tower -> Teller owner handoff authority.

Security:
- opaque short-lived one-time code
- raw code never retained
- SHA-256 lookup only
- HMAC-authenticated payload
- owner-session binding
- active step-up required
- current owner identity reverified
- entitlement reservation reverified
- replay denied
- expiry denied
- memory-only outstanding-code store
- runtime restart invalidates outstanding codes
- signed short-lived receipt
- navigation context is signed into handoff + receipt
- arbitrary URLs are forbidden
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import threading
import time

from datetime import datetime, timezone
from typing import Any, Mapping

from tower.identity_authority import (
    hosted_owner_identity_authority,
)

from tower.teller_owner_entitlement_reservation import (
    teller_owner_entitlement_reservation,
)


TOWER_SESSION_SECRET_ENV = "TOWER_SESSION_SECRET"

TELLER_APP_ID = "teller"
TELLER_OWNER_ENTRY_PATH = "/teller"

HANDOFF_SCHEMA_VERSION = (
    "tower.owner-teller-handoff.v1"
)

ACCESS_RECEIPT_SCHEMA_VERSION = (
    "tower.owner-teller-access-receipt.v1"
)

HANDOFF_TTL_SECONDS = 60
ACCESS_RECEIPT_TTL_SECONDS = 15 * 60
MINIMUM_SESSION_SECRET_LENGTH = 32


class OwnerTellerHandoffError(ValueError):

    def __init__(self, code: str):
        self.code = str(
            code
            or "owner_teller_handoff_failed"
        )

        super().__init__(
            self.code
        )


_STORE_LOCK = threading.Lock()

_HANDOFF_STORE: dict[
    str,
    dict[str, Any],
] = {}


_ALLOWED_NAVIGATION_APPS = {
    "tower",
    "clouds",
}

_ALLOWED_CONTEXT_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789._:-"
)


def _clean(value):
    return str(
        value
        if value is not None
        else ""
    ).strip()


def _now(value=None):
    return (
        float(value)
        if value is not None
        else time.time()
    )


def _aware_epoch(
    value,
    *,
    error_code,
):

    text = _clean(
        value
    )

    if not text:
        raise OwnerTellerHandoffError(
            error_code
        )

    if text.endswith("Z"):
        text = (
            text[:-1]
            + "+00:00"
        )

    try:
        parsed = datetime.fromisoformat(
            text
        )

    except ValueError as exc:
        raise OwnerTellerHandoffError(
            error_code
        ) from exc

    if parsed.tzinfo is None:
        raise OwnerTellerHandoffError(
            error_code
        )

    return (
        parsed
        .astimezone(
            timezone.utc
        )
        .timestamp()
    )


def _session_secret():

    secret = _clean(
        os.environ.get(
            TOWER_SESSION_SECRET_ENV
        )
    )

    if not secret:
        raise OwnerTellerHandoffError(
            "owner_teller_session_secret_not_configured"
        )

    if (
        len(secret)
        < MINIMUM_SESSION_SECRET_LENGTH
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_session_secret_too_short"
        )

    return secret


def _derive_key(
    secret,
    purpose,
):

    return hmac.new(
        secret.encode("utf-8"),
        (
            "tower.owner-teller."
            + purpose
            + ".v1"
        ).encode("utf-8"),
        hashlib.sha256,
    ).digest()


def _canonical_bytes(payload):

    return json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sign(
    payload,
    *,
    secret,
    purpose,
):

    return hmac.new(
        _derive_key(
            secret,
            purpose,
        ),
        _canonical_bytes(
            payload
        ),
        hashlib.sha256,
    ).hexdigest()


def _signature_valid(
    payload,
    signature,
    *,
    secret,
    purpose,
):

    expected = _sign(
        payload,
        secret=secret,
        purpose=purpose,
    )

    return hmac.compare_digest(
        expected,
        _clean(signature),
    )


def _safe_context_token(
    value,
    *,
    field,
    required=False,
    maximum_length=128,
):

    text = _clean(value)

    if not text:

        if required:
            raise OwnerTellerHandoffError(
                f"owner_teller_navigation_{field}_missing"
            )

        return ""

    if len(text) > maximum_length:
        raise OwnerTellerHandoffError(
            f"owner_teller_navigation_{field}_too_long"
        )

    if any(
        ch not in _ALLOWED_CONTEXT_CHARS
        for ch in text
    ):
        raise OwnerTellerHandoffError(
            f"owner_teller_navigation_{field}_invalid"
        )

    return text


def _normalize_navigation_context(
    context,
):

    if context is None:
        source = {}

    elif isinstance(
        context,
        Mapping,
    ):
        source = dict(context)

    else:
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_context_invalid"
        )

    source_app = _safe_context_token(
        source.get("source_app")
        or "tower",
        field="source_app",
        required=True,
        maximum_length=32,
    )

    return_app = _safe_context_token(
        source.get("return_app")
        or source_app,
        field="return_app",
        required=True,
        maximum_length=32,
    )

    if source_app not in _ALLOWED_NAVIGATION_APPS:
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_source_app_not_allowed"
        )

    if return_app not in _ALLOWED_NAVIGATION_APPS:
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_return_app_not_allowed"
        )

    destination = _safe_context_token(
        source.get("destination")
        or "owner_money_workspace",
        field="destination",
        required=True,
        maximum_length=96,
    )

    item_id = _safe_context_token(
        source.get("item_id"),
        field="item_id",
        maximum_length=128,
    )

    return_destination = _safe_context_token(
        source.get("return_destination")
        or (
            "overview"
            if return_app == "clouds"
            else "access_home"
        ),
        field="return_destination",
        required=True,
        maximum_length=96,
    )

    correlation_id = _safe_context_token(
        source.get("correlation_id")
        or (
            "corr_"
            + secrets.token_hex(16)
        ),
        field="correlation_id",
        required=True,
        maximum_length=96,
    )

    return {
        "source_app":
            source_app,

        "destination_app":
            TELLER_APP_ID,

        "destination":
            destination,

        "item_id":
            item_id,

        "return_app":
            return_app,

        "return_destination":
            return_destination,

        "correlation_id":
            correlation_id,
    }


def _validate_signed_navigation_context(
    context,
):

    if not isinstance(
        context,
        Mapping,
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_context_missing"
        )

    value = dict(
        context
    )

    if (
        value.get("destination_app")
        != TELLER_APP_ID
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_destination_app_invalid"
        )

    source_app = _safe_context_token(
        value.get("source_app"),
        field="source_app",
        required=True,
        maximum_length=32,
    )

    return_app = _safe_context_token(
        value.get("return_app"),
        field="return_app",
        required=True,
        maximum_length=32,
    )

    if source_app not in _ALLOWED_NAVIGATION_APPS:
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_source_app_not_allowed"
        )

    if return_app not in _ALLOWED_NAVIGATION_APPS:
        raise OwnerTellerHandoffError(
            "owner_teller_navigation_return_app_not_allowed"
        )

    _safe_context_token(
        value.get("destination"),
        field="destination",
        required=True,
        maximum_length=96,
    )

    _safe_context_token(
        value.get("item_id"),
        field="item_id",
        maximum_length=128,
    )

    _safe_context_token(
        value.get("return_destination"),
        field="return_destination",
        required=True,
        maximum_length=96,
    )

    _safe_context_token(
        value.get("correlation_id"),
        field="correlation_id",
        required=True,
        maximum_length=96,
    )

    return value


def _validate_session_context(
    context,
    *,
    secret,
    now_epoch,
):

    if not isinstance(
        context,
        Mapping,
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_session_context_missing"
        )

    if (
        context.get("authenticated")
        is not True
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_owner_session_not_verified"
        )

    role = _clean(
        context.get("role")
    )

    if role != "owner":
        raise OwnerTellerHandoffError(
            "owner_teller_owner_role_not_verified"
        )

    owner_id = _clean(
        context.get("owner_id")
    )

    username = _clean(
        context.get("username")
    )

    authenticated_at = _clean(
        context.get("authenticated_at")
    )

    step_up_until = _clean(
        context.get("step_up_until")
    )

    tower_session_id = _clean(
        context.get(
            "tower_session_id"
        )
    )

    if (
        tower_session_id
        and (
            len(
                tower_session_id
            )
            > 128
            or any(
                ch
                not in
                _ALLOWED_CONTEXT_CHARS
                for ch
                in tower_session_id
            )
        )
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_session_id_invalid"
        )

    if not all(
        (
            owner_id,
            username,
            authenticated_at,
            step_up_until,
        )
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_session_context_incomplete"
        )

    auth_epoch = _aware_epoch(
        authenticated_at,
        error_code=(
            "owner_teller_authentication_timestamp_invalid"
        ),
    )

    step_up_epoch = _aware_epoch(
        step_up_until,
        error_code=(
            "owner_teller_step_up_timestamp_invalid"
        ),
    )

    if (
        auth_epoch
        > now_epoch + 5
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_authentication_timestamp_future"
        )

    if step_up_epoch <= now_epoch:
        raise OwnerTellerHandoffError(
            "owner_teller_step_up_not_active"
        )

    binding_payload = {
        "authenticated":
            True,

        "role":
            role,

        "owner_id":
            owner_id,

        "username":
            username,

        "authenticated_at":
            authenticated_at,

        "step_up_until":
            step_up_until,

        "tower_session_id":
            tower_session_id,
    }

    session_binding = _sign(
        binding_payload,
        secret=secret,
        purpose="session-binding",
    )

    return {
        **binding_payload,

        "step_up_until_epoch":
            step_up_epoch,

        "session_binding":
            session_binding,
    }


def _verify_current_owner(
    session_truth,
):

    authority = (
        hosted_owner_identity_authority()
    )

    if (
        authority.get("verification_state")
        != "VERIFIED"
        or authority.get("configured")
        is not True
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_identity_not_verified"
        )

    record = authority.get(
        "record"
    )

    if not isinstance(
        record,
        Mapping,
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_identity_record_missing"
        )

    if (
        _clean(
            record.get("role")
        )
        != "owner"
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_identity_role_not_owner"
        )

    if not hmac.compare_digest(
        _clean(
            record.get("username")
        ),
        _clean(
            session_truth.get("username")
        ),
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_identity_session_mismatch"
        )

    requested_owner_id = _clean(
        session_truth.get(
            "owner_id"
        )
    )

    record_owner_id = _clean(
        record.get(
            "person_id"
        )
    )

    if (
        requested_owner_id
        and record_owner_id
        and not hmac.compare_digest(
            requested_owner_id,
            record_owner_id,
        )
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_identity_owner_id_mismatch"
        )

    return dict(record)


def _verify_entitlement_reservation():

    reservation = (
        teller_owner_entitlement_reservation()
    )

    if (
        reservation.get("policy_contract_verified")
        is not True
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_entitlement_reservation_not_verified"
        )

    if (
        reservation.get("reservation_state")
        != "ACTIVATED"
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_entitlement_not_activated"
        )

    if (
        reservation.get("effective_entitlement")
        is not True
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_effective_entitlement_missing"
        )

    if (
        reservation.get("activation_gate")
        != "TWR190"
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_entitlement_activation_gate_changed"
        )

    return dict(reservation)


def owner_teller_handoff_authority_status():

    secret = _clean(
        os.environ.get(
            TOWER_SESSION_SECRET_ENV
        )
    )

    with _STORE_LOCK:
        count = len(
            _HANDOFF_STORE
        )

    return {
        "configured":
            bool(
                secret
                and len(secret)
                >= MINIMUM_SESSION_SECRET_LENGTH
            ),

        "storage":
            "PROCESS_MEMORY",

        "durable":
            False,

        "restart_invalidates_outstanding_handoffs":
            True,

        "raw_handoff_code_persisted":
            False,

        "active_record_count":
            count,

        "handoff_ttl_seconds":
            HANDOFF_TTL_SECONDS,

        "receipt_ttl_seconds":
            ACCESS_RECEIPT_TTL_SECONDS,

        "broker_authority":
            False,

        "capital_authority":
            False,

        "payroll_execution_authority":
            False,

        "live_auto_authority":
            False,
    }


def issue_owner_teller_handoff(
    session_context,
    *,
    navigation_context=None,
    now_epoch=None,
):

    now = _now(
        now_epoch
    )

    secret = _session_secret()

    session_truth = (
        _validate_session_context(
            session_context,
            secret=secret,
            now_epoch=now,
        )
    )

    _verify_current_owner(
        session_truth
    )

    _verify_entitlement_reservation()

    navigation = (
        _normalize_navigation_context(
            navigation_context
        )
    )

    expires_at = min(
        now + HANDOFF_TTL_SECONDS,
        float(
            session_truth[
                "step_up_until_epoch"
            ]
        ),
    )

    if expires_at <= now:
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_has_no_valid_lifetime"
        )

    raw_code = secrets.token_urlsafe(
        32
    )

    code_hash = hashlib.sha256(
        raw_code.encode("utf-8")
    ).hexdigest()

    handoff_id = (
        "tower_teller_handoff_"
        + secrets.token_hex(16)
    )

    payload = {
        "schema_version":
            HANDOFF_SCHEMA_VERSION,

        "handoff_id":
            handoff_id,

        "issuer":
            "tower",

        "audience":
            TELLER_APP_ID,

        "app_id":
            TELLER_APP_ID,

        "role":
            "owner",

        "target_path":
            TELLER_OWNER_ENTRY_PATH,

        "owner_id":
            session_truth[
                "owner_id"
            ],

        "username":
            session_truth[
                "username"
            ],

        "tower_session_id":
            session_truth.get(
                "tower_session_id",
                "",
            ),

        "session_binding":
            session_truth[
                "session_binding"
            ],

        "issued_at_epoch":
            now,

        "expires_at_epoch":
            expires_at,

        "one_time":
            True,

        "effective_entitlement_at_issue":
            True,

        "activation_gate":
            "TWR190",

        "navigation_context":
            navigation,
    }

    signature = _sign(
        payload,
        secret=secret,
        purpose="handoff-payload",
    )

    with _STORE_LOCK:

        if code_hash in _HANDOFF_STORE:
            raise OwnerTellerHandoffError(
                "owner_teller_handoff_code_collision"
            )

        _HANDOFF_STORE[
            code_hash
        ] = {
            "payload":
                payload,

            "payload_signature":
                signature,

            "consumed":
                False,
        }

    return {
        "handoff_code":
            raw_code,

        "handoff_id":
            handoff_id,

        "app_id":
            TELLER_APP_ID,

        "target_path":
            TELLER_OWNER_ENTRY_PATH,

        "expires_at_epoch":
            expires_at,

        "one_time":
            True,

        "storage":
            "PROCESS_MEMORY",

        "durable":
            False,

        "raw_code_persisted":
            False,

        "effective_entitlement":
            True,

        "activation_gate":
            "TWR190",

        "navigation_context":
            navigation,
    }


def consume_owner_teller_handoff(
    handoff_code,
    *,
    now_epoch=None,
):

    now = _now(
        now_epoch
    )

    secret = _session_secret()

    raw_code = _clean(
        handoff_code
    )

    if not raw_code:
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_code_missing"
        )

    code_hash = hashlib.sha256(
        raw_code.encode("utf-8")
    ).hexdigest()

    with _STORE_LOCK:

        record = _HANDOFF_STORE.get(
            code_hash
        )

        if record is None:
            raise OwnerTellerHandoffError(
                "owner_teller_handoff_unknown"
            )

        if (
            record.get("consumed")
            is True
        ):
            raise OwnerTellerHandoffError(
                "owner_teller_handoff_replay_denied"
            )

        payload = dict(
            record.get("payload")
            or {}
        )

        signature = _clean(
            record.get(
                "payload_signature"
            )
        )

    if not _signature_valid(
        payload,
        signature,
        secret=secret,
        purpose="handoff-payload",
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_payload_signature_invalid"
        )

    if (
        payload.get("schema_version")
        != HANDOFF_SCHEMA_VERSION
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_schema_invalid"
        )

    if (
        payload.get("issuer")
        != "tower"
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_issuer_invalid"
        )

    if (
        payload.get("audience")
        != TELLER_APP_ID
        or payload.get("app_id")
        != TELLER_APP_ID
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_app_invalid"
        )

    if (
        payload.get("role")
        != "owner"
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_role_invalid"
        )

    if (
        payload.get("target_path")
        != TELLER_OWNER_ENTRY_PATH
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_handoff_target_invalid"
        )

    navigation = (
        _validate_signed_navigation_context(
            payload.get(
                "navigation_context"
            )
        )
    )

    expires_at = float(
        payload.get(
            "expires_at_epoch"
        )
        or 0
    )

    if expires_at <= now:

        with _STORE_LOCK:
            _HANDOFF_STORE.pop(
                code_hash,
                None,
            )

        raise OwnerTellerHandoffError(
            "owner_teller_handoff_expired"
        )

    _verify_current_owner(
        {
            "username":
                payload.get("username"),

            "owner_id":
                payload.get("owner_id"),
        }
    )

    _verify_entitlement_reservation()

    receipt_id = (
        "tower_teller_receipt_"
        + secrets.token_hex(16)
    )

    receipt = {
        "schema_version":
            ACCESS_RECEIPT_SCHEMA_VERSION,

        "receipt_id":
            receipt_id,

        "handoff_id":
            payload[
                "handoff_id"
            ],

        "issuer":
            "tower",

        "audience":
            TELLER_APP_ID,

        "app_id":
            TELLER_APP_ID,

        "role":
            "owner",

        "owner_id":
            payload[
                "owner_id"
            ],

        "tower_session_id":
            payload.get(
                "tower_session_id",
                "",
            ),

        "target_path":
            TELLER_OWNER_ENTRY_PATH,

        "session_binding":
            payload[
                "session_binding"
            ],

        "consumed_at_epoch":
            now,

        "expires_at_epoch":
            now
            + ACCESS_RECEIPT_TTL_SECONDS,

        "current_owner_identity_verified":
            True,

        "broker_authority":
            False,

        "capital_authority":
            False,

        "payroll_execution_authority":
            False,

        "live_auto_authority":
            False,

        "navigation_context":
            navigation,
    }

    receipt_signature = _sign(
        receipt,
        secret=secret,
        purpose="access-receipt",
    )

    with _STORE_LOCK:

        current = _HANDOFF_STORE.get(
            code_hash
        )

        if current is None:
            raise OwnerTellerHandoffError(
                "owner_teller_handoff_unknown"
            )

        if (
            current.get("consumed")
            is True
        ):
            raise OwnerTellerHandoffError(
                "owner_teller_handoff_replay_denied"
            )

        current[
            "consumed"
        ] = True

    return {
        **receipt,
        "signature":
            receipt_signature,
    }


def validate_owner_teller_access_receipt(
    receipt,
    *,
    now_epoch=None,
):

    now = _now(
        now_epoch
    )

    secret = _session_secret()

    if not isinstance(
        receipt,
        Mapping,
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_missing"
        )

    payload = dict(
        receipt
    )

    signature = _clean(
        payload.pop(
            "signature",
            "",
        )
    )

    if not _signature_valid(
        payload,
        signature,
        secret=secret,
        purpose="access-receipt",
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_signature_invalid"
        )

    if (
        payload.get("schema_version")
        != ACCESS_RECEIPT_SCHEMA_VERSION
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_schema_invalid"
        )

    if (
        payload.get("app_id")
        != TELLER_APP_ID
        or payload.get("audience")
        != TELLER_APP_ID
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_app_invalid"
        )

    if (
        payload.get("role")
        != "owner"
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_role_invalid"
        )

    if (
        payload.get("target_path")
        != TELLER_OWNER_ENTRY_PATH
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_target_invalid"
        )

    navigation = (
        _validate_signed_navigation_context(
            payload.get(
                "navigation_context"
            )
        )
    )

    if (
        float(
            payload.get(
                "expires_at_epoch"
            )
            or 0
        )
        <= now
    ):
        raise OwnerTellerHandoffError(
            "owner_teller_access_receipt_expired"
        )

    return {
        **payload,

        "navigation_context":
            navigation,

        "signature_valid":
            True,

        "access_verified":
            True,
    }


def reset_owner_teller_handoff_store_for_tests():

    with _STORE_LOCK:
        _HANDOFF_STORE.clear()
