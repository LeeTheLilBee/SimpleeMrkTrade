"""Archive Vault GP701-GP710.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Preparation Layer.

This layer prepares reference-only evidence for a future Tower-controlled
owner decision recording flow.

The GP691-GP700 recording gate remains sealed and closed.

Doctrine:
    Tower is the face and protocol authority.
    Vault is sealed memory.
    Teller is the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller

Prior recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED

Current recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_PREPARED

This service never:
    * opens the owner decision recording gate
    * creates or starts an owner session
    * authenticates an owner
    * performs owner step-up
    * invents an owner decision
    * recommends an owner decision
    * defaults an owner decision
    * selects an owner decision
    * records an owner decision
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
    * exposes raw material, paths, URLs, credentials, or tokens
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


PACK_START = 701
PACK_END = 710

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_GATE_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_PREPARED"
)

PREPARATION_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_"
    "PREPARED_GATE_REMAINS_CLOSED"
)

REQUIRED_RECORDING_GATE_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_GATE_"
    "SEALED_CLOSED"
)

TOWER_DESTINATION = "TOWER"

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_PREPARATION_OPERATIONS = frozenset(
    {
        "INTAKE_RECORDING_GATE_REFERENCE",
        "VERIFY_RECORDING_GATE_CLOSED",
        "ASSEMBLE_OWNER_SESSION_REQUIREMENT_REFERENCES",
        "ASSEMBLE_OWNER_IDENTITY_REQUIREMENT_REFERENCES",
        "ASSEMBLE_OWNER_STEP_UP_REQUIREMENT_REFERENCES",
        "ASSEMBLE_DUAL_RECEIPT_REQUIREMENT_REFERENCES",
        "ASSEMBLE_SECOND_AUTHORITY_REQUIREMENT_REFERENCES",
        "FREEZE_RECORDING_PREPARATION_ENVELOPE",
        "DRAFT_RECORDING_PREPARATION_RECEIPT",
        "SEAL_RECORDING_PREPARATION_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "CREATE_OWNER_SESSION",
        "START_OWNER_SESSION",
        "CREATE_TOWER_OWNER_SESSION",
        "START_TOWER_OWNER_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
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
    }
)

SAFETY_STATE_FIELDS = (
    "owner_decision_recording_gate_opened",
    "owner_session_created",
    "owner_session_started",
    "tower_owner_session_created",
    "tower_owner_session_started",
    "owner_authenticated",
    "owner_stepped_up",
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


class DecisionRecordingPreparationError(ValueError):
    """Raised when GP701-GP710 input violates preparation boundaries."""


class DecisionRecordingPreparationIntegrityError(RuntimeError):
    """Raised when sealed GP701-GP710 evidence fails verification."""


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
        raise DecisionRecordingPreparationError(
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

            nested_location = (
                f"{location}.{key_text}"
            )

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
        raise DecisionRecordingPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(
                dict(value)
            )
        )
    except (TypeError, ValueError) as exc:
        raise DecisionRecordingPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise DecisionRecordingPreparationError(
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
        raise DecisionRecordingPreparationError(
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
class DecisionRecordingPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    preparation_state: str

    recording_prepared: bool
    recording_gate_open: bool
    owner_session_created: bool
    owner_session_started: bool
    owner_decision_selected: bool
    owner_decision_recorded: bool
    authorization_granted: bool
    authorization_token_issued: bool

    immutable: bool
    append_only: bool
    idempotent_replay: bool

    def as_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "preparation_id": self.preparation_id,
            "preparation_hash": self.preparation_hash,
            "recommendation": self.recommendation,
            "preparation_state": self.preparation_state,
            "recording_prepared": self.recording_prepared,
            "recording_gate_open": self.recording_gate_open,
            "owner_session_created": self.owner_session_created,
            "owner_session_started": self.owner_session_started,
            "owner_decision_selected": self.owner_decision_selected,
            "owner_decision_recorded": self.owner_decision_recorded,
            "authorization_granted": self.authorization_granted,
            "authorization_token_issued": (
                self.authorization_token_issued
            ),
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": self.idempotent_replay,
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingPreparationService:
    """Persistent GP701-GP710 recording preparation service."""

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
                vault_gp701_710_authorization_decision_recording_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    recording_gate_id TEXT NOT NULL,
                    recording_gate_hash TEXT NOT NULL,
                    recording_gate_state TEXT NOT NULL
                        CHECK(
                            recording_gate_state =
                            'AUTHORIZATION_DECISION_RECORDING_GATE_SEALED_CLOSED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    preparation_shell_json TEXT NOT NULL,
                    recording_gate_lineage_json TEXT NOT NULL,
                    owner_session_requirement_board_json TEXT NOT NULL,
                    owner_identity_requirement_board_json TEXT NOT NULL,
                    owner_step_up_requirement_board_json TEXT NOT NULL,
                    dual_receipt_requirement_board_json TEXT NOT NULL,
                    second_authority_requirement_board_json TEXT NOT NULL,
                    recording_preparation_envelope_json TEXT NOT NULL,
                    recording_preparation_receipt_draft_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    preparation_payload_json TEXT NOT NULL,
                    preparation_hash TEXT NOT NULL UNIQUE,
                    predecessor_preparation_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_PREPARED'
                        ),

                    preparation_state TEXT NOT NULL
                        CHECK(
                            preparation_state =
                            'AUTHORIZATION_DECISION_RECORDING_PREPARED_GATE_REMAINS_CLOSED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp701_710_authorization_decision_recording_preparation_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES
                        vault_gp701_710_authorization_decision_recording_preparations(
                            preparation_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp701_710_recovery_case
                ON vault_gp701_710_authorization_decision_recording_preparations(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp701_710_recording_gate
                ON vault_gp701_710_authorization_decision_recording_preparations(
                    recording_gate_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp701_710_event_chain
                ON vault_gp701_710_authorization_decision_recording_preparation_events(
                    preparation_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp701_710_preparation_no_update
                BEFORE UPDATE
                ON vault_gp701_710_authorization_decision_recording_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP701-GP710 recording preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp701_710_preparation_no_delete
                BEFORE DELETE
                ON vault_gp701_710_authorization_decision_recording_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP701-GP710 recording preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp701_710_event_no_update
                BEFORE UPDATE
                ON vault_gp701_710_authorization_decision_recording_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP701-GP710 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp701_710_event_no_delete
                BEFORE DELETE
                ON vault_gp701_710_authorization_decision_recording_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP701-GP710 events are append-only'
                    );
                END;
                """
            )

    def prepare_decision_recording(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        recording_gate_id: str,
        recording_gate_hash: str,
        recording_gate_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> DecisionRecordingPreparationReceipt:
        """Prepare recording evidence while preserving the closed gate."""

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

        recording_gate_id = _required_text(
            "recording_gate_id",
            recording_gate_id,
        )

        recording_gate_hash = _required_text(
            "recording_gate_hash",
            recording_gate_hash,
        )

        recording_gate_state = _required_text(
            "recording_gate_state",
            recording_gate_state,
        ).upper()

        if (
            recording_gate_state
            != REQUIRED_RECORDING_GATE_STATE
        ):
            raise DecisionRecordingPreparationError(
                "recording_gate_state must preserve "
                "AUTHORIZATION_DECISION_RECORDING_GATE_SEALED_CLOSED"
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
            "recording_gate_id": (
                recording_gate_id
            ),
            "recording_gate_hash": (
                recording_gate_hash
            ),
            "recording_gate_state": (
                recording_gate_state
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

        preparation_id = (
            "vault-gp701-710-"
            + _sha256_text(
                _canonical_json(
                    identity
                )
            )[:24]
        )

        # GP701 — Decision Recording Preparation Shell
        preparation_shell = {
            "pack": "GP701",
            "preparation_id": preparation_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": (
                PRIOR_RECOMMENDATION
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "preparation_state": (
                PREPARATION_STATE
            ),
            "recording_prepared": True,
            "recording_gate_open": False,
            "owner_decision_recorded": False,
        }

        # GP702 — Recording Gate Lineage Intake Board
        recording_gate_lineage = {
            "pack": "GP702",
            "recording_gate_id": (
                recording_gate_id
            ),
            "recording_gate_hash": (
                recording_gate_hash
            ),
            "recording_gate_state": (
                recording_gate_state
            ),
            "required_recording_gate_state": (
                REQUIRED_RECORDING_GATE_STATE
            ),
            "recording_gate_reference_present": True,
            "recording_gate_hash_present": True,
            "recording_gate_open_in_lineage": False,
            "owner_decision_recorded_in_lineage": False,
            "authorization_granted_in_lineage": False,
        }

        # GP703 — Owner Session Requirement Board
        owner_session_requirement_board = {
            "pack": "GP703",
            "tower_owner_session_required_for_future_recording": True,
            "owner_session_created": False,
            "owner_session_started": False,
            "tower_owner_session_created": False,
            "tower_owner_session_started": False,
            "owner_session_created_by_this_layer": False,
            "owner_session_started_by_this_layer": False,
            "recording_gate_open_without_owner_session": False,
            "recording_blocked_without_owner_session": True,
        }

        # GP704 — Owner Identity Requirement Board
        owner_identity_requirement_board = {
            "pack": "GP704",
            "owner_decision_record_id": (
                owner_decision_record_id
            ),
            "owner_identity_required_for_future_recording": True,
            "owner_authenticated": False,
            "owner_identity_verified_by_this_layer": False,
            "recording_gate_open_without_owner_identity": False,
            "recording_blocked_without_owner_identity": True,
        }

        # GP705 — Owner Step-Up Requirement Board
        owner_step_up_requirement_board = {
            "pack": "GP705",
            "owner_step_up_required_for_future_recording": True,
            "owner_stepped_up": False,
            "step_up_performed_by_this_layer": False,
            "recording_gate_open_without_owner_step_up": False,
            "recording_blocked_without_owner_step_up": True,
        }

        # GP706 — Dual Receipt Requirement Board
        dual_receipt_requirement_board = {
            "pack": "GP706",
            "dual_receipt_required_for_future_recording": True,
            "dual_receipt_satisfied": False,
            "dual_receipt_satisfied_by_this_layer": False,
            "recording_gate_open_without_dual_receipt": False,
            "recording_blocked_without_dual_receipt": True,
        }

        # GP707 — Second Authority Requirement Board
        second_authority_requirement_board = {
            "pack": "GP707",
            "second_authority_required_for_future_recording": True,
            "second_authority_review_granted": False,
            "second_authority_granted_by_this_layer": False,
            "recording_gate_open_without_second_authority": False,
            "recording_blocked_without_second_authority": True,
        }

        # GP708 — Recording Preparation Envelope Freeze Board
        recording_preparation_envelope = {
            "pack": "GP708",
            "envelope_type": (
                "TOWER_OWNER_DECISION_RECORDING_PREPARATION_ENVELOPE"
            ),
            "envelope_version": 1,
            "preparation_id": preparation_id,
            "recording_gate_id": (
                recording_gate_id
            ),
            "recording_gate_hash": (
                recording_gate_hash
            ),
            "recording_gate_state": (
                recording_gate_state
            ),
            "owner_decision_record_id": (
                owner_decision_record_id
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
            "destination": (
                TOWER_DESTINATION
            ),
            "safe_metadata": (
                metadata
            ),
            "requested_operations": (
                operations
            ),
            "owner_session_reference": None,
            "owner_authentication_reference": None,
            "owner_step_up_reference": None,
            "dual_receipt_reference": None,
            "second_authority_reference": None,
            "owner_decision_value": None,
            "owner_decision_recommended": False,
            "owner_decision_defaulted": False,
            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,
            "recording_gate_open": False,
            "frozen_for_preparation": True,
        }

        recording_preparation_envelope[
            "envelope_hash"
        ] = _sha256_text(
            _canonical_json(
                recording_preparation_envelope
            )
        )

        # GP709 — Recording Preparation Receipt Draft Ledger
        recording_preparation_receipt_draft = {
            "pack": "GP709",
            "receipt_type": (
                "TOWER_OWNER_DECISION_RECORDING_PREPARATION_RECEIPT_DRAFT"
            ),
            "receipt_status": (
                "DRAFT_RECORDING_PREPARED_GATE_CLOSED"
            ),
            "preparation_id": (
                preparation_id
            ),
            "recording_gate_open_event_id": None,
            "owner_session_event_id": None,
            "owner_authentication_event_id": None,
            "owner_step_up_event_id": None,
            "owner_decision_event_id": None,
            "owner_decision_value": None,
            "authorization_event_id": None,
            "authorization_token_reference": None,
            "go_decision_reference": None,
            "receipt_finalized": False,
        }

        recording_preparation_receipt_draft[
            "receipt_draft_hash"
        ] = _sha256_text(
            _canonical_json(
                recording_preparation_receipt_draft
            )
        )

        # GP710 — Decision Recording Preparation Readiness Checkpoint
        safety_state = _false_safety_state()

        checkpoint = {
            "pack": "GP710",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                "DECISION_RECORDING_PREPARATION_READINESS"
            ),
            "preparation_id": (
                preparation_id
            ),
            "prior_pack_range": (
                "GP691-GP700"
            ),
            "current_pack_range": (
                "GP701-GP710"
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "preparation_state": (
                PREPARATION_STATE
            ),

            "recording_prepared": True,
            "recording_gate_open": False,

            "owner_session_created": False,
            "owner_session_started": False,
            "tower_owner_session_created": False,
            "tower_owner_session_started": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,
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

            "safety_state": (
                safety_state
            ),

            "next_gate": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                "DECISION_RECORDING_OWNER_SESSION_REQUIREMENT_GATE"
            ),
        }

        preparation_payload = {
            "gp701_preparation_shell": (
                preparation_shell
            ),
            "gp702_recording_gate_lineage": (
                recording_gate_lineage
            ),
            "gp703_owner_session_requirement_board": (
                owner_session_requirement_board
            ),
            "gp704_owner_identity_requirement_board": (
                owner_identity_requirement_board
            ),
            "gp705_owner_step_up_requirement_board": (
                owner_step_up_requirement_board
            ),
            "gp706_dual_receipt_requirement_board": (
                dual_receipt_requirement_board
            ),
            "gp707_second_authority_requirement_board": (
                second_authority_requirement_board
            ),
            "gp708_recording_preparation_envelope": (
                recording_preparation_envelope
            ),
            "gp709_recording_preparation_receipt_draft": (
                recording_preparation_receipt_draft
            ),
            "gp710_checkpoint": (
                checkpoint
            ),
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
                FROM vault_gp701_710_authorization_decision_recording_preparations
                WHERE idempotency_key = ?
                """,
                (
                    idempotency_key,
                ),
            ).fetchone()

            if existing is not None:
                if (
                    existing["preparation_payload_json"]
                    != preparation_payload_json
                    or existing["preparation_hash"]
                    != preparation_hash
                ):
                    raise DecisionRecordingPreparationError(
                        "idempotency_key already exists with "
                        "different immutable recording-preparation inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp701_710_authorization_decision_recording_preparations
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
                    vault_gp701_710_authorization_decision_recording_preparations (
                        preparation_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        recording_gate_id,
                        recording_gate_hash,
                        recording_gate_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        preparation_shell_json,
                        recording_gate_lineage_json,
                        owner_session_requirement_board_json,
                        owner_identity_requirement_board_json,
                        owner_step_up_requirement_board_json,
                        dual_receipt_requirement_board_json,
                        second_authority_requirement_board_json,
                        recording_preparation_envelope_json,
                        recording_preparation_receipt_draft_json,
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
                    recording_gate_id,
                    recording_gate_hash,
                    recording_gate_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(
                        preparation_shell
                    ),
                    _canonical_json(
                        recording_gate_lineage
                    ),
                    _canonical_json(
                        owner_session_requirement_board
                    ),
                    _canonical_json(
                        owner_identity_requirement_board
                    ),
                    _canonical_json(
                        owner_step_up_requirement_board
                    ),
                    _canonical_json(
                        dual_receipt_requirement_board
                    ),
                    _canonical_json(
                        second_authority_requirement_board
                    ),
                    _canonical_json(
                        recording_preparation_envelope
                    ),
                    _canonical_json(
                        recording_preparation_receipt_draft
                    ),
                    _canonical_json(
                        checkpoint
                    ),
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
                    "GP701_710_TOWER_HANDOFF_DELIVERY_"
                    "AUTHORIZATION_DECISION_RECORDING_PREPARATION_SEALED"
                ),
                event_payload={
                    "preparation_hash": (
                        preparation_hash
                    ),
                    "recommendation": (
                        CURRENT_RECOMMENDATION
                    ),
                    "preparation_state": (
                        PREPARATION_STATE
                    ),
                    "recording_prepared": True,
                    "recording_gate_open": False,
                    "owner_session_created": False,
                    "owner_session_started": False,
                    "owner_authenticated": False,
                    "owner_stepped_up": False,
                    "owner_decision_selected": False,
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
                FROM vault_gp701_710_authorization_decision_recording_preparations
                WHERE preparation_id = ?
                """,
                (
                    preparation_id,
                ),
            ).fetchone()

            if row is None:
                raise DecisionRecordingPreparationIntegrityError(
                    "decision recording preparation failed to persist"
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
                FROM vault_gp701_710_authorization_decision_recording_preparations
                WHERE preparation_id = ?
                """,
                (
                    preparation_id,
                ),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP701-GP710 preparation: {preparation_id}"
            )

        result = dict(
            row
        )

        json_columns = (
            "preparation_shell_json",
            "recording_gate_lineage_json",
            "owner_session_requirement_board_json",
            "owner_identity_requirement_board_json",
            "owner_step_up_requirement_board_json",
            "dual_receipt_requirement_board_json",
            "second_authority_requirement_board_json",
            "recording_preparation_envelope_json",
            "recording_preparation_receipt_draft_json",
            "checkpoint_json",
            "preparation_payload_json",
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
                FROM vault_gp701_710_authorization_decision_recording_preparation_events
                WHERE preparation_id = ?
                ORDER BY event_id ASC
                """,
                (
                    preparation_id,
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

    def verify_preparation(
        self,
        preparation_id: str,
    ) -> dict[str, Any]:
        record = self.get_preparation(
            preparation_id
        )

        payload_json = _canonical_json(
            record[
                "preparation_payload"
            ]
        )

        expected_preparation_hash = _sha256_text(
            payload_json
        )

        if (
            expected_preparation_hash
            != record["preparation_hash"]
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation payload hash mismatch"
            )

        if (
            record["destination"]
            != TOWER_DESTINATION
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation destination is not Tower"
            )

        if (
            record["recording_gate_state"]
            != REQUIRED_RECORDING_GATE_STATE
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording gate closed-state lineage mismatch"
            )

        if (
            record["recommendation"]
            != CURRENT_RECOMMENDATION
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation recommendation mismatch"
            )

        if (
            record["preparation_state"]
            != PREPARATION_STATE
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation state mismatch"
            )

        lineage = record[
            "recording_gate_lineage"
        ]

        if (
            lineage[
                "recording_gate_open_in_lineage"
            ]
            is not False
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording gate was open in lineage"
            )

        if (
            lineage[
                "owner_decision_recorded_in_lineage"
            ]
            is not False
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "owner decision was recorded in lineage"
            )

        session_board = record[
            "owner_session_requirement_board"
        ]

        forbidden_session_true = (
            "owner_session_created",
            "owner_session_started",
            "tower_owner_session_created",
            "tower_owner_session_started",
            "owner_session_created_by_this_layer",
            "owner_session_started_by_this_layer",
            "recording_gate_open_without_owner_session",
        )

        invalid_session_fields = [
            field
            for field in forbidden_session_true
            if session_board[field] is True
        ]

        if invalid_session_fields:
            raise DecisionRecordingPreparationIntegrityError(
                "unsafe owner-session preparation state: "
                + ", ".join(
                    invalid_session_fields
                )
            )

        envelope = record[
            "recording_preparation_envelope"
        ]

        forbidden_non_null_envelope_fields = (
            "owner_session_reference",
            "owner_authentication_reference",
            "owner_step_up_reference",
            "dual_receipt_reference",
            "second_authority_reference",
            "owner_decision_value",
        )

        invalid_non_null_fields = [
            field
            for field in forbidden_non_null_envelope_fields
            if envelope[field] is not None
        ]

        if invalid_non_null_fields:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation envelope contains active evidence: "
                + ", ".join(
                    invalid_non_null_fields
                )
            )

        forbidden_true_envelope_fields = (
            "owner_decision_recommended",
            "owner_decision_defaulted",
            "owner_decision_selected",
            "owner_decision_invented",
            "owner_decision_recorded",
            "recording_gate_open",
        )

        invalid_true_envelope_fields = [
            field
            for field in forbidden_true_envelope_fields
            if envelope[field] is True
        ]

        if invalid_true_envelope_fields:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation envelope contains unsafe state: "
                + ", ".join(
                    invalid_true_envelope_fields
                )
            )

        receipt = record[
            "recording_preparation_receipt_draft"
        ]

        if (
            receipt["receipt_status"]
            != "DRAFT_RECORDING_PREPARED_GATE_CLOSED"
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation receipt escaped draft state"
            )

        forbidden_receipt_values = (
            "recording_gate_open_event_id",
            "owner_session_event_id",
            "owner_authentication_event_id",
            "owner_step_up_event_id",
            "owner_decision_event_id",
            "owner_decision_value",
            "authorization_event_id",
            "authorization_token_reference",
            "go_decision_reference",
        )

        invalid_receipt_values = [
            field
            for field in forbidden_receipt_values
            if receipt[field] is not None
        ]

        if invalid_receipt_values:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation receipt contains operational evidence: "
                + ", ".join(
                    invalid_receipt_values
                )
            )

        if (
            receipt["receipt_finalized"]
            is not False
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation receipt was finalized"
            )

        checkpoint = record[
            "checkpoint"
        ]

        if (
            checkpoint[
                "recording_prepared"
            ]
            is not True
        ):
            raise DecisionRecordingPreparationIntegrityError(
                "GP710 checkpoint is not prepared"
            )

        safety_state = checkpoint[
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
            raise DecisionRecordingPreparationIntegrityError(
                "missing recording preparation safety fields: "
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
            raise DecisionRecordingPreparationIntegrityError(
                "unsafe completed recording preparation actions: "
                + ", ".join(
                    unsafe_true
                )
            )

        forbidden_true_checkpoint_fields = (
            "recording_gate_open",
            "owner_session_created",
            "owner_session_started",
            "tower_owner_session_created",
            "tower_owner_session_started",
            "owner_authenticated",
            "owner_stepped_up",
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
            raise DecisionRecordingPreparationIntegrityError(
                "unsafe GP710 checkpoint state: "
                + ", ".join(
                    invalid_checkpoint_fields
                )
            )

        events = self.list_events(
            preparation_id
        )

        if not events:
            raise DecisionRecordingPreparationIntegrityError(
                "recording preparation has no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if (
                event["previous_event_hash"]
                != previous_event_hash
            ):
                raise DecisionRecordingPreparationIntegrityError(
                    "recording preparation event predecessor mismatch"
                )

            material = {
                "preparation_id": (
                    event["preparation_id"]
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
                raise DecisionRecordingPreparationIntegrityError(
                    "recording preparation event hash mismatch"
                )

            previous_event_hash = (
                event["event_hash"]
            )

        return {
            "pack_range": "GP701-GP710",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "recording_gate_closed_lineage": True,

            "recording_prepared": True,
            "recording_gate_open": False,

            "owner_session_created": False,
            "owner_session_started": False,
            "tower_owner_session_created": False,
            "tower_owner_session_started": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,
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
                ALLOWED_PREPARATION_OPERATIONS
            )

        if isinstance(
            requested_operations,
            (
                str,
                bytes,
            ),
        ):
            raise DecisionRecordingPreparationError(
                "requested_operations must be a sequence"
            )

        operations: list[str] = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise DecisionRecordingPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if (
                normalized
                not in ALLOWED_PREPARATION_OPERATIONS
            ):
                raise DecisionRecordingPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(
                normalized
            )

        if not operations:
            raise DecisionRecordingPreparationError(
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
        preparation_id: str,
        event_type: str,
        event_payload: Mapping[str, Any],
    ) -> str:
        predecessor = connection.execute(
            """
            SELECT event_hash
            FROM vault_gp701_710_authorization_decision_recording_preparation_events
            WHERE preparation_id = ?
            ORDER BY event_id DESC
            LIMIT 1
            """,
            (
                preparation_id,
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
            "preparation_id": (
                preparation_id
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
                vault_gp701_710_authorization_decision_recording_preparation_events (
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
    ) -> DecisionRecordingPreparationReceipt:
        return DecisionRecordingPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            preparation_state=row["preparation_state"],

            recording_prepared=True,
            recording_gate_open=False,
            owner_session_created=False,
            owner_session_started=False,
            owner_decision_selected=False,
            owner_decision_recorded=False,
            authorization_granted=False,
            authorization_token_issued=False,

            immutable=True,
            append_only=True,
            idempotent_replay=(
                idempotent_replay
            ),
        )


__all__ = [
    "ALLOWED_PREPARATION_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "DecisionRecordingPreparationError",
    "DecisionRecordingPreparationIntegrityError",
    "DecisionRecordingPreparationReceipt",
    "PACK_END",
    "PACK_START",
    "PREPARATION_STATE",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_RECORDING_GATE_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingPreparationService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
