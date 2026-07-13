
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT FINAL "
    "GO/NO-GO REVIEW LAYER / GP581-GP590"
)

LAYER_ID = (
    "vault_gp581_590_"
    "recovery_commit_final_go_no_go_review_layer"
)

READINESS_LABEL = (
    "Recovery commit final go-no-go review ready"
)

CURRENT_DECISION = (
    "NO_GO_HOLD_PENDING_APPROVALS_AND_ACTIVATION"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_final_go_no_go_review_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.controlled_recovery_commit_execution_dry_run_layer_service import (
        get_recovery_commit_closeout_intake_board,
        get_recovery_commit_preconditions_verification_board,
        get_isolated_commit_execution_sandbox_board,
        get_recovery_commit_command_simulation_queue,
        get_recovery_write_barrier_rollback_simulation_board,
        get_commit_outcome_diff_integrity_preview_board,
        get_tower_recovery_commit_dry_run_receipt_draft_ledger,
        validate_controlled_recovery_commit_execution_dry_run_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP581-GP590 requires the completed "
        "GP571-GP580 controlled recovery commit dry-run layer."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "tower_is_only_final_decision_authority": True,
    "final_review_layer_only": True,
    "decision_draft_only": True,
    "current_decision": CURRENT_DECISION,
    "go_decision_granted": False,
    "no_go_hold_required": True,
    "owner_admin_approval_required": True,
    "step_up_required": True,
    "dual_receipt_required": True,
    "second_authority_review_required": True,
    "scope_freeze_activation_required": True,
    "commit_window_activation_required": True,
    "execution_window_required": True,
    "commit_point_closed": True,
    "live_authorization_granted": False,
    "authorization_token_issued": False,
    "commit_command_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "final_go_no_go_review_layer": True,
    "dry_run_evidence_review_allowed": True,
    "precondition_revalidation_allowed": True,
    "approval_decision_review_allowed": True,
    "scope_window_review_allowed": True,
    "barrier_readiness_review_allowed": True,
    "final_decision_drafts_allowed": True,
    "review_receipt_drafts_allowed": True,

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
    "offline_package_write_allowed": False,

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
    "physical_media_write_allowed": False,
    "physical_object_move_allowed": False,
}


PACKS = [
    {
        "gp": 581,
        "title": (
            "Recovery Commit Final Go/No-Go Review Shell"
        ),
        "route": (
            "/vault/recovery-commit-final-go-no-go-"
            "review-shell.json"
        ),
    },
    {
        "gp": 582,
        "title": (
            "Commit Dry-Run Evidence Review Intake Board"
        ),
        "route": (
            "/vault/commit-dry-run-evidence-"
            "review-intake-board.json"
        ),
    },
    {
        "gp": 583,
        "title": (
            "Final Commit Preconditions "
            "Revalidation Board"
        ),
        "route": (
            "/vault/final-commit-preconditions-"
            "revalidation-board.json"
        ),
    },
    {
        "gp": 584,
        "title": (
            "Owner/Admin Approval Decision Review Board"
        ),
        "route": (
            "/vault/owner-admin-approval-"
            "decision-review-board.json"
        ),
    },
    {
        "gp": 585,
        "title": (
            "Scope Freeze and Commit Window Review Board"
        ),
        "route": (
            "/vault/scope-freeze-commit-"
            "window-review-board.json"
        ),
    },
    {
        "gp": 586,
        "title": (
            "Write Barrier and Rollback "
            "Readiness Review Board"
        ),
        "route": (
            "/vault/write-barrier-rollback-"
            "readiness-review-board.json"
        ),
    },
    {
        "gp": 587,
        "title": (
            "Tower Final Go/No-Go Decision Draft Board"
        ),
        "route": (
            "/vault/tower-final-go-no-go-"
            "decision-draft-board.json"
        ),
    },
    {
        "gp": 588,
        "title": (
            "Tower Final Go/No-Go Review "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-final-go-no-go-review-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 589,
        "title": "Final Go/No-Go Safety Blocker Board",
        "route": (
            "/vault/final-go-no-go-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 590,
        "title": (
            "Final Go/No-Go Review Readiness Checkpoint"
        ),
        "route": (
            "/vault/final-go-no-go-"
            "review-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_go_without_owner_admin",
        "go_without_owner_admin_approval",
        "Owner/admin approval must be granted first.",
    ),
    (
        "no_go_without_step_up",
        "go_without_step_up",
        "Tower step-up must be satisfied first.",
    ),
    (
        "no_go_without_dual_receipt",
        "go_without_dual_receipt",
        "The required dual receipt must be satisfied first.",
    ),
    (
        "no_go_without_second_authority",
        "go_without_second_authority_review",
        "Second authority review must be granted first.",
    ),
    (
        "no_go_without_scope_activation",
        "go_without_scope_freeze_activation",
        "The exact scope freeze must be activated first.",
    ),
    (
        "no_go_without_window_activation",
        "go_without_commit_window_activation",
        "The one-time commit window must be activated first.",
    ),
    (
        "no_go_without_execution_window",
        "go_without_execution_window",
        "The execution window must remain closed.",
    ),
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "This review layer cannot grant authorization.",
    ),
    (
        "no_authorization_token",
        "recovery_authorization_token_issue",
        "This review layer cannot issue a token.",
    ),
    (
        "no_commit_point_open",
        "commit_point_open",
        "The real commit point remains closed.",
    ),
    (
        "no_real_commit_command",
        "real_commit_command",
        "No real commit command may be issued.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "No actual restore may run.",
    ),
    (
        "no_production_mount",
        "production_storage_mount",
        "Production storage cannot be mounted.",
    ),
    (
        "no_writable_mount",
        "writable_recovery_mount",
        "No writable mount can be created.",
    ),
    (
        "no_production_write",
        "production_recovery_write",
        "Production writes remain locked.",
    ),
    (
        "no_final_index_write",
        "final_rebuilt_index_write",
        "Final rebuilt index writes remain locked.",
    ),
    (
        "no_pack_overwrite",
        "final_pack_overwrite",
        "Sealed packs cannot be overwritten.",
    ),
    (
        "no_sealed_bytes_write",
        "sealed_pack_bytes_write",
        "Sealed bytes cannot be written.",
    ),
    (
        "no_package_materialization",
        "backup_package_materialization",
        "Backup packages remain hash-only.",
    ),
    (
        "no_external_provider",
        "external_provider_connection",
        "No external provider may be connected.",
    ),
    (
        "no_teller_direct_decision",
        "teller_direct_go_no_go_decision",
        "Tower controls the final recovery decision.",
    ),
    (
        "no_teller_vault_call",
        "teller_to_vault_direct_call",
        "Teller must route requests through Tower.",
    ),
    (
        "no_resident_access",
        "resident_direct_vault_access",
        "Residents cannot enter Vault directly.",
    ),
    (
        "no_vendor_access",
        "vendor_direct_vault_access",
        "Vendors cannot enter Vault directly.",
    ),
    (
        "no_public_access",
        "public_vault_access",
        "Vault has no public access path.",
    ),
    (
        "no_raw_bytes",
        "raw_file_bytes_returned_by_json",
        "Outputs contain metadata and hashes only.",
    ),
    (
        "no_raw_paths",
        "raw_path_or_file_url_exposure",
        "Vault paths and URLs remain sealed.",
    ),
    (
        "no_raw_tokens",
        "raw_recovery_token_exposure",
        "No raw token is generated or exposed.",
    ),
    (
        "no_delete_purge_release",
        "delete_purge_quarantine_release",
        "Review cannot delete, purge, or release evidence.",
    ),
    (
        "no_physical_move",
        "physical_object_move",
        "Review cannot move physical media.",
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
        get_recovery_commit_closeout_intake_board()
        .get("dry_run_intakes", [])
    )

    precondition_rows = (
        get_recovery_commit_preconditions_verification_board()
        .get("precondition_verifications", [])
    )

    sandbox_rows = (
        get_isolated_commit_execution_sandbox_board()
        .get("commit_sandboxes", [])
    )

    command_rows = (
        get_recovery_commit_command_simulation_queue()
        .get("command_simulations", [])
    )

    barrier_rows = (
        get_recovery_write_barrier_rollback_simulation_board()
        .get("barrier_simulations", [])
    )

    outcome_rows = (
        get_commit_outcome_diff_integrity_preview_board()
        .get("outcome_previews", [])
    )

    receipt_rows = (
        get_tower_recovery_commit_dry_run_receipt_draft_ledger()
        .get("dry_run_receipt_drafts", [])
    )

    precondition_by_request = {
        row["request_id"]: row
        for row in precondition_rows
    }

    sandbox_by_request = {
        row["request_id"]: row
        for row in sandbox_rows
    }

    command_by_request = {
        row["request_id"]: row
        for row in command_rows
    }

    barrier_by_request = {
        row["request_id"]: row
        for row in barrier_rows
    }

    outcome_by_request = {
        row["request_id"]: row
        for row in outcome_rows
    }

    receipt_by_request = {
        row["request_id"]: row
        for row in receipt_rows
    }

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
                "precondition": (
                    precondition_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "sandbox": sandbox_by_request.get(
                    request_id,
                    {},
                ),
                "command": command_by_request.get(
                    request_id,
                    {},
                ),
                "barrier": barrier_by_request.get(
                    request_id,
                    {},
                ),
                "outcome": outcome_by_request.get(
                    request_id,
                    {},
                ),
                "receipt": receipt_by_request.get(
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
        validate_controlled_recovery_commit_execution_dry_run_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS review_intakes (
                review_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                dry_run_intake_verified INTEGER NOT NULL,
                preconditions_verified INTEGER NOT NULL,
                sandbox_verified INTEGER NOT NULL,
                command_simulation_verified INTEGER NOT NULL,
                barrier_simulation_verified INTEGER NOT NULL,
                outcome_preview_verified INTEGER NOT NULL,
                dry_run_receipt_verified INTEGER NOT NULL,
                eligible_for_final_review INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS precondition_revalidations (
                revalidation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                evidence_complete INTEGER NOT NULL,
                tower_authority_reconfirmed INTEGER NOT NULL,
                exact_scope_bound INTEGER NOT NULL,
                one_time_window_required INTEGER NOT NULL,
                all_approval_requirements_present INTEGER NOT NULL,
                all_approval_decisions_pending INTEGER NOT NULL,
                scope_freeze_inactive INTEGER NOT NULL,
                commit_window_inactive INTEGER NOT NULL,
                execution_window_closed INTEGER NOT NULL,
                commit_point_closed INTEGER NOT NULL,
                go_criteria_currently_met INTEGER NOT NULL,
                revalidation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approval_decision_reviews (
                approval_review_id TEXT PRIMARY KEY,
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
                approval_gate_complete INTEGER NOT NULL,
                no_go_hold_required INTEGER NOT NULL,
                approval_review_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scope_window_reviews (
                scope_window_review_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                exact_scope_bound INTEGER NOT NULL,
                one_time_window_required INTEGER NOT NULL,
                scope_freeze_activation_required INTEGER NOT NULL,
                commit_window_activation_required INTEGER NOT NULL,
                scope_freeze_activated INTEGER NOT NULL,
                commit_window_activated INTEGER NOT NULL,
                execution_window_open INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                scope_window_ready_for_activation_review INTEGER NOT NULL,
                scope_window_review_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS barrier_readiness_reviews (
                barrier_review_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                command_sequence_simulated INTEGER NOT NULL,
                real_commit_command_count INTEGER NOT NULL,
                actual_restore_count INTEGER NOT NULL,
                production_write_count INTEGER NOT NULL,
                final_index_write_count INTEGER NOT NULL,
                pack_overwrite_count INTEGER NOT NULL,
                sealed_bytes_write_count INTEGER NOT NULL,
                package_materialization_count INTEGER NOT NULL,
                all_write_barriers_engaged INTEGER NOT NULL,
                abort_on_mismatch INTEGER NOT NULL,
                rollback_on_mutation INTEGER NOT NULL,
                expected_integrity_match INTEGER NOT NULL,
                actual_mutation_count INTEGER NOT NULL,
                barrier_readiness_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_drafts (
                decision_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                evidence_review_complete INTEGER NOT NULL,
                precondition_review_complete INTEGER NOT NULL,
                barrier_review_complete INTEGER NOT NULL,
                eligible_for_owner_decision_review INTEGER NOT NULL,
                technical_dry_run_passed INTEGER NOT NULL,
                approval_gate_complete INTEGER NOT NULL,
                activation_gate_complete INTEGER NOT NULL,
                current_decision TEXT NOT NULL,
                go_decision_granted INTEGER NOT NULL,
                no_go_hold_required INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                decision_draft_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS review_receipt_drafts (
                review_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                decision_draft_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                evidence_review_recorded INTEGER NOT NULL,
                precondition_review_recorded INTEGER NOT NULL,
                approval_review_recorded INTEGER NOT NULL,
                scope_window_review_recorded INTEGER NOT NULL,
                barrier_review_recorded INTEGER NOT NULL,
                decision_draft_recorded INTEGER NOT NULL,
                no_go_hold_recorded INTEGER NOT NULL,
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
            "review_intakes",
            "precondition_revalidations",
            "approval_decision_reviews",
            "scope_window_reviews",
            "barrier_readiness_reviews",
            "decision_drafts",
            "review_receipt_drafts",
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
            sandbox = source["sandbox"]
            command = source["command"]
            barrier = source["barrier"]
            outcome = source["outcome"]
            receipt = source["receipt"]

            dry_run_intake_verified = all(
                [
                    bool(
                        intake.get(
                            "closeout_evidence_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "tower_authority_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "approval_requirements_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "scope_freeze_draft_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "commit_window_draft_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "closeout_draft_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "closeout_receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_commit_dry_run",
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
                            "evidence_closeout_complete",
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
                            "owner_admin_approval_required",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "step_up_required",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "dual_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        precondition.get(
                            "second_authority_review_required",
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
                            "commit_point_closed",
                            0,
                        )
                    ),
                    len(
                        precondition.get(
                            "precondition_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            sandbox_verified = all(
                [
                    bool(
                        sandbox.get(
                            "isolated",
                            0,
                        )
                    ),
                    bool(
                        sandbox.get(
                            "ephemeral",
                            0,
                        )
                    ),
                    bool(
                        sandbox.get(
                            "hash_only",
                            0,
                        )
                    ),
                    not bool(
                        sandbox.get(
                            "production_mount_allowed",
                            1,
                        )
                    ),
                    not bool(
                        sandbox.get(
                            "writable_mount_allowed",
                            1,
                        )
                    ),
                    not bool(
                        sandbox.get(
                            "network_egress_allowed",
                            1,
                        )
                    ),
                    not bool(
                        sandbox.get(
                            "external_provider_connection_allowed",
                            1,
                        )
                    ),
                    not bool(
                        sandbox.get(
                            "raw_bytes_materialized",
                            1,
                        )
                    ),
                    not bool(
                        sandbox.get(
                            "raw_paths_exposed",
                            1,
                        )
                    ),
                    len(
                        sandbox.get(
                            "sandbox_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            command_simulation_verified = all(
                [
                    int(
                        command.get(
                            "simulated_command_count",
                            0,
                        )
                    )
                    > 0,
                    bool(
                        command.get(
                            "simulated_commit_command",
                            0,
                        )
                    ),
                    int(
                        command.get(
                            "real_commit_command_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        command.get(
                            "actual_restore_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        command.get(
                            "production_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        command.get(
                            "final_index_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        command.get(
                            "pack_overwrite_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        command.get(
                            "sealed_bytes_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        command.get(
                            "package_materialization_count",
                            1,
                        )
                    )
                    == 0,
                    len(
                        command.get(
                            "command_simulation_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            barrier_simulation_verified = all(
                [
                    bool(
                        barrier.get(
                            "production_write_barrier_engaged",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "final_index_barrier_engaged",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "pack_overwrite_barrier_engaged",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "sealed_bytes_barrier_engaged",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "provider_connection_barrier_engaged",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "abort_on_any_mismatch",
                            0,
                        )
                    ),
                    bool(
                        barrier.get(
                            "rollback_on_any_mutation",
                            0,
                        )
                    ),
                    int(
                        barrier.get(
                            "simulated_abort_count",
                            0,
                        )
                    )
                    >= 1,
                    int(
                        barrier.get(
                            "simulated_rollback_count",
                            0,
                        )
                    )
                    >= 1,
                    int(
                        barrier.get(
                            "actual_abort_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        barrier.get(
                            "actual_rollback_count",
                            1,
                        )
                    )
                    == 0,
                    len(
                        barrier.get(
                            "barrier_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            outcome_preview_verified = all(
                [
                    len(
                        outcome.get(
                            "source_closeout_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        outcome.get(
                            "simulated_command_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        outcome.get(
                            "simulated_barrier_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        outcome.get(
                            "simulated_outcome_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        outcome.get(
                            "expected_integrity_match",
                            0,
                        )
                    ),
                    int(
                        outcome.get(
                            "actual_mutation_count",
                            1,
                        )
                    )
                    == 0,
                    not bool(
                        outcome.get(
                            "production_diff_generated",
                            1,
                        )
                    ),
                    not bool(
                        outcome.get(
                            "raw_bytes_included",
                            1,
                        )
                    ),
                    not bool(
                        outcome.get(
                            "raw_paths_included",
                            1,
                        )
                    ),
                    not bool(
                        outcome.get(
                            "raw_tokens_included",
                            1,
                        )
                    ),
                    not bool(
                        outcome.get(
                            "public_links_included",
                            1,
                        )
                    ),
                    len(
                        outcome.get(
                            "outcome_preview_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            dry_run_receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "dry_run_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "preconditions_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "sandbox_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "command_simulation_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "barrier_simulation_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "outcome_preview_recorded",
                            0,
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
                            "real_commit_recorded",
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

            eligible_for_final_review = all(
                [
                    dry_run_intake_verified,
                    preconditions_verified,
                    sandbox_verified,
                    command_simulation_verified,
                    barrier_simulation_verified,
                    outcome_preview_verified,
                    dry_run_receipt_verified,
                ]
            )

            review_intake_id = _id(
                "final_go_no_go_review_intake",
                request_id,
            )

            revalidation_id = _id(
                "final_precondition_revalidation",
                request_id,
            )

            approval_review_id = _id(
                "approval_decision_review",
                request_id,
            )

            scope_window_review_id = _id(
                "scope_window_review",
                request_id,
            )

            barrier_review_id = _id(
                "barrier_readiness_review",
                request_id,
            )

            decision_draft_id = _id(
                "tower_final_go_no_go_decision",
                request_id,
            )

            review_receipt_id = _id(
                "tower_final_go_no_go_review_receipt",
                request_id,
            )

            connection.execute(
                """
                INSERT INTO review_intakes (
                    review_intake_id,
                    request_id,
                    workflow_type,
                    state,
                    dry_run_intake_verified,
                    preconditions_verified,
                    sandbox_verified,
                    command_simulation_verified,
                    barrier_simulation_verified,
                    outcome_preview_verified,
                    dry_run_receipt_verified,
                    eligible_for_final_review,
                    live_authorization_granted,
                    commit_point_open,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    review_intake_id,
                    request_id,
                    workflow_type,
                    (
                        "eligible_for_final_go_no_go_"
                        "review_not_live_authorization"
                    ),
                    int(dry_run_intake_verified),
                    int(preconditions_verified),
                    int(sandbox_verified),
                    int(command_simulation_verified),
                    int(barrier_simulation_verified),
                    int(outcome_preview_verified),
                    int(dry_run_receipt_verified),
                    int(eligible_for_final_review),
                    0,
                    0,
                    now,
                ),
            )

            precondition_payload = {
                "request_id": request_id,
                "evidence_complete": (
                    eligible_for_final_review
                ),
                "tower_authority_reconfirmed": True,
                "exact_scope_bound": True,
                "one_time_window_required": True,
                "all_approval_requirements_present": True,
                "all_approval_decisions_pending": True,
                "scope_freeze_inactive": True,
                "commit_window_inactive": True,
                "execution_window_closed": True,
                "commit_point_closed": True,
                "go_criteria_currently_met": False,
            }

            revalidation_hash = _canonical_hash(
                precondition_payload
            )

            connection.execute(
                """
                INSERT INTO precondition_revalidations (
                    revalidation_id,
                    request_id,
                    state,
                    evidence_complete,
                    tower_authority_reconfirmed,
                    exact_scope_bound,
                    one_time_window_required,
                    all_approval_requirements_present,
                    all_approval_decisions_pending,
                    scope_freeze_inactive,
                    commit_window_inactive,
                    execution_window_closed,
                    commit_point_closed,
                    go_criteria_currently_met,
                    revalidation_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    revalidation_id,
                    request_id,
                    (
                        "technical_preconditions_passed_"
                        "approval_activation_gates_pending"
                    ),
                    int(eligible_for_final_review),
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    revalidation_hash,
                    now,
                ),
            )

            approval_payload = {
                "request_id": request_id,
                "owner_admin_approval_required": True,
                "step_up_required": True,
                "dual_receipt_required": True,
                "second_authority_review_required": True,
                "owner_admin_approval_granted": False,
                "step_up_satisfied": False,
                "dual_receipt_satisfied": False,
                "second_authority_review_granted": False,
                "approval_gate_complete": False,
                "no_go_hold_required": True,
            }

            approval_review_hash = _canonical_hash(
                approval_payload
            )

            connection.execute(
                """
                INSERT INTO approval_decision_reviews (
                    approval_review_id,
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
                    approval_gate_complete,
                    no_go_hold_required,
                    approval_review_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    approval_review_id,
                    request_id,
                    (
                        "approval_decision_review_"
                        "pending_no_go_hold"
                    ),
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    approval_review_hash,
                    now,
                ),
            )

            scope_window_payload = {
                "request_id": request_id,
                "exact_scope_bound": True,
                "one_time_window_required": True,
                "scope_freeze_activation_required": True,
                "commit_window_activation_required": True,
                "scope_freeze_activated": False,
                "commit_window_activated": False,
                "execution_window_open": False,
                "commit_point_open": False,
                "production_target_allowed": False,
                "external_provider_allowed": False,
                "scope_window_ready_for_activation_review": True,
            }

            scope_window_review_hash = _canonical_hash(
                scope_window_payload
            )

            connection.execute(
                """
                INSERT INTO scope_window_reviews (
                    scope_window_review_id,
                    request_id,
                    state,
                    exact_scope_bound,
                    one_time_window_required,
                    scope_freeze_activation_required,
                    commit_window_activation_required,
                    scope_freeze_activated,
                    commit_window_activated,
                    execution_window_open,
                    commit_point_open,
                    production_target_allowed,
                    external_provider_allowed,
                    scope_window_ready_for_activation_review,
                    scope_window_review_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    scope_window_review_id,
                    request_id,
                    (
                        "scope_and_window_verified_"
                        "activation_not_performed"
                    ),
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
                    1,
                    scope_window_review_hash,
                    now,
                ),
            )

            barrier_payload = {
                "request_id": request_id,
                "command_sequence_simulated": True,
                "real_commit_command_count": 0,
                "actual_restore_count": 0,
                "production_write_count": 0,
                "final_index_write_count": 0,
                "pack_overwrite_count": 0,
                "sealed_bytes_write_count": 0,
                "package_materialization_count": 0,
                "all_write_barriers_engaged": True,
                "abort_on_mismatch": True,
                "rollback_on_mutation": True,
                "expected_integrity_match": True,
                "actual_mutation_count": 0,
            }

            barrier_readiness_hash = _canonical_hash(
                barrier_payload
            )

            connection.execute(
                """
                INSERT INTO barrier_readiness_reviews (
                    barrier_review_id,
                    request_id,
                    state,
                    command_sequence_simulated,
                    real_commit_command_count,
                    actual_restore_count,
                    production_write_count,
                    final_index_write_count,
                    pack_overwrite_count,
                    sealed_bytes_write_count,
                    package_materialization_count,
                    all_write_barriers_engaged,
                    abort_on_mismatch,
                    rollback_on_mutation,
                    expected_integrity_match,
                    actual_mutation_count,
                    barrier_readiness_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    barrier_review_id,
                    request_id,
                    (
                        "write_barriers_and_rollback_"
                        "ready_no_real_execution"
                    ),
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    1,
                    1,
                    1,
                    1,
                    0,
                    barrier_readiness_hash,
                    now,
                ),
            )

            technical_dry_run_passed = all(
                [
                    eligible_for_final_review,
                    command_simulation_verified,
                    barrier_simulation_verified,
                    outcome_preview_verified,
                ]
            )

            approval_gate_complete = False
            activation_gate_complete = False
            go_decision_granted = False
            no_go_hold_required = True

            decision_payload = {
                "request_id": request_id,
                "evidence_review_complete": True,
                "precondition_review_complete": True,
                "barrier_review_complete": True,
                "eligible_for_owner_decision_review": True,
                "technical_dry_run_passed": (
                    technical_dry_run_passed
                ),
                "approval_gate_complete": (
                    approval_gate_complete
                ),
                "activation_gate_complete": (
                    activation_gate_complete
                ),
                "current_decision": CURRENT_DECISION,
                "go_decision_granted": (
                    go_decision_granted
                ),
                "no_go_hold_required": (
                    no_go_hold_required
                ),
                "live_authorization_granted": False,
                "authorization_token_issued": False,
                "commit_command_issued": False,
                "actual_restore_allowed": False,
                "production_write_allowed": False,
            }

            decision_draft_hash = _canonical_hash(
                decision_payload
            )

            connection.execute(
                """
                INSERT INTO decision_drafts (
                    decision_draft_id,
                    request_id,
                    state,
                    evidence_review_complete,
                    precondition_review_complete,
                    barrier_review_complete,
                    eligible_for_owner_decision_review,
                    technical_dry_run_passed,
                    approval_gate_complete,
                    activation_gate_complete,
                    current_decision,
                    go_decision_granted,
                    no_go_hold_required,
                    live_authorization_granted,
                    authorization_token_issued,
                    commit_command_issued,
                    actual_restore_allowed,
                    production_write_allowed,
                    decision_draft_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    decision_draft_id,
                    request_id,
                    (
                        "final_decision_draft_"
                        "no_go_hold_pending_owner_controls"
                    ),
                    1,
                    1,
                    1,
                    1,
                    int(technical_dry_run_passed),
                    0,
                    0,
                    CURRENT_DECISION,
                    0,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    decision_draft_hash,
                    now,
                ),
            )

            receipt_payload = {
                "request_id": request_id,
                "decision_draft_id": decision_draft_id,
                "evidence_review_recorded": True,
                "precondition_review_recorded": True,
                "approval_review_recorded": True,
                "scope_window_review_recorded": True,
                "barrier_review_recorded": True,
                "decision_draft_recorded": True,
                "no_go_hold_recorded": True,
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

            connection.execute(
                """
                INSERT INTO review_receipt_drafts (
                    review_receipt_id,
                    request_id,
                    decision_draft_id,
                    state,
                    tower_controlled,
                    evidence_review_recorded,
                    precondition_review_recorded,
                    approval_review_recorded,
                    scope_window_review_recorded,
                    barrier_review_recorded,
                    decision_draft_recorded,
                    no_go_hold_recorded,
                    go_decision_recorded,
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
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    review_receipt_id,
                    request_id,
                    decision_draft_id,
                    (
                        "tower_final_go_no_go_"
                        "review_receipt_draft"
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
        "previous_dry_run_layer_ready": bool(
            previous.get("ready", False)
        ),
        "current_decision": CURRENT_DECISION,
        "db_path": str(
            DB_PATH.relative_to(PROJECT_ROOT)
        ),
    }

    _INIT_CACHE = dict(result)
    return result


def get_recovery_commit_final_go_no_go_review_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 581,
        "title": (
            "Recovery Commit Final Go/No-Go Review Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_decision": CURRENT_DECISION,
        "decision_draft_only": True,
        "go_decision_granted": False,
        "no_go_hold_required": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "commit_point_closed": True,
        "commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_commit_dry_run_evidence_review_intake_board(
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
        "gp": 582,
        "title": (
            "Commit Dry-Run Evidence Review Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "review_intakes": rows,
        "all_dry_run_intakes_verified": all(
            bool(row["dry_run_intake_verified"])
            for row in rows
        ),
        "all_preconditions_verified": all(
            bool(row["preconditions_verified"])
            for row in rows
        ),
        "all_sandboxes_verified": all(
            bool(row["sandbox_verified"])
            for row in rows
        ),
        "all_command_simulations_verified": all(
            bool(row["command_simulation_verified"])
            for row in rows
        ),
        "all_barrier_simulations_verified": all(
            bool(row["barrier_simulation_verified"])
            for row in rows
        ),
        "all_outcome_previews_verified": all(
            bool(row["outcome_preview_verified"])
            for row in rows
        ),
        "all_dry_run_receipts_verified": all(
            bool(row["dry_run_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_final_review": all(
            bool(row["eligible_for_final_review"])
            for row in rows
        ),
        "no_live_authorization_granted": all(
            not bool(row["live_authorization_granted"])
            for row in rows
        ),
        "all_commit_points_closed": all(
            not bool(row["commit_point_open"])
            for row in rows
        ),
    }


def get_final_commit_preconditions_revalidation_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM precondition_revalidations
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 583,
        "title": (
            "Final Commit Preconditions "
            "Revalidation Board"
        ),
        "ready": True,
        "revalidation_count": len(rows),
        "revalidations": rows,
        "all_evidence_complete": all(
            bool(row["evidence_complete"])
            for row in rows
        ),
        "all_tower_authority_reconfirmed": all(
            bool(row["tower_authority_reconfirmed"])
            for row in rows
        ),
        "all_exact_scopes_bound": all(
            bool(row["exact_scope_bound"])
            for row in rows
        ),
        "all_one_time_windows_required": all(
            bool(row["one_time_window_required"])
            for row in rows
        ),
        "all_approval_requirements_present": all(
            bool(
                row["all_approval_requirements_present"]
            )
            for row in rows
        ),
        "all_approval_decisions_pending": all(
            bool(row["all_approval_decisions_pending"])
            for row in rows
        ),
        "all_scope_freezes_inactive": all(
            bool(row["scope_freeze_inactive"])
            for row in rows
        ),
        "all_commit_windows_inactive": all(
            bool(row["commit_window_inactive"])
            for row in rows
        ),
        "all_execution_windows_closed": all(
            bool(row["execution_window_closed"])
            for row in rows
        ),
        "all_commit_points_closed": all(
            bool(row["commit_point_closed"])
            for row in rows
        ),
        "no_go_criteria_currently_met": all(
            not bool(row["go_criteria_currently_met"])
            for row in rows
        ),
        "all_revalidation_hashes_present": all(
            len(row["revalidation_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_admin_approval_decision_review_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM approval_decision_reviews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 584,
        "title": (
            "Owner/Admin Approval Decision Review Board"
        ),
        "ready": True,
        "review_count": len(rows),
        "approval_decision_reviews": rows,
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
        "all_second_authority_review_required": all(
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
        "no_dual_receipt_satisfied": all(
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
        "all_no_go_holds_required": all(
            bool(row["no_go_hold_required"])
            for row in rows
        ),
        "all_review_hashes_present": all(
            len(row["approval_review_hash"]) == 64
            for row in rows
        ),
    }


def get_scope_freeze_commit_window_review_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM scope_window_reviews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 585,
        "title": (
            "Scope Freeze and Commit Window Review Board"
        ),
        "ready": True,
        "review_count": len(rows),
        "scope_window_reviews": rows,
        "all_exact_scopes_bound": all(
            bool(row["exact_scope_bound"])
            for row in rows
        ),
        "all_one_time_windows_required": all(
            bool(row["one_time_window_required"])
            for row in rows
        ),
        "all_scope_freeze_activation_required": all(
            bool(
                row["scope_freeze_activation_required"]
            )
            for row in rows
        ),
        "all_commit_window_activation_required": all(
            bool(
                row["commit_window_activation_required"]
            )
            for row in rows
        ),
        "no_scope_freezes_activated": all(
            not bool(row["scope_freeze_activated"])
            for row in rows
        ),
        "no_commit_windows_activated": all(
            not bool(row["commit_window_activated"])
            for row in rows
        ),
        "no_execution_windows_open": all(
            not bool(row["execution_window_open"])
            for row in rows
        ),
        "no_commit_points_open": all(
            not bool(row["commit_point_open"])
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
        "all_ready_for_activation_review": all(
            bool(
                row[
                    "scope_window_ready_for_activation_review"
                ]
            )
            for row in rows
        ),
        "all_review_hashes_present": all(
            len(row["scope_window_review_hash"]) == 64
            for row in rows
        ),
    }


def get_write_barrier_rollback_readiness_review_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM barrier_readiness_reviews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 586,
        "title": (
            "Write Barrier and Rollback "
            "Readiness Review Board"
        ),
        "ready": True,
        "review_count": len(rows),
        "barrier_readiness_reviews": rows,
        "all_command_sequences_simulated": all(
            bool(row["command_sequence_simulated"])
            for row in rows
        ),
        "no_real_commit_commands": all(
            row["real_commit_command_count"] == 0
            for row in rows
        ),
        "no_actual_restores": all(
            row["actual_restore_count"] == 0
            for row in rows
        ),
        "no_production_writes": all(
            row["production_write_count"] == 0
            for row in rows
        ),
        "no_final_index_writes": all(
            row["final_index_write_count"] == 0
            for row in rows
        ),
        "no_pack_overwrites": all(
            row["pack_overwrite_count"] == 0
            for row in rows
        ),
        "no_sealed_bytes_writes": all(
            row["sealed_bytes_write_count"] == 0
            for row in rows
        ),
        "no_package_materialization": all(
            row["package_materialization_count"] == 0
            for row in rows
        ),
        "all_write_barriers_engaged": all(
            bool(row["all_write_barriers_engaged"])
            for row in rows
        ),
        "all_abort_on_mismatch": all(
            bool(row["abort_on_mismatch"])
            for row in rows
        ),
        "all_rollback_on_mutation": all(
            bool(row["rollback_on_mutation"])
            for row in rows
        ),
        "all_expected_integrity_matches": all(
            bool(row["expected_integrity_match"])
            for row in rows
        ),
        "no_actual_mutations": all(
            row["actual_mutation_count"] == 0
            for row in rows
        ),
        "all_readiness_hashes_present": all(
            len(row["barrier_readiness_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_final_go_no_go_decision_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM decision_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 587,
        "title": (
            "Tower Final Go/No-Go Decision Draft Board"
        ),
        "ready": True,
        "decision_count": len(rows),
        "decision_drafts": rows,
        "current_decision": CURRENT_DECISION,
        "all_evidence_reviews_complete": all(
            bool(row["evidence_review_complete"])
            for row in rows
        ),
        "all_precondition_reviews_complete": all(
            bool(row["precondition_review_complete"])
            for row in rows
        ),
        "all_barrier_reviews_complete": all(
            bool(row["barrier_review_complete"])
            for row in rows
        ),
        "all_eligible_for_owner_decision_review": all(
            bool(
                row[
                    "eligible_for_owner_decision_review"
                ]
            )
            for row in rows
        ),
        "all_technical_dry_runs_passed": all(
            bool(row["technical_dry_run_passed"])
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
        "all_decisions_are_no_go_hold": all(
            row["current_decision"] == CURRENT_DECISION
            and not bool(row["go_decision_granted"])
            and bool(row["no_go_hold_required"])
            for row in rows
        ),
        "no_live_authorization_granted": all(
            not bool(row["live_authorization_granted"])
            for row in rows
        ),
        "no_tokens_issued": all(
            not bool(row["authorization_token_issued"])
            for row in rows
        ),
        "no_commit_commands_issued": all(
            not bool(row["commit_command_issued"])
            for row in rows
        ),
        "no_restore_or_write_allowed": all(
            not bool(row["actual_restore_allowed"])
            and not bool(row["production_write_allowed"])
            for row in rows
        ),
        "all_decision_hashes_present": all(
            len(row["decision_draft_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_final_go_no_go_review_receipt_draft_ledger(
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
        "gp": 588,
        "title": (
            "Tower Final Go/No-Go Review "
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
            bool(row["evidence_review_recorded"])
            and bool(
                row["precondition_review_recorded"]
            )
            and bool(row["approval_review_recorded"])
            and bool(
                row["scope_window_review_recorded"]
            )
            and bool(row["barrier_review_recorded"])
            and bool(row["decision_draft_recorded"])
            for row in rows
        ),
        "all_no_go_holds_recorded": all(
            bool(row["no_go_hold_recorded"])
            for row in rows
        ),
        "no_go_decisions_recorded": all(
            not bool(row["go_decision_recorded"])
            for row in rows
        ),
        "no_authorization_or_token_recorded": all(
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


def get_final_go_no_go_safety_blocker_board(
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
        "gp": 589,
        "title": "Final Go/No-Go Safety Blocker Board",
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


def get_final_go_no_go_review_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_recovery_commit_final_go_no_go_review_shell()
    )

    intakes = (
        get_commit_dry_run_evidence_review_intake_board()
    )

    preconditions = (
        get_final_commit_preconditions_revalidation_board()
    )

    approvals = (
        get_owner_admin_approval_decision_review_board()
    )

    scopes = (
        get_scope_freeze_commit_window_review_board()
    )

    barriers = (
        get_write_barrier_rollback_readiness_review_board()
    )

    decisions = (
        get_tower_final_go_no_go_decision_draft_board()
    )

    receipts = (
        get_tower_final_go_no_go_review_receipt_draft_ledger()
    )

    blockers = (
        get_final_go_no_go_safety_blocker_board()
    )

    checks = {
        "previous_dry_run_layer_ready": (
            initialized[
                "previous_dry_run_layer_ready"
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
        "tower_only_final_decision": (
            DOCTRINE[
                "tower_is_only_final_decision_authority"
            ]
            is True
            and DOCTRINE["final_review_layer_only"]
            is True
            and DOCTRINE["decision_draft_only"]
            is True
        ),
        "current_decision_is_no_go_hold": (
            DOCTRINE["current_decision"]
            == CURRENT_DECISION
            and DOCTRINE["go_decision_granted"]
            is False
            and DOCTRINE["no_go_hold_required"]
            is True
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "all_dry_run_evidence_verified": (
            intakes[
                "all_dry_run_intakes_verified"
            ]
            is True
            and intakes[
                "all_preconditions_verified"
            ]
            is True
            and intakes[
                "all_sandboxes_verified"
            ]
            is True
            and intakes[
                "all_command_simulations_verified"
            ]
            is True
            and intakes[
                "all_barrier_simulations_verified"
            ]
            is True
            and intakes[
                "all_outcome_previews_verified"
            ]
            is True
            and intakes[
                "all_dry_run_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_final_review"
            ]
            is True
        ),
        "intakes_no_live_commit": (
            intakes[
                "no_live_authorization_granted"
            ]
            is True
            and intakes[
                "all_commit_points_closed"
            ]
            is True
        ),

        "preconditions_present": (
            preconditions["revalidation_count"] >= 1
        ),
        "technical_preconditions_revalidated": (
            preconditions["all_evidence_complete"]
            is True
            and preconditions[
                "all_tower_authority_reconfirmed"
            ]
            is True
            and preconditions[
                "all_exact_scopes_bound"
            ]
            is True
            and preconditions[
                "all_one_time_windows_required"
            ]
            is True
            and preconditions[
                "all_approval_requirements_present"
            ]
            is True
        ),
        "go_preconditions_not_yet_met": (
            preconditions[
                "all_approval_decisions_pending"
            ]
            is True
            and preconditions[
                "all_scope_freezes_inactive"
            ]
            is True
            and preconditions[
                "all_commit_windows_inactive"
            ]
            is True
            and preconditions[
                "all_execution_windows_closed"
            ]
            is True
            and preconditions[
                "all_commit_points_closed"
            ]
            is True
            and preconditions[
                "no_go_criteria_currently_met"
            ]
            is True
        ),

        "approval_reviews_present": (
            approvals["review_count"] >= 1
        ),
        "approval_requirements_locked": (
            approvals[
                "all_owner_admin_approval_required"
            ]
            is True
            and approvals["all_step_up_required"]
            is True
            and approvals[
                "all_dual_receipts_required"
            ]
            is True
            and approvals[
                "all_second_authority_review_required"
            ]
            is True
        ),
        "approval_gate_still_pending": (
            approvals[
                "no_owner_admin_approval_granted"
            ]
            is True
            and approvals[
                "no_step_up_satisfied"
            ]
            is True
            and approvals[
                "no_dual_receipt_satisfied"
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
            and approvals[
                "all_no_go_holds_required"
            ]
            is True
        ),

        "scope_window_reviews_present": (
            scopes["review_count"] >= 1
        ),
        "scope_window_drafts_valid": (
            scopes["all_exact_scopes_bound"]
            is True
            and scopes[
                "all_one_time_windows_required"
            ]
            is True
            and scopes[
                "all_scope_freeze_activation_required"
            ]
            is True
            and scopes[
                "all_commit_window_activation_required"
            ]
            is True
            and scopes[
                "all_ready_for_activation_review"
            ]
            is True
        ),
        "scope_window_not_activated": (
            scopes[
                "no_scope_freezes_activated"
            ]
            is True
            and scopes[
                "no_commit_windows_activated"
            ]
            is True
            and scopes[
                "no_execution_windows_open"
            ]
            is True
            and scopes["no_commit_points_open"]
            is True
            and scopes[
                "no_production_targets_allowed"
            ]
            is True
            and scopes[
                "no_external_providers_allowed"
            ]
            is True
        ),

        "barrier_reviews_present": (
            barriers["review_count"] >= 1
        ),
        "write_barriers_and_rollback_ready": (
            barriers[
                "all_command_sequences_simulated"
            ]
            is True
            and barriers[
                "all_write_barriers_engaged"
            ]
            is True
            and barriers[
                "all_abort_on_mismatch"
            ]
            is True
            and barriers[
                "all_rollback_on_mutation"
            ]
            is True
            and barriers[
                "all_expected_integrity_matches"
            ]
            is True
        ),
        "no_real_mutation_occurred": (
            barriers[
                "no_real_commit_commands"
            ]
            is True
            and barriers["no_actual_restores"]
            is True
            and barriers[
                "no_production_writes"
            ]
            is True
            and barriers[
                "no_final_index_writes"
            ]
            is True
            and barriers["no_pack_overwrites"]
            is True
            and barriers[
                "no_sealed_bytes_writes"
            ]
            is True
            and barriers[
                "no_package_materialization"
            ]
            is True
            and barriers["no_actual_mutations"]
            is True
        ),

        "decision_drafts_present": (
            decisions["decision_count"] >= 1
        ),
        "technical_review_complete": (
            decisions[
                "all_evidence_reviews_complete"
            ]
            is True
            and decisions[
                "all_precondition_reviews_complete"
            ]
            is True
            and decisions[
                "all_barrier_reviews_complete"
            ]
            is True
            and decisions[
                "all_eligible_for_owner_decision_review"
            ]
            is True
            and decisions[
                "all_technical_dry_runs_passed"
            ]
            is True
        ),
        "final_decision_correctly_held": (
            decisions[
                "no_approval_gates_complete"
            ]
            is True
            and decisions[
                "no_activation_gates_complete"
            ]
            is True
            and decisions[
                "all_decisions_are_no_go_hold"
            ]
            is True
            and decisions[
                "no_live_authorization_granted"
            ]
            is True
            and decisions["no_tokens_issued"]
            is True
            and decisions[
                "no_commit_commands_issued"
            ]
            is True
            and decisions[
                "no_restore_or_write_allowed"
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
                "all_no_go_holds_recorded"
            ]
            is True
            and receipts[
                "no_go_decisions_recorded"
            ]
            is True
            and receipts[
                "no_authorization_or_token_recorded"
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
                LOCKS["real_commit_attempted"]
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
                    "final_rebuilt_index_write_allowed"
                ]
                is False,
                LOCKS[
                    "final_pack_overwrite_allowed"
                ]
                is False,
                LOCKS[
                    "sealed_pack_bytes_write_allowed"
                ]
                is False,
                LOCKS[
                    "backup_package_materialization_allowed"
                ]
                is False,
                LOCKS[
                    "production_mount_allowed"
                ]
                is False,
                LOCKS[
                    "writable_mount_allowed"
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
        "gp": 590,
        "title": (
            "Final Go/No-Go Review Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Recovery commit final "
                "go-no-go review blocked"
            )
        ),
        "checks": checks,
        "current_decision": CURRENT_DECISION,
        "decision_status": (
            "technical_dry_run_passed_"
            "final_no_go_hold_correctly_applied"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION PREPARATION LAYER / GP591-GP600"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
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
            "no real commit point open",
            "no real commit command",
            "no actual restore execution",
            "no production mount or writable mount",
            "no production recovery write",
            "no final rebuilt index write",
            "no sealed-pack overwrite",
            "no sealed bytes write",
            "no backup-package materialization",
            "no external provider connection",
            "no Teller-to-Vault direct call",
            "no resident, vendor, employee, customer, or public access",
            "no raw bytes, paths, URLs, or tokens",
            "no delete, purge, or quarantine release",
            "no physical object movement",
        ],
    }


def get_recovery_commit_final_go_no_go_review_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_final_go_no_go_review_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": (
            checkpoint["readiness_label"]
        ),
        "current_decision": CURRENT_DECISION,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "packs": PACKS,
        "checkpoint": checkpoint,
    }


def validate_recovery_commit_final_go_no_go_review_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_final_go_no_go_review_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True
    assert checkpoint["current_decision"] == (
        CURRENT_DECISION
    )
    assert checkpoint[
        "operational_readiness_gate_reached"
    ] is False
    assert checkpoint["corridor_continues"] is True

    for check_name, passed in checkpoint[
        "checks"
    ].items():
        assert passed is True, check_name

    return {
        "ok": True,
        "section": SECTION,
        "ready": True,
        "current_decision": CURRENT_DECISION,
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
        get_final_go_no_go_review_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "current_decision": CURRENT_DECISION,
        "go_decision_granted": False,
        "no_go_hold_required": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "commit_point_closed": True,
        "real_commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "locks_preserved": True,
    }


def get_gp581_status():
    return _gp_status(581)


def get_gp582_status():
    return _gp_status(582)


def get_gp583_status():
    return _gp_status(583)


def get_gp584_status():
    return _gp_status(584)


def get_gp585_status():
    return _gp_status(585)


def get_gp586_status():
    return _gp_status(586)


def get_gp587_status():
    return _gp_status(587)


def get_gp588_status():
    return _gp_status(588)


def get_gp589_status():
    return _gp_status(589)


def get_gp590_status():
    return _gp_status(590)
