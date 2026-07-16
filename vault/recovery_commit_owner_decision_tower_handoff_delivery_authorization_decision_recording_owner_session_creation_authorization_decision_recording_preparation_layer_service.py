"""Archive Vault GP781-GP790.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Owner Session Creation Authorization Decision Recording Preparation
Layer.

This layer prepares immutable, reference-only evidence requirements for a
later Tower-owned authorization-decision recording authority gate.

It does not authorize recording, accept a decision value, record a decision,
grant authorization, create a session, authenticate an owner, perform step-up,
open an owner-decision recording gate, or execute recovery.

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


PACK_START = 781
PACK_END = 790

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_"
    "PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_GATE_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_PREPARED_NOT_RECORDED"
)

PREPARATION_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_PREPARATION_SEALED_NOT_AUTHORIZED"
)

REQUIRED_PRIOR_GATE_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_GATE_SEALED_RECORDING_NOT_AUTHORIZED"
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
        "INTAKE_RECORDING_GATE_REFERENCE",
        "VERIFY_RECORDING_GATE_STATE",
        "PREPARE_RECORDING_AUTHORITY_REQUEST",
        "PREPARE_DECISION_VALUE_REFERENCE_REQUIREMENT",
        "PREPARE_DECISION_REASON_REFERENCE_REQUIREMENT",
        "PREPARE_DECISION_EVIDENCE_PACKAGE_REQUIREMENT",
        "PREPARE_TOWER_OWNER_SESSION_REQUIREMENT",
        "PREPARE_RECORDING_CONSUMPTION_REQUIREMENT",
        "PREPARE_RECORDING_AUTHORITY_PREREQUISITE_BOARD",
        "SEAL_RECORDING_PREPARATION_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_RECORDING_AUTHORITY_REQUEST",
        "DELIVER_RECORDING_AUTHORITY_REQUEST",
        "ACCEPT_RECORDING_AUTHORITY_REQUEST",
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


class DecisionRecordingPreparationError(ValueError):
    """Raised when GP781-GP790 input is unsafe."""


class DecisionRecordingPreparationIntegrityError(RuntimeError):
    """Raised when sealed GP781-GP790 evidence fails verification."""


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
        raise DecisionRecordingPreparationError(
            f"{name} must be a non-empty string"
        )

    return value.strip()


def _blocked_keys(
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
                _blocked_keys(
                    nested,
                    location=nested_location,
                )
            )

    elif isinstance(value, list):
        for index, nested in enumerate(value):
            blocked.extend(
                _blocked_keys(
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
        raise DecisionRecordingPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise DecisionRecordingPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    blocked = sorted(set(_blocked_keys(normalized)))

    if blocked:
        raise DecisionRecordingPreparationError(
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
class DecisionRecordingPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    preparation_state: str

    preparation_sealed: bool
    recording_authority_request_prepared: bool
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


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingPreparationLayerService:
    """Persistent fail-closed GP781-GP790 preparation service."""

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
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
                vault_gp781_790_recording_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    prior_recording_gate_id TEXT NOT NULL,
                    prior_recording_gate_hash TEXT NOT NULL,
                    prior_recording_gate_state TEXT NOT NULL
                        CHECK(
                            prior_recording_gate_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED_RECORDING_NOT_AUTHORIZED'
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
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_PREPARED_NOT_RECORDED'
                        ),

                    preparation_state TEXT NOT NULL
                        CHECK(
                            preparation_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_PREPARATION_SEALED_NOT_AUTHORIZED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp781_790_recording_preparation_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES vault_gp781_790_recording_preparations(
                            preparation_id
                        )
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp781_790_preparation_no_update
                BEFORE UPDATE
                ON vault_gp781_790_recording_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP781-GP790 recording preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp781_790_preparation_no_delete
                BEFORE DELETE
                ON vault_gp781_790_recording_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP781-GP790 recording preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp781_790_event_no_update
                BEFORE UPDATE
                ON vault_gp781_790_recording_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP781-GP790 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp781_790_event_no_delete
                BEFORE DELETE
                ON vault_gp781_790_recording_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP781-GP790 events are append-only'
                    );
                END;
                """
            )

    def seal_recording_preparation(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        prior_recording_gate_id: str,
        prior_recording_gate_hash: str,
        prior_recording_gate_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> DecisionRecordingPreparationReceipt:
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

        prior_recording_gate_id = _required_text(
            "prior_recording_gate_id",
            prior_recording_gate_id,
        )

        prior_recording_gate_hash = _required_text(
            "prior_recording_gate_hash",
            prior_recording_gate_hash,
        )

        prior_recording_gate_state = _required_text(
            "prior_recording_gate_state",
            prior_recording_gate_state,
        ).upper()

        if prior_recording_gate_state != REQUIRED_PRIOR_GATE_STATE:
            raise DecisionRecordingPreparationError(
                "prior_recording_gate_state must preserve "
                "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
                "RECORDING_GATE_SEALED_RECORDING_NOT_AUTHORIZED"
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
            raise DecisionRecordingPreparationError(
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
            "prior_recording_gate_id": prior_recording_gate_id,
            "prior_recording_gate_hash": prior_recording_gate_hash,
            "prior_recording_gate_state": prior_recording_gate_state,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        preparation_id = (
            "vault-gp781-790-"
            + _sha256(_canonical_json(identity))[:24]
        )

        payload = {
            "gp781_preparation_shell": {
                "pack": "GP781",
                "preparation_id": preparation_id,
                "recommendation": CURRENT_RECOMMENDATION,
                "preparation_state": PREPARATION_STATE,
                "preparation_sealed": True,
                "recording_authority_request_prepared": True,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,
            },
            "gp782_prior_gate_lineage": {
                "pack": "GP782",
                "prior_recording_gate_id": prior_recording_gate_id,
                "prior_recording_gate_hash": prior_recording_gate_hash,
                "prior_recording_gate_state": prior_recording_gate_state,
                "required_prior_gate_state": REQUIRED_PRIOR_GATE_STATE,
                "gate_reference_present": True,
                "gate_hash_present": True,
                "recording_authorized_in_lineage": False,
                "authorization_decision_recorded_in_lineage": False,
            },
            "gp783_recording_authority_request": {
                "pack": "GP783",
                "destination": TOWER_DESTINATION,
                "recording_authority": TOWER_DESTINATION,
                "request_prepared": True,
                "request_sent": False,
                "request_delivered": False,
                "request_accepted": False,
                "recording_authority_granted": False,
            },
            "gp784_decision_value_reference_board": {
                "pack": "GP784",
                "decision_value_reference_required": True,
                "decision_value_reference_present": False,
                "decision_value_present": False,
                "decision_value_selected": False,
                "decision_value_invented": False,
                "default_decision_allowed": False,
                "recording_ready": False,
            },
            "gp785_decision_reason_reference_board": {
                "pack": "GP785",
                "decision_reason_reference_required": True,
                "decision_reason_reference_present": False,
                "raw_reason_allowed": False,
                "tower_safe_reason_required": True,
                "case_bound_reason_required": True,
                "decision_bound_reason_required": True,
                "recording_ready": False,
            },
            "gp786_evidence_package_board": {
                "pack": "GP786",
                "scope_evidence_required": True,
                "lifetime_evidence_required": True,
                "replay_evidence_required": True,
                "authentication_evidence_required": True,
                "step_up_evidence_required": True,
                "evidence_package_reference_present": False,
                "evidence_package_hash_present": False,
                "all_evidence_bindings_verified": False,
                "recording_ready": False,
            },
            "gp787_tower_owner_session_board": {
                "pack": "GP787",
                "tower_owner_session_required": True,
                "owner_authentication_required": True,
                "owner_step_up_required": True,
                "owner_admin_approval_required": True,
                "second_authority_review_required": True,
                "dual_receipt_required": True,
                "tower_owner_session_present": False,
                "owner_authenticated": False,
                "owner_stepped_up": False,
                "owner_admin_approval_granted": False,
                "second_authority_review_granted": False,
                "dual_receipt_satisfied": False,
                "recording_ready": False,
            },
            "gp788_recording_consumption_board": {
                "pack": "GP788",
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
                "recording_ready": False,
            },
            "gp789_recording_authority_prerequisites": {
                "pack": "GP789",
                "prior_gate_reference_present": True,
                "prior_gate_hash_present": True,
                "recording_authority_request_prepared": True,

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

                "all_recording_authority_prerequisites_satisfied": False,
                "recording_authority_granted": False,
                "decision_recording_authorized": False,
                "authorization_decision_may_be_recorded": False,
                "authorization_decision_recorded": False,
                "authorization_granted": False,
            },
            "gp790_checkpoint": {
                "pack": "GP790",
                "prior_pack_range": "GP771-GP780",
                "current_pack_range": "GP781-GP790",
                "recommendation": CURRENT_RECOMMENDATION,
                "preparation_state": PREPARATION_STATE,
                "preparation_sealed": True,

                "recording_authority_request_prepared": True,
                "recording_authority_request_sent": False,
                "recording_authority_request_delivered": False,
                "recording_authority_request_accepted": False,
                "recording_authority_granted": False,

                "decision_recording_authorized": False,
                "authorization_decision_recorded": False,
                "authorization_granted": False,

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

                "owner_authenticated": False,
                "owner_stepped_up": False,
                "owner_decision_recording_gate_opened": False,

                "owner_decision_recommended": False,
                "owner_decision_defaulted": False,
                "owner_decision_selected": False,
                "owner_decision_invented": False,
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

                "safety_state": _false_safety_state(),

                "next_gate": (
                    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
                    "RECORDING_AUTHORITY_GATE"
                ),
            },
            "requested_operations": operations,
            "safe_metadata": metadata,
        }

        payload_json = _canonical_json(payload)
        preparation_hash = _sha256(payload_json)
        created_at = _utc_now()

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp781_790_recording_preparations
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["payload_json"] != payload_json
                    or existing["preparation_hash"] != preparation_hash
                ):
                    raise DecisionRecordingPreparationError(
                        "idempotency_key already exists with different "
                        "immutable recording-preparation inputs"
                    )

                return self._receipt(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp781_790_recording_preparations
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
                INSERT INTO vault_gp781_790_recording_preparations (
                    preparation_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    prior_recording_gate_id,
                    prior_recording_gate_hash,
                    prior_recording_gate_state,
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
                    prior_recording_gate_id,
                    prior_recording_gate_hash,
                    prior_recording_gate_state,
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
                    "GP781_790_DECISION_RECORDING_PREPARATION_SEALED"
                ),
                event_payload={
                    "preparation_hash": preparation_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "preparation_state": PREPARATION_STATE,
                    "recording_authority_request_prepared": True,
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
                    "destructive_action_occurred": False,
                },
            )

            row = connection.execute(
                """
                SELECT *
                FROM vault_gp781_790_recording_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

            if row is None:
                raise DecisionRecordingPreparationIntegrityError(
                    "recording preparation failed to persist"
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
                FROM vault_gp781_790_recording_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP781-GP790 preparation: {preparation_id}"
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
                FROM vault_gp781_790_recording_preparation_events
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
        record = self.get_preparation(preparation_id)

        canonical_payload = _canonical_json(
            record["payload"]
        )

        if _sha256(canonical_payload) != record["preparation_hash"]:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation destination is not Tower"
            )

        if (
            record["prior_recording_gate_state"]
            != REQUIRED_PRIOR_GATE_STATE
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording gate lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation recommendation mismatch"
            )

        if record["preparation_state"] != PREPARATION_STATE:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation state mismatch"
            )

        payload = record["payload"]
        checkpoint = payload["gp790_checkpoint"]

        required_true = (
            "preparation_sealed",
            "recording_authority_request_prepared",
        )

        for field in required_true:
            if checkpoint[field] is not True:
                raise DecisionRecordingPreparationIntegrityError(
                    f"required preparation state missing: {field}"
                )

        prohibited_true = (
            "recording_authority_request_sent",
            "recording_authority_request_delivered",
            "recording_authority_request_accepted",
            "recording_authority_granted",
            "decision_recording_authorized",
            "authorization_decision_recorded",
            "authorization_granted",
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
            "recovery_authorization_granted",
            "authorization_token_issued",
            "handoff_delivered",
            "recovery_commit_command_issued",
            "recovery_commit_executed",
            "restore_occurred",
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
            raise DecisionRecordingPreparationIntegrityError(
                "unsafe recording preparation state: "
                + ", ".join(unsafe)
            )

        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation safety-field mismatch"
            )

        unsafe_safety = [
            field
            for field, value in safety_state.items()
            if value is True
        ]

        if unsafe_safety:
            raise DecisionRecordingPreparationIntegrityError(
                "unsafe completed actions: "
                + ", ".join(unsafe_safety)
            )

        events = self.list_events(preparation_id)

        if not events:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation has no append-only events"
            )

        previous_event_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise DecisionRecordingPreparationIntegrityError(
                    "recording event predecessor mismatch"
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
                raise DecisionRecordingPreparationIntegrityError(
                    "recording event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP781-GP790",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "prior_recording_gate_lineage_valid": True,

            "preparation_sealed": True,
            "recording_authority_request_prepared": True,
            "recording_authority_request_sent": False,
            "recording_authority_granted": False,

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
            return sorted(ALLOWED_OPERATIONS)

        if isinstance(requested_operations, (str, bytes)):
            raise DecisionRecordingPreparationError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise DecisionRecordingPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise DecisionRecordingPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise DecisionRecordingPreparationError(
                "requested_operations cannot be empty"
            )

        return sorted(set(operations))

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
            FROM vault_gp781_790_recording_preparation_events
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
            _canonical_json(dict(event_payload))
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
            INSERT INTO vault_gp781_790_recording_preparation_events (
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
    ) -> DecisionRecordingPreparationReceipt:
        return DecisionRecordingPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            preparation_state=row["preparation_state"],

            preparation_sealed=True,
            recording_authority_request_prepared=True,
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
    "DecisionRecordingPreparationError",
    "DecisionRecordingPreparationIntegrityError",
    "DecisionRecordingPreparationReceipt",
    "PACK_END",
    "PACK_START",
    "PREPARATION_STATE",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_PRIOR_GATE_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingPreparationLayerService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
