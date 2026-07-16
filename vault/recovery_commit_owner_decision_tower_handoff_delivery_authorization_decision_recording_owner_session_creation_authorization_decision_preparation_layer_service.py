"""Archive Vault GP761-GP770.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Owner Session Creation Authorization Decision Preparation Layer.

This layer prepares immutable evidence for a later Tower-owned recording of an
owner-session-creation authorization decision.

It does not record a decision, grant authorization, create a session,
authenticate an owner, perform step-up, open the owner-decision recording gate,
or execute recovery.

Tower remains the protocol, identity, step-up, session, and authorization
decision authority.

Vault remains sealed memory.

Teller remains the workflow and request source.

Permitted ecosystem flow:
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


PACK_START = 761
PACK_END = 770

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_OWNER_SESSION_CREATION_"
    "AUTHORIZATION_DECISION_PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_GATE_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED"
)

PREPARATION_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "PREPARATION_SEALED_DECISION_NOT_RECORDED"
)

REQUIRED_GATE_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_"
    "DECISION_GATE_SEALED_DECISION_NOT_RECORDED"
)

TOWER_DESTINATION = "TOWER"

SESSION_PURPOSE = (
    "RECOVERY_COMMIT_OWNER_DECISION_RECORDING"
)

SESSION_TYPE = (
    "TOWER_OWNER_DECISION_RECORDING_SESSION"
)

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_OPERATIONS = frozenset(
    {
        "INTAKE_AUTHORIZATION_DECISION_GATE_REFERENCE",
        "VERIFY_AUTHORIZATION_DECISION_GATE_STATE",
        "PREPARE_TOWER_DECISION_RECORDING_REQUEST",
        "PREPARE_DECISION_VALUE_CONTRACT",
        "PREPARE_DECISION_REASON_REQUIREMENTS",
        "PREPARE_DECISION_EVIDENCE_BINDING_REQUIREMENTS",
        "PREPARE_DECISION_AUTHORITY_REQUIREMENTS",
        "PREPARE_DECISION_REPLAY_PROTECTION_REQUIREMENTS",
        "PREPARE_DECISION_RECORDING_PREREQUISITE_BOARD",
        "SEAL_AUTHORIZATION_DECISION_PREPARATION_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_DECISION_RECORDING_REQUEST",
        "DELIVER_DECISION_RECORDING_REQUEST",
        "ACCEPT_DECISION_RECORDING_REQUEST",
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
        "GRANT_OWNER_APPROVAL",
        "GRANT_ADMIN_APPROVAL",
        "SATISFY_DUAL_RECEIPT",
        "GRANT_SECOND_AUTHORITY_REVIEW",
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
    }
)

SAFETY_STATE_FIELDS = (
    "decision_recording_request_sent",
    "decision_recording_request_delivered",
    "decision_recording_request_accepted",
    "authorization_decision_recording_authorized",
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
    "owner_admin_approval_granted",
    "dual_receipt_satisfied",
    "second_authority_review_granted",
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


class OwnerSessionCreationAuthorizationDecisionPreparationError(
    ValueError
):
    """Raised when GP761-GP770 preparation input is unsafe."""


class OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
    RuntimeError
):
    """Raised when sealed GP761-GP770 evidence fails verification."""


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


def _sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _required_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OwnerSessionCreationAuthorizationDecisionPreparationError(
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
        for key, nested_value in value.items():
            key_text = str(key)
            normalized_key = key_text.strip().lower()
            nested_location = f"{location}.{key_text}"

            if normalized_key in PROHIBITED_METADATA_KEYS:
                blocked.append(nested_location)

            blocked.extend(
                _find_blocked_keys(
                    nested_value,
                    location=nested_location,
                )
            )

    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            blocked.extend(
                _find_blocked_keys(
                    nested_value,
                    location=f"{location}[{index}]",
                )
            )

    return blocked


def _normalize_safe_metadata(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise OwnerSessionCreationAuthorizationDecisionPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise OwnerSessionCreationAuthorizationDecisionPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise OwnerSessionCreationAuthorizationDecisionPreparationError(
            "safe_metadata must serialize to an object"
        )

    blocked = sorted(
        set(
            _find_blocked_keys(normalized)
        )
    )

    if blocked:
        raise OwnerSessionCreationAuthorizationDecisionPreparationError(
            "safe_metadata contains prohibited raw, path, URL, token, "
            "secret, credential, session, authorization, or decision fields: "
            + ", ".join(blocked)
        )

    return normalized


def _false_safety_state() -> dict[str, bool]:
    return {
        field: False
        for field in SAFETY_STATE_FIELDS
    }


@dataclass(frozen=True)
class OwnerSessionCreationAuthorizationDecisionPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    preparation_state: str

    preparation_sealed: bool
    decision_recording_request_prepared: bool
    authorization_decision_recorded: bool
    authorization_granted: bool

    owner_session_creation_authorized: bool
    owner_session_created: bool
    owner_session_started: bool

    recording_gate_open: bool
    owner_decision_recorded: bool

    immutable: bool
    append_only: bool
    idempotent_replay: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "preparation_id": self.preparation_id,
            "preparation_hash": self.preparation_hash,
            "recommendation": self.recommendation,
            "preparation_state": self.preparation_state,
            "preparation_sealed": self.preparation_sealed,
            "decision_recording_request_prepared": (
                self.decision_recording_request_prepared
            ),
            "authorization_decision_recorded": (
                self.authorization_decision_recorded
            ),
            "authorization_granted": self.authorization_granted,
            "owner_session_creation_authorized": (
                self.owner_session_creation_authorized
            ),
            "owner_session_created": self.owner_session_created,
            "owner_session_started": self.owner_session_started,
            "recording_gate_open": self.recording_gate_open,
            "owner_decision_recorded": self.owner_decision_recorded,
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": self.idempotent_replay,
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionPreparationLayerService:
    """Persistent fail-closed GP761-GP770 preparation service."""

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
                vault_gp761_770_owner_session_creation_authorization_decision_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    authorization_decision_gate_id TEXT NOT NULL,
                    authorization_decision_gate_hash TEXT NOT NULL,
                    authorization_decision_gate_state TEXT NOT NULL
                        CHECK(
                            authorization_decision_gate_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_GATE_SEALED_DECISION_NOT_RECORDED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    preparation_shell_json TEXT NOT NULL,
                    gate_lineage_intake_json TEXT NOT NULL,
                    recording_request_envelope_json TEXT NOT NULL,
                    decision_value_contract_json TEXT NOT NULL,
                    decision_reason_board_json TEXT NOT NULL,
                    evidence_binding_board_json TEXT NOT NULL,
                    authority_requirement_board_json TEXT NOT NULL,
                    replay_protection_board_json TEXT NOT NULL,
                    recording_prerequisite_board_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    preparation_payload_json TEXT NOT NULL,
                    preparation_hash TEXT NOT NULL UNIQUE,
                    predecessor_preparation_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED'
                        ),

                    preparation_state TEXT NOT NULL
                        CHECK(
                            preparation_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_PREPARATION_SEALED_DECISION_NOT_RECORDED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp761_770_owner_session_creation_authorization_decision_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES
                        vault_gp761_770_owner_session_creation_authorization_decision_preparations(
                            preparation_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp761_770_recovery_case
                ON vault_gp761_770_owner_session_creation_authorization_decision_preparations(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp761_770_prior_gate
                ON vault_gp761_770_owner_session_creation_authorization_decision_preparations(
                    authorization_decision_gate_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp761_770_event_chain
                ON vault_gp761_770_owner_session_creation_authorization_decision_events(
                    preparation_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp761_770_preparation_no_update
                BEFORE UPDATE
                ON vault_gp761_770_owner_session_creation_authorization_decision_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP761-GP770 decision preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp761_770_preparation_no_delete
                BEFORE DELETE
                ON vault_gp761_770_owner_session_creation_authorization_decision_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP761-GP770 decision preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp761_770_event_no_update
                BEFORE UPDATE
                ON vault_gp761_770_owner_session_creation_authorization_decision_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP761-GP770 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp761_770_event_no_delete
                BEFORE DELETE
                ON vault_gp761_770_owner_session_creation_authorization_decision_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP761-GP770 events are append-only'
                    );
                END;
                """
            )

    def seal_decision_preparation(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        authorization_decision_gate_id: str,
        authorization_decision_gate_hash: str,
        authorization_decision_gate_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> OwnerSessionCreationAuthorizationDecisionPreparationReceipt:
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

        authorization_decision_gate_id = _required_text(
            "authorization_decision_gate_id",
            authorization_decision_gate_id,
        )

        authorization_decision_gate_hash = _required_text(
            "authorization_decision_gate_hash",
            authorization_decision_gate_hash,
        )

        authorization_decision_gate_state = _required_text(
            "authorization_decision_gate_state",
            authorization_decision_gate_state,
        ).upper()

        if authorization_decision_gate_state != REQUIRED_GATE_STATE:
            raise OwnerSessionCreationAuthorizationDecisionPreparationError(
                "authorization_decision_gate_state must preserve "
                "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
                "GATE_SEALED_DECISION_NOT_RECORDED"
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
            raise OwnerSessionCreationAuthorizationDecisionPreparationError(
                "target_environment must be STAGING or PRODUCTION"
            )

        operations = self._normalize_operations(
            requested_operations
        )

        metadata = _normalize_safe_metadata(
            safe_metadata
        )

        identity = {
            "layer_id": LAYER_ID,
            "idempotency_key": idempotency_key,
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "authorization_decision_gate_id": (
                authorization_decision_gate_id
            ),
            "authorization_decision_gate_hash": (
                authorization_decision_gate_hash
            ),
            "authorization_decision_gate_state": (
                authorization_decision_gate_state
            ),
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        preparation_id = (
            "vault-gp761-770-"
            + _sha256_text(
                _canonical_json(identity)
            )[:24]
        )

        # GP761 — Decision Preparation Shell
        preparation_shell = {
            "pack": "GP761",
            "preparation_id": preparation_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": PRIOR_RECOMMENDATION,
            "recommendation": CURRENT_RECOMMENDATION,
            "preparation_state": PREPARATION_STATE,
            "preparation_sealed": True,
            "decision_recording_request_prepared": True,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
        }

        # GP762 — Prior Gate Lineage Intake
        gate_lineage_intake = {
            "pack": "GP762",
            "authorization_decision_gate_id": (
                authorization_decision_gate_id
            ),
            "authorization_decision_gate_hash": (
                authorization_decision_gate_hash
            ),
            "authorization_decision_gate_state": (
                authorization_decision_gate_state
            ),
            "required_gate_state": REQUIRED_GATE_STATE,
            "gate_reference_present": True,
            "gate_hash_present": True,
            "gate_sealed_in_lineage": True,
            "authorization_decision_recorded_in_lineage": False,
            "authorization_granted_in_lineage": False,
        }

        # GP763 — Tower Decision Recording Request Envelope
        recording_request_envelope = {
            "pack": "GP763",
            "envelope_type": (
                "TOWER_OWNER_SESSION_CREATION_AUTHORIZATION_"
                "DECISION_RECORDING_REQUEST_PREPARATION"
            ),
            "destination": TOWER_DESTINATION,
            "recording_authority": TOWER_DESTINATION,
            "session_type": SESSION_TYPE,
            "session_purpose": SESSION_PURPOSE,
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "request_prepared": True,
            "request_sent": False,
            "request_delivered": False,
            "request_accepted": False,
            "decision_recording_authorized": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
        }

        # GP764 — Decision Value Contract
        decision_value_contract = {
            "pack": "GP764",
            "allowed_decision_values": [
                "GRANT",
                "DENY",
                "HOLD",
            ],
            "decision_value_required": True,
            "decision_value_present": False,
            "decision_value_selected": False,
            "decision_value_invented": False,
            "default_decision_allowed": False,
            "implicit_grant_allowed": False,
            "implicit_deny_allowed": False,
            "implicit_hold_allowed": False,
            "authorization_decision_ready": False,
        }

        # GP765 — Decision Reason Requirements
        decision_reason_board = {
            "pack": "GP765",
            "decision_reason_required": True,
            "decision_reason_reference_required": True,
            "decision_reason_present": False,
            "decision_reason_reference_present": False,
            "freeform_raw_reason_allowed": False,
            "reason_must_be_tower_safe": True,
            "reason_must_be_case_bound": True,
            "reason_must_be_decision_bound": True,
            "authorization_decision_ready": False,
        }

        # GP766 — Decision Evidence Binding
        evidence_binding_board = {
            "pack": "GP766",
            "scope_binding_evidence_required": True,
            "lifetime_evidence_required": True,
            "replay_protection_evidence_required": True,
            "authentication_evidence_required": True,
            "step_up_evidence_required": True,
            "case_binding_required": True,
            "owner_decision_binding_required": True,
            "environment_binding_required": True,
            "tower_authority_binding_required": True,
            "evidence_package_reference_present": False,
            "evidence_bindings_verified": False,
            "authorization_decision_ready": False,
        }

        # GP767 — Decision Authority Requirements
        authority_requirement_board = {
            "pack": "GP767",
            "tower_decision_authority_required": True,
            "tower_owner_session_required": True,
            "tower_owner_authentication_required": True,
            "tower_owner_step_up_required": True,
            "owner_admin_approval_required": True,
            "second_authority_review_required": True,
            "dual_receipt_required": True,
            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,
            "authorization_decision_ready": False,
        }

        # GP768 — Decision Replay Protection
        replay_protection_board = {
            "pack": "GP768",
            "decision_nonce_required": True,
            "decision_idempotency_key_required": True,
            "single_recording_allowed": True,
            "duplicate_recording_rejected": True,
            "changed_replay_rejected": True,
            "cross_case_replay_rejected": True,
            "cross_decision_replay_rejected": True,
            "cross_environment_replay_rejected": True,
            "decision_nonce_reference_present": False,
            "recording_consumption_receipt_present": False,
            "replay_protection_verified": False,
            "authorization_decision_ready": False,
        }

        # GP769 — Decision Recording Prerequisite Board
        recording_prerequisite_board = {
            "pack": "GP769",
            "prior_gate_reference_present": True,
            "prior_gate_hash_present": True,
            "decision_recording_request_prepared": True,

            "decision_value_present": False,
            "decision_value_selected": False,
            "decision_reason_present": False,
            "decision_reason_reference_present": False,

            "evidence_package_reference_present": False,
            "evidence_bindings_verified": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "decision_nonce_reference_present": False,
            "replay_protection_verified": False,

            "all_decision_recording_prerequisites_satisfied": False,
            "authorization_decision_recording_authorized": False,
            "authorization_decision_may_be_recorded": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,

            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,
            "session_creation_may_proceed": False,
            "recording_gate_may_open": False,
        }

        # GP770 — Preparation Readiness Checkpoint
        safety_state = _false_safety_state()

        checkpoint = {
            "pack": "GP770",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_"
                "DECISION_PREPARATION_READINESS"
            ),
            "preparation_id": preparation_id,
            "prior_pack_range": "GP751-GP760",
            "current_pack_range": "GP761-GP770",
            "recommendation": CURRENT_RECOMMENDATION,
            "preparation_state": PREPARATION_STATE,

            "preparation_sealed": True,

            "decision_recording_request_prepared": True,
            "decision_recording_request_sent": False,
            "decision_recording_request_delivered": False,
            "decision_recording_request_accepted": False,

            "decision_value_present": False,
            "decision_value_selected": False,
            "decision_value_invented": False,

            "decision_reason_present": False,
            "decision_reason_reference_present": False,

            "evidence_package_reference_present": False,
            "evidence_bindings_verified": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "decision_nonce_reference_present": False,
            "replay_protection_verified": False,

            "authorization_decision_recording_authorized": False,
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

            "safety_state": safety_state,

            "next_gate": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_"
                "DECISION_RECORDING_GATE"
            ),
        }

        preparation_payload = {
            "gp761_preparation_shell": preparation_shell,
            "gp762_gate_lineage_intake": gate_lineage_intake,
            "gp763_recording_request_envelope": (
                recording_request_envelope
            ),
            "gp764_decision_value_contract": (
                decision_value_contract
            ),
            "gp765_decision_reason_board": (
                decision_reason_board
            ),
            "gp766_evidence_binding_board": (
                evidence_binding_board
            ),
            "gp767_authority_requirement_board": (
                authority_requirement_board
            ),
            "gp768_replay_protection_board": (
                replay_protection_board
            ),
            "gp769_recording_prerequisite_board": (
                recording_prerequisite_board
            ),
            "gp770_checkpoint": checkpoint,
            "safe_metadata": metadata,
            "requested_operations": operations,
        }

        preparation_payload_json = _canonical_json(
            preparation_payload
        )

        preparation_hash = _sha256_text(
            preparation_payload_json
        )

        created_at = _utc_now()

        with self._connect() as connection:
            connection.execute(
                "BEGIN IMMEDIATE"
            )

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp761_770_owner_session_creation_authorization_decision_preparations
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["preparation_payload_json"]
                    != preparation_payload_json
                    or existing["preparation_hash"]
                    != preparation_hash
                ):
                    raise OwnerSessionCreationAuthorizationDecisionPreparationError(
                        "idempotency_key already exists with different "
                        "immutable decision-preparation inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp761_770_owner_session_creation_authorization_decision_preparations
                ORDER BY rowid DESC
                LIMIT 1
                """
            ).fetchone()

            predecessor_preparation_hash = (
                predecessor["preparation_hash"]
                if predecessor
                else None
            )

            connection.execute(
                """
                INSERT INTO
                    vault_gp761_770_owner_session_creation_authorization_decision_preparations (
                        preparation_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        authorization_decision_gate_id,
                        authorization_decision_gate_hash,
                        authorization_decision_gate_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        preparation_shell_json,
                        gate_lineage_intake_json,
                        recording_request_envelope_json,
                        decision_value_contract_json,
                        decision_reason_board_json,
                        evidence_binding_board_json,
                        authority_requirement_board_json,
                        replay_protection_board_json,
                        recording_prerequisite_board_json,
                        checkpoint_json,
                        preparation_payload_json,
                        preparation_hash,
                        predecessor_preparation_hash,
                        recommendation,
                        preparation_state,
                        created_at
                    )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    preparation_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    authorization_decision_gate_id,
                    authorization_decision_gate_hash,
                    authorization_decision_gate_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(preparation_shell),
                    _canonical_json(gate_lineage_intake),
                    _canonical_json(recording_request_envelope),
                    _canonical_json(decision_value_contract),
                    _canonical_json(decision_reason_board),
                    _canonical_json(evidence_binding_board),
                    _canonical_json(authority_requirement_board),
                    _canonical_json(replay_protection_board),
                    _canonical_json(recording_prerequisite_board),
                    _canonical_json(checkpoint),
                    preparation_payload_json,
                    preparation_hash,
                    predecessor_preparation_hash,
                    CURRENT_RECOMMENDATION,
                    PREPARATION_STATE,
                    created_at,
                ),
            )

            self._append_event(
                connection,
                preparation_id=preparation_id,
                event_type=(
                    "GP761_770_OWNER_SESSION_CREATION_"
                    "AUTHORIZATION_DECISION_PREPARATION_SEALED"
                ),
                event_payload={
                    "preparation_hash": preparation_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "preparation_state": PREPARATION_STATE,
                    "decision_recording_request_prepared": True,
                    "decision_recording_request_sent": False,
                    "authorization_decision_recording_authorized": False,
                    "authorization_decision_recorded": False,
                    "authorization_granted": False,
                    "owner_session_creation_authorized": False,
                    "owner_session_created": False,
                    "owner_authenticated": False,
                    "owner_stepped_up": False,
                    "owner_decision_recording_gate_opened": False,
                    "owner_decision_recorded": False,
                    "go_decision_granted": False,
                    "recovery_authorization_granted": False,
                    "authorization_token_issued": False,
                    "recovery_commit_command_issued": False,
                    "production_write_occurred": False,
                    "provider_connection_occurred": False,
                    "destructive_action_occurred": False,
                },
            )

            row = connection.execute(
                """
                SELECT *
                FROM vault_gp761_770_owner_session_creation_authorization_decision_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

            if row is None:
                raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                    "authorization decision preparation failed to persist"
                )

            return self._receipt_from_row(
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
                FROM vault_gp761_770_owner_session_creation_authorization_decision_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP761-GP770 preparation: {preparation_id}"
            )

        result = dict(row)

        json_columns = (
            "preparation_shell_json",
            "gate_lineage_intake_json",
            "recording_request_envelope_json",
            "decision_value_contract_json",
            "decision_reason_board_json",
            "evidence_binding_board_json",
            "authority_requirement_board_json",
            "replay_protection_board_json",
            "recording_prerequisite_board_json",
            "checkpoint_json",
            "preparation_payload_json",
        )

        for column in json_columns:
            result[column[:-5]] = json.loads(
                result.pop(column)
            )

        return result

    def list_events(
        self,
        preparation_id: str,
    ) -> list[dict[str, Any]]:
        preparation_id = _required_text(
            "preparation_id",
            preparation_id,
        )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM vault_gp761_770_owner_session_creation_authorization_decision_events
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

        payload_json = _canonical_json(
            record["preparation_payload"]
        )

        if _sha256_text(payload_json) != record["preparation_hash"]:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision preparation payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision preparation destination is not Tower"
            )

        if (
            record["authorization_decision_gate_state"]
            != REQUIRED_GATE_STATE
        ):
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "authorization decision gate lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision preparation recommendation mismatch"
            )

        if record["preparation_state"] != PREPARATION_STATE:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision preparation state mismatch"
            )

        envelope = record[
            "recording_request_envelope"
        ]

        if envelope["request_prepared"] is not True:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision recording request was not prepared"
            )

        forbidden_envelope_fields = (
            "request_sent",
            "request_delivered",
            "request_accepted",
            "decision_recording_authorized",
            "authorization_decision_recorded",
            "authorization_granted",
        )

        invalid_envelope = [
            field
            for field in forbidden_envelope_fields
            if envelope[field] is True
        ]

        if invalid_envelope:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "unsafe recording request state: "
                + ", ".join(invalid_envelope)
            )

        value_contract = record[
            "decision_value_contract"
        ]

        forbidden_value_fields = (
            "decision_value_present",
            "decision_value_selected",
            "decision_value_invented",
            "authorization_decision_ready",
        )

        invalid_value_fields = [
            field
            for field in forbidden_value_fields
            if value_contract[field] is True
        ]

        if invalid_value_fields:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "unsafe decision value state: "
                + ", ".join(invalid_value_fields)
            )

        prerequisite_board = record[
            "recording_prerequisite_board"
        ]

        forbidden_prerequisite_fields = (
            "decision_value_present",
            "decision_value_selected",
            "decision_reason_present",
            "decision_reason_reference_present",
            "evidence_package_reference_present",
            "evidence_bindings_verified",
            "tower_owner_session_present",
            "owner_authenticated",
            "owner_stepped_up",
            "owner_admin_approval_granted",
            "second_authority_review_granted",
            "dual_receipt_satisfied",
            "decision_nonce_reference_present",
            "replay_protection_verified",
            "all_decision_recording_prerequisites_satisfied",
            "authorization_decision_recording_authorized",
            "authorization_decision_may_be_recorded",
            "authorization_decision_recorded",
            "authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
            "session_creation_may_proceed",
            "recording_gate_may_open",
        )

        invalid_prerequisites = [
            field
            for field in forbidden_prerequisite_fields
            if prerequisite_board[field] is True
        ]

        if invalid_prerequisites:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "unsafe decision prerequisite state: "
                + ", ".join(invalid_prerequisites)
            )

        checkpoint = record["checkpoint"]
        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision preparation safety field mismatch"
            )

        unsafe_true = sorted(
            field
            for field, value in safety_state.items()
            if value is True
        )

        if unsafe_true:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "unsafe completed actions: "
                + ", ".join(unsafe_true)
            )

        events = self.list_events(
            preparation_id
        )

        if not events:
            raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                "decision preparation has no append-only events"
            )

        previous_event_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                    "decision preparation event predecessor mismatch"
                )

            material = {
                "preparation_id": event["preparation_id"],
                "event_type": event["event_type"],
                "event_payload": event["event_payload"],
                "previous_event_hash": event["previous_event_hash"],
                "created_at": event["created_at"],
            }

            expected_event_hash = _sha256_text(
                _canonical_json(material)
            )

            if expected_event_hash != event["event_hash"]:
                raise OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError(
                    "decision preparation event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP761-GP770",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "authorization_decision_gate_lineage_valid": True,

            "preparation_sealed": True,

            "decision_recording_request_prepared": True,
            "decision_recording_request_sent": False,
            "decision_recording_request_delivered": False,
            "decision_recording_request_accepted": False,

            "decision_value_present": False,
            "decision_value_selected": False,
            "decision_value_invented": False,

            "decision_reason_present": False,
            "decision_reason_reference_present": False,

            "evidence_package_reference_present": False,
            "evidence_bindings_verified": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "decision_nonce_reference_present": False,
            "replay_protection_verified": False,

            "authorization_decision_recording_authorized": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,

            "owner_session_creation_authorization_granted": False,
            "tower_owner_session_creation_authorization_granted": False,

            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,

            "owner_session_created": False,
            "owner_session_started": False,

            "recording_gate_open": False,
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
            raise OwnerSessionCreationAuthorizationDecisionPreparationError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationDecisionPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationDecisionPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise OwnerSessionCreationAuthorizationDecisionPreparationError(
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
            FROM vault_gp761_770_owner_session_creation_authorization_decision_events
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

        event_hash = _sha256_text(
            _canonical_json(material)
        )

        connection.execute(
            """
            INSERT INTO
                vault_gp761_770_owner_session_creation_authorization_decision_events (
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

    def _receipt_from_row(
        self,
        row: sqlite3.Row,
        *,
        idempotent_replay: bool,
    ) -> OwnerSessionCreationAuthorizationDecisionPreparationReceipt:
        return OwnerSessionCreationAuthorizationDecisionPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            preparation_state=row["preparation_state"],

            preparation_sealed=True,
            decision_recording_request_prepared=True,
            authorization_decision_recorded=False,
            authorization_granted=False,

            owner_session_creation_authorized=False,
            owner_session_created=False,
            owner_session_started=False,

            recording_gate_open=False,
            owner_decision_recorded=False,

            immutable=True,
            append_only=True,
            idempotent_replay=idempotent_replay,
        )


__all__ = [
    "ALLOWED_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "OwnerSessionCreationAuthorizationDecisionPreparationError",
    "OwnerSessionCreationAuthorizationDecisionPreparationIntegrityError",
    "OwnerSessionCreationAuthorizationDecisionPreparationReceipt",
    "PACK_END",
    "PACK_START",
    "PREPARATION_STATE",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_GATE_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionPreparationLayerService",
    "SAFETY_STATE_FIELDS",
    "SESSION_PURPOSE",
    "SESSION_TYPE",
    "TOWER_DESTINATION",
]
