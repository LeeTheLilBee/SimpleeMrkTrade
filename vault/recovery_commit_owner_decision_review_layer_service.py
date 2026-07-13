
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER "
    "DECISION REVIEW LAYER / GP601-GP610"
)

LAYER_ID = (
    "vault_gp601_610_"
    "recovery_commit_owner_decision_review_layer"
)

READINESS_LABEL = (
    "Recovery commit owner decision review ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_PENDING_OWNER_REVIEW_AND_CONTROLS"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_review_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_owner_decision_preparation_layer_service import (
        get_final_go_no_go_review_intake_board,
        get_owner_decision_criteria_matrix,
        get_owner_admin_control_decision_packet_board,
        get_scope_freeze_commit_window_activation_plan_draft_board,
        get_recovery_decision_alternatives_rationale_board,
        get_tower_owner_decision_record_draft_board,
        get_tower_owner_decision_receipt_draft_ledger,
        validate_recovery_commit_owner_decision_preparation_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP601-GP610 requires the completed "
        "GP591-GP600 owner decision preparation layer."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "tower_presents_owner_review": True,
    "vault_preserves_review_evidence": True,
    "owner_decision_review_only": True,
    "owner_decision_recording_allowed": False,
    "technical_readiness_is_not_authorization": True,
    "current_recommendation": CURRENT_RECOMMENDATION,
    "review_session_started": False,
    "owner_authenticated": False,
    "owner_decision_recorded": False,
    "go_decision_granted": False,
    "owner_admin_approval_granted": False,
    "step_up_satisfied": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,
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
    "owner_decision_review_layer": True,
    "preparation_intake_allowed": True,
    "tower_review_session_drafts_allowed": True,
    "control_satisfaction_review_allowed": True,
    "activation_decision_review_allowed": True,
    "option_evaluation_allowed": True,
    "owner_review_drafts_allowed": True,
    "owner_review_receipt_drafts_allowed": True,

    "review_session_started": False,
    "owner_authenticated": False,
    "owner_decision_recorded": False,
    "go_decision_granted": False,

    "live_recovery_authorization_granted": False,
    "authorization_token_issued": False,
    "recovery_capability_token_issued": False,
    "recovery_bypass_token_issued": False,

    "owner_admin_approval_granted": False,
    "step_up_satisfied": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,

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

    "teller_direct_review_allowed": False,
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
        "gp": 601,
        "title": (
            "Recovery Commit Owner Decision Review Shell"
        ),
        "route": (
            "/vault/recovery-commit-owner-decision-"
            "review-shell.json"
        ),
    },
    {
        "gp": 602,
        "title": (
            "Owner Decision Preparation Intake Board"
        ),
        "route": (
            "/vault/owner-decision-preparation-"
            "intake-board.json"
        ),
    },
    {
        "gp": 603,
        "title": (
            "Tower Owner Decision Review Session Board"
        ),
        "route": (
            "/vault/tower-owner-decision-review-"
            "session-board.json"
        ),
    },
    {
        "gp": 604,
        "title": (
            "Owner/Admin Control Satisfaction "
            "Review Board"
        ),
        "route": (
            "/vault/owner-admin-control-satisfaction-"
            "review-board.json"
        ),
    },
    {
        "gp": 605,
        "title": (
            "Scope Freeze and Commit Window "
            "Decision Review Board"
        ),
        "route": (
            "/vault/scope-freeze-commit-window-"
            "decision-review-board.json"
        ),
    },
    {
        "gp": 606,
        "title": (
            "Recovery Decision Option Evaluation Board"
        ),
        "route": (
            "/vault/recovery-decision-option-"
            "evaluation-board.json"
        ),
    },
    {
        "gp": 607,
        "title": (
            "Tower Owner Decision Review Draft Board"
        ),
        "route": (
            "/vault/tower-owner-decision-"
            "review-draft-board.json"
        ),
    },
    {
        "gp": 608,
        "title": (
            "Tower Owner Decision Review "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-owner-decision-review-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 609,
        "title": (
            "Owner Decision Review Safety Blocker Board"
        ),
        "route": (
            "/vault/owner-decision-review-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 610,
        "title": (
            "Owner Decision Review Readiness Checkpoint"
        ),
        "route": (
            "/vault/owner-decision-review-readiness.json"
        ),
    },
]


DECISION_OPTIONS = [
    {
        "decision": "MAINTAIN_NO_GO_HOLD",
        "available": True,
        "recommended": True,
        "effect": (
            "Keep all recovery, authorization, "
            "activation, and execution locks closed."
        ),
    },
    {
        "decision": "RETURN_FOR_REMEDIATION",
        "available": True,
        "recommended": False,
        "effect": (
            "Return the sealed decision packet for "
            "technical, evidence, scope, or control repair."
        ),
    },
    {
        "decision": "DEFER_OWNER_DECISION",
        "available": True,
        "recommended": False,
        "effect": (
            "Keep the package sealed and pending "
            "without changing recovery authority."
        ),
    },
    {
        "decision": "GRANT_GO",
        "available": False,
        "recommended": False,
        "effect": (
            "Unavailable until owner authentication, "
            "all controls, and the recording gate pass."
        ),
    },
]


BLOCKERS = [
    (
        "no_review_session_auto_start",
        "automatic_owner_review_session_start",
        "Vault cannot start the Tower owner session.",
    ),
    (
        "no_owner_authentication",
        "vault_owner_authentication",
        "Tower must authenticate and step up the owner.",
    ),
    (
        "no_automatic_owner_decision",
        "automatic_owner_decision",
        "Vault cannot select or record the owner decision.",
    ),
    (
        "no_go_without_owner_admin",
        "go_without_owner_admin_approval",
        "Owner/admin approval remains required.",
    ),
    (
        "no_go_without_step_up",
        "go_without_step_up",
        "Tower step-up remains required.",
    ),
    (
        "no_go_without_dual_receipt",
        "go_without_dual_receipt",
        "Dual receipt remains required.",
    ),
    (
        "no_go_without_second_authority",
        "go_without_second_authority_review",
        "Second-authority review remains required.",
    ),
    (
        "no_scope_freeze_activation",
        "scope_freeze_activation",
        "Review cannot activate the scope freeze.",
    ),
    (
        "no_commit_window_activation",
        "commit_window_activation",
        "Review cannot activate the commit window.",
    ),
    (
        "no_execution_window",
        "execution_window_open",
        "Review cannot open execution.",
    ),
    (
        "no_commit_point_open",
        "commit_point_open",
        "Review cannot open the commit point.",
    ),
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "Review cannot grant live authorization.",
    ),
    (
        "no_authorization_token",
        "authorization_token_issue",
        "Review cannot issue a recovery token.",
    ),
    (
        "no_real_commit_command",
        "real_commit_command",
        "Review cannot issue a real commit command.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "Review cannot execute restore.",
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
        "no_teller_direct_review",
        "teller_direct_owner_review",
        "Owner review is presented through Tower.",
    ),
    (
        "no_teller_vault_call",
        "teller_to_vault_direct_call",
        "Teller must route through Tower.",
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
        "Owner review returns metadata and hashes only.",
    ),
    (
        "no_destructive_action",
        "delete_purge_release_or_move",
        "Owner review cannot destroy or move evidence.",
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

    column_sql = ", ".join(columns)

    connection.execute(
        (
            f"INSERT INTO {table} "
            f"({column_sql}) "
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
        get_final_go_no_go_review_intake_board()
        .get("preparation_intakes", [])
    )

    criteria_rows = (
        get_owner_decision_criteria_matrix()
        .get("decision_criteria", [])
    )

    control_rows = (
        get_owner_admin_control_decision_packet_board()
        .get("owner_control_packets", [])
    )

    activation_rows = (
        get_scope_freeze_commit_window_activation_plan_draft_board()
        .get("activation_plan_drafts", [])
    )

    option_rows = (
        get_recovery_decision_alternatives_rationale_board()
        .get("alternative_reviews", [])
    )

    decision_rows = (
        get_tower_owner_decision_record_draft_board()
        .get("owner_decision_record_drafts", [])
    )

    receipt_rows = (
        get_tower_owner_decision_receipt_draft_ledger()
        .get("owner_decision_receipt_drafts", [])
    )

    criteria = _by_request(criteria_rows)
    controls = _by_request(control_rows)
    activations = _by_request(activation_rows)
    options = _by_request(option_rows)
    decisions = _by_request(decision_rows)
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
                "criteria": criteria.get(
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
                "decision": decisions.get(
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
        validate_recovery_commit_owner_decision_preparation_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS review_intakes (
                review_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                preparation_packet_verified INTEGER NOT NULL,
                criteria_verified INTEGER NOT NULL,
                controls_verified INTEGER NOT NULL,
                activation_plan_verified INTEGER NOT NULL,
                alternatives_verified INTEGER NOT NULL,
                decision_record_verified INTEGER NOT NULL,
                receipt_verified INTEGER NOT NULL,
                eligible_for_owner_decision_review INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS review_sessions (
                review_session_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_session_required INTEGER NOT NULL,
                owner_presence_required INTEGER NOT NULL,
                owner_identity_verification_required INTEGER NOT NULL,
                step_up_challenge_required INTEGER NOT NULL,
                dual_receipt_review_required INTEGER NOT NULL,
                second_authority_review_required INTEGER NOT NULL,
                session_started INTEGER NOT NULL,
                owner_authenticated INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                session_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS control_satisfaction_reviews (
                control_review_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                second_authority_review_required INTEGER NOT NULL,
                owner_admin_approval_granted INTEGER NOT NULL,
                step_up_satisfied INTEGER NOT NULL,
                dual_receipt_satisfied INTEGER NOT NULL,
                second_authority_review_granted INTEGER NOT NULL,
                control_gate_complete INTEGER NOT NULL,
                no_go_hold_required INTEGER NOT NULL,
                control_review_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS activation_decision_reviews (
                activation_review_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                exact_scope_bound INTEGER NOT NULL,
                one_time_commit_window_required INTEGER NOT NULL,
                scope_freeze_activation_required INTEGER NOT NULL,
                commit_window_activation_required INTEGER NOT NULL,
                execution_window_required INTEGER NOT NULL,
                commit_point_activation_required INTEGER NOT NULL,
                scope_freeze_activated INTEGER NOT NULL,
                commit_window_activated INTEGER NOT NULL,
                execution_window_open INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                activation_decision_recorded INTEGER NOT NULL,
                activation_gate_complete INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                activation_review_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS option_evaluations (
                option_evaluation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                options_json TEXT NOT NULL,
                available_option_count INTEGER NOT NULL,
                maintain_hold_available INTEGER NOT NULL,
                remediation_available INTEGER NOT NULL,
                defer_available INTEGER NOT NULL,
                go_available INTEGER NOT NULL,
                owner_selection_pending INTEGER NOT NULL,
                current_recommendation TEXT NOT NULL,
                option_evaluation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS owner_decision_review_drafts (
                review_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                review_session_id TEXT NOT NULL,
                control_review_id TEXT NOT NULL,
                activation_review_id TEXT NOT NULL,
                option_evaluation_id TEXT NOT NULL,
                state TEXT NOT NULL,
                preparation_packet_complete INTEGER NOT NULL,
                review_session_ready INTEGER NOT NULL,
                controls_pending INTEGER NOT NULL,
                activation_pending INTEGER NOT NULL,
                owner_selection_pending INTEGER NOT NULL,
                current_recommendation TEXT NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                go_decision_granted INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                review_draft_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS review_receipt_drafts (
                review_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                review_draft_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                preparation_packet_recorded INTEGER NOT NULL,
                review_session_requirements_recorded INTEGER NOT NULL,
                control_status_recorded INTEGER NOT NULL,
                activation_status_recorded INTEGER NOT NULL,
                options_recorded INTEGER NOT NULL,
                owner_selection_pending_recorded INTEGER NOT NULL,
                recommendation_recorded INTEGER NOT NULL,
                final_owner_decision_recorded INTEGER NOT NULL,
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
            "review_intakes",
            "review_sessions",
            "control_satisfaction_reviews",
            "activation_decision_reviews",
            "option_evaluations",
            "owner_decision_review_drafts",
            "review_receipt_drafts",
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
            criteria = source["criteria"]
            control = source["control"]
            activation = source["activation"]
            options = source["options"]
            decision = source["decision"]
            receipt = source["receipt"]

            preparation_packet_verified = all(
                [
                    bool(
                        intake.get(
                            "final_review_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "technical_dry_run_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "technical_evidence_complete",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "approval_gate_pending",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "activation_gate_pending",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "current_no_go_hold_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_owner_decision_preparation",
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

            criteria_verified = all(
                [
                    bool(
                        criteria.get(
                            "technical_readiness_passed",
                            0,
                        )
                    ),
                    bool(
                        criteria.get(
                            "evidence_integrity_passed",
                            0,
                        )
                    ),
                    bool(
                        criteria.get(
                            "barrier_readiness_passed",
                            0,
                        )
                    ),
                    not bool(
                        criteria.get(
                            "approval_gate_complete",
                            1,
                        )
                    ),
                    not bool(
                        criteria.get(
                            "activation_gate_complete",
                            1,
                        )
                    ),
                    not bool(
                        criteria.get(
                            "go_eligible",
                            1,
                        )
                    ),
                    bool(
                        criteria.get(
                            "no_go_hold_required",
                            0,
                        )
                    ),
                    not bool(
                        criteria.get(
                            "remediation_required",
                            1,
                        )
                    ),
                    len(
                        criteria.get(
                            "criteria_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            controls_verified = all(
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
                    bool(
                        control.get(
                            "tower_only_presentation",
                            0,
                        )
                    ),
                    not bool(
                        control.get(
                            "vault_decision_authority",
                            1,
                        )
                    ),
                    not bool(
                        control.get(
                            "teller_decision_authority",
                            1,
                        )
                    ),
                    len(
                        control.get(
                            "control_packet_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            activation_plan_verified = all(
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
                            "activation_plan_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            alternatives_verified = all(
                [
                    int(
                        options.get(
                            "available_alternative_count",
                            0,
                        )
                    )
                    == 3,
                    not bool(
                        options.get(
                            "go_option_available",
                            1,
                        )
                    ),
                    bool(
                        options.get(
                            "no_go_hold_available",
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
                    len(
                        options.get(
                            "rationale_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            decision_record_verified = all(
                [
                    bool(
                        decision.get(
                            "technical_review_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "criteria_matrix_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "control_packet_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "activation_plan_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "alternatives_review_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "owner_decision_pending",
                            0,
                        )
                    ),
                    not bool(
                        decision.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "go_decision_granted",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "live_authorization_granted",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "authorization_token_issued",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "commit_command_issued",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "actual_restore_allowed",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "production_write_allowed",
                            1,
                        )
                    ),
                    len(
                        decision.get(
                            "decision_record_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "technical_review_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "criteria_matrix_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "control_packet_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "activation_plan_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "alternatives_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "owner_decision_pending_recorded",
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

            eligible_for_review = all(
                [
                    preparation_packet_verified,
                    criteria_verified,
                    controls_verified,
                    activation_plan_verified,
                    alternatives_verified,
                    decision_record_verified,
                    receipt_verified,
                ]
            )

            review_intake_id = _id(
                "owner_decision_review_intake",
                request_id,
            )

            review_session_id = _id(
                "tower_owner_review_session",
                request_id,
            )

            control_review_id = _id(
                "owner_control_satisfaction_review",
                request_id,
            )

            activation_review_id = _id(
                "activation_decision_review",
                request_id,
            )

            option_evaluation_id = _id(
                "owner_decision_option_evaluation",
                request_id,
            )

            review_draft_id = _id(
                "tower_owner_decision_review",
                request_id,
            )

            review_receipt_id = _id(
                "tower_owner_review_receipt",
                request_id,
            )

            _insert_row(
                connection,
                "review_intakes",
                {
                    "review_intake_id": review_intake_id,
                    "request_id": request_id,
                    "workflow_type": workflow_type,
                    "state": (
                        "owner_decision_packet_verified_"
                        "ready_for_tower_review_only"
                    ),
                    "preparation_packet_verified": int(
                        preparation_packet_verified
                    ),
                    "criteria_verified": int(
                        criteria_verified
                    ),
                    "controls_verified": int(
                        controls_verified
                    ),
                    "activation_plan_verified": int(
                        activation_plan_verified
                    ),
                    "alternatives_verified": int(
                        alternatives_verified
                    ),
                    "decision_record_verified": int(
                        decision_record_verified
                    ),
                    "receipt_verified": int(
                        receipt_verified
                    ),
                    "eligible_for_owner_decision_review": int(
                        eligible_for_review
                    ),
                    "owner_decision_recorded": 0,
                    "live_authorization_granted": 0,
                    "created_at": now,
                },
            )

            session_payload = {
                "request_id": request_id,
                "tower_session_required": True,
                "owner_presence_required": True,
                "owner_identity_verification_required": True,
                "step_up_challenge_required": True,
                "dual_receipt_review_required": True,
                "second_authority_review_required": True,
                "session_started": False,
                "owner_authenticated": False,
                "owner_decision_recorded": False,
            }

            session_hash = _canonical_hash(
                session_payload
            )

            _insert_row(
                connection,
                "review_sessions",
                {
                    "review_session_id": review_session_id,
                    "request_id": request_id,
                    "state": (
                        "tower_owner_review_session_"
                        "requirements_ready_not_started"
                    ),
                    "tower_session_required": 1,
                    "owner_presence_required": 1,
                    "owner_identity_verification_required": 1,
                    "step_up_challenge_required": 1,
                    "dual_receipt_review_required": 1,
                    "second_authority_review_required": 1,
                    "session_started": 0,
                    "owner_authenticated": 0,
                    "owner_decision_recorded": 0,
                    "session_hash": session_hash,
                    "created_at": now,
                },
            )

            control_payload = {
                "request_id": request_id,
                "owner_admin_approval_required": True,
                "step_up_required": True,
                "dual_receipt_required": True,
                "second_authority_review_required": True,
                "owner_admin_approval_granted": False,
                "step_up_satisfied": False,
                "dual_receipt_satisfied": False,
                "second_authority_review_granted": False,
                "control_gate_complete": False,
                "no_go_hold_required": True,
            }

            control_review_hash = _canonical_hash(
                control_payload
            )

            _insert_row(
                connection,
                "control_satisfaction_reviews",
                {
                    "control_review_id": control_review_id,
                    "request_id": request_id,
                    "state": (
                        "owner_control_review_"
                        "all_controls_pending"
                    ),
                    "owner_admin_approval_required": 1,
                    "step_up_required": 1,
                    "dual_receipt_required": 1,
                    "second_authority_review_required": 1,
                    "owner_admin_approval_granted": 0,
                    "step_up_satisfied": 0,
                    "dual_receipt_satisfied": 0,
                    "second_authority_review_granted": 0,
                    "control_gate_complete": 0,
                    "no_go_hold_required": 1,
                    "control_review_hash": (
                        control_review_hash
                    ),
                    "created_at": now,
                },
            )

            activation_payload = {
                "request_id": request_id,
                "exact_scope_bound": True,
                "one_time_commit_window_required": True,
                "scope_freeze_activation_required": True,
                "commit_window_activation_required": True,
                "execution_window_required": True,
                "commit_point_activation_required": True,
                "scope_freeze_activated": False,
                "commit_window_activated": False,
                "execution_window_open": False,
                "commit_point_open": False,
                "activation_decision_recorded": False,
                "activation_gate_complete": False,
                "production_target_allowed": False,
                "external_provider_allowed": False,
            }

            activation_review_hash = _canonical_hash(
                activation_payload
            )

            _insert_row(
                connection,
                "activation_decision_reviews",
                {
                    "activation_review_id": (
                        activation_review_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "activation_decision_review_"
                        "exact_plan_verified_not_activated"
                    ),
                    "exact_scope_bound": 1,
                    "one_time_commit_window_required": 1,
                    "scope_freeze_activation_required": 1,
                    "commit_window_activation_required": 1,
                    "execution_window_required": 1,
                    "commit_point_activation_required": 1,
                    "scope_freeze_activated": 0,
                    "commit_window_activated": 0,
                    "execution_window_open": 0,
                    "commit_point_open": 0,
                    "activation_decision_recorded": 0,
                    "activation_gate_complete": 0,
                    "production_target_allowed": 0,
                    "external_provider_allowed": 0,
                    "activation_review_hash": (
                        activation_review_hash
                    ),
                    "created_at": now,
                },
            )

            options_json = json.dumps(
                DECISION_OPTIONS,
                sort_keys=True,
                separators=(",", ":"),
            )

            option_payload = {
                "request_id": request_id,
                "decision_options": DECISION_OPTIONS,
                "available_option_count": 3,
                "maintain_hold_available": True,
                "remediation_available": True,
                "defer_available": True,
                "go_available": False,
                "owner_selection_pending": True,
                "current_recommendation": (
                    CURRENT_RECOMMENDATION
                ),
            }

            option_evaluation_hash = _canonical_hash(
                option_payload
            )

            _insert_row(
                connection,
                "option_evaluations",
                {
                    "option_evaluation_id": (
                        option_evaluation_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "owner_decision_options_reviewed_"
                        "go_unavailable_selection_pending"
                    ),
                    "options_json": options_json,
                    "available_option_count": 3,
                    "maintain_hold_available": 1,
                    "remediation_available": 1,
                    "defer_available": 1,
                    "go_available": 0,
                    "owner_selection_pending": 1,
                    "current_recommendation": (
                        CURRENT_RECOMMENDATION
                    ),
                    "option_evaluation_hash": (
                        option_evaluation_hash
                    ),
                    "created_at": now,
                },
            )

            review_payload = {
                "request_id": request_id,
                "review_session_id": review_session_id,
                "control_review_id": control_review_id,
                "activation_review_id": (
                    activation_review_id
                ),
                "option_evaluation_id": (
                    option_evaluation_id
                ),
                "preparation_packet_complete": True,
                "review_session_ready": True,
                "controls_pending": True,
                "activation_pending": True,
                "owner_selection_pending": True,
                "current_recommendation": (
                    CURRENT_RECOMMENDATION
                ),
                "owner_decision_recorded": False,
                "go_decision_granted": False,
                "live_authorization_granted": False,
                "authorization_token_issued": False,
                "commit_command_issued": False,
                "actual_restore_allowed": False,
                "production_write_allowed": False,
            }

            review_draft_hash = _canonical_hash(
                review_payload
            )

            _insert_row(
                connection,
                "owner_decision_review_drafts",
                {
                    "review_draft_id": review_draft_id,
                    "request_id": request_id,
                    "review_session_id": review_session_id,
                    "control_review_id": control_review_id,
                    "activation_review_id": (
                        activation_review_id
                    ),
                    "option_evaluation_id": (
                        option_evaluation_id
                    ),
                    "state": (
                        "tower_owner_decision_review_"
                        "draft_ready_decision_not_recorded"
                    ),
                    "preparation_packet_complete": 1,
                    "review_session_ready": 1,
                    "controls_pending": 1,
                    "activation_pending": 1,
                    "owner_selection_pending": 1,
                    "current_recommendation": (
                        CURRENT_RECOMMENDATION
                    ),
                    "owner_decision_recorded": 0,
                    "go_decision_granted": 0,
                    "live_authorization_granted": 0,
                    "authorization_token_issued": 0,
                    "commit_command_issued": 0,
                    "actual_restore_allowed": 0,
                    "production_write_allowed": 0,
                    "review_draft_hash": review_draft_hash,
                    "created_at": now,
                },
            )

            receipt_payload = {
                "request_id": request_id,
                "review_draft_id": review_draft_id,
                "preparation_packet_recorded": True,
                "review_session_requirements_recorded": True,
                "control_status_recorded": True,
                "activation_status_recorded": True,
                "options_recorded": True,
                "owner_selection_pending_recorded": True,
                "recommendation_recorded": True,
                "final_owner_decision_recorded": False,
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
                "review_receipt_drafts",
                {
                    "review_receipt_id": (
                        review_receipt_id
                    ),
                    "request_id": request_id,
                    "review_draft_id": review_draft_id,
                    "state": (
                        "tower_owner_decision_review_"
                        "receipt_draft"
                    ),
                    "tower_controlled": 1,
                    "preparation_packet_recorded": 1,
                    "review_session_requirements_recorded": 1,
                    "control_status_recorded": 1,
                    "activation_status_recorded": 1,
                    "options_recorded": 1,
                    "owner_selection_pending_recorded": 1,
                    "recommendation_recorded": 1,
                    "final_owner_decision_recorded": 0,
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
        "previous_preparation_layer_ready": bool(
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


def get_recovery_commit_owner_decision_review_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 601,
        "title": (
            "Recovery Commit Owner Decision Review Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "owner_decision_review_only": True,
        "review_session_started": False,
        "owner_authenticated": False,
        "owner_decision_recorded": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "commit_point_open": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_owner_decision_preparation_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM review_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 602,
        "title": (
            "Owner Decision Preparation Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "review_intakes": rows,
        "all_preparation_packets_verified": all(
            bool(row["preparation_packet_verified"])
            for row in rows
        ),
        "all_criteria_verified": all(
            bool(row["criteria_verified"])
            for row in rows
        ),
        "all_controls_verified": all(
            bool(row["controls_verified"])
            for row in rows
        ),
        "all_activation_plans_verified": all(
            bool(row["activation_plan_verified"])
            for row in rows
        ),
        "all_alternatives_verified": all(
            bool(row["alternatives_verified"])
            for row in rows
        ),
        "all_decision_records_verified": all(
            bool(row["decision_record_verified"])
            for row in rows
        ),
        "all_receipts_verified": all(
            bool(row["receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_owner_review": all(
            bool(
                row[
                    "eligible_for_owner_decision_review"
                ]
            )
            for row in rows
        ),
        "no_owner_decisions_recorded": all(
            not bool(row["owner_decision_recorded"])
            for row in rows
        ),
        "no_live_authorization_granted": all(
            not bool(row["live_authorization_granted"])
            for row in rows
        ),
    }


def get_tower_owner_decision_review_session_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM review_sessions
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 603,
        "title": (
            "Tower Owner Decision Review Session Board"
        ),
        "ready": True,
        "session_count": len(rows),
        "review_sessions": rows,
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
        "all_step_up_challenges_required": all(
            bool(row["step_up_challenge_required"])
            for row in rows
        ),
        "all_dual_receipt_reviews_required": all(
            bool(row["dual_receipt_review_required"])
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
        "no_sessions_started": all(
            not bool(row["session_started"])
            for row in rows
        ),
        "no_owners_authenticated": all(
            not bool(row["owner_authenticated"])
            for row in rows
        ),
        "no_owner_decisions_recorded": all(
            not bool(row["owner_decision_recorded"])
            for row in rows
        ),
        "all_session_hashes_present": all(
            len(row["session_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_admin_control_satisfaction_review_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM control_satisfaction_reviews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 604,
        "title": (
            "Owner/Admin Control Satisfaction "
            "Review Board"
        ),
        "ready": True,
        "review_count": len(rows),
        "control_satisfaction_reviews": rows,
        "all_owner_admin_approval_required": all(
            bool(row["owner_admin_approval_required"])
            for row in rows
        ),
        "all_step_up_required": all(
            bool(row["step_up_required"])
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
        "no_owner_admin_approval_granted": all(
            not bool(row["owner_admin_approval_granted"])
            for row in rows
        ),
        "no_step_up_satisfied": all(
            not bool(row["step_up_satisfied"])
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
        "no_control_gates_complete": all(
            not bool(row["control_gate_complete"])
            for row in rows
        ),
        "all_no_go_holds_required": all(
            bool(row["no_go_hold_required"])
            for row in rows
        ),
        "all_control_hashes_present": all(
            len(row["control_review_hash"]) == 64
            for row in rows
        ),
    }


def get_scope_freeze_commit_window_decision_review_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM activation_decision_reviews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 605,
        "title": (
            "Scope Freeze and Commit Window "
            "Decision Review Board"
        ),
        "ready": True,
        "review_count": len(rows),
        "activation_decision_reviews": rows,
        "all_exact_scopes_bound": all(
            bool(row["exact_scope_bound"])
            for row in rows
        ),
        "all_one_time_windows_required": all(
            bool(row["one_time_commit_window_required"])
            for row in rows
        ),
        "all_activation_steps_required": all(
            bool(
                row["scope_freeze_activation_required"]
            )
            and bool(
                row["commit_window_activation_required"]
            )
            and bool(row["execution_window_required"])
            and bool(
                row["commit_point_activation_required"]
            )
            for row in rows
        ),
        "nothing_activated": all(
            not bool(row["scope_freeze_activated"])
            and not bool(row["commit_window_activated"])
            and not bool(row["execution_window_open"])
            and not bool(row["commit_point_open"])
            for row in rows
        ),
        "no_activation_decisions_recorded": all(
            not bool(
                row["activation_decision_recorded"]
            )
            for row in rows
        ),
        "no_activation_gates_complete": all(
            not bool(row["activation_gate_complete"])
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
        "all_activation_hashes_present": all(
            len(row["activation_review_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_decision_option_evaluation_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM option_evaluations
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 606,
        "title": (
            "Recovery Decision Option Evaluation Board"
        ),
        "ready": True,
        "evaluation_count": len(rows),
        "option_evaluations": rows,
        "decision_options": DECISION_OPTIONS,
        "all_have_three_available_options": all(
            row["available_option_count"] == 3
            for row in rows
        ),
        "all_hold_options_available": all(
            bool(row["maintain_hold_available"])
            for row in rows
        ),
        "all_remediation_options_available": all(
            bool(row["remediation_available"])
            for row in rows
        ),
        "all_defer_options_available": all(
            bool(row["defer_available"])
            for row in rows
        ),
        "no_go_options_available": all(
            not bool(row["go_available"])
            for row in rows
        ),
        "all_owner_selections_pending": all(
            bool(row["owner_selection_pending"])
            for row in rows
        ),
        "all_recommendations_are_no_go_hold": all(
            row["current_recommendation"]
            == CURRENT_RECOMMENDATION
            for row in rows
        ),
        "all_option_hashes_present": all(
            len(row["option_evaluation_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_review_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM owner_decision_review_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 607,
        "title": (
            "Tower Owner Decision Review Draft Board"
        ),
        "ready": True,
        "draft_count": len(rows),
        "owner_decision_review_drafts": rows,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "all_preparation_packets_complete": all(
            bool(row["preparation_packet_complete"])
            for row in rows
        ),
        "all_review_sessions_ready": all(
            bool(row["review_session_ready"])
            for row in rows
        ),
        "all_controls_pending": all(
            bool(row["controls_pending"])
            for row in rows
        ),
        "all_activations_pending": all(
            bool(row["activation_pending"])
            for row in rows
        ),
        "all_owner_selections_pending": all(
            bool(row["owner_selection_pending"])
            for row in rows
        ),
        "all_recommendations_are_no_go_hold": all(
            row["current_recommendation"]
            == CURRENT_RECOMMENDATION
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
        "all_review_hashes_present": all(
            len(row["review_draft_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_review_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM review_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 608,
        "title": (
            "Tower Owner Decision Review "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "review_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_review_components_recorded": all(
            bool(row["preparation_packet_recorded"])
            and bool(
                row[
                    "review_session_requirements_recorded"
                ]
            )
            and bool(row["control_status_recorded"])
            and bool(row["activation_status_recorded"])
            and bool(row["options_recorded"])
            and bool(
                row[
                    "owner_selection_pending_recorded"
                ]
            )
            and bool(row["recommendation_recorded"])
            for row in rows
        ),
        "no_final_owner_decisions_recorded": all(
            not bool(
                row["final_owner_decision_recorded"]
            )
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


def get_owner_decision_review_safety_blocker_board(
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
        "gp": 609,
        "title": (
            "Owner Decision Review Safety Blocker Board"
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


def get_owner_decision_review_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_recovery_commit_owner_decision_review_shell()
    )

    intakes = (
        get_owner_decision_preparation_intake_board()
    )

    sessions = (
        get_tower_owner_decision_review_session_board()
    )

    controls = (
        get_owner_admin_control_satisfaction_review_board()
    )

    activations = (
        get_scope_freeze_commit_window_decision_review_board()
    )

    options = (
        get_recovery_decision_option_evaluation_board()
    )

    drafts = (
        get_tower_owner_decision_review_draft_board()
    )

    receipts = (
        get_tower_owner_decision_review_receipt_draft_ledger()
    )

    blockers = (
        get_owner_decision_review_safety_blocker_board()
    )

    checks = {
        "previous_preparation_layer_ready": (
            initialized[
                "previous_preparation_layer_ready"
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
        "review_only": (
            DOCTRINE[
                "owner_decision_review_only"
            ]
            is True
            and DOCTRINE[
                "owner_decision_recording_allowed"
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
        "prepared_packet_verified": (
            intakes[
                "all_preparation_packets_verified"
            ]
            is True
            and intakes[
                "all_criteria_verified"
            ]
            is True
            and intakes[
                "all_controls_verified"
            ]
            is True
            and intakes[
                "all_activation_plans_verified"
            ]
            is True
            and intakes[
                "all_alternatives_verified"
            ]
            is True
            and intakes[
                "all_decision_records_verified"
            ]
            is True
            and intakes[
                "all_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_owner_review"
            ]
            is True
        ),
        "intakes_no_decision_or_authorization": (
            intakes[
                "no_owner_decisions_recorded"
            ]
            is True
            and intakes[
                "no_live_authorization_granted"
            ]
            is True
        ),

        "sessions_present": (
            sessions["session_count"] >= 1
        ),
        "tower_review_requirements_ready": (
            sessions[
                "all_tower_sessions_required"
            ]
            is True
            and sessions[
                "all_owner_presence_required"
            ]
            is True
            and sessions[
                "all_identity_verification_required"
            ]
            is True
            and sessions[
                "all_step_up_challenges_required"
            ]
            is True
            and sessions[
                "all_dual_receipt_reviews_required"
            ]
            is True
            and sessions[
                "all_second_authority_reviews_required"
            ]
            is True
        ),
        "review_sessions_not_started": (
            sessions["no_sessions_started"]
            is True
            and sessions[
                "no_owners_authenticated"
            ]
            is True
            and sessions[
                "no_owner_decisions_recorded"
            ]
            is True
        ),

        "control_reviews_present": (
            controls["review_count"] >= 1
        ),
        "owner_controls_required": (
            controls[
                "all_owner_admin_approval_required"
            ]
            is True
            and controls[
                "all_step_up_required"
            ]
            is True
            and controls[
                "all_dual_receipts_required"
            ]
            is True
            and controls[
                "all_second_authority_reviews_required"
            ]
            is True
        ),
        "owner_controls_still_pending": (
            controls[
                "no_owner_admin_approval_granted"
            ]
            is True
            and controls[
                "no_step_up_satisfied"
            ]
            is True
            and controls[
                "no_dual_receipts_satisfied"
            ]
            is True
            and controls[
                "no_second_authority_granted"
            ]
            is True
            and controls[
                "no_control_gates_complete"
            ]
            is True
            and controls[
                "all_no_go_holds_required"
            ]
            is True
        ),

        "activation_reviews_present": (
            activations["review_count"] >= 1
        ),
        "activation_plan_verified": (
            activations[
                "all_exact_scopes_bound"
            ]
            is True
            and activations[
                "all_one_time_windows_required"
            ]
            is True
            and activations[
                "all_activation_steps_required"
            ]
            is True
        ),
        "activation_still_closed": (
            activations["nothing_activated"]
            is True
            and activations[
                "no_activation_decisions_recorded"
            ]
            is True
            and activations[
                "no_activation_gates_complete"
            ]
            is True
            and activations[
                "no_production_targets_allowed"
            ]
            is True
            and activations[
                "no_external_providers_allowed"
            ]
            is True
        ),

        "option_evaluations_present": (
            options["evaluation_count"] >= 1
        ),
        "decision_options_safe": (
            options[
                "all_have_three_available_options"
            ]
            is True
            and options[
                "all_hold_options_available"
            ]
            is True
            and options[
                "all_remediation_options_available"
            ]
            is True
            and options[
                "all_defer_options_available"
            ]
            is True
            and options[
                "no_go_options_available"
            ]
            is True
            and options[
                "all_owner_selections_pending"
            ]
            is True
            and options[
                "all_recommendations_are_no_go_hold"
            ]
            is True
        ),

        "review_drafts_present": (
            drafts["draft_count"] >= 1
        ),
        "owner_review_packet_ready": (
            drafts[
                "all_preparation_packets_complete"
            ]
            is True
            and drafts[
                "all_review_sessions_ready"
            ]
            is True
            and drafts[
                "all_controls_pending"
            ]
            is True
            and drafts[
                "all_activations_pending"
            ]
            is True
            and drafts[
                "all_owner_selections_pending"
            ]
            is True
            and drafts[
                "all_recommendations_are_no_go_hold"
            ]
            is True
        ),
        "no_owner_decision_or_execution": (
            drafts[
                "no_owner_decisions_recorded"
            ]
            is True
            and drafts[
                "no_go_decisions_granted"
            ]
            is True
            and drafts[
                "no_authorization_or_tokens"
            ]
            is True
            and drafts[
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
                "all_review_components_recorded"
            ]
            is True
            and receipts[
                "no_final_owner_decisions_recorded"
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
                LOCKS[
                    "review_session_started"
                ]
                is False,
                LOCKS["owner_authenticated"]
                is False,
                LOCKS[
                    "owner_decision_recorded"
                ]
                is False,
                LOCKS["go_decision_granted"]
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
        "gp": 610,
        "title": (
            "Owner Decision Review Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Recovery commit owner decision "
                "review blocked"
            )
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "review_status": (
            "owner_review_packet_ready_"
            "review_session_not_started_"
            "owner_decision_not_recorded_"
            "all_execution_locks_closed"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION RECORDING GATE / GP611-GP620"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no Tower owner-review session started",
            "no owner authenticated",
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


def get_recovery_commit_owner_decision_review_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_review_readiness_checkpoint()
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


def validate_recovery_commit_owner_decision_review_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_review_readiness_checkpoint()
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
        get_owner_decision_review_readiness_checkpoint()
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
        "review_session_started": False,
        "owner_authenticated": False,
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


def get_gp601_status():
    return _gp_status(601)


def get_gp602_status():
    return _gp_status(602)


def get_gp603_status():
    return _gp_status(603)


def get_gp604_status():
    return _gp_status(604)


def get_gp605_status():
    return _gp_status(605)


def get_gp606_status():
    return _gp_status(606)


def get_gp607_status():
    return _gp_status(607)


def get_gp608_status():
    return _gp_status(608)


def get_gp609_status():
    return _gp_status(609)


def get_gp610_status():
    return _gp_status(610)
