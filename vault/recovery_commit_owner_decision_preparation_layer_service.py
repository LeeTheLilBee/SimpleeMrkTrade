
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER "
    "DECISION PREPARATION LAYER / GP591-GP600"
)

LAYER_ID = (
    "vault_gp591_600_"
    "recovery_commit_owner_decision_preparation_layer"
)

READINESS_LABEL = (
    "Recovery commit owner decision preparation ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_PENDING_OWNER_CONTROL_DECISIONS"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_preparation_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_final_go_no_go_review_layer_service import (
        get_commit_dry_run_evidence_review_intake_board,
        get_final_commit_preconditions_revalidation_board,
        get_owner_admin_approval_decision_review_board,
        get_scope_freeze_commit_window_review_board,
        get_write_barrier_rollback_readiness_review_board,
        get_tower_final_go_no_go_decision_draft_board,
        get_tower_final_go_no_go_review_receipt_draft_ledger,
        validate_recovery_commit_final_go_no_go_review_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP591-GP600 requires the completed "
        "GP581-GP590 final go-no-go review layer."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "owner_decision_preparation_only": True,
    "tower_presents_owner_decision_packet": True,
    "vault_preserves_sealed_decision_evidence": True,
    "technical_readiness_is_not_authorization": True,
    "current_recommendation": CURRENT_RECOMMENDATION,
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
    "owner_decision_preparation_layer": True,
    "final_review_intake_allowed": True,
    "decision_criteria_matrix_allowed": True,
    "owner_control_packet_allowed": True,
    "activation_plan_drafts_allowed": True,
    "decision_alternative_reviews_allowed": True,
    "owner_decision_record_drafts_allowed": True,
    "owner_decision_receipt_drafts_allowed": True,

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
        "gp": 591,
        "title": (
            "Recovery Commit Owner Decision "
            "Preparation Shell"
        ),
        "route": (
            "/vault/recovery-commit-owner-decision-"
            "preparation-shell.json"
        ),
    },
    {
        "gp": 592,
        "title": "Final Go/No-Go Review Intake Board",
        "route": (
            "/vault/final-go-no-go-"
            "review-intake-board.json"
        ),
    },
    {
        "gp": 593,
        "title": "Owner Decision Criteria Matrix",
        "route": (
            "/vault/owner-decision-criteria-matrix.json"
        ),
    },
    {
        "gp": 594,
        "title": (
            "Owner/Admin Control Decision Packet Board"
        ),
        "route": (
            "/vault/owner-admin-control-"
            "decision-packet-board.json"
        ),
    },
    {
        "gp": 595,
        "title": (
            "Scope Freeze and Commit Window "
            "Activation Plan Draft Board"
        ),
        "route": (
            "/vault/scope-freeze-commit-window-"
            "activation-plan-draft-board.json"
        ),
    },
    {
        "gp": 596,
        "title": (
            "Recovery Decision Alternatives "
            "and Rationale Board"
        ),
        "route": (
            "/vault/recovery-decision-alternatives-"
            "rationale-board.json"
        ),
    },
    {
        "gp": 597,
        "title": (
            "Tower Owner Decision Record Draft Board"
        ),
        "route": (
            "/vault/tower-owner-decision-"
            "record-draft-board.json"
        ),
    },
    {
        "gp": 598,
        "title": (
            "Tower Owner Decision Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-owner-decision-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 599,
        "title": (
            "Owner Decision Preparation "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/owner-decision-preparation-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 600,
        "title": (
            "Owner Decision Preparation "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/owner-decision-"
            "preparation-readiness.json"
        ),
    },
]


DECISION_ALTERNATIVES = [
    {
        "decision": "MAINTAIN_NO_GO_HOLD",
        "available_now": True,
        "recommended_now": True,
        "effect": (
            "Preserve every recovery lock and return "
            "no execution authority."
        ),
    },
    {
        "decision": "RETURN_FOR_REMEDIATION",
        "available_now": True,
        "recommended_now": False,
        "effect": (
            "Return the package for technical, evidence, "
            "scope, or control remediation."
        ),
    },
    {
        "decision": "DEFER_OWNER_DECISION",
        "available_now": True,
        "recommended_now": False,
        "effect": (
            "Keep the package sealed and pending without "
            "opening any recovery control."
        ),
    },
    {
        "decision": "GRANT_GO",
        "available_now": False,
        "recommended_now": False,
        "effect": (
            "Unavailable until all owner controls and "
            "activation prerequisites are satisfied."
        ),
    },
]


BLOCKERS = [
    (
        "no_automatic_owner_decision",
        "automatic_owner_go_decision",
        "Vault cannot make the owner decision.",
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
        "Second authority review remains required.",
    ),
    (
        "no_scope_freeze_activation",
        "scope_freeze_activation",
        "Preparation cannot activate scope freeze.",
    ),
    (
        "no_commit_window_activation",
        "commit_window_activation",
        "Preparation cannot activate the commit window.",
    ),
    (
        "no_execution_window",
        "execution_window_open",
        "Preparation cannot open execution.",
    ),
    (
        "no_commit_point_open",
        "commit_point_open",
        "Preparation cannot open the commit point.",
    ),
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "Preparation cannot grant live authorization.",
    ),
    (
        "no_authorization_token",
        "authorization_token_issue",
        "Preparation cannot issue a token.",
    ),
    (
        "no_real_commit_command",
        "real_commit_command",
        "Preparation cannot issue a commit command.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "Preparation cannot execute restore.",
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
        "no_teller_direct_decision",
        "teller_direct_owner_decision",
        "Owner decisions are presented through Tower.",
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
        "Decision preparation returns metadata only.",
    ),
    (
        "no_destructive_action",
        "delete_purge_release_or_move",
        "Decision preparation cannot destroy or move evidence.",
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


def _source_rows() -> List[Dict[str, Any]]:
    intake_rows = (
        get_commit_dry_run_evidence_review_intake_board()
        .get("review_intakes", [])
    )

    precondition_rows = (
        get_final_commit_preconditions_revalidation_board()
        .get("revalidations", [])
    )

    approval_rows = (
        get_owner_admin_approval_decision_review_board()
        .get("approval_decision_reviews", [])
    )

    scope_rows = (
        get_scope_freeze_commit_window_review_board()
        .get("scope_window_reviews", [])
    )

    barrier_rows = (
        get_write_barrier_rollback_readiness_review_board()
        .get("barrier_readiness_reviews", [])
    )

    decision_rows = (
        get_tower_final_go_no_go_decision_draft_board()
        .get("decision_drafts", [])
    )

    receipt_rows = (
        get_tower_final_go_no_go_review_receipt_draft_ledger()
        .get("review_receipt_drafts", [])
    )

    by_request = lambda rows: {
        row["request_id"]: row
        for row in rows
    }

    preconditions = by_request(precondition_rows)
    approvals = by_request(approval_rows)
    scopes = by_request(scope_rows)
    barriers = by_request(barrier_rows)
    decisions = by_request(decision_rows)
    receipts = by_request(receipt_rows)

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
                "precondition": preconditions.get(
                    request_id,
                    {},
                ),
                "approval": approvals.get(
                    request_id,
                    {},
                ),
                "scope": scopes.get(
                    request_id,
                    {},
                ),
                "barrier": barriers.get(
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
        validate_recovery_commit_final_go_no_go_review_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS preparation_intakes (
                preparation_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                final_review_verified INTEGER NOT NULL,
                technical_dry_run_verified INTEGER NOT NULL,
                technical_evidence_complete INTEGER NOT NULL,
                approval_gate_pending INTEGER NOT NULL,
                activation_gate_pending INTEGER NOT NULL,
                current_no_go_hold_verified INTEGER NOT NULL,
                eligible_for_owner_decision_preparation INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_criteria (
                criteria_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                technical_readiness_passed INTEGER NOT NULL,
                evidence_integrity_passed INTEGER NOT NULL,
                barrier_readiness_passed INTEGER NOT NULL,
                approval_gate_complete INTEGER NOT NULL,
                activation_gate_complete INTEGER NOT NULL,
                go_eligible INTEGER NOT NULL,
                no_go_hold_required INTEGER NOT NULL,
                remediation_required INTEGER NOT NULL,
                criteria_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS owner_control_packets (
                control_packet_id TEXT PRIMARY KEY,
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
                tower_only_presentation INTEGER NOT NULL,
                vault_decision_authority INTEGER NOT NULL,
                teller_decision_authority INTEGER NOT NULL,
                control_packet_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS activation_plan_drafts (
                activation_plan_id TEXT PRIMARY KEY,
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
                production_target_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                activation_plan_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_alternative_reviews (
                alternative_review_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                alternatives_json TEXT NOT NULL,
                available_alternative_count INTEGER NOT NULL,
                go_option_available INTEGER NOT NULL,
                no_go_hold_available INTEGER NOT NULL,
                remediation_available INTEGER NOT NULL,
                defer_available INTEGER NOT NULL,
                current_recommendation TEXT NOT NULL,
                rationale_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS owner_decision_record_drafts (
                decision_record_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                technical_review_complete INTEGER NOT NULL,
                criteria_matrix_complete INTEGER NOT NULL,
                control_packet_complete INTEGER NOT NULL,
                activation_plan_complete INTEGER NOT NULL,
                alternatives_review_complete INTEGER NOT NULL,
                owner_decision_pending INTEGER NOT NULL,
                current_recommendation TEXT NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                go_decision_granted INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                decision_record_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS owner_decision_receipt_drafts (
                owner_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                decision_record_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                technical_review_recorded INTEGER NOT NULL,
                criteria_matrix_recorded INTEGER NOT NULL,
                control_packet_recorded INTEGER NOT NULL,
                activation_plan_recorded INTEGER NOT NULL,
                alternatives_recorded INTEGER NOT NULL,
                owner_decision_pending_recorded INTEGER NOT NULL,
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
            "preparation_intakes",
            "decision_criteria",
            "owner_control_packets",
            "activation_plan_drafts",
            "decision_alternative_reviews",
            "owner_decision_record_drafts",
            "owner_decision_receipt_drafts",
            "safety_blockers",
        ]:
            connection.execute(
                f"DELETE FROM {table}"
            )

        now = _now()

        for blocker_id, action, reason in BLOCKERS:
            connection.execute(
                """
                INSERT INTO safety_blockers (
                    blocker_id,
                    blocked_action,
                    allowed,
                    reason,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    blocker_id,
                    action,
                    0,
                    reason,
                    now,
                ),
            )

        for source in _source_rows():
            request_id = source["request_id"]
            workflow_type = source["workflow_type"]

            intake = source["intake"]
            precondition = source["precondition"]
            approval = source["approval"]
            scope = source["scope"]
            barrier = source["barrier"]
            decision = source["decision"]
            receipt = source["receipt"]

            technical_review_verified = all(
                [
                    bool(
                        intake.get(
                            "dry_run_intake_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "preconditions_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "sandbox_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "command_simulation_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "barrier_simulation_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "outcome_preview_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "dry_run_receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_final_review",
                            0,
                        )
                    ),
                    not bool(
                        intake.get(
                            "live_authorization_granted",
                            1,
                        )
                    ),
                    not bool(
                        intake.get(
                            "commit_point_open",
                            1,
                        )
                    ),
                ]
            )

            preconditions_verified = all(
                [
                    bool(
                        precondition.get(
                            "evidence_complete",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "tower_authority_reconfirmed",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "exact_scope_bound",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "one_time_window_required",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "all_approval_requirements_present",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "all_approval_decisions_pending",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "scope_freeze_inactive",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "commit_window_inactive",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "execution_window_closed",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "commit_point_closed",
                            0,
                        )
                    ),
                    not bool(
                        precondition.get(
                            "go_criteria_currently_met",
                            1,
                        )
                    ),
                    len(
                        precondition.get(
                            "revalidation_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            approval_gate_pending = all(
                [
                    bool(
                        approval.get(
                            "owner_admin_approval_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "step_up_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "dual_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "second_authority_review_required",
                            0,
                        )
                    ),
                    not bool(
                        approval.get(
                            "owner_admin_approval_granted",
                            1,
                        )
                    ),
                    not bool(
                        approval.get(
                            "step_up_satisfied",
                            1,
                        )
                    ),
                    not bool(
                        approval.get(
                            "dual_receipt_satisfied",
                            1,
                        )
                    ),
                    not bool(
                        approval.get(
                            "second_authority_review_granted",
                            1,
                        )
                    ),
                    not bool(
                        approval.get(
                            "approval_gate_complete",
                            1,
                        )
                    ),
                    bool(
                        approval.get(
                            "no_go_hold_required",
                            0,
                        )
                    ),
                ]
            )

            activation_gate_pending = all(
                [
                    bool(
                        scope.get(
                            "exact_scope_bound",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "one_time_window_required",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "scope_freeze_activation_required",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "commit_window_activation_required",
                            0,
                        )
                    ),
                    not bool(
                        scope.get(
                            "scope_freeze_activated",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "commit_window_activated",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "execution_window_open",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "commit_point_open",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "production_target_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "external_provider_allowed",
                            1,
                        )
                    ),
                ]
            )

            barrier_readiness_verified = all(
                [
                    bool(
                        barrier.get(
                            "command_sequence_simulated",
                            0,
                        )
                    ),
                    int(
                        barrier.get(
                            "real_commit_command_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "actual_restore_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "production_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "final_index_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "pack_overwrite_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "sealed_bytes_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "package_materialization_count",
                            1,
                        )
                    )
                    == 0,
                    bool(
                        barrier.get(
                            "all_write_barriers_engaged",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "abort_on_mismatch",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "rollback_on_mutation",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "expected_integrity_match",
                            0,
                        )
                    ),
                    int(
                        barrier.get(
                            "actual_mutation_count",
                            1,
                        )
                    )
                    == 0,
                ]
            )

            final_decision_hold_verified = all(
                [
                    bool(
                        decision.get(
                            "evidence_review_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "precondition_review_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "barrier_review_complete",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "eligible_for_owner_decision_review",
                            0,
                        )
                    ),
                    bool(
                        decision.get(
                            "technical_dry_run_passed",
                            0,
                        )
                    ),
                    not bool(
                        decision.get(
                            "approval_gate_complete",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "activation_gate_complete",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "go_decision_granted",
                            1,
                        )
                    ),
                    bool(
                        decision.get(
                            "no_go_hold_required",
                            0,
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
                            "decision_draft_hash",
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
                            "evidence_review_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "precondition_review_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "approval_review_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "scope_window_review_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "barrier_review_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "decision_draft_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "no_go_hold_recorded",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "go_decision_recorded",
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

            eligible_for_preparation = all(
                [
                    technical_review_verified,
                    preconditions_verified,
                    approval_gate_pending,
                    activation_gate_pending,
                    barrier_readiness_verified,
                    final_decision_hold_verified,
                    review_receipt_verified,
                ]
            )

            preparation_intake_id = _id(
                "owner_decision_preparation_intake",
                request_id,
            )

            criteria_id = _id(
                "owner_decision_criteria",
                request_id,
            )

            control_packet_id = _id(
                "owner_control_packet",
                request_id,
            )

            activation_plan_id = _id(
                "activation_plan_draft",
                request_id,
            )

            alternative_review_id = _id(
                "decision_alternative_review",
                request_id,
            )

            decision_record_id = _id(
                "owner_decision_record_draft",
                request_id,
            )

            owner_receipt_id = _id(
                "owner_decision_receipt_draft",
                request_id,
            )

            connection.execute(
                """
                INSERT INTO preparation_intakes (
                    preparation_intake_id,
                    request_id,
                    workflow_type,
                    state,
                    final_review_verified,
                    technical_dry_run_verified,
                    technical_evidence_complete,
                    approval_gate_pending,
                    activation_gate_pending,
                    current_no_go_hold_verified,
                    eligible_for_owner_decision_preparation,
                    owner_decision_recorded,
                    live_authorization_granted,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    preparation_intake_id,
                    request_id,
                    workflow_type,
                    (
                        "eligible_for_owner_decision_"
                        "preparation_no_decision_recorded"
                    ),
                    int(technical_review_verified),
                    int(barrier_readiness_verified),
                    int(preconditions_verified),
                    int(approval_gate_pending),
                    int(activation_gate_pending),
                    int(final_decision_hold_verified),
                    int(eligible_for_preparation),
                    0,
                    0,
                    now,
                ),
            )

            criteria_payload = {
                "request_id": request_id,
                "technical_readiness_passed": True,
                "evidence_integrity_passed": True,
                "barrier_readiness_passed": True,
                "approval_gate_complete": False,
                "activation_gate_complete": False,
                "go_eligible": False,
                "no_go_hold_required": True,
                "remediation_required": False,
            }

            criteria_hash = _canonical_hash(
                criteria_payload
            )

            connection.execute(
                """
                INSERT INTO decision_criteria (
                    criteria_id,
                    request_id,
                    state,
                    technical_readiness_passed,
                    evidence_integrity_passed,
                    barrier_readiness_passed,
                    approval_gate_complete,
                    activation_gate_complete,
                    go_eligible,
                    no_go_hold_required,
                    remediation_required,
                    criteria_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    criteria_id,
                    request_id,
                    (
                        "technical_criteria_passed_"
                        "owner_controls_pending"
                    ),
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    1,
                    0,
                    criteria_hash,
                    now,
                ),
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
                "tower_only_presentation": True,
                "vault_decision_authority": False,
                "teller_decision_authority": False,
            }

            control_packet_hash = _canonical_hash(
                control_payload
            )

            connection.execute(
                """
                INSERT INTO owner_control_packets (
                    control_packet_id,
                    request_id,
                    state,
                    owner_admin_approval_required,
                    step_up_required,
                    dual_receipt_required,
                    second_authority_review_required,
                    owner_admin_approval_granted,
                    step_up_satisfied,
                    dual_receipt_satisfied,
                    second_authority_review_granted,
                    tower_only_presentation,
                    vault_decision_authority,
                    teller_decision_authority,
                    control_packet_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    control_packet_id,
                    request_id,
                    (
                        "owner_control_packet_"
                        "complete_all_decisions_pending"
                    ),
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    1,
                    0,
                    0,
                    control_packet_hash,
                    now,
                ),
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
                "production_target_allowed": False,
                "external_provider_allowed": False,
            }

            activation_plan_hash = _canonical_hash(
                activation_payload
            )

            connection.execute(
                """
                INSERT INTO activation_plan_drafts (
                    activation_plan_id,
                    request_id,
                    state,
                    exact_scope_bound,
                    one_time_commit_window_required,
                    scope_freeze_activation_required,
                    commit_window_activation_required,
                    execution_window_required,
                    commit_point_activation_required,
                    scope_freeze_activated,
                    commit_window_activated,
                    execution_window_open,
                    commit_point_open,
                    production_target_allowed,
                    external_provider_allowed,
                    activation_plan_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    activation_plan_id,
                    request_id,
                    (
                        "activation_sequence_drafted_"
                        "nothing_activated"
                    ),
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    activation_plan_hash,
                    now,
                ),
            )

            alternatives_json = json.dumps(
                DECISION_ALTERNATIVES,
                sort_keys=True,
                separators=(",", ":"),
            )

            rationale_payload = {
                "request_id": request_id,
                "alternatives": DECISION_ALTERNATIVES,
                "current_recommendation": (
                    CURRENT_RECOMMENDATION
                ),
            }

            rationale_hash = _canonical_hash(
                rationale_payload
            )

            connection.execute(
                """
                INSERT INTO decision_alternative_reviews (
                    alternative_review_id,
                    request_id,
                    state,
                    alternatives_json,
                    available_alternative_count,
                    go_option_available,
                    no_go_hold_available,
                    remediation_available,
                    defer_available,
                    current_recommendation,
                    rationale_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    alternative_review_id,
                    request_id,
                    (
                        "decision_alternatives_reviewed_"
                        "go_unavailable"
                    ),
                    alternatives_json,
                    3,
                    0,
                    1,
                    1,
                    1,
                    CURRENT_RECOMMENDATION,
                    rationale_hash,
                    now,
                ),
            )

            decision_record_payload = {
                "request_id": request_id,
                "technical_review_complete": True,
                "criteria_matrix_complete": True,
                "control_packet_complete": True,
                "activation_plan_complete": True,
                "alternatives_review_complete": True,
                "owner_decision_pending": True,
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

            decision_record_hash = _canonical_hash(
                decision_record_payload
            )

            connection.execute(
                """
                INSERT INTO owner_decision_record_drafts (
                    decision_record_id,
                    request_id,
                    state,
                    technical_review_complete,
                    criteria_matrix_complete,
                    control_packet_complete,
                    activation_plan_complete,
                    alternatives_review_complete,
                    owner_decision_pending,
                    current_recommendation,
                    owner_decision_recorded,
                    go_decision_granted,
                    live_authorization_granted,
                    authorization_token_issued,
                    commit_command_issued,
                    actual_restore_allowed,
                    production_write_allowed,
                    decision_record_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    decision_record_id,
                    request_id,
                    (
                        "tower_owner_decision_record_"
                        "draft_pending_owner_action"
                    ),
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    CURRENT_RECOMMENDATION,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    decision_record_hash,
                    now,
                ),
            )

            receipt_payload = {
                "request_id": request_id,
                "decision_record_id": decision_record_id,
                "technical_review_recorded": True,
                "criteria_matrix_recorded": True,
                "control_packet_recorded": True,
                "activation_plan_recorded": True,
                "alternatives_recorded": True,
                "owner_decision_pending_recorded": True,
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

            connection.execute(
                """
                INSERT INTO owner_decision_receipt_drafts (
                    owner_receipt_id,
                    request_id,
                    decision_record_id,
                    state,
                    tower_controlled,
                    technical_review_recorded,
                    criteria_matrix_recorded,
                    control_packet_recorded,
                    activation_plan_recorded,
                    alternatives_recorded,
                    owner_decision_pending_recorded,
                    recommendation_recorded,
                    final_owner_decision_recorded,
                    live_authorization_recorded,
                    authorization_token_recorded,
                    commit_command_recorded,
                    actual_restore_recorded,
                    production_write_recorded,
                    raw_bytes_recorded,
                    raw_paths_recorded,
                    raw_tokens_recorded,
                    public_links_recorded,
                    finalized,
                    append_only,
                    mutable,
                    receipt_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    owner_receipt_id,
                    request_id,
                    decision_record_id,
                    (
                        "tower_owner_decision_"
                        "preparation_receipt_draft"
                    ),
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    0,
                    receipt_hash,
                    now,
                ),
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_final_review_ready": bool(
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


def get_recovery_commit_owner_decision_preparation_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 591,
        "title": (
            "Recovery Commit Owner Decision "
            "Preparation Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "owner_decision_preparation_only": True,
        "owner_decision_recorded": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "commit_point_open": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_final_go_no_go_review_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM preparation_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 592,
        "title": "Final Go/No-Go Review Intake Board",
        "ready": True,
        "intake_count": len(rows),
        "preparation_intakes": rows,
        "all_final_reviews_verified": all(
            bool(row["final_review_verified"])
            for row in rows
        ),
        "all_technical_dry_runs_verified": all(
            bool(row["technical_dry_run_verified"])
            for row in rows
        ),
        "all_technical_evidence_complete": all(
            bool(row["technical_evidence_complete"])
            for row in rows
        ),
        "all_approval_gates_pending": all(
            bool(row["approval_gate_pending"])
            for row in rows
        ),
        "all_activation_gates_pending": all(
            bool(row["activation_gate_pending"])
            for row in rows
        ),
        "all_no_go_holds_verified": all(
            bool(row["current_no_go_hold_verified"])
            for row in rows
        ),
        "all_eligible_for_preparation": all(
            bool(
                row[
                    "eligible_for_owner_decision_preparation"
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


def get_owner_decision_criteria_matrix(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM decision_criteria
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 593,
        "title": "Owner Decision Criteria Matrix",
        "ready": True,
        "criteria_count": len(rows),
        "decision_criteria": rows,
        "all_technical_readiness_passed": all(
            bool(row["technical_readiness_passed"])
            for row in rows
        ),
        "all_evidence_integrity_passed": all(
            bool(row["evidence_integrity_passed"])
            for row in rows
        ),
        "all_barrier_readiness_passed": all(
            bool(row["barrier_readiness_passed"])
            for row in rows
        ),
        "no_approval_gates_complete": all(
            not bool(row["approval_gate_complete"])
            for row in rows
        ),
        "no_activation_gates_complete": all(
            not bool(row["activation_gate_complete"])
            for row in rows
        ),
        "no_go_eligibility": all(
            not bool(row["go_eligible"])
            for row in rows
        ),
        "all_no_go_holds_required": all(
            bool(row["no_go_hold_required"])
            for row in rows
        ),
        "no_remediation_required": all(
            not bool(row["remediation_required"])
            for row in rows
        ),
        "all_criteria_hashes_present": all(
            len(row["criteria_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_admin_control_decision_packet_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM owner_control_packets
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 594,
        "title": (
            "Owner/Admin Control Decision Packet Board"
        ),
        "ready": True,
        "packet_count": len(rows),
        "owner_control_packets": rows,
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
        "all_tower_only_presented": all(
            bool(row["tower_only_presentation"])
            for row in rows
        ),
        "no_vault_decision_authority": all(
            not bool(row["vault_decision_authority"])
            for row in rows
        ),
        "no_teller_decision_authority": all(
            not bool(row["teller_decision_authority"])
            for row in rows
        ),
        "all_control_hashes_present": all(
            len(row["control_packet_hash"]) == 64
            for row in rows
        ),
    }


def get_scope_freeze_commit_window_activation_plan_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM activation_plan_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 595,
        "title": (
            "Scope Freeze and Commit Window "
            "Activation Plan Draft Board"
        ),
        "ready": True,
        "plan_count": len(rows),
        "activation_plan_drafts": rows,
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
        "no_production_targets_allowed": all(
            not bool(row["production_target_allowed"])
            for row in rows
        ),
        "no_external_providers_allowed": all(
            not bool(row["external_provider_allowed"])
            for row in rows
        ),
        "all_activation_hashes_present": all(
            len(row["activation_plan_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_decision_alternatives_rationale_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM decision_alternative_reviews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 596,
        "title": (
            "Recovery Decision Alternatives "
            "and Rationale Board"
        ),
        "ready": True,
        "review_count": len(rows),
        "alternative_reviews": rows,
        "decision_alternatives": (
            DECISION_ALTERNATIVES
        ),
        "all_have_three_available_options": all(
            row["available_alternative_count"] == 3
            for row in rows
        ),
        "no_go_option_available": all(
            not bool(row["go_option_available"])
            for row in rows
        ),
        "all_no_go_holds_available": all(
            bool(row["no_go_hold_available"])
            for row in rows
        ),
        "all_remediation_available": all(
            bool(row["remediation_available"])
            for row in rows
        ),
        "all_defer_available": all(
            bool(row["defer_available"])
            for row in rows
        ),
        "all_recommendations_are_no_go_hold": all(
            row["current_recommendation"]
            == CURRENT_RECOMMENDATION
            for row in rows
        ),
        "all_rationale_hashes_present": all(
            len(row["rationale_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_record_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM owner_decision_record_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 597,
        "title": (
            "Tower Owner Decision Record Draft Board"
        ),
        "ready": True,
        "record_count": len(rows),
        "owner_decision_record_drafts": rows,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "all_packet_components_complete": all(
            bool(row["technical_review_complete"])
            and bool(row["criteria_matrix_complete"])
            and bool(row["control_packet_complete"])
            and bool(row["activation_plan_complete"])
            and bool(
                row["alternatives_review_complete"]
            )
            for row in rows
        ),
        "all_owner_decisions_pending": all(
            bool(row["owner_decision_pending"])
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
        "all_record_hashes_present": all(
            len(row["decision_record_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM owner_decision_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 598,
        "title": (
            "Tower Owner Decision Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "owner_decision_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_preparation_components_recorded": all(
            bool(row["technical_review_recorded"])
            and bool(row["criteria_matrix_recorded"])
            and bool(row["control_packet_recorded"])
            and bool(row["activation_plan_recorded"])
            and bool(row["alternatives_recorded"])
            and bool(
                row["owner_decision_pending_recorded"]
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


def get_owner_decision_preparation_safety_blocker_board(
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
        "gp": 599,
        "title": (
            "Owner Decision Preparation "
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


def get_owner_decision_preparation_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_recovery_commit_owner_decision_preparation_shell()
    )

    intakes = (
        get_final_go_no_go_review_intake_board()
    )

    criteria = get_owner_decision_criteria_matrix()

    controls = (
        get_owner_admin_control_decision_packet_board()
    )

    activations = (
        get_scope_freeze_commit_window_activation_plan_draft_board()
    )

    alternatives = (
        get_recovery_decision_alternatives_rationale_board()
    )

    decisions = (
        get_tower_owner_decision_record_draft_board()
    )

    receipts = (
        get_tower_owner_decision_receipt_draft_ledger()
    )

    blockers = (
        get_owner_decision_preparation_safety_blocker_board()
    )

    checks = {
        "previous_final_review_ready": (
            initialized[
                "previous_final_review_ready"
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
        "preparation_only": (
            DOCTRINE[
                "owner_decision_preparation_only"
            ]
            is True
            and DOCTRINE[
                "technical_readiness_is_not_authorization"
            ]
            is True
            and DOCTRINE[
                "owner_decision_recorded"
            ]
            is False
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "final_review_package_verified": (
            intakes[
                "all_final_reviews_verified"
            ]
            is True
            and intakes[
                "all_technical_dry_runs_verified"
            ]
            is True
            and intakes[
                "all_technical_evidence_complete"
            ]
            is True
            and intakes[
                "all_approval_gates_pending"
            ]
            is True
            and intakes[
                "all_activation_gates_pending"
            ]
            is True
            and intakes[
                "all_no_go_holds_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_preparation"
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

        "criteria_present": (
            criteria["criteria_count"] >= 1
        ),
        "technical_criteria_passed": (
            criteria[
                "all_technical_readiness_passed"
            ]
            is True
            and criteria[
                "all_evidence_integrity_passed"
            ]
            is True
            and criteria[
                "all_barrier_readiness_passed"
            ]
            is True
            and criteria[
                "no_remediation_required"
            ]
            is True
        ),
        "go_criteria_correctly_blocked": (
            criteria[
                "no_approval_gates_complete"
            ]
            is True
            and criteria[
                "no_activation_gates_complete"
            ]
            is True
            and criteria[
                "no_go_eligibility"
            ]
            is True
            and criteria[
                "all_no_go_holds_required"
            ]
            is True
        ),

        "control_packets_present": (
            controls["packet_count"] >= 1
        ),
        "owner_controls_preserved": (
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
            and controls[
                "all_tower_only_presented"
            ]
            is True
        ),
        "control_decisions_still_pending": (
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
                "no_vault_decision_authority"
            ]
            is True
            and controls[
                "no_teller_decision_authority"
            ]
            is True
        ),

        "activation_plans_present": (
            activations["plan_count"] >= 1
        ),
        "activation_plans_complete_but_inactive": (
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
            and activations[
                "nothing_activated"
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

        "alternatives_present": (
            alternatives["review_count"] >= 1
        ),
        "decision_alternatives_safe": (
            alternatives[
                "all_have_three_available_options"
            ]
            is True
            and alternatives[
                "no_go_option_available"
            ]
            is True
            and alternatives[
                "all_no_go_holds_available"
            ]
            is True
            and alternatives[
                "all_remediation_available"
            ]
            is True
            and alternatives[
                "all_defer_available"
            ]
            is True
            and alternatives[
                "all_recommendations_are_no_go_hold"
            ]
            is True
        ),

        "decision_records_present": (
            decisions["record_count"] >= 1
        ),
        "decision_packet_complete": (
            decisions[
                "all_packet_components_complete"
            ]
            is True
            and decisions[
                "all_owner_decisions_pending"
            ]
            is True
            and decisions[
                "all_recommendations_are_no_go_hold"
            ]
            is True
        ),
        "no_owner_decision_or_execution": (
            decisions[
                "no_owner_decisions_recorded"
            ]
            is True
            and decisions[
                "no_go_decisions_granted"
            ]
            is True
            and decisions[
                "no_authorization_or_tokens"
            ]
            is True
            and decisions[
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
                "all_preparation_components_recorded"
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
        "gp": 600,
        "title": (
            "Owner Decision Preparation "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Recovery commit owner decision "
                "preparation blocked"
            )
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "preparation_status": (
            "owner_decision_packet_complete_"
            "owner_decision_pending_"
            "all_execution_locks_closed"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION REVIEW LAYER / GP601-GP610"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no owner decision recorded",
            "no GO decision granted",
            "no live recovery authorization",
            "no authorization or capability token",
            "no owner/admin approval granted",
            "no step-up satisfied",
            "no dual receipt satisfied",
            "no second authority review granted",
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


def get_recovery_commit_owner_decision_preparation_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_preparation_readiness_checkpoint()
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


def validate_recovery_commit_owner_decision_preparation_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_preparation_readiness_checkpoint()
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
        get_owner_decision_preparation_readiness_checkpoint()
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


def get_gp591_status():
    return _gp_status(591)


def get_gp592_status():
    return _gp_status(592)


def get_gp593_status():
    return _gp_status(593)


def get_gp594_status():
    return _gp_status(594)


def get_gp595_status():
    return _gp_status(595)


def get_gp596_status():
    return _gp_status(596)


def get_gp597_status():
    return _gp_status(597)


def get_gp598_status():
    return _gp_status(598)


def get_gp599_status():
    return _gp_status(599)


def get_gp600_status():
    return _gp_status(600)
