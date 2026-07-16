"""Archive Vault GP791-GP800.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Authority Gate.

This layer seals a fail-closed gate around any later Tower-owned grant of
authorization-decision recording authority.

It does not grant recording authority, authorize decision recording, accept or
record a decision, grant owner-session creation authorization, create a
session, authenticate an owner, perform step-up, execute recovery, write
production storage, or connect an external provider.

Tower remains the protocol, identity, step-up, session, authorization-decision,
decision-recording, and recording-authority owner.

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


PACK_START = 791
PACK_END = 800

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
    "RECORDING_AUTHORITY_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_PREPARED_NOT_RECORDED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_GATE_SEALED"
)

GATE_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_"
    "AUTHORITY_GATE_SEALED_AUTHORITY_NOT_GRANTED"
)

REQUIRED_PREPARATION_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_PREPARATION_SEALED_NOT_AUTHORIZED"
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
        "INTAKE_RECORDING_PREPARATION_REFERENCE",
        "VERIFY_RECORDING_PREPARATION_STATE",
        "VERIFY_RECORDING_AUTHORITY_REQUEST_PREPARED",
        "VERIFY_DECISION_REFERENCE_REQUIREMENTS",
        "VERIFY_EVIDENCE_BINDING_REQUIREMENTS",
        "VERIFY_TOWER_OWNER_SESSION_REQUIREMENTS",
        "VERIFY_RECORDING_CONSUMPTION_REQUIREMENTS",
        "EVALUATE_RECORDING_AUTHORITY_BLOCKERS",
        "SEAL_RECORDING_AUTHORITY_GATE",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_RECORDING_AUTHORITY_REQUEST",
        "DELIVER_RECORDING_AUTHORITY_REQUEST",
        "ACCEPT_RECORDING_AUTHORITY_REQUEST",
        "GRANT_RECORDING_AUTHORITY",
        "AUTHORIZE_DECISION_RECORDING",
        "OPEN_DECISION_RECORDING_AUTHORITY_GATE",
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
    "recording_authority_request_sent",
    "recording_authority_request_delivered",
    "recording_authority_request_accepted",
    "recording_authority_granted",
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


class DecisionRecordingAuthorityGateError(ValueError):
    """Raised when GP791-GP800 gate input is unsafe."""


class DecisionRecordingAuthorityGateIntegrityError(RuntimeError):
    """Raised when sealed GP791-GP800 evidence fails verification."""


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
        raise DecisionRecordingAuthorityGateError(
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
        raise DecisionRecordingAuthorityGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise DecisionRecordingAuthorityGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    blocked = sorted(
        set(_find_blocked_keys(normalized))
    )

    if blocked:
        raise DecisionRecordingAuthorityGateError(
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
class DecisionRecordingAuthorityGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    recording_authority_granted: bool
    decision_recording_authorized: bool
    authorization_decision_recorded: bool
    authorization_granted: bool

    owner_session_created: bool
    owner_session_started: bool
    owner_authenticated: bool
    owner_stepped_up: bool

    immutable: bool
    append_only: bool
    idempotent_replay: bool


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityGateService:
    """Persistent fail-closed GP791-GP800 recording-authority gate."""

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
                vault_gp791_800_recording_authority_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    recording_preparation_id TEXT NOT NULL,
                    recording_preparation_hash TEXT NOT NULL,
                    recording_preparation_state TEXT NOT NULL
                        CHECK(
                            recording_preparation_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_PREPARATION_SEALED_NOT_AUTHORIZED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    payload_json TEXT NOT NULL,
                    gate_hash TEXT NOT NULL UNIQUE,
                    predecessor_gate_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_AUTHORITY_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'AUTHORIZATION_DECISION_RECORDING_AUTHORITY_GATE_SEALED_AUTHORITY_NOT_GRANTED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp791_800_recording_authority_gate_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES vault_gp791_800_recording_authority_gates(
                            gate_id
                        )
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp791_800_gate_no_update
                BEFORE UPDATE
                ON vault_gp791_800_recording_authority_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP791-GP800 recording authority gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp791_800_gate_no_delete
                BEFORE DELETE
                ON vault_gp791_800_recording_authority_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP791-GP800 recording authority gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp791_800_event_no_update
                BEFORE UPDATE
                ON vault_gp791_800_recording_authority_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP791-GP800 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp791_800_event_no_delete
                BEFORE DELETE
                ON vault_gp791_800_recording_authority_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP791-GP800 events are append-only'
                    );
                END;
                """
            )

    def seal_recording_authority_gate(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        recording_preparation_id: str,
        recording_preparation_hash: str,
        recording_preparation_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> DecisionRecordingAuthorityGateReceipt:
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

        recording_preparation_id = _required_text(
            "recording_preparation_id",
            recording_preparation_id,
        )

        recording_preparation_hash = _required_text(
            "recording_preparation_hash",
            recording_preparation_hash,
        )

        recording_preparation_state = _required_text(
            "recording_preparation_state",
            recording_preparation_state,
        ).upper()

        if recording_preparation_state != REQUIRED_PREPARATION_STATE:
            raise DecisionRecordingAuthorityGateError(
                "recording_preparation_state must preserve "
                "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
                "RECORDING_PREPARATION_SEALED_NOT_AUTHORIZED"
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
            raise DecisionRecordingAuthorityGateError(
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
            "recording_preparation_id": recording_preparation_id,
            "recording_preparation_hash": recording_preparation_hash,
            "recording_preparation_state": recording_preparation_state,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        gate_id = (
            "vault-gp791-800-"
            + _sha256(
                _canonical_json(identity)
            )[:24]
        )

        payload = {
            "gp791_gate_shell": {
                "pack": "GP791",
                "gate_id": gate_id,
                "recommendation": CURRENT_RECOMMENDATION,
                "gate_state": GATE_STATE,
                "gate_sealed": True,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,
                "authorization_granted": False,
            },

            "gp792_preparation_lineage_gate": {
                "pack": "GP792",
                "recording_preparation_id": recording_preparation_id,
                "recording_preparation_hash": recording_preparation_hash,
                "recording_preparation_state": recording_preparation_state,
                "required_preparation_state": REQUIRED_PREPARATION_STATE,
                "preparation_reference_present": True,
                "preparation_hash_present": True,
                "preparation_sealed_in_lineage": True,
                "recording_authority_granted_in_lineage": False,
                "decision_recording_authorized_in_lineage": False,
                "authorization_decision_recorded_in_lineage": False,
            },

            "gp793_recording_authority_request_gate": {
                "pack": "GP793",
                "destination": TOWER_DESTINATION,
                "recording_authority": TOWER_DESTINATION,
                "tower_authority_id": tower_authority_id,
                "tower_delivery_target_id": tower_delivery_target_id,
                "request_prepared": True,
                "request_sent": False,
                "request_delivered": False,
                "request_accepted": False,
                "recording_authority_granted": False,
            },

            "gp794_decision_reference_gate": {
                "pack": "GP794",
                "decision_value_reference_required": True,
                "decision_reason_reference_required": True,
                "decision_value_reference_present": False,
                "decision_reason_reference_present": False,
                "decision_value_present": False,
                "decision_value_selected": False,
                "decision_value_invented": False,
                "recording_authority_blocked": True,
            },

            "gp795_evidence_binding_gate": {
                "pack": "GP795",
                "evidence_package_reference_required": True,
                "evidence_package_hash_required": True,
                "scope_binding_required": True,
                "lifetime_binding_required": True,
                "replay_binding_required": True,
                "authentication_binding_required": True,
                "step_up_binding_required": True,
                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "all_evidence_bindings_verified": False,
                "recording_authority_blocked": True,
            },

            "gp796_tower_owner_session_gate": {
                "pack": "GP796",
                "tower_owner_session_required": True,
                "owner_authentication_required": True,
                "owner_step_up_required": True,
                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,
                "recording_authority_blocked": True,
            },

            "gp797_second_authority_gate": {
                "pack": "GP797",
                "owner_admin_approval_required": True,
                "second_authority_review_required": True,
                "dual_receipt_required": True,
                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,
                "recording_authority_blocked": True,
            },

            "gp798_recording_consumption_gate": {
                "pack": "GP798",
                "decision_nonce_reference_required": True,
                "recording_consumption_receipt_required": True,
                "single_recording_required": True,
                "duplicate_recording_rejected": True,
                "changed_replay_rejected": True,
                "cross_case_replay_rejected": True,
                "cross_environment_replay_rejected": True,
                "decision_nonce_reference_present": False,
                "recording_consumption_receipt_present": False,
                "replay_protection_verified": False,
                "recording_authority_blocked": True,
            },

            "gp799_recording_authority_blocker_matrix": {
                "pack": "GP799",

                "preparation_reference_present": True,
                "preparation_hash_present": True,
                "recording_authority_request_prepared": True,

                "decision_value_reference_present": False,
                "decision_reason_reference_present": False,

                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "all_evidence_bindings_verified": False,

                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,

                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,

                "decision_nonce_reference_present": False,
                "recording_consumption_receipt_present": False,
                "replay_protection_verified": False,

                "all_recording_authority_prerequisites_satisfied": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_may_be_recorded": False,
                "authorization_decision_recorded": False,
                "authorization_granted": False,

                "owner_session_creation_authorized": False,
                "tower_owner_session_creation_authorized": False,
                "session_creation_may_proceed": False,
                "owner_decision_recording_gate_may_open": False,
            },

            "gp800_checkpoint": {
                "pack": "GP800",
                "checkpoint_type": (
                    "AUTHORIZATION_DECISION_RECORDING_"
                    "AUTHORITY_GATE_READINESS"
                ),
                "prior_pack_range": "GP781-GP790",
                "current_pack_range": "GP791-GP800",
                "recommendation": CURRENT_RECOMMENDATION,
                "gate_state": GATE_STATE,

                "gate_sealed": True,

                "recording_authority_request_prepared": True,
                "recording_authority_request_sent": False,
                "recording_authority_request_delivered": False,
                "recording_authority_request_accepted": False,

                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,
                "authorization_granted": False,

                "decision_value_reference_present": False,
                "decision_reason_reference_present": False,

                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "all_evidence_bindings_verified": False,

                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,

                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,

                "decision_nonce_reference_present": False,
                "recording_consumption_receipt_present": False,
                "replay_protection_verified": False,

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
                    "AUTHORIZATION_DECISION_RECORDING_"
                    "AUTHORITY_PREPARATION_LAYER"
                ),
            },

            "requested_operations": operations,
            "safe_metadata": metadata,
        }

        payload_json = _canonical_json(payload)
        gate_hash = _sha256(payload_json)
        created_at = _utc_now()

        with self._connect() as connection:
            connection.execute(
                "BEGIN IMMEDIATE"
            )

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp791_800_recording_authority_gates
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["payload_json"] != payload_json
                    or existing["gate_hash"] != gate_hash
                ):
                    raise DecisionRecordingAuthorityGateError(
                        "idempotency_key already exists with different "
                        "immutable recording-authority-gate inputs"
                    )

                return self._receipt(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp791_800_recording_authority_gates
                ORDER BY rowid DESC
                LIMIT 1
                """
            ).fetchone()

            predecessor_hash = (
                predecessor["gate_hash"]
                if predecessor
                else None
            )

            connection.execute(
                """
                INSERT INTO vault_gp791_800_recording_authority_gates (
                    gate_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    recording_preparation_id,
                    recording_preparation_hash,
                    recording_preparation_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    destination,
                    payload_json,
                    gate_hash,
                    predecessor_gate_hash,
                    recommendation,
                    gate_state,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    gate_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    recording_preparation_id,
                    recording_preparation_hash,
                    recording_preparation_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    payload_json,
                    gate_hash,
                    predecessor_hash,
                    CURRENT_RECOMMENDATION,
                    GATE_STATE,
                    created_at,
                ),
            )

            self._append_event(
                connection,
                gate_id=gate_id,
                event_type=(
                    "GP791_800_RECORDING_AUTHORITY_GATE_SEALED"
                ),
                event_payload={
                    "gate_hash": gate_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "gate_state": GATE_STATE,
                    "gate_sealed": True,
                    "recording_authority_granted": False,
                    "decision_recording_authorized": False,
                    "authorization_decision_recorded": False,
                    "authorization_granted": False,
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
                FROM vault_gp791_800_recording_authority_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

            if row is None:
                raise DecisionRecordingAuthorityGateIntegrityError(
                    "recording authority gate failed to persist"
                )

            return self._receipt(
                row,
                idempotent_replay=False,
            )

    def get_gate(
        self,
        gate_id: str,
    ) -> dict[str, Any]:
        gate_id = _required_text(
            "gate_id",
            gate_id,
        )

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM vault_gp791_800_recording_authority_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP791-GP800 gate: {gate_id}"
            )

        result = dict(row)

        result["payload"] = json.loads(
            result.pop("payload_json")
        )

        return result

    def list_events(
        self,
        gate_id: str,
    ) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM vault_gp791_800_recording_authority_gate_events
                WHERE gate_id = ?
                ORDER BY event_id ASC
                """,
                (gate_id,),
            ).fetchall()

        events = []

        for row in rows:
            event = dict(row)

            event["event_payload"] = json.loads(
                event.pop("event_payload_json")
            )

            events.append(event)

        return events

    def verify_gate(
        self,
        gate_id: str,
    ) -> dict[str, Any]:
        record = self.get_gate(
            gate_id
        )

        canonical_payload = _canonical_json(
            record["payload"]
        )

        if _sha256(canonical_payload) != record["gate_hash"]:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority gate payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority gate destination is not Tower"
            )

        if (
            record["recording_preparation_state"]
            != REQUIRED_PREPARATION_STATE
        ):
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording preparation lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority gate recommendation mismatch"
            )

        if record["gate_state"] != GATE_STATE:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority gate state mismatch"
            )

        payload = record["payload"]
        checkpoint = payload["gp800_checkpoint"]

        if checkpoint["gate_sealed"] is not True:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority gate is not sealed"
            )

        if (
            checkpoint["recording_authority_request_prepared"]
            is not True
        ):
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority request was not prepared"
            )

        prohibited_true = (
            "recording_authority_request_sent",
            "recording_authority_request_delivered",
            "recording_authority_request_accepted",
            "recording_authority_granted",
            "decision_recording_authorized",
            "authorization_decision_recorded",
            "authorization_granted",
            "decision_value_reference_present",
            "decision_reason_reference_present",
            "evidence_package_reference_present",
            "evidence_package_hash_present",
            "all_evidence_bindings_verified",
            "tower_owner_session_present",
            "owner_authenticated",
            "owner_stepped_up",
            "owner_admin_approval_granted",
            "second_authority_review_granted",
            "dual_receipt_satisfied",
            "decision_nonce_reference_present",
            "recording_consumption_receipt_present",
            "replay_protection_verified",
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
            raise DecisionRecordingAuthorityGateIntegrityError(
                "unsafe recording authority gate state: "
                + ", ".join(unsafe)
            )

        blockers = payload[
            "gp799_recording_authority_blocker_matrix"
        ]

        blocker_false_fields = (
            "decision_value_reference_present",
            "decision_reason_reference_present",
            "evidence_package_reference_present",
            "evidence_package_hash_present",
            "all_evidence_bindings_verified",
            "tower_owner_session_present",
            "owner_authenticated",
            "owner_stepped_up",
            "owner_admin_approval_granted",
            "second_authority_review_granted",
            "dual_receipt_satisfied",
            "decision_nonce_reference_present",
            "recording_consumption_receipt_present",
            "replay_protection_verified",
            "all_recording_authority_prerequisites_satisfied",
            "recording_authority_granted",
            "decision_recording_authorized",
            "authorization_decision_may_be_recorded",
            "authorization_decision_recorded",
            "authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
            "session_creation_may_proceed",
            "owner_decision_recording_gate_may_open",
        )

        invalid_blockers = [
            field
            for field in blocker_false_fields
            if blockers[field] is True
        ]

        if invalid_blockers:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "unsafe recording authority blocker state: "
                + ", ".join(invalid_blockers)
            )

        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority safety field mismatch"
            )

        unsafe_safety = [
            field
            for field, value in safety_state.items()
            if value is True
        ]

        if unsafe_safety:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "unsafe completed actions: "
                + ", ".join(unsafe_safety)
            )

        events = self.list_events(
            gate_id
        )

        if not events:
            raise DecisionRecordingAuthorityGateIntegrityError(
                "recording authority gate has no append-only events"
            )

        previous_event_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise DecisionRecordingAuthorityGateIntegrityError(
                    "recording authority event predecessor mismatch"
                )

            material = {
                "gate_id": event["gate_id"],
                "event_type": event["event_type"],
                "event_payload": event["event_payload"],
                "previous_event_hash": event["previous_event_hash"],
                "created_at": event["created_at"],
            }

            expected_hash = _sha256(
                _canonical_json(material)
            )

            if expected_hash != event["event_hash"]:
                raise DecisionRecordingAuthorityGateIntegrityError(
                    "recording authority event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP791-GP800",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "recording_preparation_lineage_valid": True,

            "gate_sealed": True,

            "recording_authority_request_prepared": True,
            "recording_authority_request_sent": False,
            "recording_authority_request_delivered": False,
            "recording_authority_request_accepted": False,

            "recording_authority_granted": False,
            "decision_recording_authorized": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,

            "decision_value_reference_present": False,
            "decision_reason_reference_present": False,
            "evidence_package_reference_present": False,
            "all_evidence_bindings_verified": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "decision_nonce_reference_present": False,
            "recording_consumption_receipt_present": False,
            "replay_protection_verified": False,

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
            raise DecisionRecordingAuthorityGateError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise DecisionRecordingAuthorityGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise DecisionRecordingAuthorityGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise DecisionRecordingAuthorityGateError(
                "requested_operations cannot be empty"
            )

        return sorted(
            set(operations)
        )

    def _append_event(
        self,
        connection: sqlite3.Connection,
        *,
        gate_id: str,
        event_type: str,
        event_payload: Mapping[str, Any],
    ) -> str:
        predecessor = connection.execute(
            """
            SELECT event_hash
            FROM vault_gp791_800_recording_authority_gate_events
            WHERE gate_id = ?
            ORDER BY event_id DESC
            LIMIT 1
            """,
            (gate_id,),
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
            "gate_id": gate_id,
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
            INSERT INTO vault_gp791_800_recording_authority_gate_events (
                gate_id,
                event_type,
                event_payload_json,
                previous_event_hash,
                event_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                gate_id,
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
    ) -> DecisionRecordingAuthorityGateReceipt:
        return DecisionRecordingAuthorityGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            recording_authority_granted=False,
            decision_recording_authorized=False,
            authorization_decision_recorded=False,
            authorization_granted=False,

            owner_session_created=False,
            owner_session_started=False,
            owner_authenticated=False,
            owner_stepped_up=False,

            immutable=True,
            append_only=True,
            idempotent_replay=idempotent_replay,
        )


__all__ = [
    "ALLOWED_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "DecisionRecordingAuthorityGateError",
    "DecisionRecordingAuthorityGateIntegrityError",
    "DecisionRecordingAuthorityGateReceipt",
    "GATE_STATE",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_PREPARATION_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityGateService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
