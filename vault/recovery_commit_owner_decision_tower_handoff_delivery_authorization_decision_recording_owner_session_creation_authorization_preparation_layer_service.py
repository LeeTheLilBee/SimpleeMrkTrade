"""Archive Vault GP741-GP750.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Owner Session Creation Authorization Preparation Layer.

This layer prepares immutable evidence requirements for a later Tower-owned
owner-session-creation authorization decision.

It does not grant authorization, create a session, authenticate an owner,
perform step-up, open the decision-recording gate, or execute recovery.

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


PACK_START = 741
PACK_END = 750

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_OWNER_SESSION_CREATION_"
    "AUTHORIZATION_PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_GATE_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_PREPARED_NOT_GRANTED"
)

PREPARATION_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_"
    "PREPARATION_SEALED_AUTHORIZATION_NOT_GRANTED"
)

REQUIRED_GATE_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_GATE_"
    "SEALED_AUTHORIZATION_NOT_GRANTED"
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
        "INTAKE_CREATION_AUTHORIZATION_GATE_REFERENCE",
        "VERIFY_CREATION_AUTHORIZATION_GATE_STATE",
        "PREPARE_TOWER_AUTHORIZATION_DECISION_REQUEST",
        "PREPARE_SCOPE_BINDING_EVIDENCE_REQUIREMENTS",
        "PREPARE_SESSION_LIFETIME_EVIDENCE_REQUIREMENTS",
        "PREPARE_REPLAY_PROTECTION_EVIDENCE_REQUIREMENTS",
        "PREPARE_OWNER_AUTHENTICATION_EVIDENCE_REQUIREMENTS",
        "PREPARE_OWNER_STEP_UP_EVIDENCE_REQUIREMENTS",
        "PREPARE_AUTHORIZATION_DECISION_PREREQUISITE_BOARD",
        "SEAL_CREATION_AUTHORIZATION_PREPARATION_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SEND_AUTHORIZATION_DECISION_REQUEST",
        "DELIVER_AUTHORIZATION_DECISION_REQUEST",
        "ACCEPT_AUTHORIZATION_DECISION_REQUEST",
        "AUTHORIZE_OWNER_SESSION_CREATION",
        "AUTHORIZE_TOWER_OWNER_SESSION_CREATION",
        "GRANT_OWNER_SESSION_CREATION_AUTHORIZATION",
        "GRANT_TOWER_OWNER_SESSION_CREATION_AUTHORIZATION",
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
        "CREATE_TOWER_DELIVERY_SESSION",
        "START_TOWER_DELIVERY_SESSION",
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
    }
)

SAFETY_STATE_FIELDS = (
    "authorization_decision_request_sent",
    "authorization_decision_request_delivered",
    "authorization_decision_request_accepted",
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
    "tower_delivery_session_created",
    "tower_delivery_session_started",
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


class OwnerSessionCreationAuthorizationPreparationError(ValueError):
    """Raised when GP741-GP750 preparation input is unsafe."""


class OwnerSessionCreationAuthorizationPreparationIntegrityError(RuntimeError):
    """Raised when sealed GP741-GP750 evidence fails verification."""


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
        raise OwnerSessionCreationAuthorizationPreparationError(
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
        raise OwnerSessionCreationAuthorizationPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise OwnerSessionCreationAuthorizationPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise OwnerSessionCreationAuthorizationPreparationError(
            "safe_metadata must serialize to an object"
        )

    blocked = sorted(
        set(_find_blocked_keys(normalized))
    )

    if blocked:
        raise OwnerSessionCreationAuthorizationPreparationError(
            "safe_metadata contains prohibited raw, path, URL, token, "
            "secret, credential, session, or authorization fields: "
            + ", ".join(blocked)
        )

    return normalized


def _false_safety_state() -> dict[str, bool]:
    return {
        field: False
        for field in SAFETY_STATE_FIELDS
    }


@dataclass(frozen=True)
class OwnerSessionCreationAuthorizationPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    preparation_state: str

    preparation_sealed: bool
    authorization_decision_request_prepared: bool
    authorization_granted: bool

    owner_session_creation_authorized: bool
    tower_owner_session_creation_authorized: bool

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
            "authorization_decision_request_prepared": (
                self.authorization_decision_request_prepared
            ),
            "authorization_granted": self.authorization_granted,
            "owner_session_creation_authorized": (
                self.owner_session_creation_authorized
            ),
            "tower_owner_session_creation_authorized": (
                self.tower_owner_session_creation_authorized
            ),
            "owner_session_created": self.owner_session_created,
            "owner_session_started": self.owner_session_started,
            "recording_gate_open": self.recording_gate_open,
            "owner_decision_recorded": self.owner_decision_recorded,
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": self.idempotent_replay,
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationPreparationLayerService:
    """Persistent fail-closed GP741-GP750 preparation service."""

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
                vault_gp741_750_owner_session_creation_authorization_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    creation_authorization_gate_id TEXT NOT NULL,
                    creation_authorization_gate_hash TEXT NOT NULL,
                    creation_authorization_gate_state TEXT NOT NULL
                        CHECK(
                            creation_authorization_gate_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    preparation_shell_json TEXT NOT NULL,
                    gate_lineage_intake_json TEXT NOT NULL,
                    decision_request_envelope_json TEXT NOT NULL,
                    scope_binding_evidence_board_json TEXT NOT NULL,
                    lifetime_evidence_board_json TEXT NOT NULL,
                    replay_evidence_board_json TEXT NOT NULL,
                    authentication_evidence_board_json TEXT NOT NULL,
                    step_up_evidence_board_json TEXT NOT NULL,
                    decision_prerequisite_board_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    preparation_payload_json TEXT NOT NULL,
                    preparation_hash TEXT NOT NULL UNIQUE,
                    predecessor_preparation_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_PREPARED_NOT_GRANTED'
                        ),

                    preparation_state TEXT NOT NULL
                        CHECK(
                            preparation_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_PREPARATION_SEALED_AUTHORIZATION_NOT_GRANTED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp741_750_owner_session_creation_authorization_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES
                        vault_gp741_750_owner_session_creation_authorization_preparations(
                            preparation_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp741_750_recovery_case
                ON vault_gp741_750_owner_session_creation_authorization_preparations(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp741_750_prior_gate
                ON vault_gp741_750_owner_session_creation_authorization_preparations(
                    creation_authorization_gate_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp741_750_event_chain
                ON vault_gp741_750_owner_session_creation_authorization_events(
                    preparation_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp741_750_preparation_no_update
                BEFORE UPDATE
                ON vault_gp741_750_owner_session_creation_authorization_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP741-GP750 authorization preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp741_750_preparation_no_delete
                BEFORE DELETE
                ON vault_gp741_750_owner_session_creation_authorization_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP741-GP750 authorization preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp741_750_event_no_update
                BEFORE UPDATE
                ON vault_gp741_750_owner_session_creation_authorization_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP741-GP750 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp741_750_event_no_delete
                BEFORE DELETE
                ON vault_gp741_750_owner_session_creation_authorization_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP741-GP750 events are append-only'
                    );
                END;
                """
            )

    def seal_authorization_preparation(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        creation_authorization_gate_id: str,
        creation_authorization_gate_hash: str,
        creation_authorization_gate_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> OwnerSessionCreationAuthorizationPreparationReceipt:
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

        creation_authorization_gate_id = _required_text(
            "creation_authorization_gate_id",
            creation_authorization_gate_id,
        )

        creation_authorization_gate_hash = _required_text(
            "creation_authorization_gate_hash",
            creation_authorization_gate_hash,
        )

        creation_authorization_gate_state = _required_text(
            "creation_authorization_gate_state",
            creation_authorization_gate_state,
        ).upper()

        if creation_authorization_gate_state != REQUIRED_GATE_STATE:
            raise OwnerSessionCreationAuthorizationPreparationError(
                "creation_authorization_gate_state must preserve "
                "OWNER_SESSION_CREATION_AUTHORIZATION_GATE_"
                "SEALED_AUTHORIZATION_NOT_GRANTED"
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
            raise OwnerSessionCreationAuthorizationPreparationError(
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
            "creation_authorization_gate_id": (
                creation_authorization_gate_id
            ),
            "creation_authorization_gate_hash": (
                creation_authorization_gate_hash
            ),
            "creation_authorization_gate_state": (
                creation_authorization_gate_state
            ),
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        preparation_id = (
            "vault-gp741-750-"
            + _sha256_text(
                _canonical_json(identity)
            )[:24]
        )

        # GP741 — Authorization Preparation Shell
        preparation_shell = {
            "pack": "GP741",
            "preparation_id": preparation_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": PRIOR_RECOMMENDATION,
            "recommendation": CURRENT_RECOMMENDATION,
            "preparation_state": PREPARATION_STATE,
            "preparation_sealed": True,
            "authorization_decision_request_prepared": True,
            "authorization_granted": False,
        }

        # GP742 — Prior Authorization Gate Intake
        gate_lineage_intake = {
            "pack": "GP742",
            "creation_authorization_gate_id": (
                creation_authorization_gate_id
            ),
            "creation_authorization_gate_hash": (
                creation_authorization_gate_hash
            ),
            "creation_authorization_gate_state": (
                creation_authorization_gate_state
            ),
            "required_gate_state": REQUIRED_GATE_STATE,
            "gate_reference_present": True,
            "gate_hash_present": True,
            "gate_sealed_in_lineage": True,
            "authorization_granted_in_lineage": False,
            "owner_session_created_in_lineage": False,
        }

        # GP743 — Tower Authorization Decision Request Envelope
        decision_request_envelope = {
            "pack": "GP743",
            "envelope_type": (
                "TOWER_OWNER_SESSION_CREATION_"
                "AUTHORIZATION_DECISION_REQUEST_PREPARATION"
            ),
            "destination": TOWER_DESTINATION,
            "decision_authority": TOWER_DESTINATION,
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
            "authorization_decision_recorded": False,
            "authorization_granted": False,
        }

        # GP744 — Scope-Binding Evidence Preparation
        scope_binding_evidence_board = {
            "pack": "GP744",
            "recovery_case_binding_required": True,
            "owner_decision_binding_required": True,
            "environment_binding_required": True,
            "tower_authority_binding_required": True,
            "delivery_target_binding_required": True,
            "scope_binding_evidence_required": True,
            "scope_binding_evidence_reference": None,
            "scope_binding_evidence_present": False,
            "scope_bindings_verified": False,
            "authorization_decision_ready": False,
        }

        # GP745 — Lifetime Evidence Preparation
        lifetime_evidence_board = {
            "pack": "GP745",
            "issued_at_required": True,
            "not_before_required": True,
            "expires_at_required": True,
            "short_lived_session_required": True,
            "indefinite_session_allowed": False,
            "lifetime_evidence_required": True,
            "lifetime_evidence_reference": None,
            "lifetime_evidence_present": False,
            "session_lifetime_verified": False,
            "authorization_decision_ready": False,
        }

        # GP746 — Replay Evidence Preparation
        replay_evidence_board = {
            "pack": "GP746",
            "nonce_reference_required": True,
            "single_active_use_boundary_required": True,
            "replay_detection_required": True,
            "duplicate_use_rejected": True,
            "cross_case_replay_rejected": True,
            "cross_owner_decision_replay_rejected": True,
            "cross_environment_replay_rejected": True,
            "replay_evidence_required": True,
            "replay_evidence_reference": None,
            "replay_evidence_present": False,
            "replay_protection_verified": False,
            "authorization_decision_ready": False,
        }

        # GP747 — Authentication Evidence Preparation
        authentication_evidence_board = {
            "pack": "GP747",
            "tower_authentication_required": True,
            "authenticated_owner_identity_required": True,
            "owner_identity_binding_required": True,
            "anonymous_session_allowed": False,
            "vault_authentication_allowed": False,
            "authentication_evidence_required": True,
            "authentication_evidence_reference": None,
            "authentication_evidence_present": False,
            "owner_authenticated": False,
            "authentication_verified": False,
            "authorization_decision_ready": False,
        }

        # GP748 — Step-Up Evidence Preparation
        step_up_evidence_board = {
            "pack": "GP748",
            "tower_step_up_required": True,
            "purpose_bound_step_up_required": True,
            "recovery_case_bound_step_up_required": True,
            "owner_decision_bound_step_up_required": True,
            "fresh_step_up_required": True,
            "vault_step_up_allowed": False,
            "step_up_evidence_required": True,
            "step_up_evidence_reference": None,
            "step_up_evidence_present": False,
            "owner_stepped_up": False,
            "step_up_verified": False,
            "authorization_decision_ready": False,
        }

        # GP749 — Authorization Decision Prerequisite Board
        decision_prerequisite_board = {
            "pack": "GP749",
            "prior_gate_reference_present": True,
            "prior_gate_hash_present": True,
            "authorization_decision_request_prepared": True,

            "scope_binding_evidence_present": False,
            "scope_bindings_verified": False,

            "lifetime_evidence_present": False,
            "session_lifetime_verified": False,

            "replay_evidence_present": False,
            "replay_protection_verified": False,

            "authentication_evidence_present": False,
            "owner_authenticated": False,
            "authentication_verified": False,

            "step_up_evidence_present": False,
            "owner_stepped_up": False,
            "step_up_verified": False,

            "all_authorization_decision_prerequisites_satisfied": False,
            "authorization_decision_may_be_recorded": False,

            "owner_session_creation_authorization_granted": False,
            "tower_owner_session_creation_authorization_granted": False,

            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,

            "session_creation_may_proceed": False,
            "recording_gate_may_open": False,
        }

        # GP750 — Authorization Preparation Readiness Checkpoint
        safety_state = _false_safety_state()

        checkpoint = {
            "pack": "GP750",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_"
                "PREPARATION_READINESS"
            ),
            "preparation_id": preparation_id,
            "prior_pack_range": "GP731-GP740",
            "current_pack_range": "GP741-GP750",
            "recommendation": CURRENT_RECOMMENDATION,
            "preparation_state": PREPARATION_STATE,

            "preparation_sealed": True,

            "authorization_decision_request_prepared": True,
            "authorization_decision_request_sent": False,
            "authorization_decision_request_delivered": False,
            "authorization_decision_request_accepted": False,
            "authorization_decision_recorded": False,

            "scope_binding_evidence_present": False,
            "scope_bindings_verified": False,

            "lifetime_evidence_present": False,
            "session_lifetime_verified": False,

            "replay_evidence_present": False,
            "replay_protection_verified": False,

            "authentication_evidence_present": False,
            "owner_authenticated": False,
            "authentication_verified": False,

            "step_up_evidence_present": False,
            "owner_stepped_up": False,
            "step_up_verified": False,

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

            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

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
                "DECISION_GATE"
            ),
        }

        preparation_payload = {
            "gp741_preparation_shell": preparation_shell,
            "gp742_gate_lineage_intake": gate_lineage_intake,
            "gp743_decision_request_envelope": decision_request_envelope,
            "gp744_scope_binding_evidence_board": (
                scope_binding_evidence_board
            ),
            "gp745_lifetime_evidence_board": lifetime_evidence_board,
            "gp746_replay_evidence_board": replay_evidence_board,
            "gp747_authentication_evidence_board": (
                authentication_evidence_board
            ),
            "gp748_step_up_evidence_board": step_up_evidence_board,
            "gp749_decision_prerequisite_board": (
                decision_prerequisite_board
            ),
            "gp750_checkpoint": checkpoint,
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
            connection.execute("BEGIN IMMEDIATE")

            existing = connection.execute(
                """
                SELECT *
                FROM vault_gp741_750_owner_session_creation_authorization_preparations
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
                    raise OwnerSessionCreationAuthorizationPreparationError(
                        "idempotency_key already exists with different "
                        "immutable authorization-preparation inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp741_750_owner_session_creation_authorization_preparations
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
                    vault_gp741_750_owner_session_creation_authorization_preparations (
                        preparation_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        creation_authorization_gate_id,
                        creation_authorization_gate_hash,
                        creation_authorization_gate_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        preparation_shell_json,
                        gate_lineage_intake_json,
                        decision_request_envelope_json,
                        scope_binding_evidence_board_json,
                        lifetime_evidence_board_json,
                        replay_evidence_board_json,
                        authentication_evidence_board_json,
                        step_up_evidence_board_json,
                        decision_prerequisite_board_json,
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
                    creation_authorization_gate_id,
                    creation_authorization_gate_hash,
                    creation_authorization_gate_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(preparation_shell),
                    _canonical_json(gate_lineage_intake),
                    _canonical_json(decision_request_envelope),
                    _canonical_json(scope_binding_evidence_board),
                    _canonical_json(lifetime_evidence_board),
                    _canonical_json(replay_evidence_board),
                    _canonical_json(authentication_evidence_board),
                    _canonical_json(step_up_evidence_board),
                    _canonical_json(decision_prerequisite_board),
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
                    "GP741_750_OWNER_SESSION_CREATION_"
                    "AUTHORIZATION_PREPARATION_SEALED"
                ),
                event_payload={
                    "preparation_hash": preparation_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "preparation_state": PREPARATION_STATE,
                    "authorization_decision_request_prepared": True,
                    "authorization_decision_request_sent": False,
                    "authorization_granted": False,
                    "owner_session_creation_authorized": False,
                    "tower_owner_session_creation_authorized": False,
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
                FROM vault_gp741_750_owner_session_creation_authorization_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

            if row is None:
                raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                    "authorization preparation failed to persist"
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
                FROM vault_gp741_750_owner_session_creation_authorization_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP741-GP750 preparation: {preparation_id}"
            )

        result = dict(row)

        json_columns = (
            "preparation_shell_json",
            "gate_lineage_intake_json",
            "decision_request_envelope_json",
            "scope_binding_evidence_board_json",
            "lifetime_evidence_board_json",
            "replay_evidence_board_json",
            "authentication_evidence_board_json",
            "step_up_evidence_board_json",
            "decision_prerequisite_board_json",
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
                FROM vault_gp741_750_owner_session_creation_authorization_events
                WHERE preparation_id = ?
                ORDER BY event_id ASC
                """,
                (preparation_id,),
            ).fetchall()

        events: list[dict[str, Any]] = []

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

        payload_json = _canonical_json(
            record["preparation_payload"]
        )

        if _sha256_text(payload_json) != record["preparation_hash"]:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization preparation payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization preparation destination is not Tower"
            )

        if (
            record["creation_authorization_gate_state"]
            != REQUIRED_GATE_STATE
        ):
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "creation authorization gate lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization preparation recommendation mismatch"
            )

        if record["preparation_state"] != PREPARATION_STATE:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization preparation state mismatch"
            )

        envelope = record["decision_request_envelope"]

        if envelope["request_prepared"] is not True:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization decision request was not prepared"
            )

        forbidden_envelope_true = (
            "request_sent",
            "request_delivered",
            "request_accepted",
            "authorization_decision_recorded",
            "authorization_granted",
        )

        invalid_envelope = [
            field
            for field in forbidden_envelope_true
            if envelope[field] is True
        ]

        if invalid_envelope:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "unsafe decision request state: "
                + ", ".join(invalid_envelope)
            )

        prerequisite_board = record[
            "decision_prerequisite_board"
        ]

        false_prerequisites = (
            "scope_binding_evidence_present",
            "scope_bindings_verified",
            "lifetime_evidence_present",
            "session_lifetime_verified",
            "replay_evidence_present",
            "replay_protection_verified",
            "authentication_evidence_present",
            "owner_authenticated",
            "authentication_verified",
            "step_up_evidence_present",
            "owner_stepped_up",
            "step_up_verified",
            "all_authorization_decision_prerequisites_satisfied",
            "authorization_decision_may_be_recorded",
            "owner_session_creation_authorization_granted",
            "tower_owner_session_creation_authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
            "session_creation_may_proceed",
            "recording_gate_may_open",
        )

        invalid_prerequisites = [
            field
            for field in false_prerequisites
            if prerequisite_board[field] is True
        ]

        if invalid_prerequisites:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "unsafe authorization prerequisite state: "
                + ", ".join(invalid_prerequisites)
            )

        checkpoint = record["checkpoint"]
        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization preparation safety field mismatch"
            )

        unsafe_true = sorted(
            field
            for field, value in safety_state.items()
            if value is True
        )

        if unsafe_true:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "unsafe completed authorization actions: "
                + ", ".join(unsafe_true)
            )

        false_checkpoint_fields = (
            "authorization_decision_request_sent",
            "authorization_decision_request_delivered",
            "authorization_decision_request_accepted",
            "authorization_decision_recorded",
            "scope_binding_evidence_present",
            "scope_bindings_verified",
            "lifetime_evidence_present",
            "session_lifetime_verified",
            "replay_evidence_present",
            "replay_protection_verified",
            "authentication_evidence_present",
            "owner_authenticated",
            "authentication_verified",
            "step_up_evidence_present",
            "owner_stepped_up",
            "step_up_verified",
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

        invalid_checkpoint = [
            field
            for field in false_checkpoint_fields
            if checkpoint[field] is True
        ]

        if invalid_checkpoint:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "unsafe GP750 checkpoint state: "
                + ", ".join(invalid_checkpoint)
            )

        events = self.list_events(preparation_id)

        if not events:
            raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                "authorization preparation has no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                    "authorization preparation event predecessor mismatch"
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
                raise OwnerSessionCreationAuthorizationPreparationIntegrityError(
                    "authorization preparation event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP741-GP750",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "authorization_gate_lineage_valid": True,

            "preparation_sealed": True,
            "authorization_decision_request_prepared": True,
            "authorization_decision_request_sent": False,
            "authorization_decision_recorded": False,

            "scope_binding_evidence_present": False,
            "scope_bindings_verified": False,

            "lifetime_evidence_present": False,
            "session_lifetime_verified": False,

            "replay_evidence_present": False,
            "replay_protection_verified": False,

            "authentication_evidence_present": False,
            "owner_authenticated": False,
            "authentication_verified": False,

            "step_up_evidence_present": False,
            "owner_stepped_up": False,
            "step_up_verified": False,

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
            return sorted(ALLOWED_OPERATIONS)

        if isinstance(requested_operations, (str, bytes)):
            raise OwnerSessionCreationAuthorizationPreparationError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise OwnerSessionCreationAuthorizationPreparationError(
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
            FROM vault_gp741_750_owner_session_creation_authorization_events
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

        event_hash = _sha256_text(
            _canonical_json(material)
        )

        connection.execute(
            """
            INSERT INTO
                vault_gp741_750_owner_session_creation_authorization_events (
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
    ) -> OwnerSessionCreationAuthorizationPreparationReceipt:
        return OwnerSessionCreationAuthorizationPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            preparation_state=row["preparation_state"],

            preparation_sealed=True,
            authorization_decision_request_prepared=True,
            authorization_granted=False,

            owner_session_creation_authorized=False,
            tower_owner_session_creation_authorized=False,

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
    "OwnerSessionCreationAuthorizationPreparationError",
    "OwnerSessionCreationAuthorizationPreparationIntegrityError",
    "OwnerSessionCreationAuthorizationPreparationReceipt",
    "PACK_END",
    "PACK_START",
    "PREPARATION_STATE",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_GATE_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationPreparationLayerService",
    "SAFETY_STATE_FIELDS",
    "SESSION_PURPOSE",
    "SESSION_TYPE",
    "TOWER_DESTINATION",
]
