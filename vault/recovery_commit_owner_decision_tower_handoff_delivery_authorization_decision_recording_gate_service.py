"""Archive Vault GP691-GP700.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Gate.

This layer seals a fail-closed gate around any future recording of an owner
authorization decision.

The gate remains closed.

Doctrine:
    Tower is the face and protocol authority.
    Vault is sealed memory.
    Teller is the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller

Prior recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_PREPARED

Current recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED

This service never:
    * invents an owner decision
    * selects an owner decision
    * records an owner decision
    * opens the decision recording gate
    * authenticates an owner
    * performs owner step-up
    * grants owner or administrator approval
    * satisfies a dual receipt
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


PACK_START = 691
PACK_END = 700

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_PREPARED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_GATE_SEALED"
)

GATE_STATE = (
    "AUTHORIZATION_DECISION_RECORDING_GATE_"
    "SEALED_CLOSED"
)

TOWER_DESTINATION = "TOWER"

REQUIRED_DECISION_PREPARATION_STATE = (
    "AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED"
)

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_GATE_OPERATIONS = frozenset(
    {
        "INTAKE_DECISION_PREPARATION_REFERENCE",
        "VERIFY_DECISION_PACKET_PREPARED",
        "VERIFY_NO_OWNER_DECISION_SELECTED",
        "VERIFY_NO_OWNER_DECISION_RECORDED",
        "VERIFY_OWNER_AUTHENTICATION_REQUIREMENT",
        "VERIFY_OWNER_STEP_UP_REQUIREMENT",
        "VERIFY_DUAL_RECEIPT_REQUIREMENT",
        "VERIFY_SECOND_AUTHORITY_REQUIREMENT",
        "EVALUATE_RECORDING_GATE_BLOCKERS",
        "SEAL_DECISION_RECORDING_GATE_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
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
    }
)

SAFETY_STATE_FIELDS = (
    "owner_decision_selected",
    "owner_decision_invented",
    "owner_decision_recorded",
    "owner_decision_recording_gate_opened",
    "owner_authenticated",
    "owner_stepped_up",
    "owner_admin_approval_granted",
    "dual_receipt_satisfied",
    "second_authority_review_granted",
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


class DecisionRecordingGateError(ValueError):
    """Raised when GP691-GP700 input violates the closed gate."""


class DecisionRecordingGateIntegrityError(RuntimeError):
    """Raised when sealed GP691-GP700 evidence fails verification."""


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
        raise DecisionRecordingGateError(
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
        raise DecisionRecordingGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(
                dict(value)
            )
        )
    except (TypeError, ValueError) as exc:
        raise DecisionRecordingGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise DecisionRecordingGateError(
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
        raise DecisionRecordingGateError(
            "safe_metadata contains prohibited raw, path, URL, token, "
            "secret, credential, or authorization fields: "
            + ", ".join(blocked)
        )

    return normalized


def _false_safety_state() -> dict[str, bool]:
    return {
        field: False
        for field in SAFETY_STATE_FIELDS
    }


@dataclass(frozen=True)
class DecisionRecordingGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    gate_open: bool
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
            "gate_id": self.gate_id,
            "gate_hash": self.gate_hash,
            "recommendation": self.recommendation,
            "gate_state": self.gate_state,
            "gate_sealed": self.gate_sealed,
            "gate_open": self.gate_open,
            "owner_decision_selected": (
                self.owner_decision_selected
            ),
            "owner_decision_recorded": (
                self.owner_decision_recorded
            ),
            "authorization_granted": (
                self.authorization_granted
            ),
            "authorization_token_issued": (
                self.authorization_token_issued
            ),
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": (
                self.idempotent_replay
            ),
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingGateService:
    """Persistent GP691-GP700 fail-closed decision recording gate."""

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
                vault_gp691_700_authorization_decision_recording_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    decision_preparation_id TEXT NOT NULL,
                    decision_preparation_hash TEXT NOT NULL,
                    decision_preparation_state TEXT NOT NULL
                        CHECK(
                            decision_preparation_state =
                            'AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    recording_gate_shell_json TEXT NOT NULL,
                    preparation_lineage_gate_json TEXT NOT NULL,
                    owner_identity_requirement_gate_json TEXT NOT NULL,
                    owner_step_up_requirement_gate_json TEXT NOT NULL,
                    dual_receipt_requirement_gate_json TEXT NOT NULL,
                    second_authority_requirement_gate_json TEXT NOT NULL,
                    recording_prerequisite_matrix_json TEXT NOT NULL,
                    recording_blocker_board_json TEXT NOT NULL,
                    recording_receipt_draft_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    gate_payload_json TEXT NOT NULL,
                    gate_hash TEXT NOT NULL UNIQUE,
                    predecessor_gate_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'AUTHORIZATION_DECISION_RECORDING_GATE_SEALED_CLOSED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp691_700_authorization_decision_recording_gate_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES
                        vault_gp691_700_authorization_decision_recording_gates(
                            gate_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp691_700_recovery_case
                ON vault_gp691_700_authorization_decision_recording_gates(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp691_700_decision_preparation
                ON vault_gp691_700_authorization_decision_recording_gates(
                    decision_preparation_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp691_700_event_chain
                ON vault_gp691_700_authorization_decision_recording_gate_events(
                    gate_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp691_700_gate_no_update
                BEFORE UPDATE
                ON vault_gp691_700_authorization_decision_recording_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP691-GP700 decision recording gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp691_700_gate_no_delete
                BEFORE DELETE
                ON vault_gp691_700_authorization_decision_recording_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP691-GP700 decision recording gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp691_700_event_no_update
                BEFORE UPDATE
                ON vault_gp691_700_authorization_decision_recording_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP691-GP700 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp691_700_event_no_delete
                BEFORE DELETE
                ON vault_gp691_700_authorization_decision_recording_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP691-GP700 events are append-only'
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
    ) -> DecisionRecordingGateReceipt:
        """Seal the recording gate in a closed state."""

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

        if (
            decision_preparation_state
            != REQUIRED_DECISION_PREPARATION_STATE
        ):
            raise DecisionRecordingGateError(
                "decision_preparation_state must preserve "
                "AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED"
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
            raise DecisionRecordingGateError(
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
            "decision_preparation_id": (
                decision_preparation_id
            ),
            "decision_preparation_hash": (
                decision_preparation_hash
            ),
            "decision_preparation_state": (
                decision_preparation_state
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
            "vault-gp691-700-"
            + _sha256_text(
                _canonical_json(
                    identity
                )
            )[:24]
        )

        # GP691 — Authorization Decision Recording Gate Shell
        recording_gate_shell = {
            "pack": "GP691",
            "gate_id": gate_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": (
                PRIOR_RECOMMENDATION
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "gate_state": (
                GATE_STATE
            ),
            "gate_sealed": True,
            "gate_open": False,
            "owner_decision_recorded": False,
        }

        # GP692 — Decision Preparation Lineage Gate
        preparation_lineage_gate = {
            "pack": "GP692",
            "decision_preparation_id": (
                decision_preparation_id
            ),
            "decision_preparation_hash": (
                decision_preparation_hash
            ),
            "decision_preparation_state": (
                decision_preparation_state
            ),
            "required_state": (
                REQUIRED_DECISION_PREPARATION_STATE
            ),
            "decision_packet_reference_present": True,
            "decision_packet_hash_present": True,
            "owner_decision_selected_in_lineage": False,
            "owner_decision_recorded_in_lineage": False,
            "authorization_granted_in_lineage": False,
        }

        # GP693 — Owner Identity Recording Requirement Gate
        owner_identity_requirement_gate = {
            "pack": "GP693",
            "owner_identity_required_for_future_recording": True,
            "owner_decision_record_id": (
                owner_decision_record_id
            ),
            "owner_authenticated": False,
            "owner_identity_verified_by_this_layer": False,
            "recording_gate_open_without_identity": False,
            "recording_blocked_without_owner_identity": True,
        }

        # GP694 — Owner Step-Up Recording Requirement Gate
        owner_step_up_requirement_gate = {
            "pack": "GP694",
            "owner_step_up_required_for_future_recording": True,
            "owner_stepped_up": False,
            "step_up_performed_by_this_layer": False,
            "recording_gate_open_without_step_up": False,
            "recording_blocked_without_step_up": True,
        }

        # GP695 — Dual Receipt Recording Requirement Gate
        dual_receipt_requirement_gate = {
            "pack": "GP695",
            "dual_receipt_required_for_future_recording": True,
            "dual_receipt_satisfied": False,
            "dual_receipt_satisfied_by_this_layer": False,
            "recording_gate_open_without_dual_receipt": False,
            "recording_blocked_without_dual_receipt": True,
        }

        # GP696 — Second Authority Recording Requirement Gate
        second_authority_requirement_gate = {
            "pack": "GP696",
            "second_authority_required_for_future_recording": True,
            "second_authority_review_granted": False,
            "second_authority_granted_by_this_layer": False,
            "recording_gate_open_without_second_authority": False,
            "recording_blocked_without_second_authority": True,
        }

        # GP697 — Decision Recording Prerequisite Matrix
        recording_prerequisite_matrix = {
            "pack": "GP697",

            "decision_preparation_reference_present": True,
            "decision_preparation_hash_present": True,
            "tower_authority_reference_present": True,
            "owner_decision_reference_present": True,

            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

            "owner_decision_selected": False,
            "owner_decision_recorded": False,

            "all_recording_prerequisites_satisfied": False,
            "decision_recording_gate_open": False,
        }

        # GP698 — Decision Recording Safety Blocker Board
        safety_state = _false_safety_state()

        recording_blocker_board = {
            "pack": "GP698",
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "decision_recording_blocked": True,
            "authorization_blocked": True,
            "delivery_blocked": True,
            "safety_state": (
                safety_state
            ),
            "active_blockers": [
                "NO_OWNER_AUTHENTICATION",
                "NO_OWNER_STEP_UP",
                "NO_OWNER_ADMIN_APPROVAL",
                "NO_DUAL_RECEIPT_SATISFACTION",
                "NO_SECOND_AUTHORITY_REVIEW",
                "NO_SELECTED_OWNER_DECISION",
                "NO_OWNER_DECISION_RECORD",
                "RECORDING_GATE_CLOSED",
                "NO_GO_DECISION",
                "NO_RECOVERY_AUTHORIZATION",
                "NO_AUTHORIZATION_TOKEN",
                "NO_RECOVERY_COMMIT_COMMAND",
                "NO_PROVIDER_CONNECTION",
                "NO_PRODUCTION_STORAGE_WRITE",
            ],
        }

        # GP699 — Decision Recording Receipt Draft Ledger
        recording_receipt_draft = {
            "pack": "GP699",
            "receipt_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                "DECISION_RECORDING_RECEIPT_DRAFT"
            ),
            "receipt_status": (
                "DRAFT_RECORDING_GATE_CLOSED"
            ),
            "gate_id": (
                gate_id
            ),
            "recording_gate_open_event_id": None,
            "owner_decision_event_id": None,
            "owner_decision_value": None,
            "authorization_event_id": None,
            "authorization_token_reference": None,
            "go_decision_reference": None,
            "receipt_finalized": False,
        }

        recording_receipt_draft[
            "receipt_draft_hash"
        ] = _sha256_text(
            _canonical_json(
                recording_receipt_draft
            )
        )

        # GP700 — Decision Recording Gate Readiness Checkpoint
        checkpoint = {
            "pack": "GP700",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                "DECISION_RECORDING_GATE_READINESS"
            ),
            "gate_id": (
                gate_id
            ),
            "prior_pack_range": (
                "GP681-GP690"
            ),
            "current_pack_range": (
                "GP691-GP700"
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "gate_state": (
                GATE_STATE
            ),

            "gate_sealed": True,
            "gate_open": False,

            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,

            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

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
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                "DECISION_RECORDING_PREPARATION_LAYER"
            ),
        }

        gate_payload = {
            "gp691_recording_gate_shell": (
                recording_gate_shell
            ),
            "gp692_preparation_lineage_gate": (
                preparation_lineage_gate
            ),
            "gp693_owner_identity_requirement_gate": (
                owner_identity_requirement_gate
            ),
            "gp694_owner_step_up_requirement_gate": (
                owner_step_up_requirement_gate
            ),
            "gp695_dual_receipt_requirement_gate": (
                dual_receipt_requirement_gate
            ),
            "gp696_second_authority_requirement_gate": (
                second_authority_requirement_gate
            ),
            "gp697_recording_prerequisite_matrix": (
                recording_prerequisite_matrix
            ),
            "gp698_recording_blocker_board": (
                recording_blocker_board
            ),
            "gp699_recording_receipt_draft": (
                recording_receipt_draft
            ),
            "gp700_checkpoint": (
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
                FROM vault_gp691_700_authorization_decision_recording_gates
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
                    raise DecisionRecordingGateError(
                        "idempotency_key already exists with "
                        "different immutable decision-recording-gate inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp691_700_authorization_decision_recording_gates
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
                    vault_gp691_700_authorization_decision_recording_gates (
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
                        recording_gate_shell_json,
                        preparation_lineage_gate_json,
                        owner_identity_requirement_gate_json,
                        owner_step_up_requirement_gate_json,
                        dual_receipt_requirement_gate_json,
                        second_authority_requirement_gate_json,
                        recording_prerequisite_matrix_json,
                        recording_blocker_board_json,
                        recording_receipt_draft_json,
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
                    _canonical_json(
                        recording_gate_shell
                    ),
                    _canonical_json(
                        preparation_lineage_gate
                    ),
                    _canonical_json(
                        owner_identity_requirement_gate
                    ),
                    _canonical_json(
                        owner_step_up_requirement_gate
                    ),
                    _canonical_json(
                        dual_receipt_requirement_gate
                    ),
                    _canonical_json(
                        second_authority_requirement_gate
                    ),
                    _canonical_json(
                        recording_prerequisite_matrix
                    ),
                    _canonical_json(
                        recording_blocker_board
                    ),
                    _canonical_json(
                        recording_receipt_draft
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
                    "GP691_700_TOWER_HANDOFF_DELIVERY_"
                    "AUTHORIZATION_DECISION_RECORDING_GATE_SEALED"
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
                    "gate_open": False,
                    "owner_decision_selected": False,
                    "owner_decision_recorded": False,
                    "recovery_authorization_granted": False,
                    "authorization_token_issued": False,
                    "go_decision_granted": False,
                    "handoff_delivered": False,
                    "recovery_commit_command_issued": False,
                    "provider_connection_occurred": False,
                    "production_write_occurred": False,
                    "destructive_action_occurred": False,
                },
            )

            row = connection.execute(
                """
                SELECT *
                FROM vault_gp691_700_authorization_decision_recording_gates
                WHERE gate_id = ?
                """,
                (
                    gate_id,
                ),
            ).fetchone()

            if row is None:
                raise DecisionRecordingGateIntegrityError(
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
                FROM vault_gp691_700_authorization_decision_recording_gates
                WHERE gate_id = ?
                """,
                (
                    gate_id,
                ),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP691-GP700 gate: {gate_id}"
            )

        result = dict(
            row
        )

        json_columns = (
            "recording_gate_shell_json",
            "preparation_lineage_gate_json",
            "owner_identity_requirement_gate_json",
            "owner_step_up_requirement_gate_json",
            "dual_receipt_requirement_gate_json",
            "second_authority_requirement_gate_json",
            "recording_prerequisite_matrix_json",
            "recording_blocker_board_json",
            "recording_receipt_draft_json",
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
                FROM vault_gp691_700_authorization_decision_recording_gate_events
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
            raise DecisionRecordingGateIntegrityError(
                "decision recording gate payload hash mismatch"
            )

        if (
            record["destination"]
            != TOWER_DESTINATION
        ):
            raise DecisionRecordingGateIntegrityError(
                "decision recording gate destination is not Tower"
            )

        if (
            record["decision_preparation_state"]
            != REQUIRED_DECISION_PREPARATION_STATE
        ):
            raise DecisionRecordingGateIntegrityError(
                "decision preparation lineage mismatch"
            )

        if (
            record["recommendation"]
            != CURRENT_RECOMMENDATION
        ):
            raise DecisionRecordingGateIntegrityError(
                "decision recording recommendation mismatch"
            )

        if (
            record["gate_state"]
            != GATE_STATE
        ):
            raise DecisionRecordingGateIntegrityError(
                "decision recording gate state mismatch"
            )

        shell = record[
            "recording_gate_shell"
        ]

        if shell["gate_open"] is not False:
            raise DecisionRecordingGateIntegrityError(
                "decision recording gate is open"
            )

        if (
            shell["owner_decision_recorded"]
            is not False
        ):
            raise DecisionRecordingGateIntegrityError(
                "owner decision was recorded"
            )

        matrix = record[
            "recording_prerequisite_matrix"
        ]

        if (
            matrix[
                "all_recording_prerequisites_satisfied"
            ]
            is not False
        ):
            raise DecisionRecordingGateIntegrityError(
                "recording prerequisites incorrectly satisfied"
            )

        if (
            matrix[
                "decision_recording_gate_open"
            ]
            is not False
        ):
            raise DecisionRecordingGateIntegrityError(
                "recording gate incorrectly opened"
            )

        blocker_board = record[
            "recording_blocker_board"
        ]

        if (
            blocker_board[
                "decision_recording_blocked"
            ]
            is not True
        ):
            raise DecisionRecordingGateIntegrityError(
                "decision recording blocker is inactive"
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
            raise DecisionRecordingGateIntegrityError(
                "missing decision recording safety fields: "
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
            raise DecisionRecordingGateIntegrityError(
                "unsafe completed decision-recording actions: "
                + ", ".join(
                    unsafe_true
                )
            )

        receipt = record[
            "recording_receipt_draft"
        ]

        if (
            receipt["receipt_status"]
            != "DRAFT_RECORDING_GATE_CLOSED"
        ):
            raise DecisionRecordingGateIntegrityError(
                "recording receipt escaped closed-gate draft state"
            )

        if (
            receipt["recording_gate_open_event_id"]
            is not None
        ):
            raise DecisionRecordingGateIntegrityError(
                "recording gate open event exists"
            )

        if (
            receipt["owner_decision_event_id"]
            is not None
        ):
            raise DecisionRecordingGateIntegrityError(
                "owner decision event exists"
            )

        if (
            receipt["owner_decision_value"]
            is not None
        ):
            raise DecisionRecordingGateIntegrityError(
                "owner decision value exists"
            )

        if (
            receipt["receipt_finalized"]
            is not False
        ):
            raise DecisionRecordingGateIntegrityError(
                "recording receipt was finalized"
            )

        checkpoint = record[
            "checkpoint"
        ]

        forbidden_true_checkpoint_fields = (
            "gate_open",
            "owner_decision_selected",
            "owner_decision_invented",
            "owner_decision_recorded",
            "owner_authenticated",
            "owner_stepped_up",
            "owner_admin_approval_granted",
            "dual_receipt_satisfied",
            "second_authority_review_granted",
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
            raise DecisionRecordingGateIntegrityError(
                "unsafe GP700 checkpoint state: "
                + ", ".join(
                    invalid_checkpoint_fields
                )
            )

        events = self.list_events(
            gate_id
        )

        if not events:
            raise DecisionRecordingGateIntegrityError(
                "decision recording gate has no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if (
                event["previous_event_hash"]
                != previous_event_hash
            ):
                raise DecisionRecordingGateIntegrityError(
                    "decision recording event predecessor mismatch"
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
                raise DecisionRecordingGateIntegrityError(
                    "decision recording event hash mismatch"
                )

            previous_event_hash = (
                event["event_hash"]
            )

        return {
            "pack_range": "GP691-GP700",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "decision_preparation_not_recorded_lineage": True,

            "gate_sealed": True,
            "gate_open": False,

            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,

            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

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
            raise DecisionRecordingGateError(
                "requested_operations must be a sequence"
            )

        operations: list[str] = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise DecisionRecordingGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_GATE_OPERATIONS:
                raise DecisionRecordingGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(
                normalized
            )

        if not operations:
            raise DecisionRecordingGateError(
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
            FROM vault_gp691_700_authorization_decision_recording_gate_events
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
                vault_gp691_700_authorization_decision_recording_gate_events (
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
    ) -> DecisionRecordingGateReceipt:
        return DecisionRecordingGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            gate_open=False,
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
    "ALLOWED_GATE_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "DecisionRecordingGateError",
    "DecisionRecordingGateIntegrityError",
    "DecisionRecordingGateReceipt",
    "GATE_STATE",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_DECISION_PREPARATION_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingGateService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
