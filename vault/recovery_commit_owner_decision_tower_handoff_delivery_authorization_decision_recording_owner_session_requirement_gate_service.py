"""Archive Vault GP711-GP720.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Owner Session Requirement Gate.

This layer seals a fail-closed requirement gate around the future existence of
a real Tower owner session before any owner decision recording can proceed.

It does not create or start an owner session.

Doctrine:
    Tower is the face and protocol authority.
    Vault is sealed memory.
    Teller is the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller

Prior recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_PREPARED

Current recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_GATE_SEALED

This service never:
    * creates an owner session
    * starts an owner session
    * creates a Tower owner session
    * starts a Tower owner session
    * authenticates an owner
    * performs owner step-up
    * opens the owner decision recording gate
    * invents, recommends, defaults, selects, or records an owner decision
    * grants owner or administrator approval
    * satisfies dual receipt
    * grants second-authority review
    * grants a GO decision
    * grants or issues recovery authorization
    * issues or mints an authorization token
    * sends or delivers a handoff
    * starts a Tower delivery session
    * activates scope, commit, execution, or recovery windows
    * opens a commit point
    * issues or executes a recovery commit command
    * restores data
    * mounts or writes production storage
    * connects an external provider
    * exposes raw material, paths, URLs, credentials, sessions, or tokens
    * performs destructive action
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


PACK_START = 711
PACK_END = 720

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_OWNER_SESSION_REQUIREMENT_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_PREPARED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_GATE_SEALED"
)

GATE_STATE = (
    "OWNER_SESSION_REQUIREMENT_GATE_"
    "SEALED_SESSION_ABSENT"
)

REQUIRED_RECORDING_PREPARATION_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_"
    "PREPARED_GATE_REMAINS_CLOSED"
)

TOWER_DESTINATION = "TOWER"

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_GATE_OPERATIONS = frozenset(
    {
        "INTAKE_RECORDING_PREPARATION_REFERENCE",
        "VERIFY_RECORDING_PREPARATION_STATE",
        "VERIFY_RECORDING_GATE_CLOSED",
        "EVALUATE_OWNER_SESSION_REQUIREMENT",
        "EVALUATE_TOWER_OWNER_SESSION_REQUIREMENT",
        "EVALUATE_SESSION_BINDING_REQUIREMENT",
        "EVALUATE_SESSION_EXPIRY_REQUIREMENT",
        "EVALUATE_SESSION_REPLAY_REQUIREMENT",
        "EVALUATE_OWNER_SESSION_BLOCKERS",
        "SEAL_OWNER_SESSION_REQUIREMENT_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "ISSUE_OWNER_SESSION",
        "ACTIVATE_OWNER_SESSION",
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
    }
)

SAFETY_STATE_FIELDS = (
    "owner_session_created",
    "owner_session_started",
    "owner_session_issued",
    "owner_session_activated",
    "tower_owner_session_created",
    "tower_owner_session_started",
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


class OwnerSessionRequirementGateError(ValueError):
    """Raised when GP711-GP720 input violates the session gate."""


class OwnerSessionRequirementGateIntegrityError(RuntimeError):
    """Raised when sealed GP711-GP720 evidence fails verification."""


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="microseconds"
    )


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


def _required_text(
    name: str,
    value: Any,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OwnerSessionRequirementGateError(
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
                blocked.append(
                    nested_location
                )

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
        raise OwnerSessionRequirementGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(
                dict(value)
            )
        )
    except (TypeError, ValueError) as exc:
        raise OwnerSessionRequirementGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise OwnerSessionRequirementGateError(
            "safe_metadata must serialize to an object"
        )

    blocked = sorted(
        set(
            _find_blocked_keys(
                normalized
            )
        )
    )

    if blocked:
        raise OwnerSessionRequirementGateError(
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
class OwnerSessionRequirementGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    owner_session_required: bool
    owner_session_created: bool
    owner_session_started: bool
    tower_owner_session_created: bool
    tower_owner_session_started: bool
    recording_gate_open: bool
    owner_decision_recorded: bool

    immutable: bool
    append_only: bool
    idempotent_replay: bool

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "gate_hash": self.gate_hash,
            "recommendation": self.recommendation,
            "gate_state": self.gate_state,
            "gate_sealed": self.gate_sealed,
            "owner_session_required": (
                self.owner_session_required
            ),
            "owner_session_created": (
                self.owner_session_created
            ),
            "owner_session_started": (
                self.owner_session_started
            ),
            "tower_owner_session_created": (
                self.tower_owner_session_created
            ),
            "tower_owner_session_started": (
                self.tower_owner_session_started
            ),
            "recording_gate_open": (
                self.recording_gate_open
            ),
            "owner_decision_recorded": (
                self.owner_decision_recorded
            ),
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": (
                self.idempotent_replay
            ),
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionRequirementGateService:
    """Persistent GP711-GP720 fail-closed owner session requirement gate."""

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
    def _connect(
        self,
    ) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            str(
                self.database_path
            )
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            "PRAGMA busy_timeout = 5000"
        )

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_schema(
        self,
    ) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS
                vault_gp711_720_owner_session_requirement_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    recording_preparation_id TEXT NOT NULL,
                    recording_preparation_hash TEXT NOT NULL,
                    recording_preparation_state TEXT NOT NULL
                        CHECK(
                            recording_preparation_state =
                            'AUTHORIZATION_DECISION_RECORDING_PREPARED_GATE_REMAINS_CLOSED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    gate_shell_json TEXT NOT NULL,
                    preparation_lineage_gate_json TEXT NOT NULL,
                    owner_session_contract_board_json TEXT NOT NULL,
                    tower_session_authority_board_json TEXT NOT NULL,
                    session_binding_requirement_board_json TEXT NOT NULL,
                    session_expiry_requirement_board_json TEXT NOT NULL,
                    replay_protection_requirement_board_json TEXT NOT NULL,
                    session_prerequisite_matrix_json TEXT NOT NULL,
                    session_blocker_board_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    gate_payload_json TEXT NOT NULL,
                    gate_hash TEXT NOT NULL UNIQUE,
                    predecessor_gate_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'OWNER_SESSION_REQUIREMENT_GATE_SEALED_SESSION_ABSENT'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp711_720_owner_session_requirement_gate_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES
                        vault_gp711_720_owner_session_requirement_gates(
                            gate_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp711_720_recovery_case
                ON vault_gp711_720_owner_session_requirement_gates(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp711_720_recording_preparation
                ON vault_gp711_720_owner_session_requirement_gates(
                    recording_preparation_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp711_720_event_chain
                ON vault_gp711_720_owner_session_requirement_gate_events(
                    gate_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp711_720_gate_no_update
                BEFORE UPDATE
                ON vault_gp711_720_owner_session_requirement_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP711-GP720 owner session requirement gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp711_720_gate_no_delete
                BEFORE DELETE
                ON vault_gp711_720_owner_session_requirement_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP711-GP720 owner session requirement gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp711_720_event_no_update
                BEFORE UPDATE
                ON vault_gp711_720_owner_session_requirement_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP711-GP720 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp711_720_event_no_delete
                BEFORE DELETE
                ON vault_gp711_720_owner_session_requirement_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP711-GP720 events are append-only'
                    );
                END;
                """
            )

    def seal_owner_session_requirement_gate(
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
    ) -> OwnerSessionRequirementGateReceipt:
        """Seal owner-session requirements without creating a session."""

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

        if (
            recording_preparation_state
            != REQUIRED_RECORDING_PREPARATION_STATE
        ):
            raise OwnerSessionRequirementGateError(
                "recording_preparation_state must preserve "
                "AUTHORIZATION_DECISION_RECORDING_"
                "PREPARED_GATE_REMAINS_CLOSED"
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
            raise OwnerSessionRequirementGateError(
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
            "owner_decision_record_id": (
                owner_decision_record_id
            ),
            "recording_preparation_id": (
                recording_preparation_id
            ),
            "recording_preparation_hash": (
                recording_preparation_hash
            ),
            "recording_preparation_state": (
                recording_preparation_state
            ),
            "tower_authority_id": (
                tower_authority_id
            ),
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "target_environment": (
                target_environment
            ),
            "destination": TOWER_DESTINATION,
        }

        gate_id = (
            "vault-gp711-720-"
            + _sha256_text(
                _canonical_json(
                    identity
                )
            )[:24]
        )

        # GP711 — Owner Session Requirement Gate Shell
        gate_shell = {
            "pack": "GP711",
            "gate_id": gate_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": (
                PRIOR_RECOMMENDATION
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "gate_state": GATE_STATE,
            "gate_sealed": True,
            "owner_session_required": True,
            "owner_session_created": False,
            "owner_session_started": False,
        }

        # GP712 — Recording Preparation Lineage Gate
        preparation_lineage_gate = {
            "pack": "GP712",
            "recording_preparation_id": (
                recording_preparation_id
            ),
            "recording_preparation_hash": (
                recording_preparation_hash
            ),
            "recording_preparation_state": (
                recording_preparation_state
            ),
            "required_state": (
                REQUIRED_RECORDING_PREPARATION_STATE
            ),
            "recording_preparation_reference_present": True,
            "recording_preparation_hash_present": True,
            "recording_gate_open_in_lineage": False,
            "owner_session_created_in_lineage": False,
            "owner_session_started_in_lineage": False,
            "owner_decision_recorded_in_lineage": False,
        }

        # GP713 — Owner Session Contract Board
        owner_session_contract_board = {
            "pack": "GP713",
            "session_type": (
                "TOWER_OWNER_DECISION_RECORDING_SESSION"
            ),
            "session_required": True,
            "session_authority": TOWER_DESTINATION,
            "session_owner_scope_required": True,
            "session_recovery_case_binding_required": True,
            "session_owner_decision_binding_required": True,
            "session_target_environment_binding_required": True,
            "session_created": False,
            "session_started": False,
            "session_issued": False,
            "session_activated": False,
            "session_reference": None,
        }

        # GP714 — Tower Owner Session Authority Board
        tower_session_authority_board = {
            "pack": "GP714",
            "tower_authority_id": (
                tower_authority_id
            ),
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "destination": TOWER_DESTINATION,
            "tower_is_session_authority": True,
            "vault_may_create_owner_session": False,
            "vault_may_start_owner_session": False,
            "teller_may_create_owner_session": False,
            "teller_may_start_owner_session": False,
            "direct_user_vault_session_allowed": False,
            "tower_owner_session_created": False,
            "tower_owner_session_started": False,
        }

        # GP715 — Session Binding Requirement Board
        session_binding_requirement_board = {
            "pack": "GP715",
            "recovery_case_id": (
                recovery_case_id
            ),
            "owner_decision_record_id": (
                owner_decision_record_id
            ),
            "target_environment": (
                target_environment
            ),
            "tower_authority_id": (
                tower_authority_id
            ),
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "recovery_case_binding_required": True,
            "owner_decision_binding_required": True,
            "target_environment_binding_required": True,
            "tower_authority_binding_required": True,
            "delivery_target_binding_required": True,
            "all_session_bindings_present": False,
            "session_binding_receipt_reference": None,
        }

        # GP716 — Session Expiry Requirement Board
        session_expiry_requirement_board = {
            "pack": "GP716",
            "explicit_expiry_required": True,
            "short_lived_session_required": True,
            "expired_session_rejected": True,
            "missing_expiry_rejected": True,
            "indefinite_session_allowed": False,
            "session_expiry_reference": None,
            "session_expiry_verified": False,
        }

        # GP717 — Session Replay Protection Requirement Board
        replay_protection_requirement_board = {
            "pack": "GP717",
            "single_active_use_boundary_required": True,
            "session_nonce_reference_required": True,
            "session_replay_detection_required": True,
            "duplicate_session_use_rejected": True,
            "cross_case_replay_rejected": True,
            "cross_owner_decision_replay_rejected": True,
            "cross_environment_replay_rejected": True,
            "session_nonce_reference": None,
            "replay_protection_verified": False,
        }

        # GP718 — Owner Session Prerequisite Matrix
        session_prerequisite_matrix = {
            "pack": "GP718",
            "recording_preparation_reference_present": True,
            "recording_preparation_hash_present": True,
            "tower_authority_reference_present": True,
            "owner_decision_reference_present": True,

            "owner_session_created": False,
            "owner_session_started": False,
            "tower_owner_session_created": False,
            "tower_owner_session_started": False,

            "session_binding_receipt_present": False,
            "session_expiry_verified": False,
            "session_replay_protection_verified": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,

            "all_owner_session_prerequisites_satisfied": False,
            "recording_gate_may_open": False,
        }

        # GP719 — Owner Session Safety Blocker Board
        safety_state = _false_safety_state()

        session_blocker_board = {
            "pack": "GP719",
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "owner_session_gate_blocked": True,
            "decision_recording_blocked": True,
            "authorization_blocked": True,
            "delivery_blocked": True,
            "safety_state": (
                safety_state
            ),
            "active_blockers": [
                "NO_OWNER_SESSION",
                "NO_TOWER_OWNER_SESSION",
                "NO_SESSION_BINDING_RECEIPT",
                "NO_SESSION_EXPIRY_VERIFICATION",
                "NO_SESSION_REPLAY_PROTECTION_VERIFICATION",
                "NO_OWNER_AUTHENTICATION",
                "NO_OWNER_STEP_UP",
                "RECORDING_GATE_CLOSED",
                "NO_OWNER_DECISION_RECORD",
                "NO_GO_DECISION",
                "NO_RECOVERY_AUTHORIZATION",
                "NO_AUTHORIZATION_TOKEN",
                "NO_RECOVERY_COMMIT_COMMAND",
                "NO_PROVIDER_CONNECTION",
                "NO_PRODUCTION_STORAGE_WRITE",
            ],
        }

        # GP720 — Owner Session Requirement Gate Readiness Checkpoint
        checkpoint = {
            "pack": "GP720",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_REQUIREMENT_GATE_READINESS"
            ),
            "gate_id": (
                gate_id
            ),
            "prior_pack_range": (
                "GP701-GP710"
            ),
            "current_pack_range": (
                "GP711-GP720"
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "gate_state": (
                GATE_STATE
            ),

            "gate_sealed": True,
            "owner_session_required": True,

            "owner_session_created": False,
            "owner_session_started": False,
            "owner_session_issued": False,
            "owner_session_activated": False,

            "tower_owner_session_created": False,
            "tower_owner_session_started": False,

            "session_binding_receipt_present": False,
            "session_expiry_verified": False,
            "session_replay_protection_verified": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,

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
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,

            "handoff_delivered": False,
            "tower_delivery_session_started": False,

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

            "next_gate": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_PREPARATION_LAYER"
            ),
        }

        gate_payload = {
            "gp711_gate_shell": (
                gate_shell
            ),
            "gp712_preparation_lineage_gate": (
                preparation_lineage_gate
            ),
            "gp713_owner_session_contract_board": (
                owner_session_contract_board
            ),
            "gp714_tower_session_authority_board": (
                tower_session_authority_board
            ),
            "gp715_session_binding_requirement_board": (
                session_binding_requirement_board
            ),
            "gp716_session_expiry_requirement_board": (
                session_expiry_requirement_board
            ),
            "gp717_replay_protection_requirement_board": (
                replay_protection_requirement_board
            ),
            "gp718_session_prerequisite_matrix": (
                session_prerequisite_matrix
            ),
            "gp719_session_blocker_board": (
                session_blocker_board
            ),
            "gp720_checkpoint": (
                checkpoint
            ),
            "safe_metadata": (
                metadata
            ),
            "requested_operations": (
                operations
            ),
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
                FROM vault_gp711_720_owner_session_requirement_gates
                WHERE idempotency_key = ?
                """,
                (
                    idempotency_key,
                ),
            ).fetchone()

            if existing is not None:
                if (
                    existing["gate_payload_json"]
                    != gate_payload_json
                    or existing["gate_hash"]
                    != gate_hash
                ):
                    raise OwnerSessionRequirementGateError(
                        "idempotency_key already exists with "
                        "different immutable owner-session-gate inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp711_720_owner_session_requirement_gates
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
                    vault_gp711_720_owner_session_requirement_gates (
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
                        gate_shell_json,
                        preparation_lineage_gate_json,
                        owner_session_contract_board_json,
                        tower_session_authority_board_json,
                        session_binding_requirement_board_json,
                        session_expiry_requirement_board_json,
                        replay_protection_requirement_board_json,
                        session_prerequisite_matrix_json,
                        session_blocker_board_json,
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
                    recording_preparation_id,
                    recording_preparation_hash,
                    recording_preparation_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(
                        gate_shell
                    ),
                    _canonical_json(
                        preparation_lineage_gate
                    ),
                    _canonical_json(
                        owner_session_contract_board
                    ),
                    _canonical_json(
                        tower_session_authority_board
                    ),
                    _canonical_json(
                        session_binding_requirement_board
                    ),
                    _canonical_json(
                        session_expiry_requirement_board
                    ),
                    _canonical_json(
                        replay_protection_requirement_board
                    ),
                    _canonical_json(
                        session_prerequisite_matrix
                    ),
                    _canonical_json(
                        session_blocker_board
                    ),
                    _canonical_json(
                        checkpoint
                    ),
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
                    "GP711_720_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                    "DECISION_RECORDING_OWNER_SESSION_REQUIREMENT_GATE_SEALED"
                ),
                event_payload={
                    "gate_hash": (
                        gate_hash
                    ),
                    "recommendation": (
                        CURRENT_RECOMMENDATION
                    ),
                    "gate_state": (
                        GATE_STATE
                    ),
                    "gate_sealed": True,
                    "owner_session_required": True,
                    "owner_session_created": False,
                    "owner_session_started": False,
                    "tower_owner_session_created": False,
                    "tower_owner_session_started": False,
                    "owner_authenticated": False,
                    "owner_stepped_up": False,
                    "owner_decision_recording_gate_opened": False,
                    "owner_decision_recorded": False,
                    "recovery_authorization_granted": False,
                    "authorization_token_issued": False,
                    "go_decision_granted": False,
                    "recovery_commit_command_issued": False,
                    "provider_connection_occurred": False,
                    "production_write_occurred": False,
                    "destructive_action_occurred": False,
                },
            )

            row = connection.execute(
                """
                SELECT *
                FROM vault_gp711_720_owner_session_requirement_gates
                WHERE gate_id = ?
                """,
                (
                    gate_id,
                ),
            ).fetchone()

            if row is None:
                raise OwnerSessionRequirementGateIntegrityError(
                    "owner session requirement gate failed to persist"
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
                FROM vault_gp711_720_owner_session_requirement_gates
                WHERE gate_id = ?
                """,
                (
                    gate_id,
                ),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP711-GP720 gate: {gate_id}"
            )

        result = dict(
            row
        )

        json_columns = (
            "gate_shell_json",
            "preparation_lineage_gate_json",
            "owner_session_contract_board_json",
            "tower_session_authority_board_json",
            "session_binding_requirement_board_json",
            "session_expiry_requirement_board_json",
            "replay_protection_requirement_board_json",
            "session_prerequisite_matrix_json",
            "session_blocker_board_json",
            "checkpoint_json",
            "gate_payload_json",
        )

        for column in json_columns:
            result[
                column[:-5]
            ] = json.loads(
                result.pop(
                    column
                )
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
                FROM vault_gp711_720_owner_session_requirement_gate_events
                WHERE gate_id = ?
                ORDER BY event_id ASC
                """,
                (
                    gate_id,
                ),
            ).fetchall()

        events: list[dict[str, Any]] = []

        for row in rows:
            event = dict(
                row
            )

            event[
                "event_payload"
            ] = json.loads(
                event.pop(
                    "event_payload_json"
                )
            )

            events.append(
                event
            )

        return events

    def verify_gate(
        self,
        gate_id: str,
    ) -> dict[str, Any]:
        record = self.get_gate(
            gate_id
        )

        payload_json = _canonical_json(
            record[
                "gate_payload"
            ]
        )

        expected_gate_hash = _sha256_text(
            payload_json
        )

        if (
            expected_gate_hash
            != record["gate_hash"]
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session gate payload hash mismatch"
            )

        if (
            record["destination"]
            != TOWER_DESTINATION
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session gate destination is not Tower"
            )

        if (
            record["recording_preparation_state"]
            != REQUIRED_RECORDING_PREPARATION_STATE
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "recording preparation lineage mismatch"
            )

        if (
            record["recommendation"]
            != CURRENT_RECOMMENDATION
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session gate recommendation mismatch"
            )

        if (
            record["gate_state"]
            != GATE_STATE
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session gate state mismatch"
            )

        session_contract = record[
            "owner_session_contract_board"
        ]

        forbidden_true_session_fields = (
            "session_created",
            "session_started",
            "session_issued",
            "session_activated",
        )

        invalid_session_fields = [
            field
            for field in forbidden_true_session_fields
            if session_contract[field] is True
        ]

        if invalid_session_fields:
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session contract contains active session state: "
                + ", ".join(
                    invalid_session_fields
                )
            )

        if (
            session_contract["session_reference"]
            is not None
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session reference exists"
            )

        authority_board = record[
            "tower_session_authority_board"
        ]

        if (
            authority_board["vault_may_create_owner_session"]
            is not False
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "Vault was granted owner-session creation authority"
            )

        if (
            authority_board["vault_may_start_owner_session"]
            is not False
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "Vault was granted owner-session start authority"
            )

        if (
            authority_board["tower_owner_session_created"]
            is not False
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "Tower owner session was created"
            )

        if (
            authority_board["tower_owner_session_started"]
            is not False
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "Tower owner session was started"
            )

        matrix = record[
            "session_prerequisite_matrix"
        ]

        if (
            matrix["all_owner_session_prerequisites_satisfied"]
            is not False
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session prerequisites were incorrectly satisfied"
            )

        if (
            matrix["recording_gate_may_open"]
            is not False
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "recording gate may-open state was incorrectly granted"
            )

        blocker_board = record[
            "session_blocker_board"
        ]

        if (
            blocker_board["owner_session_gate_blocked"]
            is not True
        ):
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session blocker is inactive"
            )

        safety_state = blocker_board[
            "safety_state"
        ]

        missing_safety_fields = sorted(
            set(
                SAFETY_STATE_FIELDS
            )
            - set(
                safety_state
            )
        )

        if missing_safety_fields:
            raise OwnerSessionRequirementGateIntegrityError(
                "missing owner session safety fields: "
                + ", ".join(
                    missing_safety_fields
                )
            )

        unsafe_true = sorted(
            field
            for field, value in safety_state.items()
            if value is True
        )

        if unsafe_true:
            raise OwnerSessionRequirementGateIntegrityError(
                "unsafe completed owner-session actions: "
                + ", ".join(
                    unsafe_true
                )
            )

        checkpoint = record[
            "checkpoint"
        ]

        forbidden_true_checkpoint_fields = (
            "owner_session_created",
            "owner_session_started",
            "owner_session_issued",
            "owner_session_activated",
            "tower_owner_session_created",
            "tower_owner_session_started",
            "session_binding_receipt_present",
            "session_expiry_verified",
            "session_replay_protection_verified",
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
            "recovery_authorization_granted",
            "authorization_token_issued",
            "handoff_delivered",
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
            "raw_material_exposed",
            "destructive_action_occurred",
        )

        invalid_checkpoint_fields = [
            field
            for field in forbidden_true_checkpoint_fields
            if checkpoint[field] is True
        ]

        if invalid_checkpoint_fields:
            raise OwnerSessionRequirementGateIntegrityError(
                "unsafe GP720 checkpoint state: "
                + ", ".join(
                    invalid_checkpoint_fields
                )
            )

        events = self.list_events(
            gate_id
        )

        if not events:
            raise OwnerSessionRequirementGateIntegrityError(
                "owner session gate has no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if (
                event["previous_event_hash"]
                != previous_event_hash
            ):
                raise OwnerSessionRequirementGateIntegrityError(
                    "owner session event predecessor mismatch"
                )

            material = {
                "gate_id": (
                    event["gate_id"]
                ),
                "event_type": (
                    event["event_type"]
                ),
                "event_payload": (
                    event["event_payload"]
                ),
                "previous_event_hash": (
                    event["previous_event_hash"]
                ),
                "created_at": (
                    event["created_at"]
                ),
            }

            expected_event_hash = _sha256_text(
                _canonical_json(
                    material
                )
            )

            if (
                expected_event_hash
                != event["event_hash"]
            ):
                raise OwnerSessionRequirementGateIntegrityError(
                    "owner session event hash mismatch"
                )

            previous_event_hash = (
                event["event_hash"]
            )

        return {
            "pack_range": "GP711-GP720",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "recording_preparation_closed_lineage": True,

            "gate_sealed": True,
            "owner_session_required": True,

            "owner_session_created": False,
            "owner_session_started": False,
            "owner_session_issued": False,
            "owner_session_activated": False,

            "tower_owner_session_created": False,
            "tower_owner_session_started": False,

            "session_binding_receipt_present": False,
            "session_expiry_verified": False,
            "session_replay_protection_verified": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,

            "recording_gate_open": False,

            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

            "owner_decision_recommended": False,
            "owner_decision_defaulted": False,
            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,

            "go_decision_granted": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,

            "handoff_delivered": False,
            "tower_delivery_session_started": False,

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

            "unsafe_completed_actions": [],
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "verified": True,
        }

    def _normalize_operations(
        self,
        requested_operations: Sequence[str] | None,
    ) -> list[str]:
        if requested_operations is None:
            return sorted(
                ALLOWED_GATE_OPERATIONS
            )

        if isinstance(
            requested_operations,
            (
                str,
                bytes,
            ),
        ):
            raise OwnerSessionRequirementGateError(
                "requested_operations must be a sequence"
            )

        operations: list[str] = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise OwnerSessionRequirementGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_GATE_OPERATIONS:
                raise OwnerSessionRequirementGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(
                normalized
            )

        if not operations:
            raise OwnerSessionRequirementGateError(
                "requested_operations cannot be empty"
            )

        return sorted(
            set(
                operations
            )
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
            FROM vault_gp711_720_owner_session_requirement_gate_events
            WHERE gate_id = ?
            ORDER BY event_id DESC
            LIMIT 1
            """,
            (
                gate_id,
            ),
        ).fetchone()

        previous_event_hash = (
            predecessor["event_hash"]
            if predecessor
            else None
        )

        created_at = _utc_now()

        normalized_payload = json.loads(
            _canonical_json(
                dict(
                    event_payload
                )
            )
        )

        material = {
            "gate_id": (
                gate_id
            ),
            "event_type": (
                event_type
            ),
            "event_payload": (
                normalized_payload
            ),
            "previous_event_hash": (
                previous_event_hash
            ),
            "created_at": (
                created_at
            ),
        }

        event_hash = _sha256_text(
            _canonical_json(
                material
            )
        )

        connection.execute(
            """
            INSERT INTO
                vault_gp711_720_owner_session_requirement_gate_events (
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
                _canonical_json(
                    normalized_payload
                ),
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
    ) -> OwnerSessionRequirementGateReceipt:
        return OwnerSessionRequirementGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            owner_session_required=True,
            owner_session_created=False,
            owner_session_started=False,
            tower_owner_session_created=False,
            tower_owner_session_started=False,
            recording_gate_open=False,
            owner_decision_recorded=False,

            immutable=True,
            append_only=True,
            idempotent_replay=(
                idempotent_replay
            ),
        )


__all__ = [
    "ALLOWED_GATE_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "GATE_STATE",
    "OwnerSessionRequirementGateError",
    "OwnerSessionRequirementGateIntegrityError",
    "OwnerSessionRequirementGateReceipt",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_RECORDING_PREPARATION_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionRequirementGateService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
