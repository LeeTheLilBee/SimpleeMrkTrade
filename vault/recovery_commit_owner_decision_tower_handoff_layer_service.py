
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER "
    "DECISION TOWER HANDOFF LAYER / GP631-GP640"
)

LAYER_ID = (
    "vault_gp631_640_"
    "recovery_commit_owner_decision_tower_handoff_layer"
)

READINESS_LABEL = (
    "Owner decision Tower handoff package ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_PACKAGE_READY_NOT_ACCEPTED"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_tower_handoff_layer.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_owner_decision_recording_closeout_layer_service import (
        ALLOWED_DECISION_VALUES,
        RECORDING_CONTRACT_FIELDS,
        get_recording_gate_evidence_closeout_intake_board,
        get_identity_step_up_prerequisite_closeout_board,
        get_approval_dual_receipt_gate_closeout_board,
        get_owner_decision_recording_contract_freeze_board,
        get_scope_freeze_commit_window_boundary_closeout_board,
        get_tower_owner_decision_recording_closeout_record_draft_board,
        get_tower_recording_closeout_receipt_draft_ledger,
        validate_recovery_commit_owner_decision_recording_closeout_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP631-GP640 requires the completed "
        "GP621-GP630 owner decision recording closeout layer."
    ) from exc


_INIT_CACHE = None


HANDOFF_ENVELOPE_FIELDS = [
    "handoff_id",
    "request_id",
    "source_closeout_record_hash",
    "source_closeout_receipt_hash",
    "source_identity_closeout_hash",
    "source_approval_closeout_hash",
    "source_contract_freeze_hash",
    "source_boundary_closeout_hash",
    "target_service",
    "target_workflow",
    "requested_tower_action",
    "required_tower_session_type",
    "required_owner_principal_reference",
    "required_tower_actor_reference",
    "required_identity_receipt_reference",
    "required_step_up_receipt_reference",
    "required_owner_admin_approval_receipt_reference",
    "required_primary_dual_receipt_reference",
    "required_secondary_dual_receipt_reference",
    "required_second_authority_receipt_reference",
    "exact_scope_hash_reference",
    "one_time_commit_window_hash_reference",
    "idempotency_key",
    "handoff_created_at",
]


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "tower_handoff_packaging_only": True,
    "tower_handoff_delivery_allowed": False,
    "tower_handoff_acceptance_allowed": False,
    "tower_is_only_owner_session_boundary": True,
    "vault_may_not_collect_owner_input": True,
    "vault_preserves_handoff_evidence": True,
    "current_recommendation": CURRENT_RECOMMENDATION,
    "handoff_delivered": False,
    "handoff_accepted": False,
    "tower_session_created": False,
    "review_session_started": False,
    "owner_authenticated": False,
    "step_up_satisfied": False,
    "owner_admin_approval_granted": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,
    "owner_selection_present": False,
    "owner_decision_recorded": False,
    "recording_gate_open": False,
    "go_decision_granted": False,
    "live_authorization_granted": False,
    "authorization_token_issued": False,
    "scope_freeze_activated": False,
    "commit_window_activated": False,
    "execution_window_open": False,
    "commit_point_open": False,
    "commit_command_issued": False,
    "actual_restore_execution_allowed": False,
    "production_recovery_write_allowed": False,
    "vault_answers_tower_only": True,
    "teller_can_call_vault_directly": False,
}


LOCKS = {
    "tower_handoff_layer": True,
    "closeout_package_intake_allowed": True,
    "handoff_envelope_definition_allowed": True,
    "session_prerequisite_definition_allowed": True,
    "owner_input_contract_definition_allowed": True,
    "approval_reference_definition_allowed": True,
    "handoff_packet_drafts_allowed": True,
    "handoff_receipt_drafts_allowed": True,

    "handoff_delivered": False,
    "handoff_accepted": False,
    "tower_session_created": False,
    "review_session_started": False,
    "owner_authenticated": False,
    "step_up_satisfied": False,
    "owner_admin_approval_granted": False,
    "dual_receipt_satisfied": False,
    "second_authority_review_granted": False,
    "owner_selection_present": False,
    "owner_decision_recorded": False,
    "recording_gate_open": False,
    "recording_execution_allowed": False,
    "go_decision_granted": False,

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

    "teller_direct_handoff_allowed": False,
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
        "gp": 631,
        "title": "Owner Decision Tower Handoff Shell",
        "route": (
            "/vault/owner-decision-"
            "tower-handoff-shell.json"
        ),
    },
    {
        "gp": 632,
        "title": (
            "Recording Closeout Package Intake Board"
        ),
        "route": (
            "/vault/recording-closeout-package-"
            "intake-board.json"
        ),
    },
    {
        "gp": 633,
        "title": (
            "Tower Handoff Envelope Contract Board"
        ),
        "route": (
            "/vault/tower-handoff-envelope-"
            "contract-board.json"
        ),
    },
    {
        "gp": 634,
        "title": (
            "Tower Owner Review Session Launch "
            "Prerequisite Board"
        ),
        "route": (
            "/vault/tower-owner-review-session-launch-"
            "prerequisite-board.json"
        ),
    },
    {
        "gp": 635,
        "title": (
            "Owner Decision Input Handoff Contract Board"
        ),
        "route": (
            "/vault/owner-decision-input-handoff-"
            "contract-board.json"
        ),
    },
    {
        "gp": 636,
        "title": (
            "Approval and Receipt Reference "
            "Handoff Board"
        ),
        "route": (
            "/vault/approval-receipt-reference-"
            "handoff-board.json"
        ),
    },
    {
        "gp": 637,
        "title": (
            "Tower Owner Decision Handoff "
            "Packet Draft Board"
        ),
        "route": (
            "/vault/tower-owner-decision-handoff-"
            "packet-draft-board.json"
        ),
    },
    {
        "gp": 638,
        "title": (
            "Tower Owner Decision Handoff "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-owner-decision-handoff-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 639,
        "title": "Tower Handoff Safety Blocker Board",
        "route": (
            "/vault/tower-handoff-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 640,
        "title": "Tower Handoff Readiness Checkpoint",
        "route": (
            "/vault/tower-handoff-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_live_handoff_delivery",
        "live_handoff_delivery",
        "This layer packages but does not deliver the handoff.",
    ),
    (
        "no_tower_acceptance",
        "tower_handoff_acceptance",
        "Tower acceptance requires a later controlled gate.",
    ),
    (
        "no_tower_session_creation",
        "tower_session_creation",
        "Vault cannot create a Tower owner session.",
    ),
    (
        "no_owner_review_session_start",
        "owner_review_session_start",
        "Tower must start the owner-review session.",
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
        "no_owner_input_collection",
        "owner_input_collection",
        "Vault cannot collect direct owner input.",
    ),
    (
        "no_owner_selection_invention",
        "owner_selection_invention",
        "Vault cannot invent an owner selection.",
    ),
    (
        "no_owner_decision_recording",
        "owner_decision_recording",
        "No owner decision is recorded.",
    ),
    (
        "no_recording_gate_open",
        "recording_gate_open",
        "The recording gate remains closed.",
    ),
    (
        "no_go_decision",
        "go_decision_grant",
        "GO remains unavailable.",
    ),
    (
        "no_live_authorization",
        "live_authorization_grant",
        "No recovery authorization is granted.",
    ),
    (
        "no_token_issue",
        "authorization_token_issue",
        "No authorization token is issued.",
    ),
    (
        "no_scope_activation",
        "scope_freeze_activation",
        "Scope freeze remains inactive.",
    ),
    (
        "no_window_activation",
        "commit_window_activation",
        "Commit window remains inactive.",
    ),
    (
        "no_execution_window",
        "execution_window_open",
        "Execution remains closed.",
    ),
    (
        "no_commit_point",
        "commit_point_open",
        "Commit point remains closed.",
    ),
    (
        "no_commit_command",
        "real_commit_command",
        "No real commit command may be issued.",
    ),
    (
        "no_actual_restore",
        "actual_restore_execution",
        "No restore may be executed.",
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
        "No storage provider may be connected.",
    ),
    (
        "no_teller_direct_handoff",
        "teller_direct_handoff",
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
        "The handoff contains references and hashes only.",
    ),
    (
        "no_destructive_action",
        "delete_purge_release_or_move",
        "Handoff packaging cannot destroy evidence.",
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
        get_recording_gate_evidence_closeout_intake_board()
        .get("closeout_intakes", [])
    )

    identity_rows = (
        get_identity_step_up_prerequisite_closeout_board()
        .get("identity_closeouts", [])
    )

    approval_rows = (
        get_approval_dual_receipt_gate_closeout_board()
        .get("approval_closeouts", [])
    )

    contract_rows = (
        get_owner_decision_recording_contract_freeze_board()
        .get("contract_freezes", [])
    )

    boundary_rows = (
        get_scope_freeze_commit_window_boundary_closeout_board()
        .get("boundary_closeouts", [])
    )

    record_rows = (
        get_tower_owner_decision_recording_closeout_record_draft_board()
        .get("closeout_record_drafts", [])
    )

    receipt_rows = (
        get_tower_recording_closeout_receipt_draft_ledger()
        .get("closeout_receipt_drafts", [])
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
        validate_recovery_commit_owner_decision_recording_closeout_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS handoff_intakes (
                handoff_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                closeout_intake_verified INTEGER NOT NULL,
                identity_closeout_verified INTEGER NOT NULL,
                approval_closeout_verified INTEGER NOT NULL,
                contract_freeze_verified INTEGER NOT NULL,
                boundary_closeout_verified INTEGER NOT NULL,
                closeout_record_verified INTEGER NOT NULL,
                closeout_receipt_verified INTEGER NOT NULL,
                eligible_for_tower_handoff_packaging INTEGER NOT NULL,
                handoff_delivered INTEGER NOT NULL,
                handoff_accepted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS handoff_envelopes (
                handoff_envelope_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                target_service TEXT NOT NULL,
                target_workflow TEXT NOT NULL,
                requested_tower_action TEXT NOT NULL,
                required_fields_json TEXT NOT NULL,
                required_field_count INTEGER NOT NULL,
                source_package_hash TEXT NOT NULL,
                source_closeout_record_hash TEXT NOT NULL,
                source_closeout_receipt_hash TEXT NOT NULL,
                tower_only INTEGER NOT NULL,
                references_only INTEGER NOT NULL,
                raw_material_allowed INTEGER NOT NULL,
                delivery_allowed INTEGER NOT NULL,
                acceptance_allowed INTEGER NOT NULL,
                envelope_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS session_launch_prerequisites (
                session_prerequisite_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_session_type_required INTEGER NOT NULL,
                owner_presence_required INTEGER NOT NULL,
                tower_actor_reference_required INTEGER NOT NULL,
                owner_principal_reference_required INTEGER NOT NULL,
                identity_receipt_reference_required INTEGER NOT NULL,
                step_up_receipt_reference_required INTEGER NOT NULL,
                owner_admin_approval_receipt_required INTEGER NOT NULL,
                dual_receipts_required INTEGER NOT NULL,
                second_authority_receipt_required INTEGER NOT NULL,
                session_created INTEGER NOT NULL,
                session_started INTEGER NOT NULL,
                owner_authenticated INTEGER NOT NULL,
                step_up_satisfied INTEGER NOT NULL,
                prerequisite_complete INTEGER NOT NULL,
                prerequisite_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS owner_input_contracts (
                input_contract_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                allowed_decisions_json TEXT NOT NULL,
                required_recording_fields_json TEXT NOT NULL,
                allowed_decision_count INTEGER NOT NULL,
                required_field_count INTEGER NOT NULL,
                tower_ui_only INTEGER NOT NULL,
                vault_direct_input_allowed INTEGER NOT NULL,
                teller_direct_input_allowed INTEGER NOT NULL,
                owner_selection_present INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                decision_reason_required INTEGER NOT NULL,
                idempotency_key_required INTEGER NOT NULL,
                append_only_required INTEGER NOT NULL,
                mutation_allowed INTEGER NOT NULL,
                contract_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approval_reference_handoffs (
                approval_handoff_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                identity_receipt_reference_required INTEGER NOT NULL,
                step_up_receipt_reference_required INTEGER NOT NULL,
                owner_admin_approval_receipt_required INTEGER NOT NULL,
                primary_dual_receipt_reference_required INTEGER NOT NULL,
                secondary_dual_receipt_reference_required INTEGER NOT NULL,
                second_authority_receipt_reference_required INTEGER NOT NULL,
                exact_scope_hash_reference_required INTEGER NOT NULL,
                commit_window_hash_reference_required INTEGER NOT NULL,
                supplied_reference_count INTEGER NOT NULL,
                reference_gate_complete INTEGER NOT NULL,
                owner_admin_approval_granted INTEGER NOT NULL,
                dual_receipt_satisfied INTEGER NOT NULL,
                second_authority_review_granted INTEGER NOT NULL,
                reference_handoff_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS handoff_packet_drafts (
                handoff_packet_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                handoff_envelope_id TEXT NOT NULL,
                session_prerequisite_id TEXT NOT NULL,
                input_contract_id TEXT NOT NULL,
                approval_handoff_id TEXT NOT NULL,
                source_closeout_record_hash TEXT NOT NULL,
                source_closeout_receipt_hash TEXT NOT NULL,
                package_complete INTEGER NOT NULL,
                eligible_for_future_tower_acceptance INTEGER NOT NULL,
                handoff_delivered INTEGER NOT NULL,
                handoff_accepted INTEGER NOT NULL,
                tower_session_created INTEGER NOT NULL,
                owner_selection_present INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                recording_gate_open INTEGER NOT NULL,
                go_decision_granted INTEGER NOT NULL,
                live_authorization_granted INTEGER NOT NULL,
                authorization_token_issued INTEGER NOT NULL,
                commit_command_issued INTEGER NOT NULL,
                actual_restore_allowed INTEGER NOT NULL,
                production_write_allowed INTEGER NOT NULL,
                finalized INTEGER NOT NULL,
                append_only INTEGER NOT NULL,
                mutable INTEGER NOT NULL,
                packet_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS handoff_receipt_drafts (
                handoff_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                handoff_packet_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                closeout_package_recorded INTEGER NOT NULL,
                envelope_contract_recorded INTEGER NOT NULL,
                session_prerequisites_recorded INTEGER NOT NULL,
                owner_input_contract_recorded INTEGER NOT NULL,
                approval_references_recorded INTEGER NOT NULL,
                packet_draft_recorded INTEGER NOT NULL,
                handoff_delivery_recorded INTEGER NOT NULL,
                handoff_acceptance_recorded INTEGER NOT NULL,
                tower_session_creation_recorded INTEGER NOT NULL,
                owner_selection_recorded INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                recording_gate_open_recorded INTEGER NOT NULL,
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
            "handoff_intakes",
            "handoff_envelopes",
            "session_launch_prerequisites",
            "owner_input_contracts",
            "approval_reference_handoffs",
            "handoff_packet_drafts",
            "handoff_receipt_drafts",
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

            closeout_intake_verified = all(
                [
                    bool(
                        intake.get(
                            "recording_intake_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "identity_prerequisite_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "approval_gate_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "recording_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "scope_window_boundary_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "record_draft_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "receipt_draft_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_recording_closeout",
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

            identity_closeout_verified = all(
                [
                    bool(
                        identity.get(
                            "requirements_sealed",
                            0,
                        )
                    ),
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
                            "identity_verification_required",
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
                            "all_reference_requirements_present",
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
                            "source_prerequisite_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        identity.get(
                            "closeout_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            approval_closeout_verified = all(
                [
                    bool(
                        approval.get(
                            "requirements_sealed",
                            0,
                        )
                    ),
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
                            "all_receipt_references_required",
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
                            "source_approval_gate_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        approval.get(
                            "closeout_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            contract_freeze_verified = all(
                [
                    bool(
                        contract.get(
                            "contract_frozen",
                            0,
                        )
                    ),
                    int(
                        contract.get(
                            "allowed_decision_count",
                            0,
                        )
                    )
                    == len(ALLOWED_DECISION_VALUES),
                    int(
                        contract.get(
                            "required_field_count",
                            0,
                        )
                    )
                    == len(RECORDING_CONTRACT_FIELDS),
                    not bool(
                        contract.get(
                            "owner_selection_present",
                            1,
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
                            "raw_material_allowed",
                            1,
                        )
                    ),
                    len(
                        contract.get(
                            "source_contract_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        contract.get(
                            "contract_freeze_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            boundary_closeout_verified = all(
                [
                    bool(
                        boundary.get(
                            "boundary_sealed",
                            0,
                        )
                    ),
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
                            "scope_window_hashes_required",
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
                            "source_boundary_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        boundary.get(
                            "closeout_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            closeout_record_verified = all(
                [
                    len(
                        record.get(
                            "source_record_draft_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        record.get(
                            "source_receipt_draft_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        record.get(
                            "closeout_package_complete",
                            0,
                        )
                    ),
                    bool(
                        record.get(
                            "future_tower_handoff_eligible",
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
                            "closeout_record_hash",
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
                            "recording_gate_evidence_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "identity_closeout_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "approval_closeout_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "contract_freeze_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "boundary_closeout_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "closeout_package_recorded",
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
                            "owner_decision_recorded",
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

            eligible_for_handoff_packaging = all(
                [
                    closeout_intake_verified,
                    identity_closeout_verified,
                    approval_closeout_verified,
                    contract_freeze_verified,
                    boundary_closeout_verified,
                    closeout_record_verified,
                    closeout_receipt_verified,
                ]
            )

            handoff_intake_id = _id(
                "tower_handoff_intake",
                request_id,
            )

            handoff_envelope_id = _id(
                "tower_handoff_envelope",
                request_id,
            )

            session_prerequisite_id = _id(
                "tower_session_launch_prerequisite",
                request_id,
            )

            input_contract_id = _id(
                "tower_owner_input_contract",
                request_id,
            )

            approval_handoff_id = _id(
                "tower_approval_reference_handoff",
                request_id,
            )

            handoff_packet_id = _id(
                "tower_owner_decision_handoff_packet",
                request_id,
            )

            handoff_receipt_id = _id(
                "tower_owner_decision_handoff_receipt",
                request_id,
            )

            _insert_row(
                connection,
                "handoff_intakes",
                {
                    "handoff_intake_id": handoff_intake_id,
                    "request_id": request_id,
                    "workflow_type": workflow_type,
                    "state": (
                        "recording_closeout_verified_"
                        "eligible_for_handoff_packaging"
                    ),
                    "closeout_intake_verified": int(
                        closeout_intake_verified
                    ),
                    "identity_closeout_verified": int(
                        identity_closeout_verified
                    ),
                    "approval_closeout_verified": int(
                        approval_closeout_verified
                    ),
                    "contract_freeze_verified": int(
                        contract_freeze_verified
                    ),
                    "boundary_closeout_verified": int(
                        boundary_closeout_verified
                    ),
                    "closeout_record_verified": int(
                        closeout_record_verified
                    ),
                    "closeout_receipt_verified": int(
                        closeout_receipt_verified
                    ),
                    "eligible_for_tower_handoff_packaging": int(
                        eligible_for_handoff_packaging
                    ),
                    "handoff_delivered": 0,
                    "handoff_accepted": 0,
                    "created_at": now,
                },
            )

            source_package_payload = {
                "request_id": request_id,
                "identity_closeout_hash": identity.get(
                    "closeout_hash",
                    "",
                ),
                "approval_closeout_hash": approval.get(
                    "closeout_hash",
                    "",
                ),
                "contract_freeze_hash": contract.get(
                    "contract_freeze_hash",
                    "",
                ),
                "boundary_closeout_hash": boundary.get(
                    "closeout_hash",
                    "",
                ),
                "closeout_record_hash": record.get(
                    "closeout_record_hash",
                    "",
                ),
                "closeout_receipt_hash": receipt.get(
                    "receipt_hash",
                    "",
                ),
            }

            source_package_hash = _canonical_hash(
                source_package_payload
            )

            envelope_payload = {
                "request_id": request_id,
                "target_service": "tower",
                "target_workflow": (
                    "owner_recovery_decision_review"
                ),
                "requested_tower_action": (
                    "accept_sealed_owner_decision_handoff"
                ),
                "required_fields": HANDOFF_ENVELOPE_FIELDS,
                "source_package_hash": source_package_hash,
                "tower_only": True,
                "references_only": True,
                "raw_material_allowed": False,
                "delivery_allowed": False,
                "acceptance_allowed": False,
            }

            envelope_hash = _canonical_hash(
                envelope_payload
            )

            _insert_row(
                connection,
                "handoff_envelopes",
                {
                    "handoff_envelope_id": (
                        handoff_envelope_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_handoff_envelope_defined_"
                        "not_delivered"
                    ),
                    "target_service": "tower",
                    "target_workflow": (
                        "owner_recovery_decision_review"
                    ),
                    "requested_tower_action": (
                        "accept_sealed_owner_decision_handoff"
                    ),
                    "required_fields_json": json.dumps(
                        HANDOFF_ENVELOPE_FIELDS,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "required_field_count": len(
                        HANDOFF_ENVELOPE_FIELDS
                    ),
                    "source_package_hash": (
                        source_package_hash
                    ),
                    "source_closeout_record_hash": (
                        record.get(
                            "closeout_record_hash",
                            "",
                        )
                    ),
                    "source_closeout_receipt_hash": (
                        receipt.get(
                            "receipt_hash",
                            "",
                        )
                    ),
                    "tower_only": 1,
                    "references_only": 1,
                    "raw_material_allowed": 0,
                    "delivery_allowed": 0,
                    "acceptance_allowed": 0,
                    "envelope_hash": envelope_hash,
                    "created_at": now,
                },
            )

            session_payload = {
                "request_id": request_id,
                "tower_session_type_required": True,
                "owner_presence_required": True,
                "tower_actor_reference_required": True,
                "owner_principal_reference_required": True,
                "identity_receipt_reference_required": True,
                "step_up_receipt_reference_required": True,
                "owner_admin_approval_receipt_required": True,
                "dual_receipts_required": True,
                "second_authority_receipt_required": True,
                "session_created": False,
                "session_started": False,
                "owner_authenticated": False,
                "step_up_satisfied": False,
                "prerequisite_complete": False,
            }

            prerequisite_hash = _canonical_hash(
                session_payload
            )

            _insert_row(
                connection,
                "session_launch_prerequisites",
                {
                    "session_prerequisite_id": (
                        session_prerequisite_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_session_launch_requirements_"
                        "defined_not_satisfied"
                    ),
                    "tower_session_type_required": 1,
                    "owner_presence_required": 1,
                    "tower_actor_reference_required": 1,
                    "owner_principal_reference_required": 1,
                    "identity_receipt_reference_required": 1,
                    "step_up_receipt_reference_required": 1,
                    "owner_admin_approval_receipt_required": 1,
                    "dual_receipts_required": 1,
                    "second_authority_receipt_required": 1,
                    "session_created": 0,
                    "session_started": 0,
                    "owner_authenticated": 0,
                    "step_up_satisfied": 0,
                    "prerequisite_complete": 0,
                    "prerequisite_hash": prerequisite_hash,
                    "created_at": now,
                },
            )

            input_payload = {
                "request_id": request_id,
                "allowed_decisions": ALLOWED_DECISION_VALUES,
                "required_recording_fields": (
                    RECORDING_CONTRACT_FIELDS
                ),
                "tower_ui_only": True,
                "vault_direct_input_allowed": False,
                "teller_direct_input_allowed": False,
                "owner_selection_present": False,
                "owner_decision_recorded": False,
                "decision_reason_required": True,
                "idempotency_key_required": True,
                "append_only_required": True,
                "mutation_allowed": False,
            }

            input_contract_hash = _canonical_hash(
                input_payload
            )

            _insert_row(
                connection,
                "owner_input_contracts",
                {
                    "input_contract_id": input_contract_id,
                    "request_id": request_id,
                    "state": (
                        "owner_input_contract_defined_"
                        "tower_ui_only_no_input_collected"
                    ),
                    "allowed_decisions_json": json.dumps(
                        ALLOWED_DECISION_VALUES,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "required_recording_fields_json": (
                        json.dumps(
                            RECORDING_CONTRACT_FIELDS,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                    ),
                    "allowed_decision_count": len(
                        ALLOWED_DECISION_VALUES
                    ),
                    "required_field_count": len(
                        RECORDING_CONTRACT_FIELDS
                    ),
                    "tower_ui_only": 1,
                    "vault_direct_input_allowed": 0,
                    "teller_direct_input_allowed": 0,
                    "owner_selection_present": 0,
                    "owner_decision_recorded": 0,
                    "decision_reason_required": 1,
                    "idempotency_key_required": 1,
                    "append_only_required": 1,
                    "mutation_allowed": 0,
                    "contract_hash": input_contract_hash,
                    "created_at": now,
                },
            )

            approval_reference_payload = {
                "request_id": request_id,
                "identity_receipt_reference_required": True,
                "step_up_receipt_reference_required": True,
                "owner_admin_approval_receipt_required": True,
                "primary_dual_receipt_reference_required": True,
                "secondary_dual_receipt_reference_required": True,
                "second_authority_receipt_reference_required": True,
                "exact_scope_hash_reference_required": True,
                "commit_window_hash_reference_required": True,
                "supplied_reference_count": 0,
                "reference_gate_complete": False,
                "owner_admin_approval_granted": False,
                "dual_receipt_satisfied": False,
                "second_authority_review_granted": False,
            }

            approval_reference_hash = _canonical_hash(
                approval_reference_payload
            )

            _insert_row(
                connection,
                "approval_reference_handoffs",
                {
                    "approval_handoff_id": (
                        approval_handoff_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "approval_reference_requirements_"
                        "defined_none_supplied"
                    ),
                    "identity_receipt_reference_required": 1,
                    "step_up_receipt_reference_required": 1,
                    "owner_admin_approval_receipt_required": 1,
                    "primary_dual_receipt_reference_required": 1,
                    "secondary_dual_receipt_reference_required": 1,
                    "second_authority_receipt_reference_required": 1,
                    "exact_scope_hash_reference_required": 1,
                    "commit_window_hash_reference_required": 1,
                    "supplied_reference_count": 0,
                    "reference_gate_complete": 0,
                    "owner_admin_approval_granted": 0,
                    "dual_receipt_satisfied": 0,
                    "second_authority_review_granted": 0,
                    "reference_handoff_hash": (
                        approval_reference_hash
                    ),
                    "created_at": now,
                },
            )

            packet_payload = {
                "request_id": request_id,
                "handoff_envelope_id": (
                    handoff_envelope_id
                ),
                "session_prerequisite_id": (
                    session_prerequisite_id
                ),
                "input_contract_id": input_contract_id,
                "approval_handoff_id": (
                    approval_handoff_id
                ),
                "source_closeout_record_hash": record.get(
                    "closeout_record_hash",
                    "",
                ),
                "source_closeout_receipt_hash": receipt.get(
                    "receipt_hash",
                    "",
                ),
                "package_complete": True,
                "eligible_for_future_tower_acceptance": True,
                "handoff_delivered": False,
                "handoff_accepted": False,
                "tower_session_created": False,
                "owner_selection_present": False,
                "owner_decision_recorded": False,
                "recording_gate_open": False,
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

            packet_hash = _canonical_hash(
                packet_payload
            )

            _insert_row(
                connection,
                "handoff_packet_drafts",
                {
                    "handoff_packet_id": (
                        handoff_packet_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_handoff_packet_complete_"
                        "not_delivered_not_accepted"
                    ),
                    "handoff_envelope_id": (
                        handoff_envelope_id
                    ),
                    "session_prerequisite_id": (
                        session_prerequisite_id
                    ),
                    "input_contract_id": input_contract_id,
                    "approval_handoff_id": (
                        approval_handoff_id
                    ),
                    "source_closeout_record_hash": (
                        record.get(
                            "closeout_record_hash",
                            "",
                        )
                    ),
                    "source_closeout_receipt_hash": (
                        receipt.get(
                            "receipt_hash",
                            "",
                        )
                    ),
                    "package_complete": 1,
                    "eligible_for_future_tower_acceptance": 1,
                    "handoff_delivered": 0,
                    "handoff_accepted": 0,
                    "tower_session_created": 0,
                    "owner_selection_present": 0,
                    "owner_decision_recorded": 0,
                    "recording_gate_open": 0,
                    "go_decision_granted": 0,
                    "live_authorization_granted": 0,
                    "authorization_token_issued": 0,
                    "commit_command_issued": 0,
                    "actual_restore_allowed": 0,
                    "production_write_allowed": 0,
                    "finalized": 0,
                    "append_only": 1,
                    "mutable": 0,
                    "packet_hash": packet_hash,
                    "created_at": now,
                },
            )

            receipt_payload = {
                "request_id": request_id,
                "handoff_packet_id": handoff_packet_id,
                "closeout_package_recorded": True,
                "envelope_contract_recorded": True,
                "session_prerequisites_recorded": True,
                "owner_input_contract_recorded": True,
                "approval_references_recorded": True,
                "packet_draft_recorded": True,
                "handoff_delivery_recorded": False,
                "handoff_acceptance_recorded": False,
                "tower_session_creation_recorded": False,
                "owner_selection_recorded": False,
                "owner_decision_recorded": False,
                "recording_gate_open_recorded": False,
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
                "handoff_receipt_drafts",
                {
                    "handoff_receipt_id": (
                        handoff_receipt_id
                    ),
                    "request_id": request_id,
                    "handoff_packet_id": (
                        handoff_packet_id
                    ),
                    "state": (
                        "tower_handoff_receipt_draft_"
                        "delivery_not_recorded"
                    ),
                    "tower_controlled": 1,
                    "closeout_package_recorded": 1,
                    "envelope_contract_recorded": 1,
                    "session_prerequisites_recorded": 1,
                    "owner_input_contract_recorded": 1,
                    "approval_references_recorded": 1,
                    "packet_draft_recorded": 1,
                    "handoff_delivery_recorded": 0,
                    "handoff_acceptance_recorded": 0,
                    "tower_session_creation_recorded": 0,
                    "owner_selection_recorded": 0,
                    "owner_decision_recorded": 0,
                    "recording_gate_open_recorded": 0,
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
        "previous_recording_closeout_ready": bool(
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


def get_owner_decision_tower_handoff_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 631,
        "title": "Owner Decision Tower Handoff Shell",
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "tower_handoff_packaging_only": True,
        "handoff_delivered": False,
        "handoff_accepted": False,
        "tower_session_created": False,
        "owner_selection_present": False,
        "owner_decision_recorded": False,
        "recording_gate_open": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "commit_point_open": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_recording_closeout_package_intake_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM handoff_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 632,
        "title": (
            "Recording Closeout Package Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "handoff_intakes": rows,
        "all_closeout_intakes_verified": all(
            bool(row["closeout_intake_verified"])
            for row in rows
        ),
        "all_identity_closeouts_verified": all(
            bool(row["identity_closeout_verified"])
            for row in rows
        ),
        "all_approval_closeouts_verified": all(
            bool(row["approval_closeout_verified"])
            for row in rows
        ),
        "all_contract_freezes_verified": all(
            bool(row["contract_freeze_verified"])
            for row in rows
        ),
        "all_boundaries_verified": all(
            bool(row["boundary_closeout_verified"])
            for row in rows
        ),
        "all_closeout_records_verified": all(
            bool(row["closeout_record_verified"])
            for row in rows
        ),
        "all_closeout_receipts_verified": all(
            bool(row["closeout_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_handoff_packaging": all(
            bool(
                row[
                    "eligible_for_tower_handoff_packaging"
                ]
            )
            for row in rows
        ),
        "no_handoffs_delivered": all(
            not bool(row["handoff_delivered"])
            for row in rows
        ),
        "no_handoffs_accepted": all(
            not bool(row["handoff_accepted"])
            for row in rows
        ),
    }


def get_tower_handoff_envelope_contract_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM handoff_envelopes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 633,
        "title": (
            "Tower Handoff Envelope Contract Board"
        ),
        "ready": True,
        "envelope_count": len(rows),
        "handoff_envelopes": rows,
        "required_envelope_fields": (
            HANDOFF_ENVELOPE_FIELDS
        ),
        "all_target_tower": all(
            row["target_service"] == "tower"
            for row in rows
        ),
        "all_workflows_bound": all(
            row["target_workflow"]
            == "owner_recovery_decision_review"
            for row in rows
        ),
        "all_required_fields_complete": all(
            row["required_field_count"]
            == len(HANDOFF_ENVELOPE_FIELDS)
            for row in rows
        ),
        "all_source_hashes_present": all(
            len(row["source_package_hash"]) == 64
            and len(
                row["source_closeout_record_hash"]
            )
            == 64
            and len(
                row["source_closeout_receipt_hash"]
            )
            == 64
            for row in rows
        ),
        "all_tower_only": all(
            bool(row["tower_only"])
            for row in rows
        ),
        "all_references_only": all(
            bool(row["references_only"])
            for row in rows
        ),
        "no_raw_material_allowed": all(
            not bool(row["raw_material_allowed"])
            for row in rows
        ),
        "no_delivery_allowed": all(
            not bool(row["delivery_allowed"])
            for row in rows
        ),
        "no_acceptance_allowed": all(
            not bool(row["acceptance_allowed"])
            for row in rows
        ),
        "all_envelope_hashes_present": all(
            len(row["envelope_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_review_session_launch_prerequisite_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM session_launch_prerequisites
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 634,
        "title": (
            "Tower Owner Review Session Launch "
            "Prerequisite Board"
        ),
        "ready": True,
        "prerequisite_count": len(rows),
        "session_launch_prerequisites": rows,
        "all_session_requirements_present": all(
            bool(row["tower_session_type_required"])
            and bool(row["owner_presence_required"])
            and bool(
                row["tower_actor_reference_required"]
            )
            and bool(
                row["owner_principal_reference_required"]
            )
            and bool(
                row["identity_receipt_reference_required"]
            )
            and bool(
                row["step_up_receipt_reference_required"]
            )
            and bool(
                row[
                    "owner_admin_approval_receipt_required"
                ]
            )
            and bool(row["dual_receipts_required"])
            and bool(
                row[
                    "second_authority_receipt_required"
                ]
            )
            for row in rows
        ),
        "no_sessions_created": all(
            not bool(row["session_created"])
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
        "all_prerequisite_hashes_present": all(
            len(row["prerequisite_hash"]) == 64
            for row in rows
        ),
    }


def get_owner_decision_input_handoff_contract_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM owner_input_contracts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 635,
        "title": (
            "Owner Decision Input Handoff Contract Board"
        ),
        "ready": True,
        "contract_count": len(rows),
        "owner_input_contracts": rows,
        "allowed_decision_values": (
            ALLOWED_DECISION_VALUES
        ),
        "required_recording_fields": (
            RECORDING_CONTRACT_FIELDS
        ),
        "all_decision_enums_complete": all(
            row["allowed_decision_count"]
            == len(ALLOWED_DECISION_VALUES)
            for row in rows
        ),
        "all_recording_fields_complete": all(
            row["required_field_count"]
            == len(RECORDING_CONTRACT_FIELDS)
            for row in rows
        ),
        "all_tower_ui_only": all(
            bool(row["tower_ui_only"])
            for row in rows
        ),
        "no_vault_direct_input": all(
            not bool(row["vault_direct_input_allowed"])
            for row in rows
        ),
        "no_teller_direct_input": all(
            not bool(row["teller_direct_input_allowed"])
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
        "all_integrity_requirements_present": all(
            bool(row["decision_reason_required"])
            and bool(row["idempotency_key_required"])
            and bool(row["append_only_required"])
            and not bool(row["mutation_allowed"])
            for row in rows
        ),
        "all_contract_hashes_present": all(
            len(row["contract_hash"]) == 64
            for row in rows
        ),
    }


def get_approval_receipt_reference_handoff_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM approval_reference_handoffs
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 636,
        "title": (
            "Approval and Receipt Reference "
            "Handoff Board"
        ),
        "ready": True,
        "handoff_count": len(rows),
        "approval_reference_handoffs": rows,
        "all_required_references_present": all(
            bool(
                row[
                    "identity_receipt_reference_required"
                ]
            )
            and bool(
                row[
                    "step_up_receipt_reference_required"
                ]
            )
            and bool(
                row[
                    "owner_admin_approval_receipt_required"
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
            and bool(
                row[
                    "exact_scope_hash_reference_required"
                ]
            )
            and bool(
                row[
                    "commit_window_hash_reference_required"
                ]
            )
            for row in rows
        ),
        "no_references_supplied": all(
            row["supplied_reference_count"] == 0
            for row in rows
        ),
        "no_reference_gates_complete": all(
            not bool(row["reference_gate_complete"])
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
        "all_reference_hashes_present": all(
            len(row["reference_handoff_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_handoff_packet_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM handoff_packet_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 637,
        "title": (
            "Tower Owner Decision Handoff "
            "Packet Draft Board"
        ),
        "ready": True,
        "packet_count": len(rows),
        "handoff_packet_drafts": rows,
        "all_source_hashes_present": all(
            len(row["source_closeout_record_hash"]) == 64
            and len(
                row["source_closeout_receipt_hash"]
            )
            == 64
            for row in rows
        ),
        "all_packages_complete": all(
            bool(row["package_complete"])
            for row in rows
        ),
        "all_future_acceptance_eligible": all(
            bool(
                row[
                    "eligible_for_future_tower_acceptance"
                ]
            )
            for row in rows
        ),
        "no_handoffs_delivered": all(
            not bool(row["handoff_delivered"])
            for row in rows
        ),
        "no_handoffs_accepted": all(
            not bool(row["handoff_accepted"])
            for row in rows
        ),
        "no_tower_sessions_created": all(
            not bool(row["tower_session_created"])
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
        "no_recording_gates_open": all(
            not bool(row["recording_gate_open"])
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
        "all_packets_unfinalized": all(
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
        "all_packet_hashes_present": all(
            len(row["packet_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_owner_decision_handoff_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM handoff_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 638,
        "title": (
            "Tower Owner Decision Handoff "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "handoff_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_package_components_recorded": all(
            bool(row["closeout_package_recorded"])
            and bool(row["envelope_contract_recorded"])
            and bool(
                row["session_prerequisites_recorded"]
            )
            and bool(
                row["owner_input_contract_recorded"]
            )
            and bool(
                row["approval_references_recorded"]
            )
            and bool(row["packet_draft_recorded"])
            for row in rows
        ),
        "no_delivery_acceptance_or_session_recorded": all(
            not bool(row["handoff_delivery_recorded"])
            and not bool(
                row["handoff_acceptance_recorded"]
            )
            and not bool(
                row["tower_session_creation_recorded"]
            )
            for row in rows
        ),
        "no_owner_selection_or_decision_recorded": all(
            not bool(row["owner_selection_recorded"])
            and not bool(row["owner_decision_recorded"])
            and not bool(
                row["recording_gate_open_recorded"]
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


def get_tower_handoff_safety_blocker_board(
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
        "gp": 639,
        "title": "Tower Handoff Safety Blocker Board",
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


def get_tower_handoff_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = get_owner_decision_tower_handoff_shell()

    intakes = (
        get_recording_closeout_package_intake_board()
    )

    envelopes = (
        get_tower_handoff_envelope_contract_board()
    )

    sessions = (
        get_tower_owner_review_session_launch_prerequisite_board()
    )

    inputs = (
        get_owner_decision_input_handoff_contract_board()
    )

    approvals = (
        get_approval_receipt_reference_handoff_board()
    )

    packets = (
        get_tower_owner_decision_handoff_packet_draft_board()
    )

    receipts = (
        get_tower_owner_decision_handoff_receipt_draft_ledger()
    )

    blockers = get_tower_handoff_safety_blocker_board()

    checks = {
        "previous_recording_closeout_ready": (
            initialized[
                "previous_recording_closeout_ready"
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
        "handoff_packaging_only": (
            DOCTRINE[
                "tower_handoff_packaging_only"
            ]
            is True
            and DOCTRINE[
                "tower_handoff_delivery_allowed"
            ]
            is False
            and DOCTRINE[
                "tower_handoff_acceptance_allowed"
            ]
            is False
            and DOCTRINE[
                "vault_may_not_collect_owner_input"
            ]
            is True
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "closeout_package_verified": (
            intakes[
                "all_closeout_intakes_verified"
            ]
            is True
            and intakes[
                "all_identity_closeouts_verified"
            ]
            is True
            and intakes[
                "all_approval_closeouts_verified"
            ]
            is True
            and intakes[
                "all_contract_freezes_verified"
            ]
            is True
            and intakes[
                "all_boundaries_verified"
            ]
            is True
            and intakes[
                "all_closeout_records_verified"
            ]
            is True
            and intakes[
                "all_closeout_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_handoff_packaging"
            ]
            is True
        ),
        "handoff_not_delivered_or_accepted": (
            intakes["no_handoffs_delivered"]
            is True
            and intakes["no_handoffs_accepted"]
            is True
        ),

        "envelopes_present": (
            envelopes["envelope_count"] >= 1
        ),
        "envelope_contract_complete": (
            envelopes["all_target_tower"]
            is True
            and envelopes["all_workflows_bound"]
            is True
            and envelopes[
                "all_required_fields_complete"
            ]
            is True
            and envelopes[
                "all_source_hashes_present"
            ]
            is True
            and envelopes["all_tower_only"]
            is True
            and envelopes["all_references_only"]
            is True
            and envelopes[
                "no_raw_material_allowed"
            ]
            is True
        ),
        "envelope_delivery_closed": (
            envelopes["no_delivery_allowed"]
            is True
            and envelopes["no_acceptance_allowed"]
            is True
        ),

        "session_prerequisites_present": (
            sessions["prerequisite_count"] >= 1
        ),
        "session_requirements_complete": (
            sessions[
                "all_session_requirements_present"
            ]
            is True
        ),
        "session_controls_unsatisfied": (
            sessions["no_sessions_created"]
            is True
            and sessions["no_sessions_started"]
            is True
            and sessions[
                "no_owners_authenticated"
            ]
            is True
            and sessions[
                "no_step_up_satisfied"
            ]
            is True
            and sessions[
                "no_prerequisites_complete"
            ]
            is True
        ),

        "input_contracts_present": (
            inputs["contract_count"] >= 1
        ),
        "owner_input_contract_complete": (
            inputs[
                "all_decision_enums_complete"
            ]
            is True
            and inputs[
                "all_recording_fields_complete"
            ]
            is True
            and inputs["all_tower_ui_only"]
            is True
            and inputs["no_vault_direct_input"]
            is True
            and inputs["no_teller_direct_input"]
            is True
            and inputs[
                "all_integrity_requirements_present"
            ]
            is True
        ),
        "owner_input_absent": (
            inputs["no_owner_selections_present"]
            is True
            and inputs[
                "no_owner_decisions_recorded"
            ]
            is True
        ),

        "approval_handoffs_present": (
            approvals["handoff_count"] >= 1
        ),
        "approval_reference_requirements_complete": (
            approvals[
                "all_required_references_present"
            ]
            is True
        ),
        "approval_references_unsupplied": (
            approvals["no_references_supplied"]
            is True
            and approvals[
                "no_reference_gates_complete"
            ]
            is True
            and approvals[
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
        ),

        "packets_present": (
            packets["packet_count"] >= 1
        ),
        "handoff_packet_complete": (
            packets["all_source_hashes_present"]
            is True
            and packets["all_packages_complete"]
            is True
            and packets[
                "all_future_acceptance_eligible"
            ]
            is True
            and packets["all_packets_unfinalized"]
            is True
            and packets["all_append_only"]
            is True
            and packets["all_immutable"]
            is True
        ),
        "packet_actions_not_executed": (
            packets["no_handoffs_delivered"]
            is True
            and packets["no_handoffs_accepted"]
            is True
            and packets[
                "no_tower_sessions_created"
            ]
            is True
            and packets[
                "no_owner_selections_present"
            ]
            is True
            and packets[
                "no_owner_decisions_recorded"
            ]
            is True
            and packets[
                "no_recording_gates_open"
            ]
            is True
            and packets[
                "no_go_decisions_granted"
            ]
            is True
            and packets[
                "no_authorization_or_tokens"
            ]
            is True
            and packets[
                "no_commit_restore_or_write"
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
                "all_package_components_recorded"
            ]
            is True
            and receipts[
                "no_delivery_acceptance_or_session_recorded"
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
                LOCKS["handoff_delivered"]
                is False,
                LOCKS["handoff_accepted"]
                is False,
                LOCKS["tower_session_created"]
                is False,
                LOCKS["review_session_started"]
                is False,
                LOCKS["owner_authenticated"]
                is False,
                LOCKS["step_up_satisfied"]
                is False,
                LOCKS[
                    "owner_admin_approval_granted"
                ]
                is False,
                LOCKS["dual_receipt_satisfied"]
                is False,
                LOCKS[
                    "second_authority_review_granted"
                ]
                is False,
                LOCKS["owner_selection_present"]
                is False,
                LOCKS["owner_decision_recorded"]
                is False,
                LOCKS["recording_gate_open"]
                is False,
                LOCKS["go_decision_granted"]
                is False,
                LOCKS[
                    "live_recovery_authorization_granted"
                ]
                is False,
                LOCKS["authorization_token_issued"]
                is False,
                LOCKS["scope_freeze_activated"]
                is False,
                LOCKS["commit_window_activated"]
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
        "gp": 640,
        "title": "Tower Handoff Readiness Checkpoint",
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else "Owner decision Tower handoff blocked"
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "handoff_status": (
            "sealed_closeout_package_verified_"
            "tower_handoff_packet_ready_"
            "handoff_not_delivered_or_accepted_"
            "owner_decision_absent"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION TOWER HANDOFF "
            "ACCEPTANCE GATE / GP641-GP650"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no live Tower handoff delivery",
            "no Tower handoff acceptance",
            "no Tower owner-review session created",
            "no Tower owner-review session started",
            "no owner authenticated",
            "no step-up satisfied",
            "no owner/admin approval granted",
            "no dual receipt satisfied",
            "no second-authority review granted",
            "no owner selection present",
            "no owner decision recorded",
            "no recording gate open",
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


def get_recovery_commit_owner_decision_tower_handoff_home(
) -> Dict[str, Any]:
    checkpoint = get_tower_handoff_readiness_checkpoint()

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


def validate_recovery_commit_owner_decision_tower_handoff_layer(
) -> Dict[str, Any]:
    checkpoint = get_tower_handoff_readiness_checkpoint()

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

    checkpoint = get_tower_handoff_readiness_checkpoint()

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
        "handoff_delivered": False,
        "handoff_accepted": False,
        "tower_session_created": False,
        "owner_authenticated": False,
        "owner_selection_present": False,
        "owner_decision_recorded": False,
        "recording_gate_open": False,
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


def get_gp631_status():
    return _gp_status(631)


def get_gp632_status():
    return _gp_status(632)


def get_gp633_status():
    return _gp_status(633)


def get_gp634_status():
    return _gp_status(634)


def get_gp635_status():
    return _gp_status(635)


def get_gp636_status():
    return _gp_status(636)


def get_gp637_status():
    return _gp_status(637)


def get_gp638_status():
    return _gp_status(638)


def get_gp639_status():
    return _gp_status(639)


def get_gp640_status():
    return _gp_status(640)
