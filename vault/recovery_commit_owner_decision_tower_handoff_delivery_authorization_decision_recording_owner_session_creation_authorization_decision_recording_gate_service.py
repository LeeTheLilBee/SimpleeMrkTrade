"""Archive Vault GP771-GP780.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Owner Session Creation Authorization Decision Recording Gate.

This layer seals a fail-closed gate around any later Tower-owned recording of
an owner-session-creation authorization decision.

No decision value is accepted, selected, inferred, defaulted, or recorded.
No authorization is granted.

Tower remains the protocol, identity, step-up, session, authorization-decision,
and decision-recording authority.

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


PACK_START = 771
PACK_END = 780

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_OWNER_SESSION_CREATION_"
    "AUTHORIZATION_DECISION_RECORDING_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED"
)

GATE_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "RECORDING_GATE_SEALED_RECORDING_NOT_AUTHORIZED"
)

REQUIRED_PREPARATION_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
    "PREPARATION_SEALED_DECISION_NOT_RECORDED"
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
        "INTAKE_DECISION_PREPARATION_REFERENCE",
        "VERIFY_DECISION_PREPARATION_STATE",
        "VERIFY_DECISION_RECORDING_REQUEST_PREPARED",
        "VERIFY_DECISION_VALUE_REQUIREMENT",
        "VERIFY_DECISION_REASON_REQUIREMENT",
        "VERIFY_EVIDENCE_BINDING_REQUIREMENT",
        "VERIFY_DECISION_AUTHORITY_REQUIREMENT",
        "VERIFY_DECISION_REPLAY_PROTECTION_REQUIREMENT",
        "EVALUATE_DECISION_RECORDING_BLOCKERS",
        "SEAL_DECISION_RECORDING_GATE",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_DECISION_RECORDING_REQUEST",
        "DELIVER_DECISION_RECORDING_REQUEST",
        "ACCEPT_DECISION_RECORDING_REQUEST",
        "AUTHORIZE_DECISION_RECORDING",
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
        "decision_reason",
    }
)

SAFETY_STATE_FIELDS = (
    "decision_recording_request_sent",
    "decision_recording_request_delivered",
    "decision_recording_request_accepted",
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


class OwnerSessionCreationAuthorizationDecisionRecordingGateError(
    ValueError
):
    """Raised when GP771-GP780 gate input is unsafe."""


class OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
    RuntimeError
):
    """Raised when sealed GP771-GP780 evidence fails verification."""


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
        raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
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
        raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
            "safe_metadata must serialize to an object"
        )

    blocked = sorted(
        set(
            _find_blocked_keys(normalized)
        )
    )

    if blocked:
        raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
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
class OwnerSessionCreationAuthorizationDecisionRecordingGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    decision_recording_authorized: bool
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
            "gate_id": self.gate_id,
            "gate_hash": self.gate_hash,
            "recommendation": self.recommendation,
            "gate_state": self.gate_state,
            "gate_sealed": self.gate_sealed,
            "decision_recording_authorized": (
                self.decision_recording_authorized
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


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingGateService:
    """Persistent fail-closed GP771-GP780 decision-recording gate."""

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
                vault_gp771_780_owner_session_creation_authorization_decision_recording_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    decision_preparation_id TEXT NOT NULL,
                    decision_preparation_hash TEXT NOT NULL,
                    decision_preparation_state TEXT NOT NULL
                        CHECK(
                            decision_preparation_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_PREPARATION_SEALED_DECISION_NOT_RECORDED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    gate_shell_json TEXT NOT NULL,
                    preparation_lineage_gate_json TEXT NOT NULL,
                    recording_request_gate_json TEXT NOT NULL,
                    decision_value_gate_json TEXT NOT NULL,
                    decision_reason_gate_json TEXT NOT NULL,
                    evidence_binding_gate_json TEXT NOT NULL,
                    authority_gate_json TEXT NOT NULL,
                    replay_protection_gate_json TEXT NOT NULL,
                    recording_blocker_matrix_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    gate_payload_json TEXT NOT NULL,
                    gate_hash TEXT NOT NULL UNIQUE,
                    predecessor_gate_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED_RECORDING_NOT_AUTHORIZED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp771_780_owner_session_creation_authorization_decision_recording_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES
                        vault_gp771_780_owner_session_creation_authorization_decision_recording_gates(
                            gate_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp771_780_recovery_case
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_gates(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp771_780_preparation
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_gates(
                    decision_preparation_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp771_780_event_chain
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_events(
                    gate_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp771_780_gate_no_update
                BEFORE UPDATE
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP771-GP780 recording gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp771_780_gate_no_delete
                BEFORE DELETE
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP771-GP780 recording gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp771_780_event_no_update
                BEFORE UPDATE
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP771-GP780 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp771_780_event_no_delete
                BEFORE DELETE
                ON vault_gp771_780_owner_session_creation_authorization_decision_recording_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP771-GP780 events are append-only'
                    );
                END;
                """
            )

    def seal_decision_recording_gate(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        decision_preparation_id: str,
        decision_preparation_hash: str,
        decision_preparation_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> OwnerSessionCreationAuthorizationDecisionRecordingGateReceipt:
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

        decision_preparation_id = _required_text(
            "decision_preparation_id",
            decision_preparation_id,
        )

        decision_preparation_hash = _required_text(
            "decision_preparation_hash",
            decision_preparation_hash,
        )

        decision_preparation_state = _required_text(
            "decision_preparation_state",
            decision_preparation_state,
        ).upper()

        if decision_preparation_state != REQUIRED_PREPARATION_STATE:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
                "decision_preparation_state must preserve "
                "OWNER_SESSION_CREATION_AUTHORIZATION_DECISION_"
                "PREPARATION_SEALED_DECISION_NOT_RECORDED"
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
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
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
            "decision_preparation_id": decision_preparation_id,
            "decision_preparation_hash": decision_preparation_hash,
            "decision_preparation_state": decision_preparation_state,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        gate_id = (
            "vault-gp771-780-"
            + _sha256_text(
                _canonical_json(identity)
            )[:24]
        )

        gate_shell = {
            "pack": "GP771",
            "gate_id": gate_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": PRIOR_RECOMMENDATION,
            "recommendation": CURRENT_RECOMMENDATION,
            "gate_state": GATE_STATE,
            "gate_sealed": True,
            "decision_recording_authorized": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
        }

        preparation_lineage_gate = {
            "pack": "GP772",
            "decision_preparation_id": decision_preparation_id,
            "decision_preparation_hash": decision_preparation_hash,
            "decision_preparation_state": decision_preparation_state,
            "required_preparation_state": REQUIRED_PREPARATION_STATE,
            "preparation_reference_present": True,
            "preparation_hash_present": True,
            "preparation_sealed_in_lineage": True,
            "decision_recording_request_prepared_in_lineage": True,
            "decision_recording_request_sent_in_lineage": False,
            "authorization_decision_recorded_in_lineage": False,
            "authorization_granted_in_lineage": False,
        }

        recording_request_gate = {
            "pack": "GP773",
            "destination": TOWER_DESTINATION,
            "recording_authority": TOWER_DESTINATION,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "request_prepared": True,
            "request_sent": False,
            "request_delivered": False,
            "request_accepted": False,
            "decision_recording_authorized": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,
        }

        decision_value_gate = {
            "pack": "GP774",
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
            "implicit_decision_allowed": False,
            "decision_value_requirement_satisfied": False,
            "decision_recording_blocked": True,
        }

        decision_reason_gate = {
            "pack": "GP775",
            "decision_reason_required": True,
            "decision_reason_reference_required": True,
            "decision_reason_present": False,
            "decision_reason_reference_present": False,
            "freeform_raw_reason_allowed": False,
            "tower_safe_reason_required": True,
            "case_bound_reason_required": True,
            "decision_bound_reason_required": True,
            "decision_reason_requirement_satisfied": False,
            "decision_recording_blocked": True,
        }

        evidence_binding_gate = {
            "pack": "GP776",
            "scope_binding_evidence_required": True,
            "lifetime_evidence_required": True,
            "replay_protection_evidence_required": True,
            "authentication_evidence_required": True,
            "step_up_evidence_required": True,
            "evidence_package_reference_present": False,
            "case_binding_verified": False,
            "owner_decision_binding_verified": False,
            "environment_binding_verified": False,
            "tower_authority_binding_verified": False,
            "all_evidence_bindings_verified": False,
            "decision_recording_blocked": True,
        }

        authority_gate = {
            "pack": "GP777",
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
            "decision_authority_requirement_satisfied": False,
            "decision_recording_blocked": True,
        }

        replay_protection_gate = {
            "pack": "GP778",
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
            "decision_recording_blocked": True,
        }

        recording_blocker_matrix = {
            "pack": "GP779",
            "preparation_reference_present": True,
            "preparation_hash_present": True,
            "decision_recording_request_prepared": True,

            "decision_value_present": False,
            "decision_value_selected": False,
            "decision_reason_present": False,
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
            "replay_protection_verified": False,

            "all_recording_prerequisites_satisfied": False,
            "decision_recording_authorized": False,
            "authorization_decision_may_be_recorded": False,
            "authorization_decision_recorded": False,
            "authorization_granted": False,

            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,
            "session_creation_may_proceed": False,
            "owner_decision_recording_gate_may_open": False,
        }

        safety_state = _false_safety_state()

        checkpoint = {
            "pack": "GP780",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_"
                "DECISION_RECORDING_GATE_READINESS"
            ),
            "gate_id": gate_id,
            "prior_pack_range": "GP761-GP770",
            "current_pack_range": "GP771-GP780",
            "recommendation": CURRENT_RECOMMENDATION,
            "gate_state": GATE_STATE,

            "gate_sealed": True,

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
            "all_evidence_bindings_verified": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "decision_nonce_reference_present": False,
            "replay_protection_verified": False,

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

            "safety_state": safety_state,

            "next_gate": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_"
                "DECISION_RECORDING_PREPARATION_LAYER"
            ),
        }

        gate_payload = {
            "gp771_gate_shell": gate_shell,
            "gp772_preparation_lineage_gate": (
                preparation_lineage_gate
            ),
            "gp773_recording_request_gate": recording_request_gate,
            "gp774_decision_value_gate": decision_value_gate,
            "gp775_decision_reason_gate": decision_reason_gate,
            "gp776_evidence_binding_gate": evidence_binding_gate,
            "gp777_authority_gate": authority_gate,
            "gp778_replay_protection_gate": replay_protection_gate,
            "gp779_recording_blocker_matrix": (
                recording_blocker_matrix
            ),
            "gp780_checkpoint": checkpoint,
            "safe_metadata": metadata,
            "requested_operations": operations,
        }

        gate_payload_json = _canonical_json(
            gate_payload
        )

        gate_hash = _sha256_text(
            gate_payload_json
        )

        created_at = _utc_now()

        with self._connect() as connection:
            connection.execute(
                "BEGIN IMMEDIATE"
            )

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["gate_payload_json"]
                    != gate_payload_json
                    or existing["gate_hash"]
                    != gate_hash
                ):
                    raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
                        "idempotency_key already exists with different "
                        "immutable decision-recording-gate inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                ORDER BY rowid DESC
                LIMIT 1
                """
            ).fetchone()

            predecessor_gate_hash = (
                predecessor["gate_hash"]
                if predecessor
                else None
            )

            connection.execute(
                """
                INSERT INTO
                    vault_gp771_780_owner_session_creation_authorization_decision_recording_gates (
                        gate_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        decision_preparation_id,
                        decision_preparation_hash,
                        decision_preparation_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        gate_shell_json,
                        preparation_lineage_gate_json,
                        recording_request_gate_json,
                        decision_value_gate_json,
                        decision_reason_gate_json,
                        evidence_binding_gate_json,
                        authority_gate_json,
                        replay_protection_gate_json,
                        recording_blocker_matrix_json,
                        checkpoint_json,
                        gate_payload_json,
                        gate_hash,
                        predecessor_gate_hash,
                        recommendation,
                        gate_state,
                        created_at
                    )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    gate_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    decision_preparation_id,
                    decision_preparation_hash,
                    decision_preparation_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(gate_shell),
                    _canonical_json(preparation_lineage_gate),
                    _canonical_json(recording_request_gate),
                    _canonical_json(decision_value_gate),
                    _canonical_json(decision_reason_gate),
                    _canonical_json(evidence_binding_gate),
                    _canonical_json(authority_gate),
                    _canonical_json(replay_protection_gate),
                    _canonical_json(recording_blocker_matrix),
                    _canonical_json(checkpoint),
                    gate_payload_json,
                    gate_hash,
                    predecessor_gate_hash,
                    CURRENT_RECOMMENDATION,
                    GATE_STATE,
                    created_at,
                ),
            )

            self._append_event(
                connection,
                gate_id=gate_id,
                event_type=(
                    "GP771_780_OWNER_SESSION_CREATION_"
                    "AUTHORIZATION_DECISION_RECORDING_GATE_SEALED"
                ),
                event_payload={
                    "gate_hash": gate_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "gate_state": GATE_STATE,
                    "gate_sealed": True,
                    "decision_recording_authorized": False,
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
                FROM vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

            if row is None:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                    "decision recording gate failed to persist"
                )

            return self._receipt_from_row(
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
                FROM vault_gp771_780_owner_session_creation_authorization_decision_recording_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP771-GP780 gate: {gate_id}"
            )

        result = dict(row)

        json_columns = (
            "gate_shell_json",
            "preparation_lineage_gate_json",
            "recording_request_gate_json",
            "decision_value_gate_json",
            "decision_reason_gate_json",
            "evidence_binding_gate_json",
            "authority_gate_json",
            "replay_protection_gate_json",
            "recording_blocker_matrix_json",
            "checkpoint_json",
            "gate_payload_json",
        )

        for column in json_columns:
            result[column[:-5]] = json.loads(
                result.pop(column)
            )

        return result

    def list_events(
        self,
        gate_id: str,
    ) -> list[dict[str, Any]]:
        gate_id = _required_text(
            "gate_id",
            gate_id,
        )

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM vault_gp771_780_owner_session_creation_authorization_decision_recording_events
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

        payload_json = _canonical_json(
            record["gate_payload"]
        )

        if _sha256_text(payload_json) != record["gate_hash"]:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording gate payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording gate destination is not Tower"
            )

        if (
            record["decision_preparation_state"]
            != REQUIRED_PREPARATION_STATE
        ):
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision preparation lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording gate recommendation mismatch"
            )

        if record["gate_state"] != GATE_STATE:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording gate state mismatch"
            )

        shell = record["gate_shell"]

        if shell["gate_sealed"] is not True:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording gate is not sealed"
            )

        for field in (
            "decision_recording_authorized",
            "authorization_decision_recorded",
            "authorization_granted",
        ):
            if shell[field] is True:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                    f"unsafe decision recording shell state: {field}"
                )

        recording_request_gate = record[
            "recording_request_gate"
        ]

        if recording_request_gate["request_prepared"] is not True:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording request preparation missing"
            )

        forbidden_request_fields = (
            "request_sent",
            "request_delivered",
            "request_accepted",
            "decision_recording_authorized",
            "authorization_decision_recorded",
            "authorization_granted",
        )

        invalid_request_fields = [
            field
            for field in forbidden_request_fields
            if recording_request_gate[field] is True
        ]

        if invalid_request_fields:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "unsafe decision recording request state: "
                + ", ".join(invalid_request_fields)
            )

        gate_boards = (
            record["decision_value_gate"],
            record["decision_reason_gate"],
            record["evidence_binding_gate"],
            record["authority_gate"],
            record["replay_protection_gate"],
        )

        for gate_board in gate_boards:
            if gate_board["decision_recording_blocked"] is not True:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                    "decision recording blocker is inactive"
                )

        matrix = record[
            "recording_blocker_matrix"
        ]

        forbidden_matrix_fields = (
            "decision_value_present",
            "decision_value_selected",
            "decision_reason_present",
            "decision_reason_reference_present",
            "evidence_package_reference_present",
            "all_evidence_bindings_verified",
            "tower_owner_session_present",
            "owner_authenticated",
            "owner_stepped_up",
            "owner_admin_approval_granted",
            "second_authority_review_granted",
            "dual_receipt_satisfied",
            "decision_nonce_reference_present",
            "replay_protection_verified",
            "all_recording_prerequisites_satisfied",
            "decision_recording_authorized",
            "authorization_decision_may_be_recorded",
            "authorization_decision_recorded",
            "authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
            "session_creation_may_proceed",
            "owner_decision_recording_gate_may_open",
        )

        invalid_matrix_fields = [
            field
            for field in forbidden_matrix_fields
            if matrix[field] is True
        ]

        if invalid_matrix_fields:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "unsafe recording blocker matrix state: "
                + ", ".join(invalid_matrix_fields)
            )

        checkpoint = record["checkpoint"]
        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording safety field mismatch"
            )

        unsafe_true = sorted(
            field
            for field, value in safety_state.items()
            if value is True
        )

        if unsafe_true:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "unsafe completed actions: "
                + ", ".join(unsafe_true)
            )

        events = self.list_events(
            gate_id
        )

        if not events:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                "decision recording gate has no append-only events"
            )

        previous_event_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                    "decision recording event predecessor mismatch"
                )

            material = {
                "gate_id": event["gate_id"],
                "event_type": event["event_type"],
                "event_payload": event["event_payload"],
                "previous_event_hash": event["previous_event_hash"],
                "created_at": event["created_at"],
            }

            expected_event_hash = _sha256_text(
                _canonical_json(material)
            )

            if expected_event_hash != event["event_hash"]:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError(
                    "decision recording event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP771-GP780",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "decision_preparation_lineage_valid": True,

            "gate_sealed": True,

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
            "all_evidence_bindings_verified": False,

            "tower_owner_session_present": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,

            "owner_admin_approval_granted": False,
            "second_authority_review_granted": False,
            "dual_receipt_satisfied": False,

            "decision_nonce_reference_present": False,
            "replay_protection_verified": False,

            "decision_recording_authorized": False,
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
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise OwnerSessionCreationAuthorizationDecisionRecordingGateError(
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
            FROM vault_gp771_780_owner_session_creation_authorization_decision_recording_events
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

        event_hash = _sha256_text(
            _canonical_json(material)
        )

        connection.execute(
            """
            INSERT INTO
                vault_gp771_780_owner_session_creation_authorization_decision_recording_events (
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

    def _receipt_from_row(
        self,
        row: sqlite3.Row,
        *,
        idempotent_replay: bool,
    ) -> OwnerSessionCreationAuthorizationDecisionRecordingGateReceipt:
        return OwnerSessionCreationAuthorizationDecisionRecordingGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            decision_recording_authorized=False,
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
    "GATE_STATE",
    "OwnerSessionCreationAuthorizationDecisionRecordingGateError",
    "OwnerSessionCreationAuthorizationDecisionRecordingGateIntegrityError",
    "OwnerSessionCreationAuthorizationDecisionRecordingGateReceipt",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_PREPARATION_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationDecisionRecordingGateService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
