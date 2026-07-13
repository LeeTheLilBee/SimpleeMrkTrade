
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER "
    "DECISION RECORDING GATE / GP611-GP620"
)

LAYER_ID = (
    "vault_gp611_620_"
    "recovery_commit_owner_decision_recording_gate"
)

READINESS_LABEL = (
    "Recovery commit owner decision recording gate ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_RECORDING_GATE_CLOSED"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_recording_gate.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_owner_decision_review_layer_service import (
        get_owner_decision_preparation_intake_board,
        get_tower_owner_decision_review_session_board,
        get_owner_admin_control_satisfaction_review_board,
        get_scope_freeze_commit_window_decision_review_board,
        get_recovery_decision_option_evaluation_board,
        get_tower_owner_decision_review_draft_board,
        get_tower_owner_decision_review_receipt_draft_ledger,
        validate_recovery_commit_owner_decision_review_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP611-GP620 requires the completed "
        "GP601-GP610 owner decision review layer."
    ) from exc


_INIT_CACHE = None


ALLOWED_DECISION_VALUES = [
    "MAINTAIN_NO_GO_HOLD",
    "RETURN_FOR_REMEDIATION",
    "DEFER_OWNER_DECISION",
    "GRANT_GO",
]


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "tower_is_only_recording_boundary": True,
    "vault_preserves_append_only_decision_evidence": True,
    "recording_gate_definition_only": True,
    "recording_execution_allowed": False,
    "technical_readiness_is_not_authorization": True,
    "current_recommendation": CURRENT_RECOMMENDATION,
    "review_session_started": False,
    "owner_authenticated": False,
    "step_up_satisfied": False,
    "owner_admin_approval_granted": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,
    "owner_selection_present": False,
    "owner_decision_recorded": False,
    "go_decision_granted": False,
    "scope_freeze_activated": False,
    "commit_window_activated": False,
    "execution_window_open": False,
    "commit_point_open": False,
    "live_authorization_granted": False,
    "authorization_token_issued": False,
    "commit_command_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "owner_decision_recording_gate": True,
    "review_intake_verification_allowed": True,
    "identity_prerequisite_definition_allowed": True,
    "approval_gate_definition_allowed": True,
    "recording_contract_definition_allowed": True,
    "scope_window_boundary_definition_allowed": True,
    "append_only_record_drafts_allowed": True,
    "recording_receipt_drafts_allowed": True,

    "recording_gate_open": False,
    "recording_execution_allowed": False,
    "review_session_started": False,
    "owner_authenticated": False,
    "owner_selection_present": False,
    "owner_decision_recorded": False,
    "go_decision_granted": False,

    "owner_admin_approval_granted": False,
    "step_up_satisfied": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,

    "live_recovery_authorization_granted": False,
    "authorization_token_issued": False,
    "recovery_capability_token_issued": False,
    "recovery_bypass_token_issued": False,

    "scope_freeze_activated": False,
    "commit_window_activated": False,
    "execution_window_open": False,
    "commit_point_open": False,
    "commit_command_issued": False,
    "real_commit_attempted": False,

    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "backup_package_materialization_allowed": False,

    "production_mount_allowed": False,
    "writable_mount_allowed": False,
    "network_egress_allowed": False,
    "external_provider_connection_allowed": False,
    "external_provider_restore_allowed": False,

    "raw_file_bytes_returned_by_json": False,
    "raw_file_bytes_materialized": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "raw_download_token_exposed": False,
    "raw_recovery_token_exposed": False,
    "public_url_created": False,
    "share_link_created": False,

    "teller_direct_recording_allowed": False,
    "teller_direct_decision_allowed": False,
    "teller_direct_authorization_allowed": False,
    "teller_direct_restore_allowed": False,
    "teller_to_vault_direct_call_allowed": False,

    "resident_vault_access_allowed": False,
    "vendor_vault_access_allowed": False,
    "employee_vault_access_allowed": False,
    "customer_vault_access_allowed": False,
    "public_vault_access_allowed": False,
    "direct_vault_user_portal_allowed": False,

    "hard_delete_allowed": False,
    "purge_allowed": False,
    "quarantine_release_allowed": False,
    "physical_object_move_allowed": False,
}


PACKS = [
    {
        "gp": 611,
        "title": (
            "Recovery Commit Owner Decision "
            "Recording Gate Shell"
        ),
        "route": (
            "/vault/recovery-commit-owner-decision-"
            "recording-gate-shell.json"
        ),
    },
    {
        "gp": 612,
        "title": (
            "Tower Owner Review Intake "
            "Verification Board"
        ),
        "route": (
            "/vault/tower-owner-review-intake-"
            "verification-board.json"
        ),
    },
    {
        "gp": 613,
        "title": (
            "Owner Identity and Step-Up "
            "Recording Prerequisite Board"
        ),
        "route": (
            "/vault/owner-identity-step-up-recording-"
            "prerequisite-board.json"
        ),
    },
    {
        "gp": 614,
        "title": (
            "Owner/Admin Approval and Dual-Receipt "
            "Recording Gate"
        ),
        "route": (
            "/vault/owner-admin-approval-dual-receipt-"
            "recording-gate.json"
        ),
    },
    {
        "gp": 615,
        "title": (
            "Owner Decision Selection "
            "Recording Contract Board"
        ),
        "route": (
            "/vault/owner-decision-selection-recording-"
            "contract-board.json"
        ),
    },
    {
        "gp": 616,
        "title": (
            "Scope Freeze and Commit Window "
            "Recording Boundary Board"
        ),
        "route": (
            "/vault/scope-freeze-commit-window-recording-"
            "boundary-board.json"
        ),
    },
    {
        "gp": 617,
        "title": (
            "Tower Owner Decision Append-Only "
            "Record Draft Board"
        ),
        "route": (
            "/vault/tower-owner-decision-append-only-"
            "record-draft-board.json"
        ),
    },
    {
        "gp": 618,
        "title": (
            "Tower Owner Decision Recording "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-owner-decision-recording-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 619,
        "title": (
            "Owner Decision Recording "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/owner-decision-recording-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 620,
        "title": (
            "Owner Decision Recording Gate "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/owner-decision-recording-"
            "gate-readiness.json"
        ),
    },
]


RECORDING_CONTRACT_FIELDS = [
    "request_id",
    "tower_review_session_id",
    "tower_actor_reference",
    "owner_principal_reference",
    "owner_identity_verification_receipt_reference",
    "step_up_receipt_reference",
    "owner_admin_approval_receipt_reference",
    "dual_receipt_primary_reference",
    "dual_receipt_secondary_reference",
    "second_authority_review_receipt_reference",
    "owner_decision_value",
    "owner_decision_reason_code",
    "owner_decision_reason_summary",
    "exact_scope_hash",
    "one_time_commit_window_hash",
    "source_review_draft_hash",
    "source_review_receipt_hash",
    "idempotency_key",
    "recorded_at",
]


BLOCKERS = [
    (
        "no_recording_gate_auto_open",
        "automatic_recording_gate_open",
        "Vault cannot open the owner recording gate.",
    ),
    (
        "no_review_session_auto_start",
        "automatic_owner_review_session_start",
        "Tower must start the owner-review session.",
    ),
    (
        "no_owner_authentication",
        "vault_owner_authentication",
        "Tower must authenticate the owner.",
    ),
    (
        "no_step_up_satisfaction",
        "vault_step_up_satisfaction",
        "Tower must satisfy step-up.",
    ),
    (
        "no_owner_admin_approval",
        "vault_owner_admin_approval",
        "Tower must record owner/admin approval.",
    ),
    (
        "no_dual_receipt_satisfaction",
        "vault_dual_receipt_satisfaction",
        "Tower must validate both required receipts.",
    ),
    (
        "no_second_authority_grant",
        "vault_second_authority_grant",
        "Tower must validate second-authority review.",
    ),
    (
        "no_owner_selection_invention",
        "automatic_owner_selection",
        "Vault cannot invent the owner's selection.",
    ),
    (
        "no_owner_decision_recording",
        "owner_decision_recording_execution",
        "This layer defines the recording gate only.",
    ),
    (
        "no_go_without_complete_gate",
        "go_decision_without_complete_recording_gate",
        "GO remains unavailable while the gate is closed.",
    ),
    (
        "no_scope_freeze_activation",
        "scope_freeze_activation",
        "The recording gate cannot activate scope freeze.",
    ),
    (
        "no_commit_window_activation",
        "commit_window_activation",
        "The recording gate cannot activate the window.",
    ),
    (
        "no_execution_window",
        "execution_window_open",
        "The recording gate cannot open execution.",
    ),
    (
        "no_commit_point_open",
        "commit_point_open",
        "The recording gate cannot open the commit point.",
    ),
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "The recording gate cannot grant authorization.",
    ),
    (
        "no_authorization_token",
        "authorization_token_issue",
        "The recording gate cannot issue a token.",
    ),
    (
        "no_real_commit_command",
        "real_commit_command",
        "The recording gate cannot issue a commit command.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "The recording gate cannot execute restore.",
    ),
    (
        "no_production_mount",
        "production_storage_mount",
        "Production storage cannot be mounted.",
    ),
    (
        "no_production_write",
        "production_recovery_write",
        "Production writes remain locked.",
    ),
    (
        "no_external_provider",
        "external_provider_connection",
        "No provider may be connected.",
    ),
    (
        "no_teller_direct_recording",
        "teller_direct_owner_decision_recording",
        "Teller must route the workflow through Tower.",
    ),
    (
        "no_resident_access",
        "resident_direct_vault_access",
        "Residents cannot enter Vault.",
    ),
    (
        "no_vendor_access",
        "vendor_direct_vault_access",
        "Vendors cannot enter Vault.",
    ),
    (
        "no_public_access",
        "public_vault_access",
        "Vault has no public access path.",
    ),
    (
        "no_raw_material",
        "raw_bytes_paths_urls_or_tokens",
        "Recording contracts expose references only.",
    ),
    (
        "no_destructive_action",
        "delete_purge_release_or_move",
        "Recording preparation cannot destroy evidence.",
    ),
]


def _now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return calculate_sha256_bytes(payload)


def _id(prefix: str, request_id: str) -> str:
    return (
        f"{prefix}_"
        f"{_canonical_hash([prefix, request_id])[:24]}"
    )


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _rows(
    connection: sqlite3.Connection,
    query: str,
) -> List[Dict[str, Any]]:
    return [
        dict(row)
        for row in connection.execute(query).fetchall()
    ]


def _insert_row(
    connection: sqlite3.Connection,
    table: str,
    row: Dict[str, Any],
) -> None:
    columns = list(row.keys())

    placeholders = ", ".join(
        "?"
        for _ in columns
    )

    connection.execute(
        (
            f"INSERT INTO {table} "
            f"({', '.join(columns)}) "
            f"VALUES ({placeholders})"
        ),
        tuple(
            row[column]
            for column in columns
        ),
    )


def _by_request(
    rows: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    return {
        row["request_id"]: row
        for row in rows
    }


def _source_rows() -> List[Dict[str, Any]]:
    intake_rows = (
        get_owner_decision_preparation_intake_board()
        .get("review_intakes", [])
    )

    session_rows = (
        get_tower_owner_decision_review_session_board()
        .get("review_sessions", [])
    )

    control_rows = (
        get_owner_admin_control_satisfaction_review_board()
        .get("control_satisfaction_reviews", [])
    )

    activation_rows = (
        get_scope_freeze_commit_window_decision_review_board()
        .get("activation_decision_reviews", [])
    )

    option_rows = (
        get_recovery_decision_option_evaluation_board()
        .get("option_evaluations", [])
    )

    review_rows = (
        get_tower_owner_decision_review_draft_board()
        .get("owner_decision_review_drafts", [])
    )

    receipt_rows = (
        get_tower_owner_decision_review_receipt_draft_ledger()
        .get("review_receipt_drafts", [])
    )

    sessions = _by_request(session_rows)
    controls = _by_request(control_rows)
    activations = _by_request(activation_rows)
    options = _by_request(option_rows)
    reviews = _by_request(review_rows)
    receipts = _by_request(receipt_rows)

    results = []

    for intake in intake_rows:
        request_id = intake["request_id"]

        results.append(
            {
                "request_id": request_id,
                "workflow_type": intake.get(
                    "workflow_type",
                    "unknown_workflow",
                ),
                "intake": intake,
                "session": sessions.get(
                    request_id,
                    {},
                ),
                "control": controls.get(
                    request_id,
                    {},
                ),
                "activation": activations.get(
                    request_id,
                    {},
                ),
                "options": options.get(
                    request_id,
                    {},
                ),
                "review": reviews.get(
                    request_id,
                    {},
                ),
                "receipt": receipts.get(
                    request_id,
                    {},
                ),
            }
        )

    return results


def initialize_layer() -> Dict[str, Any]:
    global _INIT_CACHE

    if (
        _INIT_CACHE is not None
        and DB_PATH.exists()
    ):
        return dict(_INIT_CACHE)

    previous = (
        validate_recovery_commit_owner_decision_review_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS recording_intakes (
                recording_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                review_packet_verified INTEGER NOT NULL,
                session_requirements_verified INTEGER NOT NULL,
                control_requirements_verified INTEGER NOT NULL,
                activation_boundary_verified INTEGER NOT NULL,
                decision_options_verified INTEGER NOT NULL,
                review_draft_verified INTEGER NOT NULL,
                review_receipt_verified INTEGER NOT NULL,
                eligible_for_recording_gate_review INTEGER NOT NULL,
                recording_gate_open INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS identity_prerequisites (
                identity_prerequisite_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_session_required INTEGER NOT NULL,
                owner_presence_required INTEGER NOT NULL,
                owner_identity_verification_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                tower_actor_reference_required INTEGER NOT NULL,
                owner_principal_reference_required INTEGER NOT NULL,
                identity_receipt_reference_required INTEGER NOT NULL,
                step_up_receipt_reference_required INTEGER NOT NULL,
                session_started INTEGER NOT NULL,
                owner_authenticated INTEGER NOT NULL,
                step_up_satisfied INTEGER NOT NULL,
                prerequisite_complete INTEGER NOT NULL,
                prerequisite_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approval_recording_gates (
                approval_gate_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                second_authority_review_required INTEGER NOT NULL,
                approval_receipt_reference_required INTEGER NOT NULL,
                primary_dual_receipt_reference_required INTEGER NOT NULL,
                secondary_dual_receipt_reference_required INTEGER NOT NULL,
                second_authority_receipt_reference_required INTEGER NOT NULL,
                owner_admin_approval_granted INTEGER NOT NULL,
                dual_receipt_satisfied INTEGER NOT NULL,
                second_authority_review_granted INTEGER NOT NULL,
                approval_gate_complete INTEGER NOT NULL,
                approval_gate_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recording_contracts (
                recording_contract_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                allowed_decisions_json TEXT NOT NULL,
                required_fields_json TEXT NOT NULL,
                allowed_decision_count INTEGER NOT NULL,
                selected_decision_present INTEGER NOT NULL,
                decision_reason_required INTEGER NOT NULL,
                idempotency_key_required INTEGER NOT NULL,
                source_review_hash_required INTEGER NOT NULL,
                source_receipt_hash_required INTEGER NOT NULL,
                exact_scope_hash_required INTEGER NOT NULL,
                commit_window_hash_required INTEGER NOT NULL,
                append_only_required INTEGER NOT NULL,
                mutation_allowed INTEGER NOT NULL,
                raw_bytes_allowed INTEGER NOT NULL,
                raw_paths_allowed INTEGER NOT NULL,
                raw_tokens_allowed INTEGER NOT NULL,
                contract_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scope_window_boundaries (
                boundary_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                exact_scope_bound INTEGER NOT NULL,
                one_time_commit_window_required INTEGER NOT NULL,
                exact_scope_hash_required INTEGER NOT NULL,
                commit_window_hash_required INTEGER NOT NULL,
                scope_freeze_activated INTEGER NOT NULL,
                commit_window_activated INTEGER NOT NULL,
                execution_window_open INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                recording_may_activate_scope INTEGER NOT NULL,
                recording_may_activate_window INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                boundary_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_record_drafts (
                decision_record_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                recording_contract_id TEXT NOT NULL,
                identity_prerequisite_id TEXT NOT NULL,
                approval_gate_id TEXT NOT NULL,
                boundary_id TEXT NOT NULL,
                source_review_draft_hash TEXT NOT NULL,
                source_review_receipt_hash TEXT NOT NULL,
                recording_gate_ready_for_future_tower_input INTEGER NOT NULL,
                recording_gate_open INTEGER NOT NULL,
                owner_selection_present INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                go_decision_granted INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                record_draft_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recording_receipt_drafts (
                recording_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                decision_record_draft_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                review_packet_recorded INTEGER NOT NULL,
                identity_requirements_recorded INTEGER NOT NULL,
                approval_requirements_recorded INTEGER NOT NULL,
                recording_contract_recorded INTEGER NOT NULL,
                scope_window_boundary_recorded INTEGER NOT NULL,
                recording_gate_closed_recorded INTEGER NOT NULL,
                owner_selection_recorded INTEGER NOT NULL,
                final_owner_decision_recorded INTEGER NOT NULL,
                go_decision_recorded INTEGER NOT NULL,
                live_authorization_recorded INTEGER NOT NULL,
                authorization_token_recorded INTEGER NOT NULL,
                commit_command_recorded INTEGER NOT NULL,
                actual_restore_recorded INTEGER NOT NULL,
                production_write_recorded INTEGER NOT NULL,
                raw_bytes_recorded INTEGER NOT NULL,
                raw_paths_recorded INTEGER NOT NULL,
                raw_tokens_recorded INTEGER NOT NULL,
                public_links_recorded INTEGER NOT NULL,
                finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                receipt_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS safety_blockers (
                blocker_id TEXT PRIMARY KEY,
                blocked_action TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        for table in [
            "recording_intakes",
            "identity_prerequisites",
            "approval_recording_gates",
            "recording_contracts",
            "scope_window_boundaries",
            "decision_record_drafts",
            "recording_receipt_drafts",
            "safety_blockers",
        ]:
            connection.execute(
                f"DELETE FROM {table}"
            )

        now = _now()

        for blocker_id, action, reason in BLOCKERS:
            _insert_row(
                connection,
                "safety_blockers",
                {
                    "blocker_id": blocker_id,
                    "blocked_action": action,
                    "allowed": 0,
                    "reason": reason,
                    "created_at": now,
                },
            )

        for source in _source_rows():
            request_id = source["request_id"]
            workflow_type = source["workflow_type"]

            intake = source["intake"]
            session = source["session"]
            control = source["control"]
            activation = source["activation"]
            options = source["options"]
            review = source["review"]
            receipt = source["receipt"]

            review_packet_verified = all(
                [
                    bool(
                        intake.get(
                            "preparation_packet_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "criteria_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "controls_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "activation_plan_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "alternatives_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "decision_record_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_owner_decision_review",
                            0,
                        )
                    ),
                    not bool(
                        intake.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        intake.get(
                            "live_authorization_granted",
                            1,
                        )
                    ),
                ]
            )

            session_requirements_verified = all(
                [
                    bool(
                        session.get(
                            "tower_session_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "owner_presence_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "owner_identity_verification_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "step_up_challenge_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "dual_receipt_review_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "second_authority_review_required",
                            0,
                        )
                    ),
                    not bool(
                        session.get(
                            "session_started",
                            1,
                        )
                    ),
                    not bool(
                        session.get(
                            "owner_authenticated",
                            1,
                        )
                    ),
                    not bool(
                        session.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    len(
                        session.get(
                            "session_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            control_requirements_verified = all(
                [
                    bool(
                        control.get(
                            "owner_admin_approval_required",
                            0,
                        )
                    ),
                    bool(
                        control.get(
                            "step_up_required",
                            0,
                        )
                    ),
                    bool(
                        control.get(
                            "dual_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        control.get(
                            "second_authority_review_required",
                            0,
                        )
                    ),
                    not bool(
                        control.get(
                            "owner_admin_approval_granted",
                            1,
                        )
                    ),
                    not bool(
                        control.get(
                            "step_up_satisfied",
                            1,
                        )
                    ),
                    not bool(
                        control.get(
                            "dual_receipt_satisfied",
                            1,
                        )
                    ),
                    not bool(
                        control.get(
                            "second_authority_review_granted",
                            1,
                        )
                    ),
                    not bool(
                        control.get(
                            "control_gate_complete",
                            1,
                        )
                    ),
                    bool(
                        control.get(
                            "no_go_hold_required",
                            0,
                        )
                    ),
                    len(
                        control.get(
                            "control_review_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            activation_boundary_verified = all(
                [
                    bool(
                        activation.get(
                            "exact_scope_bound",
                            0,
                        )
                    ),
                    bool(
                        activation.get(
                            "one_time_commit_window_required",
                            0,
                        )
                    ),
                    bool(
                        activation.get(
                            "scope_freeze_activation_required",
                            0,
                        )
                    ),
                    bool(
                        activation.get(
                            "commit_window_activation_required",
                            0,
                        )
                    ),
                    bool(
                        activation.get(
                            "execution_window_required",
                            0,
                        )
                    ),
                    bool(
                        activation.get(
                            "commit_point_activation_required",
                            0,
                        )
                    ),
                    not bool(
                        activation.get(
                            "scope_freeze_activated",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "commit_window_activated",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "execution_window_open",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "commit_point_open",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "activation_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "activation_gate_complete",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "production_target_allowed",
                            1,
                        )
                    ),
                    not bool(
                        activation.get(
                            "external_provider_allowed",
                            1,
                        )
                    ),
                    len(
                        activation.get(
                            "activation_review_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            decision_options_verified = all(
                [
                    int(
                        options.get(
                            "available_option_count",
                            0,
                        )
                    )
                    == 3,
                    bool(
                        options.get(
                            "maintain_hold_available",
                            0,
                        )
                    ),
                    bool(
                        options.get(
                            "remediation_available",
                            0,
                        )
                    ),
                    bool(
                        options.get(
                            "defer_available",
                            0,
                        )
                    ),
                    not bool(
                        options.get(
                            "go_available",
                            1,
                        )
                    ),
                    bool(
                        options.get(
                            "owner_selection_pending",
                            0,
                        )
                    ),
                    len(
                        options.get(
                            "option_evaluation_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            review_draft_verified = all(
                [
                    bool(
                        review.get(
                            "preparation_packet_complete",
                            0,
                        )
                    ),
                    bool(
                        review.get(
                            "review_session_ready",
                            0,
                        )
                    ),
                    bool(
                        review.get(
                            "controls_pending",
                            0,
                        )
                    ),
                    bool(
                        review.get(
                            "activation_pending",
                            0,
                        )
                    ),
                    bool(
                        review.get(
                            "owner_selection_pending",
                            0,
                        )
                    ),
                    not bool(
                        review.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        review.get(
                            "go_decision_granted",
                            1,
                        )
                    ),
                    not bool(
                        review.get(
                            "live_authorization_granted",
                            1,
                        )
                    ),
                    not bool(
                        review.get(
                            "authorization_token_issued",
                            1,
                        )
                    ),
                    not bool(
                        review.get(
                            "commit_command_issued",
                            1,
                        )
                    ),
                    not bool(
                        review.get(
                            "actual_restore_allowed",
                            1,
                        )
                    ),
                    not bool(
                        review.get(
                            "production_write_allowed",
                            1,
                        )
                    ),
                    len(
                        review.get(
                            "review_draft_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            review_receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "preparation_packet_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "review_session_requirements_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "control_status_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "activation_status_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "options_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "owner_selection_pending_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "recommendation_recorded",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "final_owner_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "live_authorization_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "authorization_token_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "commit_command_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "actual_restore_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "production_write_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "raw_bytes_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "raw_paths_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "raw_tokens_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "public_links_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "finalized",
                            1,
                        )
                    ),
                    bool(
                        receipt.get(
                            "append_only",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "mutable",
                            1,
                        )
                    ),
                    len(
                        receipt.get(
                            "receipt_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            eligible_for_gate_review = all(
                [
                    review_packet_verified,
                    session_requirements_verified,
                    control_requirements_verified,
                    activation_boundary_verified,
                    decision_options_verified,
                    review_draft_verified,
                    review_receipt_verified,
                ]
            )

            recording_intake_id = _id(
                "recording_gate_intake",
                request_id,
            )

            identity_prerequisite_id = _id(
                "recording_identity_prerequisite",
                request_id,
            )

            approval_gate_id = _id(
                "recording_approval_gate",
                request_id,
            )

            recording_contract_id = _id(
                "owner_decision_recording_contract",
                request_id,
            )

            boundary_id = _id(
                "recording_scope_window_boundary",
                request_id,
            )

            decision_record_draft_id = _id(
                "owner_decision_append_only_record",
                request_id,
            )

            recording_receipt_id = _id(
                "owner_decision_recording_receipt",
                request_id,
            )

            _insert_row(
                connection,
                "recording_intakes",
                {
                    "recording_intake_id": (
                        recording_intake_id
                    ),
                    "request_id": request_id,
                    "workflow_type": workflow_type,
                    "state": (
                        "review_packet_verified_"
                        "recording_gate_closed"
                    ),
                    "review_packet_verified": int(
                        review_packet_verified
                    ),
                    "session_requirements_verified": int(
                        session_requirements_verified
                    ),
                    "control_requirements_verified": int(
                        control_requirements_verified
                    ),
                    "activation_boundary_verified": int(
                        activation_boundary_verified
                    ),
                    "decision_options_verified": int(
                        decision_options_verified
                    ),
                    "review_draft_verified": int(
                        review_draft_verified
                    ),
                    "review_receipt_verified": int(
                        review_receipt_verified
                    ),
                    "eligible_for_recording_gate_review": int(
                        eligible_for_gate_review
                    ),
                    "recording_gate_open": 0,
                    "owner_decision_recorded": 0,
                    "created_at": now,
                },
            )

            identity_payload = {
                "request_id": request_id,
                "tower_session_required": True,
                "owner_presence_required": True,
                "owner_identity_verification_required": True,
                "step_up_required": True,
                "tower_actor_reference_required": True,
                "owner_principal_reference_required": True,
                "identity_receipt_reference_required": True,
                "step_up_receipt_reference_required": True,
                "session_started": False,
                "owner_authenticated": False,
                "step_up_satisfied": False,
                "prerequisite_complete": False,
            }

            prerequisite_hash = _canonical_hash(
                identity_payload
            )

            _insert_row(
                connection,
                "identity_prerequisites",
                {
                    "identity_prerequisite_id": (
                        identity_prerequisite_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_identity_and_step_up_"
                        "requirements_defined_not_satisfied"
                    ),
                    "tower_session_required": 1,
                    "owner_presence_required": 1,
                    "owner_identity_verification_required": 1,
                    "step_up_required": 1,
                    "tower_actor_reference_required": 1,
                    "owner_principal_reference_required": 1,
                    "identity_receipt_reference_required": 1,
                    "step_up_receipt_reference_required": 1,
                    "session_started": 0,
                    "owner_authenticated": 0,
                    "step_up_satisfied": 0,
                    "prerequisite_complete": 0,
                    "prerequisite_hash": prerequisite_hash,
                    "created_at": now,
                },
            )

            approval_payload = {
                "request_id": request_id,
                "owner_admin_approval_required": True,
                "dual_receipt_required": True,
                "second_authority_review_required": True,
                "approval_receipt_reference_required": True,
                "primary_dual_receipt_reference_required": True,
                "secondary_dual_receipt_reference_required": True,
                "second_authority_receipt_reference_required": True,
                "owner_admin_approval_granted": False,
                "dual_receipt_satisfied": False,
                "second_authority_review_granted": False,
                "approval_gate_complete": False,
            }

            approval_gate_hash = _canonical_hash(
                approval_payload
            )

            _insert_row(
                connection,
                "approval_recording_gates",
                {
                    "approval_gate_id": approval_gate_id,
                    "request_id": request_id,
                    "state": (
                        "approval_and_dual_receipt_"
                        "requirements_defined_not_satisfied"
                    ),
                    "owner_admin_approval_required": 1,
                    "dual_receipt_required": 1,
                    "second_authority_review_required": 1,
                    "approval_receipt_reference_required": 1,
                    "primary_dual_receipt_reference_required": 1,
                    "secondary_dual_receipt_reference_required": 1,
                    "second_authority_receipt_reference_required": 1,
                    "owner_admin_approval_granted": 0,
                    "dual_receipt_satisfied": 0,
                    "second_authority_review_granted": 0,
                    "approval_gate_complete": 0,
                    "approval_gate_hash": approval_gate_hash,
                    "created_at": now,
                },
            )

            contract_payload = {
                "request_id": request_id,
                "allowed_decisions": ALLOWED_DECISION_VALUES,
                "required_fields": RECORDING_CONTRACT_FIELDS,
                "selected_decision_present": False,
                "decision_reason_required": True,
                "idempotency_key_required": True,
                "source_review_hash_required": True,
                "source_receipt_hash_required": True,
                "exact_scope_hash_required": True,
                "commit_window_hash_required": True,
                "append_only_required": True,
                "mutation_allowed": False,
                "raw_bytes_allowed": False,
                "raw_paths_allowed": False,
                "raw_tokens_allowed": False,
            }

            contract_hash = _canonical_hash(
                contract_payload
            )

            _insert_row(
                connection,
                "recording_contracts",
                {
                    "recording_contract_id": (
                        recording_contract_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "recording_contract_defined_"
                        "owner_selection_absent"
                    ),
                    "allowed_decisions_json": json.dumps(
                        ALLOWED_DECISION_VALUES,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "required_fields_json": json.dumps(
                        RECORDING_CONTRACT_FIELDS,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "allowed_decision_count": len(
                        ALLOWED_DECISION_VALUES
                    ),
                    "selected_decision_present": 0,
                    "decision_reason_required": 1,
                    "idempotency_key_required": 1,
                    "source_review_hash_required": 1,
                    "source_receipt_hash_required": 1,
                    "exact_scope_hash_required": 1,
                    "commit_window_hash_required": 1,
                    "append_only_required": 1,
                    "mutation_allowed": 0,
                    "raw_bytes_allowed": 0,
                    "raw_paths_allowed": 0,
                    "raw_tokens_allowed": 0,
                    "contract_hash": contract_hash,
                    "created_at": now,
                },
            )

            boundary_payload = {
                "request_id": request_id,
                "exact_scope_bound": True,
                "one_time_commit_window_required": True,
                "exact_scope_hash_required": True,
                "commit_window_hash_required": True,
                "scope_freeze_activated": False,
                "commit_window_activated": False,
                "execution_window_open": False,
                "commit_point_open": False,
                "recording_may_activate_scope": False,
                "recording_may_activate_window": False,
                "production_target_allowed": False,
                "external_provider_allowed": False,
            }

            boundary_hash = _canonical_hash(
                boundary_payload
            )

            _insert_row(
                connection,
                "scope_window_boundaries",
                {
                    "boundary_id": boundary_id,
                    "request_id": request_id,
                    "state": (
                        "scope_and_window_hash_boundary_"
                        "defined_nothing_activated"
                    ),
                    "exact_scope_bound": 1,
                    "one_time_commit_window_required": 1,
                    "exact_scope_hash_required": 1,
                    "commit_window_hash_required": 1,
                    "scope_freeze_activated": 0,
                    "commit_window_activated": 0,
                    "execution_window_open": 0,
                    "commit_point_open": 0,
                    "recording_may_activate_scope": 0,
                    "recording_may_activate_window": 0,
                    "production_target_allowed": 0,
                    "external_provider_allowed": 0,
                    "boundary_hash": boundary_hash,
                    "created_at": now,
                },
            )

            source_review_draft_hash = review.get(
                "review_draft_hash",
                "",
            )

            source_review_receipt_hash = receipt.get(
                "receipt_hash",
                "",
            )

            record_payload = {
                "request_id": request_id,
                "recording_contract_id": (
                    recording_contract_id
                ),
                "identity_prerequisite_id": (
                    identity_prerequisite_id
                ),
                "approval_gate_id": approval_gate_id,
                "boundary_id": boundary_id,
                "source_review_draft_hash": (
                    source_review_draft_hash
                ),
                "source_review_receipt_hash": (
                    source_review_receipt_hash
                ),
                "recording_gate_ready_for_future_tower_input": True,
                "recording_gate_open": False,
                "owner_selection_present": False,
                "owner_decision_recorded": False,
                "go_decision_granted": False,
                "live_authorization_granted": False,
                "authorization_token_issued": False,
                "commit_command_issued": False,
                "actual_restore_allowed": False,
                "production_write_allowed": False,
                "finalized": False,
                "append_only": True,
                "mutable": False,
            }

            record_draft_hash = _canonical_hash(
                record_payload
            )

            _insert_row(
                connection,
                "decision_record_drafts",
                {
                    "decision_record_draft_id": (
                        decision_record_draft_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "append_only_owner_decision_"
                        "record_draft_gate_closed"
                    ),
                    "recording_contract_id": (
                        recording_contract_id
                    ),
                    "identity_prerequisite_id": (
                        identity_prerequisite_id
                    ),
                    "approval_gate_id": approval_gate_id,
                    "boundary_id": boundary_id,
                    "source_review_draft_hash": (
                        source_review_draft_hash
                    ),
                    "source_review_receipt_hash": (
                        source_review_receipt_hash
                    ),
                    "recording_gate_ready_for_future_tower_input": 1,
                    "recording_gate_open": 0,
                    "owner_selection_present": 0,
                    "owner_decision_recorded": 0,
                    "go_decision_granted": 0,
                    "live_authorization_granted": 0,
                    "authorization_token_issued": 0,
                    "commit_command_issued": 0,
                    "actual_restore_allowed": 0,
                    "production_write_allowed": 0,
                    "finalized": 0,
                    "append_only": 1,
                    "mutable": 0,
                    "record_draft_hash": record_draft_hash,
                    "created_at": now,
                },
            )

            receipt_payload = {
                "request_id": request_id,
                "decision_record_draft_id": (
                    decision_record_draft_id
                ),
                "review_packet_recorded": True,
                "identity_requirements_recorded": True,
                "approval_requirements_recorded": True,
                "recording_contract_recorded": True,
                "scope_window_boundary_recorded": True,
                "recording_gate_closed_recorded": True,
                "owner_selection_recorded": False,
                "final_owner_decision_recorded": False,
                "go_decision_recorded": False,
                "live_authorization_recorded": False,
                "authorization_token_recorded": False,
                "commit_command_recorded": False,
                "actual_restore_recorded": False,
                "production_write_recorded": False,
            }

            receipt_hash = _canonical_hash(
                receipt_payload
            )

            _insert_row(
                connection,
                "recording_receipt_drafts",
                {
                    "recording_receipt_id": (
                        recording_receipt_id
                    ),
                    "request_id": request_id,
                    "decision_record_draft_id": (
                        decision_record_draft_id
                    ),
                    "state": (
                        "tower_owner_decision_recording_"
                        "receipt_draft_gate_closed"
                    ),
                    "tower_controlled": 1,
                    "review_packet_recorded": 1,
                    "identity_requirements_recorded": 1,
                    "approval_requirements_recorded": 1,
                    "recording_contract_recorded": 1,
                    "scope_window_boundary_recorded": 1,
                    "recording_gate_closed_recorded": 1,
                    "owner_selection_recorded": 0,
                    "final_owner_decision_recorded": 0,
                    "go_decision_recorded": 0,
                    "live_authorization_recorded": 0,
                    "authorization_token_recorded": 0,
                    "commit_command_recorded": 0,
                    "actual_restore_recorded": 0,
                    "production_write_recorded": 0,
                    "raw_bytes_recorded": 0,
                    "raw_paths_recorded": 0,
                    "raw_tokens_recorded": 0,
                    "public_links_recorded": 0,
                    "finalized": 0,
                    "append_only": 1,
                    "mutable": 0,
                    "receipt_hash": receipt_hash,
                    "created_at": now,
                },
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_owner_review_layer_ready": bool(
            previous.get("ready", False)
        ),
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "db_path": str(
            DB_PATH.relative_to(PROJECT_ROOT)
        ),
    }

    _INIT_CACHE = dict(result)
    return result


def get_recovery_commit_owner_decision_recording_gate_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 611,
        "title": (
            "Recovery Commit Owner Decision "
            "Recording Gate Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "recording_gate_definition_only": True,
        "recording_gate_open": False,
        "recording_execution_allowed": False,
        "owner_authenticated": False,
        "owner_selection_present": False,
        "owner_decision_recorded": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "commit_point_open": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_tower_owner_review_intake_verification_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM recording_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 612,
        "title": (
            "Tower Owner Review Intake "
            "Verification Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "recording_intakes": rows,
        "all_review_packets_verified": all(
            bool(row["review_packet_verified"])
            for row in rows
        ),
        "all_session_requirements_verified": all(
            bool(
                row[
                    "session_requirements_verified"
                ]
            )
            for row in rows
        ),
        "all_control_requirements_verified": all(
            bool(
                row[
                    "control_requirements_verified"
                ]
            )
            for row in rows
        ),
        "all_activation_boundaries_verified": all(
            bool(
                row[
                    "activation_boundary_verified"
                ]
            )
            for row in rows
        ),
        "all_decision_options_verified": all(
            bool(row["decision_options_verified"])
            for row in rows
        ),
        "all_review_drafts_verified": all(
            bool(row["review_draft_verified"])
            for row in rows
        ),
        "all_review_receipts_verified": all(
            bool(row["review_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_gate_review": all(
            bool(
                row[
                    "eligible_for_recording_gate_review"
                ]
            )
            for row in rows
        ),
        "no_recording_gates_open": all(
            not bool(row["recording_gate_open"])
            for row in rows
        ),
        "no_owner_decisions_recorded": all(
            not bool(row["owner_decision_recorded"])
            for row in rows
        ),
    }


def get_owner_identity_step_up_recording_prerequisite_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM identity_prerequisites
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 613,
        "title": (
            "Owner Identity and Step-Up "
            "Recording Prerequisite Board"
        ),
        "ready": True,
        "prerequisite_count": len(rows),
        "identity_prerequisites": rows,
        "all_tower_sessions_required": all(
            bool(row["tower_session_required"])
            for row in rows
        ),
        "all_owner_presence_required": all(
            bool(row["owner_presence_required"])
            for row in rows
        ),
        "all_identity_verification_required": all(
            bool(
                row[
                    "owner_identity_verification_required"
                ]
            )
            for row in rows
        ),
        "all_step_up_required": all(
            bool(row["step_up_required"])
            for row in rows
        ),
        "all_reference_requirements_present": all(
            bool(row["tower_actor_reference_required"])
            and bool(
                row["owner_principal_reference_required"]
            )
            and bool(
                row[
                    "identity_receipt_reference_required"
                ]
            )
            and bool(
                row[
                    "step_up_receipt_reference_required"
                ]
            )
            for row in rows
        ),
        "no_sessions_started": all(
            not bool(row["session_started"])
            for row in rows
        ),
        "no_owners_authenticated": all(
            not bool(row["owner_authenticated"])
            for row in rows
        ),
        "no_step_up_satisfied": all(
            not bool(row["step_up_satisfied"])
            for row in rows
        ),
        "no_identity_prerequisites_complete": all(
            not bool(row["prerequisite_complete"])
            for row in rows
        ),
        "all_prerequisite_hashes_present": all(
            len(row["prerequisite_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_admin_approval_dual_receipt_recording_gate(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM approval_recording_gates
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 614,
        "title": (
            "Owner/Admin Approval and Dual-Receipt "
            "Recording Gate"
        ),
        "ready": True,
        "gate_count": len(rows),
        "approval_recording_gates": rows,
        "all_owner_admin_approval_required": all(
            bool(row["owner_admin_approval_required"])
            for row in rows
        ),
        "all_dual_receipts_required": all(
            bool(row["dual_receipt_required"])
            for row in rows
        ),
        "all_second_authority_reviews_required": all(
            bool(
                row[
                    "second_authority_review_required"
                ]
            )
            for row in rows
        ),
        "all_receipt_references_required": all(
            bool(
                row[
                    "approval_receipt_reference_required"
                ]
            )
            and bool(
                row[
                    "primary_dual_receipt_reference_required"
                ]
            )
            and bool(
                row[
                    "secondary_dual_receipt_reference_required"
                ]
            )
            and bool(
                row[
                    "second_authority_receipt_reference_required"
                ]
            )
            for row in rows
        ),
        "no_owner_admin_approval_granted": all(
            not bool(row["owner_admin_approval_granted"])
            for row in rows
        ),
        "no_dual_receipts_satisfied": all(
            not bool(row["dual_receipt_satisfied"])
            for row in rows
        ),
        "no_second_authority_granted": all(
            not bool(
                row[
                    "second_authority_review_granted"
                ]
            )
            for row in rows
        ),
        "no_approval_gates_complete": all(
            not bool(row["approval_gate_complete"])
            for row in rows
        ),
        "all_gate_hashes_present": all(
            len(row["approval_gate_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_decision_selection_recording_contract_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM recording_contracts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 615,
        "title": (
            "Owner Decision Selection "
            "Recording Contract Board"
        ),
        "ready": True,
        "contract_count": len(rows),
        "recording_contracts": rows,
        "allowed_decision_values": (
            ALLOWED_DECISION_VALUES
        ),
        "required_contract_fields": (
            RECORDING_CONTRACT_FIELDS
        ),
        "all_decision_enums_complete": all(
            row["allowed_decision_count"]
            == len(ALLOWED_DECISION_VALUES)
            for row in rows
        ),
        "no_selected_decisions_present": all(
            not bool(row["selected_decision_present"])
            for row in rows
        ),
        "all_integrity_requirements_present": all(
            bool(row["decision_reason_required"])
            and bool(row["idempotency_key_required"])
            and bool(row["source_review_hash_required"])
            and bool(row["source_receipt_hash_required"])
            and bool(row["exact_scope_hash_required"])
            and bool(row["commit_window_hash_required"])
            and bool(row["append_only_required"])
            for row in rows
        ),
        "no_mutation_allowed": all(
            not bool(row["mutation_allowed"])
            for row in rows
        ),
        "no_raw_material_allowed": all(
            not bool(row["raw_bytes_allowed"])
            and not bool(row["raw_paths_allowed"])
            and not bool(row["raw_tokens_allowed"])
            for row in rows
        ),
        "all_contract_hashes_present": all(
            len(row["contract_hash"]) == 64
            for row in rows
        ),
    }


def get_scope_freeze_commit_window_recording_boundary_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM scope_window_boundaries
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 616,
        "title": (
            "Scope Freeze and Commit Window "
            "Recording Boundary Board"
        ),
        "ready": True,
        "boundary_count": len(rows),
        "scope_window_boundaries": rows,
        "all_exact_scopes_bound": all(
            bool(row["exact_scope_bound"])
            for row in rows
        ),
        "all_one_time_windows_required": all(
            bool(row["one_time_commit_window_required"])
            for row in rows
        ),
        "all_scope_window_hashes_required": all(
            bool(row["exact_scope_hash_required"])
            and bool(row["commit_window_hash_required"])
            for row in rows
        ),
        "nothing_activated": all(
            not bool(row["scope_freeze_activated"])
            and not bool(row["commit_window_activated"])
            and not bool(row["execution_window_open"])
            and not bool(row["commit_point_open"])
            for row in rows
        ),
        "recording_cannot_activate_scope_or_window": all(
            not bool(
                row["recording_may_activate_scope"]
            )
            and not bool(
                row["recording_may_activate_window"]
            )
            for row in rows
        ),
        "no_production_targets_allowed": all(
            not bool(row["production_target_allowed"])
            for row in rows
        ),
        "no_external_providers_allowed": all(
            not bool(row["external_provider_allowed"])
            for row in rows
        ),
        "all_boundary_hashes_present": all(
            len(row["boundary_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_append_only_record_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM decision_record_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 617,
        "title": (
            "Tower Owner Decision Append-Only "
            "Record Draft Board"
        ),
        "ready": True,
        "draft_count": len(rows),
        "decision_record_drafts": rows,
        "all_source_hashes_present": all(
            len(row["source_review_draft_hash"]) == 64
            and len(
                row["source_review_receipt_hash"]
            )
            == 64
            for row in rows
        ),
        "all_ready_for_future_tower_input": all(
            bool(
                row[
                    "recording_gate_ready_for_future_tower_input"
                ]
            )
            for row in rows
        ),
        "no_recording_gates_open": all(
            not bool(row["recording_gate_open"])
            for row in rows
        ),
        "no_owner_selections_present": all(
            not bool(row["owner_selection_present"])
            for row in rows
        ),
        "no_owner_decisions_recorded": all(
            not bool(row["owner_decision_recorded"])
            for row in rows
        ),
        "no_go_decisions_granted": all(
            not bool(row["go_decision_granted"])
            for row in rows
        ),
        "no_authorization_or_tokens": all(
            not bool(row["live_authorization_granted"])
            and not bool(
                row["authorization_token_issued"]
            )
            for row in rows
        ),
        "no_commit_restore_or_write": all(
            not bool(row["commit_command_issued"])
            and not bool(row["actual_restore_allowed"])
            and not bool(row["production_write_allowed"])
            for row in rows
        ),
        "all_drafts_unfinalized": all(
            not bool(row["finalized"])
            for row in rows
        ),
        "all_append_only": all(
            bool(row["append_only"])
            for row in rows
        ),
        "all_immutable": all(
            not bool(row["mutable"])
            for row in rows
        ),
        "all_record_hashes_present": all(
            len(row["record_draft_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_recording_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM recording_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 618,
        "title": (
            "Tower Owner Decision Recording "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "recording_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_gate_definition_components_recorded": all(
            bool(row["review_packet_recorded"])
            and bool(
                row["identity_requirements_recorded"]
            )
            and bool(
                row["approval_requirements_recorded"]
            )
            and bool(
                row["recording_contract_recorded"]
            )
            and bool(
                row["scope_window_boundary_recorded"]
            )
            and bool(
                row["recording_gate_closed_recorded"]
            )
            for row in rows
        ),
        "no_owner_selection_or_decision_recorded": all(
            not bool(row["owner_selection_recorded"])
            and not bool(
                row["final_owner_decision_recorded"]
            )
            and not bool(row["go_decision_recorded"])
            for row in rows
        ),
        "no_authorization_or_tokens_recorded": all(
            not bool(
                row["live_authorization_recorded"]
            )
            and not bool(
                row["authorization_token_recorded"]
            )
            for row in rows
        ),
        "no_commit_restore_or_write_recorded": all(
            not bool(row["commit_command_recorded"])
            and not bool(row["actual_restore_recorded"])
            and not bool(row["production_write_recorded"])
            for row in rows
        ),
        "no_raw_or_public_recorded": all(
            not bool(row["raw_bytes_recorded"])
            and not bool(row["raw_paths_recorded"])
            and not bool(row["raw_tokens_recorded"])
            and not bool(row["public_links_recorded"])
            for row in rows
        ),
        "all_receipts_draft": all(
            not bool(row["finalized"])
            for row in rows
        ),
        "all_append_only": all(
            bool(row["append_only"])
            for row in rows
        ),
        "all_immutable": all(
            not bool(row["mutable"])
            for row in rows
        ),
        "all_receipt_hashes_present": all(
            len(row["receipt_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_decision_recording_safety_blocker_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM safety_blockers
            ORDER BY blocker_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 619,
        "title": (
            "Owner Decision Recording "
            "Safety Blocker Board"
        ),
        "ready": True,
        "blocker_count": len(rows),
        "blockers": rows,
        "unsafe_action_count": sum(
            1
            for row in rows
            if bool(row["allowed"])
        ),
        "all_dangerous_actions_blocked": all(
            not bool(row["allowed"])
            for row in rows
        ),
    }


def get_owner_decision_recording_gate_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_recovery_commit_owner_decision_recording_gate_shell()
    )

    intakes = (
        get_tower_owner_review_intake_verification_board()
    )

    identities = (
        get_owner_identity_step_up_recording_prerequisite_board()
    )

    approvals = (
        get_owner_admin_approval_dual_receipt_recording_gate()
    )

    contracts = (
        get_owner_decision_selection_recording_contract_board()
    )

    boundaries = (
        get_scope_freeze_commit_window_recording_boundary_board()
    )

    records = (
        get_tower_owner_decision_append_only_record_draft_board()
    )

    receipts = (
        get_tower_owner_decision_recording_receipt_draft_ledger()
    )

    blockers = (
        get_owner_decision_recording_safety_blocker_board()
    )

    checks = {
        "previous_owner_review_layer_ready": (
            initialized[
                "previous_owner_review_layer_ready"
            ]
            is True
        ),
        "shell_ready": shell["ready"] is True,
        "doctrine_locked": (
            DOCTRINE["tower"]
            == "face_protocol_authority"
            and DOCTRINE["teller"]
            == "workflow_request_source"
            and DOCTRINE["vault"]
            == "sealed_memory"
            and DOCTRINE["correct_flow"]
            == (
                "Teller -> Tower -> Vault -> Tower -> Teller"
            )
        ),
        "recording_definition_only": (
            DOCTRINE[
                "tower_is_only_recording_boundary"
            ]
            is True
            and DOCTRINE[
                "recording_gate_definition_only"
            ]
            is True
            and DOCTRINE[
                "recording_execution_allowed"
            ]
            is False
            and DOCTRINE[
                "technical_readiness_is_not_authorization"
            ]
            is True
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "owner_review_package_verified": (
            intakes[
                "all_review_packets_verified"
            ]
            is True
            and intakes[
                "all_session_requirements_verified"
            ]
            is True
            and intakes[
                "all_control_requirements_verified"
            ]
            is True
            and intakes[
                "all_activation_boundaries_verified"
            ]
            is True
            and intakes[
                "all_decision_options_verified"
            ]
            is True
            and intakes[
                "all_review_drafts_verified"
            ]
            is True
            and intakes[
                "all_review_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_gate_review"
            ]
            is True
        ),
        "intake_recording_gate_closed": (
            intakes[
                "no_recording_gates_open"
            ]
            is True
            and intakes[
                "no_owner_decisions_recorded"
            ]
            is True
        ),

        "identity_prerequisites_present": (
            identities["prerequisite_count"] >= 1
        ),
        "identity_requirements_complete": (
            identities[
                "all_tower_sessions_required"
            ]
            is True
            and identities[
                "all_owner_presence_required"
            ]
            is True
            and identities[
                "all_identity_verification_required"
            ]
            is True
            and identities[
                "all_step_up_required"
            ]
            is True
            and identities[
                "all_reference_requirements_present"
            ]
            is True
        ),
        "identity_requirements_not_satisfied": (
            identities["no_sessions_started"]
            is True
            and identities[
                "no_owners_authenticated"
            ]
            is True
            and identities[
                "no_step_up_satisfied"
            ]
            is True
            and identities[
                "no_identity_prerequisites_complete"
            ]
            is True
        ),

        "approval_gates_present": (
            approvals["gate_count"] >= 1
        ),
        "approval_requirements_complete": (
            approvals[
                "all_owner_admin_approval_required"
            ]
            is True
            and approvals[
                "all_dual_receipts_required"
            ]
            is True
            and approvals[
                "all_second_authority_reviews_required"
            ]
            is True
            and approvals[
                "all_receipt_references_required"
            ]
            is True
        ),
        "approval_requirements_not_satisfied": (
            approvals[
                "no_owner_admin_approval_granted"
            ]
            is True
            and approvals[
                "no_dual_receipts_satisfied"
            ]
            is True
            and approvals[
                "no_second_authority_granted"
            ]
            is True
            and approvals[
                "no_approval_gates_complete"
            ]
            is True
        ),

        "recording_contracts_present": (
            contracts["contract_count"] >= 1
        ),
        "recording_contract_complete": (
            contracts[
                "all_decision_enums_complete"
            ]
            is True
            and contracts[
                "all_integrity_requirements_present"
            ]
            is True
            and contracts[
                "no_mutation_allowed"
            ]
            is True
            and contracts[
                "no_raw_material_allowed"
            ]
            is True
        ),
        "owner_selection_absent": (
            contracts[
                "no_selected_decisions_present"
            ]
            is True
        ),

        "boundaries_present": (
            boundaries["boundary_count"] >= 1
        ),
        "scope_window_boundary_complete": (
            boundaries[
                "all_exact_scopes_bound"
            ]
            is True
            and boundaries[
                "all_one_time_windows_required"
            ]
            is True
            and boundaries[
                "all_scope_window_hashes_required"
            ]
            is True
        ),
        "scope_window_activation_closed": (
            boundaries["nothing_activated"]
            is True
            and boundaries[
                "recording_cannot_activate_scope_or_window"
            ]
            is True
            and boundaries[
                "no_production_targets_allowed"
            ]
            is True
            and boundaries[
                "no_external_providers_allowed"
            ]
            is True
        ),

        "record_drafts_present": (
            records["draft_count"] >= 1
        ),
        "append_only_record_drafts_ready": (
            records[
                "all_source_hashes_present"
            ]
            is True
            and records[
                "all_ready_for_future_tower_input"
            ]
            is True
            and records[
                "all_drafts_unfinalized"
            ]
            is True
            and records["all_append_only"]
            is True
            and records["all_immutable"]
            is True
        ),
        "no_decision_or_execution_recorded": (
            records[
                "no_recording_gates_open"
            ]
            is True
            and records[
                "no_owner_selections_present"
            ]
            is True
            and records[
                "no_owner_decisions_recorded"
            ]
            is True
            and records[
                "no_go_decisions_granted"
            ]
            is True
            and records[
                "no_authorization_or_tokens"
            ]
            is True
            and records[
                "no_commit_restore_or_write"
            ]
            is True
        ),

        "receipt_drafts_present": (
            receipts["receipt_count"] >= 1
        ),
        "receipt_drafts_safe": (
            receipts["all_tower_controlled"]
            is True
            and receipts[
                "all_gate_definition_components_recorded"
            ]
            is True
            and receipts[
                "no_owner_selection_or_decision_recorded"
            ]
            is True
            and receipts[
                "no_authorization_or_tokens_recorded"
            ]
            is True
            and receipts[
                "no_commit_restore_or_write_recorded"
            ]
            is True
            and receipts[
                "no_raw_or_public_recorded"
            ]
            is True
            and receipts["all_receipts_draft"]
            is True
            and receipts["all_append_only"]
            is True
            and receipts["all_immutable"]
            is True
        ),

        "blockers_ready": (
            blockers[
                "all_dangerous_actions_blocked"
            ]
            is True
        ),

        "global_locks_preserved": all(
            [
                LOCKS["recording_gate_open"]
                is False,
                LOCKS[
                    "recording_execution_allowed"
                ]
                is False,
                LOCKS[
                    "review_session_started"
                ]
                is False,
                LOCKS["owner_authenticated"]
                is False,
                LOCKS[
                    "owner_selection_present"
                ]
                is False,
                LOCKS[
                    "owner_decision_recorded"
                ]
                is False,
                LOCKS["go_decision_granted"]
                is False,
                LOCKS[
                    "owner_admin_approval_granted"
                ]
                is False,
                LOCKS["step_up_satisfied"]
                is False,
                LOCKS["dual_receipt_satisfied"]
                is False,
                LOCKS[
                    "second_authority_review_granted"
                ]
                is False,
                LOCKS[
                    "live_recovery_authorization_granted"
                ]
                is False,
                LOCKS[
                    "authorization_token_issued"
                ]
                is False,
                LOCKS[
                    "scope_freeze_activated"
                ]
                is False,
                LOCKS[
                    "commit_window_activated"
                ]
                is False,
                LOCKS["execution_window_open"]
                is False,
                LOCKS["commit_point_open"]
                is False,
                LOCKS["commit_command_issued"]
                is False,
                LOCKS[
                    "actual_restore_execution_allowed"
                ]
                is False,
                LOCKS[
                    "production_recovery_write_allowed"
                ]
                is False,
                LOCKS[
                    "external_provider_connection_allowed"
                ]
                is False,
                LOCKS[
                    "raw_file_bytes_returned_by_json"
                ]
                is False,
                LOCKS[
                    "raw_file_bytes_materialized"
                ]
                is False,
                LOCKS["raw_path_exposed"]
                is False,
                LOCKS["raw_file_url_exposed"]
                is False,
                LOCKS[
                    "raw_recovery_token_exposed"
                ]
                is False,
                LOCKS["public_url_created"]
                is False,
                LOCKS["share_link_created"]
                is False,
                LOCKS[
                    "teller_to_vault_direct_call_allowed"
                ]
                is False,
                LOCKS[
                    "resident_vault_access_allowed"
                ]
                is False,
                LOCKS[
                    "vendor_vault_access_allowed"
                ]
                is False,
                LOCKS[
                    "public_vault_access_allowed"
                ]
                is False,
                LOCKS["hard_delete_allowed"]
                is False,
                LOCKS["purge_allowed"]
                is False,
                LOCKS[
                    "quarantine_release_allowed"
                ]
                is False,
                LOCKS[
                    "physical_object_move_allowed"
                ]
                is False,
            ]
        ),
    }

    ready = all(checks.values())

    return {
        "section": SECTION,
        "gp": 620,
        "title": (
            "Owner Decision Recording Gate "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Recovery commit owner decision "
                "recording gate blocked"
            )
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "recording_gate_status": (
            "recording_contract_ready_"
            "identity_and_approval_prerequisites_pending_"
            "recording_gate_closed_"
            "no_owner_decision_recorded"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION RECORDING CLOSEOUT "
            "LAYER / GP621-GP630"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no recording gate open",
            "no recording execution allowed",
            "no Tower owner-review session started",
            "no owner authenticated",
            "no owner selection present",
            "no owner decision recorded",
            "no GO decision granted",
            "no owner/admin approval granted",
            "no step-up satisfied",
            "no dual receipt satisfied",
            "no second-authority review granted",
            "no live recovery authorization",
            "no authorization or capability token",
            "no scope-freeze activation",
            "no commit-window activation",
            "no execution window",
            "no commit point open",
            "no real commit command",
            "no actual restore execution",
            "no production mount or write",
            "no external provider connection",
            "no Teller-to-Vault direct call",
            "no resident, vendor, employee, customer, or public access",
            "no raw bytes, paths, URLs, or tokens",
            "no destructive action",
        ],
    }


def get_recovery_commit_owner_decision_recording_gate_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_recording_gate_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": (
            checkpoint["readiness_label"]
        ),
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "packs": PACKS,
        "checkpoint": checkpoint,
    }


def validate_recovery_commit_owner_decision_recording_gate(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_recording_gate_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert checkpoint["current_recommendation"] == (
        CURRENT_RECOMMENDATION
    )
    assert checkpoint["corridor_continues"] is True
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False

    for check_name, passed in checkpoint[
        "checks"
    ].items():
        assert passed is True, check_name

    return {
        "ok": True,
        "section": SECTION,
        "ready": True,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "readiness_label": (
            checkpoint["readiness_label"]
        ),
        "validated_at": _now(),
    }


def _gp_status(gp: int) -> Dict[str, Any]:
    pack = next(
        pack
        for pack in PACKS
        if pack["gp"] == gp
    )

    checkpoint = (
        get_owner_decision_recording_gate_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "recording_gate_open": False,
        "recording_execution_allowed": False,
        "review_session_started": False,
        "owner_authenticated": False,
        "owner_selection_present": False,
        "owner_decision_recorded": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "commit_point_open": False,
        "commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "locks_preserved": True,
    }


def get_gp611_status():
    return _gp_status(611)


def get_gp612_status():
    return _gp_status(612)


def get_gp613_status():
    return _gp_status(613)


def get_gp614_status():
    return _gp_status(614)


def get_gp615_status():
    return _gp_status(615)


def get_gp616_status():
    return _gp_status(616)


def get_gp617_status():
    return _gp_status(617)


def get_gp618_status():
    return _gp_status(618)


def get_gp619_status():
    return _gp_status(619)


def get_gp620_status():
    return _gp_status(620)
