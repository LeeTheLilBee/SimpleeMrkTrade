
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT "
    "AUTHORIZATION CLOSEOUT LAYER / GP561-GP570"
)

LAYER_ID = (
    "vault_gp561_570_"
    "recovery_commit_authorization_closeout_layer"
)

READINESS_LABEL = (
    "Recovery commit authorization closeout layer ready"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_authorization_closeout_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.controlled_recovery_execution_staging_layer_service import (
        get_authorized_recovery_staging_intake_board,
        get_isolated_recovery_staging_environment_board,
        get_recovery_action_plan_draft_board,
        get_recovery_write_simulation_queue,
        get_recovery_mutation_diff_preview_board,
        get_recovery_commit_point_lock_board,
        get_tower_recovery_staging_receipt_draft_ledger,
        validate_controlled_recovery_execution_staging_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP561-GP570 requires the completed "
        "GP551-GP560 controlled recovery staging layer."
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
    "authorization_closeout_drafts_only": True,
    "scope_freeze_drafts_only": True,
    "commit_window_drafts_only": True,
    "commit_point_closed": True,
    "owner_admin_approval_required": True,
    "step_up_required": True,
    "dual_receipt_required": True,
    "second_authority_review_required": True,
    "live_authorization_granted": False,
    "authorization_token_issued": False,
    "commit_command_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "recovery_commit_authorization_closeout_layer": True,
    "staging_evidence_closeout_allowed": True,
    "tower_authority_reconfirmation_allowed": True,
    "approval_closeout_drafts_allowed": True,
    "scope_freeze_drafts_allowed": True,
    "commit_window_drafts_allowed": True,
    "one_time_commit_closeout_drafts_allowed": True,
    "commit_authorization_receipt_drafts_allowed": True,

    "live_recovery_authorization_granted": False,
    "authorization_token_issued": False,
    "recovery_capability_token_issued": False,
    "recovery_bypass_token_issued": False,

    "scope_freeze_activated": False,
    "commit_window_activated": False,
    "execution_window_open": False,
    "commit_point_open": False,
    "commit_command_issued": False,

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

    "teller_direct_closeout_allowed": False,
    "teller_direct_authorization_allowed": False,
    "teller_direct_restore_allowed": False,
    "teller_to_vault_direct_call_allowed": False,

    "direct_vault_user_portal_allowed": False,
    "public_vault_dashboard_allowed": False,
    "standalone_external_vault_dashboard_allowed": False,
    "employee_vault_browsing_allowed": False,
    "vendor_vault_browsing_allowed": False,
    "customer_vault_browsing_allowed": False,

    "hard_delete_allowed": False,
    "purge_allowed": False,
    "quarantine_release_allowed": False,
    "physical_media_write_allowed": False,
    "physical_object_move_allowed": False,
}


PACKS = [
    {
        "gp": 561,
        "title": (
            "Recovery Commit Authorization "
            "Closeout Shell"
        ),
        "route": (
            "/vault/recovery-commit-authorization-"
            "closeout-shell.json"
        ),
    },
    {
        "gp": 562,
        "title": (
            "Recovery Staging Evidence "
            "Closeout Intake Board"
        ),
        "route": (
            "/vault/recovery-staging-evidence-"
            "closeout-intake-board.json"
        ),
    },
    {
        "gp": 563,
        "title": (
            "Tower Recovery Commit Authority "
            "Reconfirmation Board"
        ),
        "route": (
            "/vault/tower-recovery-commit-authority-"
            "reconfirmation-board.json"
        ),
    },
    {
        "gp": 564,
        "title": (
            "Owner/Admin Step-Up Dual Receipt "
            "Closeout Board"
        ),
        "route": (
            "/vault/owner-admin-step-up-dual-receipt-"
            "closeout-board.json"
        ),
    },
    {
        "gp": 565,
        "title": "Recovery Commit Scope Freeze Board",
        "route": (
            "/vault/recovery-commit-scope-freeze-board.json"
        ),
    },
    {
        "gp": 566,
        "title": "Recovery Commit Window Draft Board",
        "route": (
            "/vault/recovery-commit-window-draft-board.json"
        ),
    },
    {
        "gp": 567,
        "title": (
            "One-Time Commit Authorization "
            "Closeout Draft Board"
        ),
        "route": (
            "/vault/one-time-commit-authorization-"
            "closeout-draft-board.json"
        ),
    },
    {
        "gp": 568,
        "title": (
            "Tower Recovery Commit Authorization "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-recovery-commit-authorization-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 569,
        "title": (
            "Recovery Commit Authorization Closeout "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/recovery-commit-authorization-closeout-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 570,
        "title": (
            "Recovery Commit Authorization Closeout "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/recovery-commit-authorization-"
            "closeout-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "Closeout drafts do not grant live authorization.",
    ),
    (
        "no_authorization_token",
        "recovery_authorization_token_issue",
        "Closeout drafts do not issue recovery tokens.",
    ),
    (
        "no_scope_freeze_activation",
        "recovery_scope_freeze_activation",
        "The scope freeze remains a draft.",
    ),
    (
        "no_commit_window_activation",
        "recovery_commit_window_activation",
        "The commit window remains a draft.",
    ),
    (
        "no_commit_point_open",
        "recovery_commit_point_open",
        "The recovery commit point remains closed.",
    ),
    (
        "no_commit_command",
        "recovery_commit_command",
        "No recovery commit command is issued.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "Authorization closeout does not execute recovery.",
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
        "Production recovery writes remain locked.",
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
        "Sealed pack bytes cannot be written.",
    ),
    (
        "no_package_materialization",
        "backup_package_materialization",
        "Backup packages remain hash-only.",
    ),
    (
        "no_external_provider",
        "external_provider_restore_connection",
        "External recovery providers remain locked.",
    ),
    (
        "no_teller_closeout",
        "teller_direct_commit_authorization_closeout",
        "Tower controls recovery authorization closeout.",
    ),
    (
        "no_teller_vault_call",
        "teller_to_vault_direct_call",
        "Teller must route requests through Tower.",
    ),
    (
        "no_raw_bytes",
        "raw_file_bytes_returned_by_json",
        "Outputs contain metadata and hashes only.",
    ),
    (
        "no_raw_path",
        "raw_path_or_file_url_exposure",
        "Vault paths and file URLs remain sealed.",
    ),
    (
        "no_raw_token",
        "raw_recovery_token_exposure",
        "No recovery token is exposed.",
    ),
    (
        "no_public_link",
        "public_recovery_link",
        "Recovery closeout remains private.",
    ),
    (
        "no_delete_purge_release",
        "delete_purge_quarantine_release",
        "Closeout cannot delete, purge, or release.",
    ),
    (
        "no_physical_move",
        "physical_object_move",
        "Closeout cannot move physical media.",
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
        get_authorized_recovery_staging_intake_board()
        .get("staging_intakes", [])
    )

    environment_rows = (
        get_isolated_recovery_staging_environment_board()
        .get("staging_environments", [])
    )

    plan_rows = (
        get_recovery_action_plan_draft_board()
        .get("action_plan_drafts", [])
    )

    simulation_rows = (
        get_recovery_write_simulation_queue()
        .get("write_simulations", [])
    )

    diff_rows = (
        get_recovery_mutation_diff_preview_board()
        .get("mutation_diff_previews", [])
    )

    lock_rows = (
        get_recovery_commit_point_lock_board()
        .get("commit_point_locks", [])
    )

    receipt_rows = (
        get_tower_recovery_staging_receipt_draft_ledger()
        .get("staging_receipt_drafts", [])
    )

    environment_by_request = {
        row["request_id"]: row
        for row in environment_rows
    }

    plan_by_request = {
        row["request_id"]: row
        for row in plan_rows
    }

    simulation_by_request = {
        row["request_id"]: row
        for row in simulation_rows
    }

    diff_by_request = {
        row["request_id"]: row
        for row in diff_rows
    }

    lock_by_request = {
        row["request_id"]: row
        for row in lock_rows
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
                "environment": (
                    environment_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "plan": plan_by_request.get(
                    request_id,
                    {},
                ),
                "simulation": (
                    simulation_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "diff": diff_by_request.get(
                    request_id,
                    {},
                ),
                "lock": lock_by_request.get(
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
        validate_controlled_recovery_execution_staging_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS closeout_intakes (
                closeout_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                staging_intake_verified INTEGER NOT NULL,
                environment_verified INTEGER NOT NULL,
                action_plan_verified INTEGER NOT NULL,
                simulation_verified INTEGER NOT NULL,
                diff_preview_verified INTEGER NOT NULL,
                commit_lock_verified INTEGER NOT NULL,
                staging_receipt_verified INTEGER NOT NULL,
                eligible_for_closeout_draft INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS authority_reconfirmations (
                authority_reconfirmation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requester_service TEXT NOT NULL,
                tower_identity_reconfirmed INTEGER NOT NULL,
                tower_permission_reconfirmed INTEGER NOT NULL,
                recovery_clearance_reconfirmed INTEGER NOT NULL,
                least_privilege_reconfirmed INTEGER NOT NULL,
                vault_answer_target TEXT NOT NULL,
                teller_authority_allowed INTEGER NOT NULL,
                direct_vault_user_access_allowed INTEGER NOT NULL,
                authority_reconfirmation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approval_closeouts (
                approval_closeout_id TEXT PRIMARY KEY,
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
                closeout_requirements_packaged INTEGER NOT NULL,
                live_authorization_allowed INTEGER NOT NULL,
                approval_closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scope_freezes (
                scope_freeze_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                staging_environment_hash TEXT NOT NULL,
                action_plan_hash TEXT NOT NULL,
                simulation_hash TEXT NOT NULL,
                diff_preview_hash TEXT NOT NULL,
                commit_lock_hash TEXT NOT NULL,
                staging_receipt_hash TEXT NOT NULL,
                request_bound INTEGER NOT NULL,
                environment_bound INTEGER NOT NULL,
                action_plan_bound INTEGER NOT NULL,
                mutation_diff_bound INTEGER NOT NULL,
                scope_expansion_allowed INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                scope_freeze_activated INTEGER NOT NULL,
                scope_freeze_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commit_window_drafts (
                commit_window_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                scope_freeze_id TEXT NOT NULL,
                state TEXT NOT NULL,
                one_time_window_required INTEGER NOT NULL,
                request_bound INTEGER NOT NULL,
                scope_bound INTEGER NOT NULL,
                authority_bound INTEGER NOT NULL,
                expiry_required INTEGER NOT NULL,
                activation_requires_owner_admin INTEGER NOT NULL,
                activation_requires_step_up INTEGER NOT NULL,
                activation_requires_dual_receipt INTEGER NOT NULL,
                activation_requires_second_authority INTEGER NOT NULL,
                commit_window_activated INTEGER NOT NULL,
                execution_window_open INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                commit_window_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commit_closeout_drafts (
                closeout_draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                authority_reconfirmation_id TEXT NOT NULL,
                approval_closeout_id TEXT NOT NULL,
                scope_freeze_id TEXT NOT NULL,
                commit_window_id TEXT NOT NULL,
                state TEXT NOT NULL,
                evidence_closeout_complete INTEGER NOT NULL,
                authority_reconfirmation_complete INTEGER NOT NULL,
                approval_requirements_packaged INTEGER NOT NULL,
                scope_freeze_draft_complete INTEGER NOT NULL,
                commit_window_draft_complete INTEGER NOT NULL,
                one_time_authorization_required INTEGER NOT NULL,
                authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                closeout_draft_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS closeout_receipt_drafts (
                closeout_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                closeout_draft_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                evidence_closeout_recorded INTEGER NOT NULL,
                authority_reconfirmation_recorded INTEGER NOT NULL,
                approval_requirements_recorded INTEGER NOT NULL,
                scope_freeze_draft_recorded INTEGER NOT NULL,
                commit_window_draft_recorded INTEGER NOT NULL,
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
            "closeout_intakes",
            "authority_reconfirmations",
            "approval_closeouts",
            "scope_freezes",
            "commit_window_drafts",
            "commit_closeout_drafts",
            "closeout_receipt_drafts",
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
            environment = source["environment"]
            plan = source["plan"]
            simulation = source["simulation"]
            diff = source["diff"]
            lock = source["lock"]
            receipt = source["receipt"]

            staging_intake_verified = all(
                [
                    bool(
                        intake.get(
                            "authorization_review_eligible",
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
                            "evidence_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "safe_scope_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "authorization_still_pending",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "staging_design_allowed",
                            0,
                        )
                    ),
                    not bool(
                        intake.get(
                            "live_execution_allowed",
                            1,
                        )
                    ),
                    not bool(
                        intake.get(
                            "production_write_allowed",
                            1,
                        )
                    ),
                ]
            )

            environment_verified = all(
                [
                    bool(
                        environment.get(
                            "isolated_environment_required",
                            0,
                        )
                    ),
                    bool(
                        environment.get(
                            "hash_only_environment",
                            0,
                        )
                    ),
                    bool(
                        environment.get(
                            "ephemeral_environment_required",
                            0,
                        )
                    ),
                    not bool(
                        environment.get(
                            "production_mount_allowed",
                            1,
                        )
                    ),
                    not bool(
                        environment.get(
                            "writable_mount_allowed",
                            1,
                        )
                    ),
                    not bool(
                        environment.get(
                            "network_egress_allowed",
                            1,
                        )
                    ),
                    not bool(
                        environment.get(
                            "external_provider_connection_allowed",
                            1,
                        )
                    ),
                    not bool(
                        environment.get(
                            "raw_bytes_materialized",
                            1,
                        )
                    ),
                    not bool(
                        environment.get(
                            "raw_paths_exposed",
                            1,
                        )
                    ),
                    len(
                        environment.get(
                            "environment_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            action_plan_verified = all(
                [
                    bool(
                        plan.get(
                            "simulation_only",
                            0,
                        )
                    ),
                    bool(
                        plan.get(
                            "abort_on_any_mismatch",
                            0,
                        )
                    ),
                    bool(
                        plan.get(
                            "rollback_guard_required",
                            0,
                        )
                    ),
                    not bool(
                        plan.get(
                            "live_execution_allowed",
                            1,
                        )
                    ),
                    int(
                        plan.get(
                            "action_count",
                            0,
                        )
                    )
                    > 0,
                    len(
                        plan.get(
                            "action_plan_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            simulation_verified = all(
                [
                    int(
                        simulation.get(
                            "simulated_write_count",
                            0,
                        )
                    )
                    > 0,
                    int(
                        simulation.get(
                            "actual_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        simulation.get(
                            "production_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        simulation.get(
                            "sealed_bytes_write_count",
                            1,
                        )
                    )
                    == 0,
                    int(
                        simulation.get(
                            "package_materialization_count",
                            1,
                        )
                    )
                    == 0,
                    len(
                        simulation.get(
                            "simulation_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            diff_preview_verified = all(
                [
                    len(
                        diff.get(
                            "expected_before_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        diff.get(
                            "simulated_after_hash",
                            "",
                        )
                    )
                    == 64,
                    not bool(
                        diff.get(
                            "actual_before_hash_recorded",
                            1,
                        )
                    ),
                    not bool(
                        diff.get(
                            "actual_after_hash_recorded",
                            1,
                        )
                    ),
                    int(
                        diff.get(
                            "actual_mutation_count",
                            1,
                        )
                    )
                    == 0,
                    not bool(
                        diff.get(
                            "production_diff_generated",
                            1,
                        )
                    ),
                    not bool(
                        diff.get(
                            "raw_bytes_included",
                            1,
                        )
                    ),
                    not bool(
                        diff.get(
                            "raw_paths_included",
                            1,
                        )
                    ),
                    len(
                        diff.get(
                            "diff_preview_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            commit_lock_verified = all(
                [
                    bool(
                        lock.get(
                            "commit_point_required",
                            0,
                        )
                    ),
                    not bool(
                        lock.get(
                            "commit_point_open",
                            1,
                        )
                    ),
                    not bool(
                        lock.get(
                            "commit_command_issued",
                            1,
                        )
                    ),
                    bool(
                        lock.get(
                            "authorization_pending",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "owner_admin_approval_pending",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "step_up_pending",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "dual_receipt_pending",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "second_authority_review_pending",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "production_write_locked",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "final_index_write_locked",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "pack_overwrite_locked",
                            0,
                        )
                    ),
                    bool(
                        lock.get(
                            "sealed_bytes_write_locked",
                            0,
                        )
                    ),
                    len(
                        lock.get(
                            "lock_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            staging_receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "staging_design_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "simulation_recorded",
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

            eligible_for_closeout_draft = all(
                [
                    staging_intake_verified,
                    environment_verified,
                    action_plan_verified,
                    simulation_verified,
                    diff_preview_verified,
                    commit_lock_verified,
                    staging_receipt_verified,
                ]
            )

            closeout_intake_id = _id(
                "commit_closeout_intake",
                request_id,
            )

            authority_reconfirmation_id = _id(
                "commit_authority_reconfirmation",
                request_id,
            )

            approval_closeout_id = _id(
                "commit_approval_closeout",
                request_id,
            )

            scope_freeze_id = _id(
                "commit_scope_freeze",
                request_id,
            )

            commit_window_id = _id(
                "commit_window_draft",
                request_id,
            )

            closeout_draft_id = _id(
                "commit_authorization_closeout",
                request_id,
            )

            closeout_receipt_id = _id(
                "commit_authorization_receipt",
                request_id,
            )

            connection.execute(
                """
                INSERT INTO closeout_intakes (
                    closeout_intake_id,
                    request_id,
                    workflow_type,
                    state,
                    staging_intake_verified,
                    environment_verified,
                    action_plan_verified,
                    simulation_verified,
                    diff_preview_verified,
                    commit_lock_verified,
                    staging_receipt_verified,
                    eligible_for_closeout_draft,
                    live_authorization_granted,
                    commit_point_open,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    closeout_intake_id,
                    request_id,
                    workflow_type,
                    (
                        "staging_evidence_closed_for_"
                        "authorization_draft_only"
                    ),
                    int(staging_intake_verified),
                    int(environment_verified),
                    int(action_plan_verified),
                    int(simulation_verified),
                    int(diff_preview_verified),
                    int(commit_lock_verified),
                    int(staging_receipt_verified),
                    int(eligible_for_closeout_draft),
                    0,
                    0,
                    now,
                ),
            )

            authority_payload = {
                "request_id": request_id,
                "requester_service": "Tower",
                "tower_identity_reconfirmed": True,
                "tower_permission_reconfirmed": True,
                "recovery_clearance_reconfirmed": True,
                "least_privilege_reconfirmed": True,
                "vault_answer_target": "Tower",
                "teller_authority_allowed": False,
                "direct_vault_user_access_allowed": False,
            }

            authority_hash = _canonical_hash(
                authority_payload
            )

            connection.execute(
                """
                INSERT INTO authority_reconfirmations (
                    authority_reconfirmation_id,
                    request_id,
                    state,
                    requester_service,
                    tower_identity_reconfirmed,
                    tower_permission_reconfirmed,
                    recovery_clearance_reconfirmed,
                    least_privilege_reconfirmed,
                    vault_answer_target,
                    teller_authority_allowed,
                    direct_vault_user_access_allowed,
                    authority_reconfirmation_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?
                )
                """,
                (
                    authority_reconfirmation_id,
                    request_id,
                    (
                        "tower_commit_authority_"
                        "reconfirmed_no_execution_grant"
                    ),
                    "Tower",
                    1,
                    1,
                    1,
                    1,
                    "Tower",
                    0,
                    0,
                    authority_hash,
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
                "closeout_requirements_packaged": True,
                "live_authorization_allowed": False,
            }

            approval_hash = _canonical_hash(
                approval_payload
            )

            connection.execute(
                """
                INSERT INTO approval_closeouts (
                    approval_closeout_id,
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
                    closeout_requirements_packaged,
                    live_authorization_allowed,
                    approval_closeout_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    approval_closeout_id,
                    request_id,
                    (
                        "approval_requirements_packaged_"
                        "all_decisions_pending"
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
                    approval_hash,
                    now,
                ),
            )

            scope_payload = {
                "request_id": request_id,
                "staging_environment_hash": (
                    environment.get(
                        "environment_hash",
                        "",
                    )
                ),
                "action_plan_hash": plan.get(
                    "action_plan_hash",
                    "",
                ),
                "simulation_hash": simulation.get(
                    "simulation_hash",
                    "",
                ),
                "diff_preview_hash": diff.get(
                    "diff_preview_hash",
                    "",
                ),
                "commit_lock_hash": lock.get(
                    "lock_hash",
                    "",
                ),
                "staging_receipt_hash": receipt.get(
                    "receipt_hash",
                    "",
                ),
                "request_bound": True,
                "environment_bound": True,
                "action_plan_bound": True,
                "mutation_diff_bound": True,
                "scope_expansion_allowed": False,
                "production_target_allowed": False,
                "external_provider_allowed": False,
                "scope_freeze_activated": False,
            }

            scope_freeze_hash = _canonical_hash(
                scope_payload
            )

            connection.execute(
                """
                INSERT INTO scope_freezes (
                    scope_freeze_id,
                    request_id,
                    state,
                    staging_environment_hash,
                    action_plan_hash,
                    simulation_hash,
                    diff_preview_hash,
                    commit_lock_hash,
                    staging_receipt_hash,
                    request_bound,
                    environment_bound,
                    action_plan_bound,
                    mutation_diff_bound,
                    scope_expansion_allowed,
                    production_target_allowed,
                    external_provider_allowed,
                    scope_freeze_activated,
                    scope_freeze_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    scope_freeze_id,
                    request_id,
                    (
                        "recovery_commit_scope_freeze_"
                        "draft_exact_scope_not_activated"
                    ),
                    scope_payload[
                        "staging_environment_hash"
                    ],
                    scope_payload["action_plan_hash"],
                    scope_payload["simulation_hash"],
                    scope_payload["diff_preview_hash"],
                    scope_payload["commit_lock_hash"],
                    scope_payload["staging_receipt_hash"],
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    scope_freeze_hash,
                    now,
                ),
            )

            window_payload = {
                "request_id": request_id,
                "scope_freeze_id": scope_freeze_id,
                "one_time_window_required": True,
                "request_bound": True,
                "scope_bound": True,
                "authority_bound": True,
                "expiry_required": True,
                "activation_requires_owner_admin": True,
                "activation_requires_step_up": True,
                "activation_requires_dual_receipt": True,
                "activation_requires_second_authority": True,
                "commit_window_activated": False,
                "execution_window_open": False,
                "commit_point_open": False,
            }

            commit_window_hash = _canonical_hash(
                window_payload
            )

            connection.execute(
                """
                INSERT INTO commit_window_drafts (
                    commit_window_id,
                    request_id,
                    scope_freeze_id,
                    state,
                    one_time_window_required,
                    request_bound,
                    scope_bound,
                    authority_bound,
                    expiry_required,
                    activation_requires_owner_admin,
                    activation_requires_step_up,
                    activation_requires_dual_receipt,
                    activation_requires_second_authority,
                    commit_window_activated,
                    execution_window_open,
                    commit_point_open,
                    commit_window_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    commit_window_id,
                    request_id,
                    scope_freeze_id,
                    (
                        "one_time_commit_window_"
                        "draft_not_activated"
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
                    0,
                    commit_window_hash,
                    now,
                ),
            )

            closeout_payload = {
                "request_id": request_id,
                "authority_reconfirmation_id": (
                    authority_reconfirmation_id
                ),
                "approval_closeout_id": (
                    approval_closeout_id
                ),
                "scope_freeze_id": scope_freeze_id,
                "commit_window_id": commit_window_id,
                "evidence_closeout_complete": True,
                "authority_reconfirmation_complete": True,
                "approval_requirements_packaged": True,
                "scope_freeze_draft_complete": True,
                "commit_window_draft_complete": True,
                "one_time_authorization_required": True,
                "authorization_granted": False,
                "authorization_token_issued": False,
                "commit_command_issued": False,
                "actual_restore_allowed": False,
                "production_write_allowed": False,
            }

            closeout_draft_hash = _canonical_hash(
                closeout_payload
            )

            connection.execute(
                """
                INSERT INTO commit_closeout_drafts (
                    closeout_draft_id,
                    request_id,
                    authority_reconfirmation_id,
                    approval_closeout_id,
                    scope_freeze_id,
                    commit_window_id,
                    state,
                    evidence_closeout_complete,
                    authority_reconfirmation_complete,
                    approval_requirements_packaged,
                    scope_freeze_draft_complete,
                    commit_window_draft_complete,
                    one_time_authorization_required,
                    authorization_granted,
                    authorization_token_issued,
                    commit_command_issued,
                    actual_restore_allowed,
                    production_write_allowed,
                    closeout_draft_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    closeout_draft_id,
                    request_id,
                    authority_reconfirmation_id,
                    approval_closeout_id,
                    scope_freeze_id,
                    commit_window_id,
                    (
                        "commit_authorization_closeout_"
                        "draft_complete_not_granted"
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
                    closeout_draft_hash,
                    now,
                ),
            )

            receipt_payload = {
                "request_id": request_id,
                "closeout_draft_id": closeout_draft_id,
                "evidence_closeout_recorded": True,
                "authority_reconfirmation_recorded": True,
                "approval_requirements_recorded": True,
                "scope_freeze_draft_recorded": True,
                "commit_window_draft_recorded": True,
                "live_authorization_recorded": False,
                "authorization_token_recorded": False,
                "commit_command_recorded": False,
                "actual_restore_recorded": False,
                "production_write_recorded": False,
            }

            closeout_receipt_hash = _canonical_hash(
                receipt_payload
            )

            connection.execute(
                """
                INSERT INTO closeout_receipt_drafts (
                    closeout_receipt_id,
                    request_id,
                    closeout_draft_id,
                    state,
                    tower_controlled,
                    evidence_closeout_recorded,
                    authority_reconfirmation_recorded,
                    approval_requirements_recorded,
                    scope_freeze_draft_recorded,
                    commit_window_draft_recorded,
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
                    ?, ?, ?, ?
                )
                """,
                (
                    closeout_receipt_id,
                    request_id,
                    closeout_draft_id,
                    (
                        "tower_commit_authorization_"
                        "closeout_receipt_draft"
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
                    0,
                    0,
                    0,
                    0,
                    1,
                    0,
                    closeout_receipt_hash,
                    now,
                ),
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_staging_layer_ready": bool(
            previous.get("ready", False)
        ),
        "db_path": str(
            DB_PATH.relative_to(PROJECT_ROOT)
        ),
    }

    _INIT_CACHE = dict(result)
    return result


def get_recovery_commit_authorization_closeout_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 561,
        "title": (
            "Recovery Commit Authorization "
            "Closeout Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "closeout_drafts_only": True,
        "scope_freeze_drafts_only": True,
        "commit_window_drafts_only": True,
        "commit_point_closed": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_recovery_staging_evidence_closeout_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM closeout_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 562,
        "title": (
            "Recovery Staging Evidence "
            "Closeout Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "closeout_intakes": rows,
        "all_staging_intakes_verified": all(
            bool(row["staging_intake_verified"])
            for row in rows
        ),
        "all_environments_verified": all(
            bool(row["environment_verified"])
            for row in rows
        ),
        "all_action_plans_verified": all(
            bool(row["action_plan_verified"])
            for row in rows
        ),
        "all_simulations_verified": all(
            bool(row["simulation_verified"])
            for row in rows
        ),
        "all_diff_previews_verified": all(
            bool(row["diff_preview_verified"])
            for row in rows
        ),
        "all_commit_locks_verified": all(
            bool(row["commit_lock_verified"])
            for row in rows
        ),
        "all_staging_receipts_verified": all(
            bool(row["staging_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_closeout_draft": all(
            bool(row["eligible_for_closeout_draft"])
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


def get_tower_recovery_commit_authority_reconfirmation_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM authority_reconfirmations
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 563,
        "title": (
            "Tower Recovery Commit Authority "
            "Reconfirmation Board"
        ),
        "ready": True,
        "reconfirmation_count": len(rows),
        "authority_reconfirmations": rows,
        "all_requesters_are_tower": all(
            row["requester_service"] == "Tower"
            for row in rows
        ),
        "all_identity_reconfirmed": all(
            bool(row["tower_identity_reconfirmed"])
            for row in rows
        ),
        "all_permissions_reconfirmed": all(
            bool(row["tower_permission_reconfirmed"])
            for row in rows
        ),
        "all_clearances_reconfirmed": all(
            bool(row["recovery_clearance_reconfirmed"])
            for row in rows
        ),
        "all_least_privilege_reconfirmed": all(
            bool(row["least_privilege_reconfirmed"])
            for row in rows
        ),
        "all_vault_answers_target_tower": all(
            row["vault_answer_target"] == "Tower"
            for row in rows
        ),
        "no_teller_authority": all(
            not bool(row["teller_authority_allowed"])
            for row in rows
        ),
        "no_direct_vault_user_access": all(
            not bool(
                row["direct_vault_user_access_allowed"]
            )
            for row in rows
        ),
        "all_reconfirmation_hashes_present": all(
            len(
                row["authority_reconfirmation_hash"]
            )
            == 64
            for row in rows
        ),
    }


def get_owner_admin_step_up_dual_receipt_closeout_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM approval_closeouts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 564,
        "title": (
            "Owner/Admin Step-Up Dual Receipt "
            "Closeout Board"
        ),
        "ready": True,
        "closeout_count": len(rows),
        "approval_closeouts": rows,
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
        "all_requirements_packaged": all(
            bool(row["closeout_requirements_packaged"])
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
        "no_live_authorization_allowed": all(
            not bool(row["live_authorization_allowed"])
            for row in rows
        ),
        "all_approval_hashes_present": all(
            len(row["approval_closeout_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_commit_scope_freeze_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM scope_freezes
            ORDER BY request_id
            """,
        )

    hash_fields = [
        "staging_environment_hash",
        "action_plan_hash",
        "simulation_hash",
        "diff_preview_hash",
        "commit_lock_hash",
        "staging_receipt_hash",
        "scope_freeze_hash",
    ]

    return {
        "section": SECTION,
        "gp": 565,
        "title": "Recovery Commit Scope Freeze Board",
        "ready": True,
        "scope_freeze_count": len(rows),
        "scope_freezes": rows,
        "all_source_hashes_present": all(
            all(
                len(str(row[field])) == 64
                for field in hash_fields
            )
            for row in rows
        ),
        "all_request_bound": all(
            bool(row["request_bound"])
            for row in rows
        ),
        "all_environment_bound": all(
            bool(row["environment_bound"])
            for row in rows
        ),
        "all_action_plan_bound": all(
            bool(row["action_plan_bound"])
            for row in rows
        ),
        "all_mutation_diff_bound": all(
            bool(row["mutation_diff_bound"])
            for row in rows
        ),
        "no_scope_expansion": all(
            not bool(row["scope_expansion_allowed"])
            for row in rows
        ),
        "no_production_target": all(
            not bool(row["production_target_allowed"])
            for row in rows
        ),
        "no_external_provider": all(
            not bool(row["external_provider_allowed"])
            for row in rows
        ),
        "no_scope_freeze_activated": all(
            not bool(row["scope_freeze_activated"])
            for row in rows
        ),
    }


def get_recovery_commit_window_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM commit_window_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 566,
        "title": "Recovery Commit Window Draft Board",
        "ready": True,
        "window_count": len(rows),
        "commit_window_drafts": rows,
        "all_one_time_windows_required": all(
            bool(row["one_time_window_required"])
            for row in rows
        ),
        "all_request_bound": all(
            bool(row["request_bound"])
            for row in rows
        ),
        "all_scope_bound": all(
            bool(row["scope_bound"])
            for row in rows
        ),
        "all_authority_bound": all(
            bool(row["authority_bound"])
            for row in rows
        ),
        "all_expiry_required": all(
            bool(row["expiry_required"])
            for row in rows
        ),
        "all_activation_requirements_present": all(
            bool(
                row["activation_requires_owner_admin"]
            )
            and bool(
                row["activation_requires_step_up"]
            )
            and bool(
                row["activation_requires_dual_receipt"]
            )
            and bool(
                row[
                    "activation_requires_second_authority"
                ]
            )
            for row in rows
        ),
        "no_windows_activated": all(
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
        "all_window_hashes_present": all(
            len(row["commit_window_hash"]) == 64
            for row in rows
        ),
    }


def get_one_time_commit_authorization_closeout_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM commit_closeout_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 567,
        "title": (
            "One-Time Commit Authorization "
            "Closeout Draft Board"
        ),
        "ready": True,
        "draft_count": len(rows),
        "closeout_drafts": rows,
        "all_evidence_closeouts_complete": all(
            bool(row["evidence_closeout_complete"])
            for row in rows
        ),
        "all_authority_reconfirmations_complete": all(
            bool(
                row[
                    "authority_reconfirmation_complete"
                ]
            )
            for row in rows
        ),
        "all_approval_requirements_packaged": all(
            bool(row["approval_requirements_packaged"])
            for row in rows
        ),
        "all_scope_freeze_drafts_complete": all(
            bool(row["scope_freeze_draft_complete"])
            for row in rows
        ),
        "all_commit_window_drafts_complete": all(
            bool(row["commit_window_draft_complete"])
            for row in rows
        ),
        "all_one_time_authorization_required": all(
            bool(row["one_time_authorization_required"])
            for row in rows
        ),
        "no_authorization_granted": all(
            not bool(row["authorization_granted"])
            for row in rows
        ),
        "no_authorization_tokens_issued": all(
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
        "all_closeout_hashes_present": all(
            len(row["closeout_draft_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_recovery_commit_authorization_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM closeout_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 568,
        "title": (
            "Tower Recovery Commit Authorization "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "closeout_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_closeout_components_recorded": all(
            bool(row["evidence_closeout_recorded"])
            and bool(
                row[
                    "authority_reconfirmation_recorded"
                ]
            )
            and bool(
                row["approval_requirements_recorded"]
            )
            and bool(
                row["scope_freeze_draft_recorded"]
            )
            and bool(
                row["commit_window_draft_recorded"]
            )
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
        "no_commit_or_execution_recorded": all(
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


def get_recovery_commit_authorization_closeout_safety_blocker_board(
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
        "gp": 569,
        "title": (
            "Recovery Commit Authorization Closeout "
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


def get_recovery_commit_authorization_closeout_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_recovery_commit_authorization_closeout_shell()
    )

    intakes = (
        get_recovery_staging_evidence_closeout_intake_board()
    )

    authority = (
        get_tower_recovery_commit_authority_reconfirmation_board()
    )

    approvals = (
        get_owner_admin_step_up_dual_receipt_closeout_board()
    )

    scopes = get_recovery_commit_scope_freeze_board()

    windows = get_recovery_commit_window_draft_board()

    drafts = (
        get_one_time_commit_authorization_closeout_draft_board()
    )

    receipts = (
        get_tower_recovery_commit_authorization_receipt_draft_ledger()
    )

    blockers = (
        get_recovery_commit_authorization_closeout_safety_blocker_board()
    )

    checks = {
        "previous_staging_layer_ready": (
            initialized[
                "previous_staging_layer_ready"
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
        "closeout_drafts_only": (
            DOCTRINE[
                "authorization_closeout_drafts_only"
            ]
            is True
            and DOCTRINE[
                "scope_freeze_drafts_only"
            ]
            is True
            and DOCTRINE[
                "commit_window_drafts_only"
            ]
            is True
            and DOCTRINE["commit_point_closed"]
            is True
        ),
        "no_live_authorization_or_execution": (
            DOCTRINE[
                "live_authorization_granted"
            ]
            is False
            and DOCTRINE[
                "authorization_token_issued"
            ]
            is False
            and DOCTRINE["commit_command_issued"]
            is False
            and DOCTRINE[
                "actual_restore_execution_allowed"
            ]
            is False
            and DOCTRINE[
                "production_recovery_write_allowed"
            ]
            is False
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "all_staging_evidence_closed": (
            intakes[
                "all_staging_intakes_verified"
            ]
            is True
            and intakes[
                "all_environments_verified"
            ]
            is True
            and intakes[
                "all_action_plans_verified"
            ]
            is True
            and intakes[
                "all_simulations_verified"
            ]
            is True
            and intakes[
                "all_diff_previews_verified"
            ]
            is True
            and intakes[
                "all_commit_locks_verified"
            ]
            is True
            and intakes[
                "all_staging_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_closeout_draft"
            ]
            is True
        ),
        "intakes_no_authorization_or_commit": (
            intakes[
                "no_live_authorization_granted"
            ]
            is True
            and intakes[
                "all_commit_points_closed"
            ]
            is True
        ),

        "authority_reconfirmations_present": (
            authority["reconfirmation_count"] >= 1
        ),
        "tower_authority_reconfirmed": (
            authority["all_requesters_are_tower"]
            is True
            and authority[
                "all_identity_reconfirmed"
            ]
            is True
            and authority[
                "all_permissions_reconfirmed"
            ]
            is True
            and authority[
                "all_clearances_reconfirmed"
            ]
            is True
            and authority[
                "all_least_privilege_reconfirmed"
            ]
            is True
            and authority[
                "all_vault_answers_target_tower"
            ]
            is True
            and authority["no_teller_authority"]
            is True
            and authority[
                "no_direct_vault_user_access"
            ]
            is True
        ),

        "approval_closeouts_present": (
            approvals["closeout_count"] >= 1
        ),
        "approval_requirements_packaged": (
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
            and approvals[
                "all_requirements_packaged"
            ]
            is True
        ),
        "approval_decisions_still_pending": (
            approvals[
                "no_owner_admin_approval_granted"
            ]
            is True
            and approvals["no_step_up_satisfied"]
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
                "no_live_authorization_allowed"
            ]
            is True
        ),

        "scope_freezes_present": (
            scopes["scope_freeze_count"] >= 1
        ),
        "scope_freezes_exact_and_inactive": (
            scopes[
                "all_source_hashes_present"
            ]
            is True
            and scopes["all_request_bound"]
            is True
            and scopes["all_environment_bound"]
            is True
            and scopes["all_action_plan_bound"]
            is True
            and scopes["all_mutation_diff_bound"]
            is True
            and scopes["no_scope_expansion"]
            is True
            and scopes["no_production_target"]
            is True
            and scopes["no_external_provider"]
            is True
            and scopes[
                "no_scope_freeze_activated"
            ]
            is True
        ),

        "commit_windows_present": (
            windows["window_count"] >= 1
        ),
        "commit_windows_one_time_and_inactive": (
            windows[
                "all_one_time_windows_required"
            ]
            is True
            and windows["all_request_bound"]
            is True
            and windows["all_scope_bound"]
            is True
            and windows["all_authority_bound"]
            is True
            and windows["all_expiry_required"]
            is True
            and windows[
                "all_activation_requirements_present"
            ]
            is True
            and windows["no_windows_activated"]
            is True
            and windows[
                "no_execution_windows_open"
            ]
            is True
            and windows["no_commit_points_open"]
            is True
        ),

        "closeout_drafts_present": (
            drafts["draft_count"] >= 1
        ),
        "closeout_drafts_complete": (
            drafts[
                "all_evidence_closeouts_complete"
            ]
            is True
            and drafts[
                "all_authority_reconfirmations_complete"
            ]
            is True
            and drafts[
                "all_approval_requirements_packaged"
            ]
            is True
            and drafts[
                "all_scope_freeze_drafts_complete"
            ]
            is True
            and drafts[
                "all_commit_window_drafts_complete"
            ]
            is True
            and drafts[
                "all_one_time_authorization_required"
            ]
            is True
        ),
        "closeout_drafts_not_granted": (
            drafts["no_authorization_granted"]
            is True
            and drafts[
                "no_authorization_tokens_issued"
            ]
            is True
            and drafts[
                "no_commit_commands_issued"
            ]
            is True
            and drafts[
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
                "all_closeout_components_recorded"
            ]
            is True
            and receipts[
                "no_live_authorization_or_token_recorded"
            ]
            is True
            and receipts[
                "no_commit_or_execution_recorded"
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
                    "network_egress_allowed"
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
        "gp": 570,
        "title": (
            "Recovery Commit Authorization Closeout "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Recovery commit authorization "
                "closeout layer blocked"
            )
        ),
        "checks": checks,
        "closeout_status": (
            "commit_authorization_closeout_drafts_ready_"
            "commit_point_closed"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — CONTROLLED RECOVERY "
            "COMMIT EXECUTION DRY-RUN LAYER / GP571-GP580"
        ),
        "still_locked": [
            "no live recovery authorization",
            "no recovery authorization token",
            "no scope freeze activation",
            "no commit window activation",
            "no recovery commit point open",
            "no recovery commit command",
            "no actual restore execution",
            "no production mount",
            "no writable mount",
            "no production recovery write",
            "no final rebuilt index write",
            "no final pack overwrite",
            "no sealed pack bytes write",
            "no backup package materialization",
            "no external provider connection",
            "no Teller-to-Vault direct call",
            "no raw bytes, paths, URLs, or tokens",
            "no public links",
            "no delete, purge, or quarantine release",
            "no physical object move",
        ],
    }


def get_recovery_commit_authorization_closeout_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_recovery_commit_authorization_closeout_readiness_checkpoint()
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


def validate_recovery_commit_authorization_closeout_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_recovery_commit_authorization_closeout_readiness_checkpoint()
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
        get_recovery_commit_authorization_closeout_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "closeout_drafts_only": True,
        "scope_freeze_drafts_only": True,
        "commit_window_drafts_only": True,
        "commit_point_closed": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "commit_command_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "locks_preserved": True,
    }


def get_gp561_status():
    return _gp_status(561)


def get_gp562_status():
    return _gp_status(562)


def get_gp563_status():
    return _gp_status(563)


def get_gp564_status():
    return _gp_status(564)


def get_gp565_status():
    return _gp_status(565)


def get_gp566_status():
    return _gp_status(566)


def get_gp567_status():
    return _gp_status(567)


def get_gp568_status():
    return _gp_status(568)


def get_gp569_status():
    return _gp_status(569)


def get_gp570_status():
    return _gp_status(570)
