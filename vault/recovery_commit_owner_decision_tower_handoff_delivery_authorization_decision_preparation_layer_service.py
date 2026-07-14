"""Archive Vault GP681-GP690.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Preparation Layer.

This layer prepares a future Tower-controlled authorization decision packet.

It does not make, infer, grant, record, or execute an owner decision.

Doctrine:
    Tower is the face and protocol authority.
    Vault is sealed memory.
    Teller is the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller

Prior recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE_SEALED

Current recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_PREPARED

This service never:
    * invents an owner decision
    * selects an owner decision
    * records an owner decision
    * opens an owner-decision recording gate
    * authenticates or steps up an owner
    * grants owner/admin approval
    * satisfies dual receipt
    * grants second-authority review
    * grants a GO decision
    * grants recovery authorization
    * issues or mints an authorization token
    * sends or delivers a handoff
    * starts a Tower delivery session
    * activates scope, commit, execution, or recovery windows
    * opens a commit point
    * issues or executes a recovery commit command
    * restores data
    * mounts or writes production storage
    * connects an external provider
    * exposes raw material, raw paths, raw URLs, or raw tokens
    * performs a destructive action
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


PACK_START = 681
PACK_END = 690

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_PREPARED"
)

PREPARATION_STATE = (
    "AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED"
)

TOWER_DESTINATION = "TOWER"

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_DECISION_PREPARATION_OPERATIONS = frozenset(
    {
        "INTAKE_AUTHORIZATION_GATE_REFERENCE",
        "VERIFY_AUTHORIZATION_NOT_GRANTED_STATE",
        "ASSEMBLE_OWNER_DECISION_CONTEXT_REFERENCES",
        "ASSEMBLE_AUTHORIZATION_PREREQUISITE_SUMMARY",
        "ASSEMBLE_BLOCKER_SUMMARY",
        "DRAFT_OWNER_DECISION_OPTIONS",
        "FREEZE_DECISION_PACKET",
        "DRAFT_DECISION_RECEIPT",
        "VERIFY_NO_DECISION_RECORDED",
        "SEAL_DECISION_PREPARATION_CHECKPOINT",
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

DECISION_OPTIONS = (
    "HOLD",
    "RETURN_FOR_REVIEW",
    "DECLINE_AUTHORIZATION",
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


class AuthorizationDecisionPreparationError(ValueError):
    """Raised when GP681-GP690 preparation input violates doctrine."""


class AuthorizationDecisionPreparationIntegrityError(RuntimeError):
    """Raised when sealed GP681-GP690 evidence fails verification."""


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
        raise AuthorizationDecisionPreparationError(
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
        raise AuthorizationDecisionPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(
                dict(value)
            )
        )
    except (TypeError, ValueError) as exc:
        raise AuthorizationDecisionPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise AuthorizationDecisionPreparationError(
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
        raise AuthorizationDecisionPreparationError(
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
class AuthorizationDecisionPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    preparation_state: str

    decision_packet_prepared: bool
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
            "decision_packet_prepared": (
                self.decision_packet_prepared
            ),
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


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionPreparationService:
    """Persistent GP681-GP690 authorization decision preparation service."""

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
            str(self.database_path)
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
                vault_gp681_690_authorization_decision_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    authorization_gate_id TEXT NOT NULL,
                    authorization_gate_hash TEXT NOT NULL,
                    authorization_gate_state TEXT NOT NULL
                        CHECK(
                            authorization_gate_state =
                            'AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    decision_preparation_shell_json TEXT NOT NULL,
                    gate_lineage_intake_json TEXT NOT NULL,
                    decision_context_board_json TEXT NOT NULL,
                    prerequisite_summary_json TEXT NOT NULL,
                    blocker_summary_json TEXT NOT NULL,
                    decision_option_board_json TEXT NOT NULL,
                    decision_packet_json TEXT NOT NULL,
                    decision_receipt_draft_json TEXT NOT NULL,
                    safety_blocker_board_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    preparation_payload_json TEXT NOT NULL,
                    preparation_hash TEXT NOT NULL UNIQUE,
                    predecessor_preparation_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_PREPARED'
                        ),

                    preparation_state TEXT NOT NULL
                        CHECK(
                            preparation_state =
                            'AUTHORIZATION_DECISION_PREPARED_NOT_RECORDED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp681_690_authorization_decision_preparation_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES
                        vault_gp681_690_authorization_decision_preparations(
                            preparation_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp681_690_recovery_case
                ON vault_gp681_690_authorization_decision_preparations(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp681_690_authorization_gate
                ON vault_gp681_690_authorization_decision_preparations(
                    authorization_gate_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp681_690_event_chain
                ON vault_gp681_690_authorization_decision_preparation_events(
                    preparation_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp681_690_preparation_no_update
                BEFORE UPDATE
                ON vault_gp681_690_authorization_decision_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP681-GP690 decision preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp681_690_preparation_no_delete
                BEFORE DELETE
                ON vault_gp681_690_authorization_decision_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP681-GP690 decision preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp681_690_event_no_update
                BEFORE UPDATE
                ON vault_gp681_690_authorization_decision_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP681-GP690 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp681_690_event_no_delete
                BEFORE DELETE
                ON vault_gp681_690_authorization_decision_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP681-GP690 events are append-only'
                    );
                END;
                """
            )

    def prepare_authorization_decision(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        authorization_gate_id: str,
        authorization_gate_hash: str,
        authorization_gate_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> AuthorizationDecisionPreparationReceipt:
        """Prepare a Tower decision packet without selecting a decision."""

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

        authorization_gate_id = _required_text(
            "authorization_gate_id",
            authorization_gate_id,
        )

        authorization_gate_hash = _required_text(
            "authorization_gate_hash",
            authorization_gate_hash,
        )

        authorization_gate_state = _required_text(
            "authorization_gate_state",
            authorization_gate_state,
        ).upper()

        if (
            authorization_gate_state
            != "AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED"
        ):
            raise AuthorizationDecisionPreparationError(
                "authorization_gate_state must preserve "
                "AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED"
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
            raise AuthorizationDecisionPreparationError(
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
            "authorization_gate_id": (
                authorization_gate_id
            ),
            "authorization_gate_hash": (
                authorization_gate_hash
            ),
            "authorization_gate_state": (
                authorization_gate_state
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
            "vault-gp681-690-"
            + _sha256_text(
                _canonical_json(
                    identity
                )
            )[:24]
        )

        # GP681 — Authorization Decision Preparation Shell
        decision_preparation_shell = {
            "pack": "GP681",
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
            "decision_packet_prepared": True,
            "owner_decision_selected": False,
            "owner_decision_recorded": False,
        }

        # GP682 — Authorization Gate Lineage Intake Board
        gate_lineage_intake = {
            "pack": "GP682",
            "authorization_gate_id": (
                authorization_gate_id
            ),
            "authorization_gate_hash": (
                authorization_gate_hash
            ),
            "authorization_gate_state": (
                authorization_gate_state
            ),
            "required_gate_state": (
                "AUTHORIZATION_GATE_SEALED_"
                "AUTHORIZATION_NOT_GRANTED"
            ),
            "authorization_granted_in_lineage": False,
            "authorization_token_present": False,
            "go_decision_present": False,
        }

        # GP683 — Owner Decision Context Reference Board
        decision_context_board = {
            "pack": "GP683",
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
            "reference_only": True,
            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,
        }

        # GP684 — Authorization Prerequisite Summary Board
        prerequisite_summary = {
            "pack": "GP684",
            "authorization_gate_reference_present": True,
            "authorization_gate_hash_present": True,
            "tower_authority_reference_present": True,
            "owner_decision_reference_present": True,

            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,
            "go_decision_granted": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,

            "all_authorization_prerequisites_satisfied": False,
        }

        # GP685 — Authorization Blocker Summary Board
        blocker_summary = {
            "pack": "GP685",
            "authorization_blocked": True,
            "decision_recording_blocked": True,
            "active_blockers": [
                "NO_OWNER_AUTHENTICATION",
                "NO_OWNER_STEP_UP",
                "NO_OWNER_ADMIN_APPROVAL",
                "NO_DUAL_RECEIPT_SATISFACTION",
                "NO_SECOND_AUTHORITY_REVIEW",
                "NO_GO_DECISION",
                "NO_RECOVERY_AUTHORIZATION",
                "NO_AUTHORIZATION_TOKEN",
                "NO_OWNER_DECISION_RECORDING_GATE",
            ],
        }

        # GP686 — Owner Decision Option Draft Board
        decision_option_board = {
            "pack": "GP686",
            "options": list(
                DECISION_OPTIONS
            ),
            "option_mode": (
                "DRAFT_OPTIONS_ONLY"
            ),
            "default_option": None,
            "recommended_option": None,
            "selected_option": None,
            "selection_inferred": False,
            "selection_recorded": False,
            "authorization_option_exposed": False,
        }

        # GP687 — Authorization Decision Packet Freeze Board
        decision_packet = {
            "pack": "GP687",
            "packet_type": (
                "TOWER_HANDOFF_DELIVERY_"
                "AUTHORIZATION_DECISION_PACKET"
            ),
            "packet_status": (
                "FROZEN_PREPARED_NOT_PRESENTED_FOR_RECORDING"
            ),
            "preparation_id": (
                preparation_id
            ),
            "authorization_gate_id": (
                authorization_gate_id
            ),
            "authorization_gate_hash": (
                authorization_gate_hash
            ),
            "owner_decision_record_id": (
                owner_decision_record_id
            ),
            "decision_options": list(
                DECISION_OPTIONS
            ),
            "selected_decision": None,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,
            "decision_recording_gate_opened": False,
            "authorization_granted": False,
            "authorization_token_issued": False,
            "safe_metadata": metadata,
            "requested_operations": operations,
        }

        decision_packet[
            "packet_hash"
        ] = _sha256_text(
            _canonical_json(
                decision_packet
            )
        )

        # GP688 — Authorization Decision Receipt Draft Ledger
        decision_receipt_draft = {
            "pack": "GP688",
            "receipt_type": (
                "TOWER_HANDOFF_DELIVERY_"
                "AUTHORIZATION_DECISION_RECEIPT_DRAFT"
            ),
            "receipt_status": (
                "DRAFT_NO_OWNER_DECISION_RECORDED"
            ),
            "preparation_id": (
                preparation_id
            ),
            "decision_event_id": None,
            "decision_value": None,
            "authorization_event_id": None,
            "authorization_token_reference": None,
            "go_decision_reference": None,
            "receipt_finalized": False,
        }

        decision_receipt_draft[
            "receipt_draft_hash"
        ] = _sha256_text(
            _canonical_json(
                decision_receipt_draft
            )
        )

        # GP689 — Decision Preparation Safety Blocker Board
        safety_state = _false_safety_state()

        safety_blocker_board = {
            "pack": "GP689",
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
                "DECISION_OPTIONS_ARE_DRAFT_ONLY",
                "NO_SELECTED_OWNER_DECISION",
                "NO_OWNER_DECISION_RECORD",
                "NO_OWNER_DECISION_RECORDING_GATE",
                "NO_OWNER_AUTHENTICATION",
                "NO_OWNER_STEP_UP",
                "NO_GO_DECISION",
                "NO_RECOVERY_AUTHORIZATION",
                "NO_AUTHORIZATION_TOKEN",
                "NO_RECOVERY_COMMIT_COMMAND",
                "NO_PROVIDER_CONNECTION",
                "NO_PRODUCTION_STORAGE_WRITE",
            ],
        }

        # GP690 — Authorization Decision Preparation Readiness Checkpoint
        checkpoint = {
            "pack": "GP690",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                "DECISION_PREPARATION_READINESS"
            ),
            "preparation_id": (
                preparation_id
            ),
            "prior_pack_range": (
                "GP671-GP680"
            ),
            "current_pack_range": (
                "GP681-GP690"
            ),
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "preparation_state": (
                PREPARATION_STATE
            ),
            "decision_packet_prepared": True,
            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,
            "owner_decision_recording_gate_opened": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,
            "go_decision_granted": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,
            "handoff_delivered": False,
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
                "DECISION_RECORDING_GATE"
            ),
        }

        preparation_payload = {
            "gp681_decision_preparation_shell": (
                decision_preparation_shell
            ),
            "gp682_gate_lineage_intake": (
                gate_lineage_intake
            ),
            "gp683_decision_context_board": (
                decision_context_board
            ),
            "gp684_prerequisite_summary": (
                prerequisite_summary
            ),
            "gp685_blocker_summary": (
                blocker_summary
            ),
            "gp686_decision_option_board": (
                decision_option_board
            ),
            "gp687_decision_packet": (
                decision_packet
            ),
            "gp688_decision_receipt_draft": (
                decision_receipt_draft
            ),
            "gp689_safety_blocker_board": (
                safety_blocker_board
            ),
            "gp690_checkpoint": (
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
                FROM vault_gp681_690_authorization_decision_preparations
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
                    raise AuthorizationDecisionPreparationError(
                        "idempotency_key already exists with "
                        "different immutable decision-preparation inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp681_690_authorization_decision_preparations
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
                    vault_gp681_690_authorization_decision_preparations (
                        preparation_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        authorization_gate_id,
                        authorization_gate_hash,
                        authorization_gate_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        decision_preparation_shell_json,
                        gate_lineage_intake_json,
                        decision_context_board_json,
                        prerequisite_summary_json,
                        blocker_summary_json,
                        decision_option_board_json,
                        decision_packet_json,
                        decision_receipt_draft_json,
                        safety_blocker_board_json,
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
                    authorization_gate_id,
                    authorization_gate_hash,
                    authorization_gate_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(
                        decision_preparation_shell
                    ),
                    _canonical_json(
                        gate_lineage_intake
                    ),
                    _canonical_json(
                        decision_context_board
                    ),
                    _canonical_json(
                        prerequisite_summary
                    ),
                    _canonical_json(
                        blocker_summary
                    ),
                    _canonical_json(
                        decision_option_board
                    ),
                    _canonical_json(
                        decision_packet
                    ),
                    _canonical_json(
                        decision_receipt_draft
                    ),
                    _canonical_json(
                        safety_blocker_board
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
                    "GP681_690_TOWER_HANDOFF_DELIVERY_"
                    "AUTHORIZATION_DECISION_PREPARATION_SEALED"
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
                    "decision_packet_prepared": True,
                    "owner_decision_selected": False,
                    "owner_decision_recorded": False,
                    "authorization_granted": False,
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
                FROM vault_gp681_690_authorization_decision_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

            if row is None:
                raise AuthorizationDecisionPreparationIntegrityError(
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
                FROM vault_gp681_690_authorization_decision_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP681-GP690 preparation: {preparation_id}"
            )

        result = dict(
            row
        )

        json_columns = (
            "decision_preparation_shell_json",
            "gate_lineage_intake_json",
            "decision_context_board_json",
            "prerequisite_summary_json",
            "blocker_summary_json",
            "decision_option_board_json",
            "decision_packet_json",
            "decision_receipt_draft_json",
            "safety_blocker_board_json",
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
                FROM vault_gp681_690_authorization_decision_preparation_events
                WHERE preparation_id = ?
                ORDER BY event_id ASC
                """,
                (preparation_id,),
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

        expected_hash = _sha256_text(
            payload_json
        )

        if expected_hash != record["preparation_hash"]:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision preparation payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision preparation destination is not Tower"
            )

        if (
            record["authorization_gate_state"]
            != "AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED"
        ):
            raise AuthorizationDecisionPreparationIntegrityError(
                "authorization-gate lineage boundary mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision preparation recommendation mismatch"
            )

        if record["preparation_state"] != PREPARATION_STATE:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision preparation state mismatch"
            )

        option_board = record[
            "decision_option_board"
        ]

        if option_board["selected_option"] is not None:
            raise AuthorizationDecisionPreparationIntegrityError(
                "owner decision option was selected"
            )

        if option_board["recommended_option"] is not None:
            raise AuthorizationDecisionPreparationIntegrityError(
                "owner decision option was recommended"
            )

        if option_board["default_option"] is not None:
            raise AuthorizationDecisionPreparationIntegrityError(
                "owner decision option was defaulted"
            )

        if (
            option_board["authorization_option_exposed"]
            is not False
        ):
            raise AuthorizationDecisionPreparationIntegrityError(
                "authorization option was exposed"
            )

        packet = record[
            "decision_packet"
        ]

        if packet["selected_decision"] is not None:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision packet contains a selected decision"
            )

        if (
            packet["decision_recording_gate_opened"]
            is not False
        ):
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision recording gate was opened"
            )

        receipt = record[
            "decision_receipt_draft"
        ]

        if (
            receipt["receipt_status"]
            != "DRAFT_NO_OWNER_DECISION_RECORDED"
        ):
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision receipt escaped draft state"
            )

        if receipt["decision_value"] is not None:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision receipt contains a decision value"
            )

        if receipt["receipt_finalized"] is not False:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision receipt was finalized"
            )

        safety_state = record[
            "safety_blocker_board"
        ]["safety_state"]

        missing_safety_fields = sorted(
            set(
                SAFETY_STATE_FIELDS
            )
            - set(
                safety_state
            )
        )

        if missing_safety_fields:
            raise AuthorizationDecisionPreparationIntegrityError(
                "missing decision safety fields: "
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
            raise AuthorizationDecisionPreparationIntegrityError(
                "unsafe completed decision-preparation actions: "
                + ", ".join(
                    unsafe_true
                )
            )

        checkpoint = record[
            "checkpoint"
        ]

        forbidden_true_checkpoint_fields = (
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
            "recovery_authorization_granted",
            "authorization_token_issued",
            "handoff_delivered",
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
            raise AuthorizationDecisionPreparationIntegrityError(
                "unsafe GP690 checkpoint state: "
                + ", ".join(
                    invalid_checkpoint_fields
                )
            )

        events = self.list_events(
            preparation_id
        )

        if not events:
            raise AuthorizationDecisionPreparationIntegrityError(
                "decision preparation has no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if (
                event["previous_event_hash"]
                != previous_event_hash
            ):
                raise AuthorizationDecisionPreparationIntegrityError(
                    "decision preparation event predecessor mismatch"
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
                raise AuthorizationDecisionPreparationIntegrityError(
                    "decision preparation event hash mismatch"
                )

            previous_event_hash = event[
                "event_hash"
            ]

        return {
            "pack_range": "GP681-GP690",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "authorization_gate_not_granted_lineage": True,

            "decision_packet_prepared": True,
            "owner_decision_selected": False,
            "owner_decision_invented": False,
            "owner_decision_recorded": False,
            "owner_decision_recording_gate_opened": False,

            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

            "go_decision_granted": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,

            "handoff_delivered": False,
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
                ALLOWED_DECISION_PREPARATION_OPERATIONS
            )

        if isinstance(
            requested_operations,
            (str, bytes),
        ):
            raise AuthorizationDecisionPreparationError(
                "requested_operations must be a sequence"
            )

        operations: list[str] = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise AuthorizationDecisionPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if (
                normalized
                not in ALLOWED_DECISION_PREPARATION_OPERATIONS
            ):
                raise AuthorizationDecisionPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(
                normalized
            )

        if not operations:
            raise AuthorizationDecisionPreparationError(
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
            FROM vault_gp681_690_authorization_decision_preparation_events
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
                vault_gp681_690_authorization_decision_preparation_events (
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
    ) -> AuthorizationDecisionPreparationReceipt:
        return AuthorizationDecisionPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            preparation_state=row["preparation_state"],

            decision_packet_prepared=True,
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
    "ALLOWED_DECISION_PREPARATION_OPERATIONS",
    "AuthorizationDecisionPreparationError",
    "AuthorizationDecisionPreparationIntegrityError",
    "AuthorizationDecisionPreparationReceipt",
    "CURRENT_RECOMMENDATION",
    "DECISION_OPTIONS",
    "PACK_END",
    "PACK_START",
    "PREPARATION_STATE",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionPreparationService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
