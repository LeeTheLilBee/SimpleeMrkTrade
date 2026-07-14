"""Archive Vault GP731-GP740.

Recovery Commit Owner Decision Tower Handoff Delivery Authorization Decision
Recording Owner Session Creation Authorization Gate.

This layer seals a fail-closed authorization gate around any future Tower
owner-session creation.

The gate remains closed. No authorization is granted.

Tower remains the protocol, identity, step-up, and session authority.

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


PACK_START = 731
PACK_END = 740

LAYER_ID = (
    "RECOVERY_COMMIT_OWNER_DECISION_"
    "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
    "DECISION_RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_GATE"
)

PRIOR_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_PREPARED_NOT_CREATED"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_"
    "AUTHORIZATION_DECISION_RECORDING_"
    "OWNER_SESSION_CREATION_AUTHORIZATION_GATE_SEALED"
)

GATE_STATE = (
    "OWNER_SESSION_CREATION_AUTHORIZATION_GATE_"
    "SEALED_AUTHORIZATION_NOT_GRANTED"
)

REQUIRED_PREPARATION_STATE = (
    "OWNER_SESSION_PREPARATION_SEALED_"
    "SESSION_NOT_CREATED"
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

ALLOWED_GATE_OPERATIONS = frozenset(
    {
        "INTAKE_OWNER_SESSION_PREPARATION_REFERENCE",
        "VERIFY_OWNER_SESSION_PREPARATION_STATE",
        "VERIFY_TOWER_SESSION_REQUEST_PREPARED",
        "VERIFY_SESSION_SCOPE_BINDING_REQUIREMENTS",
        "VERIFY_SESSION_LIFETIME_REQUIREMENTS",
        "VERIFY_SESSION_REPLAY_PROTECTION_REQUIREMENTS",
        "VERIFY_OWNER_AUTHENTICATION_REQUIREMENT",
        "VERIFY_OWNER_STEP_UP_REQUIREMENT",
        "EVALUATE_OWNER_SESSION_CREATION_AUTHORIZATION_BLOCKERS",
        "SEAL_OWNER_SESSION_CREATION_AUTHORIZATION_GATE",
    }
)

PROHIBITED_OPERATIONS = frozenset(
    {
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
    "owner_session_creation_authorized",
    "tower_owner_session_creation_authorized",
    "owner_session_creation_authorization_granted",
    "tower_owner_session_creation_authorization_granted",
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


class OwnerSessionCreationAuthorizationGateError(ValueError):
    """Raised when GP731-GP740 authorization-gate input is unsafe."""


class OwnerSessionCreationAuthorizationGateIntegrityError(RuntimeError):
    """Raised when GP731-GP740 sealed gate evidence fails verification."""


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
        raise OwnerSessionCreationAuthorizationGateError(
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
        raise OwnerSessionCreationAuthorizationGateError(
            "safe_metadata must be a mapping"
        )

    try:
        normalized = json.loads(
            _canonical_json(dict(value))
        )
    except (TypeError, ValueError) as exc:
        raise OwnerSessionCreationAuthorizationGateError(
            "safe_metadata must be JSON serializable"
        ) from exc

    if not isinstance(normalized, dict):
        raise OwnerSessionCreationAuthorizationGateError(
            "safe_metadata must serialize to an object"
        )

    blocked = sorted(
        set(
            _find_blocked_keys(normalized)
        )
    )

    if blocked:
        raise OwnerSessionCreationAuthorizationGateError(
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
class OwnerSessionCreationAuthorizationGateReceipt:
    gate_id: str
    gate_hash: str
    recommendation: str
    gate_state: str

    gate_sealed: bool
    authorization_granted: bool
    owner_session_creation_authorized: bool
    tower_owner_session_creation_authorized: bool

    owner_session_created: bool
    owner_session_started: bool
    tower_owner_session_created: bool
    tower_owner_session_started: bool

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
            "authorization_granted": self.authorization_granted,
            "owner_session_creation_authorized": (
                self.owner_session_creation_authorized
            ),
            "tower_owner_session_creation_authorized": (
                self.tower_owner_session_creation_authorized
            ),
            "owner_session_created": self.owner_session_created,
            "owner_session_started": self.owner_session_started,
            "tower_owner_session_created": (
                self.tower_owner_session_created
            ),
            "tower_owner_session_started": (
                self.tower_owner_session_started
            ),
            "recording_gate_open": self.recording_gate_open,
            "owner_decision_recorded": self.owner_decision_recorded,
            "immutable": self.immutable,
            "append_only": self.append_only,
            "idempotent_replay": self.idempotent_replay,
        }


class RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationGateService:
    """Persistent GP731-GP740 fail-closed creation authorization gate."""

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

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS
                vault_gp731_740_owner_session_creation_authorization_gates (
                    gate_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,

                    recovery_case_id TEXT NOT NULL,
                    owner_decision_record_id TEXT NOT NULL,

                    owner_session_preparation_id TEXT NOT NULL,
                    owner_session_preparation_hash TEXT NOT NULL,
                    owner_session_preparation_state TEXT NOT NULL
                        CHECK(
                            owner_session_preparation_state =
                            'OWNER_SESSION_PREPARATION_SEALED_SESSION_NOT_CREATED'
                        ),

                    tower_authority_id TEXT NOT NULL,
                    tower_delivery_target_id TEXT NOT NULL,
                    target_environment TEXT NOT NULL,

                    destination TEXT NOT NULL
                        CHECK(destination = 'TOWER'),

                    gate_shell_json TEXT NOT NULL,
                    preparation_lineage_gate_json TEXT NOT NULL,
                    tower_session_request_gate_json TEXT NOT NULL,
                    scope_binding_authorization_gate_json TEXT NOT NULL,
                    lifetime_authorization_gate_json TEXT NOT NULL,
                    replay_protection_authorization_gate_json TEXT NOT NULL,
                    owner_authentication_authorization_gate_json TEXT NOT NULL,
                    owner_step_up_authorization_gate_json TEXT NOT NULL,
                    authorization_prerequisite_matrix_json TEXT NOT NULL,
                    checkpoint_json TEXT NOT NULL,

                    gate_payload_json TEXT NOT NULL,
                    gate_hash TEXT NOT NULL UNIQUE,
                    predecessor_gate_hash TEXT,

                    recommendation TEXT NOT NULL
                        CHECK(
                            recommendation =
                            'NO_GO_HOLD_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_GATE_SEALED'
                        ),

                    gate_state TEXT NOT NULL
                        CHECK(
                            gate_state =
                            'OWNER_SESSION_CREATION_AUTHORIZATION_GATE_SEALED_AUTHORIZATION_NOT_GRANTED'
                        ),

                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS
                vault_gp731_740_owner_session_creation_authorization_gate_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_payload_json TEXT NOT NULL,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(gate_id)
                        REFERENCES
                        vault_gp731_740_owner_session_creation_authorization_gates(
                            gate_id
                        )
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp731_740_recovery_case
                ON vault_gp731_740_owner_session_creation_authorization_gates(
                    recovery_case_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp731_740_session_preparation
                ON vault_gp731_740_owner_session_creation_authorization_gates(
                    owner_session_preparation_id
                );

                CREATE INDEX IF NOT EXISTS
                idx_vault_gp731_740_event_chain
                ON vault_gp731_740_owner_session_creation_authorization_gate_events(
                    gate_id,
                    event_id
                );

                CREATE TRIGGER IF NOT EXISTS
                vault_gp731_740_gate_no_update
                BEFORE UPDATE
                ON vault_gp731_740_owner_session_creation_authorization_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP731-GP740 owner session creation authorization gates are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp731_740_gate_no_delete
                BEFORE DELETE
                ON vault_gp731_740_owner_session_creation_authorization_gates
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP731-GP740 owner session creation authorization gates are append-only'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp731_740_event_no_update
                BEFORE UPDATE
                ON vault_gp731_740_owner_session_creation_authorization_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP731-GP740 events are immutable'
                    );
                END;

                CREATE TRIGGER IF NOT EXISTS
                vault_gp731_740_event_no_delete
                BEFORE DELETE
                ON vault_gp731_740_owner_session_creation_authorization_gate_events
                BEGIN
                    SELECT RAISE(
                        ABORT,
                        'GP731-GP740 events are append-only'
                    );
                END;
                """
            )

    def seal_owner_session_creation_authorization_gate(
        self,
        *,
        idempotency_key: str,
        recovery_case_id: str,
        owner_decision_record_id: str,
        owner_session_preparation_id: str,
        owner_session_preparation_hash: str,
        owner_session_preparation_state: str,
        tower_authority_id: str,
        tower_delivery_target_id: str,
        target_environment: str,
        requested_operations: Sequence[str] | None = None,
        safe_metadata: Mapping[str, Any] | None = None,
    ) -> OwnerSessionCreationAuthorizationGateReceipt:
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

        owner_session_preparation_id = _required_text(
            "owner_session_preparation_id",
            owner_session_preparation_id,
        )

        owner_session_preparation_hash = _required_text(
            "owner_session_preparation_hash",
            owner_session_preparation_hash,
        )

        owner_session_preparation_state = _required_text(
            "owner_session_preparation_state",
            owner_session_preparation_state,
        ).upper()

        if (
            owner_session_preparation_state
            != REQUIRED_PREPARATION_STATE
        ):
            raise OwnerSessionCreationAuthorizationGateError(
                "owner_session_preparation_state must preserve "
                "OWNER_SESSION_PREPARATION_SEALED_SESSION_NOT_CREATED"
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
            raise OwnerSessionCreationAuthorizationGateError(
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
            "owner_session_preparation_id": (
                owner_session_preparation_id
            ),
            "owner_session_preparation_hash": (
                owner_session_preparation_hash
            ),
            "owner_session_preparation_state": (
                owner_session_preparation_state
            ),
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "target_environment": target_environment,
            "destination": TOWER_DESTINATION,
        }

        gate_id = (
            "vault-gp731-740-"
            + _sha256_text(
                _canonical_json(identity)
            )[:24]
        )

        # GP731 — Owner Session Creation Authorization Gate Shell
        gate_shell = {
            "pack": "GP731",
            "gate_id": gate_id,
            "layer_id": LAYER_ID,
            "recovery_case_id": recovery_case_id,
            "prior_recommendation": PRIOR_RECOMMENDATION,
            "recommendation": CURRENT_RECOMMENDATION,
            "gate_state": GATE_STATE,
            "gate_sealed": True,
            "authorization_granted": False,
            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,
        }

        # GP732 — Owner Session Preparation Lineage Gate
        preparation_lineage_gate = {
            "pack": "GP732",
            "owner_session_preparation_id": (
                owner_session_preparation_id
            ),
            "owner_session_preparation_hash": (
                owner_session_preparation_hash
            ),
            "owner_session_preparation_state": (
                owner_session_preparation_state
            ),
            "required_state": REQUIRED_PREPARATION_STATE,
            "preparation_reference_present": True,
            "preparation_hash_present": True,
            "tower_session_request_prepared_in_lineage": True,
            "tower_session_request_sent_in_lineage": False,
            "owner_session_creation_authorized_in_lineage": False,
            "owner_session_created_in_lineage": False,
            "owner_session_started_in_lineage": False,
        }

        # GP733 — Tower Session Request Authorization Gate
        tower_session_request_gate = {
            "pack": "GP733",
            "session_type": SESSION_TYPE,
            "session_purpose": SESSION_PURPOSE,
            "destination": TOWER_DESTINATION,
            "session_authority": TOWER_DESTINATION,
            "tower_authority_id": tower_authority_id,
            "tower_delivery_target_id": tower_delivery_target_id,
            "request_prepared": True,
            "request_sent": False,
            "request_delivered": False,
            "request_accepted": False,
            "request_authorized_for_creation": False,
            "session_creation_authorized": False,
        }

        # GP734 — Scope Binding Authorization Gate
        scope_binding_authorization_gate = {
            "pack": "GP734",
            "recovery_case_id": recovery_case_id,
            "owner_decision_record_id": owner_decision_record_id,
            "target_environment": target_environment,
            "recovery_case_binding_required": True,
            "owner_decision_binding_required": True,
            "environment_binding_required": True,
            "tower_authority_binding_required": True,
            "delivery_target_binding_required": True,
            "binding_receipt_required": True,
            "binding_receipt_present": False,
            "bindings_verified": False,
            "scope_binding_authorization_satisfied": False,
            "creation_authorization_blocked": True,
        }

        # GP735 — Session Lifetime Authorization Gate
        lifetime_authorization_gate = {
            "pack": "GP735",
            "issued_at_required": True,
            "not_before_required": True,
            "expires_at_required": True,
            "short_lived_session_required": True,
            "indefinite_session_allowed": False,
            "expired_session_rejected": True,
            "premature_session_rejected": True,
            "missing_expiry_rejected": True,
            "lifetime_receipt_required": True,
            "lifetime_receipt_present": False,
            "lifetime_verified": False,
            "lifetime_authorization_satisfied": False,
            "creation_authorization_blocked": True,
        }

        # GP736 — Session Replay Protection Authorization Gate
        replay_protection_authorization_gate = {
            "pack": "GP736",
            "nonce_reference_required": True,
            "single_active_use_boundary_required": True,
            "replay_detection_required": True,
            "duplicate_use_rejected": True,
            "consumed_session_reuse_rejected": True,
            "cross_case_replay_rejected": True,
            "cross_owner_decision_replay_rejected": True,
            "cross_environment_replay_rejected": True,
            "replay_protection_receipt_required": True,
            "replay_protection_receipt_present": False,
            "replay_protection_verified": False,
            "replay_protection_authorization_satisfied": False,
            "creation_authorization_blocked": True,
        }

        # GP737 — Owner Authentication Authorization Gate
        owner_authentication_authorization_gate = {
            "pack": "GP737",
            "tower_authentication_required": True,
            "authenticated_owner_identity_required": True,
            "owner_identity_binding_required": True,
            "anonymous_session_allowed": False,
            "vault_authentication_allowed": False,
            "teller_authentication_authority_allowed": False,
            "authentication_receipt_required": True,
            "authentication_receipt_present": False,
            "owner_authenticated": False,
            "authentication_verified": False,
            "authentication_authorization_satisfied": False,
            "creation_authorization_blocked": True,
        }

        # GP738 — Owner Step-Up Authorization Gate
        owner_step_up_authorization_gate = {
            "pack": "GP738",
            "tower_step_up_required": True,
            "purpose_bound_step_up_required": True,
            "recovery_case_bound_step_up_required": True,
            "owner_decision_bound_step_up_required": True,
            "fresh_step_up_required": True,
            "vault_step_up_allowed": False,
            "teller_step_up_authority_allowed": False,
            "step_up_receipt_required": True,
            "step_up_receipt_present": False,
            "owner_stepped_up": False,
            "step_up_verified": False,
            "step_up_authorization_satisfied": False,
            "creation_authorization_blocked": True,
        }

        # GP739 — Session Creation Authorization Prerequisite Matrix
        authorization_prerequisite_matrix = {
            "pack": "GP739",
            "preparation_reference_present": True,
            "preparation_hash_present": True,
            "tower_session_request_prepared": True,

            "scope_binding_receipt_present": False,
            "scope_bindings_verified": False,

            "lifetime_receipt_present": False,
            "session_lifetime_verified": False,

            "replay_protection_receipt_present": False,
            "session_replay_protection_verified": False,

            "authentication_receipt_present": False,
            "owner_authenticated": False,
            "owner_authentication_verified": False,

            "step_up_receipt_present": False,
            "owner_stepped_up": False,
            "owner_step_up_verified": False,

            "owner_session_creation_authorization_granted": False,
            "tower_owner_session_creation_authorization_granted": False,

            "owner_session_creation_authorized": False,
            "tower_owner_session_creation_authorized": False,

            "owner_session_created": False,
            "owner_session_started": False,
            "tower_owner_session_created": False,
            "tower_owner_session_started": False,

            "all_creation_authorization_prerequisites_satisfied": False,
            "session_creation_authorization_may_be_granted": False,
            "session_creation_may_proceed": False,
            "recording_gate_may_open": False,
        }

        # GP740 — Owner Session Creation Authorization Gate Checkpoint
        safety_state = _false_safety_state()

        checkpoint = {
            "pack": "GP740",
            "checkpoint_type": (
                "TOWER_HANDOFF_DELIVERY_AUTHORIZATION_DECISION_"
                "RECORDING_OWNER_SESSION_CREATION_AUTHORIZATION_GATE_READINESS"
            ),
            "gate_id": gate_id,
            "prior_pack_range": "GP721-GP730",
            "current_pack_range": "GP731-GP740",
            "recommendation": CURRENT_RECOMMENDATION,
            "gate_state": GATE_STATE,

            "gate_sealed": True,
            "authorization_granted": False,

            "tower_session_request_prepared": True,
            "tower_session_request_sent": False,
            "tower_session_request_delivered": False,
            "tower_session_request_accepted": False,

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

            "session_binding_receipt_present": False,
            "session_bindings_verified": False,

            "session_lifetime_receipt_present": False,
            "session_lifetime_verified": False,

            "session_replay_protection_receipt_present": False,
            "session_replay_protection_verified": False,

            "owner_authentication_receipt_present": False,
            "owner_authenticated": False,
            "owner_authentication_verified": False,

            "owner_step_up_receipt_present": False,
            "owner_stepped_up": False,
            "owner_step_up_verified": False,

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
                "PREPARATION_LAYER"
            ),
        }

        gate_payload = {
            "gp731_gate_shell": gate_shell,
            "gp732_preparation_lineage_gate": preparation_lineage_gate,
            "gp733_tower_session_request_gate": tower_session_request_gate,
            "gp734_scope_binding_authorization_gate": (
                scope_binding_authorization_gate
            ),
            "gp735_lifetime_authorization_gate": (
                lifetime_authorization_gate
            ),
            "gp736_replay_protection_authorization_gate": (
                replay_protection_authorization_gate
            ),
            "gp737_owner_authentication_authorization_gate": (
                owner_authentication_authorization_gate
            ),
            "gp738_owner_step_up_authorization_gate": (
                owner_step_up_authorization_gate
            ),
            "gp739_authorization_prerequisite_matrix": (
                authorization_prerequisite_matrix
            ),
            "gp740_checkpoint": checkpoint,
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
                FROM vault_gp731_740_owner_session_creation_authorization_gates
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

            if existing is not None:
                if (
                    existing["gate_payload_json"] != gate_payload_json
                    or existing["gate_hash"] != gate_hash
                ):
                    raise OwnerSessionCreationAuthorizationGateError(
                        "idempotency_key already exists with different "
                        "immutable owner-session-creation-authorization-gate inputs"
                    )

                return self._receipt_from_row(
                    existing,
                    idempotent_replay=True,
                )

            predecessor = connection.execute(
                """
                SELECT gate_hash
                FROM vault_gp731_740_owner_session_creation_authorization_gates
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
                    vault_gp731_740_owner_session_creation_authorization_gates (
                        gate_id,
                        idempotency_key,
                        recovery_case_id,
                        owner_decision_record_id,
                        owner_session_preparation_id,
                        owner_session_preparation_hash,
                        owner_session_preparation_state,
                        tower_authority_id,
                        tower_delivery_target_id,
                        target_environment,
                        destination,
                        gate_shell_json,
                        preparation_lineage_gate_json,
                        tower_session_request_gate_json,
                        scope_binding_authorization_gate_json,
                        lifetime_authorization_gate_json,
                        replay_protection_authorization_gate_json,
                        owner_authentication_authorization_gate_json,
                        owner_step_up_authorization_gate_json,
                        authorization_prerequisite_matrix_json,
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
                    owner_session_preparation_id,
                    owner_session_preparation_hash,
                    owner_session_preparation_state,
                    tower_authority_id,
                    tower_delivery_target_id,
                    target_environment,
                    TOWER_DESTINATION,
                    _canonical_json(gate_shell),
                    _canonical_json(preparation_lineage_gate),
                    _canonical_json(tower_session_request_gate),
                    _canonical_json(scope_binding_authorization_gate),
                    _canonical_json(lifetime_authorization_gate),
                    _canonical_json(
                        replay_protection_authorization_gate
                    ),
                    _canonical_json(
                        owner_authentication_authorization_gate
                    ),
                    _canonical_json(owner_step_up_authorization_gate),
                    _canonical_json(authorization_prerequisite_matrix),
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
                    "GP731_740_TOWER_HANDOFF_DELIVERY_AUTHORIZATION_"
                    "DECISION_RECORDING_OWNER_SESSION_CREATION_"
                    "AUTHORIZATION_GATE_SEALED"
                ),
                event_payload={
                    "gate_hash": gate_hash,
                    "recommendation": CURRENT_RECOMMENDATION,
                    "gate_state": GATE_STATE,
                    "gate_sealed": True,
                    "authorization_granted": False,
                    "owner_session_creation_authorized": False,
                    "tower_owner_session_creation_authorized": False,
                    "owner_session_created": False,
                    "owner_session_started": False,
                    "tower_owner_session_created": False,
                    "tower_owner_session_started": False,
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
                FROM vault_gp731_740_owner_session_creation_authorization_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

            if row is None:
                raise OwnerSessionCreationAuthorizationGateIntegrityError(
                    "owner session creation authorization gate "
                    "failed to persist"
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
                FROM vault_gp731_740_owner_session_creation_authorization_gates
                WHERE gate_id = ?
                """,
                (gate_id,),
            ).fetchone()

        if row is None:
            raise KeyError(
                f"Unknown GP731-GP740 gate: {gate_id}"
            )

        result = dict(row)

        json_columns = (
            "gate_shell_json",
            "preparation_lineage_gate_json",
            "tower_session_request_gate_json",
            "scope_binding_authorization_gate_json",
            "lifetime_authorization_gate_json",
            "replay_protection_authorization_gate_json",
            "owner_authentication_authorization_gate_json",
            "owner_step_up_authorization_gate_json",
            "authorization_prerequisite_matrix_json",
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
                FROM vault_gp731_740_owner_session_creation_authorization_gate_events
                WHERE gate_id = ?
                ORDER BY event_id ASC
                """,
                (gate_id,),
            ).fetchall()

        events: list[dict[str, Any]] = []

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
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session creation authorization gate "
                "payload hash mismatch"
            )

        if record["destination"] != TOWER_DESTINATION:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session creation authorization gate "
                "destination is not Tower"
            )

        if (
            record["owner_session_preparation_state"]
            != REQUIRED_PREPARATION_STATE
        ):
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session preparation lineage mismatch"
            )

        if record["recommendation"] != CURRENT_RECOMMENDATION:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session creation authorization gate "
                "recommendation mismatch"
            )

        if record["gate_state"] != GATE_STATE:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session creation authorization gate state mismatch"
            )

        shell = record["gate_shell"]

        forbidden_shell_true = (
            "authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
        )

        invalid_shell = [
            field
            for field in forbidden_shell_true
            if shell[field] is True
        ]

        if invalid_shell:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "unsafe gate shell state: "
                + ", ".join(invalid_shell)
            )

        request_gate = record["tower_session_request_gate"]

        if request_gate["request_prepared"] is not True:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "Tower session request preparation lineage missing"
            )

        forbidden_request_true = (
            "request_sent",
            "request_delivered",
            "request_accepted",
            "request_authorized_for_creation",
            "session_creation_authorized",
        )

        invalid_request = [
            field
            for field in forbidden_request_true
            if request_gate[field] is True
        ]

        if invalid_request:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "unsafe Tower session request gate state: "
                + ", ".join(invalid_request)
            )

        gate_boards = (
            record["scope_binding_authorization_gate"],
            record["lifetime_authorization_gate"],
            record["replay_protection_authorization_gate"],
            record["owner_authentication_authorization_gate"],
            record["owner_step_up_authorization_gate"],
        )

        for gate_board in gate_boards:
            if gate_board["creation_authorization_blocked"] is not True:
                raise OwnerSessionCreationAuthorizationGateIntegrityError(
                    "creation authorization blocker is inactive"
                )

        matrix = record["authorization_prerequisite_matrix"]

        forbidden_matrix_true = (
            "scope_binding_receipt_present",
            "scope_bindings_verified",
            "lifetime_receipt_present",
            "session_lifetime_verified",
            "replay_protection_receipt_present",
            "session_replay_protection_verified",
            "authentication_receipt_present",
            "owner_authenticated",
            "owner_authentication_verified",
            "step_up_receipt_present",
            "owner_stepped_up",
            "owner_step_up_verified",
            "owner_session_creation_authorization_granted",
            "tower_owner_session_creation_authorization_granted",
            "owner_session_creation_authorized",
            "tower_owner_session_creation_authorized",
            "owner_session_created",
            "owner_session_started",
            "tower_owner_session_created",
            "tower_owner_session_started",
            "all_creation_authorization_prerequisites_satisfied",
            "session_creation_authorization_may_be_granted",
            "session_creation_may_proceed",
            "recording_gate_may_open",
        )

        invalid_matrix = [
            field
            for field in forbidden_matrix_true
            if matrix[field] is True
        ]

        if invalid_matrix:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "unsafe creation authorization prerequisite state: "
                + ", ".join(invalid_matrix)
            )

        checkpoint = record["checkpoint"]

        safety_state = checkpoint["safety_state"]

        if set(safety_state) != set(SAFETY_STATE_FIELDS):
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session creation authorization safety field mismatch"
            )

        unsafe_true = sorted(
            field
            for field, value in safety_state.items()
            if value is True
        )

        if unsafe_true:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "unsafe completed owner session authorization actions: "
                + ", ".join(unsafe_true)
            )

        forbidden_checkpoint_true = (
            "authorization_granted",
            "tower_session_request_sent",
            "tower_session_request_delivered",
            "tower_session_request_accepted",
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
            "session_binding_receipt_present",
            "session_bindings_verified",
            "session_lifetime_receipt_present",
            "session_lifetime_verified",
            "session_replay_protection_receipt_present",
            "session_replay_protection_verified",
            "owner_authentication_receipt_present",
            "owner_authenticated",
            "owner_authentication_verified",
            "owner_step_up_receipt_present",
            "owner_stepped_up",
            "owner_step_up_verified",
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
            for field in forbidden_checkpoint_true
            if checkpoint[field] is True
        ]

        if invalid_checkpoint:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "unsafe GP740 checkpoint state: "
                + ", ".join(invalid_checkpoint)
            )

        events = self.list_events(
            gate_id
        )

        if not events:
            raise OwnerSessionCreationAuthorizationGateIntegrityError(
                "owner session creation authorization gate has "
                "no append-only events"
            )

        previous_event_hash: str | None = None

        for event in events:
            if event["previous_event_hash"] != previous_event_hash:
                raise OwnerSessionCreationAuthorizationGateIntegrityError(
                    "owner session creation authorization event "
                    "predecessor mismatch"
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
                raise OwnerSessionCreationAuthorizationGateIntegrityError(
                    "owner session creation authorization event hash mismatch"
                )

            previous_event_hash = event["event_hash"]

        return {
            "pack_range": "GP731-GP740",
            "gate_id": gate_id,
            "gate_hash_valid": True,
            "event_chain_valid": True,
            "event_count": len(events),

            "tower_destination_only": True,
            "owner_session_preparation_lineage_valid": True,

            "gate_sealed": True,
            "authorization_granted": False,

            "tower_session_request_prepared": True,
            "tower_session_request_sent": False,

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

            "session_binding_receipt_present": False,
            "session_bindings_verified": False,

            "session_lifetime_receipt_present": False,
            "session_lifetime_verified": False,

            "session_replay_protection_receipt_present": False,
            "session_replay_protection_verified": False,

            "owner_authentication_receipt_present": False,
            "owner_authenticated": False,
            "owner_authentication_verified": False,

            "owner_step_up_receipt_present": False,
            "owner_stepped_up": False,
            "owner_step_up_verified": False,

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

            "recovery_authorization_issued": False,
            "recovery_authorization_granted": False,

            "authorization_token_issued": False,
            "authorization_token_minted": False,

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
            "recommendation": CURRENT_RECOMMENDATION,
            "verified": True,
        }

    def _normalize_operations(
        self,
        requested_operations: Sequence[str] | None,
    ) -> list[str]:
        if requested_operations is None:
            return sorted(ALLOWED_GATE_OPERATIONS)

        if isinstance(requested_operations, (str, bytes)):
            raise OwnerSessionCreationAuthorizationGateError(
                "requested_operations must be a sequence"
            )

        operations: list[str] = []

        for operation in requested_operations:
            normalized = _required_text(
                "requested_operation",
                operation,
            ).upper()

            if normalized in PROHIBITED_OPERATIONS:
                raise OwnerSessionCreationAuthorizationGateError(
                    f"prohibited operation: {normalized}"
                )

            if normalized not in ALLOWED_GATE_OPERATIONS:
                raise OwnerSessionCreationAuthorizationGateError(
                    f"operation is not allowed: {normalized}"
                )

            operations.append(normalized)

        if not operations:
            raise OwnerSessionCreationAuthorizationGateError(
                "requested_operations cannot be empty"
            )

        return sorted(set(operations))

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
            FROM vault_gp731_740_owner_session_creation_authorization_gate_events
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
            _canonical_json(dict(event_payload))
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
                vault_gp731_740_owner_session_creation_authorization_gate_events (
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
    ) -> OwnerSessionCreationAuthorizationGateReceipt:
        return OwnerSessionCreationAuthorizationGateReceipt(
            gate_id=row["gate_id"],
            gate_hash=row["gate_hash"],
            recommendation=row["recommendation"],
            gate_state=row["gate_state"],

            gate_sealed=True,
            authorization_granted=False,
            owner_session_creation_authorized=False,
            tower_owner_session_creation_authorized=False,

            owner_session_created=False,
            owner_session_started=False,
            tower_owner_session_created=False,
            tower_owner_session_started=False,

            recording_gate_open=False,
            owner_decision_recorded=False,

            immutable=True,
            append_only=True,
            idempotent_replay=idempotent_replay,
        )


__all__ = [
    "ALLOWED_GATE_OPERATIONS",
    "CURRENT_RECOMMENDATION",
    "GATE_STATE",
    "OwnerSessionCreationAuthorizationGateError",
    "OwnerSessionCreationAuthorizationGateIntegrityError",
    "OwnerSessionCreationAuthorizationGateReceipt",
    "PACK_END",
    "PACK_START",
    "PRIOR_RECOMMENDATION",
    "PROHIBITED_OPERATIONS",
    "REQUIRED_PREPARATION_STATE",
    "RecoveryCommitOwnerDecisionTowerHandoffDeliveryAuthorizationDecisionRecordingOwnerSessionCreationAuthorizationGateService",
    "SAFETY_STATE_FIELDS",
    "SESSION_PURPOSE",
    "SESSION_TYPE",
    "TOWER_DESTINATION",
]
