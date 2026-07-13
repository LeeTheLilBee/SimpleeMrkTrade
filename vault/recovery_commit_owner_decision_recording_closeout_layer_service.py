
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER "
    "DECISION RECORDING CLOSEOUT LAYER / GP621-GP630"
)

LAYER_ID = (
    "vault_gp621_630_"
    "recovery_commit_owner_decision_recording_closeout_layer"
)

READINESS_LABEL = (
    "Owner decision recording closeout ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_RECORDING_GATE_CLOSEOUT_SEALED"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_recording_closeout_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_owner_decision_recording_gate_service import (
        ALLOWED_DECISION_VALUES,
        RECORDING_CONTRACT_FIELDS,
        get_tower_owner_review_intake_verification_board,
        get_owner_identity_step_up_recording_prerequisite_board,
        get_owner_admin_approval_dual_receipt_recording_gate,
        get_owner_decision_selection_recording_contract_board,
        get_scope_freeze_commit_window_recording_boundary_board,
        get_tower_owner_decision_append_only_record_draft_board,
        get_tower_owner_decision_recording_receipt_draft_ledger,
        validate_recovery_commit_owner_decision_recording_gate,
    )
except Exception as exc:
    raise RuntimeError(
        "GP621-GP630 requires the completed "
        "GP611-GP620 owner decision recording gate."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "recording_closeout_only": True,
    "recording_contract_may_be_frozen": True,
    "recording_gate_may_be_opened": False,
    "owner_decision_may_be_recorded": False,
    "vault_preserves_closeout_evidence": True,
    "tower_is_only_future_recording_boundary": True,
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
    "recording_gate_open": False,
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
    "recording_closeout_layer": True,
    "closeout_intake_allowed": True,
    "identity_requirement_closeout_allowed": True,
    "approval_requirement_closeout_allowed": True,
    "recording_contract_freeze_allowed": True,
    "scope_window_boundary_closeout_allowed": True,
    "closeout_record_drafts_allowed": True,
    "closeout_receipt_drafts_allowed": True,

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
        "gp": 621,
        "title": (
            "Owner Decision Recording Closeout Shell"
        ),
        "route": (
            "/vault/owner-decision-recording-"
            "closeout-shell.json"
        ),
    },
    {
        "gp": 622,
        "title": (
            "Recording Gate Evidence Closeout Intake Board"
        ),
        "route": (
            "/vault/recording-gate-evidence-"
            "closeout-intake-board.json"
        ),
    },
    {
        "gp": 623,
        "title": (
            "Identity and Step-Up Prerequisite "
            "Closeout Board"
        ),
        "route": (
            "/vault/identity-step-up-prerequisite-"
            "closeout-board.json"
        ),
    },
    {
        "gp": 624,
        "title": (
            "Approval and Dual-Receipt Gate "
            "Closeout Board"
        ),
        "route": (
            "/vault/approval-dual-receipt-gate-"
            "closeout-board.json"
        ),
    },
    {
        "gp": 625,
        "title": (
            "Owner Decision Recording Contract "
            "Freeze Board"
        ),
        "route": (
            "/vault/owner-decision-recording-"
            "contract-freeze-board.json"
        ),
    },
    {
        "gp": 626,
        "title": (
            "Scope Freeze and Commit Window "
            "Boundary Closeout Board"
        ),
        "route": (
            "/vault/scope-freeze-commit-window-"
            "boundary-closeout-board.json"
        ),
    },
    {
        "gp": 627,
        "title": (
            "Tower Owner Decision Recording "
            "Closeout Record Draft Board"
        ),
        "route": (
            "/vault/tower-owner-decision-recording-"
            "closeout-record-draft-board.json"
        ),
    },
    {
        "gp": 628,
        "title": (
            "Tower Recording Closeout "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-recording-closeout-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 629,
        "title": (
            "Owner Decision Recording Closeout "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/owner-decision-recording-closeout-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 630,
        "title": (
            "Owner Decision Recording Closeout "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/owner-decision-recording-"
            "closeout-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_recording_gate_open",
        "recording_gate_open",
        "Closeout cannot open the recording gate.",
    ),
    (
        "no_recording_execution",
        "recording_execution",
        "Closeout cannot execute owner-decision recording.",
    ),
    (
        "no_owner_review_session_start",
        "owner_review_session_start",
        "Tower must start any future review session.",
    ),
    (
        "no_owner_authentication",
        "owner_authentication",
        "Tower must authenticate the owner.",
    ),
    (
        "no_step_up_satisfaction",
        "step_up_satisfaction",
        "Tower must satisfy step-up.",
    ),
    (
        "no_owner_admin_approval",
        "owner_admin_approval",
        "Tower must capture owner/admin approval.",
    ),
    (
        "no_dual_receipt_satisfaction",
        "dual_receipt_satisfaction",
        "Tower must validate both receipts.",
    ),
    (
        "no_second_authority_grant",
        "second_authority_grant",
        "Tower must validate second authority.",
    ),
    (
        "no_owner_selection_invention",
        "owner_selection_invention",
        "Vault cannot invent the owner selection.",
    ),
    (
        "no_owner_decision_recording",
        "owner_decision_recording",
        "No owner decision is recorded by closeout.",
    ),
    (
        "no_go_decision",
        "go_decision_grant",
        "GO remains unavailable.",
    ),
    (
        "no_scope_activation",
        "scope_freeze_activation",
        "Closeout cannot activate scope freeze.",
    ),
    (
        "no_window_activation",
        "commit_window_activation",
        "Closeout cannot activate a commit window.",
    ),
    (
        "no_execution_window",
        "execution_window_open",
        "Closeout cannot open execution.",
    ),
    (
        "no_commit_point",
        "commit_point_open",
        "Closeout cannot open the commit point.",
    ),
    (
        "no_live_authorization",
        "live_authorization_grant",
        "Closeout cannot grant authorization.",
    ),
    (
        "no_token_issue",
        "authorization_token_issue",
        "Closeout cannot issue a token.",
    ),
    (
        "no_commit_command",
        "real_commit_command",
        "Closeout cannot issue a commit command.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "Closeout cannot execute restore.",
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
        "teller_direct_recording",
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
        "Closeout exposes references and hashes only.",
    ),
    (
        "no_destructive_action",
        "delete_purge_release_or_move",
        "Closeout cannot destroy or move evidence.",
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
        get_tower_owner_review_intake_verification_board()
        .get("recording_intakes", [])
    )

    identity_rows = (
        get_owner_identity_step_up_recording_prerequisite_board()
        .get("identity_prerequisites", [])
    )

    approval_rows = (
        get_owner_admin_approval_dual_receipt_recording_gate()
        .get("approval_recording_gates", [])
    )

    contract_rows = (
        get_owner_decision_selection_recording_contract_board()
        .get("recording_contracts", [])
    )

    boundary_rows = (
        get_scope_freeze_commit_window_recording_boundary_board()
        .get("scope_window_boundaries", [])
    )

    record_rows = (
        get_tower_owner_decision_append_only_record_draft_board()
        .get("decision_record_drafts", [])
    )

    receipt_rows = (
        get_tower_owner_decision_recording_receipt_draft_ledger()
        .get("recording_receipt_drafts", [])
    )

    identities = _by_request(identity_rows)
    approvals = _by_request(approval_rows)
    contracts = _by_request(contract_rows)
    boundaries = _by_request(boundary_rows)
    records = _by_request(record_rows)
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
                "identity": identities.get(
                    request_id,
                    {},
                ),
                "approval": approvals.get(
                    request_id,
                    {},
                ),
                "contract": contracts.get(
                    request_id,
                    {},
                ),
                "boundary": boundaries.get(
                    request_id,
                    {},
                ),
                "record": records.get(
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
        validate_recovery_commit_owner_decision_recording_gate()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS closeout_intakes (
                closeout_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                recording_intake_verified INTEGER NOT NULL,
                identity_prerequisite_verified INTEGER NOT NULL,
                approval_gate_verified INTEGER NOT NULL,
                recording_contract_verified INTEGER NOT NULL,
                scope_window_boundary_verified INTEGER NOT NULL,
                record_draft_verified INTEGER NOT NULL,
                receipt_draft_verified INTEGER NOT NULL,
                eligible_for_recording_closeout INTEGER NOT NULL,
                recording_gate_open INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS identity_closeouts (
                identity_closeout_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requirements_sealed INTEGER NOT NULL,
                tower_session_required INTEGER NOT NULL,
                owner_presence_required INTEGER NOT NULL,
                identity_verification_required INTEGER NOT NULL,
                step_up_required INTEGER NOT NULL,
                all_reference_requirements_present INTEGER NOT NULL,
                session_started INTEGER NOT NULL,
                owner_authenticated INTEGER NOT NULL,
                step_up_satisfied INTEGER NOT NULL,
                prerequisite_complete INTEGER NOT NULL,
                source_prerequisite_hash TEXT NOT NULL,
                closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approval_closeouts (
                approval_closeout_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requirements_sealed INTEGER NOT NULL,
                owner_admin_approval_required INTEGER NOT NULL,
                dual_receipt_required INTEGER NOT NULL,
                second_authority_review_required INTEGER NOT NULL,
                all_receipt_references_required INTEGER NOT NULL,
                owner_admin_approval_granted INTEGER NOT NULL,
                dual_receipt_satisfied INTEGER NOT NULL,
                second_authority_review_granted INTEGER NOT NULL,
                approval_gate_complete INTEGER NOT NULL,
                source_approval_gate_hash TEXT NOT NULL,
                closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS contract_freezes (
                contract_freeze_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                contract_frozen INTEGER NOT NULL,
                allowed_decisions_json TEXT NOT NULL,
                required_fields_json TEXT NOT NULL,
                allowed_decision_count INTEGER NOT NULL,
                required_field_count INTEGER NOT NULL,
                owner_selection_present INTEGER NOT NULL,
                append_only_required INTEGER NOT NULL,
                mutation_allowed INTEGER NOT NULL,
                raw_material_allowed INTEGER NOT NULL,
                source_contract_hash TEXT NOT NULL,
                contract_freeze_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS boundary_closeouts (
                boundary_closeout_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                boundary_sealed INTEGER NOT NULL,
                exact_scope_bound INTEGER NOT NULL,
                one_time_commit_window_required INTEGER NOT NULL,
                scope_window_hashes_required INTEGER NOT NULL,
                scope_freeze_activated INTEGER NOT NULL,
                commit_window_activated INTEGER NOT NULL,
                execution_window_open INTEGER NOT NULL,
                commit_point_open INTEGER NOT NULL,
                recording_may_activate_scope INTEGER NOT NULL,
                recording_may_activate_window INTEGER NOT NULL,
                production_target_allowed INTEGER NOT NULL,
                external_provider_allowed INTEGER NOT NULL,
                source_boundary_hash TEXT NOT NULL,
                closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS closeout_record_drafts (
                closeout_record_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                identity_closeout_id TEXT NOT NULL,
                approval_closeout_id TEXT NOT NULL,
                contract_freeze_id TEXT NOT NULL,
                boundary_closeout_id TEXT NOT NULL,
                source_record_draft_hash TEXT NOT NULL,
                source_receipt_draft_hash TEXT NOT NULL,
                closeout_package_complete INTEGER NOT NULL,
                future_tower_handoff_eligible INTEGER NOT NULL,
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
                closeout_record_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS closeout_receipt_drafts (
                closeout_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                closeout_record_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                recording_gate_evidence_recorded INTEGER NOT NULL,
                identity_closeout_recorded INTEGER NOT NULL,
                approval_closeout_recorded INTEGER NOT NULL,
                contract_freeze_recorded INTEGER NOT NULL,
                boundary_closeout_recorded INTEGER NOT NULL,
                closeout_package_recorded INTEGER NOT NULL,
                recording_gate_closed_recorded INTEGER NOT NULL,
                owner_selection_recorded INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
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
            "closeout_intakes",
            "identity_closeouts",
            "approval_closeouts",
            "contract_freezes",
            "boundary_closeouts",
            "closeout_record_drafts",
            "closeout_receipt_drafts",
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
            identity = source["identity"]
            approval = source["approval"]
            contract = source["contract"]
            boundary = source["boundary"]
            record = source["record"]
            receipt = source["receipt"]

            recording_intake_verified = all(
                [
                    bool(
                        intake.get(
                            "review_packet_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "session_requirements_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "control_requirements_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "activation_boundary_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "decision_options_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "review_draft_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "review_receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_recording_gate_review",
                            0,
                        )
                    ),
                    not bool(
                        intake.get(
                            "recording_gate_open",
                            1,
                        )
                    ),
                    not bool(
                        intake.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                ]
            )

            identity_verified = all(
                [
                    bool(
                        identity.get(
                            "tower_session_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "owner_presence_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "owner_identity_verification_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "step_up_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "tower_actor_reference_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "owner_principal_reference_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "identity_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        identity.get(
                            "step_up_receipt_reference_required",
                            0,
                        )
                    ),
                    not bool(
                        identity.get(
                            "session_started",
                            1,
                        )
                    ),
                    not bool(
                        identity.get(
                            "owner_authenticated",
                            1,
                        )
                    ),
                    not bool(
                        identity.get(
                            "step_up_satisfied",
                            1,
                        )
                    ),
                    not bool(
                        identity.get(
                            "prerequisite_complete",
                            1,
                        )
                    ),
                    len(
                        identity.get(
                            "prerequisite_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            approval_verified = all(
                [
                    bool(
                        approval.get(
                            "owner_admin_approval_required",
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
                            "approval_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "primary_dual_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "secondary_dual_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "second_authority_receipt_reference_required",
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
                    len(
                        approval.get(
                            "approval_gate_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            contract_verified = all(
                [
                    int(
                        contract.get(
                            "allowed_decision_count",
                            0,
                        )
                    )
                    == len(ALLOWED_DECISION_VALUES),
                    not bool(
                        contract.get(
                            "selected_decision_present",
                            1,
                        )
                    ),
                    bool(
                        contract.get(
                            "decision_reason_required",
                            0,
                        )
                    ),
                    bool(
                        contract.get(
                            "idempotency_key_required",
                            0,
                        )
                    ),
                    bool(
                        contract.get(
                            "source_review_hash_required",
                            0,
                        )
                    ),
                    bool(
                        contract.get(
                            "source_receipt_hash_required",
                            0,
                        )
                    ),
                    bool(
                        contract.get(
                            "exact_scope_hash_required",
                            0,
                        )
                    ),
                    bool(
                        contract.get(
                            "commit_window_hash_required",
                            0,
                        )
                    ),
                    bool(
                        contract.get(
                            "append_only_required",
                            0,
                        )
                    ),
                    not bool(
                        contract.get(
                            "mutation_allowed",
                            1,
                        )
                    ),
                    not bool(
                        contract.get(
                            "raw_bytes_allowed",
                            1,
                        )
                    ),
                    not bool(
                        contract.get(
                            "raw_paths_allowed",
                            1,
                        )
                    ),
                    not bool(
                        contract.get(
                            "raw_tokens_allowed",
                            1,
                        )
                    ),
                    len(
                        contract.get(
                            "contract_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            boundary_verified = all(
                [
                    bool(
                        boundary.get(
                            "exact_scope_bound",
                            0,
                        )
                    ),
                    bool(
                        boundary.get(
                            "one_time_commit_window_required",
                            0,
                        )
                    ),
                    bool(
                        boundary.get(
                            "exact_scope_hash_required",
                            0,
                        )
                    ),
                    bool(
                        boundary.get(
                            "commit_window_hash_required",
                            0,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "scope_freeze_activated",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "commit_window_activated",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "execution_window_open",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "commit_point_open",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "recording_may_activate_scope",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "recording_may_activate_window",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "production_target_allowed",
                            1,
                        )
                    ),
                    not bool(
                        boundary.get(
                            "external_provider_allowed",
                            1,
                        )
                    ),
                    len(
                        boundary.get(
                            "boundary_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            record_verified = all(
                [
                    len(
                        record.get(
                            "source_review_draft_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        record.get(
                            "source_review_receipt_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        record.get(
                            "recording_gate_ready_for_future_tower_input",
                            0,
                        )
                    ),
                    not bool(
                        record.get(
                            "recording_gate_open",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "owner_selection_present",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "go_decision_granted",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "live_authorization_granted",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "authorization_token_issued",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "commit_command_issued",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "actual_restore_allowed",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "production_write_allowed",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "finalized",
                            1,
                        )
                    ),
                    bool(
                        record.get(
                            "append_only",
                            0,
                        )
                    ),
                    not bool(
                        record.get(
                            "mutable",
                            1,
                        )
                    ),
                    len(
                        record.get(
                            "record_draft_hash",
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
                            "review_packet_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "identity_requirements_recorded",
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
                            "recording_contract_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "scope_window_boundary_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "recording_gate_closed_recorded",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "owner_selection_recorded",
                            1,
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

            eligible_for_closeout = all(
                [
                    recording_intake_verified,
                    identity_verified,
                    approval_verified,
                    contract_verified,
                    boundary_verified,
                    record_verified,
                    receipt_verified,
                ]
            )

            closeout_intake_id = _id(
                "recording_closeout_intake",
                request_id,
            )

            identity_closeout_id = _id(
                "identity_requirement_closeout",
                request_id,
            )

            approval_closeout_id = _id(
                "approval_requirement_closeout",
                request_id,
            )

            contract_freeze_id = _id(
                "recording_contract_freeze",
                request_id,
            )

            boundary_closeout_id = _id(
                "scope_window_boundary_closeout",
                request_id,
            )

            closeout_record_id = _id(
                "tower_recording_closeout_record",
                request_id,
            )

            closeout_receipt_id = _id(
                "tower_recording_closeout_receipt",
                request_id,
            )

            _insert_row(
                connection,
                "closeout_intakes",
                {
                    "closeout_intake_id": closeout_intake_id,
                    "request_id": request_id,
                    "workflow_type": workflow_type,
                    "state": (
                        "recording_gate_evidence_verified_"
                        "eligible_for_closeout"
                    ),
                    "recording_intake_verified": int(
                        recording_intake_verified
                    ),
                    "identity_prerequisite_verified": int(
                        identity_verified
                    ),
                    "approval_gate_verified": int(
                        approval_verified
                    ),
                    "recording_contract_verified": int(
                        contract_verified
                    ),
                    "scope_window_boundary_verified": int(
                        boundary_verified
                    ),
                    "record_draft_verified": int(
                        record_verified
                    ),
                    "receipt_draft_verified": int(
                        receipt_verified
                    ),
                    "eligible_for_recording_closeout": int(
                        eligible_for_closeout
                    ),
                    "recording_gate_open": 0,
                    "owner_decision_recorded": 0,
                    "created_at": now,
                },
            )

            identity_payload = {
                "request_id": request_id,
                "requirements_sealed": True,
                "tower_session_required": True,
                "owner_presence_required": True,
                "identity_verification_required": True,
                "step_up_required": True,
                "all_reference_requirements_present": True,
                "session_started": False,
                "owner_authenticated": False,
                "step_up_satisfied": False,
                "prerequisite_complete": False,
                "source_prerequisite_hash": identity.get(
                    "prerequisite_hash",
                    "",
                ),
            }

            identity_closeout_hash = _canonical_hash(
                identity_payload
            )

            _insert_row(
                connection,
                "identity_closeouts",
                {
                    "identity_closeout_id": (
                        identity_closeout_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "identity_and_step_up_requirements_"
                        "sealed_not_satisfied"
                    ),
                    "requirements_sealed": 1,
                    "tower_session_required": 1,
                    "owner_presence_required": 1,
                    "identity_verification_required": 1,
                    "step_up_required": 1,
                    "all_reference_requirements_present": 1,
                    "session_started": 0,
                    "owner_authenticated": 0,
                    "step_up_satisfied": 0,
                    "prerequisite_complete": 0,
                    "source_prerequisite_hash": identity.get(
                        "prerequisite_hash",
                        "",
                    ),
                    "closeout_hash": (
                        identity_closeout_hash
                    ),
                    "created_at": now,
                },
            )

            approval_payload = {
                "request_id": request_id,
                "requirements_sealed": True,
                "owner_admin_approval_required": True,
                "dual_receipt_required": True,
                "second_authority_review_required": True,
                "all_receipt_references_required": True,
                "owner_admin_approval_granted": False,
                "dual_receipt_satisfied": False,
                "second_authority_review_granted": False,
                "approval_gate_complete": False,
                "source_approval_gate_hash": approval.get(
                    "approval_gate_hash",
                    "",
                ),
            }

            approval_closeout_hash = _canonical_hash(
                approval_payload
            )

            _insert_row(
                connection,
                "approval_closeouts",
                {
                    "approval_closeout_id": (
                        approval_closeout_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "approval_and_receipt_requirements_"
                        "sealed_not_satisfied"
                    ),
                    "requirements_sealed": 1,
                    "owner_admin_approval_required": 1,
                    "dual_receipt_required": 1,
                    "second_authority_review_required": 1,
                    "all_receipt_references_required": 1,
                    "owner_admin_approval_granted": 0,
                    "dual_receipt_satisfied": 0,
                    "second_authority_review_granted": 0,
                    "approval_gate_complete": 0,
                    "source_approval_gate_hash": approval.get(
                        "approval_gate_hash",
                        "",
                    ),
                    "closeout_hash": (
                        approval_closeout_hash
                    ),
                    "created_at": now,
                },
            )

            frozen_decisions = json.dumps(
                ALLOWED_DECISION_VALUES,
                sort_keys=True,
                separators=(",", ":"),
            )

            frozen_fields = json.dumps(
                RECORDING_CONTRACT_FIELDS,
                sort_keys=True,
                separators=(",", ":"),
            )

            contract_payload = {
                "request_id": request_id,
                "contract_frozen": True,
                "allowed_decisions": ALLOWED_DECISION_VALUES,
                "required_fields": RECORDING_CONTRACT_FIELDS,
                "owner_selection_present": False,
                "append_only_required": True,
                "mutation_allowed": False,
                "raw_material_allowed": False,
                "source_contract_hash": contract.get(
                    "contract_hash",
                    "",
                ),
            }

            contract_freeze_hash = _canonical_hash(
                contract_payload
            )

            _insert_row(
                connection,
                "contract_freezes",
                {
                    "contract_freeze_id": (
                        contract_freeze_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "recording_contract_frozen_"
                        "owner_selection_absent"
                    ),
                    "contract_frozen": 1,
                    "allowed_decisions_json": (
                        frozen_decisions
                    ),
                    "required_fields_json": frozen_fields,
                    "allowed_decision_count": len(
                        ALLOWED_DECISION_VALUES
                    ),
                    "required_field_count": len(
                        RECORDING_CONTRACT_FIELDS
                    ),
                    "owner_selection_present": 0,
                    "append_only_required": 1,
                    "mutation_allowed": 0,
                    "raw_material_allowed": 0,
                    "source_contract_hash": contract.get(
                        "contract_hash",
                        "",
                    ),
                    "contract_freeze_hash": (
                        contract_freeze_hash
                    ),
                    "created_at": now,
                },
            )

            boundary_payload = {
                "request_id": request_id,
                "boundary_sealed": True,
                "exact_scope_bound": True,
                "one_time_commit_window_required": True,
                "scope_window_hashes_required": True,
                "scope_freeze_activated": False,
                "commit_window_activated": False,
                "execution_window_open": False,
                "commit_point_open": False,
                "recording_may_activate_scope": False,
                "recording_may_activate_window": False,
                "production_target_allowed": False,
                "external_provider_allowed": False,
                "source_boundary_hash": boundary.get(
                    "boundary_hash",
                    "",
                ),
            }

            boundary_closeout_hash = _canonical_hash(
                boundary_payload
            )

            _insert_row(
                connection,
                "boundary_closeouts",
                {
                    "boundary_closeout_id": (
                        boundary_closeout_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "scope_window_boundary_sealed_"
                        "nothing_activated"
                    ),
                    "boundary_sealed": 1,
                    "exact_scope_bound": 1,
                    "one_time_commit_window_required": 1,
                    "scope_window_hashes_required": 1,
                    "scope_freeze_activated": 0,
                    "commit_window_activated": 0,
                    "execution_window_open": 0,
                    "commit_point_open": 0,
                    "recording_may_activate_scope": 0,
                    "recording_may_activate_window": 0,
                    "production_target_allowed": 0,
                    "external_provider_allowed": 0,
                    "source_boundary_hash": boundary.get(
                        "boundary_hash",
                        "",
                    ),
                    "closeout_hash": (
                        boundary_closeout_hash
                    ),
                    "created_at": now,
                },
            )

            closeout_record_payload = {
                "request_id": request_id,
                "identity_closeout_id": (
                    identity_closeout_id
                ),
                "approval_closeout_id": (
                    approval_closeout_id
                ),
                "contract_freeze_id": contract_freeze_id,
                "boundary_closeout_id": (
                    boundary_closeout_id
                ),
                "source_record_draft_hash": record.get(
                    "record_draft_hash",
                    "",
                ),
                "source_receipt_draft_hash": receipt.get(
                    "receipt_hash",
                    "",
                ),
                "closeout_package_complete": True,
                "future_tower_handoff_eligible": True,
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

            closeout_record_hash = _canonical_hash(
                closeout_record_payload
            )

            _insert_row(
                connection,
                "closeout_record_drafts",
                {
                    "closeout_record_id": (
                        closeout_record_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_recording_closeout_"
                        "draft_complete_gate_closed"
                    ),
                    "identity_closeout_id": (
                        identity_closeout_id
                    ),
                    "approval_closeout_id": (
                        approval_closeout_id
                    ),
                    "contract_freeze_id": (
                        contract_freeze_id
                    ),
                    "boundary_closeout_id": (
                        boundary_closeout_id
                    ),
                    "source_record_draft_hash": record.get(
                        "record_draft_hash",
                        "",
                    ),
                    "source_receipt_draft_hash": receipt.get(
                        "receipt_hash",
                        "",
                    ),
                    "closeout_package_complete": 1,
                    "future_tower_handoff_eligible": 1,
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
                    "closeout_record_hash": (
                        closeout_record_hash
                    ),
                    "created_at": now,
                },
            )

            closeout_receipt_payload = {
                "request_id": request_id,
                "closeout_record_id": closeout_record_id,
                "recording_gate_evidence_recorded": True,
                "identity_closeout_recorded": True,
                "approval_closeout_recorded": True,
                "contract_freeze_recorded": True,
                "boundary_closeout_recorded": True,
                "closeout_package_recorded": True,
                "recording_gate_closed_recorded": True,
                "owner_selection_recorded": False,
                "owner_decision_recorded": False,
                "go_decision_recorded": False,
                "live_authorization_recorded": False,
                "authorization_token_recorded": False,
                "commit_command_recorded": False,
                "actual_restore_recorded": False,
                "production_write_recorded": False,
            }

            closeout_receipt_hash = _canonical_hash(
                closeout_receipt_payload
            )

            _insert_row(
                connection,
                "closeout_receipt_drafts",
                {
                    "closeout_receipt_id": (
                        closeout_receipt_id
                    ),
                    "request_id": request_id,
                    "closeout_record_id": (
                        closeout_record_id
                    ),
                    "state": (
                        "tower_recording_closeout_"
                        "receipt_draft"
                    ),
                    "tower_controlled": 1,
                    "recording_gate_evidence_recorded": 1,
                    "identity_closeout_recorded": 1,
                    "approval_closeout_recorded": 1,
                    "contract_freeze_recorded": 1,
                    "boundary_closeout_recorded": 1,
                    "closeout_package_recorded": 1,
                    "recording_gate_closed_recorded": 1,
                    "owner_selection_recorded": 0,
                    "owner_decision_recorded": 0,
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
                    "receipt_hash": (
                        closeout_receipt_hash
                    ),
                    "created_at": now,
                },
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_recording_gate_ready": bool(
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


def get_owner_decision_recording_closeout_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 621,
        "title": (
            "Owner Decision Recording Closeout Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "recording_closeout_only": True,
        "recording_contract_frozen": True,
        "recording_gate_open": False,
        "recording_execution_allowed": False,
        "owner_selection_present": False,
        "owner_decision_recorded": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "commit_point_open": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_recording_gate_evidence_closeout_intake_board(
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
        "gp": 622,
        "title": (
            "Recording Gate Evidence Closeout Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "closeout_intakes": rows,
        "all_recording_intakes_verified": all(
            bool(row["recording_intake_verified"])
            for row in rows
        ),
        "all_identity_prerequisites_verified": all(
            bool(
                row[
                    "identity_prerequisite_verified"
                ]
            )
            for row in rows
        ),
        "all_approval_gates_verified": all(
            bool(row["approval_gate_verified"])
            for row in rows
        ),
        "all_recording_contracts_verified": all(
            bool(row["recording_contract_verified"])
            for row in rows
        ),
        "all_boundaries_verified": all(
            bool(
                row[
                    "scope_window_boundary_verified"
                ]
            )
            for row in rows
        ),
        "all_record_drafts_verified": all(
            bool(row["record_draft_verified"])
            for row in rows
        ),
        "all_receipt_drafts_verified": all(
            bool(row["receipt_draft_verified"])
            for row in rows
        ),
        "all_eligible_for_closeout": all(
            bool(
                row[
                    "eligible_for_recording_closeout"
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


def get_identity_step_up_prerequisite_closeout_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM identity_closeouts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 623,
        "title": (
            "Identity and Step-Up Prerequisite "
            "Closeout Board"
        ),
        "ready": True,
        "closeout_count": len(rows),
        "identity_closeouts": rows,
        "all_requirements_sealed": all(
            bool(row["requirements_sealed"])
            for row in rows
        ),
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
                row["identity_verification_required"]
            )
            for row in rows
        ),
        "all_step_up_required": all(
            bool(row["step_up_required"])
            for row in rows
        ),
        "all_reference_requirements_present": all(
            bool(
                row[
                    "all_reference_requirements_present"
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
        "no_prerequisites_complete": all(
            not bool(row["prerequisite_complete"])
            for row in rows
        ),
        "all_source_hashes_present": all(
            len(row["source_prerequisite_hash"]) == 64
            for row in rows
        ),
        "all_closeout_hashes_present": all(
            len(row["closeout_hash"]) == 64
            for row in rows
        ),
    }


def get_approval_dual_receipt_gate_closeout_board(
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
        "gp": 624,
        "title": (
            "Approval and Dual-Receipt Gate "
            "Closeout Board"
        ),
        "ready": True,
        "closeout_count": len(rows),
        "approval_closeouts": rows,
        "all_requirements_sealed": all(
            bool(row["requirements_sealed"])
            for row in rows
        ),
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
                    "all_receipt_references_required"
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
        "all_source_hashes_present": all(
            len(row["source_approval_gate_hash"]) == 64
            for row in rows
        ),
        "all_closeout_hashes_present": all(
            len(row["closeout_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_decision_recording_contract_freeze_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM contract_freezes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 625,
        "title": (
            "Owner Decision Recording Contract "
            "Freeze Board"
        ),
        "ready": True,
        "freeze_count": len(rows),
        "contract_freezes": rows,
        "allowed_decision_values": (
            ALLOWED_DECISION_VALUES
        ),
        "required_contract_fields": (
            RECORDING_CONTRACT_FIELDS
        ),
        "all_contracts_frozen": all(
            bool(row["contract_frozen"])
            for row in rows
        ),
        "all_decision_enums_complete": all(
            row["allowed_decision_count"]
            == len(ALLOWED_DECISION_VALUES)
            for row in rows
        ),
        "all_required_fields_complete": all(
            row["required_field_count"]
            == len(RECORDING_CONTRACT_FIELDS)
            for row in rows
        ),
        "no_owner_selections_present": all(
            not bool(row["owner_selection_present"])
            for row in rows
        ),
        "all_append_only_required": all(
            bool(row["append_only_required"])
            for row in rows
        ),
        "no_mutation_allowed": all(
            not bool(row["mutation_allowed"])
            for row in rows
        ),
        "no_raw_material_allowed": all(
            not bool(row["raw_material_allowed"])
            for row in rows
        ),
        "all_source_hashes_present": all(
            len(row["source_contract_hash"]) == 64
            for row in rows
        ),
        "all_freeze_hashes_present": all(
            len(row["contract_freeze_hash"]) == 64
            for row in rows
        ),
    }


def get_scope_freeze_commit_window_boundary_closeout_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM boundary_closeouts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 626,
        "title": (
            "Scope Freeze and Commit Window "
            "Boundary Closeout Board"
        ),
        "ready": True,
        "closeout_count": len(rows),
        "boundary_closeouts": rows,
        "all_boundaries_sealed": all(
            bool(row["boundary_sealed"])
            for row in rows
        ),
        "all_exact_scopes_bound": all(
            bool(row["exact_scope_bound"])
            for row in rows
        ),
        "all_one_time_windows_required": all(
            bool(row["one_time_commit_window_required"])
            for row in rows
        ),
        "all_scope_window_hashes_required": all(
            bool(row["scope_window_hashes_required"])
            for row in rows
        ),
        "nothing_activated": all(
            not bool(row["scope_freeze_activated"])
            and not bool(row["commit_window_activated"])
            and not bool(row["execution_window_open"])
            and not bool(row["commit_point_open"])
            for row in rows
        ),
        "recording_cannot_activate_boundaries": all(
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
        "all_source_hashes_present": all(
            len(row["source_boundary_hash"]) == 64
            for row in rows
        ),
        "all_closeout_hashes_present": all(
            len(row["closeout_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_recording_closeout_record_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM closeout_record_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 627,
        "title": (
            "Tower Owner Decision Recording "
            "Closeout Record Draft Board"
        ),
        "ready": True,
        "record_count": len(rows),
        "closeout_record_drafts": rows,
        "all_source_hashes_present": all(
            len(row["source_record_draft_hash"]) == 64
            and len(
                row["source_receipt_draft_hash"]
            )
            == 64
            for row in rows
        ),
        "all_closeout_packages_complete": all(
            bool(row["closeout_package_complete"])
            for row in rows
        ),
        "all_future_tower_handoffs_eligible": all(
            bool(
                row[
                    "future_tower_handoff_eligible"
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
        "all_records_unfinalized": all(
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
        "all_closeout_hashes_present": all(
            len(row["closeout_record_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_recording_closeout_receipt_draft_ledger(
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
        "gp": 628,
        "title": (
            "Tower Recording Closeout "
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
            bool(
                row[
                    "recording_gate_evidence_recorded"
                ]
            )
            and bool(row["identity_closeout_recorded"])
            and bool(row["approval_closeout_recorded"])
            and bool(row["contract_freeze_recorded"])
            and bool(row["boundary_closeout_recorded"])
            and bool(row["closeout_package_recorded"])
            and bool(
                row["recording_gate_closed_recorded"]
            )
            for row in rows
        ),
        "no_owner_selection_or_decision_recorded": all(
            not bool(row["owner_selection_recorded"])
            and not bool(row["owner_decision_recorded"])
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


def get_owner_decision_recording_closeout_safety_blocker_board(
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
        "gp": 629,
        "title": (
            "Owner Decision Recording Closeout "
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


def get_owner_decision_recording_closeout_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_owner_decision_recording_closeout_shell()
    )

    intakes = (
        get_recording_gate_evidence_closeout_intake_board()
    )

    identities = (
        get_identity_step_up_prerequisite_closeout_board()
    )

    approvals = (
        get_approval_dual_receipt_gate_closeout_board()
    )

    contracts = (
        get_owner_decision_recording_contract_freeze_board()
    )

    boundaries = (
        get_scope_freeze_commit_window_boundary_closeout_board()
    )

    records = (
        get_tower_owner_decision_recording_closeout_record_draft_board()
    )

    receipts = (
        get_tower_recording_closeout_receipt_draft_ledger()
    )

    blockers = (
        get_owner_decision_recording_closeout_safety_blocker_board()
    )

    checks = {
        "previous_recording_gate_ready": (
            initialized[
                "previous_recording_gate_ready"
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
        "closeout_only": (
            DOCTRINE["recording_closeout_only"]
            is True
            and DOCTRINE[
                "recording_contract_may_be_frozen"
            ]
            is True
            and DOCTRINE[
                "recording_gate_may_be_opened"
            ]
            is False
            and DOCTRINE[
                "owner_decision_may_be_recorded"
            ]
            is False
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "recording_evidence_verified": (
            intakes[
                "all_recording_intakes_verified"
            ]
            is True
            and intakes[
                "all_identity_prerequisites_verified"
            ]
            is True
            and intakes[
                "all_approval_gates_verified"
            ]
            is True
            and intakes[
                "all_recording_contracts_verified"
            ]
            is True
            and intakes[
                "all_boundaries_verified"
            ]
            is True
            and intakes[
                "all_record_drafts_verified"
            ]
            is True
            and intakes[
                "all_receipt_drafts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_closeout"
            ]
            is True
        ),
        "recording_gate_still_closed": (
            intakes["no_recording_gates_open"]
            is True
            and intakes[
                "no_owner_decisions_recorded"
            ]
            is True
        ),

        "identity_closeouts_present": (
            identities["closeout_count"] >= 1
        ),
        "identity_requirements_sealed": (
            identities[
                "all_requirements_sealed"
            ]
            is True
            and identities[
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
        "identity_controls_not_satisfied": (
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
                "no_prerequisites_complete"
            ]
            is True
        ),

        "approval_closeouts_present": (
            approvals["closeout_count"] >= 1
        ),
        "approval_requirements_sealed": (
            approvals[
                "all_requirements_sealed"
            ]
            is True
            and approvals[
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
        "approval_controls_not_satisfied": (
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

        "contract_freezes_present": (
            contracts["freeze_count"] >= 1
        ),
        "recording_contract_frozen": (
            contracts["all_contracts_frozen"]
            is True
            and contracts[
                "all_decision_enums_complete"
            ]
            is True
            and contracts[
                "all_required_fields_complete"
            ]
            is True
            and contracts[
                "all_append_only_required"
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
        "owner_selection_still_absent": (
            contracts[
                "no_owner_selections_present"
            ]
            is True
        ),

        "boundary_closeouts_present": (
            boundaries["closeout_count"] >= 1
        ),
        "boundaries_sealed": (
            boundaries[
                "all_boundaries_sealed"
            ]
            is True
            and boundaries[
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
        "boundaries_not_activated": (
            boundaries["nothing_activated"]
            is True
            and boundaries[
                "recording_cannot_activate_boundaries"
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

        "closeout_records_present": (
            records["record_count"] >= 1
        ),
        "closeout_record_package_ready": (
            records[
                "all_source_hashes_present"
            ]
            is True
            and records[
                "all_closeout_packages_complete"
            ]
            is True
            and records[
                "all_future_tower_handoffs_eligible"
            ]
            is True
            and records[
                "all_records_unfinalized"
            ]
            is True
            and records["all_append_only"]
            is True
            and records["all_immutable"]
            is True
        ),
        "no_decision_or_execution_recorded": (
            records["no_recording_gates_open"]
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

        "closeout_receipts_present": (
            receipts["receipt_count"] >= 1
        ),
        "closeout_receipts_safe": (
            receipts["all_tower_controlled"]
            is True
            and receipts[
                "all_closeout_components_recorded"
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
        "gp": 630,
        "title": (
            "Owner Decision Recording Closeout "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else (
                "Owner decision recording "
                "closeout blocked"
            )
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "closeout_status": (
            "recording_gate_contracts_sealed_"
            "prerequisites_unsatisfied_"
            "recording_gate_closed_"
            "owner_decision_absent"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION TOWER HANDOFF "
            "LAYER / GP631-GP640"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no recording gate open",
            "no recording execution",
            "no Tower owner-review session started",
            "no owner authenticated",
            "no step-up satisfied",
            "no owner/admin approval granted",
            "no dual receipt satisfied",
            "no second-authority review granted",
            "no owner selection present",
            "no owner decision recorded",
            "no GO decision granted",
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


def get_recovery_commit_owner_decision_recording_closeout_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_recording_closeout_readiness_checkpoint()
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


def validate_recovery_commit_owner_decision_recording_closeout_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_owner_decision_recording_closeout_readiness_checkpoint()
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
        get_owner_decision_recording_closeout_readiness_checkpoint()
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
        "recording_contract_frozen": True,
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


def get_gp621_status():
    return _gp_status(621)


def get_gp622_status():
    return _gp_status(622)


def get_gp623_status():
    return _gp_status(623)


def get_gp624_status():
    return _gp_status(624)


def get_gp625_status():
    return _gp_status(625)


def get_gp626_status():
    return _gp_status(626)


def get_gp627_status():
    return _gp_status(627)


def get_gp628_status():
    return _gp_status(628)


def get_gp629_status():
    return _gp_status(629)


def get_gp630_status():
    return _gp_status(630)
