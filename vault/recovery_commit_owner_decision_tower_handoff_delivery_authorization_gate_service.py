"""Archive Vault GP671-GP680.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Gate.

This layer receives reference-only evidence from the sealed GP661-GP670
delivery-preparation layer and evaluates whether the evidence needed by a
future Tower-controlled authorization decision is present.

This layer cannot grant authorization.

Doctrine:
    Tower is the face and protocol authority.
    Vault is sealed memory.
    Teller is the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller

Prior recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_PREPARED_NOT_SENT

Current recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE_SEALED

This service never:
    * delivers or sends a handoff
    * accepts a handoff
    * invents or records an owner decision
    * creates or starts a Tower acceptance or delivery session
    * authenticates or steps up an owner
    * grants owner or administrator approval
    * satisfies a dual receipt
    * grants second-authority review
    * opens an owner-decision recording gate
    * grants a GO decision
    * grants or issues recovery authorization
    * mints or issues an authorization token
    * activates scope, commit, execution, or recovery windows
    * opens a commit point
    * issues or executes a recovery commit command
    * restores data
    * mounts or writes production storage
    * connects an external provider
    * exposes raw paths, URLs, tokens, credentials, or raw material
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


PACK_START = 671
PACK_END = 680

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_PREPARED_NOT_SENT"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE_SEALED"
)

GATE_STATE = (
    "AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED"
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
        "INTAKE_PREPARED_HANDOFF_REFERENCE",
        "VERIFY_PREPARED_NOT_SENT_STATE",
        "VERIFY_TOWER_AUTHORITY_REFERENCE",
        "VERIFY_OWNER_DECISION_REFERENCE",
        "VERIFY_ACCEPTANCE_CLOSEOUT_LINEAGE",
        "EVALUATE_AUTHORIZATION_PREREQUISITES",
        "EVALUATE_DUAL_RECEIPT_REQUIREMENT",
        "EVALUATE_SECOND_AUTHORITY_REQUIREMENT",
        "EVALUATE_AUTHORIZATION_BLOCKERS",
        "SEAL_AUTHORIZATION_GATE_CHECKPOINT",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
        "DELIVER_HANDOFF",
        "SEND_HANDOFF",
        "ACCEPT_HANDOFF",
        "RECORD_ACCEPTANCE_DECISION",
        "CREATE_TOWER_ACCEPTANCE_SESSION",
        "START_TOWER_ACCEPTANCE_SESSION",
        "CREATE_TOWER_DELIVERY_SESSION",
        "START_TOWER_DELIVERY_SESSION",
        "AUTHENTICATE_OWNER",
        "STEP_UP_OWNER",
        "GRANT_OWNER_APPROVAL",
        "GRANT_ADMIN_APPROVAL",
        "SATISFY_DUAL_RECEIPT",
        "GRANT_SECOND_AUTHORITY_REVIEW",
        "SELECT_OWNER_DECISION",
        "INVENT_OWNER_DECISION",
        "RECORD_OWNER_DECISION",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "GRANT_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
        "MINT_AUTHORIZATION_TOKEN",
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
    "handoff_delivered",
    "handoff_sent",
    "handoff_accepted",
    "acceptance_decision_recorded",
    "tower_acceptance_session_created",
    "tower_acceptance_session_started",
    "tower_delivery_session_created",
    "tower_delivery_session_started",
    "owner_authenticated",
    "owner_stepped_up",
    "owner_admin_approval_granted",
    "dual_receipt_satisfied",
    "second_authority_review_granted",
    "owner_selection_recorded",
    "owner_decision_invented",
    "owner_decision_recorded",
    "owner_decision_recording_gate_opened",
    "go_decision_granted",
    "recovery_authorization_issued",
    "recovery_authorization_granted",
    "authorization_token_issued",
    "authorization_token_minted",
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


class AuthorizationGateError(ValueError):
    """Raised when GP671-GP680 input violates a locked boundary."""


class AuthorizationGateIntegrityError(RuntimeError):
    """Raised when sealed GP671-GP680 evidence fails verification."""


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
        raise AuthorizationGateError(
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
                    location=(
                        f"{location}[{index}]"
                    ),
                )
            )

    return blocked


def _normalize_safe_metadata(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise AuthorizationGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(
                dict(value)
            )
        )
    except (TypeError, ValueError) as exc:
        raise AuthorizationGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise AuthorizationGateError(
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
        raise AuthorizationGateError(
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
class AuthorizationGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    delivery_authorized: bool
    recovery_authorization_granted: bool
    authorization_token_issued: bool
    go_decision_granted: bool

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
            "delivery_authorized": (
                self.delivery_authorized
            ),
            "recovery_authorization_granted": (
                self.recovery_authorization_granted
            ),
            "authorization_token_issued": (
                self.authorization_token_issued
            ),
            "go_decision_granted": (
                self.go_decision_granted
            ),
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": (
                self.idempotent_replay
            ),
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationGateService:
    """Persistent GP671-GP680 authorization evidence gate."""

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
                vault_gp671_680_delivery_authorization_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,
                    acceptance_closeout_record_id TEXT NOT NULL,

                    delivery_preparation_id TEXT NOT NULL,
                    delivery_preparation_hash TEXT NOT NULL,
                    delivery_preparation_state TEXT NOT NULL
                        CHECK(
                            delivery_preparation_state =
                            'PREPARED_NOT_SENT'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    gate_intake_json TEXT NOT NULL,
                    preparation_lineage_board_json TEXT NOT NULL,
                    tower_authority_gate_json TEXT NOT NULL,
                    owner_decision_reference_gate_json TEXT NOT NULL,
                    dual_receipt_gate_json TEXT NOT NULL,
                    second_authority_gate_json TEXT NOT NULL,
                    authorization_prerequisite_matrix_json TEXT NOT NULL,
                    authorization_blocker_board_json TEXT NOT NULL,
                    authorization_receipt_draft_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    gate_payload_json TEXT NOT NULL,
                    gate_hash TEXT NOT NULL UNIQUE,
                    predecessor_gate_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp671_680_delivery_authorization_gate_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES
                        vault_gp671_680_delivery_authorization_gates(
                            gate_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp671_680_gate_recovery_case
                ON vault_gp671_680_delivery_authorization_gates(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp671_680_gate_preparation
                ON vault_gp671_680_delivery_authorization_gates(
                    delivery_preparation_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp671_680_gate_tower_authority
                ON vault_gp671_680_delivery_authorization_gates(
                    tower_authority_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp671_680_event_chain
                ON vault_gp671_680_delivery_authorization_gate_events(
                    gate_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp671_680_gate_no_update
                BEFORE UPDATE
                ON vault_gp671_680_delivery_authorization_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP671-GP680 authorization gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp671_680_gate_no_delete
                BEFORE DELETE
                ON vault_gp671_680_delivery_authorization_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP671-GP680 authorization gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp671_680_event_no_update
                BEFORE UPDATE
                ON vault_gp671_680_delivery_authorization_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP671-GP680 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp671_680_event_no_delete
                BEFORE DELETE
                ON vault_gp671_680_delivery_authorization_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP671-GP680 events are append-only'
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
        acceptance_closeout_record_id: str,
        delivery_preparation_id: str,
        delivery_preparation_hash: str,
        delivery_preparation_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> AuthorizationGateReceipt:
        """Seal gate evidence without granting authorization."""

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

        acceptance_closeout_record_id = _required_text(
            "acceptance_closeout_record_id",
            acceptance_closeout_record_id,
        )

        delivery_preparation_id = _required_text(
            "delivery_preparation_id",
            delivery_preparation_id,
        )

        delivery_preparation_hash = _required_text(
            "delivery_preparation_hash",
            delivery_preparation_hash,
        )

        delivery_preparation_state = _required_text(
            "delivery_preparation_state",
            delivery_preparation_state,
        ).upper()

        if delivery_preparation_state != "PREPARED_NOT_SENT":
            raise AuthorizationGateError(
                "delivery_preparation_state must be PREPARED_NOT_SENT"
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
            raise AuthorizationGateError(
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
            "acceptance_closeout_record_id": (
                acceptance_closeout_record_id
            ),
            "delivery_preparation_id": (
                delivery_preparation_id
            ),
            "delivery_preparation_hash": (
                delivery_preparation_hash
            ),
            "delivery_preparation_state": (
                delivery_preparation_state
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
            "vault-gp671-680-"
            + _sha256_text(
                _canonical_json(
                    identity
                )
            )[:24]
        )

        # GP671 — Tower Handoff Delivery Authorization Gate Shell
        gate_intake = {
            "pack": "GP671",
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
            "delivery_authorized": False,
            "recovery_authorization_granted": False,
        }

        # GP672 — Prepared Delivery Package Lineage Gate
        preparation_lineage_board = {
            "pack": "GP672",
            "delivery_preparation_id": (
                delivery_preparation_id
            ),
            "delivery_preparation_hash": (
                delivery_preparation_hash
            ),
            "delivery_preparation_state": (
                delivery_preparation_state
            ),
            "required_state": "PREPARED_NOT_SENT",
            "prepared_reference_present": True,
            "prepared_hash_present": True,
            "sent_state_detected": False,
            "authorization_inferred_from_preparation": False,
            "lineage_gate_state": (
                "PREPARATION_LINEAGE_RECORDED_"
                "AUTHORIZATION_NOT_GRANTED"
            ),
        }

        # GP673 — Tower Protocol Authority Gate
        tower_authority_gate = {
            "pack": "GP673",
            "destination": TOWER_DESTINATION,
            "tower_authority_id": (
                tower_authority_id
            ),
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "target_environment": (
                target_environment
            ),
            "tower_authority_reference_present": True,
            "tower_destination_bound": True,
            "tower_acceptance_session_created": False,
            "tower_acceptance_session_started": False,
            "tower_delivery_session_created": False,
            "tower_delivery_session_started": False,
            "tower_authority_approval_granted": False,
        }

        # GP674 — Owner Decision Reference Boundary Gate
        owner_decision_reference_gate = {
            "pack": "GP674",
            "owner_decision_record_id": (
                owner_decision_record_id
            ),
            "reference_present": True,
            "owner_selection_invented": False,
            "owner_decision_invented": False,
            "owner_decision_recorded_by_this_layer": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "owner_decision_recording_gate_opened": False,
        }

        # GP675 — Dual Receipt Authorization Requirement Gate
        dual_receipt_gate = {
            "pack": "GP675",
            "dual_receipt_required_for_later_authorization": True,
            "dual_receipt_requirement_recorded": True,
            "dual_receipt_satisfied": False,
            "dual_receipt_satisfied_by_this_layer": False,
            "authorization_blocked_without_dual_receipt": True,
        }

        # GP676 — Second Authority Authorization Requirement Gate
        second_authority_gate = {
            "pack": "GP676",
            "second_authority_required_for_later_authorization": True,
            "second_authority_requirement_recorded": True,
            "second_authority_review_granted": False,
            "second_authority_granted_by_this_layer": False,
            "authorization_blocked_without_second_authority": True,
        }

        # GP677 — Delivery Authorization Prerequisite Matrix
        authorization_prerequisite_matrix = {
            "pack": "GP677",
            "prepared_not_sent_reference": True,
            "tower_authority_reference": True,
            "owner_decision_reference": True,
            "acceptance_closeout_reference": True,

            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,
            "go_decision_granted": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,

            "all_authorization_prerequisites_satisfied": False,
            "delivery_authorized": False,
        }

        # GP678 — Delivery Authorization Safety Blocker Board
        safety_state = _false_safety_state()

        authorization_blocker_board = {
            "pack": "GP678",
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "authorization_blocked": True,
            "delivery_blocked": True,
            "safety_state": safety_state,
            "active_blockers": [
                "NO_OWNER_AUTHENTICATION",
                "NO_OWNER_STEP_UP",
                "NO_OWNER_ADMIN_APPROVAL",
                "NO_DUAL_RECEIPT_SATISFACTION",
                "NO_SECOND_AUTHORITY_REVIEW",
                "NO_GO_DECISION",
                "NO_RECOVERY_AUTHORIZATION",
                "NO_AUTHORIZATION_TOKEN",
                "NO_TOWER_DELIVERY_SESSION",
                "NO_RECOVERY_COMMIT_COMMAND",
                "NO_PROVIDER_CONNECTION",
                "NO_PRODUCTION_STORAGE_WRITE",
            ],
        }

        # GP679 — Authorization Receipt Draft Ledger
        authorization_receipt_draft = {
            "pack": "GP679",
            "receipt_type": (
                "TOWER_HANDOFF_DELIVERY_"
                "AUTHORIZATION_RECEIPT_DRAFT"
            ),
            "receipt_status": (
                "DRAFT_AUTHORIZATION_NOT_GRANTED"
            ),
            "gate_id": gate_id,
            "authorization_event_id": None,
            "authorization_token_reference": None,
            "go_decision_reference": None,
            "delivery_authorized": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,
            "receipt_finalized": False,
        }

        authorization_receipt_draft[
            "receipt_draft_hash"
        ] = _sha256_text(
            _canonical_json(
                authorization_receipt_draft
            )
        )

        # GP680 — Authorization Gate Readiness Checkpoint
        checkpoint = {
            "pack": "GP680",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_"
                "AUTHORIZATION_GATE_READINESS"
            ),
            "gate_id": gate_id,
            "prior_pack_range": "GP661-GP670",
            "current_pack_range": "GP671-GP680",
            "recommendation": (
                CURRENT_RECOMMENDATION
            ),
            "gate_state": GATE_STATE,
            "gate_sealed": True,

            "delivery_authorized": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,
            "go_decision_granted": False,
            "owner_decision_invented": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

            "recovery_commit_command_issued": False,
            "recovery_commit_executed": False,
            "restore_occurred": False,
            "production_mount_occurred": False,
            "production_write_occurred": False,
            "provider_connection_occurred": False,
            "raw_material_exposed": False,
            "destructive_action_occurred": False,

            "next_gate": (
                "TOWER_HANDOFF_DELIVERY_"
                "AUTHORIZATION_DECISION_PREPARATION_LAYER"
            ),
        }

        gate_payload = {
            "gp671_gate_intake": (
                gate_intake
            ),
            "gp672_preparation_lineage_board": (
                preparation_lineage_board
            ),
            "gp673_tower_authority_gate": (
                tower_authority_gate
            ),
            "gp674_owner_decision_reference_gate": (
                owner_decision_reference_gate
            ),
            "gp675_dual_receipt_gate": (
                dual_receipt_gate
            ),
            "gp676_second_authority_gate": (
                second_authority_gate
            ),
            "gp677_authorization_prerequisite_matrix": (
                authorization_prerequisite_matrix
            ),
            "gp678_authorization_blocker_board": (
                authorization_blocker_board
            ),
            "gp679_authorization_receipt_draft": (
                authorization_receipt_draft
            ),
            "gp680_checkpoint": (
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
                FROM vault_gp671_680_delivery_authorization_gates
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
                    raise AuthorizationGateError(
                        "idempotency_key already exists with "
                        "different immutable authorization-gate inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp671_680_delivery_authorization_gates
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
                    vault_gp671_680_delivery_authorization_gates (
                        gate_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        acceptance_closeout_record_id,
                        delivery_preparation_id,
                        delivery_preparation_hash,
                        delivery_preparation_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        gate_intake_json,
                        preparation_lineage_board_json,
                        tower_authority_gate_json,
                        owner_decision_reference_gate_json,
                        dual_receipt_gate_json,
                        second_authority_gate_json,
                        authorization_prerequisite_matrix_json,
                        authorization_blocker_board_json,
                        authorization_receipt_draft_json,
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
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    gate_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    acceptance_closeout_record_id,
                    delivery_preparation_id,
                    delivery_preparation_hash,
                    delivery_preparation_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(
                        gate_intake
                    ),
                    _canonical_json(
                        preparation_lineage_board
                    ),
                    _canonical_json(
                        tower_authority_gate
                    ),
                    _canonical_json(
                        owner_decision_reference_gate
                    ),
                    _canonical_json(
                        dual_receipt_gate
                    ),
                    _canonical_json(
                        second_authority_gate
                    ),
                    _canonical_json(
                        authorization_prerequisite_matrix
                    ),
                    _canonical_json(
                        authorization_blocker_board
                    ),
                    _canonical_json(
                        authorization_receipt_draft
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
                    "GP671_680_TOWER_HANDOFF_DELIVERY_"
                    "AUTHORIZATION_GATE_SEALED"
                ),
                event_payload={
                    "gate_hash": gate_hash,
                    "recommendation": (
                        CURRENT_RECOMMENDATION
                    ),
                    "gate_state": (
                        GATE_STATE
                    ),
                    "gate_sealed": True,
                    "delivery_authorized": False,
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
                FROM vault_gp671_680_delivery_authorization_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

            if row is None:
                raise AuthorizationGateIntegrityError(
                    "authorization gate failed to persist"
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
                FROM vault_gp671_680_delivery_authorization_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP671-GP680 gate: {gate_id}"
            )

        result = dict(
            row
        )

        json_columns = (
            "gate_intake_json",
            "preparation_lineage_board_json",
            "tower_authority_gate_json",
            "owner_decision_reference_gate_json",
            "dual_receipt_gate_json",
            "second_authority_gate_json",
            "authorization_prerequisite_matrix_json",
            "authorization_blocker_board_json",
            "authorization_receipt_draft_json",
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
                FROM vault_gp671_680_delivery_authorization_gate_events
                WHERE gate_id = ?
                ORDER BY event_id ASC
                """,
                (gate_id,),
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
            raise AuthorizationGateIntegrityError(
                "authorization gate payload hash mismatch"
            )

        if (
            record["destination"]
            != TOWER_DESTINATION
        ):
            raise AuthorizationGateIntegrityError(
                "authorization gate destination is not Tower"
            )

        if (
            record["delivery_preparation_state"]
            != "PREPARED_NOT_SENT"
        ):
            raise AuthorizationGateIntegrityError(
                "prepared-not-sent lineage boundary mismatch"
            )

        if (
            record["recommendation"]
            != CURRENT_RECOMMENDATION
        ):
            raise AuthorizationGateIntegrityError(
                "authorization gate recommendation mismatch"
            )

        if (
            record["gate_state"]
            != GATE_STATE
        ):
            raise AuthorizationGateIntegrityError(
                "authorization gate state mismatch"
            )

        prerequisite_matrix = record[
            "authorization_prerequisite_matrix"
        ]

        if (
            prerequisite_matrix[
                "all_authorization_prerequisites_satisfied"
            ]
            is not False
        ):
            raise AuthorizationGateIntegrityError(
                "authorization prerequisites were incorrectly satisfied"
            )

        if (
            prerequisite_matrix[
                "delivery_authorized"
            ]
            is not False
        ):
            raise AuthorizationGateIntegrityError(
                "delivery was incorrectly authorized"
            )

        blocker_board = record[
            "authorization_blocker_board"
        ]

        if (
            blocker_board[
                "authorization_blocked"
            ]
            is not True
        ):
            raise AuthorizationGateIntegrityError(
                "authorization blocker is not active"
            )

        if (
            blocker_board[
                "delivery_blocked"
            ]
            is not True
        ):
            raise AuthorizationGateIntegrityError(
                "delivery blocker is not active"
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
            raise AuthorizationGateIntegrityError(
                "missing authorization safety fields: "
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
            raise AuthorizationGateIntegrityError(
                "unsafe completed authorization-gate actions: "
                + ", ".join(
                    unsafe_true
                )
            )

        receipt_draft = record[
            "authorization_receipt_draft"
        ]

        if (
            receipt_draft[
                "receipt_status"
            ]
            != "DRAFT_AUTHORIZATION_NOT_GRANTED"
        ):
            raise AuthorizationGateIntegrityError(
                "authorization receipt escaped draft state"
            )

        if (
            receipt_draft[
                "receipt_finalized"
            ]
            is not False
        ):
            raise AuthorizationGateIntegrityError(
                "authorization receipt was finalized"
            )

        if (
            receipt_draft[
                "authorization_token_reference"
            ]
            is not None
        ):
            raise AuthorizationGateIntegrityError(
                "authorization token reference exists"
            )

        checkpoint = record[
            "checkpoint"
        ]

        forbidden_true_checkpoint_fields = (
            "delivery_authorized",
            "recovery_authorization_granted",
            "authorization_token_issued",
            "go_decision_granted",
            "owner_decision_invented",
            "owner_authenticated",
            "owner_stepped_up",
            "owner_admin_approval_granted",
            "dual_receipt_satisfied",
            "second_authority_review_granted",
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
            raise AuthorizationGateIntegrityError(
                "unsafe GP680 checkpoint state: "
                + ", ".join(
                    invalid_checkpoint_fields
                )
            )

        events = self.list_events(
            gate_id
        )

        if not events:
            raise AuthorizationGateIntegrityError(
                "authorization gate has no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if (
                event[
                    "previous_event_hash"
                ]
                != previous_event_hash
            ):
                raise AuthorizationGateIntegrityError(
                    "authorization gate event predecessor mismatch"
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
                    event[
                        "previous_event_hash"
                    ]
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
                raise AuthorizationGateIntegrityError(
                    "authorization gate event hash mismatch"
                )

            previous_event_hash = (
                event["event_hash"]
            )

        return {
            "pack_range": "GP671-GP680",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "prepared_not_sent_lineage": True,

            "gate_sealed": True,
            "delivery_authorized": False,
            "recovery_authorization_granted": False,
            "authorization_token_issued": False,
            "go_decision_granted": False,

            "owner_decision_invented": False,
            "owner_authenticated": False,
            "owner_stepped_up": False,
            "owner_admin_approval_granted": False,
            "dual_receipt_satisfied": False,
            "second_authority_review_granted": False,

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
            (str, bytes),
        ):
            raise AuthorizationGateError(
                "requested_operations must be a sequence"
            )

        operations: list[str] = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise AuthorizationGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_GATE_OPERATIONS:
                raise AuthorizationGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(
                normalized
            )

        if not operations:
            raise AuthorizationGateError(
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
            FROM vault_gp671_680_delivery_authorization_gate_events
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
                dict(
                    event_payload
                )
            )
        )

        material = {
            "gate_id": gate_id,
            "event_type": event_type,
            "event_payload": (
                normalized_payload
            ),
            "previous_event_hash": (
                previous_event_hash
            ),
            "created_at": created_at,
        }

        event_hash = _sha256_text(
            _canonical_json(
                material
            )
        )

        connection.execute(
            """
            INSERT INTO
                vault_gp671_680_delivery_authorization_gate_events (
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
    ) -> AuthorizationGateReceipt:
        return AuthorizationGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            delivery_authorized=False,
            recovery_authorization_granted=False,
            authorization_token_issued=False,
            go_decision_granted=False,

            immutable=True,
            append_only=True,
            idempotent_replay=(
                idempotent_replay
            ),
        )


__all__ = [
    "ALLOWED_GATE_OPERATIONS",
    "AuthorizationGateError",
    "AuthorizationGateIntegrityError",
    "AuthorizationGateReceipt",
    "CURRENT_RECOMMENDATION",
    "GATE_STATE",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationGateService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
