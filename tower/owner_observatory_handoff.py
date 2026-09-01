"""Real owner Tower -> Observatory operational handoff / TWR146-TWR150.

This is NOT the historical GP046 rehearsal contract.

Operational rules:

- explicit Tower session secret required
- explicit durable handoff ledger required
- current hosted owner identity must verify
- current Observatory entitlement must verify
- current Observatory app truth must be launchable
- active Tower session + step-up are bound into the handoff
- browser receives only a short-lived opaque one-time code
- only the SHA-256 code hash is persisted
- payload is HMAC authenticated
- handoff is consumed atomically once
- replay fails closed
- receiving boundary reverifies current identity and app truth
- successful consumption returns a signed session-bound OB access receipt

No broker authority.
No capital authority.
No Manual Live authorization.
No Live Auto authorization.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from tower.app_truth_projection import (
    app_truth_by_id,
)
from tower.identity_authority import (
    hosted_owner_identity_authority,
)


TOWER_SESSION_SECRET_ENV = (
    "TOWER_SESSION_SECRET"
)

TOWER_OB_HANDOFF_LEDGER_PATH_ENV = (
    "TOWER_OB_HANDOFF_LEDGER_PATH"
)

HANDOFF_SCHEMA_VERSION = (
    "tower.owner-observatory-handoff.v1"
)

ACCESS_RECEIPT_SCHEMA_VERSION = (
    "tower.owner-observatory-access-receipt.v1"
)

OBSERVATORY_APP_ID = (
    "observatory"
)

OBSERVATORY_ENTRY_PATH = (
    "/ob/dashboard"
)

HANDOFF_TTL_SECONDS = 60
ACCESS_RECEIPT_MAX_TTL_SECONDS = 15 * 60

MINIMUM_SESSION_SECRET_LENGTH = 32


class OwnerObservatoryHandoffError(
    ValueError
):
    """Fail-closed owner Observatory handoff error."""

    def __init__(
        self,
        code: str,
    ) -> None:

        self.code = str(
            code
            or "owner_observatory_handoff_failed"
        )

        super().__init__(
            self.code
        )


def _clean(
    value: Any,
) -> str:

    return str(
        value
        if value is not None
        else ""
    ).strip()


def _now_epoch(
    value: float | None = None,
) -> float:

    return (
        float(value)
        if value is not None
        else time.time()
    )


def _aware_timestamp_epoch(
    value: Any,
    *,
    error_code: str,
) -> float:

    text = _clean(
        value
    )

    if not text:

        raise OwnerObservatoryHandoffError(
            error_code
        )

    candidate = text

    if candidate.endswith(
        "Z"
    ):
        candidate = (
            candidate[:-1]
            + "+00:00"
        )

    try:

        parsed = (
            datetime.fromisoformat(
                candidate
            )
        )

    except ValueError as exc:

        raise OwnerObservatoryHandoffError(
            error_code
        ) from exc

    if parsed.tzinfo is None:

        raise OwnerObservatoryHandoffError(
            error_code
        )

    return parsed.astimezone(
        timezone.utc
    ).timestamp()


def handoff_configuration_status(
) -> dict[str, Any]:

    secret = _clean(
        os.environ.get(
            TOWER_SESSION_SECRET_ENV
        )
    )

    ledger = _clean(
        os.environ.get(
            TOWER_OB_HANDOFF_LEDGER_PATH_ENV
        )
    )

    secret_present = bool(
        secret
    )

    secret_strong_enough = (
        len(secret)
        >= MINIMUM_SESSION_SECRET_LENGTH
    )

    ledger_present = bool(
        ledger
    )

    ledger_absolute = bool(
        ledger
        and Path(
            ledger
        ).is_absolute()
    )

    configured = all((
        secret_present,
        secret_strong_enough,
        ledger_present,
        ledger_absolute,
    ))

    return {
        "configured":
            configured,

        "session_secret_present":
            secret_present,

        "session_secret_strong_enough":
            secret_strong_enough,

        "ledger_configured":
            ledger_present,

        "ledger_absolute":
            ledger_absolute,

        "session_secret_exposed":
            False,

        "ledger_path_exposed":
            False,

        "raw_handoff_code_persisted":
            False,
    }


def _configuration(
) -> tuple[str, Path]:

    status = (
        handoff_configuration_status()
    )

    if not status[
        "session_secret_present"
    ]:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_session_secret_not_configured"
        )

    if not status[
        "session_secret_strong_enough"
    ]:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_session_secret_too_short"
        )

    if not status[
        "ledger_configured"
    ]:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_handoff_ledger_not_configured"
        )

    if not status[
        "ledger_absolute"
    ]:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_handoff_ledger_must_be_absolute"
        )

    secret = _clean(
        os.environ.get(
            TOWER_SESSION_SECRET_ENV
        )
    )

    ledger = Path(
        _clean(
            os.environ.get(
                TOWER_OB_HANDOFF_LEDGER_PATH_ENV
            )
        )
    )

    return (
        secret,
        ledger,
    )


def _derive_key(
    secret: str,
    purpose: str,
) -> bytes:

    return hmac.new(
        secret.encode(
            "utf-8"
        ),
        (
            "tower.owner-observatory."
            + purpose
            + ".v1"
        ).encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()


def _canonical_bytes(
    payload: Mapping[str, Any],
) -> bytes:

    return json.dumps(
        dict(
            payload
        ),
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )


def _sign(
    payload: Mapping[str, Any],
    *,
    secret: str,
    purpose: str,
) -> str:

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
    payload: Mapping[str, Any],
    signature: str,
    *,
    secret: str,
    purpose: str,
) -> bool:

    expected = _sign(
        payload,
        secret=secret,
        purpose=purpose,
    )

    return hmac.compare_digest(
        expected,
        _clean(
            signature
        ),
    )


def _session_binding(
    context: Mapping[str, Any],
    *,
    secret: str,
) -> str:

    binding_payload = {
        "authenticated":
            context.get(
                "authenticated"
            )
            is True,

        "role":
            _clean(
                context.get(
                    "role"
                )
            ),

        "owner_id":
            _clean(
                context.get(
                    "owner_id"
                )
            ),

        "username":
            _clean(
                context.get(
                    "username"
                )
            ),

        "authenticated_at":
            _clean(
                context.get(
                    "authenticated_at"
                )
            ),

        "step_up_until":
            _clean(
                context.get(
                    "step_up_until"
                )
            ),
    }

    return _sign(
        binding_payload,
        secret=secret,
        purpose="session-binding",
    )


def _validate_session_context(
    context: Mapping[str, Any],
    *,
    secret: str,
    now_epoch: float,
) -> dict[str, Any]:

    if not isinstance(
        context,
        Mapping,
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_session_context_missing"
        )

    if (
        context.get(
            "authenticated"
        )
        is not True
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_owner_session_not_verified"
        )

    role = _clean(
        context.get(
            "role"
        )
    )

    if role != "owner":

        raise OwnerObservatoryHandoffError(
            "owner_observatory_owner_role_not_verified"
        )

    owner_id = _clean(
        context.get(
            "owner_id"
        )
    )

    username = _clean(
        context.get(
            "username"
        )
    )

    authenticated_at = _clean(
        context.get(
            "authenticated_at"
        )
    )

    step_up_until = _clean(
        context.get(
            "step_up_until"
        )
    )

    if not all((
        owner_id,
        username,
        authenticated_at,
        step_up_until,
    )):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_session_context_incomplete"
        )

    auth_epoch = (
        _aware_timestamp_epoch(
            authenticated_at,
            error_code=(
                "owner_observatory_authentication_timestamp_invalid"
            ),
        )
    )

    step_up_epoch = (
        _aware_timestamp_epoch(
            step_up_until,
            error_code=(
                "owner_observatory_step_up_timestamp_invalid"
            ),
        )
    )

    if auth_epoch > (
        now_epoch
        + 5
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_authentication_timestamp_future"
        )

    if step_up_epoch <= now_epoch:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_step_up_not_active"
        )

    return {
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

        "step_up_until_epoch":
            step_up_epoch,

        "session_binding":
            _session_binding(
                context,
                secret=secret,
            ),
    }


def _verified_owner_and_app(
    session_context: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:

    identity = (
        hosted_owner_identity_authority()
    )

    if (
        identity.get(
            "verification_state"
        )
        != "VERIFIED"
        or identity.get(
            "configured"
        )
        is not True
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_identity_not_verified"
        )

    record = identity.get(
        "record"
    )

    if not isinstance(
        record,
        Mapping,
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_identity_record_missing"
        )

    if (
        _clean(
            record.get(
                "role"
            )
        )
        != "owner"
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_identity_role_not_owner"
        )

    if not hmac.compare_digest(
        _clean(
            record.get(
                "username"
            )
        ),
        _clean(
            session_context.get(
                "username"
            )
        ),
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_identity_session_mismatch"
        )

    app = app_truth_by_id(
        OBSERVATORY_APP_ID
    )

    if not isinstance(
        app,
        Mapping,
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_app_truth_missing"
        )

    if (
        app.get(
            "launchable"
        )
        is not True
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_app_not_launchable"
        )

    if (
        app.get(
            "request_authorization_required"
        )
        is not True
    ):

        raise OwnerObservatoryHandoffError(
            "owner_observatory_request_authorization_boundary_missing"
        )

    return (
        dict(
            record
        ),
        dict(
            app
        ),
    )


def _connect_ledger(
    ledger: Path,
) -> sqlite3.Connection:

    ledger.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        str(
            ledger
        ),
        timeout=5.0,
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tower_owner_observatory_handoff (
            code_hash TEXT PRIMARY KEY,
            handoff_id TEXT UNIQUE NOT NULL,
            payload_json TEXT NOT NULL,
            payload_signature TEXT NOT NULL,
            issued_at_epoch REAL NOT NULL,
            expires_at_epoch REAL NOT NULL,
            consumed_at_epoch REAL,
            consumption_receipt_id TEXT
        )
        """
    )

    connection.commit()

    return connection


def issue_owner_observatory_handoff(
    session_context: Mapping[str, Any],
    *,
    now_epoch: float | None = None,
) -> dict[str, Any]:

    now = _now_epoch(
        now_epoch
    )

    secret, ledger = (
        _configuration()
    )

    session_truth = (
        _validate_session_context(
            session_context,
            secret=secret,
            now_epoch=now,
        )
    )

    identity, app = (
        _verified_owner_and_app(
            session_truth
        )
    )

    expires_at = min(
        now
        + HANDOFF_TTL_SECONDS,
        float(
            session_truth[
                "step_up_until_epoch"
            ]
        ),
    )

    if expires_at <= now:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_handoff_has_no_valid_lifetime"
        )

    raw_code = (
        secrets.token_urlsafe(
            32
        )
    )

    code_hash = hashlib.sha256(
        raw_code.encode(
            "utf-8"
        )
    ).hexdigest()

    handoff_id = (
        "tower_ob_handoff_"
        + secrets.token_hex(
            16
        )
    )

    payload = {
        "schema_version":
            HANDOFF_SCHEMA_VERSION,

        "handoff_id":
            handoff_id,

        "issuer":
            "tower",

        "app_id":
            OBSERVATORY_APP_ID,

        "target_path":
            OBSERVATORY_ENTRY_PATH,

        "owner_id":
            session_truth[
                "owner_id"
            ],

        "username":
            session_truth[
                "username"
            ],

        "identity_person_id":
            _clean(
                identity.get(
                    "person_id"
                )
            ),

        "identity_account_id":
            _clean(
                identity.get(
                    "account_id"
                )
            ),

        "session_binding":
            session_truth[
                "session_binding"
            ],

        "authenticated_at":
            session_truth[
                "authenticated_at"
            ],

        "step_up_until":
            session_truth[
                "step_up_until"
            ],

        "issued_at_epoch":
            now,

        "expires_at_epoch":
            expires_at,

        "app_launchable_verified":
            True,

        "request_authorization_required":
            True,

        "single_use":
            True,

        "broker_submission_authorized":
            False,

        "capital_movement_authorized":
            False,

        "manual_live_authorized":
            False,

        "live_auto_authorized":
            False,
    }

    signature = _sign(
        payload,
        secret=secret,
        purpose="handoff-signature",
    )

    connection = (
        _connect_ledger(
            ledger
        )
    )

    try:

        connection.execute(
            """
            INSERT INTO tower_owner_observatory_handoff (
                code_hash,
                handoff_id,
                payload_json,
                payload_signature,
                issued_at_epoch,
                expires_at_epoch,
                consumed_at_epoch,
                consumption_receipt_id
            )
            VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)
            """,
            (
                code_hash,
                handoff_id,
                _canonical_bytes(
                    payload
                ).decode(
                    "utf-8"
                ),
                signature,
                now,
                expires_at,
            ),
        )

        connection.commit()

    except Exception as exc:

        connection.rollback()

        raise OwnerObservatoryHandoffError(
            "owner_observatory_handoff_persist_failed"
        ) from exc

    finally:

        connection.close()

    return {
        "code":
            raw_code,

        "handoff_id":
            handoff_id,

        "app_id":
            OBSERVATORY_APP_ID,

        "target_path":
            OBSERVATORY_ENTRY_PATH,

        "expires_at_epoch":
            expires_at,

        "single_use":
            True,

        "raw_code_persisted":
            False,

        "ledger_path_exposed":
            False,

        "session_secret_exposed":
            False,
    }


def _build_access_receipt(
    *,
    payload: Mapping[str, Any],
    session_truth: Mapping[str, Any],
    secret: str,
    receipt_id: str,
    now_epoch: float,
) -> dict[str, Any]:

    expires_at = min(
        now_epoch
        + ACCESS_RECEIPT_MAX_TTL_SECONDS,
        float(
            session_truth[
                "step_up_until_epoch"
            ]
        ),
    )

    if expires_at <= now_epoch:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_access_receipt_has_no_valid_lifetime"
        )

    receipt_payload = {
        "schema_version":
            ACCESS_RECEIPT_SCHEMA_VERSION,

        "receipt_id":
            receipt_id,

        "source_handoff_id":
            payload[
                "handoff_id"
            ],

        "app_id":
            OBSERVATORY_APP_ID,

        "target_path":
            OBSERVATORY_ENTRY_PATH,

        "owner_id":
            session_truth[
                "owner_id"
            ],

        "username":
            session_truth[
                "username"
            ],

        "identity_person_id":
            payload.get(
                "identity_person_id"
            ),

        "identity_account_id":
            payload.get(
                "identity_account_id"
            ),

        "session_binding":
            session_truth[
                "session_binding"
            ],

        "issued_at_epoch":
            now_epoch,

        "expires_at_epoch":
            expires_at,

        "handoff_consumed":
            True,

        "request_authorization_verified":
            True,

        "broker_submission_authorized":
            False,

        "capital_movement_authorized":
            False,

        "manual_live_authorized":
            False,

        "live_auto_authorized":
            False,
    }

    signature = _sign(
        receipt_payload,
        secret=secret,
        purpose="access-receipt-signature",
    )

    return {
        "payload":
            receipt_payload,

        "signature":
            signature,

        "signature_algorithm":
            "HMAC-SHA256",

        "session_secret_exposed":
            False,
    }


def consume_owner_observatory_handoff(
    code: str,
    session_context: Mapping[str, Any],
    *,
    now_epoch: float | None = None,
) -> dict[str, Any]:

    raw_code = _clean(
        code
    )

    if not raw_code:

        raise OwnerObservatoryHandoffError(
            "owner_observatory_handoff_code_missing"
        )

    now = _now_epoch(
        now_epoch
    )

    secret, ledger = (
        _configuration()
    )

    session_truth = (
        _validate_session_context(
            session_context,
            secret=secret,
            now_epoch=now,
        )
    )

    # Reverify current authority at the receiving edge.
    _verified_owner_and_app(
        session_truth
    )

    code_hash = hashlib.sha256(
        raw_code.encode(
            "utf-8"
        )
    ).hexdigest()

    connection = (
        _connect_ledger(
            ledger
        )
    )

    try:

        connection.execute(
            "BEGIN IMMEDIATE"
        )

        row = connection.execute(
            """
            SELECT
                handoff_id,
                payload_json,
                payload_signature,
                issued_at_epoch,
                expires_at_epoch,
                consumed_at_epoch
            FROM tower_owner_observatory_handoff
            WHERE code_hash = ?
            """,
            (
                code_hash,
            ),
        ).fetchone()

        if row is None:

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_not_found"
            )

        (
            handoff_id,
            payload_json,
            payload_signature,
            issued_at_epoch,
            expires_at_epoch,
            consumed_at_epoch,
        ) = row

        if consumed_at_epoch is not None:

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_replay_rejected"
            )

        if float(
            expires_at_epoch
        ) <= now:

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_expired"
            )

        try:

            payload = json.loads(
                payload_json
            )

        except Exception as exc:

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_payload_invalid"
            ) from exc

        if not isinstance(
            payload,
            Mapping,
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_payload_invalid"
            )

        if not _signature_valid(
            payload,
            payload_signature,
            secret=secret,
            purpose="handoff-signature",
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_signature_invalid"
            )

        if (
            payload.get(
                "schema_version"
            )
            != HANDOFF_SCHEMA_VERSION
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_schema_invalid"
            )

        if (
            payload.get(
                "handoff_id"
            )
            != handoff_id
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_id_mismatch"
            )

        if (
            payload.get(
                "app_id"
            )
            != OBSERVATORY_APP_ID
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_app_mismatch"
            )

        if (
            payload.get(
                "target_path"
            )
            != OBSERVATORY_ENTRY_PATH
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_target_mismatch"
            )

        if not hmac.compare_digest(
            _clean(
                payload.get(
                    "session_binding"
                )
            ),
            session_truth[
                "session_binding"
            ],
        ):

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_session_binding_mismatch"
            )

        receipt_id = (
            "tower_ob_access_"
            + secrets.token_hex(
                16
            )
        )

        receipt = (
            _build_access_receipt(
                payload=payload,
                session_truth=session_truth,
                secret=secret,
                receipt_id=receipt_id,
                now_epoch=now,
            )
        )

        updated = connection.execute(
            """
            UPDATE tower_owner_observatory_handoff
            SET
                consumed_at_epoch = ?,
                consumption_receipt_id = ?
            WHERE
                code_hash = ?
                AND consumed_at_epoch IS NULL
            """,
            (
                now,
                receipt_id,
                code_hash,
            ),
        )

        if updated.rowcount != 1:

            raise OwnerObservatoryHandoffError(
                "owner_observatory_handoff_replay_rejected"
            )

        connection.commit()

        return receipt

    except OwnerObservatoryHandoffError:

        connection.rollback()

        raise

    except Exception as exc:

        connection.rollback()

        raise OwnerObservatoryHandoffError(
            "owner_observatory_handoff_consumption_failed"
        ) from exc

    finally:

        connection.close()


def validate_owner_observatory_access_receipt(
    receipt: Mapping[str, Any] | None,
    session_context: Mapping[str, Any],
    *,
    now_epoch: float | None = None,
) -> bool:

    if not isinstance(
        receipt,
        Mapping,
    ):

        return False

    now = _now_epoch(
        now_epoch
    )

    try:

        secret, _ledger = (
            _configuration()
        )

        session_truth = (
            _validate_session_context(
                session_context,
                secret=secret,
                now_epoch=now,
            )
        )

        # Access remains valid only while current owner/app truth
        # continues to satisfy the sealed launchability contract.
        _verified_owner_and_app(
            session_truth
        )

        payload = receipt.get(
            "payload"
        )

        signature = _clean(
            receipt.get(
                "signature"
            )
        )

        if not isinstance(
            payload,
            Mapping,
        ):

            return False

        if (
            payload.get(
                "schema_version"
            )
            != ACCESS_RECEIPT_SCHEMA_VERSION
        ):

            return False

        if (
            payload.get(
                "app_id"
            )
            != OBSERVATORY_APP_ID
        ):

            return False

        if (
            payload.get(
                "target_path"
            )
            != OBSERVATORY_ENTRY_PATH
        ):

            return False

        if (
            payload.get(
                "handoff_consumed"
            )
            is not True
        ):

            return False

        if (
            payload.get(
                "request_authorization_verified"
            )
            is not True
        ):

            return False

        expires_at = float(
            payload.get(
                "expires_at_epoch",
                0,
            )
        )

        if expires_at <= now:

            return False

        if not hmac.compare_digest(
            _clean(
                payload.get(
                    "session_binding"
                )
            ),
            session_truth[
                "session_binding"
            ],
        ):

            return False

        if not _signature_valid(
            payload,
            signature,
            secret=secret,
            purpose="access-receipt-signature",
        ):

            return False

        if (
            payload.get(
                "broker_submission_authorized"
            )
            is not False
        ):

            return False

        if (
            payload.get(
                "capital_movement_authorized"
            )
            is not False
        ):

            return False

        if (
            payload.get(
                "manual_live_authorized"
            )
            is not False
        ):

            return False

        if (
            payload.get(
                "live_auto_authorized"
            )
            is not False
        ):

            return False

        return True

    except Exception:

        return False
