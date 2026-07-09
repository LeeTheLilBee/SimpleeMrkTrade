
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — CONTROLLED RECOVERY COMMIT "
    "EXECUTION DRY-RUN LAYER / GP571-GP580"
)

LAYER_ID = (
    "vault_gp571_580_"
    "controlled_recovery_commit_execution_dry_run_layer"
)

READINESS_LABEL = (
    "Controlled recovery commit execution dry-run ready"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_controlled_recovery_commit_execution_dry_run_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_authorization_closeout_layer_service import (
        get_recovery_staging_evidence_closeout_intake_board,
        get_tower_recovery_commit_authority_reconfirmation_board,
        get_owner_admin_step_up_dual_receipt_closeout_board,
        get_recovery_commit_scope_freeze_board,
        get_recovery_commit_window_draft_board,
        get_one_time_commit_authorization_closeout_draft_board,
        get_tower_recovery_commit_authorization_receipt_draft_ledger,
        validate_recovery_commit_authorization_closeout_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP571-GP580 requires the completed "
        "GP561-GP570 recovery commit authorization closeout layer."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "tower_is_only_recovery_commit_authority": True,
    "commit_execution_dry_run_only": True,
    "hash_only_simulation": True,
    "isolated_sandbox_required": True,
    "write_barriers_required": True,
    "rollback_simulation_required": True,
    "commit_point_closed": True,
    "live_authorization_granted": False,
    "authorization_token_issued": False,
    "scope_freeze_activated": False,
    "commit_window_activated": False,
    "execution_window_open": False,
    "commit_command_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "controlled_commit_dry_run_layer": True,
    "closeout_intake_allowed": True,
    "precondition_verification_allowed": True,
    "isolated_sandbox_drafts_allowed": True,
    "commit_command_simulation_allowed": True,
    "write_barrier_simulation_allowed": True,
    "rollback_simulation_allowed": True,
    "outcome_diff_preview_allowed": True,
    "dry_run_receipt_drafts_allowed": True,

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

    "owner_admin_approval_granted": False,
    "step_up_satisfied": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,

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

    "teller_direct_dry_run_allowed": False,
    "teller_direct_authorization_allowed": False,
    "teller_direct_restore_allowed": False,
    "teller_to_vault_direct_call_allowed": False,

    "direct_vault_user_portal_allowed": False,
    "public_vault_dashboard_allowed": False,
    "standalone_external_vault_dashboard_allowed": False,

    "hard_delete_allowed": False,
    "purge_allowed": False,
    "quarantine_release_allowed": False,
    "physical_media_write_allowed": False,
    "physical_object_move_allowed": False,
}


PACKS = [
    {
        "gp": 571,
        "title": (
            "Controlled Recovery Commit "
            "Execution Dry-Run Shell"
        ),
        "route": (
            "/vault/controlled-recovery-commit-"
            "execution-dry-run-shell.json"
        ),
    },
    {
        "gp": 572,
        "title": "Recovery Commit Closeout Intake Board",
        "route": (
            "/vault/recovery-commit-"
            "closeout-intake-board.json"
        ),
    },
    {
        "gp": 573,
        "title": (
            "Recovery Commit Preconditions "
            "Verification Board"
        ),
        "route": (
            "/vault/recovery-commit-preconditions-"
            "verification-board.json"
        ),
    },
    {
        "gp": 574,
        "title": (
            "Isolated Commit Execution Sandbox Board"
        ),
        "route": (
            "/vault/isolated-commit-execution-"
            "sandbox-board.json"
        ),
    },
    {
        "gp": 575,
        "title": "Recovery Commit Command Simulation Queue",
        "route": (
            "/vault/recovery-commit-command-"
            "simulation-queue.json"
        ),
    },
    {
        "gp": 576,
        "title": (
            "Recovery Write Barrier and "
            "Rollback Simulation Board"
        ),
        "route": (
            "/vault/recovery-write-barrier-rollback-"
            "simulation-board.json"
        ),
    },
    {
        "gp": 577,
        "title": (
            "Commit Outcome Diff and "
            "Integrity Preview Board"
        ),
        "route": (
            "/vault/commit-outcome-diff-integrity-"
            "preview-board.json"
        ),
    },
    {
        "gp": 578,
        "title": (
            "Tower Recovery Commit Dry-Run "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-recovery-commit-dry-run-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 579,
        "title": (
            "Controlled Commit Dry-Run "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/controlled-commit-dry-run-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 580,
        "title": (
            "Controlled Recovery Commit "
            "Dry-Run Readiness Checkpoint"
        ),
        "route": (
            "/vault/controlled-recovery-commit-"
            "dry-run-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "The dry-run cannot grant live authorization.",
    ),
    (
        "no_authorization_token",
        "recovery_authorization_token_issue",
        "The dry-run cannot issue a recovery token.",
    ),
    (
        "no_scope_freeze_activation",
        "scope_freeze_activation",
        "The scope-freeze record remains inactive.",
    ),
    (
        "no_commit_window_activation",
        "commit_window_activation",
        "The commit window remains inactive.",
    ),
    (
        "no_execution_window",
        "execution_window_open",
        "The execution window remains closed.",
    ),
    (
        "no_commit_point_open",
        "commit_point_open",
        "The real commit point remains closed.",
    ),
    (
        "no_real_commit_command",
        "real_commit_command",
        "Only a hash-only command simulation is permitted.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "No restore operation is executed.",
    ),
    (
        "no_production_mount",
        "production_storage_mount",
        "Production storage cannot be mounted.",
    ),
    (
        "no_writable_mount",
        "writable_recovery_mount",
        "No writable recovery mount is created.",
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
        "No external recovery provider is connected.",
    ),
    (
        "no_teller_dry_run",
        "teller_direct_commit_dry_run",
        "Tower controls recovery dry-runs.",
    ),
    (
        "no_teller_vault_call",
        "teller_to_vault_direct_call",
        "Teller must route through Tower.",
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
        "No token is generated or exposed.",
    ),
    (
        "no_public_link",
        "public_recovery_link",
        "Recovery remains private and Tower-controlled.",
    ),
    (
        "no_delete_purge_release",
        "delete_purge_quarantine_release",
        "The dry-run cannot delete, purge, or release.",
    ),
    (
        "no_physical_move",
        "physical_object_move",
        "The dry-run cannot move physical media.",
    ),
]


COMMAND_SEQUENCE = [
    {
        "order": 1,
        "command": "verify_closeout_package_hashes",
        "mode": "read_only_hash_verification",
    },
    {
        "order": 2,
        "command": "verify_tower_commit_authority",
        "mode": "authority_contract_verification",
    },
    {
        "order": 3,
        "command": "verify_pending_approval_requirements",
        "mode": "requirement_verification_only",
    },
    {
        "order": 4,
        "command": "bind_exact_scope_freeze_draft",
        "mode": "hash_binding_simulation",
    },
    {
        "order": 5,
        "command": "bind_one_time_commit_window_draft",
        "mode": "window_binding_simulation",
    },
    {
        "order": 6,
        "command": "simulate_commit_preflight",
        "mode": "isolated_sandbox_simulation",
    },
    {
        "order": 7,
        "command": "simulate_recovery_commit_command",
        "mode": "no_write_command_simulation",
    },
    {
        "order": 8,
        "command": "simulate_write_barriers",
        "mode": "all_writes_blocked",
    },
    {
        "order": 9,
        "command": "simulate_abort_and_rollback",
        "mode": "rollback_hash_simulation",
    },
    {
        "order": 10,
        "command": "preview_commit_outcome_integrity",
        "mode": "hash_only_outcome_preview",
    },
    {
        "order": 11,
        "command": "draft_tower_commit_dry_run_receipt",
        "mode": "append_only_draft",
    },
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
        get_recovery_staging_evidence_closeout_intake_board()
        .get("closeout_intakes", [])
    )

    authority_rows = (
        get_tower_recovery_commit_authority_reconfirmation_board()
        .get("authority_reconfirmations", [])
    )

    approval_rows = (
        get_owner_admin_step_up_dual_receipt_closeout_board()
        .get("approval_closeouts", [])
    )

    scope_rows = (
        get_recovery_commit_scope_freeze_board()
        .get("scope_freezes", [])
    )

    window_rows = (
        get_recovery_commit_window_draft_board()
        .get("commit_window_drafts", [])
    )

    draft_rows = (
        get_one_time_commit_authorization_closeout_draft_board()
        .get("closeout_drafts", [])
    )

    receipt_rows = (
        get_tower_recovery_commit_authorization_receipt_draft_ledger()
        .get("closeout_receipt_drafts", [])
    )

    authority_by_request = {
        row["request_id"]: row
        for row in authority_rows
    }

    approval_by_request = {
        row["request_id"]: row
        for row in approval_rows
    }

    scope_by_request = {
        row["request_id"]: row
        for row in scope_rows
    }

    window_by_request = {
        row["request_id"]: row
        for row in window_rows
    }

    draft_by_request = {
        row["request_id"]: row
        for row in draft_rows
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
                "authority": authority_by_request.get(
                    request_id,
                    {},
                ),
                "approval": approval_by_request.get(
                    request_id,
                    {},
                ),
                "scope": scope_by_request.get(
                    request_id,
                    {},
                ),
                "window": window_by_request.get(
                    request_id,
                    {},
                ),
                "draft": draft_by_request.get(
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
        validate_recovery_commit_authorization_closeout_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS dry_run_intakes (
                dry_run_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                closeout_evidence_verified INTEGER NOT NULL,
                tower_authority_verified INTEGER NOT NULL,
                approval_requirements_verified INTEGER NOT NULL,
                scope_freeze_draft_verified INTEGER NOT NULL,
                commit_window_draft_verified INTEGER NOT NULL,
                closeout_draft_verified INTEGER NOT NULL,
                closeout_receipt_verified INTEGER NOT NULL,
                eligible_for_commit_dry_run INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS precondition_verifications (
                precondition_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                evidence_closeout_complete INTEGER NOT NULL,
                tower_authority_reconfirmed INTEGER NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                second_authority_review_required INTEGER NOT NULL,
                all_approval_decisions_pending INTEGER NOT NULL,
                exact_scope_bound INTEGER NOT NULL,
                one_time_window_required INTEGER NOT NULL,
                scope_freeze_inactive INTEGER NOT NULL,
                commit_window_inactive INTEGER NOT NULL,
                commit_point_closed INTEGER NOT NULL,
                precondition_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commit_sandboxes (
                sandbox_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                isolated INTEGER NOT NULL,
                ephemeral INTEGER NOT NULL,
                hash_only INTEGER NOT NULL,
                production_mount_allowed INTEGER NOT NULL,
                writable_mount_allowed INTEGER NOT NULL,
                network_egress_allowed INTEGER NOT NULL,
                external_provider_connection_allowed INTEGER NOT NULL,
                raw_bytes_materialized INTEGER NOT NULL,
                raw_paths_exposed INTEGER NOT NULL,
                sandbox_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS command_simulations (
                command_simulation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                sandbox_id TEXT NOT NULL,
                state TEXT NOT NULL,
                command_sequence_json TEXT NOT NULL,
                simulated_command_count INTEGER NOT NULL,
                simulated_commit_command INTEGER NOT NULL,
                real_commit_command_count INTEGER NOT NULL,
                actual_restore_count INTEGER NOT NULL,
                production_write_count INTEGER NOT NULL,
                final_index_write_count INTEGER NOT NULL,
                pack_overwrite_count INTEGER NOT NULL,
                sealed_bytes_write_count INTEGER NOT NULL,
                package_materialization_count INTEGER NOT NULL,
                command_simulation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS barrier_simulations (
                barrier_simulation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                command_simulation_id TEXT NOT NULL,
                state TEXT NOT NULL,
                production_write_barrier_engaged INTEGER NOT NULL,
                final_index_barrier_engaged INTEGER NOT NULL,
                pack_overwrite_barrier_engaged INTEGER NOT NULL,
                sealed_bytes_barrier_engaged INTEGER NOT NULL,
                provider_connection_barrier_engaged INTEGER NOT NULL,
                abort_on_any_mismatch INTEGER NOT NULL,
                rollback_on_any_mutation INTEGER NOT NULL,
                simulated_abort_count INTEGER NOT NULL,
                simulated_rollback_count INTEGER NOT NULL,
                actual_abort_count INTEGER NOT NULL,
                actual_rollback_count INTEGER NOT NULL,
                barrier_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS outcome_previews (
                outcome_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                command_simulation_id TEXT NOT NULL,
                barrier_simulation_id TEXT NOT NULL,
                state TEXT NOT NULL,
                source_closeout_hash TEXT NOT NULL,
                simulated_command_hash TEXT NOT NULL,
                simulated_barrier_hash TEXT NOT NULL,
                simulated_outcome_hash TEXT NOT NULL,
                expected_integrity_match INTEGER NOT NULL,
                actual_mutation_count INTEGER NOT NULL,
                production_diff_generated INTEGER NOT NULL,
                raw_bytes_included INTEGER NOT NULL,
                raw_paths_included INTEGER NOT NULL,
                raw_tokens_included INTEGER NOT NULL,
                public_links_included INTEGER NOT NULL,
                outcome_preview_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dry_run_receipt_drafts (
                dry_run_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                precondition_id TEXT NOT NULL,
                sandbox_id TEXT NOT NULL,
                command_simulation_id TEXT NOT NULL,
                barrier_simulation_id TEXT NOT NULL,
                outcome_preview_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                dry_run_recorded INTEGER NOT NULL,
                preconditions_recorded INTEGER NOT NULL,
                sandbox_recorded INTEGER NOT NULL,
                command_simulation_recorded INTEGER NOT NULL,
                barrier_simulation_recorded INTEGER NOT NULL,
                outcome_preview_recorded INTEGER NOT NULL,
                live_authorization_recorded INTEGER NOT NULL,
                authorization_token_recorded INTEGER NOT NULL,
                real_commit_recorded INTEGER NOT NULL,
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
            "dry_run_intakes",
            "precondition_verifications",
            "commit_sandboxes",
            "command_simulations",
            "barrier_simulations",
            "outcome_previews",
            "dry_run_receipt_drafts",
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
            authority = source["authority"]
            approval = source["approval"]
            scope = source["scope"]
            window = source["window"]
            draft = source["draft"]
            receipt = source["receipt"]

            closeout_evidence_verified = all(
                [
                    bool(
                        intake.get(
                            "staging_intake_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "environment_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "action_plan_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "simulation_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "diff_preview_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "commit_lock_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "staging_receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_closeout_draft",
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

            tower_authority_verified = all(
                [
                    authority.get(
                        "requester_service"
                    )
                    == "Tower",
                    bool(
                        authority.get(
                            "tower_identity_reconfirmed",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "tower_permission_reconfirmed",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "recovery_clearance_reconfirmed",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "least_privilege_reconfirmed",
                            0,
                        )
                    ),
                    authority.get(
                        "vault_answer_target"
                    )
                    == "Tower",
                    not bool(
                        authority.get(
                            "teller_authority_allowed",
                            1,
                        )
                    ),
                    not bool(
                        authority.get(
                            "direct_vault_user_access_allowed",
                            1,
                        )
                    ),
                    len(
                        authority.get(
                            "authority_reconfirmation_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            approval_requirements_verified = all(
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
                    bool(
                        approval.get(
                            "closeout_requirements_packaged",
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
                            "live_authorization_allowed",
                            1,
                        )
                    ),
                    len(
                        approval.get(
                            "approval_closeout_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            scope_freeze_draft_verified = all(
                [
                    bool(
                        scope.get(
                            "request_bound",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "environment_bound",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "action_plan_bound",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "mutation_diff_bound",
                            0,
                        )
                    ),
                    not bool(
                        scope.get(
                            "scope_expansion_allowed",
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
                    not bool(
                        scope.get(
                            "scope_freeze_activated",
                            1,
                        )
                    ),
                    len(
                        scope.get(
                            "scope_freeze_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            commit_window_draft_verified = all(
                [
                    bool(
                        window.get(
                            "one_time_window_required",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "request_bound",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "scope_bound",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "authority_bound",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "expiry_required",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "activation_requires_owner_admin",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "activation_requires_step_up",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "activation_requires_dual_receipt",
                            0,
                        )
                    ),
                    bool(
                        window.get(
                            "activation_requires_second_authority",
                            0,
                        )
                    ),
                    not bool(
                        window.get(
                            "commit_window_activated",
                            1,
                        )
                    ),
                    not bool(
                        window.get(
                            "execution_window_open",
                            1,
                        )
                    ),
                    not bool(
                        window.get(
                            "commit_point_open",
                            1,
                        )
                    ),
                    len(
                        window.get(
                            "commit_window_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            closeout_draft_verified = all(
                [
                    bool(
                        draft.get(
                            "evidence_closeout_complete",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "authority_reconfirmation_complete",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "approval_requirements_packaged",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "scope_freeze_draft_complete",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "commit_window_draft_complete",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "one_time_authorization_required",
                            0,
                        )
                    ),
                    not bool(
                        draft.get(
                            "authorization_granted",
                            1,
                        )
                    ),
                    not bool(
                        draft.get(
                            "authorization_token_issued",
                            1,
                        )
                    ),
                    not bool(
                        draft.get(
                            "commit_command_issued",
                            1,
                        )
                    ),
                    not bool(
                        draft.get(
                            "actual_restore_allowed",
                            1,
                        )
                    ),
                    not bool(
                        draft.get(
                            "production_write_allowed",
                            1,
                        )
                    ),
                    len(
                        draft.get(
                            "closeout_draft_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            closeout_receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "evidence_closeout_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "authority_reconfirmation_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "approval_requirements_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "scope_freeze_draft_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "commit_window_draft_recorded",
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

            eligible_for_commit_dry_run = all(
                [
                    closeout_evidence_verified,
                    tower_authority_verified,
                    approval_requirements_verified,
                    scope_freeze_draft_verified,
                    commit_window_draft_verified,
                    closeout_draft_verified,
                    closeout_receipt_verified,
                ]
            )

            dry_run_intake_id = _id(
                "commit_dry_run_intake",
                request_id,
            )

            precondition_id = _id(
                "commit_preconditions",
                request_id,
            )

            sandbox_id = _id(
                "commit_execution_sandbox",
                request_id,
            )

            command_simulation_id = _id(
                "commit_command_simulation",
                request_id,
            )

            barrier_simulation_id = _id(
                "write_barrier_simulation",
                request_id,
            )

            outcome_preview_id = _id(
                "commit_outcome_preview",
                request_id,
            )

            dry_run_receipt_id = _id(
                "tower_commit_dry_run_receipt",
                request_id,
            )

            connection.execute(
                """
                INSERT INTO dry_run_intakes (
                    dry_run_intake_id,
                    request_id,
                    workflow_type,
                    state,
                    closeout_evidence_verified,
                    tower_authority_verified,
                    approval_requirements_verified,
                    scope_freeze_draft_verified,
                    commit_window_draft_verified,
                    closeout_draft_verified,
                    closeout_receipt_verified,
                    eligible_for_commit_dry_run,
                    live_authorization_granted,
                    commit_point_open,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    dry_run_intake_id,
                    request_id,
                    workflow_type,
                    (
                        "eligible_for_commit_execution_"
                        "dry_run_not_live_commit"
                    ),
                    int(closeout_evidence_verified),
                    int(tower_authority_verified),
                    int(approval_requirements_verified),
                    int(scope_freeze_draft_verified),
                    int(commit_window_draft_verified),
                    int(closeout_draft_verified),
                    int(closeout_receipt_verified),
                    int(eligible_for_commit_dry_run),
                    0,
                    0,
                    now,
                ),
            )

            precondition_payload = {
                "request_id": request_id,
                "evidence_closeout_complete": (
                    closeout_evidence_verified
                ),
                "tower_authority_reconfirmed": (
                    tower_authority_verified
                ),
                "owner_admin_approval_required": True,
                "step_up_required": True,
                "dual_receipt_required": True,
                "second_authority_review_required": True,
                "all_approval_decisions_pending": True,
                "exact_scope_bound": (
                    scope_freeze_draft_verified
                ),
                "one_time_window_required": (
                    commit_window_draft_verified
                ),
                "scope_freeze_inactive": True,
                "commit_window_inactive": True,
                "commit_point_closed": True,
            }

            precondition_hash = _canonical_hash(
                precondition_payload
            )

            connection.execute(
                """
                INSERT INTO precondition_verifications (
                    precondition_id,
                    request_id,
                    state,
                    evidence_closeout_complete,
                    tower_authority_reconfirmed,
                    owner_admin_approval_required,
                    step_up_required,
                    dual_receipt_required,
                    second_authority_review_required,
                    all_approval_decisions_pending,
                    exact_scope_bound,
                    one_time_window_required,
                    scope_freeze_inactive,
                    commit_window_inactive,
                    commit_point_closed,
                    precondition_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    precondition_id,
                    request_id,
                    (
                        "commit_preconditions_verified_"
                        "approvals_pending_commit_closed"
                    ),
                    int(closeout_evidence_verified),
                    int(tower_authority_verified),
                    1,
                    1,
                    1,
                    1,
                    1,
                    int(scope_freeze_draft_verified),
                    int(commit_window_draft_verified),
                    1,
                    1,
                    1,
                    precondition_hash,
                    now,
                ),
            )

            sandbox_payload = {
                "request_id": request_id,
                "isolated": True,
                "ephemeral": True,
                "hash_only": True,
                "production_mount_allowed": False,
                "writable_mount_allowed": False,
                "network_egress_allowed": False,
                "external_provider_connection_allowed": False,
                "raw_bytes_materialized": False,
                "raw_paths_exposed": False,
            }

            sandbox_hash = _canonical_hash(
                sandbox_payload
            )

            connection.execute(
                """
                INSERT INTO commit_sandboxes (
                    sandbox_id,
                    request_id,
                    state,
                    isolated,
                    ephemeral,
                    hash_only,
                    production_mount_allowed,
                    writable_mount_allowed,
                    network_egress_allowed,
                    external_provider_connection_allowed,
                    raw_bytes_materialized,
                    raw_paths_exposed,
                    sandbox_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?
                )
                """,
                (
                    sandbox_id,
                    request_id,
                    (
                        "isolated_hash_only_commit_"
                        "sandbox_not_mounted"
                    ),
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    sandbox_hash,
                    now,
                ),
            )

            command_payload = {
                "request_id": request_id,
                "sandbox_id": sandbox_id,
                "commands": COMMAND_SEQUENCE,
                "simulated_commit_command": True,
                "real_commit_command_count": 0,
                "actual_restore_count": 0,
                "production_write_count": 0,
                "final_index_write_count": 0,
                "pack_overwrite_count": 0,
                "sealed_bytes_write_count": 0,
                "package_materialization_count": 0,
            }

            command_simulation_hash = _canonical_hash(
                command_payload
            )

            command_sequence_json = json.dumps(
                COMMAND_SEQUENCE,
                sort_keys=True,
                separators=(",", ":"),
            )

            connection.execute(
                """
                INSERT INTO command_simulations (
                    command_simulation_id,
                    request_id,
                    sandbox_id,
                    state,
                    command_sequence_json,
                    simulated_command_count,
                    simulated_commit_command,
                    real_commit_command_count,
                    actual_restore_count,
                    production_write_count,
                    final_index_write_count,
                    pack_overwrite_count,
                    sealed_bytes_write_count,
                    package_materialization_count,
                    command_simulation_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    command_simulation_id,
                    request_id,
                    sandbox_id,
                    (
                        "commit_command_sequence_"
                        "simulated_no_real_command"
                    ),
                    command_sequence_json,
                    len(COMMAND_SEQUENCE),
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    command_simulation_hash,
                    now,
                ),
            )

            barrier_payload = {
                "request_id": request_id,
                "command_simulation_id": (
                    command_simulation_id
                ),
                "production_write_barrier_engaged": True,
                "final_index_barrier_engaged": True,
                "pack_overwrite_barrier_engaged": True,
                "sealed_bytes_barrier_engaged": True,
                "provider_connection_barrier_engaged": True,
                "abort_on_any_mismatch": True,
                "rollback_on_any_mutation": True,
                "simulated_abort_count": 1,
                "simulated_rollback_count": 1,
                "actual_abort_count": 0,
                "actual_rollback_count": 0,
            }

            barrier_hash = _canonical_hash(
                barrier_payload
            )

            connection.execute(
                """
                INSERT INTO barrier_simulations (
                    barrier_simulation_id,
                    request_id,
                    command_simulation_id,
                    state,
                    production_write_barrier_engaged,
                    final_index_barrier_engaged,
                    pack_overwrite_barrier_engaged,
                    sealed_bytes_barrier_engaged,
                    provider_connection_barrier_engaged,
                    abort_on_any_mismatch,
                    rollback_on_any_mutation,
                    simulated_abort_count,
                    simulated_rollback_count,
                    actual_abort_count,
                    actual_rollback_count,
                    barrier_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    barrier_simulation_id,
                    request_id,
                    command_simulation_id,
                    (
                        "all_write_barriers_engaged_"
                        "abort_rollback_simulated"
                    ),
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
                    0,
                    barrier_hash,
                    now,
                ),
            )

            source_closeout_hash = draft.get(
                "closeout_draft_hash",
                "",
            )

            simulated_outcome_payload = {
                "request_id": request_id,
                "source_closeout_hash": (
                    source_closeout_hash
                ),
                "command_simulation_hash": (
                    command_simulation_hash
                ),
                "barrier_hash": barrier_hash,
                "expected_integrity_match": True,
                "actual_mutation_count": 0,
                "production_diff_generated": False,
            }

            simulated_outcome_hash = _canonical_hash(
                simulated_outcome_payload
            )

            outcome_preview_payload = {
                "request_id": request_id,
                "source_closeout_hash": (
                    source_closeout_hash
                ),
                "simulated_command_hash": (
                    command_simulation_hash
                ),
                "simulated_barrier_hash": barrier_hash,
                "simulated_outcome_hash": (
                    simulated_outcome_hash
                ),
                "expected_integrity_match": True,
                "actual_mutation_count": 0,
                "production_diff_generated": False,
                "raw_bytes_included": False,
                "raw_paths_included": False,
                "raw_tokens_included": False,
                "public_links_included": False,
            }

            outcome_preview_hash = _canonical_hash(
                outcome_preview_payload
            )

            connection.execute(
                """
                INSERT INTO outcome_previews (
                    outcome_preview_id,
                    request_id,
                    command_simulation_id,
                    barrier_simulation_id,
                    state,
                    source_closeout_hash,
                    simulated_command_hash,
                    simulated_barrier_hash,
                    simulated_outcome_hash,
                    expected_integrity_match,
                    actual_mutation_count,
                    production_diff_generated,
                    raw_bytes_included,
                    raw_paths_included,
                    raw_tokens_included,
                    public_links_included,
                    outcome_preview_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    outcome_preview_id,
                    request_id,
                    command_simulation_id,
                    barrier_simulation_id,
                    (
                        "commit_outcome_integrity_"
                        "preview_hash_only"
                    ),
                    source_closeout_hash,
                    command_simulation_hash,
                    barrier_hash,
                    simulated_outcome_hash,
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    outcome_preview_hash,
                    now,
                ),
            )

            receipt_payload = {
                "request_id": request_id,
                "precondition_id": precondition_id,
                "sandbox_id": sandbox_id,
                "command_simulation_id": (
                    command_simulation_id
                ),
                "barrier_simulation_id": (
                    barrier_simulation_id
                ),
                "outcome_preview_id": outcome_preview_id,
                "dry_run_recorded": True,
                "preconditions_recorded": True,
                "sandbox_recorded": True,
                "command_simulation_recorded": True,
                "barrier_simulation_recorded": True,
                "outcome_preview_recorded": True,
                "live_authorization_recorded": False,
                "authorization_token_recorded": False,
                "real_commit_recorded": False,
                "actual_restore_recorded": False,
                "production_write_recorded": False,
            }

            receipt_hash = _canonical_hash(
                receipt_payload
            )

            connection.execute(
                """
                INSERT INTO dry_run_receipt_drafts (
                    dry_run_receipt_id,
                    request_id,
                    precondition_id,
                    sandbox_id,
                    command_simulation_id,
                    barrier_simulation_id,
                    outcome_preview_id,
                    state,
                    tower_controlled,
                    dry_run_recorded,
                    preconditions_recorded,
                    sandbox_recorded,
                    command_simulation_recorded,
                    barrier_simulation_recorded,
                    outcome_preview_recorded,
                    live_authorization_recorded,
                    authorization_token_recorded,
                    real_commit_recorded,
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
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    dry_run_receipt_id,
                    request_id,
                    precondition_id,
                    sandbox_id,
                    command_simulation_id,
                    barrier_simulation_id,
                    outcome_preview_id,
                    (
                        "tower_commit_execution_"
                        "dry_run_receipt_draft"
                    ),
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
                    1,
                    0,
                    receipt_hash,
                    now,
                ),
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_closeout_layer_ready": bool(
            previous.get("ready", False)
        ),
        "db_path": str(
            DB_PATH.relative_to(PROJECT_ROOT)
        ),
    }

    _INIT_CACHE = dict(result)
    return result


def get_controlled_recovery_commit_execution_dry_run_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 571,
        "title": (
            "Controlled Recovery Commit "
            "Execution Dry-Run Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "dry_run_only": True,
        "hash_only_simulation": True,
        "commit_point_closed": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "real_commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_recovery_commit_closeout_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM dry_run_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 572,
        "title": "Recovery Commit Closeout Intake Board",
        "ready": True,
        "intake_count": len(rows),
        "dry_run_intakes": rows,
        "all_closeout_evidence_verified": all(
            bool(row["closeout_evidence_verified"])
            for row in rows
        ),
        "all_tower_authority_verified": all(
            bool(row["tower_authority_verified"])
            for row in rows
        ),
        "all_approval_requirements_verified": all(
            bool(
                row["approval_requirements_verified"]
            )
            for row in rows
        ),
        "all_scope_freezes_verified": all(
            bool(row["scope_freeze_draft_verified"])
            for row in rows
        ),
        "all_commit_windows_verified": all(
            bool(row["commit_window_draft_verified"])
            for row in rows
        ),
        "all_closeout_drafts_verified": all(
            bool(row["closeout_draft_verified"])
            for row in rows
        ),
        "all_closeout_receipts_verified": all(
            bool(row["closeout_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_commit_dry_run": all(
            bool(row["eligible_for_commit_dry_run"])
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


def get_recovery_commit_preconditions_verification_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM precondition_verifications
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 573,
        "title": (
            "Recovery Commit Preconditions "
            "Verification Board"
        ),
        "ready": True,
        "precondition_count": len(rows),
        "precondition_verifications": rows,
        "all_evidence_closeouts_complete": all(
            bool(row["evidence_closeout_complete"])
            for row in rows
        ),
        "all_tower_authority_reconfirmed": all(
            bool(row["tower_authority_reconfirmed"])
            for row in rows
        ),
        "all_approval_requirements_present": all(
            bool(row["owner_admin_approval_required"])
            and bool(row["step_up_required"])
            and bool(row["dual_receipt_required"])
            and bool(
                row["second_authority_review_required"]
            )
            for row in rows
        ),
        "all_approval_decisions_pending": all(
            bool(row["all_approval_decisions_pending"])
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
        "all_scope_freezes_inactive": all(
            bool(row["scope_freeze_inactive"])
            for row in rows
        ),
        "all_commit_windows_inactive": all(
            bool(row["commit_window_inactive"])
            for row in rows
        ),
        "all_commit_points_closed": all(
            bool(row["commit_point_closed"])
            for row in rows
        ),
        "all_precondition_hashes_present": all(
            len(row["precondition_hash"]) == 64
            for row in rows
        ),
    }


def get_isolated_commit_execution_sandbox_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM commit_sandboxes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 574,
        "title": (
            "Isolated Commit Execution Sandbox Board"
        ),
        "ready": True,
        "sandbox_count": len(rows),
        "commit_sandboxes": rows,
        "all_isolated": all(
            bool(row["isolated"])
            for row in rows
        ),
        "all_ephemeral": all(
            bool(row["ephemeral"])
            for row in rows
        ),
        "all_hash_only": all(
            bool(row["hash_only"])
            for row in rows
        ),
        "no_production_mount": all(
            not bool(row["production_mount_allowed"])
            for row in rows
        ),
        "no_writable_mount": all(
            not bool(row["writable_mount_allowed"])
            for row in rows
        ),
        "no_network_egress": all(
            not bool(row["network_egress_allowed"])
            for row in rows
        ),
        "no_external_provider_connection": all(
            not bool(
                row[
                    "external_provider_connection_allowed"
                ]
            )
            for row in rows
        ),
        "no_raw_bytes_materialized": all(
            not bool(row["raw_bytes_materialized"])
            for row in rows
        ),
        "no_raw_paths_exposed": all(
            not bool(row["raw_paths_exposed"])
            for row in rows
        ),
        "all_sandbox_hashes_present": all(
            len(row["sandbox_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_commit_command_simulation_queue(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM command_simulations
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 575,
        "title": (
            "Recovery Commit Command Simulation Queue"
        ),
        "ready": True,
        "simulation_count": len(rows),
        "command_simulations": rows,
        "all_sequences_complete": all(
            row["simulated_command_count"]
            == len(COMMAND_SEQUENCE)
            for row in rows
        ),
        "all_commit_commands_simulated": all(
            bool(row["simulated_commit_command"])
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
        "all_command_hashes_present": all(
            len(row["command_simulation_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_write_barrier_rollback_simulation_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM barrier_simulations
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 576,
        "title": (
            "Recovery Write Barrier and "
            "Rollback Simulation Board"
        ),
        "ready": True,
        "simulation_count": len(rows),
        "barrier_simulations": rows,
        "all_write_barriers_engaged": all(
            bool(
                row["production_write_barrier_engaged"]
            )
            and bool(
                row["final_index_barrier_engaged"]
            )
            and bool(
                row["pack_overwrite_barrier_engaged"]
            )
            and bool(
                row["sealed_bytes_barrier_engaged"]
            )
            and bool(
                row["provider_connection_barrier_engaged"]
            )
            for row in rows
        ),
        "all_abort_on_mismatch": all(
            bool(row["abort_on_any_mismatch"])
            for row in rows
        ),
        "all_rollback_on_mutation": all(
            bool(row["rollback_on_any_mutation"])
            for row in rows
        ),
        "all_abort_simulations_present": all(
            row["simulated_abort_count"] >= 1
            for row in rows
        ),
        "all_rollback_simulations_present": all(
            row["simulated_rollback_count"] >= 1
            for row in rows
        ),
        "no_actual_aborts": all(
            row["actual_abort_count"] == 0
            for row in rows
        ),
        "no_actual_rollbacks": all(
            row["actual_rollback_count"] == 0
            for row in rows
        ),
        "all_barrier_hashes_present": all(
            len(row["barrier_hash"]) == 64
            for row in rows
        ),
    }


def get_commit_outcome_diff_integrity_preview_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM outcome_previews
            ORDER BY request_id
            """,
        )

    hash_fields = [
        "source_closeout_hash",
        "simulated_command_hash",
        "simulated_barrier_hash",
        "simulated_outcome_hash",
        "outcome_preview_hash",
    ]

    return {
        "section": SECTION,
        "gp": 577,
        "title": (
            "Commit Outcome Diff and "
            "Integrity Preview Board"
        ),
        "ready": True,
        "preview_count": len(rows),
        "outcome_previews": rows,
        "all_hashes_present": all(
            all(
                len(str(row[field])) == 64
                for field in hash_fields
            )
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
        "no_production_diffs": all(
            not bool(row["production_diff_generated"])
            for row in rows
        ),
        "no_raw_bytes": all(
            not bool(row["raw_bytes_included"])
            for row in rows
        ),
        "no_raw_paths": all(
            not bool(row["raw_paths_included"])
            for row in rows
        ),
        "no_raw_tokens": all(
            not bool(row["raw_tokens_included"])
            for row in rows
        ),
        "no_public_links": all(
            not bool(row["public_links_included"])
            for row in rows
        ),
    }


def get_tower_recovery_commit_dry_run_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM dry_run_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 578,
        "title": (
            "Tower Recovery Commit Dry-Run "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "dry_run_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_dry_run_components_recorded": all(
            bool(row["dry_run_recorded"])
            and bool(row["preconditions_recorded"])
            and bool(row["sandbox_recorded"])
            and bool(
                row["command_simulation_recorded"]
            )
            and bool(
                row["barrier_simulation_recorded"]
            )
            and bool(row["outcome_preview_recorded"])
            for row in rows
        ),
        "no_live_authorization_or_token_recorded": all(
            not bool(
                row["live_authorization_recorded"]
            )
            and not bool(
                row["authorization_token_recorded"]
            )
            for row in rows
        ),
        "no_real_commit_restore_or_write_recorded": all(
            not bool(row["real_commit_recorded"])
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


def get_controlled_commit_dry_run_safety_blocker_board(
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
        "gp": 579,
        "title": (
            "Controlled Commit Dry-Run "
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


def get_controlled_recovery_commit_dry_run_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_controlled_recovery_commit_execution_dry_run_shell()
    )

    intakes = (
        get_recovery_commit_closeout_intake_board()
    )

    preconditions = (
        get_recovery_commit_preconditions_verification_board()
    )

    sandboxes = (
        get_isolated_commit_execution_sandbox_board()
    )

    commands = (
        get_recovery_commit_command_simulation_queue()
    )

    barriers = (
        get_recovery_write_barrier_rollback_simulation_board()
    )

    outcomes = (
        get_commit_outcome_diff_integrity_preview_board()
    )

    receipts = (
        get_tower_recovery_commit_dry_run_receipt_draft_ledger()
    )

    blockers = (
        get_controlled_commit_dry_run_safety_blocker_board()
    )

    checks = {
        "previous_closeout_layer_ready": (
            initialized[
                "previous_closeout_layer_ready"
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
        "dry_run_only": (
            DOCTRINE[
                "commit_execution_dry_run_only"
            ]
            is True
            and DOCTRINE["hash_only_simulation"]
            is True
            and DOCTRINE["isolated_sandbox_required"]
            is True
            and DOCTRINE["write_barriers_required"]
            is True
            and DOCTRINE[
                "rollback_simulation_required"
            ]
            is True
        ),
        "no_live_commit_state": (
            DOCTRINE[
                "live_authorization_granted"
            ]
            is False
            and DOCTRINE[
                "authorization_token_issued"
            ]
            is False
            and DOCTRINE[
                "scope_freeze_activated"
            ]
            is False
            and DOCTRINE[
                "commit_window_activated"
            ]
            is False
            and DOCTRINE[
                "execution_window_open"
            ]
            is False
            and DOCTRINE["commit_point_closed"]
            is True
            and DOCTRINE[
                "commit_command_issued"
            ]
            is False
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "closeout_package_verified": (
            intakes[
                "all_closeout_evidence_verified"
            ]
            is True
            and intakes[
                "all_tower_authority_verified"
            ]
            is True
            and intakes[
                "all_approval_requirements_verified"
            ]
            is True
            and intakes[
                "all_scope_freezes_verified"
            ]
            is True
            and intakes[
                "all_commit_windows_verified"
            ]
            is True
            and intakes[
                "all_closeout_drafts_verified"
            ]
            is True
            and intakes[
                "all_closeout_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_commit_dry_run"
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
            preconditions["precondition_count"] >= 1
        ),
        "preconditions_verified": (
            preconditions[
                "all_evidence_closeouts_complete"
            ]
            is True
            and preconditions[
                "all_tower_authority_reconfirmed"
            ]
            is True
            and preconditions[
                "all_approval_requirements_present"
            ]
            is True
            and preconditions[
                "all_approval_decisions_pending"
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
                "all_scope_freezes_inactive"
            ]
            is True
            and preconditions[
                "all_commit_windows_inactive"
            ]
            is True
            and preconditions[
                "all_commit_points_closed"
            ]
            is True
        ),

        "sandboxes_present": (
            sandboxes["sandbox_count"] >= 1
        ),
        "sandboxes_isolated_hash_only": (
            sandboxes["all_isolated"] is True
            and sandboxes["all_ephemeral"] is True
            and sandboxes["all_hash_only"] is True
            and sandboxes["no_production_mount"]
            is True
            and sandboxes["no_writable_mount"]
            is True
            and sandboxes["no_network_egress"]
            is True
            and sandboxes[
                "no_external_provider_connection"
            ]
            is True
            and sandboxes[
                "no_raw_bytes_materialized"
            ]
            is True
            and sandboxes[
                "no_raw_paths_exposed"
            ]
            is True
        ),

        "command_simulations_present": (
            commands["simulation_count"] >= 1
        ),
        "command_sequence_simulated_only": (
            commands["all_sequences_complete"]
            is True
            and commands[
                "all_commit_commands_simulated"
            ]
            is True
            and commands["no_real_commit_commands"]
            is True
            and commands["no_actual_restores"]
            is True
            and commands["no_production_writes"]
            is True
            and commands["no_final_index_writes"]
            is True
            and commands["no_pack_overwrites"]
            is True
            and commands["no_sealed_bytes_writes"]
            is True
            and commands[
                "no_package_materialization"
            ]
            is True
        ),

        "barrier_simulations_present": (
            barriers["simulation_count"] >= 1
        ),
        "barriers_and_rollback_verified": (
            barriers["all_write_barriers_engaged"]
            is True
            and barriers["all_abort_on_mismatch"]
            is True
            and barriers[
                "all_rollback_on_mutation"
            ]
            is True
            and barriers[
                "all_abort_simulations_present"
            ]
            is True
            and barriers[
                "all_rollback_simulations_present"
            ]
            is True
            and barriers["no_actual_aborts"]
            is True
            and barriers["no_actual_rollbacks"]
            is True
        ),

        "outcomes_present": (
            outcomes["preview_count"] >= 1
        ),
        "outcomes_hash_only_and_clean": (
            outcomes["all_hashes_present"]
            is True
            and outcomes[
                "all_expected_integrity_matches"
            ]
            is True
            and outcomes["no_actual_mutations"]
            is True
            and outcomes["no_production_diffs"]
            is True
            and outcomes["no_raw_bytes"] is True
            and outcomes["no_raw_paths"] is True
            and outcomes["no_raw_tokens"] is True
            and outcomes["no_public_links"] is True
        ),

        "receipts_present": (
            receipts["receipt_count"] >= 1
        ),
        "receipt_drafts_safe": (
            receipts["all_tower_controlled"]
            is True
            and receipts[
                "all_dry_run_components_recorded"
            ]
            is True
            and receipts[
                "no_live_authorization_or_token_recorded"
            ]
            is True
            and receipts[
                "no_real_commit_restore_or_write_recorded"
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
                LOCKS[
                    "execution_window_open"
                ]
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
                LOCKS["production_mount_allowed"]
                is False,
                LOCKS["writable_mount_allowed"]
                is False,
                LOCKS["network_egress_allowed"]
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
                    "direct_vault_user_portal_allowed"
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
        "gp": 580,
        "title": (
            "Controlled Recovery Commit "
            "Dry-Run Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Controlled recovery commit "
                "execution dry-run blocked"
            )
        ),
        "checks": checks,
        "dry_run_status": (
            "commit_execution_sequence_simulated_"
            "all_write_barriers_engaged_"
            "real_commit_closed"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "FINAL GO-NO-GO REVIEW LAYER / GP581-GP590"
        ),
        "still_locked": [
            "no live recovery authorization",
            "no authorization or capability token",
            "no scope-freeze activation",
            "no commit-window activation",
            "no execution window",
            "no real commit point open",
            "no real commit command",
            "no actual restore execution",
            "no production mount or writable mount",
            "no production recovery write",
            "no final rebuilt index write",
            "no pack overwrite",
            "no sealed bytes write",
            "no package materialization",
            "no external provider connection",
            "no Teller-to-Vault direct call",
            "no raw bytes, paths, URLs, or tokens",
            "no public links",
            "no delete, purge, or quarantine release",
            "no physical object movement",
        ],
    }


def get_controlled_recovery_commit_execution_dry_run_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_controlled_recovery_commit_dry_run_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "ready": checkpoint["ready"],
        "readiness_label": (
            checkpoint["readiness_label"]
        ),
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "packs": PACKS,
        "checkpoint": checkpoint,
    }


def validate_controlled_recovery_commit_execution_dry_run_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_controlled_recovery_commit_dry_run_readiness_checkpoint()
    )

    assert checkpoint["ready"] is True

    for check_name, passed in checkpoint[
        "checks"
    ].items():
        assert passed is True, check_name

    return {
        "ok": True,
        "section": SECTION,
        "ready": True,
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
        get_controlled_recovery_commit_dry_run_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "dry_run_only": True,
        "hash_only_simulation": True,
        "commit_point_closed": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "real_commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "locks_preserved": True,
    }


def get_gp571_status():
    return _gp_status(571)


def get_gp572_status():
    return _gp_status(572)


def get_gp573_status():
    return _gp_status(573)


def get_gp574_status():
    return _gp_status(574)


def get_gp575_status():
    return _gp_status(575)


def get_gp576_status():
    return _gp_status(576)


def get_gp577_status():
    return _gp_status(577)


def get_gp578_status():
    return _gp_status(578)


def get_gp579_status():
    return _gp_status(579)


def get_gp580_status():
    return _gp_status(580)
