"""Archive Vault GP661-GP670.

Recovery Commit Owner Decision Tower Handoff Delivery Preparation Layer.

This layer prepares a sealed, Tower-directed handoff delivery package without
sending it.

Doctrine:
    Tower is the face and protocol authority.
    Vault is sealed memory.
    Teller is the workflow and request source.

Permitted flow:
    Teller -> Tower -> Vault -> Tower -> Teller

Current recommendation:
    NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_PREPARED_NOT_SENT

This service never:
    * delivers the Tower handoff
    * records Tower acceptance
    * creates or starts an acceptance/delivery session
    * authenticates or steps up the owner
    * invents owner selection or owner decision
    * grants owner/admin approval
    * satisfies dual receipt
    * grants second-authority review
    * opens an owner-decision recording gate
    * grants a GO decision
    * issues recovery authorization or an authorization token
    * activates scope, commit, execution, or recovery windows
    * issues a recovery commit command
    * restores data
    * mounts or writes production storage
    * connects an external storage provider
    * exposes raw paths, URLs, tokens, or raw materials
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


PACK_START = 661
PACK_END = 670

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_PREPARATION_LAYER"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_ACCEPTANCE_CLOSEOUT_SEALED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_PREPARED_NOT_SENT"
)

DELIVERY_STATE = "PREPARED_NOT_SENT"

TOWER_DESTINATION = "TOWER"

ALLOWED_ENVIRONMENTS = frozenset(
    {
        "STAGING",
        "PRODUCTION",
    }
)

ALLOWED_PREPARATION_OPERATIONS = frozenset(
    {
        "INTAKE_ACCEPTANCE_CLOSEOUT_REFERENCES",
        "BIND_TOWER_DELIVERY_TARGET",
        "EVALUATE_DELIVERY_PREREQUISITES",
        "REGISTER_IDEMPOTENCY_GUARD",
        "FREEZE_SAFE_PAYLOAD_ENVELOPE",
        "DRAFT_TOWER_HANDOFF_DELIVERY_PACKET",
        "DRAFT_TOWER_HANDOFF_DELIVERY_RECEIPT",
        "EVALUATE_DELIVERY_SAFETY_BLOCKERS",
        "SEAL_DELIVERY_PREPARATION_CHECKPOINT",
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
        "RECORD_OWNER_DECISION",
        "OPEN_OWNER_DECISION_RECORDING_GATE",
        "GRANT_GO_DECISION",
        "ISSUE_RECOVERY_AUTHORIZATION",
        "ISSUE_AUTHORIZATION_TOKEN",
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
    "owner_decision_recorded",
    "owner_decision_recording_gate_opened",
    "go_decision_granted",
    "recovery_authorization_issued",
    "authorization_token_issued",
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


class DeliveryPreparationError(ValueError):
    """Raised when a GP661-GP670 preparation request is unsafe."""


class DeliveryPreparationIntegrityError(RuntimeError):
    """Raised when sealed preparation data fails integrity verification."""


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(timespec="microseconds")


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


def _required_text(
    name: str,
    value: Any,
) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DeliveryPreparationError(
            f"{name} must be a non-empty string"
        )
    return value.strip()


def _normalize_json_object(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise DeliveryPreparationError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise DeliveryPreparationError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise DeliveryPreparationError(
            "safe_metadata must serialize to an object"
        )

    blocked = _find_blocked_keys(
        normalized
    )

    if blocked:
        raise DeliveryPreparationError(
            "safe_metadata contains prohibited raw, path, URL, token, "
            "secret, credential, or authorization fields: "
            + ", ".join(sorted(set(blocked)))
        )

    return normalized


def _find_blocked_keys(
    value: Any,
    *,
    location: str = "safe_metadata",
) -> list[str]:
    blocked: list[str] = []

    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            normalized_key = key_text.strip().lower()
            nested_location = f"{location}.{key_text}"

            if normalized_key in PROHIBITED_METADATA_KEYS:
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


def _safety_state() -> dict[str, bool]:
    return {
        field: False
        for field in SAFETY_STATE_FIELDS
    }


@dataclass(frozen=True)
class DeliveryPreparationReceipt:
    preparation_id: str
    preparation_hash: str
    recommendation: str
    delivery_state: str
    prepared: bool
    sent: bool
    immutable: bool
    append_only: bool
    idempotent_replay: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "preparation_id": self.preparation_id,
            "preparation_hash": self.preparation_hash,
            "recommendation": self.recommendation,
            "delivery_state": self.delivery_state,
            "prepared": self.prepared,
            "sent": self.sent,
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": self.idempotent_replay,
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryPreparationService:
    """Persistent GP661-GP670 Tower handoff delivery preparation service."""

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
                vault_gp661_670_delivery_preparations (
                    preparation_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,
                    acceptance_closeout_record_id TEXT NOT NULL,
                    acceptance_closeout_package_hash TEXT NOT NULL,

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,
                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    prerequisite_board_json TEXT NOT NULL,
                    payload_envelope_json TEXT NOT NULL,
                    delivery_packet_draft_json TEXT NOT NULL,
                    delivery_receipt_draft_json TEXT NOT NULL,
                    safety_blocker_board_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    preparation_payload_json TEXT NOT NULL,
                    preparation_hash TEXT NOT NULL UNIQUE,
                    predecessor_preparation_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_PREPARED_NOT_SENT'
                        ),

                    delivery_state TEXT NOT NULL
                        CHECK(
                            delivery_state = 'PREPARED_NOT_SENT'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp661_670_delivery_preparation_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preparation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(preparation_id)
                        REFERENCES
                        vault_gp661_670_delivery_preparations(
                            preparation_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp661_670_recovery_case
                ON vault_gp661_670_delivery_preparations(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp661_670_tower_authority
                ON vault_gp661_670_delivery_preparations(
                    tower_authority_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp661_670_event_chain
                ON vault_gp661_670_delivery_preparation_events(
                    preparation_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp661_670_preparation_no_update
                BEFORE UPDATE
                ON vault_gp661_670_delivery_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP661-GP670 delivery preparations are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp661_670_preparation_no_delete
                BEFORE DELETE
                ON vault_gp661_670_delivery_preparations
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP661-GP670 delivery preparations are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp661_670_event_no_update
                BEFORE UPDATE
                ON vault_gp661_670_delivery_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP661-GP670 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp661_670_event_no_delete
                BEFORE DELETE
                ON vault_gp661_670_delivery_preparation_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP661-GP670 events are append-only'
                    );
                END;
                """
            )

    def prepare_tower_handoff_delivery(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        acceptance_closeout_record_id: str,
        acceptance_closeout_package_hash: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> DeliveryPreparationReceipt:
        """Prepare and seal the GP661-GP670 package without sending it."""

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

        acceptance_closeout_package_hash = _required_text(
            "acceptance_closeout_package_hash",
            acceptance_closeout_package_hash,
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
            raise DeliveryPreparationError(
                "target_environment must be STAGING or PRODUCTION"
            )

        operations = self._normalize_operations(
            requested_operations
        )

        metadata = _normalize_json_object(
            safe_metadata
        )

        identity = {
            "layer_id": LAYER_ID,
            "idempotency_key": idempotency_key,
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "acceptance_closeout_record_id": (
                acceptance_closeout_record_id
            ),
            "acceptance_closeout_package_hash": (
                acceptance_closeout_package_hash
            ),
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        preparation_id = (
            "vault-gp661-670-"
            + _sha256_text(
                _canonical_json(identity)
            )[:24]
        )

        # GP661 — Tower Handoff Delivery Preparation Shell
        preparation_shell = {
            "pack": "GP661",
            "preparation_id": preparation_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "prior_recommendation": PRIOR_RECOMMENDATION,
            "recommendation": CURRENT_RECOMMENDATION,
            "delivery_state": DELIVERY_STATE,
            "prepared": True,
            "sent": False,
        }

        # GP662 — Acceptance Closeout Package Intake Board
        acceptance_intake_board = {
            "pack": "GP662",
            "acceptance_closeout_record_id": (
                acceptance_closeout_record_id
            ),
            "acceptance_closeout_package_hash": (
                acceptance_closeout_package_hash
            ),
            "intake_mode": "REFERENCE_AND_HASH_ONLY",
            "raw_material_received": False,
            "raw_path_received": False,
            "raw_url_received": False,
            "raw_token_received": False,
            "acceptance_decision_invented": False,
        }

        # GP663 — Tower Delivery Target Contract Board
        tower_target_board = {
            "pack": "GP663",
            "destination": TOWER_DESTINATION,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "target_environment": target_environment,
            "teller_direct_vault_allowed": False,
            "resident_direct_vault_allowed": False,
            "vendor_direct_vault_allowed": False,
            "employee_direct_vault_allowed": False,
            "customer_direct_vault_allowed": False,
            "public_direct_vault_allowed": False,
        }

        # GP664 — Tower Delivery Authorization Prerequisite Board
        prerequisite_board = {
            "pack": "GP664",
            "acceptance_closeout_reference_present": True,
            "acceptance_closeout_hash_present": True,
            "tower_authority_reference_present": True,
            "tower_delivery_target_present": True,
            "owner_decision_reference_present": True,
            "authorization_granted": False,
            "authorization_token_issued": False,
            "go_decision_granted": False,
            "delivery_authorized": False,
            "prerequisite_state": (
                "PREPARATION_PREREQUISITES_RECORDED_"
                "AUTHORIZATION_NOT_GRANTED"
            ),
        }

        # GP665 — Delivery Idempotency and Replay Protection Board
        replay_board = {
            "pack": "GP665",
            "idempotency_key": idempotency_key,
            "deterministic_preparation_id": preparation_id,
            "duplicate_send_allowed": False,
            "replay_send_allowed": False,
            "replay_authorization_allowed": False,
            "idempotent_exact_replay_only": True,
        }

        # GP666 — Tower Delivery Payload Envelope Freeze Board
        payload_envelope = {
            "pack": "GP666",
            "envelope_type": (
                "TOWER_HANDOFF_DELIVERY_PREPARATION_ENVELOPE"
            ),
            "envelope_version": 1,
            "destination": TOWER_DESTINATION,
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "acceptance_closeout_record_id": (
                acceptance_closeout_record_id
            ),
            "acceptance_closeout_package_hash": (
                acceptance_closeout_package_hash
            ),
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "target_environment": target_environment,
            "safe_metadata": metadata,
            "operations": operations,
            "raw_material_included": False,
            "raw_path_included": False,
            "raw_url_included": False,
            "raw_token_included": False,
            "authorization_token_included": False,
            "provider_credential_included": False,
            "frozen_for_preparation": True,
            "sent": False,
        }

        envelope_hash = _sha256_text(
            _canonical_json(payload_envelope)
        )

        payload_envelope["envelope_hash"] = envelope_hash

        # GP667 — Tower Handoff Delivery Packet Draft Board
        delivery_packet_draft = {
            "pack": "GP667",
            "packet_type": (
                "TOWER_HANDOFF_DELIVERY_PACKET_DRAFT"
            ),
            "packet_status": "DRAFT_NOT_SENT",
            "preparation_id": preparation_id,
            "payload_envelope_hash": envelope_hash,
            "destination": TOWER_DESTINATION,
            "tower_delivery_target_id": (
                tower_delivery_target_id
            ),
            "delivery_attempted": False,
            "delivery_performed": False,
            "tower_acceptance_performed": False,
        }

        packet_draft_hash = _sha256_text(
            _canonical_json(delivery_packet_draft)
        )

        delivery_packet_draft[
            "packet_draft_hash"
        ] = packet_draft_hash

        # GP668 — Tower Handoff Delivery Receipt Draft Ledger
        delivery_receipt_draft = {
            "pack": "GP668",
            "receipt_type": (
                "TOWER_HANDOFF_DELIVERY_RECEIPT_DRAFT"
            ),
            "receipt_status": "DRAFT_NO_DELIVERY_EVENT",
            "preparation_id": preparation_id,
            "packet_draft_hash": packet_draft_hash,
            "delivery_event_id": None,
            "tower_acceptance_event_id": None,
            "sent": False,
            "accepted": False,
            "receipt_finalized": False,
        }

        receipt_draft_hash = _sha256_text(
            _canonical_json(delivery_receipt_draft)
        )

        delivery_receipt_draft[
            "receipt_draft_hash"
        ] = receipt_draft_hash

        # GP669 — Tower Handoff Delivery Safety Blocker Board
        safety_state = _safety_state()

        safety_blocker_board = {
            "pack": "GP669",
            "recommendation": CURRENT_RECOMMENDATION,
            "delivery_blocked": True,
            "safety_state": safety_state,
            "active_blockers": [
                "NO_DELIVERY_AUTHORIZATION",
                "NO_AUTHORIZATION_TOKEN",
                "NO_GO_DECISION",
                "NO_OWNER_DECISION_INVENTION",
                "NO_DELIVERY_SESSION",
                "NO_LIVE_RECOVERY_EXECUTION",
                "NO_RECOVERY_COMMIT_COMMAND",
                "NO_PROVIDER_CONNECTION",
                "NO_PRODUCTION_STORAGE_WRITE",
            ],
        }

        # GP670 — Preparation Readiness Checkpoint
        checkpoint = {
            "pack": "GP670",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_PREPARATION_READINESS"
            ),
            "preparation_id": preparation_id,
            "prior_pack_range": "GP651-GP660",
            "current_pack_range": "GP661-GP670",
            "recommendation": CURRENT_RECOMMENDATION,
            "delivery_state": DELIVERY_STATE,
            "prepared": True,
            "sent": False,
            "delivery_authorized": False,
            "go_decision_granted": False,
            "authorization_token_issued": False,
            "recovery_commit_command_issued": False,
            "restore_occurred": False,
            "production_write_occurred": False,
            "provider_connection_occurred": False,
            "raw_material_exposed": False,
            "destructive_action_occurred": False,
            "next_gate": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_GATE"
            ),
        }

        preparation_payload = {
            "gp661_preparation_shell": preparation_shell,
            "gp662_acceptance_intake_board": (
                acceptance_intake_board
            ),
            "gp663_tower_target_board": tower_target_board,
            "gp664_prerequisite_board": prerequisite_board,
            "gp665_replay_board": replay_board,
            "gp666_payload_envelope": payload_envelope,
            "gp667_delivery_packet_draft": (
                delivery_packet_draft
            ),
            "gp668_delivery_receipt_draft": (
                delivery_receipt_draft
            ),
            "gp669_safety_blocker_board": (
                safety_blocker_board
            ),
            "gp670_checkpoint": checkpoint,
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
                FROM vault_gp661_670_delivery_preparations
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
                    raise DeliveryPreparationError(
                        "idempotency_key already exists with "
                        "different immutable preparation inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT preparation_hash
                FROM vault_gp661_670_delivery_preparations
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
                INSERT INTO vault_gp661_670_delivery_preparations (
                    preparation_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    acceptance_closeout_record_id,
                    acceptance_closeout_package_hash,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    destination,
                    prerequisite_board_json,
                    payload_envelope_json,
                    delivery_packet_draft_json,
                    delivery_receipt_draft_json,
                    safety_blocker_board_json,
                    checkpoint_json,
                    preparation_payload_json,
                    preparation_hash,
                    predecessor_preparation_hash,
                    recommendation,
                    delivery_state,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    preparation_id,
                    idempotency_key,
                    recovery_case_id,
                    owner_decision_record_id,
                    acceptance_closeout_record_id,
                    acceptance_closeout_package_hash,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(prerequisite_board),
                    _canonical_json(payload_envelope),
                    _canonical_json(delivery_packet_draft),
                    _canonical_json(delivery_receipt_draft),
                    _canonical_json(safety_blocker_board),
                    _canonical_json(checkpoint),
                    preparation_payload_json,
                    preparation_hash,
                    predecessor_hash,
                    CURRENT_RECOMMENDATION,
                    DELIVERY_STATE,
                    created_at,
                ),
            )

            self._append_event(
                connection,
                preparation_id=preparation_id,
                event_type=(
                    "GP661_670_TOWER_HANDOFF_DELIVERY_"
                    "PREPARATION_SEALED"
                ),
                event_payload={
                    "preparation_hash": preparation_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "delivery_state": DELIVERY_STATE,
                    "prepared": True,
                    "sent": False,
                    "delivery_authorized": False,
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
                FROM vault_gp661_670_delivery_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

            if row is None:
                raise DeliveryPreparationIntegrityError(
                    "preparation record failed to persist"
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
                FROM vault_gp661_670_delivery_preparations
                WHERE preparation_id = ?
                """,
                (preparation_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown preparation: {preparation_id}"
            )

        result = dict(row)

        json_columns = (
            "prerequisite_board_json",
            "payload_envelope_json",
            "delivery_packet_draft_json",
            "delivery_receipt_draft_json",
            "safety_blocker_board_json",
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
                FROM vault_gp661_670_delivery_preparation_events
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

        expected_hash = _sha256_text(
            payload_json
        )

        if expected_hash != record["preparation_hash"]:
            raise DeliveryPreparationIntegrityError(
                "preparation payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise DeliveryPreparationIntegrityError(
                "delivery destination is not Tower"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise DeliveryPreparationIntegrityError(
                "recommendation boundary mismatch"
            )

        if record["delivery_state"] != DELIVERY_STATE:
            raise DeliveryPreparationIntegrityError(
                "delivery state boundary mismatch"
            )

        safety_state = record[
            "safety_blocker_board"
        ]["safety_state"]

        missing_safety_fields = sorted(
            set(SAFETY_STATE_FIELDS)
            - set(safety_state)
        )

        if missing_safety_fields:
            raise DeliveryPreparationIntegrityError(
                "missing safety state fields: "
                + ", ".join(missing_safety_fields)
            )

        unsafe_true = sorted(
            field
            for field, value in safety_state.items()
            if value is True
        )

        if unsafe_true:
            raise DeliveryPreparationIntegrityError(
                "unsafe completed actions detected: "
                + ", ".join(unsafe_true)
            )

        packet = record[
            "delivery_packet_draft"
        ]

        receipt = record[
            "delivery_receipt_draft"
        ]

        checkpoint = record["checkpoint"]

        if packet["packet_status"] != "DRAFT_NOT_SENT":
            raise DeliveryPreparationIntegrityError(
                "delivery packet escaped draft-not-sent state"
            )

        if receipt["receipt_finalized"] is not False:
            raise DeliveryPreparationIntegrityError(
                "delivery receipt draft was finalized"
            )

        if checkpoint["sent"] is not False:
            raise DeliveryPreparationIntegrityError(
                "GP670 checkpoint indicates a sent handoff"
            )

        events = self.list_events(
            preparation_id
        )

        if not events:
            raise DeliveryPreparationIntegrityError(
                "preparation has no append-only events"
            )

        previous_hash = None

        for event in events:
            if event["previous_event_hash"] != previous_hash:
                raise DeliveryPreparationIntegrityError(
                    "event predecessor hash mismatch"
                )

            material = {
                "preparation_id": event["preparation_id"],
                "event_type": event["event_type"],
                "event_payload": event["event_payload"],
                "previous_event_hash": (
                    event["previous_event_hash"]
                ),
                "created_at": event["created_at"],
            }

            expected_event_hash = _sha256_text(
                _canonical_json(material)
            )

            if expected_event_hash != event["event_hash"]:
                raise DeliveryPreparationIntegrityError(
                    "event hash mismatch"
                )

            previous_hash = event["event_hash"]

        return {
            "pack_range": "GP661-GP670",
            "preparation_id": preparation_id,
            "preparation_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),
            "tower_destination_only": True,
            "prepared": True,
            "sent": False,
            "delivery_authorized": False,
            "authorization_token_issued": False,
            "go_decision_granted": False,
            "recovery_commit_command_issued": False,
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
                ALLOWED_PREPARATION_OPERATIONS
            )

        if isinstance(
            requested_operations,
            (str, bytes),
        ):
            raise DeliveryPreparationError(
                "requested_operations must be a sequence"
            )

        operations = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise DeliveryPreparationError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_PREPARATION_OPERATIONS:
                raise DeliveryPreparationError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise DeliveryPreparationError(
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
            FROM vault_gp661_670_delivery_preparation_events
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
                vault_gp661_670_delivery_preparation_events (
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
    ) -> DeliveryPreparationReceipt:
        return DeliveryPreparationReceipt(
            preparation_id=row["preparation_id"],
            preparation_hash=row["preparation_hash"],
            recommendation=row["recommendation"],
            delivery_state=row["delivery_state"],
            prepared=True,
            sent=False,
            immutable=True,
            append_only=True,
            idempotent_replay=idempotent_replay,
        )


__all__ = [
    "ALLOWED_PREPARATION_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "DELIVERY_STATE",
    "DeliveryPreparationError",
    "DeliveryPreparationIntegrityError",
    "DeliveryPreparationReceipt",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryPreparationService",
    "SAFETY_STATE_FIELDS",
    "TOWER_DESTINATION",
]
