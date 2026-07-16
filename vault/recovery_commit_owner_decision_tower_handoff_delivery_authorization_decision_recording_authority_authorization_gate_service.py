"""Archive Vault GP811-GP820.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Authority Authorization Gate.

This layer seals a fail-closed gate around any future Tower-owned grant of
recording-authority authorization.

It does not grant recording authority, authorize decision recording, record an
authorization decision, create an owner session, authenticate an owner, perform
step-up, execute recovery, write production storage, or connect a provider.

Tower is the face and protocol authority.
Vault is sealed memory.
Teller is the workflow and request source.

Allowed flow:
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


PACK_START = 811
PACK_END = 820

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
    "RECORDING_AUTHORITY_AUTHORIZATION_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_PREPARED_NOT_GRANTED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
    "AUTHORIZATION_GATE_SEALED"
)

GATE_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
    "AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED"
)

REQUIRED_PREPARATION_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
    "PREPARATION_SEALED_AUTHORITY_NOT_GRANTED"
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
        "INTAKE_AUTHORIZATION_PREPARATION_REFERENCE",
        "VERIFY_AUTHORIZATION_PREPARATION_STATE",
        "VERIFY_AUTHORIZATION_REQUEST_PREPARED",
        "VERIFY_SCOPE_REQUIREMENTS",
        "VERIFY_EVIDENCE_REQUIREMENTS",
        "VERIFY_OWNER_SESSION_REQUIREMENTS",
        "VERIFY_SECOND_AUTHORITY_REQUIREMENTS",
        "VERIFY_REPLAY_REQUIREMENTS",
        "EVALUATE_AUTHORIZATION_BLOCKERS",
        "SEAL_RECORDING_AUTHORITY_AUTHORIZATION_GATE",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "DELIVER_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "ACCEPT_RECORDING_AUTHORITY_AUTHORIZATION_REQUEST",
        "GRANT_RECORDING_AUTHORITY_AUTHORIZATION",
        "GRANT_RECORDING_AUTHORITY",
        "AUTHORIZE_RECORDING_AUTHORITY",
        "AUTHORIZE_DECISION_RECORDING",
        "RECORD_AUTHORIZATION_DECISION",
        "RECORD_OWNER_SESSION_CREATION_AUTHORIZATION_DECISION",
        "GRANT_OWNER_SESSION_CREATION_AUTHORIZATION",
        "AUTHORIZE_OWNER_SESSION_CREATION",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "ISSUE_OWNER_SESSION",
        "ACTIVATE_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
        "DELIVER_HANDOFF",
        "EXECUTE_RECOVERY_COMMIT",
        "RESTORE_DATA",
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
        "public_url",
        "download_url",
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
        "provider_secret",
        "raw_material",
        "raw_materials",
        "raw_payload",
        "raw_data",
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
    "authorization_request_sent",
    "authorization_request_delivered",
    "authorization_request_accepted",
    "recording_authority_authorization_granted",
    "recording_authority_authorized",
    "recording_authority_granted",
    "decision_recording_authorized",
    "authorization_decision_recorded",
    "owner_session_creation_authorization_granted",
    "owner_session_creation_authorized",
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
    "owner_admin_approval_granted",
    "second_authority_review_granted",
    "dual_receipt_satisfied",
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


class RecordingAuthorityAuthorizationGateError(ValueError):
    """Raised when GP811-GP820 input is unsafe."""


class RecordingAuthorityAuthorizationGateIntegrityError(RuntimeError):
    """Raised when sealed GP811-GP820 evidence fails verification."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(
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
        raise RecordingAuthorityAuthorizationGateError(
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
        raise RecordingAuthorityAuthorizationGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise RecordingAuthorityAuthorizationGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    blocked = sorted(
        set(_find_blocked_keys(normalized))
    )

    if blocked:
        raise RecordingAuthorityAuthorizationGateError(
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
class RecordingAuthorityAuthorizationGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    authorization_granted: bool
    recording_authority_authorized: bool
    recording_authority_granted: bool
    decision_recording_authorized: bool
    authorization_decision_recorded: bool

    owner_session_created: bool
    owner_authenticated: bool
    owner_stepped_up: bool

    immutable: bool
    append_only: bool
    idempotent_replay: bool


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityAuthorizationGateService:
    """Persistent fail-closed GP811-GP820 authorization gate."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
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
                vault_gp811_820_recording_authority_authorization_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    authorization_preparation_id TEXT NOT NULL,
                    authorization_preparation_hash TEXT NOT NULL,
                    authorization_preparation_state TEXT NOT NULL
                        CHECK(
                            authorization_preparation_state =
                            'AUTHORIZATION_DECISION_RECORDING_AUTHORITY_PREPARATION_SEALED_AUTHORITY_NOT_GRANTED'
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
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_AUTHORITY_AUTHORIZATION_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'AUTHORIZATION_DECISION_RECORDING_AUTHORITY_AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp811_820_recording_authority_authorization_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES
                        vault_gp811_820_recording_authority_authorization_gates(
                            gate_id
                        )
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp811_820_gate_no_update
                BEFORE UPDATE
                ON vault_gp811_820_recording_authority_authorization_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP811-GP820 authorization gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp811_820_gate_no_delete
                BEFORE DELETE
                ON vault_gp811_820_recording_authority_authorization_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP811-GP820 authorization gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp811_820_event_no_update
                BEFORE UPDATE
                ON vault_gp811_820_recording_authority_authorization_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP811-GP820 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp811_820_event_no_delete
                BEFORE DELETE
                ON vault_gp811_820_recording_authority_authorization_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP811-GP820 events are append-only'
                    );
                END;
                """
            )

    def seal_authorization_gate(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        authorization_preparation_id: str,
        authorization_preparation_hash: str,
        authorization_preparation_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> RecordingAuthorityAuthorizationGateReceipt:
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
        authorization_preparation_id = _required_text(
            "authorization_preparation_id",
            authorization_preparation_id,
        )
        authorization_preparation_hash = _required_text(
            "authorization_preparation_hash",
            authorization_preparation_hash,
        )

        authorization_preparation_state = _required_text(
            "authorization_preparation_state",
            authorization_preparation_state,
        ).upper()

        if authorization_preparation_state != REQUIRED_PREPARATION_STATE:
            raise RecordingAuthorityAuthorizationGateError(
                "authorization_preparation_state must preserve "
                "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
                "PREPARATION_SEALED_AUTHORITY_NOT_GRANTED"
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
            raise RecordingAuthorityAuthorizationGateError(
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
            "authorization_preparation_id": authorization_preparation_id,
            "authorization_preparation_hash": authorization_preparation_hash,
            "authorization_preparation_state": authorization_preparation_state,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        gate_id = (
            "vault-gp811-820-"
            + _sha256(_canonical_json(identity))[:24]
        )

        payload = {
            "gp811_gate_shell": {
                "pack": "GP811",
                "gate_id": gate_id,
                "recommendation": CURRENT_RECOMMENDATION,
                "gate_state": GATE_STATE,
                "gate_sealed": True,
                "authorization_granted": False,
                "recording_authority_authorized": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,
            },

            "gp812_preparation_lineage_gate": {
                "pack": "GP812",
                "authorization_preparation_id": (
                    authorization_preparation_id
                ),
                "authorization_preparation_hash": (
                    authorization_preparation_hash
                ),
                "authorization_preparation_state": (
                    authorization_preparation_state
                ),
                "required_preparation_state": REQUIRED_PREPARATION_STATE,
                "preparation_reference_present": True,
                "preparation_hash_present": True,
                "preparation_sealed_in_lineage": True,
                "authorization_granted_in_lineage": False,
                "recording_authority_granted_in_lineage": False,
            },

            "gp813_authorization_request_gate": {
                "pack": "GP813",
                "destination": TOWER_DESTINATION,
                "authorization_authority": TOWER_DESTINATION,
                "tower_authority_id": tower_authority_id,
                "tower_delivery_target_id": tower_delivery_target_id,
                "request_prepared": True,
                "request_sent": False,
                "request_delivered": False,
                "request_accepted": False,
                "authorization_granted": False,
            },

            "gp814_scope_binding_gate": {
                "pack": "GP814",
                "scope_reference_required": True,
                "scope_hash_required": True,
                "recovery_case_binding_required": True,
                "owner_decision_binding_required": True,
                "environment_binding_required": True,
                "tower_authority_binding_required": True,
                "scope_reference_present": False,
                "scope_hash_present": False,
                "scope_bindings_verified": False,
                "authorization_blocked": True,
            },

            "gp815_evidence_binding_gate": {
                "pack": "GP815",
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
                "authorization_blocked": True,
            },

            "gp816_owner_session_gate": {
                "pack": "GP816",
                "tower_owner_session_required": True,
                "owner_authentication_required": True,
                "owner_step_up_required": True,
                "purpose_binding_required": True,
                "case_binding_required": True,
                "environment_binding_required": True,
                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,
                "session_bindings_verified": False,
                "authorization_blocked": True,
            },

            "gp817_second_authority_gate": {
                "pack": "GP817",
                "owner_admin_approval_required": True,
                "second_authority_review_required": True,
                "dual_receipt_required": True,
                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,
                "authorization_blocked": True,
            },

            "gp818_replay_protection_gate": {
                "pack": "GP818",
                "authorization_nonce_reference_required": True,
                "authorization_consumption_receipt_required": True,
                "single_authorization_required": True,
                "duplicate_authorization_rejected": True,
                "changed_replay_rejected": True,
                "cross_case_replay_rejected": True,
                "cross_decision_replay_rejected": True,
                "cross_environment_replay_rejected": True,
                "authorization_nonce_reference_present": False,
                "authorization_consumption_receipt_present": False,
                "replay_protection_verified": False,
                "authorization_blocked": True,
            },

            "gp819_authorization_blocker_matrix": {
                "pack": "GP819",

                "preparation_reference_present": True,
                "preparation_hash_present": True,
                "authorization_request_prepared": True,

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

                "all_authorization_prerequisites_satisfied": False,
                "recording_authority_authorization_granted": False,
                "recording_authority_authorized": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_may_be_recorded": False,
                "authorization_decision_recorded": False,

                "owner_session_creation_authorized": False,
                "session_creation_may_proceed": False,
            },

            "gp820_checkpoint": {
                "pack": "GP820",
                "checkpoint_type": (
                    "AUTHORIZATION_DECISION_RECORDING_AUTHORITY_"
                    "AUTHORIZATION_GATE_READINESS"
                ),
                "prior_pack_range": "GP801-GP810",
                "current_pack_range": "GP811-GP820",
                "recommendation": CURRENT_RECOMMENDATION,
                "gate_state": GATE_STATE,

                "gate_sealed": True,

                "authorization_request_prepared": True,
                "authorization_request_sent": False,
                "authorization_request_delivered": False,
                "authorization_request_accepted": False,

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

                "recording_authority_authorization_granted": False,
                "recording_authority_authorized": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,

                "owner_session_creation_authorization_granted": False,
                "owner_session_creation_authorized": False,

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
                "handoff_accepted": False,

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
                    "AUTHORIZATION_PREPARATION_LAYER"
                ),
            },

            "requested_operations": operations,
            "safe_metadata": metadata,
        }

        payload_json = _canonical_json(payload)
        gate_hash = _sha256(payload_json)
        created_at = _utc_now()

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp811_820_recording_authority_authorization_gates
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["payload_json"] != payload_json
                    or existing["gate_hash"] != gate_hash
                ):
                    raise RecordingAuthorityAuthorizationGateError(
                        "idempotency_key already exists with different "
                        "immutable authorization-gate inputs"
                    )

                return self._receipt(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp811_820_recording_authority_authorization_gates
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
                INSERT INTO
                    vault_gp811_820_recording_authority_authorization_gates (
                        gate_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        authorization_preparation_id,
                        authorization_preparation_hash,
                        authorization_preparation_state,
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
                    authorization_preparation_id,
                    authorization_preparation_hash,
                    authorization_preparation_state,
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
                    "GP811_820_RECORDING_AUTHORITY_"
                    "AUTHORIZATION_GATE_SEALED"
                ),
                event_payload={
                    "gate_hash": gate_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "gate_state": GATE_STATE,
                    "gate_sealed": True,
                    "authorization_granted": False,
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
                FROM vault_gp811_820_recording_authority_authorization_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

            if row is None:
                raise RecordingAuthorityAuthorizationGateIntegrityError(
                    "authorization gate failed to persist"
                )

            return self._receipt(
                row,
                idempotent_replay=False,
            )

    def get_gate(self, gate_id: str) -> dict[str, Any]:
        gate_id = _required_text("gate_id", gate_id)

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM vault_gp811_820_recording_authority_authorization_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP811-GP820 gate: {gate_id}"
            )

        result = dict(row)
        result["payload"] = json.loads(
            result.pop("payload_json")
        )

        return result

    def list_events(self, gate_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM vault_gp811_820_recording_authority_authorization_events
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

    def verify_gate(self, gate_id: str) -> dict[str, Any]:
        record = self.get_gate(gate_id)

        if _sha256(
            _canonical_json(record["payload"])
        ) != record["gate_hash"]:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization gate payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization gate destination is not Tower"
            )

        if (
            record["authorization_preparation_state"]
            != REQUIRED_PREPARATION_STATE
        ):
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization preparation lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization gate recommendation mismatch"
            )

        if record["gate_state"] != GATE_STATE:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization gate state mismatch"
            )

        checkpoint = record["payload"]["gp820_checkpoint"]

        if checkpoint["gate_sealed"] is not True:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization gate is not sealed"
            )

        if checkpoint["authorization_request_prepared"] is not True:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization request is not prepared"
            )

        permitted_true = {
            "gate_sealed",
            "authorization_request_prepared",
        }

        unsafe_checkpoint_fields = [
            key
            for key, value in checkpoint.items()
            if (
                isinstance(value, bool)
                and value is True
                and key not in permitted_true
            )
        ]

        if unsafe_checkpoint_fields:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "unsafe authorization checkpoint state: "
                + ", ".join(sorted(unsafe_checkpoint_fields))
            )

        blockers = record["payload"][
            "gp819_authorization_blocker_matrix"
        ]

        permitted_blocker_true = {
            "preparation_reference_present",
            "preparation_hash_present",
            "authorization_request_prepared",
        }

        unsafe_blocker_fields = [
            key
            for key, value in blockers.items()
            if (
                isinstance(value, bool)
                and value is True
                and key not in permitted_blocker_true
            )
        ]

        if unsafe_blocker_fields:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "unsafe authorization blocker state: "
                + ", ".join(sorted(unsafe_blocker_fields))
            )

        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization safety-field mismatch"
            )

        unsafe_actions = sorted(
            key
            for key, value in safety_state.items()
            if value is True
        )

        if unsafe_actions:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "unsafe completed actions: "
                + ", ".join(unsafe_actions)
            )

        events = self.list_events(gate_id)

        if not events:
            raise RecordingAuthorityAuthorizationGateIntegrityError(
                "authorization gate has no append-only events"
            )

        previous_event_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise RecordingAuthorityAuthorizationGateIntegrityError(
                    "authorization event predecessor mismatch"
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
                raise RecordingAuthorityAuthorizationGateIntegrityError(
                    "authorization event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP811-GP820",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "authorization_preparation_lineage_valid": True,

            "gate_sealed": True,
            "authorization_request_prepared": True,
            "authorization_request_sent": False,
            "authorization_request_delivered": False,
            "authorization_request_accepted": False,

            "scope_reference_present": False,
            "scope_bindings_verified": False,

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

            "recording_authority_authorization_granted": False,
            "recording_authority_authorized": False,
            "recording_authority_granted": False,
            "decision_recording_authorized": False,
            "authorization_decision_recorded": False,

            "owner_session_creation_authorized": False,
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
            return sorted(ALLOWED_OPERATIONS)

        if isinstance(requested_operations, (str, bytes)):
            raise RecordingAuthorityAuthorizationGateError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise RecordingAuthorityAuthorizationGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise RecordingAuthorityAuthorizationGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise RecordingAuthorityAuthorizationGateError(
                "requested_operations cannot be empty"
            )

        return sorted(set(operations))

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
            FROM vault_gp811_820_recording_authority_authorization_events
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
            _canonical_json(dict(event_payload))
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
            INSERT INTO
                vault_gp811_820_recording_authority_authorization_events (
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
    ) -> RecordingAuthorityAuthorizationGateReceipt:
        return RecordingAuthorityAuthorizationGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            authorization_granted=False,
            recording_authority_authorized=False,
            recording_authority_granted=False,
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
    "GATE_STATE",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_PREPARATION_STATE",
    "RecordingAuthorityAuthorizationGateError",
    "RecordingAuthorityAuthorizationGateIntegrityError",
    "RecordingAuthorityAuthorizationGateReceipt",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingAuthorityAuthorizationGateService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
