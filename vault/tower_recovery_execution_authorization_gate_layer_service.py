
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — TOWER RECOVERY EXECUTION "
    "AUTHORIZATION GATE LAYER / GP541-GP550"
)

LAYER_ID = (
    "vault_gp541_550_"
    "tower_recovery_execution_authorization_gate_layer"
)

READINESS_LABEL = (
    "Tower recovery execution authorization gate ready"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_tower_recovery_execution_"
    "authorization_gate_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.cold_copy_restore_drill_layer_service import (
        get_restore_drill_eligibility_board,
        get_cold_copy_manifest_verification_board,
        get_restore_reconstruction_dry_run_board,
        get_restore_integrity_comparison_board,
        get_restore_rollback_abort_guard_board,
        get_tower_restore_drill_receipt_draft_ledger,
        validate_cold_copy_restore_drill_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP541-GP550 requires the completed "
        "GP531-GP540 Cold Copy Restore Drill Layer."
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
    "authorization_gate_only": True,
    "authorization_drafts_only": True,
    "owner_admin_approval_required": True,
    "step_up_required": True,
    "dual_receipt_required": True,
    "second_authority_review_required": True,
    "verified_restore_drill_required": True,
    "live_recovery_authorization_granted": False,
    "authorization_token_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "backup_package_materialization_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "authorization_gate_layer": True,
    "authorization_intake_allowed": True,
    "tower_authority_verification_allowed": True,
    "approval_requirement_records_allowed": True,
    "evidence_prerequisite_verification_allowed": True,
    "safe_scope_allowlist_drafts_allowed": True,
    "one_time_authorization_drafts_allowed": True,
    "authorization_receipt_drafts_allowed": True,

    "live_recovery_authorization_granted": False,
    "authorization_token_issued": False,
    "recovery_capability_token_issued": False,
    "recovery_bypass_token_issued": False,
    "authorization_receipt_finalized": False,

    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "final_rebuilt_index_write_allowed": False,
    "final_pack_overwrite_allowed": False,
    "sealed_pack_bytes_write_allowed": False,
    "backup_package_materialization_allowed": False,
    "offline_package_write_allowed": False,

    "index_mutation_allowed": False,
    "pack_mutation_allowed": False,
    "metadata_mutation_allowed": False,
    "production_target_access_allowed": False,

    "external_provider_restore_allowed": False,
    "external_provider_export_allowed": False,
    "external_sync_allowed": False,
    "provider_storage_required": False,

    "raw_file_bytes_returned_by_json": False,
    "raw_file_bytes_exposed": False,
    "raw_path_exposed": False,
    "raw_file_url_exposed": False,
    "raw_download_token_exposed": False,
    "raw_recovery_token_exposed": False,
    "public_url_created": False,
    "share_link_created": False,

    "teller_direct_authorization_allowed": False,
    "teller_direct_restore_allowed": False,
    "teller_to_vault_direct_call_allowed": False,
    "vault_direct_request_from_teller_allowed": False,

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
        "gp": 541,
        "title": (
            "Tower Recovery Execution "
            "Authorization Gate Shell"
        ),
        "route": (
            "/vault/tower-recovery-execution-"
            "authorization-gate-shell.json"
        ),
    },
    {
        "gp": 542,
        "title": "Recovery Authorization Intake Board",
        "route": (
            "/vault/recovery-authorization-"
            "intake-board.json"
        ),
    },
    {
        "gp": 543,
        "title": "Tower Recovery Authority Gate",
        "route": (
            "/vault/tower-recovery-authority-gate.json"
        ),
    },
    {
        "gp": 544,
        "title": (
            "Owner/Admin Step-Up Dual Approval Gate"
        ),
        "route": (
            "/vault/owner-admin-step-up-"
            "dual-approval-gate.json"
        ),
    },
    {
        "gp": 545,
        "title": (
            "Recovery Evidence and Receipt "
            "Prerequisite Board"
        ),
        "route": (
            "/vault/recovery-evidence-receipt-"
            "prerequisite-board.json"
        ),
    },
    {
        "gp": 546,
        "title": (
            "Recovery Execution Scope Allowlist Board"
        ),
        "route": (
            "/vault/recovery-execution-"
            "scope-allowlist-board.json"
        ),
    },
    {
        "gp": 547,
        "title": (
            "One-Time Recovery Authorization Draft Board"
        ),
        "route": (
            "/vault/one-time-recovery-"
            "authorization-draft-board.json"
        ),
    },
    {
        "gp": 548,
        "title": (
            "Tower Recovery Authorization "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-recovery-authorization-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 549,
        "title": (
            "Recovery Authorization Safety Blocker Board"
        ),
        "route": (
            "/vault/recovery-authorization-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 550,
        "title": (
            "Recovery Authorization Gate "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/recovery-execution-authorization-"
            "gate-readiness-checkpoint.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_live_authorization",
        "live_recovery_authorization_grant",
        "This layer creates drafts only.",
    ),
    (
        "no_authorization_token",
        "recovery_authorization_token_issue",
        "No recovery token is issued.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "Authorization review does not execute restore.",
    ),
    (
        "no_production_write",
        "production_recovery_write",
        "Production recovery writes remain locked.",
    ),
    (
        "no_final_index_write",
        "final_rebuilt_index_write",
        "Final index writes remain locked.",
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
        "no_external_restore",
        "external_provider_restore",
        "Provider restore remains locked.",
    ),
    (
        "no_teller_authorization",
        "teller_direct_recovery_authorization",
        "Tower is the recovery authority.",
    ),
    (
        "no_teller_vault_call",
        "teller_to_vault_direct_call",
        "Teller must route through Tower.",
    ),
    (
        "no_raw_bytes",
        "raw_file_bytes_returned_by_json",
        "JSON outputs contain metadata and hashes only.",
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
        "Recovery remains private and Tower-controlled.",
    ),
    (
        "no_direct_portal",
        "direct_vault_user_portal",
        "People do not enter Vault directly.",
    ),
    (
        "no_public_dashboard",
        "public_vault_dashboard",
        "Vault remains sealed and headless.",
    ),
    (
        "no_delete_purge_release",
        "delete_purge_quarantine_release",
        "Recovery authorization cannot delete or release.",
    ),
    (
        "no_physical_move",
        "physical_object_move",
        "Recovery authorization cannot move physical media.",
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
    eligibility_rows = (
        get_restore_drill_eligibility_board()
        .get("eligibility_rows", [])
    )

    verification_rows = (
        get_cold_copy_manifest_verification_board()
        .get("verifications", [])
    )

    reconstruction_rows = (
        get_restore_reconstruction_dry_run_board()
        .get("reconstructions", [])
    )

    comparison_rows = (
        get_restore_integrity_comparison_board()
        .get("comparisons", [])
    )

    guard_rows = (
        get_restore_rollback_abort_guard_board()
        .get("guards", [])
    )

    receipt_rows = (
        get_tower_restore_drill_receipt_draft_ledger()
        .get("receipt_drafts", [])
    )

    verification_by_request = {
        row["request_id"]: row
        for row in verification_rows
    }

    reconstruction_by_request = {
        row["request_id"]: row
        for row in reconstruction_rows
    }

    comparison_by_request = {
        row["request_id"]: row
        for row in comparison_rows
    }

    guard_by_request = {
        row["request_id"]: row
        for row in guard_rows
    }

    receipt_by_request = {
        row["request_id"]: row
        for row in receipt_rows
    }

    results = []

    for eligibility in eligibility_rows:
        request_id = eligibility["request_id"]

        results.append(
            {
                "request_id": request_id,
                "workflow_type": eligibility.get(
                    "workflow_type",
                    "unknown_workflow",
                ),
                "eligibility": eligibility,
                "verification": (
                    verification_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "reconstruction": (
                    reconstruction_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "comparison": (
                    comparison_by_request.get(
                        request_id,
                        {},
                    )
                ),
                "guard": guard_by_request.get(
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

    previous = validate_cold_copy_restore_drill_layer()

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS authorization_intakes (
                intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                restore_drill_verified INTEGER NOT NULL,
                evidence_verified INTEGER NOT NULL,
                guards_verified INTEGER NOT NULL,
                receipt_verified INTEGER NOT NULL,
                eligible_for_review INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tower_authority_gates (
                gate_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requester_service TEXT NOT NULL,
                tower_identity_contract_verified INTEGER NOT NULL,
                tower_permission_contract_verified INTEGER NOT NULL,
                recovery_clearance_contract_verified INTEGER NOT NULL,
                least_privilege_contract_verified INTEGER NOT NULL,
                vault_answer_target TEXT NOT NULL,
                teller_authorization_allowed INTEGER NOT NULL,
                direct_vault_user_access_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approval_gates (
                approval_gate_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                second_authority_review_required INTEGER NOT NULL,
                owner_admin_approval_granted INTEGER NOT NULL,
                step_up_satisfied INTEGER NOT NULL,
                second_authority_review_granted INTEGER NOT NULL,
                live_authorization_allowed INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence_prerequisites (
                prerequisite_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                manifest_hash TEXT NOT NULL,
                package_hash TEXT NOT NULL,
                custody_hash TEXT NOT NULL,
                verification_hash TEXT NOT NULL,
                reconstruction_hash TEXT NOT NULL,
                comparison_hash TEXT NOT NULL,
                guard_hash TEXT NOT NULL,
                drill_receipt_hash TEXT NOT NULL,
                all_evidence_verified INTEGER NOT NULL,
                raw_bytes_included INTEGER NOT NULL,
                raw_paths_included INTEGER NOT NULL,
                raw_tokens_included INTEGER NOT NULL,
                public_links_included INTEGER NOT NULL,
                prerequisite_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scope_allowlists (
                scope_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                sandbox_reconstruction_allowed INTEGER NOT NULL,
                receipt_chain_rebuild_allowed INTEGER NOT NULL,
                metadata_capsule_rebuild_allowed INTEGER NOT NULL,
                integrity_verification_allowed INTEGER NOT NULL,
                rollback_abort_allowed INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                final_index_write_allowed INTEGER NOT NULL,
                pack_overwrite_allowed INTEGER NOT NULL,
                sealed_bytes_write_allowed INTEGER NOT NULL,
                delete_purge_allowed INTEGER NOT NULL,
                quarantine_release_allowed INTEGER NOT NULL,
                physical_move_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                scope_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS authorization_drafts (
                draft_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                prerequisite_id TEXT NOT NULL,
                approval_gate_id TEXT NOT NULL,
                state TEXT NOT NULL,
                one_time_use_required INTEGER NOT NULL,
                request_bound INTEGER NOT NULL,
                scope_bound INTEGER NOT NULL,
                expiry_required INTEGER NOT NULL,
                approvals_pending INTEGER NOT NULL,
                authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                final_index_write_allowed INTEGER NOT NULL,
                pack_overwrite_allowed INTEGER NOT NULL,
                sealed_bytes_write_allowed INTEGER NOT NULL,
                draft_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS authorization_receipts (
                receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                draft_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                approvals_recorded INTEGER NOT NULL,
                live_authorization_recorded INTEGER NOT NULL,
                token_recorded INTEGER NOT NULL,
                restore_recorded INTEGER NOT NULL,
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
            "authorization_intakes",
            "tower_authority_gates",
            "approval_gates",
            "evidence_prerequisites",
            "scope_allowlists",
            "authorization_drafts",
            "authorization_receipts",
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

            eligibility = source["eligibility"]
            verification = source["verification"]
            reconstruction = source["reconstruction"]
            comparison = source["comparison"]
            guard = source["guard"]
            receipt = source["receipt"]

            restore_drill_verified = all(
                [
                    bool(
                        eligibility.get(
                            "cold_copy_manifest_verified",
                            0,
                        )
                    ),
                    bool(
                        eligibility.get(
                            "cold_copy_package_hash_verified",
                            0,
                        )
                    ),
                    bool(
                        eligibility.get(
                            "custody_receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        eligibility.get(
                            "mutation_locks_verified",
                            0,
                        )
                    ),
                    bool(
                        eligibility.get(
                            "eligible_for_restore_drill",
                            0,
                        )
                    ),
                    not bool(
                        eligibility.get(
                            "eligible_for_actual_restore",
                            1,
                        )
                    ),
                    bool(
                        eligibility.get(
                            "tower_control_required",
                            0,
                        )
                    ),
                ]
            )

            evidence_verified = all(
                [
                    bool(
                        verification.get(
                            "manifest_hash_verified",
                            0,
                        )
                    ),
                    bool(
                        verification.get(
                            "package_hash_verified",
                            0,
                        )
                    ),
                    bool(
                        verification.get(
                            "custody_hash_verified",
                            0,
                        )
                    ),
                    bool(
                        verification.get(
                            "source_hashes_consistent",
                            0,
                        )
                    ),
                    len(
                        verification.get(
                            "verification_bundle_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        reconstruction.get(
                            "reconstruction_simulation_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        comparison.get(
                            "overall_integrity_match",
                            0,
                        )
                    ),
                    len(
                        comparison.get(
                            "integrity_comparison_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            no_reconstruction_write = all(
                [
                    not bool(
                        reconstruction.get(
                            "actual_restore_executed",
                            1,
                        )
                    ),
                    not bool(
                        reconstruction.get(
                            "production_write_executed",
                            1,
                        )
                    ),
                    not bool(
                        reconstruction.get(
                            "final_index_write_executed",
                            1,
                        )
                    ),
                    not bool(
                        reconstruction.get(
                            "pack_overwrite_executed",
                            1,
                        )
                    ),
                    not bool(
                        reconstruction.get(
                            "sealed_pack_bytes_write_executed",
                            1,
                        )
                    ),
                    not bool(
                        reconstruction.get(
                            "package_materialized",
                            1,
                        )
                    ),
                ]
            )

            guards_verified = all(
                [
                    bool(
                        guard.get(
                            "abort_on_hash_mismatch",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "abort_on_receipt_mismatch",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "abort_on_proof_mismatch",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "rollback_required_on_any_mutation",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "actual_restore_locked",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "production_write_locked",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "final_index_write_locked",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "pack_overwrite_locked",
                            0,
                        )
                    ),
                    bool(
                        guard.get(
                            "sealed_pack_bytes_write_locked",
                            0,
                        )
                    ),
                    len(
                        guard.get(
                            "guard_hash",
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
                            "owner_admin_review_required",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "step_up_required_for_future_restore",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "receipt_finalized",
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
                            "restore_drill_receipt_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            eligible_for_review = all(
                [
                    restore_drill_verified,
                    evidence_verified,
                    no_reconstruction_write,
                    guards_verified,
                    receipt_verified,
                ]
            )

            intake_id = _id(
                "recovery_authorization_intake",
                request_id,
            )

            gate_id = _id(
                "tower_recovery_authority_gate",
                request_id,
            )

            approval_gate_id = _id(
                "owner_admin_step_up_gate",
                request_id,
            )

            prerequisite_id = _id(
                "recovery_evidence_prerequisite",
                request_id,
            )

            scope_id = _id(
                "recovery_scope_allowlist",
                request_id,
            )

            draft_id = _id(
                "one_time_recovery_authorization",
                request_id,
            )

            authorization_receipt_id = _id(
                "tower_recovery_authorization_receipt",
                request_id,
            )

            connection.execute(
                """
                INSERT INTO authorization_intakes (
                    intake_id,
                    request_id,
                    workflow_type,
                    state,
                    restore_drill_verified,
                    evidence_verified,
                    guards_verified,
                    receipt_verified,
                    eligible_for_review,
                    live_authorization_granted,
                    actual_restore_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    intake_id,
                    request_id,
                    workflow_type,
                    (
                        "ready_for_tower_authorization_"
                        "review_not_granted"
                    ),
                    int(restore_drill_verified),
                    int(evidence_verified),
                    int(guards_verified),
                    int(receipt_verified),
                    int(eligible_for_review),
                    0,
                    0,
                    now,
                ),
            )

            connection.execute(
                """
                INSERT INTO tower_authority_gates (
                    gate_id,
                    request_id,
                    state,
                    requester_service,
                    tower_identity_contract_verified,
                    tower_permission_contract_verified,
                    recovery_clearance_contract_verified,
                    least_privilege_contract_verified,
                    vault_answer_target,
                    teller_authorization_allowed,
                    direct_vault_user_access_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    gate_id,
                    request_id,
                    (
                        "tower_recovery_authority_"
                        "contract_verified"
                    ),
                    "Tower",
                    1,
                    1,
                    1,
                    1,
                    "Tower",
                    0,
                    0,
                    now,
                ),
            )

            connection.execute(
                """
                INSERT INTO approval_gates (
                    approval_gate_id,
                    request_id,
                    state,
                    owner_admin_approval_required,
                    step_up_required,
                    dual_receipt_required,
                    second_authority_review_required,
                    owner_admin_approval_granted,
                    step_up_satisfied,
                    second_authority_review_granted,
                    live_authorization_allowed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_gate_id,
                    request_id,
                    (
                        "owner_admin_step_up_dual_"
                        "approval_pending"
                    ),
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    0,
                    now,
                ),
            )

            prerequisite_payload = {
                "request_id": request_id,
                "manifest_hash": verification.get(
                    "backup_manifest_hash",
                    "",
                ),
                "package_hash": verification.get(
                    "offline_package_hash",
                    "",
                ),
                "custody_hash": verification.get(
                    "chain_of_custody_receipt_hash",
                    "",
                ),
                "verification_hash": verification.get(
                    "verification_bundle_hash",
                    "",
                ),
                "reconstruction_hash": reconstruction.get(
                    "reconstruction_simulation_hash",
                    "",
                ),
                "comparison_hash": comparison.get(
                    "integrity_comparison_hash",
                    "",
                ),
                "guard_hash": guard.get(
                    "guard_hash",
                    "",
                ),
                "drill_receipt_hash": receipt.get(
                    "restore_drill_receipt_hash",
                    "",
                ),
            }

            prerequisite_hash = _canonical_hash(
                prerequisite_payload
            )

            connection.execute(
                """
                INSERT INTO evidence_prerequisites (
                    prerequisite_id,
                    request_id,
                    state,
                    manifest_hash,
                    package_hash,
                    custody_hash,
                    verification_hash,
                    reconstruction_hash,
                    comparison_hash,
                    guard_hash,
                    drill_receipt_hash,
                    all_evidence_verified,
                    raw_bytes_included,
                    raw_paths_included,
                    raw_tokens_included,
                    public_links_included,
                    prerequisite_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    prerequisite_id,
                    request_id,
                    (
                        "recovery_evidence_"
                        "prerequisites_hash_only_verified"
                    ),
                    prerequisite_payload["manifest_hash"],
                    prerequisite_payload["package_hash"],
                    prerequisite_payload["custody_hash"],
                    prerequisite_payload["verification_hash"],
                    prerequisite_payload["reconstruction_hash"],
                    prerequisite_payload["comparison_hash"],
                    prerequisite_payload["guard_hash"],
                    prerequisite_payload["drill_receipt_hash"],
                    int(
                        evidence_verified
                        and no_reconstruction_write
                    ),
                    0,
                    0,
                    0,
                    0,
                    prerequisite_hash,
                    now,
                ),
            )

            scope_payload = {
                "request_id": request_id,
                "sandbox_reconstruction_allowed": True,
                "receipt_chain_rebuild_allowed": True,
                "metadata_capsule_rebuild_allowed": True,
                "integrity_verification_allowed": True,
                "rollback_abort_allowed": True,
                "production_target_allowed": False,
                "final_index_write_allowed": False,
                "pack_overwrite_allowed": False,
                "sealed_bytes_write_allowed": False,
                "delete_purge_allowed": False,
                "quarantine_release_allowed": False,
                "physical_move_allowed": False,
                "external_provider_allowed": False,
            }

            scope_hash = _canonical_hash(
                scope_payload
            )

            connection.execute(
                """
                INSERT INTO scope_allowlists (
                    scope_id,
                    request_id,
                    state,
                    sandbox_reconstruction_allowed,
                    receipt_chain_rebuild_allowed,
                    metadata_capsule_rebuild_allowed,
                    integrity_verification_allowed,
                    rollback_abort_allowed,
                    production_target_allowed,
                    final_index_write_allowed,
                    pack_overwrite_allowed,
                    sealed_bytes_write_allowed,
                    delete_purge_allowed,
                    quarantine_release_allowed,
                    physical_move_allowed,
                    external_provider_allowed,
                    scope_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    scope_id,
                    request_id,
                    (
                        "safe_recovery_scope_"
                        "allowlist_draft_only"
                    ),
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
                    scope_hash,
                    now,
                ),
            )

            draft_payload = {
                "request_id": request_id,
                "scope_id": scope_id,
                "prerequisite_id": prerequisite_id,
                "approval_gate_id": approval_gate_id,
                "one_time_use_required": True,
                "request_bound": True,
                "scope_bound": True,
                "expiry_required": True,
                "authorization_granted": False,
                "authorization_token_issued": False,
                "actual_restore_allowed": False,
                "production_write_allowed": False,
            }

            draft_hash = _canonical_hash(
                draft_payload
            )

            connection.execute(
                """
                INSERT INTO authorization_drafts (
                    draft_id,
                    request_id,
                    scope_id,
                    prerequisite_id,
                    approval_gate_id,
                    state,
                    one_time_use_required,
                    request_bound,
                    scope_bound,
                    expiry_required,
                    approvals_pending,
                    authorization_granted,
                    authorization_token_issued,
                    actual_restore_allowed,
                    production_write_allowed,
                    final_index_write_allowed,
                    pack_overwrite_allowed,
                    sealed_bytes_write_allowed,
                    draft_hash,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    draft_id,
                    request_id,
                    scope_id,
                    prerequisite_id,
                    approval_gate_id,
                    (
                        "one_time_recovery_"
                        "authorization_draft_pending"
                    ),
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
                    draft_hash,
                    now,
                ),
            )

            receipt_payload = {
                "request_id": request_id,
                "draft_id": draft_id,
                "draft_hash": draft_hash,
                "tower_controlled": True,
                "approvals_recorded": False,
                "live_authorization_recorded": False,
                "token_recorded": False,
                "restore_recorded": False,
                "production_write_recorded": False,
            }

            authorization_receipt_hash = _canonical_hash(
                receipt_payload
            )

            connection.execute(
                """
                INSERT INTO authorization_receipts (
                    receipt_id,
                    request_id,
                    draft_id,
                    state,
                    tower_controlled,
                    approvals_recorded,
                    live_authorization_recorded,
                    token_recorded,
                    restore_recorded,
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
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    authorization_receipt_id,
                    request_id,
                    draft_id,
                    (
                        "tower_recovery_authorization_"
                        "receipt_draft_pending"
                    ),
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
                    authorization_receipt_hash,
                    now,
                ),
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_restore_drill_ready": bool(
            previous.get("ready", False)
        ),
        "db_path": str(
            DB_PATH.relative_to(PROJECT_ROOT)
        ),
    }

    _INIT_CACHE = dict(result)
    return result


def get_tower_recovery_execution_authorization_gate_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 541,
        "title": (
            "Tower Recovery Execution "
            "Authorization Gate Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "authorization_gate_only": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_recovery_authorization_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM authorization_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 542,
        "title": "Recovery Authorization Intake Board",
        "ready": True,
        "intake_count": len(rows),
        "authorization_intakes": rows,
        "all_restore_drills_verified": all(
            bool(row["restore_drill_verified"])
            for row in rows
        ),
        "all_evidence_verified": all(
            bool(row["evidence_verified"])
            for row in rows
        ),
        "all_guards_verified": all(
            bool(row["guards_verified"])
            for row in rows
        ),
        "all_receipts_verified": all(
            bool(row["receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_review": all(
            bool(row["eligible_for_review"])
            for row in rows
        ),
        "no_live_authorization_granted": all(
            not bool(row["live_authorization_granted"])
            for row in rows
        ),
        "no_actual_restore_allowed": all(
            not bool(row["actual_restore_allowed"])
            for row in rows
        ),
    }


def get_tower_recovery_authority_gate(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM tower_authority_gates
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 543,
        "title": "Tower Recovery Authority Gate",
        "ready": True,
        "gate_count": len(rows),
        "authority_gates": rows,
        "all_requesters_are_tower": all(
            row["requester_service"] == "Tower"
            for row in rows
        ),
        "all_identity_contracts_verified": all(
            bool(
                row[
                    "tower_identity_contract_verified"
                ]
            )
            for row in rows
        ),
        "all_permission_contracts_verified": all(
            bool(
                row[
                    "tower_permission_contract_verified"
                ]
            )
            for row in rows
        ),
        "all_clearance_contracts_verified": all(
            bool(
                row[
                    "recovery_clearance_contract_verified"
                ]
            )
            for row in rows
        ),
        "all_least_privilege_contracts_verified": all(
            bool(
                row[
                    "least_privilege_contract_verified"
                ]
            )
            for row in rows
        ),
        "all_vault_answers_target_tower": all(
            row["vault_answer_target"] == "Tower"
            for row in rows
        ),
        "no_teller_authorization": all(
            not bool(
                row["teller_authorization_allowed"]
            )
            for row in rows
        ),
        "no_direct_vault_user_access": all(
            not bool(
                row[
                    "direct_vault_user_access_allowed"
                ]
            )
            for row in rows
        ),
    }


def get_owner_admin_step_up_dual_approval_gate(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM approval_gates
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 544,
        "title": (
            "Owner/Admin Step-Up Dual Approval Gate"
        ),
        "ready": True,
        "gate_count": len(rows),
        "approval_gates": rows,
        "all_owner_admin_approval_required": all(
            bool(
                row["owner_admin_approval_required"]
            )
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
        "no_owner_approval_granted": all(
            not bool(
                row["owner_admin_approval_granted"]
            )
            for row in rows
        ),
        "no_step_up_satisfied": all(
            not bool(row["step_up_satisfied"])
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
            not bool(
                row["live_authorization_allowed"]
            )
            for row in rows
        ),
    }


def get_recovery_evidence_receipt_prerequisite_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM evidence_prerequisites
            ORDER BY request_id
            """,
        )

    hash_fields = [
        "manifest_hash",
        "package_hash",
        "custody_hash",
        "verification_hash",
        "reconstruction_hash",
        "comparison_hash",
        "guard_hash",
        "drill_receipt_hash",
        "prerequisite_hash",
    ]

    return {
        "section": SECTION,
        "gp": 545,
        "title": (
            "Recovery Evidence and Receipt "
            "Prerequisite Board"
        ),
        "ready": True,
        "prerequisite_count": len(rows),
        "prerequisites": rows,
        "all_hashes_present": all(
            all(
                len(str(row[field])) == 64
                for field in hash_fields
            )
            for row in rows
        ),
        "all_evidence_verified": all(
            bool(row["all_evidence_verified"])
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


def get_recovery_execution_scope_allowlist_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM scope_allowlists
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 546,
        "title": (
            "Recovery Execution Scope Allowlist Board"
        ),
        "ready": True,
        "scope_count": len(rows),
        "scope_allowlists": rows,
        "all_safe_scopes_allowed": all(
            bool(
                row[
                    "sandbox_reconstruction_allowed"
                ]
            )
            and bool(
                row[
                    "receipt_chain_rebuild_allowed"
                ]
            )
            and bool(
                row[
                    "metadata_capsule_rebuild_allowed"
                ]
            )
            and bool(
                row[
                    "integrity_verification_allowed"
                ]
            )
            and bool(
                row["rollback_abort_allowed"]
            )
            for row in rows
        ),
        "no_production_target": all(
            not bool(row["production_target_allowed"])
            for row in rows
        ),
        "no_final_index_write": all(
            not bool(row["final_index_write_allowed"])
            for row in rows
        ),
        "no_pack_overwrite": all(
            not bool(row["pack_overwrite_allowed"])
            for row in rows
        ),
        "no_sealed_bytes_write": all(
            not bool(row["sealed_bytes_write_allowed"])
            for row in rows
        ),
        "no_delete_purge": all(
            not bool(row["delete_purge_allowed"])
            for row in rows
        ),
        "no_quarantine_release": all(
            not bool(
                row["quarantine_release_allowed"]
            )
            for row in rows
        ),
        "no_physical_move": all(
            not bool(row["physical_move_allowed"])
            for row in rows
        ),
        "no_external_provider": all(
            not bool(
                row["external_provider_allowed"]
            )
            for row in rows
        ),
        "all_scope_hashes_present": all(
            len(row["scope_hash"]) == 64
            for row in rows
        ),
    }


def get_one_time_recovery_authorization_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM authorization_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 547,
        "title": (
            "One-Time Recovery Authorization Draft Board"
        ),
        "ready": True,
        "draft_count": len(rows),
        "authorization_drafts": rows,
        "all_one_time_use_required": all(
            bool(row["one_time_use_required"])
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
        "all_expiry_required": all(
            bool(row["expiry_required"])
            for row in rows
        ),
        "all_approvals_pending": all(
            bool(row["approvals_pending"])
            for row in rows
        ),
        "no_authorization_granted": all(
            not bool(row["authorization_granted"])
            for row in rows
        ),
        "no_authorization_token_issued": all(
            not bool(
                row["authorization_token_issued"]
            )
            for row in rows
        ),
        "no_restore_or_writes_allowed": all(
            not bool(row["actual_restore_allowed"])
            and not bool(
                row["production_write_allowed"]
            )
            and not bool(
                row["final_index_write_allowed"]
            )
            and not bool(
                row["pack_overwrite_allowed"]
            )
            and not bool(
                row["sealed_bytes_write_allowed"]
            )
            for row in rows
        ),
        "all_draft_hashes_present": all(
            len(row["draft_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_recovery_authorization_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM authorization_receipts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 548,
        "title": (
            "Tower Recovery Authorization "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "authorization_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "no_approvals_recorded": all(
            not bool(row["approvals_recorded"])
            for row in rows
        ),
        "no_authorization_or_token_recorded": all(
            not bool(
                row["live_authorization_recorded"]
            )
            and not bool(row["token_recorded"])
            for row in rows
        ),
        "no_restore_or_write_recorded": all(
            not bool(row["restore_recorded"])
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


def get_recovery_authorization_safety_blocker_board(
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
        "gp": 549,
        "title": (
            "Recovery Authorization Safety Blocker Board"
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


def get_recovery_execution_authorization_gate_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_tower_recovery_execution_authorization_gate_shell()
    )

    intakes = (
        get_recovery_authorization_intake_board()
    )

    authority = get_tower_recovery_authority_gate()

    approvals = (
        get_owner_admin_step_up_dual_approval_gate()
    )

    evidence = (
        get_recovery_evidence_receipt_prerequisite_board()
    )

    scopes = (
        get_recovery_execution_scope_allowlist_board()
    )

    drafts = (
        get_one_time_recovery_authorization_draft_board()
    )

    receipts = (
        get_tower_recovery_authorization_receipt_draft_ledger()
    )

    blockers = (
        get_recovery_authorization_safety_blocker_board()
    )

    checks = {
        "previous_restore_drill_ready": (
            initialized["previous_restore_drill_ready"]
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
        "tower_only_authority": (
            DOCTRINE[
                "tower_is_only_recovery_authority"
            ]
            is True
        ),
        "drafts_only": (
            DOCTRINE["authorization_gate_only"]
            is True
            and DOCTRINE["authorization_drafts_only"]
            is True
        ),
        "approval_requirements_locked": (
            DOCTRINE[
                "owner_admin_approval_required"
            ]
            is True
            and DOCTRINE["step_up_required"] is True
            and DOCTRINE["dual_receipt_required"]
            is True
            and DOCTRINE[
                "second_authority_review_required"
            ]
            is True
        ),
        "no_live_authorization": (
            DOCTRINE[
                "live_recovery_authorization_granted"
            ]
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
        "intakes_verified": (
            intakes["all_restore_drills_verified"]
            is True
            and intakes["all_evidence_verified"]
            is True
            and intakes["all_guards_verified"]
            is True
            and intakes["all_receipts_verified"]
            is True
            and intakes["all_eligible_for_review"]
            is True
        ),
        "intakes_not_authorized": (
            intakes[
                "no_live_authorization_granted"
            ]
            is True
            and intakes["no_actual_restore_allowed"]
            is True
        ),

        "authority_gates_present": (
            authority["gate_count"] >= 1
        ),
        "authority_contracts_verified": (
            authority["all_requesters_are_tower"]
            is True
            and authority[
                "all_identity_contracts_verified"
            ]
            is True
            and authority[
                "all_permission_contracts_verified"
            ]
            is True
            and authority[
                "all_clearance_contracts_verified"
            ]
            is True
            and authority[
                "all_least_privilege_contracts_verified"
            ]
            is True
            and authority[
                "all_vault_answers_target_tower"
            ]
            is True
        ),
        "no_teller_or_direct_access": (
            authority["no_teller_authorization"]
            is True
            and authority[
                "no_direct_vault_user_access"
            ]
            is True
        ),

        "approval_gates_present": (
            approvals["gate_count"] >= 1
        ),
        "approval_requirements_engaged": (
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
        "approvals_still_pending": (
            approvals[
                "no_owner_approval_granted"
            ]
            is True
            and approvals["no_step_up_satisfied"]
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

        "evidence_present": (
            evidence["prerequisite_count"] >= 1
        ),
        "evidence_hash_only_verified": (
            evidence["all_hashes_present"]
            is True
            and evidence["all_evidence_verified"]
            is True
            and evidence["no_raw_bytes"] is True
            and evidence["no_raw_paths"] is True
            and evidence["no_raw_tokens"] is True
            and evidence["no_public_links"] is True
        ),

        "scopes_present": (
            scopes["scope_count"] >= 1
        ),
        "safe_scopes_only": (
            scopes["all_safe_scopes_allowed"]
            is True
            and scopes["no_production_target"]
            is True
            and scopes["no_final_index_write"]
            is True
            and scopes["no_pack_overwrite"]
            is True
            and scopes["no_sealed_bytes_write"]
            is True
            and scopes["no_delete_purge"] is True
            and scopes["no_quarantine_release"]
            is True
            and scopes["no_physical_move"] is True
            and scopes["no_external_provider"]
            is True
        ),

        "drafts_present": (
            drafts["draft_count"] >= 1
        ),
        "one_time_drafts_pending": (
            drafts["all_one_time_use_required"]
            is True
            and drafts["all_request_bound"] is True
            and drafts["all_scope_bound"] is True
            and drafts["all_expiry_required"]
            is True
            and drafts["all_approvals_pending"]
            is True
        ),
        "drafts_not_authorized": (
            drafts["no_authorization_granted"]
            is True
            and drafts[
                "no_authorization_token_issued"
            ]
            is True
            and drafts[
                "no_restore_or_writes_allowed"
            ]
            is True
        ),

        "receipts_present": (
            receipts["receipt_count"] >= 1
        ),
        "receipt_drafts_safe": (
            receipts["all_tower_controlled"]
            is True
            and receipts["no_approvals_recorded"]
            is True
            and receipts[
                "no_authorization_or_token_recorded"
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
            and receipts["all_immutable"] is True
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
                LOCKS["final_pack_overwrite_allowed"]
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
                    "raw_file_bytes_returned_by_json"
                ]
                is False,
                LOCKS["raw_path_exposed"] is False,
                LOCKS["raw_file_url_exposed"]
                is False,
                LOCKS["raw_recovery_token_exposed"]
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
                LOCKS["hard_delete_allowed"] is False,
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
        "gp": 550,
        "title": (
            "Recovery Authorization Gate "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Tower recovery execution "
                "authorization gate blocked"
            )
        ),
        "checks": checks,
        "authorization_status": (
            "authorization_drafts_ready_"
            "live_authorization_not_granted"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — CONTROLLED RECOVERY "
            "EXECUTION STAGING LAYER / GP551-GP560"
        ),
        "still_locked": [
            "no live recovery authorization",
            "no recovery authorization token",
            "no actual restore execution",
            "no production recovery write",
            "no final rebuilt index write",
            "no final pack overwrite",
            "no sealed pack bytes write",
            "no backup package materialization",
            "no external provider restore",
            "no Teller-to-Vault direct call",
            "no raw bytes, paths, URLs, or tokens",
            "no public links",
            "no delete, purge, or quarantine release",
            "no physical object move",
        ],
    }


def get_tower_recovery_execution_authorization_gate_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_recovery_execution_authorization_gate_readiness_checkpoint()
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


def validate_tower_recovery_execution_authorization_gate_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_recovery_execution_authorization_gate_readiness_checkpoint()
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
        get_recovery_execution_authorization_gate_readiness_checkpoint()
    )

    return {
        "section": SECTION,
        "gp": gp,
        "title": pack["title"],
        "route": pack["route"],
        "ready": True,
        "checkpoint_ready": checkpoint["ready"],
        "authorization_gate_only": True,
        "live_authorization_granted": False,
        "authorization_token_issued": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
        "raw_file_bytes_returned_by_json": False,
        "public_link_created": False,
        "teller_to_vault_direct_call_allowed": False,
        "locks_preserved": True,
    }


def get_gp541_status():
    return _gp_status(541)


def get_gp542_status():
    return _gp_status(542)


def get_gp543_status():
    return _gp_status(543)


def get_gp544_status():
    return _gp_status(544)


def get_gp545_status():
    return _gp_status(545)


def get_gp546_status():
    return _gp_status(546)


def get_gp547_status():
    return _gp_status(547)


def get_gp548_status():
    return _gp_status(548)


def get_gp549_status():
    return _gp_status(549)


def get_gp550_status():
    return _gp_status(550)
