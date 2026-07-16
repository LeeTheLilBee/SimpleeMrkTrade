"""Archive Vault GP801-GP810.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Authority Preparation Layer.

This layer prepares immutable, reference-only prerequisites for a later
Tower-owned recording-authority authorization gate.

It does not send or deliver an authority request, grant recording authority,
authorize decision recording, record an authorization decision, grant
owner-session creation authorization, create a session, authenticate an owner,
perform step-up, execute recovery, write production storage, or connect an
external provider.

Tower remains the protocol, identity, step-up, session, authorization-decision,
decision-recording, recording-authority, and recording-authority-authorization
owner.

Vault remains sealed memory.

Teller remains the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


PACK_START = 801
PACK_END = 810

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
    "RECORDING_AUTHORITY_PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_GATE_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_PREPARED_NOT_GRANTED"
)

PREPARATION_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
    "PREPARATION_SEALED_AUTHORITY_NOT_GRANTED"
)

REQUIRED_GATE_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_"
    "AUTHORITY_GATE_SEALED_AUTHORITY_NOT_GRANTED"
)

TOWER_DESTINATION = "TOWER"

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_OPERATIONS = frozenset(
    {
        "INTAKE_RECORDING_AUTHORITY_GATE_REFERENCE",
        "VERIFY_RECORDING_AUTHORITY_GATE_STATE",
        "PREPARE_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "PREPARE_RECORDING_AUTHORITY_SCOPE_REQUIREMENTS",
        "PREPARE_RECORDING_AUTHORITY_EVIDENCE_REQUIREMENTS",
        "PREPARE_TOWER_OWNER_SESSION_REQUIREMENTS",
        "PREPARE_SECOND_AUTHORITY_REQUIREMENTS",
        "PREPARE_RECORDING_AUTHORITY_REPLAY_REQUIREMENTS",
        "PREPARE_RECORDING_AUTHORITY_AUTHORIZATION_PREREQUISITES",
        "SEAL_RECORDING_AUTHORITY_PREPARATION_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "DELIVER_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "ACCEPT_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "GRANT_RECORDING_AUTHORITY",
        "AUTHORIZE_RECORDING_AUTHORITY",
        "AUTHORIZE_DECISION_RECORDING",
        "OPEN_RECORDING_AUTHORITY_AUTHORIZATION_GATE",
        "RECORD_AUTHORIZATION_DECISION",
        "RECORD_OWNER_SESSION_CREATION_AUTHORIZATION_DECISION",
        "GRANT_OWNER_SESSION_CREATION_AUTHORIZATION",
        "GRANT_TOWER_OWNER_SESSION_CREATION_AUTHORIZATION",
        "AUTHORIZE_OWNER_SESSION_CREATION",
        "AUTHORIZE_TOWER_OWNER_SESSION_CREATION",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "ISSUE_OWNER_SESSION",
        "ACTIVATE_OWNER_SESSION",
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "ISSUE_TOWER_OWNER_SESSION",
        "ACTIVATE_TOWER_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "RECOMMEND_OWNER_DECISION",
        "DEFAULT_OWNER_DECISION",
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "GRANT_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
        "MINT_AUTHORIZATION_TOKEN",
        "DELIVER_HANDOFF",
        "SEND_HANDOFF",
        "ACCEPT_HANDOFF",
        "ACTIVATE_SCOPE_FREEZE",
        "ACTIVATE_COMMIT_WINDOW",
        "ACTIVATE_EXECUTION_WINDOW",
        "OPEN_COMMIT_POINT",
        "ISSUE_RECOVERY_COMMIT_COMMAND",
        "EXECUTE_RECOVERY_COMMIT",
        "RESTORE_DATA",
        "MOUNT_PRODUCTION_STORAGE",
        "WRITE_PRODUCTION_STORAGE",
        "CONNECT_EXTERNAL_PROVIDER",
        "EXPOSE_RAW_MATERIAL",
        "DELETE_DATA",
        "DESTROY_DATA",
    }
)

PROHIBITED_METADATA_KEYS = frozenset(
    {
        "raw_path",
        "raw_paths",
        "path",
        "paths",
        "file_path",
        "filesystem_path",
        "raw_url",
        "raw_urls",
        "url",
        "urls",
        "download_url",
        "public_url",
        "token",
        "tokens",
        "authorization_token",
        "access_token",
        "refresh_token",
        "secret",
        "secrets",
        "password",
        "passwords",
        "credential",
        "credentials",
        "private_key",
        "raw_material",
        "raw_materials",
        "raw_payload",
        "raw_data",
        "provider_secret",
        "session_token",
        "session_cookie",
        "session_secret",
        "session_id",
        "owner_session_id",
        "decision_value",
        "selected_decision",
        "owner_decision",
        "decision_reason",
    }
)

SAFETY_STATE_FIELDS = (
    "recording_authority_authorization_request_sent",
    "recording_authority_authorization_request_delivered",
    "recording_authority_authorization_request_accepted",
    "recording_authority_granted",
    "recording_authority_authorized",
    "decision_recording_authorized",
    "authorization_decision_recorded",
    "owner_session_creation_authorization_decision_recorded",
    "owner_session_creation_authorization_granted",
    "tower_owner_session_creation_authorization_granted",
    "owner_session_creation_authorized",
    "tower_owner_session_creation_authorized",
    "owner_session_created",
    "owner_session_started",
    "owner_session_issued",
    "owner_session_activated",
    "tower_owner_session_created",
    "tower_owner_session_started",
    "tower_owner_session_issued",
    "tower_owner_session_activated",
    "owner_authenticated",
    "owner_stepped_up",
    "owner_decision_recording_gate_opened",
    "owner_decision_recommended",
    "owner_decision_defaulted",
    "owner_decision_selected",
    "owner_decision_invented",
    "owner_decision_recorded",
    "go_decision_granted",
    "recovery_authorization_issued",
    "recovery_authorization_granted",
    "authorization_token_issued",
    "authorization_token_minted",
    "handoff_delivered",
    "handoff_sent",
    "handoff_accepted",
    "scope_freeze_activated",
    "commit_window_activated",
    "execution_window_activated",
    "commit_point_opened",
    "recovery_commit_command_issued",
    "recovery_commit_executed",
    "restore_occurred",
    "production_mount_occurred",
    "production_write_occurred",
    "provider_connection_occurred",
    "prohibited_direct_access_occurred",
    "raw_material_exposed",
    "destructive_action_occurred",
)


class RecordingAuthorityPreparationError(ValueError):
    """Raised when GP801-GP810 input is unsafe."""


class RecordingAuthorityPreparationIntegrityError(RuntimeError):
    """Raised when sealed GP801-GP810 evidence fails verification."""


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="microseconds"
    )


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha256(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _required_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordingAuthorityPreparationError(
            f"{name} must be a non-empty string"
        )

    return value.strip()


def _find_blocked_keys(
    value: Any,
    *,
    location: str = "safe_metadata",
) -> list[str]:
    blocked: list[str] = []

    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            normalized = key_text.strip().lower()
            nested_location = f"{location}.{key_text}"

            if normalized in PROHIBITED_METADATA_KEYS:
                blocked.append(nested_location)

            blocked.extend(
                _find_blocked_keys(
                    nested,
                    location=nested_location,
                )
            )

    elif isinstance(value, list):
        for index, nested in enumerate(value):
            blocked.extend(
                _find_blocked_keys(
                    nested,
                    location=f"{location}[{index}]",
                )
            )

    return blocked


def _normalize_metadata(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise RecordingAuthorityPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise RecordingAuthorityPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    blocked = sorted(
        set(
            _find_blocked_keys(normalized)
        )
    )

    if blocked:
        raise RecordingAuthorityPreparationError(
            "safe_metadata contains prohibited raw, path, URL, token, "
            "secret, credential, session, authorization, decision, or "
            "decision-reason fields: "
            + ", ".join(blocked)
        )

    return normalized


def _false_safety_state() -> dict[str, bool]:
    return {
        field: False
        for field in SAFETY_STATE_FIELDS
    }


@dataclass(frozen=True)
class RecordingAuthorityPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    preparation_state: str

    preparation_sealed: bool
    authorization_request_prepared: bool
    recording_authority_granted: bool
    recording_authority_authorized: bool
    decision_recording_authorized: bool
    authorization_decision_recorded: bool

    owner_session_created: bool
    owner_authenticated: bool
    owner_stepped_up: bool

    immutable: bool
    append_only: bool
    idempotent_replay: bool


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityPreparationLayerService:
    """Persistent fail-closed GP801-GP810 preparation service."""

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            str(self.database_path)
        )

        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS
                vault_gp801_810_recording_authority_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    recording_authority_gate_id TEXT NOT NULL,
                    recording_authority_gate_hash TEXT NOT NULL,
                    recording_authority_gate_state TEXT NOT NULL
                        CHECK(
                            recording_authority_gate_state =
                            'AUTHORIZATION_DECISION_RECORDING_AUTHORITY_GATE_SEALED_AUTHORITY_NOT_GRANTED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    payload_json TEXT NOT NULL,
                    preparation_hash TEXT NOT NULL UNIQUE,
                    predecessor_preparation_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_AUTHORITY_PREPARED_NOT_GRANTED'
                        ),

                    preparation_state TEXT NOT NULL
                        CHECK(
                            preparation_state =
                            'AUTHORIZATION_DECISION_RECORDING_AUTHORITY_PREPARATION_SEALED_AUTHORITY_NOT_GRANTED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp801_810_recording_authority_preparation_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES
                        vault_gp801_810_recording_authority_preparations(
                            preparation_id
                        )
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp801_810_preparation_no_update
                BEFORE UPDATE
                ON vault_gp801_810_recording_authority_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP801-GP810 recording authority preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp801_810_preparation_no_delete
                BEFORE DELETE
                ON vault_gp801_810_recording_authority_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP801-GP810 recording authority preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp801_810_event_no_update
                BEFORE UPDATE
                ON vault_gp801_810_recording_authority_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP801-GP810 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp801_810_event_no_delete
                BEFORE DELETE
                ON vault_gp801_810_recording_authority_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP801-GP810 events are append-only'
                    );
                END;
                """
            )

    def seal_recording_authority_preparation(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        recording_authority_gate_id: str,
        recording_authority_gate_hash: str,
        recording_authority_gate_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> RecordingAuthorityPreparationReceipt:
        idempotency_key = _required_text(
            "idempotency_key",
            idempotency_key,
        )

        recovery_case_id = _required_text(
            "recovery_case_id",
            recovery_case_id,
        )

        owner_decision_record_id = _required_text(
            "owner_decision_record_id",
            owner_decision_record_id,
        )

        recording_authority_gate_id = _required_text(
            "recording_authority_gate_id",
            recording_authority_gate_id,
        )

        recording_authority_gate_hash = _required_text(
            "recording_authority_gate_hash",
            recording_authority_gate_hash,
        )

        recording_authority_gate_state = _required_text(
            "recording_authority_gate_state",
            recording_authority_gate_state,
        ).upper()

        if recording_authority_gate_state != REQUIRED_GATE_STATE:
            raise RecordingAuthorityPreparationError(
                "recording_authority_gate_state must preserve "
                "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
                "GATE_SEALED_AUTHORITY_NOT_GRANTED"
            )

        tower_authority_id = _required_text(
            "tower_authority_id",
            tower_authority_id,
        )

        tower_delivery_target_id = _required_text(
            "tower_delivery_target_id",
            tower_delivery_target_id,
        )

        target_environment = _required_text(
            "target_environment",
            target_environment,
        ).upper()

        if target_environment not in ALLOWED_ENVIRONMENTS:
            raise RecordingAuthorityPreparationError(
                "target_environment must be STAGING or PRODUCTION"
            )

        operations = self._normalize_operations(
            requested_operations
        )

        metadata = _normalize_metadata(
            safe_metadata
        )

        identity = {
            "layer_id": LAYER_ID,
            "idempotency_key": idempotency_key,
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "recording_authority_gate_id": recording_authority_gate_id,
            "recording_authority_gate_hash": recording_authority_gate_hash,
            "recording_authority_gate_state": recording_authority_gate_state,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        preparation_id = (
            "vault-gp801-810-"
            + _sha256(
                _canonical_json(identity)
            )[:24]
        )

        payload = {
            "gp801_preparation_shell": {
                "pack": "GP801",
                "preparation_id": preparation_id,
                "recommendation": CURRENT_RECOMMENDATION,
                "preparation_state": PREPARATION_STATE,
                "preparation_sealed": True,
                "authorization_request_prepared": True,
                "authorization_request_sent": False,
                "recording_authority_granted": False,
                "recording_authority_authorized": False,
                "decision_recording_authorized": False,
            },

            "gp802_gate_lineage_intake": {
                "pack": "GP802",
                "recording_authority_gate_id": recording_authority_gate_id,
                "recording_authority_gate_hash": recording_authority_gate_hash,
                "recording_authority_gate_state": recording_authority_gate_state,
                "required_gate_state": REQUIRED_GATE_STATE,
                "gate_reference_present": True,
                "gate_hash_present": True,
                "gate_sealed_in_lineage": True,
                "recording_authority_granted_in_lineage": False,
                "decision_recording_authorized_in_lineage": False,
            },

            "gp803_authorization_request_envelope": {
                "pack": "GP803",
                "envelope_type": (
                    "TOWER_RECORDING_AUTHORITY_AUTHORIZATION_"
                    "REQUEST_PREPARATION"
                ),
                "destination": TOWER_DESTINATION,
                "authorization_authority": TOWER_DESTINATION,
                "tower_authority_id": tower_authority_id,
                "tower_delivery_target_id": tower_delivery_target_id,
                "target_environment": target_environment,
                "request_prepared": True,
                "request_sent": False,
                "request_delivered": False,
                "request_accepted": False,
                "recording_authority_granted": False,
            },

            "gp804_scope_requirement_board": {
                "pack": "GP804",
                "recovery_case_binding_required": True,
                "owner_decision_binding_required": True,
                "recording_authority_gate_binding_required": True,
                "environment_binding_required": True,
                "tower_authority_binding_required": True,
                "tower_delivery_target_binding_required": True,
                "scope_reference_present": False,
                "scope_hash_present": False,
                "scope_bindings_verified": False,
                "authorization_ready": False,
            },

            "gp805_evidence_requirement_board": {
                "pack": "GP805",
                "decision_value_reference_required": True,
                "decision_reason_reference_required": True,
                "evidence_package_reference_required": True,
                "evidence_package_hash_required": True,
                "authentication_evidence_required": True,
                "step_up_evidence_required": True,
                "decision_value_reference_present": False,
                "decision_reason_reference_present": False,
                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "authentication_evidence_present": False,
                "step_up_evidence_present": False,
                "all_evidence_requirements_satisfied": False,
                "authorization_ready": False,
            },

            "gp806_tower_owner_session_board": {
                "pack": "GP806",
                "tower_owner_session_required": True,
                "tower_owner_authentication_required": True,
                "tower_owner_step_up_required": True,
                "session_purpose_binding_required": True,
                "session_case_binding_required": True,
                "session_environment_binding_required": True,
                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,
                "session_bindings_verified": False,
                "authorization_ready": False,
            },

            "gp807_second_authority_board": {
                "pack": "GP807",
                "owner_admin_approval_required": True,
                "second_authority_review_required": True,
                "dual_receipt_required": True,
                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,
                "authorization_ready": False,
            },

            "gp808_replay_protection_board": {
                "pack": "GP808",
                "authorization_nonce_reference_required": True,
                "authorization_idempotency_key_required": True,
                "single_authorization_required": True,
                "duplicate_authorization_rejected": True,
                "changed_replay_rejected": True,
                "cross_case_replay_rejected": True,
                "cross_decision_replay_rejected": True,
                "cross_environment_replay_rejected": True,
                "authorization_nonce_reference_present": False,
                "authorization_consumption_receipt_present": False,
                "replay_protection_verified": False,
                "authorization_ready": False,
            },

            "gp809_authorization_prerequisite_board": {
                "pack": "GP809",

                "gate_reference_present": True,
                "gate_hash_present": True,
                "authorization_request_prepared": True,

                "scope_reference_present": False,
                "scope_hash_present": False,
                "scope_bindings_verified": False,

                "decision_value_reference_present": False,
                "decision_reason_reference_present": False,
                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "all_evidence_requirements_satisfied": False,

                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,
                "session_bindings_verified": False,

                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,

                "authorization_nonce_reference_present": False,
                "authorization_consumption_receipt_present": False,
                "replay_protection_verified": False,

                "all_authorization_prerequisites_satisfied": False,
                "recording_authority_authorized": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_may_be_recorded": False,
                "authorization_decision_recorded": False,
                "owner_session_creation_authorized": False,
                "session_creation_may_proceed": False,
            },

            "gp810_checkpoint": {
                "pack": "GP810",
                "checkpoint_type": (
                    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
                    "PREPARATION_READINESS"
                ),
                "prior_pack_range": "GP791-GP800",
                "current_pack_range": "GP801-GP810",
                "recommendation": CURRENT_RECOMMENDATION,
                "preparation_state": PREPARATION_STATE,

                "preparation_sealed": True,

                "recording_authority_authorization_request_prepared": True,
                "recording_authority_authorization_request_sent": False,
                "recording_authority_authorization_request_delivered": False,
                "recording_authority_authorization_request_accepted": False,

                "scope_reference_present": False,
                "scope_hash_present": False,
                "scope_bindings_verified": False,

                "decision_value_reference_present": False,
                "decision_reason_reference_present": False,
                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "authentication_evidence_present": False,
                "step_up_evidence_present": False,
                "all_evidence_requirements_satisfied": False,

                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,
                "session_bindings_verified": False,

                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,

                "authorization_nonce_reference_present": False,
                "authorization_consumption_receipt_present": False,
                "replay_protection_verified": False,

                "recording_authority_authorized": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,
                "authorization_granted": False,

                "owner_session_creation_authorization_granted": False,
                "tower_owner_session_creation_authorization_granted": False,

                "owner_session_creation_authorized": False,
                "tower_owner_session_creation_authorized": False,

                "owner_session_created": False,
                "owner_session_started": False,
                "owner_session_issued": False,
                "owner_session_activated": False,

                "tower_owner_session_created": False,
                "tower_owner_session_started": False,
                "tower_owner_session_issued": False,
                "tower_owner_session_activated": False,

                "owner_decision_recording_gate_opened": False,

                "owner_decision_recommended": False,
                "owner_decision_defaulted": False,
                "owner_decision_selected": False,
                "owner_decision_invented": False,
                "owner_decision_recorded": False,

                "go_decision_granted": False,

                "recovery_authorization_issued": False,
                "recovery_authorization_granted": False,

                "authorization_token_issued": False,
                "authorization_token_minted": False,

                "handoff_delivered": False,

                "scope_freeze_activated": False,
                "commit_window_activated": False,
                "execution_window_activated": False,
                "commit_point_opened": False,

                "recovery_commit_command_issued": False,
                "recovery_commit_executed": False,

                "restore_occurred": False,
                "production_mount_occurred": False,
                "production_write_occurred": False,

                "provider_connection_occurred": False,
                "raw_material_exposed": False,
                "destructive_action_occurred": False,

                "safety_state": _false_safety_state(),

                "next_gate": (
                    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
                    "AUTHORIZATION_GATE"
                ),
            },

            "requested_operations": operations,
            "safe_metadata": metadata,
        }

        payload_json = _canonical_json(payload)
        preparation_hash = _sha256(payload_json)
        created_at = _utc_now()

        with self._connect() as connection:
            connection.execute(
                "BEGIN IMMEDIATE"
            )

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp801_810_recording_authority_preparations
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["payload_json"] != payload_json
                    or existing["preparation_hash"] != preparation_hash
                ):
                    raise RecordingAuthorityPreparationError(
                        "idempotency_key already exists with different "
                        "immutable recording-authority-preparation inputs"
                    )

                return self._receipt(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp801_810_recording_authority_preparations
                ORDER BY rowid DESC
                LIMIT 1
                """
            ).fetchone()

            predecessor_hash = (
                predecessor["preparation_hash"]
                if predecessor
                else None
            )

            connection.execute(
                """
                INSERT INTO vault_gp801_810_recording_authority_preparations (
                    preparation_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    recording_authority_gate_id,
                    recording_authority_gate_hash,
                    recording_authority_gate_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    destination,
                    payload_json,
                    preparation_hash,
                    predecessor_preparation_hash,
                    recommendation,
                    preparation_state,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    preparation_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    recording_authority_gate_id,
                    recording_authority_gate_hash,
                    recording_authority_gate_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    payload_json,
                    preparation_hash,
                    predecessor_hash,
                    CURRENT_RECOMMENDATION,
                    PREPARATION_STATE,
                    created_at,
                ),
            )

            self._append_event(
                connection,
                preparation_id=preparation_id,
                event_type=(
                    "GP801_810_RECORDING_AUTHORITY_"
                    "PREPARATION_SEALED"
                ),
                event_payload={
                    "preparation_hash": preparation_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "preparation_state": PREPARATION_STATE,
                    "authorization_request_prepared": True,
                    "authorization_request_sent": False,
                    "recording_authority_authorized": False,
                    "recording_authority_granted": False,
                    "decision_recording_authorized": False,
                    "authorization_decision_recorded": False,
                    "owner_session_created": False,
                    "owner_authenticated": False,
                    "owner_stepped_up": False,
                    "owner_decision_recorded": False,
                    "recovery_commit_executed": False,
                    "production_write_occurred": False,
                    "provider_connection_occurred": False,
                    "destructive_action_occurred": False,
                },
            )

            row = connection.execute(
                """
                SELECT *
                FROM vault_gp801_810_recording_authority_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

            if row is None:
                raise RecordingAuthorityPreparationIntegrityError(
                    "recording authority preparation failed to persist"
                )

            return self._receipt(
                row,
                idempotent_replay=False,
            )

    def get_preparation(
        self,
        preparation_id: str,
    ) -> dict[str, Any]:
        preparation_id = _required_text(
            "preparation_id",
            preparation_id,
        )

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM vault_gp801_810_recording_authority_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP801-GP810 preparation: {preparation_id}"
            )

        result = dict(row)

        result["payload"] = json.loads(
            result.pop("payload_json")
        )

        return result

    def list_events(
        self,
        preparation_id: str,
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM vault_gp801_810_recording_authority_preparation_events
                WHERE preparation_id = ?
                ORDER BY event_id ASC
                """,
                (preparation_id,),
            ).fetchall()

        events = []

        for row in rows:
            event = dict(row)

            event["event_payload"] = json.loads(
                event.pop("event_payload_json")
            )

            events.append(event)

        return events

    def verify_preparation(
        self,
        preparation_id: str,
    ) -> dict[str, Any]:
        record = self.get_preparation(
            preparation_id
        )

        canonical_payload = _canonical_json(
            record["payload"]
        )

        if _sha256(canonical_payload) != record["preparation_hash"]:
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation destination is not Tower"
            )

        if (
            record["recording_authority_gate_state"]
            != REQUIRED_GATE_STATE
        ):
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority gate lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation recommendation mismatch"
            )

        if record["preparation_state"] != PREPARATION_STATE:
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation state mismatch"
            )

        payload = record["payload"]
        checkpoint = payload["gp810_checkpoint"]

        if checkpoint["preparation_sealed"] is not True:
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation is not sealed"
            )

        if (
            checkpoint[
                "recording_authority_authorization_request_prepared"
            ]
            is not True
        ):
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority authorization request was not prepared"
            )

        prohibited_true = (
            "recording_authority_authorization_request_sent",
            "recording_authority_authorization_request_delivered",
            "recording_authority_authorization_request_accepted",
            "scope_reference_present",
            "scope_hash_present",
            "scope_bindings_verified",
            "decision_value_reference_present",
            "decision_reason_reference_present",
            "evidence_package_reference_present",
            "evidence_package_hash_present",
            "authentication_evidence_present",
            "step_up_evidence_present",
            "all_evidence_requirements_satisfied",
            "tower_owner_session_present",
            "owner_authenticated",
            "owner_stepped_up",
            "session_bindings_verified",
            "owner_admin_approval_granted",
            "second_authority_review_granted",
            "dual_receipt_satisfied",
            "authorization_nonce_reference_present",
            "authorization_consumption_receipt_present",
            "replay_protection_verified",
            "recording_authority_authorized",
            "recording_authority_granted",
            "decision_recording_authorized",
            "authorization_decision_recorded",
            "authorization_granted",
            "owner_session_creation_authorization_granted",
            "tower_owner_session_creation_authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
            "owner_session_created",
            "owner_session_started",
            "owner_session_issued",
            "owner_session_activated",
            "tower_owner_session_created",
            "tower_owner_session_started",
            "tower_owner_session_issued",
            "tower_owner_session_activated",
            "owner_decision_recording_gate_opened",
            "owner_decision_recommended",
            "owner_decision_defaulted",
            "owner_decision_selected",
            "owner_decision_invented",
            "owner_decision_recorded",
            "go_decision_granted",
            "recovery_authorization_issued",
            "recovery_authorization_granted",
            "authorization_token_issued",
            "authorization_token_minted",
            "handoff_delivered",
            "scope_freeze_activated",
            "commit_window_activated",
            "execution_window_activated",
            "commit_point_opened",
            "recovery_commit_command_issued",
            "recovery_commit_executed",
            "restore_occurred",
            "production_mount_occurred",
            "production_write_occurred",
            "provider_connection_occurred",
            "raw_material_exposed",
            "destructive_action_occurred",
        )

        unsafe = [
            field
            for field in prohibited_true
            if checkpoint[field] is True
        ]

        if unsafe:
            raise RecordingAuthorityPreparationIntegrityError(
                "unsafe recording authority preparation state: "
                + ", ".join(unsafe)
            )

        prerequisites = payload[
            "gp809_authorization_prerequisite_board"
        ]

        prerequisite_false_fields = (
            "scope_reference_present",
            "scope_hash_present",
            "scope_bindings_verified",
            "decision_value_reference_present",
            "decision_reason_reference_present",
            "evidence_package_reference_present",
            "evidence_package_hash_present",
            "all_evidence_requirements_satisfied",
            "tower_owner_session_present",
            "owner_authenticated",
            "owner_stepped_up",
            "session_bindings_verified",
            "owner_admin_approval_granted",
            "second_authority_review_granted",
            "dual_receipt_satisfied",
            "authorization_nonce_reference_present",
            "authorization_consumption_receipt_present",
            "replay_protection_verified",
            "all_authorization_prerequisites_satisfied",
            "recording_authority_authorized",
            "recording_authority_granted",
            "decision_recording_authorized",
            "authorization_decision_may_be_recorded",
            "authorization_decision_recorded",
            "owner_session_creation_authorized",
            "session_creation_may_proceed",
        )

        invalid_prerequisites = [
            field
            for field in prerequisite_false_fields
            if prerequisites[field] is True
        ]

        if invalid_prerequisites:
            raise RecordingAuthorityPreparationIntegrityError(
                "unsafe recording authority prerequisite state: "
                + ", ".join(invalid_prerequisites)
            )

        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation safety-field mismatch"
            )

        unsafe_safety = [
            field
            for field, value in safety_state.items()
            if value is True
        ]

        if unsafe_safety:
            raise RecordingAuthorityPreparationIntegrityError(
                "unsafe completed actions: "
                + ", ".join(unsafe_safety)
            )

        events = self.list_events(
            preparation_id
        )

        if not events:
            raise RecordingAuthorityPreparationIntegrityError(
                "recording authority preparation has no append-only events"
            )

        previous_event_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise RecordingAuthorityPreparationIntegrityError(
                    "recording authority event predecessor mismatch"
                )

            material = {
                "preparation_id": event["preparation_id"],
                "event_type": event["event_type"],
                "event_payload": event["event_payload"],
                "previous_event_hash": event["previous_event_hash"],
                "created_at": event["created_at"],
            }

            expected_hash = _sha256(
                _canonical_json(material)
            )

            if expected_hash != event["event_hash"]:
                raise RecordingAuthorityPreparationIntegrityError(
                    "recording authority event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP801-GP810",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "recording_authority_gate_lineage_valid": True,

            "preparation_sealed": True,

            "authorization_request_prepared": True,
            "authorization_request_sent": False,
            "authorization_request_delivered": False,
            "authorization_request_accepted": False,

            "scope_reference_present": False,
            "scope_bindings_verified": False,

            "decision_value_reference_present": False,
            "decision_reason_reference_present": False,
            "evidence_package_reference_present": False,
            "all_evidence_requirements_satisfied": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,
            "session_bindings_verified": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "authorization_nonce_reference_present": False,
            "authorization_consumption_receipt_present": False,
            "replay_protection_verified": False,

            "recording_authority_authorized": False,
            "recording_authority_granted": False,
            "decision_recording_authorized": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,

            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,

            "owner_session_created": False,
            "owner_session_started": False,

            "owner_decision_recording_gate_open": False,
            "owner_decision_recorded": False,

            "go_decision_granted": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,

            "handoff_delivered": False,
            "recovery_commit_command_issued": False,
            "recovery_commit_executed": False,

            "restore_occurred": False,
            "production_write_occurred": False,
            "provider_connection_occurred": False,
            "raw_material_exposed": False,
            "destructive_action_occurred": False,

            "unsafe_completed_actions": [],
            "recommendation": CURRENT_RECOMMENDATION,
            "verified": True,
        }

    def _normalize_operations(
        self,
        requested_operations: Sequence[str] | None,
    ) -> list[str]:
        if requested_operations is None:
            return sorted(
                ALLOWED_OPERATIONS
            )

        if isinstance(
            requested_operations,
            (str, bytes),
        ):
            raise RecordingAuthorityPreparationError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise RecordingAuthorityPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise RecordingAuthorityPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise RecordingAuthorityPreparationError(
                "requested_operations cannot be empty"
            )

        return sorted(
            set(operations)
        )

    def _append_event(
        self,
        connection: sqlite3.Connection,
        *,
        preparation_id: str,
        event_type: str,
        event_payload: Mapping[str, Any],
    ) -> str:
        predecessor = connection.execute(
            """
            SELECT event_hash
            FROM vault_gp801_810_recording_authority_preparation_events
            WHERE preparation_id = ?
            ORDER BY event_id DESC
            LIMIT 1
            """,
            (preparation_id,),
        ).fetchone()

        previous_event_hash = (
            predecessor["event_hash"]
            if predecessor
            else None
        )

        created_at = _utc_now()

        normalized_payload = json.loads(
            _canonical_json(
                dict(event_payload)
            )
        )

        material = {
            "preparation_id": preparation_id,
            "event_type": event_type,
            "event_payload": normalized_payload,
            "previous_event_hash": previous_event_hash,
            "created_at": created_at,
        }

        event_hash = _sha256(
            _canonical_json(material)
        )

        connection.execute(
            """
            INSERT INTO
                vault_gp801_810_recording_authority_preparation_events (
                    preparation_id,
                    event_type,
                    event_payload_json,
                    previous_event_hash,
                    event_hash,
                    created_at
                )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                preparation_id,
                event_type,
                _canonical_json(normalized_payload),
                previous_event_hash,
                event_hash,
                created_at,
            ),
        )

        return event_hash

    def _receipt(
        self,
        row: sqlite3.Row,
        *,
        idempotent_replay: bool,
    ) -> RecordingAuthorityPreparationReceipt:
        return RecordingAuthorityPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            preparation_state=row["preparation_state"],

            preparation_sealed=True,
            authorization_request_prepared=True,
            recording_authority_granted=False,
            recording_authority_authorized=False,
            decision_recording_authorized=False,
            authorization_decision_recorded=False,

            owner_session_created=False,
            owner_authenticated=False,
            owner_stepped_up=False,

            immutable=True,
            append_only=True,
            idempotent_replay=idempotent_replay,
        )


__all__ = [
    "ALLOWED_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "PACK_END",
    "PACK_START",
    "PREPARATION_STATE",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_GATE_STATE",
    "RecordingAuthorityPreparationError",
    "RecordingAuthorityPreparationIntegrityError",
    "RecordingAuthorityPreparationReceipt",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityPreparationLayerService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
