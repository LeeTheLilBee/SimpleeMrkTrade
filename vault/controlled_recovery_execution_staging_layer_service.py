
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — CONTROLLED RECOVERY "
    "EXECUTION STAGING LAYER / GP551-GP560"
)

LAYER_ID = (
    "vault_gp551_560_"
    "controlled_recovery_execution_staging_layer"
)

READINESS_LABEL = (
    "Controlled recovery execution staging layer ready"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_controlled_recovery_execution_staging_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.tower_recovery_execution_authorization_gate_layer_service import (
        get_recovery_authorization_intake_board,
        get_tower_recovery_authority_gate,
        get_owner_admin_step_up_dual_approval_gate,
        get_recovery_evidence_receipt_prerequisite_board,
        get_recovery_execution_scope_allowlist_board,
        get_one_time_recovery_authorization_draft_board,
        get_tower_recovery_authorization_receipt_draft_ledger,
        validate_tower_recovery_execution_authorization_gate_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP551-GP560 requires the completed "
        "GP541-GP550 recovery authorization gate."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "tower_is_only_recovery_authority": True,
    "staging_design_only": True,
    "staging_simulation_only": True,
    "commit_point_closed": True,
    "owner_admin_approval_still_required": True,
    "step_up_still_required": True,
    "dual_receipt_still_required": True,
    "live_authorization_granted": False,
    "authorization_token_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "controlled_recovery_staging_layer": True,
    "staging_intake_allowed": True,
    "isolated_environment_drafts_allowed": True,
    "action_plan_drafts_allowed": True,
    "write_simulation_allowed": True,
    "mutation_diff_preview_allowed": True,
    "commit_point_lock_records_allowed": True,
    "staging_receipt_drafts_allowed": True,

    "live_recovery_authorization_granted": False,
    "authorization_token_issued": False,
    "recovery_capability_token_issued": False,
    "recovery_bypass_token_issued": False,

    "commit_point_open": False,
    "commit_command_issued": False,
    "execution_window_open": False,

    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "backup_package_materialization_allowed": False,
    "offline_package_write_allowed": False,

    "production_mount_allowed": False,
    "writable_mount_allowed": False,
    "production_target_access_allowed": False,
    "network_egress_allowed": False,

    "external_provider_restore_allowed": False,
    "external_provider_connection_allowed": False,
    "external_sync_allowed": False,
    "provider_storage_required": False,

    "raw_file_bytes_returned_by_json": False,
    "raw_file_bytes_materialized": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "raw_download_token_exposed": False,
    "raw_recovery_token_exposed": False,
    "public_url_created": False,
    "share_link_created": False,

    "teller_direct_staging_allowed": False,
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
        "gp": 551,
        "title": (
            "Controlled Recovery Execution Staging Shell"
        ),
        "route": (
            "/vault/controlled-recovery-execution-"
            "staging-shell.json"
        ),
    },
    {
        "gp": 552,
        "title": (
            "Authorized Recovery Staging Intake Board"
        ),
        "route": (
            "/vault/authorized-recovery-"
            "staging-intake-board.json"
        ),
    },
    {
        "gp": 553,
        "title": (
            "Isolated Recovery Staging Environment Board"
        ),
        "route": (
            "/vault/isolated-recovery-"
            "staging-environment-board.json"
        ),
    },
    {
        "gp": 554,
        "title": "Recovery Action Plan Draft Board",
        "route": (
            "/vault/recovery-action-plan-draft-board.json"
        ),
    },
    {
        "gp": 555,
        "title": "Recovery Write Simulation Queue",
        "route": (
            "/vault/recovery-write-simulation-queue.json"
        ),
    },
    {
        "gp": 556,
        "title": (
            "Recovery Mutation Diff Preview Board"
        ),
        "route": (
            "/vault/recovery-mutation-"
            "diff-preview-board.json"
        ),
    },
    {
        "gp": 557,
        "title": "Recovery Commit Point Lock Board",
        "route": (
            "/vault/recovery-commit-point-lock-board.json"
        ),
    },
    {
        "gp": 558,
        "title": (
            "Tower Recovery Staging Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-recovery-staging-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 559,
        "title": (
            "Controlled Recovery Staging "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/controlled-recovery-staging-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 560,
        "title": (
            "Controlled Recovery Execution "
            "Staging Readiness Checkpoint"
        ),
        "route": (
            "/vault/controlled-recovery-execution-"
            "staging-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "Staging does not grant live authorization.",
    ),
    (
        "no_authorization_token",
        "recovery_authorization_token_issue",
        "Staging does not issue recovery tokens.",
    ),
    (
        "no_commit_point_open",
        "recovery_commit_point_open",
        "The commit point remains closed.",
    ),
    (
        "no_commit_command",
        "recovery_commit_command",
        "No recovery commit command is issued.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "Staging performs simulation only.",
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
        "External provider recovery remains locked.",
    ),
    (
        "no_teller_staging",
        "teller_direct_recovery_staging",
        "Tower controls recovery staging.",
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
        "Vault paths and URLs remain sealed.",
    ),
    (
        "no_raw_token",
        "raw_recovery_token_exposure",
        "No recovery token is exposed.",
    ),
    (
        "no_public_link",
        "public_recovery_link",
        "Recovery staging remains private.",
    ),
    (
        "no_delete_purge_release",
        "delete_purge_quarantine_release",
        "Staging cannot delete, purge, or release.",
    ),
    (
        "no_physical_move",
        "physical_object_move",
        "Staging cannot move physical media.",
    ),
]


ACTION_SEQUENCE = [
    {
        "order": 1,
        "action": "verify_authorization_gate_evidence",
        "mode": "read_only_hash_verification",
    },
    {
        "order": 2,
        "action": "verify_recovery_scope_allowlist",
        "mode": "read_only_policy_verification",
    },
    {
        "order": 3,
        "action": "prepare_isolated_hash_only_environment",
        "mode": "identifier_draft_only",
    },
    {
        "order": 4,
        "action": "simulate_manifest_reconstruction",
        "mode": "hash_graph_simulation",
    },
    {
        "order": 5,
        "action": "simulate_receipt_chain_rebuild",
        "mode": "receipt_hash_simulation",
    },
    {
        "order": 6,
        "action": "simulate_metadata_capsule_rebuild",
        "mode": "metadata_hash_simulation",
    },
    {
        "order": 7,
        "action": "preview_mutation_diff",
        "mode": "no_write_diff_preview",
    },
    {
        "order": 8,
        "action": "verify_abort_and_rollback_guards",
        "mode": "guard_verification",
    },
    {
        "order": 9,
        "action": "draft_tower_staging_receipt",
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
        get_recovery_authorization_intake_board()
        .get("authorization_intakes", [])
    )

    authority_rows = (
        get_tower_recovery_authority_gate()
        .get("authority_gates", [])
    )

    approval_rows = (
        get_owner_admin_step_up_dual_approval_gate()
        .get("approval_gates", [])
    )

    prerequisite_rows = (
        get_recovery_evidence_receipt_prerequisite_board()
        .get("prerequisites", [])
    )

    scope_rows = (
        get_recovery_execution_scope_allowlist_board()
        .get("scope_allowlists", [])
    )

    draft_rows = (
        get_one_time_recovery_authorization_draft_board()
        .get("authorization_drafts", [])
    )

    receipt_rows = (
        get_tower_recovery_authorization_receipt_draft_ledger()
        .get("authorization_receipt_drafts", [])
    )

    authority_by_request = {
        row["request_id"]: row
        for row in authority_rows
    }

    approval_by_request = {
        row["request_id"]: row
        for row in approval_rows
    }

    prerequisite_by_request = {
        row["request_id"]: row
        for row in prerequisite_rows
    }

    scope_by_request = {
        row["request_id"]: row
        for row in scope_rows
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
                "prerequisite": (
                    prerequisite_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "scope": scope_by_request.get(
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
        validate_tower_recovery_execution_authorization_gate_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS staging_intakes (
                staging_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                authorization_review_eligible INTEGER NOT NULL,
                tower_authority_verified INTEGER NOT NULL,
                evidence_verified INTEGER NOT NULL,
                safe_scope_verified INTEGER NOT NULL,
                authorization_still_pending INTEGER NOT NULL,
                staging_design_allowed INTEGER NOT NULL,
                live_execution_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS staging_environments (
                environment_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                isolated_environment_required INTEGER NOT NULL,
                hash_only_environment INTEGER NOT NULL,
                ephemeral_environment_required INTEGER NOT NULL,
                production_mount_allowed INTEGER NOT NULL,
                writable_mount_allowed INTEGER NOT NULL,
                network_egress_allowed INTEGER NOT NULL,
                external_provider_connection_allowed INTEGER NOT NULL,
                raw_bytes_materialized INTEGER NOT NULL,
                raw_paths_exposed INTEGER NOT NULL,
                environment_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS action_plan_drafts (
                action_plan_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                environment_id TEXT NOT NULL,
                state TEXT NOT NULL,
                action_sequence_json TEXT NOT NULL,
                action_count INTEGER NOT NULL,
                simulation_only INTEGER NOT NULL,
                abort_on_any_mismatch INTEGER NOT NULL,
                rollback_guard_required INTEGER NOT NULL,
                live_execution_allowed INTEGER NOT NULL,
                action_plan_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS write_simulations (
                simulation_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                action_plan_id TEXT NOT NULL,
                state TEXT NOT NULL,
                simulated_manifest_write INTEGER NOT NULL,
                simulated_receipt_chain_write INTEGER NOT NULL,
                simulated_metadata_capsule_write INTEGER NOT NULL,
                simulated_write_count INTEGER NOT NULL,
                actual_write_count INTEGER NOT NULL,
                production_write_count INTEGER NOT NULL,
                sealed_bytes_write_count INTEGER NOT NULL,
                package_materialization_count INTEGER NOT NULL,
                simulation_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS mutation_diff_previews (
                diff_preview_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                simulation_id TEXT NOT NULL,
                state TEXT NOT NULL,
                expected_before_hash TEXT NOT NULL,
                simulated_after_hash TEXT NOT NULL,
                actual_before_hash_recorded INTEGER NOT NULL,
                actual_after_hash_recorded INTEGER NOT NULL,
                actual_mutation_count INTEGER NOT NULL,
                production_diff_generated INTEGER NOT NULL,
                raw_bytes_included INTEGER NOT NULL,
                raw_paths_included INTEGER NOT NULL,
                diff_preview_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS commit_point_locks (
                commit_lock_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                commit_point_required INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                authorization_pending INTEGER NOT NULL,
                owner_admin_approval_pending INTEGER NOT NULL,
                step_up_pending INTEGER NOT NULL,
                dual_receipt_pending INTEGER NOT NULL,
                second_authority_review_pending INTEGER NOT NULL,
                production_write_locked INTEGER NOT NULL,
                final_index_write_locked INTEGER NOT NULL,
                pack_overwrite_locked INTEGER NOT NULL,
                sealed_bytes_write_locked INTEGER NOT NULL,
                lock_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS staging_receipt_drafts (
                staging_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                action_plan_id TEXT NOT NULL,
                simulation_id TEXT NOT NULL,
                diff_preview_id TEXT NOT NULL,
                commit_lock_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                staging_design_recorded INTEGER NOT NULL,
                simulation_recorded INTEGER NOT NULL,
                live_authorization_recorded INTEGER NOT NULL,
                authorization_token_recorded INTEGER NOT NULL,
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
            "staging_intakes",
            "staging_environments",
            "action_plan_drafts",
            "write_simulations",
            "mutation_diff_previews",
            "commit_point_locks",
            "staging_receipt_drafts",
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
            prerequisite = source["prerequisite"]
            scope = source["scope"]
            draft = source["draft"]
            receipt = source["receipt"]

            authorization_review_eligible = all(
                [
                    bool(
                        intake.get(
                            "restore_drill_verified",
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
                            "guards_verified",
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
                            "eligible_for_review",
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
                            "actual_restore_allowed",
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
                            "tower_identity_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "tower_permission_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "recovery_clearance_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "least_privilege_contract_verified",
                            0,
                        )
                    ),
                    authority.get(
                        "vault_answer_target"
                    )
                    == "Tower",
                    not bool(
                        authority.get(
                            "teller_authorization_allowed",
                            1,
                        )
                    ),
                    not bool(
                        authority.get(
                            "direct_vault_user_access_allowed",
                            1,
                        )
                    ),
                ]
            )

            approval_still_pending = all(
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
                ]
            )

            evidence_verified = all(
                [
                    bool(
                        prerequisite.get(
                            "all_evidence_verified",
                            0,
                        )
                    ),
                    len(
                        prerequisite.get(
                            "manifest_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        prerequisite.get(
                            "package_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        prerequisite.get(
                            "custody_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        prerequisite.get(
                            "verification_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        prerequisite.get(
                            "prerequisite_hash",
                            "",
                        )
                    )
                    == 64,
                    not bool(
                        prerequisite.get(
                            "raw_bytes_included",
                            1,
                        )
                    ),
                    not bool(
                        prerequisite.get(
                            "raw_paths_included",
                            1,
                        )
                    ),
                    not bool(
                        prerequisite.get(
                            "raw_tokens_included",
                            1,
                        )
                    ),
                    not bool(
                        prerequisite.get(
                            "public_links_included",
                            1,
                        )
                    ),
                ]
            )

            safe_scope_verified = all(
                [
                    bool(
                        scope.get(
                            "sandbox_reconstruction_allowed",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "receipt_chain_rebuild_allowed",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "metadata_capsule_rebuild_allowed",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "integrity_verification_allowed",
                            0,
                        )
                    ),
                    bool(
                        scope.get(
                            "rollback_abort_allowed",
                            0,
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
                            "final_index_write_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "pack_overwrite_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "sealed_bytes_write_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "delete_purge_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "quarantine_release_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "physical_move_allowed",
                            1,
                        )
                    ),
                    not bool(
                        scope.get(
                            "external_provider_allowed",
                            1,
                        )
                    ),
                    len(
                        scope.get(
                            "scope_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            draft_is_pending = all(
                [
                    bool(
                        draft.get(
                            "one_time_use_required",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "request_bound",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "scope_bound",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "expiry_required",
                            0,
                        )
                    ),
                    bool(
                        draft.get(
                            "approvals_pending",
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
                            "draft_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            receipt_is_safe_draft = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "approvals_recorded",
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
                            "token_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "restore_recorded",
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

            staging_design_allowed = all(
                [
                    authorization_review_eligible,
                    tower_authority_verified,
                    approval_still_pending,
                    evidence_verified,
                    safe_scope_verified,
                    draft_is_pending,
                    receipt_is_safe_draft,
                ]
            )

            staging_intake_id = _id(
                "recovery_staging_intake",
                request_id,
            )

            environment_id = _id(
                "isolated_recovery_environment",
                request_id,
            )

            action_plan_id = _id(
                "recovery_action_plan_draft",
                request_id,
            )

            simulation_id = _id(
                "recovery_write_simulation",
                request_id,
            )

            diff_preview_id = _id(
                "recovery_mutation_diff_preview",
                request_id,
            )

            commit_lock_id = _id(
                "recovery_commit_point_lock",
                request_id,
            )

            staging_receipt_id = _id(
                "tower_recovery_staging_receipt",
                request_id,
            )

            connection.execute(
                """
                INSERT INTO staging_intakes (
                    staging_intake_id,
                    request_id,
                    workflow_type,
                    state,
                    authorization_review_eligible,
                    tower_authority_verified,
                    evidence_verified,
                    safe_scope_verified,
                    authorization_still_pending,
                    staging_design_allowed,
                    live_execution_allowed,
                    production_write_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    staging_intake_id,
                    request_id,
                    workflow_type,
                    (
                        "eligible_for_staging_design_"
                        "not_recovery_execution"
                    ),
                    int(
                        authorization_review_eligible
                    ),
                    int(tower_authority_verified),
                    int(evidence_verified),
                    int(safe_scope_verified),
                    int(
                        approval_still_pending
                        and draft_is_pending
                    ),
                    int(staging_design_allowed),
                    0,
                    0,
                    now,
                ),
            )

            environment_payload = {
                "request_id": request_id,
                "isolated_environment_required": True,
                "hash_only_environment": True,
                "ephemeral_environment_required": True,
                "production_mount_allowed": False,
                "writable_mount_allowed": False,
                "network_egress_allowed": False,
                "external_provider_connection_allowed": False,
                "raw_bytes_materialized": False,
                "raw_paths_exposed": False,
            }

            environment_hash = _canonical_hash(
                environment_payload
            )

            connection.execute(
                """
                INSERT INTO staging_environments (
                    environment_id,
                    request_id,
                    state,
                    isolated_environment_required,
                    hash_only_environment,
                    ephemeral_environment_required,
                    production_mount_allowed,
                    writable_mount_allowed,
                    network_egress_allowed,
                    external_provider_connection_allowed,
                    raw_bytes_materialized,
                    raw_paths_exposed,
                    environment_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    environment_id,
                    request_id,
                    (
                        "isolated_hash_only_environment_"
                        "draft_not_mounted"
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
                    environment_hash,
                    now,
                ),
            )

            action_plan_payload = {
                "request_id": request_id,
                "environment_id": environment_id,
                "actions": ACTION_SEQUENCE,
                "simulation_only": True,
                "abort_on_any_mismatch": True,
                "rollback_guard_required": True,
                "live_execution_allowed": False,
            }

            action_plan_hash = _canonical_hash(
                action_plan_payload
            )

            action_sequence_json = json.dumps(
                ACTION_SEQUENCE,
                sort_keys=True,
                separators=(",", ":"),
            )

            connection.execute(
                """
                INSERT INTO action_plan_drafts (
                    action_plan_id,
                    request_id,
                    environment_id,
                    state,
                    action_sequence_json,
                    action_count,
                    simulation_only,
                    abort_on_any_mismatch,
                    rollback_guard_required,
                    live_execution_allowed,
                    action_plan_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    action_plan_id,
                    request_id,
                    environment_id,
                    (
                        "recovery_action_plan_"
                        "draft_simulation_only"
                    ),
                    action_sequence_json,
                    len(ACTION_SEQUENCE),
                    1,
                    1,
                    1,
                    0,
                    action_plan_hash,
                    now,
                ),
            )

            simulation_payload = {
                "request_id": request_id,
                "action_plan_id": action_plan_id,
                "simulated_manifest_write": True,
                "simulated_receipt_chain_write": True,
                "simulated_metadata_capsule_write": True,
                "actual_write_count": 0,
                "production_write_count": 0,
                "sealed_bytes_write_count": 0,
                "package_materialization_count": 0,
            }

            simulation_hash = _canonical_hash(
                simulation_payload
            )

            connection.execute(
                """
                INSERT INTO write_simulations (
                    simulation_id,
                    request_id,
                    action_plan_id,
                    state,
                    simulated_manifest_write,
                    simulated_receipt_chain_write,
                    simulated_metadata_capsule_write,
                    simulated_write_count,
                    actual_write_count,
                    production_write_count,
                    sealed_bytes_write_count,
                    package_materialization_count,
                    simulation_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    simulation_id,
                    request_id,
                    action_plan_id,
                    (
                        "recovery_write_simulation_"
                        "complete_no_actual_write"
                    ),
                    1,
                    1,
                    1,
                    3,
                    0,
                    0,
                    0,
                    0,
                    simulation_hash,
                    now,
                ),
            )

            expected_before_hash = (
                prerequisite.get(
                    "prerequisite_hash",
                    "",
                )
            )

            diff_payload = {
                "request_id": request_id,
                "simulation_id": simulation_id,
                "expected_before_hash": (
                    expected_before_hash
                ),
                "simulated_after_hash": (
                    simulation_hash
                ),
                "actual_mutation_count": 0,
                "production_diff_generated": False,
                "raw_bytes_included": False,
                "raw_paths_included": False,
            }

            diff_preview_hash = _canonical_hash(
                diff_payload
            )

            connection.execute(
                """
                INSERT INTO mutation_diff_previews (
                    diff_preview_id,
                    request_id,
                    simulation_id,
                    state,
                    expected_before_hash,
                    simulated_after_hash,
                    actual_before_hash_recorded,
                    actual_after_hash_recorded,
                    actual_mutation_count,
                    production_diff_generated,
                    raw_bytes_included,
                    raw_paths_included,
                    diff_preview_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    diff_preview_id,
                    request_id,
                    simulation_id,
                    (
                        "mutation_diff_preview_"
                        "hash_only_no_actual_mutation"
                    ),
                    expected_before_hash,
                    simulation_hash,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    diff_preview_hash,
                    now,
                ),
            )

            lock_payload = {
                "request_id": request_id,
                "commit_point_required": True,
                "commit_point_open": False,
                "commit_command_issued": False,
                "authorization_pending": True,
                "owner_admin_approval_pending": True,
                "step_up_pending": True,
                "dual_receipt_pending": True,
                "second_authority_review_pending": True,
                "production_write_locked": True,
                "final_index_write_locked": True,
                "pack_overwrite_locked": True,
                "sealed_bytes_write_locked": True,
            }

            lock_hash = _canonical_hash(
                lock_payload
            )

            connection.execute(
                """
                INSERT INTO commit_point_locks (
                    commit_lock_id,
                    request_id,
                    state,
                    commit_point_required,
                    commit_point_open,
                    commit_command_issued,
                    authorization_pending,
                    owner_admin_approval_pending,
                    step_up_pending,
                    dual_receipt_pending,
                    second_authority_review_pending,
                    production_write_locked,
                    final_index_write_locked,
                    pack_overwrite_locked,
                    sealed_bytes_write_locked,
                    lock_hash,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    commit_lock_id,
                    request_id,
                    (
                        "recovery_commit_point_"
                        "closed_all_approvals_pending"
                    ),
                    1,
                    0,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    lock_hash,
                    now,
                ),
            )

            receipt_payload = {
                "request_id": request_id,
                "action_plan_id": action_plan_id,
                "simulation_id": simulation_id,
                "diff_preview_id": diff_preview_id,
                "commit_lock_id": commit_lock_id,
                "staging_design_recorded": True,
                "simulation_recorded": True,
                "live_authorization_recorded": False,
                "authorization_token_recorded": False,
                "actual_restore_recorded": False,
                "production_write_recorded": False,
            }

            staging_receipt_hash = _canonical_hash(
                receipt_payload
            )

            connection.execute(
                """
                INSERT INTO staging_receipt_drafts (
                    staging_receipt_id,
                    request_id,
                    action_plan_id,
                    simulation_id,
                    diff_preview_id,
                    commit_lock_id,
                    state,
                    tower_controlled,
                    staging_design_recorded,
                    simulation_recorded,
                    live_authorization_recorded,
                    authorization_token_recorded,
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
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    staging_receipt_id,
                    request_id,
                    action_plan_id,
                    simulation_id,
                    diff_preview_id,
                    commit_lock_id,
                    (
                        "tower_recovery_staging_"
                        "receipt_draft_not_execution_receipt"
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
                    0,
                    0,
                    0,
                    1,
                    0,
                    staging_receipt_hash,
                    now,
                ),
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_authorization_gate_ready": bool(
            previous.get("ready", False)
        ),
        "db_path": str(
            DB_PATH.relative_to(PROJECT_ROOT)
        ),
    }

    _INIT_CACHE = dict(result)
    return result


def get_controlled_recovery_execution_staging_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 551,
        "title": (
            "Controlled Recovery Execution Staging Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "staging_design_only": True,
        "staging_simulation_only": True,
        "commit_point_closed": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_authorized_recovery_staging_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM staging_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 552,
        "title": (
            "Authorized Recovery Staging Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "staging_intakes": rows,
        "all_authorization_reviews_eligible": all(
            bool(
                row[
                    "authorization_review_eligible"
                ]
            )
            for row in rows
        ),
        "all_tower_authority_verified": all(
            bool(row["tower_authority_verified"])
            for row in rows
        ),
        "all_evidence_verified": all(
            bool(row["evidence_verified"])
            for row in rows
        ),
        "all_safe_scopes_verified": all(
            bool(row["safe_scope_verified"])
            for row in rows
        ),
        "all_authorizations_still_pending": all(
            bool(row["authorization_still_pending"])
            for row in rows
        ),
        "all_staging_design_allowed": all(
            bool(row["staging_design_allowed"])
            for row in rows
        ),
        "no_live_execution_allowed": all(
            not bool(row["live_execution_allowed"])
            for row in rows
        ),
        "no_production_write_allowed": all(
            not bool(row["production_write_allowed"])
            for row in rows
        ),
    }


def get_isolated_recovery_staging_environment_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM staging_environments
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 553,
        "title": (
            "Isolated Recovery Staging Environment Board"
        ),
        "ready": True,
        "environment_count": len(rows),
        "staging_environments": rows,
        "all_isolated": all(
            bool(
                row["isolated_environment_required"]
            )
            for row in rows
        ),
        "all_hash_only": all(
            bool(row["hash_only_environment"])
            for row in rows
        ),
        "all_ephemeral": all(
            bool(
                row["ephemeral_environment_required"]
            )
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
        "all_environment_hashes_present": all(
            len(row["environment_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_action_plan_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM action_plan_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 554,
        "title": "Recovery Action Plan Draft Board",
        "ready": True,
        "action_plan_count": len(rows),
        "action_plan_drafts": rows,
        "all_action_counts_complete": all(
            row["action_count"]
            == len(ACTION_SEQUENCE)
            for row in rows
        ),
        "all_simulation_only": all(
            bool(row["simulation_only"])
            for row in rows
        ),
        "all_abort_on_mismatch": all(
            bool(row["abort_on_any_mismatch"])
            for row in rows
        ),
        "all_rollback_guard_required": all(
            bool(row["rollback_guard_required"])
            for row in rows
        ),
        "no_live_execution_allowed": all(
            not bool(row["live_execution_allowed"])
            for row in rows
        ),
        "all_action_plan_hashes_present": all(
            len(row["action_plan_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_write_simulation_queue(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM write_simulations
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 555,
        "title": "Recovery Write Simulation Queue",
        "ready": True,
        "simulation_count": len(rows),
        "write_simulations": rows,
        "all_expected_simulations_present": all(
            bool(row["simulated_manifest_write"])
            and bool(
                row["simulated_receipt_chain_write"]
            )
            and bool(
                row[
                    "simulated_metadata_capsule_write"
                ]
            )
            and row["simulated_write_count"] == 3
            for row in rows
        ),
        "no_actual_writes": all(
            row["actual_write_count"] == 0
            for row in rows
        ),
        "no_production_writes": all(
            row["production_write_count"] == 0
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
        "all_simulation_hashes_present": all(
            len(row["simulation_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_mutation_diff_preview_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM mutation_diff_previews
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 556,
        "title": (
            "Recovery Mutation Diff Preview Board"
        ),
        "ready": True,
        "diff_preview_count": len(rows),
        "mutation_diff_previews": rows,
        "all_expected_hashes_present": all(
            len(row["expected_before_hash"]) == 64
            and len(row["simulated_after_hash"]) == 64
            for row in rows
        ),
        "no_actual_hashes_recorded": all(
            not bool(
                row["actual_before_hash_recorded"]
            )
            and not bool(
                row["actual_after_hash_recorded"]
            )
            for row in rows
        ),
        "no_actual_mutations": all(
            row["actual_mutation_count"] == 0
            for row in rows
        ),
        "no_production_diff_generated": all(
            not bool(
                row["production_diff_generated"]
            )
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
        "all_diff_hashes_present": all(
            len(row["diff_preview_hash"]) == 64
            for row in rows
        ),
    }


def get_recovery_commit_point_lock_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM commit_point_locks
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 557,
        "title": "Recovery Commit Point Lock Board",
        "ready": True,
        "commit_lock_count": len(rows),
        "commit_point_locks": rows,
        "all_commit_points_required": all(
            bool(row["commit_point_required"])
            for row in rows
        ),
        "all_commit_points_closed": all(
            not bool(row["commit_point_open"])
            for row in rows
        ),
        "no_commit_commands_issued": all(
            not bool(row["commit_command_issued"])
            for row in rows
        ),
        "all_authorizations_pending": all(
            bool(row["authorization_pending"])
            for row in rows
        ),
        "all_approvals_pending": all(
            bool(
                row["owner_admin_approval_pending"]
            )
            and bool(row["step_up_pending"])
            and bool(row["dual_receipt_pending"])
            and bool(
                row[
                    "second_authority_review_pending"
                ]
            )
            for row in rows
        ),
        "all_dangerous_writes_locked": all(
            bool(row["production_write_locked"])
            and bool(
                row["final_index_write_locked"]
            )
            and bool(row["pack_overwrite_locked"])
            and bool(row["sealed_bytes_write_locked"])
            for row in rows
        ),
        "all_lock_hashes_present": all(
            len(row["lock_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_recovery_staging_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM staging_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 558,
        "title": (
            "Tower Recovery Staging Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "staging_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_staging_and_simulation_recorded": all(
            bool(row["staging_design_recorded"])
            and bool(row["simulation_recorded"])
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
        "no_restore_or_write_recorded": all(
            not bool(row["actual_restore_recorded"])
            and not bool(
                row["production_write_recorded"]
            )
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


def get_controlled_recovery_staging_safety_blocker_board(
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
        "gp": 559,
        "title": (
            "Controlled Recovery Staging "
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


def get_controlled_recovery_execution_staging_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_controlled_recovery_execution_staging_shell()
    )

    intakes = (
        get_authorized_recovery_staging_intake_board()
    )

    environments = (
        get_isolated_recovery_staging_environment_board()
    )

    plans = get_recovery_action_plan_draft_board()

    simulations = (
        get_recovery_write_simulation_queue()
    )

    diffs = (
        get_recovery_mutation_diff_preview_board()
    )

    locks = get_recovery_commit_point_lock_board()

    receipts = (
        get_tower_recovery_staging_receipt_draft_ledger()
    )

    blockers = (
        get_controlled_recovery_staging_safety_blocker_board()
    )

    checks = {
        "previous_authorization_gate_ready": (
            initialized[
                "previous_authorization_gate_ready"
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
        "staging_simulation_only": (
            DOCTRINE["staging_design_only"]
            is True
            and DOCTRINE["staging_simulation_only"]
            is True
            and DOCTRINE["commit_point_closed"]
            is True
        ),
        "no_authorization_or_execution": (
            DOCTRINE["live_authorization_granted"]
            is False
            and DOCTRINE[
                "authorization_token_issued"
            ]
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
        "intakes_verified_for_staging_design": (
            intakes[
                "all_authorization_reviews_eligible"
            ]
            is True
            and intakes[
                "all_tower_authority_verified"
            ]
            is True
            and intakes["all_evidence_verified"]
            is True
            and intakes["all_safe_scopes_verified"]
            is True
            and intakes[
                "all_authorizations_still_pending"
            ]
            is True
            and intakes[
                "all_staging_design_allowed"
            ]
            is True
        ),
        "intakes_no_execution_or_write": (
            intakes["no_live_execution_allowed"]
            is True
            and intakes["no_production_write_allowed"]
            is True
        ),

        "environments_present": (
            environments["environment_count"] >= 1
        ),
        "environments_isolated_hash_only": (
            environments["all_isolated"] is True
            and environments["all_hash_only"] is True
            and environments["all_ephemeral"] is True
        ),
        "environments_no_mount_network_or_raw": (
            environments["no_production_mount"]
            is True
            and environments["no_writable_mount"]
            is True
            and environments["no_network_egress"]
            is True
            and environments[
                "no_external_provider_connection"
            ]
            is True
            and environments[
                "no_raw_bytes_materialized"
            ]
            is True
            and environments[
                "no_raw_paths_exposed"
            ]
            is True
        ),

        "plans_present": (
            plans["action_plan_count"] >= 1
        ),
        "plans_simulation_only_and_guarded": (
            plans["all_action_counts_complete"]
            is True
            and plans["all_simulation_only"]
            is True
            and plans["all_abort_on_mismatch"]
            is True
            and plans[
                "all_rollback_guard_required"
            ]
            is True
            and plans["no_live_execution_allowed"]
            is True
        ),

        "simulations_present": (
            simulations["simulation_count"] >= 1
        ),
        "simulations_no_actual_writes": (
            simulations[
                "all_expected_simulations_present"
            ]
            is True
            and simulations["no_actual_writes"]
            is True
            and simulations["no_production_writes"]
            is True
            and simulations[
                "no_sealed_bytes_writes"
            ]
            is True
            and simulations[
                "no_package_materialization"
            ]
            is True
        ),

        "diffs_present": (
            diffs["diff_preview_count"] >= 1
        ),
        "diffs_hash_only_no_mutation": (
            diffs["all_expected_hashes_present"]
            is True
            and diffs["no_actual_hashes_recorded"]
            is True
            and diffs["no_actual_mutations"]
            is True
            and diffs[
                "no_production_diff_generated"
            ]
            is True
            and diffs["no_raw_bytes"] is True
            and diffs["no_raw_paths"] is True
        ),

        "commit_locks_present": (
            locks["commit_lock_count"] >= 1
        ),
        "commit_points_closed": (
            locks["all_commit_points_required"]
            is True
            and locks["all_commit_points_closed"]
            is True
            and locks["no_commit_commands_issued"]
            is True
        ),
        "commit_locks_all_approvals_pending": (
            locks["all_authorizations_pending"]
            is True
            and locks["all_approvals_pending"]
            is True
            and locks[
                "all_dangerous_writes_locked"
            ]
            is True
        ),

        "receipts_present": (
            receipts["receipt_count"] >= 1
        ),
        "receipt_drafts_safe": (
            receipts["all_tower_controlled"]
            is True
            and receipts[
                "all_staging_and_simulation_recorded"
            ]
            is True
            and receipts[
                "no_live_authorization_or_token_recorded"
            ]
            is True
            and receipts[
                "no_restore_or_write_recorded"
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
                LOCKS["authorization_token_issued"]
                is False,
                LOCKS["commit_point_open"] is False,
                LOCKS["commit_command_issued"]
                is False,
                LOCKS["execution_window_open"]
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
                LOCKS["raw_path_exposed"] is False,
                LOCKS["raw_file_url_exposed"]
                is False,
                LOCKS[
                    "raw_recovery_token_exposed"
                ]
                is False,
                LOCKS["public_url_created"] is False,
                LOCKS["share_link_created"] is False,
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
                LOCKS["purge_allowed"] is False,
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
        "gp": 560,
        "title": (
            "Controlled Recovery Execution "
            "Staging Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Controlled recovery execution "
                "staging layer blocked"
            )
        ),
        "checks": checks,
        "staging_status": (
            "isolated_hash_only_staging_ready_"
            "commit_point_closed"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "AUTHORIZATION CLOSEOUT LAYER / GP561-GP570"
        ),
        "still_locked": [
            "no live recovery authorization",
            "no recovery authorization token",
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


def get_controlled_recovery_execution_staging_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_controlled_recovery_execution_staging_readiness_checkpoint()
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


def validate_controlled_recovery_execution_staging_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_controlled_recovery_execution_staging_readiness_checkpoint()
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
        get_controlled_recovery_execution_staging_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "staging_design_only": True,
        "staging_simulation_only": True,
        "commit_point_closed": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "locks_preserved": True,
    }


def get_gp551_status():
    return _gp_status(551)


def get_gp552_status():
    return _gp_status(552)


def get_gp553_status():
    return _gp_status(553)


def get_gp554_status():
    return _gp_status(554)


def get_gp555_status():
    return _gp_status(555)


def get_gp556_status():
    return _gp_status(556)


def get_gp557_status():
    return _gp_status(557)


def get_gp558_status():
    return _gp_status(558)


def get_gp559_status():
    return _gp_status(559)


def get_gp560_status():
    return _gp_status(560)
