
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER DECISION "
    "TOWER HANDOFF ACCEPTANCE CLOSEOUT LAYER / GP651-GP660"
)

LAYER_ID = (
    "vault_gp651_660_"
    "recovery_commit_owner_decision_tower_handoff_acceptance_closeout"
)

READINESS_LABEL = (
    "Tower handoff acceptance closeout ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_ACCEPTANCE_CLOSEOUT_SEALED"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_tower_handoff_acceptance_closeout.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_owner_decision_tower_handoff_acceptance_gate_service import (
        ACCEPTANCE_CONTRACT_FIELDS,
        ACCEPTANCE_DECISIONS,
        get_tower_handoff_packet_intake_verification_board,
        get_tower_handoff_acceptance_authority_contract_board,
        get_tower_acceptance_session_prerequisite_board,
        get_tower_handoff_acceptance_evidence_reference_gate,
        get_tower_handoff_acceptance_decision_contract_board,
        get_tower_handoff_acceptance_record_draft_board,
        get_tower_handoff_acceptance_receipt_draft_ledger,
        validate_recovery_commit_owner_decision_tower_handoff_acceptance_gate,
    )
except Exception as exc:
    raise RuntimeError(
        "GP651-GP660 requires the completed "
        "GP641-GP650 Tower handoff acceptance gate."
    ) from exc


_INIT_CACHE = None


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "acceptance_closeout_only": True,
    "acceptance_requirements_may_be_sealed": True,
    "acceptance_execution_allowed": False,
    "tower_is_only_handoff_acceptance_authority": True,
    "vault_cannot_accept_its_own_handoff": True,
    "teller_cannot_accept_vault_handoff": True,
    "owner_decision_is_separate_from_handoff_acceptance": True,
    "current_recommendation": CURRENT_RECOMMENDATION,
    "handoff_delivered": False,
    "handoff_accepted": False,
    "acceptance_decision_recorded": False,
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
    "acceptance_closeout_layer": True,
    "acceptance_evidence_closeout_allowed": True,
    "authority_requirement_closeout_allowed": True,
    "session_requirement_closeout_allowed": True,
    "evidence_requirement_freeze_allowed": True,
    "decision_contract_freeze_allowed": True,
    "acceptance_closeout_record_drafts_allowed": True,
    "acceptance_closeout_receipt_drafts_allowed": True,

    "handoff_delivered": False,
    "handoff_accepted": False,
    "acceptance_decision_recorded": False,
    "acceptance_gate_open": False,
    "acceptance_execution_allowed": False,

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

    "teller_direct_acceptance_allowed": False,
    "teller_direct_recording_allowed": False,
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
        "gp": 651,
        "title": (
            "Tower Handoff Acceptance Closeout Shell"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-"
            "closeout-shell.json"
        ),
    },
    {
        "gp": 652,
        "title": (
            "Acceptance Gate Evidence Closeout "
            "Intake Board"
        ),
        "route": (
            "/vault/acceptance-gate-evidence-"
            "closeout-intake-board.json"
        ),
    },
    {
        "gp": 653,
        "title": (
            "Tower Acceptance Authority Requirement "
            "Closeout Board"
        ),
        "route": (
            "/vault/tower-acceptance-authority-"
            "requirement-closeout-board.json"
        ),
    },
    {
        "gp": 654,
        "title": (
            "Tower Acceptance Session Requirement "
            "Closeout Board"
        ),
        "route": (
            "/vault/tower-acceptance-session-"
            "requirement-closeout-board.json"
        ),
    },
    {
        "gp": 655,
        "title": (
            "Acceptance Evidence Reference Requirement "
            "Freeze Board"
        ),
        "route": (
            "/vault/acceptance-evidence-reference-"
            "requirement-freeze-board.json"
        ),
    },
    {
        "gp": 656,
        "title": (
            "Tower Acceptance Decision Contract "
            "Freeze Board"
        ),
        "route": (
            "/vault/tower-acceptance-decision-"
            "contract-freeze-board.json"
        ),
    },
    {
        "gp": 657,
        "title": (
            "Tower Acceptance Closeout "
            "Record Draft Board"
        ),
        "route": (
            "/vault/tower-acceptance-closeout-"
            "record-draft-board.json"
        ),
    },
    {
        "gp": 658,
        "title": (
            "Tower Acceptance Closeout "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-acceptance-closeout-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 659,
        "title": (
            "Tower Acceptance Closeout "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/tower-acceptance-closeout-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 660,
        "title": (
            "Tower Acceptance Closeout "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/tower-acceptance-"
            "closeout-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_handoff_delivery",
        "live_handoff_delivery",
        "Acceptance closeout cannot deliver the handoff.",
    ),
    (
        "no_handoff_acceptance",
        "live_handoff_acceptance",
        "Vault cannot accept its own handoff.",
    ),
    (
        "no_acceptance_decision",
        "acceptance_decision_recording",
        "Closeout seals the contract but records no decision.",
    ),
    (
        "no_tower_session_creation",
        "tower_session_creation",
        "Vault cannot create a Tower acceptance session.",
    ),
    (
        "no_owner_review_session_start",
        "owner_review_session_start",
        "Tower must control any later owner session.",
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
        "no_owner_input",
        "owner_input_collection",
        "Vault cannot collect owner input.",
    ),
    (
        "no_owner_decision",
        "owner_decision_recording",
        "Acceptance closeout is not an owner decision.",
    ),
    (
        "no_recording_gate_open",
        "recording_gate_open",
        "The owner-decision recording gate remains closed.",
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
        "no_restore",
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
        "no_teller_direct_acceptance",
        "teller_direct_acceptance",
        "Teller cannot accept Vault handoffs.",
    ),
    (
        "no_prohibited_person_access",
        "prohibited_person_vault_access",
        "Residents, vendors, employees, and customers cannot enter Vault.",
    ),
    (
        "no_public_access",
        "public_vault_access",
        "Vault has no public access path.",
    ),
    (
        "no_raw_material",
        "raw_bytes_paths_urls_or_tokens",
        "Closeout stores references and hashes only.",
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
        get_tower_handoff_packet_intake_verification_board()
        .get("acceptance_intakes", [])
    )

    authority_rows = (
        get_tower_handoff_acceptance_authority_contract_board()
        .get("acceptance_authority_contracts", [])
    )

    session_rows = (
        get_tower_acceptance_session_prerequisite_board()
        .get("acceptance_session_prerequisites", [])
    )

    evidence_rows = (
        get_tower_handoff_acceptance_evidence_reference_gate()
        .get("acceptance_evidence_gates", [])
    )

    decision_rows = (
        get_tower_handoff_acceptance_decision_contract_board()
        .get("acceptance_decision_contracts", [])
    )

    record_rows = (
        get_tower_handoff_acceptance_record_draft_board()
        .get("acceptance_record_drafts", [])
    )

    receipt_rows = (
        get_tower_handoff_acceptance_receipt_draft_ledger()
        .get("acceptance_receipt_drafts", [])
    )

    authorities = _by_request(authority_rows)
    sessions = _by_request(session_rows)
    evidence = _by_request(evidence_rows)
    decisions = _by_request(decision_rows)
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
                "authority": authorities.get(
                    request_id,
                    {},
                ),
                "session": sessions.get(
                    request_id,
                    {},
                ),
                "evidence": evidence.get(
                    request_id,
                    {},
                ),
                "decision": decisions.get(
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
        validate_recovery_commit_owner_decision_tower_handoff_acceptance_gate()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS closeout_intakes (
                closeout_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                acceptance_intake_verified INTEGER NOT NULL,
                authority_contract_verified INTEGER NOT NULL,
                session_contract_verified INTEGER NOT NULL,
                evidence_gate_verified INTEGER NOT NULL,
                decision_contract_verified INTEGER NOT NULL,
                acceptance_record_verified INTEGER NOT NULL,
                acceptance_receipt_verified INTEGER NOT NULL,
                eligible_for_acceptance_closeout INTEGER NOT NULL,
                handoff_delivered INTEGER NOT NULL,
                handoff_accepted INTEGER NOT NULL,
                acceptance_decision_recorded INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS authority_closeouts (
                authority_closeout_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requirements_sealed INTEGER NOT NULL,
                target_service TEXT NOT NULL,
                tower_identity_required INTEGER NOT NULL,
                tower_permission_required INTEGER NOT NULL,
                tower_clearance_required INTEGER NOT NULL,
                tower_step_up_required INTEGER NOT NULL,
                exact_handoff_hash_binding_required INTEGER NOT NULL,
                acceptance_action_scope_required INTEGER NOT NULL,
                vault_acceptance_authority INTEGER NOT NULL,
                teller_acceptance_authority INTEGER NOT NULL,
                acceptance_authority_granted INTEGER NOT NULL,
                source_authority_contract_hash TEXT NOT NULL,
                closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS session_closeouts (
                session_closeout_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requirements_sealed INTEGER NOT NULL,
                tower_acceptance_session_required INTEGER NOT NULL,
                tower_actor_reference_required INTEGER NOT NULL,
                tower_identity_receipt_required INTEGER NOT NULL,
                tower_permission_receipt_required INTEGER NOT NULL,
                tower_clearance_receipt_required INTEGER NOT NULL,
                tower_step_up_receipt_required INTEGER NOT NULL,
                source_packet_hash_required INTEGER NOT NULL,
                session_created INTEGER NOT NULL,
                session_started INTEGER NOT NULL,
                prerequisite_complete INTEGER NOT NULL,
                source_prerequisite_hash TEXT NOT NULL,
                closeout_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evidence_requirement_freezes (
                evidence_freeze_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                requirements_frozen INTEGER NOT NULL,
                envelope_hash_required INTEGER NOT NULL,
                packet_hash_required INTEGER NOT NULL,
                receipt_hash_required INTEGER NOT NULL,
                identity_receipt_required INTEGER NOT NULL,
                permission_receipt_required INTEGER NOT NULL,
                clearance_receipt_required INTEGER NOT NULL,
                step_up_receipt_required INTEGER NOT NULL,
                idempotency_key_required INTEGER NOT NULL,
                supplied_reference_count INTEGER NOT NULL,
                evidence_gate_complete INTEGER NOT NULL,
                source_evidence_gate_hash TEXT NOT NULL,
                freeze_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_contract_freezes (
                decision_freeze_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                contract_frozen INTEGER NOT NULL,
                allowed_decisions_json TEXT NOT NULL,
                required_fields_json TEXT NOT NULL,
                allowed_decision_count INTEGER NOT NULL,
                required_field_count INTEGER NOT NULL,
                tower_only INTEGER NOT NULL,
                selected_acceptance_decision_present INTEGER NOT NULL,
                acceptance_decision_recorded INTEGER NOT NULL,
                owner_decision_recorded INTEGER NOT NULL,
                append_only_required INTEGER NOT NULL,
                mutation_allowed INTEGER NOT NULL,
                raw_material_allowed INTEGER NOT NULL,
                source_decision_contract_hash TEXT NOT NULL,
                freeze_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS closeout_record_drafts (
                closeout_record_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                authority_closeout_id TEXT NOT NULL,
                session_closeout_id TEXT NOT NULL,
                evidence_freeze_id TEXT NOT NULL,
                decision_freeze_id TEXT NOT NULL,
                source_acceptance_record_hash TEXT NOT NULL,
                source_acceptance_receipt_hash TEXT NOT NULL,
                closeout_package_complete INTEGER NOT NULL,
                eligible_for_future_delivery_preparation INTEGER NOT NULL,
                handoff_delivered INTEGER NOT NULL,
                handoff_accepted INTEGER NOT NULL,
                acceptance_decision_recorded INTEGER NOT NULL,
                tower_session_created INTEGER NOT NULL,
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
                closeout_record_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS closeout_receipt_drafts (
                closeout_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                closeout_record_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                acceptance_gate_evidence_recorded INTEGER NOT NULL,
                authority_closeout_recorded INTEGER NOT NULL,
                session_closeout_recorded INTEGER NOT NULL,
                evidence_freeze_recorded INTEGER NOT NULL,
                decision_freeze_recorded INTEGER NOT NULL,
                closeout_record_draft_recorded INTEGER NOT NULL,
                handoff_delivery_recorded INTEGER NOT NULL,
                handoff_acceptance_recorded INTEGER NOT NULL,
                acceptance_decision_recorded INTEGER NOT NULL,
                tower_session_creation_recorded INTEGER NOT NULL,
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
            "closeout_intakes",
            "authority_closeouts",
            "session_closeouts",
            "evidence_requirement_freezes",
            "decision_contract_freezes",
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
            authority = source["authority"]
            session = source["session"]
            evidence = source["evidence"]
            decision = source["decision"]
            record = source["record"]
            receipt = source["receipt"]

            acceptance_intake_verified = all(
                [
                    bool(
                        intake.get(
                            "handoff_intake_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "envelope_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "session_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "owner_input_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "approval_reference_contract_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "handoff_packet_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "handoff_receipt_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "eligible_for_acceptance_gate_review",
                            0,
                        )
                    ),
                    not bool(
                        intake.get(
                            "handoff_delivered",
                            1,
                        )
                    ),
                    not bool(
                        intake.get(
                            "handoff_accepted",
                            1,
                        )
                    ),
                ]
            )

            authority_contract_verified = all(
                [
                    authority.get(
                        "target_service"
                    )
                    == "tower",
                    bool(
                        authority.get(
                            "tower_identity_required",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "tower_permission_required",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "tower_clearance_required",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "tower_step_up_required",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "exact_handoff_hash_binding_required",
                            0,
                        )
                    ),
                    bool(
                        authority.get(
                            "acceptance_action_scope_required",
                            0,
                        )
                    ),
                    not bool(
                        authority.get(
                            "vault_acceptance_authority",
                            1,
                        )
                    ),
                    not bool(
                        authority.get(
                            "teller_acceptance_authority",
                            1,
                        )
                    ),
                    not bool(
                        authority.get(
                            "acceptance_authority_granted",
                            1,
                        )
                    ),
                    len(
                        authority.get(
                            "authority_contract_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            session_contract_verified = all(
                [
                    bool(
                        session.get(
                            "tower_acceptance_session_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "tower_actor_reference_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "tower_identity_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "tower_permission_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "tower_clearance_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "tower_step_up_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "source_packet_hash_required",
                            0,
                        )
                    ),
                    not bool(
                        session.get(
                            "session_created",
                            1,
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
                            "prerequisite_complete",
                            1,
                        )
                    ),
                    len(
                        session.get(
                            "prerequisite_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            evidence_gate_verified = all(
                [
                    bool(
                        evidence.get(
                            "envelope_hash_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "packet_hash_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "receipt_hash_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "identity_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "permission_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "clearance_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "step_up_receipt_required",
                            0,
                        )
                    ),
                    bool(
                        evidence.get(
                            "idempotency_key_required",
                            0,
                        )
                    ),
                    int(
                        evidence.get(
                            "supplied_reference_count",
                            -1,
                        )
                    )
                    == 0,
                    not bool(
                        evidence.get(
                            "evidence_gate_complete",
                            1,
                        )
                    ),
                    len(
                        evidence.get(
                            "evidence_gate_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            decision_contract_verified = all(
                [
                    int(
                        decision.get(
                            "allowed_decision_count",
                            0,
                        )
                    )
                    == len(ACCEPTANCE_DECISIONS),
                    int(
                        decision.get(
                            "required_field_count",
                            0,
                        )
                    )
                    == len(ACCEPTANCE_CONTRACT_FIELDS),
                    bool(
                        decision.get(
                            "tower_only",
                            0,
                        )
                    ),
                    not bool(
                        decision.get(
                            "selected_acceptance_decision_present",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "acceptance_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    bool(
                        decision.get(
                            "append_only_required",
                            0,
                        )
                    ),
                    not bool(
                        decision.get(
                            "mutation_allowed",
                            1,
                        )
                    ),
                    not bool(
                        decision.get(
                            "raw_material_allowed",
                            1,
                        )
                    ),
                    len(
                        decision.get(
                            "decision_contract_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            acceptance_record_verified = all(
                [
                    len(
                        record.get(
                            "source_envelope_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        record.get(
                            "source_packet_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        record.get(
                            "source_receipt_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        record.get(
                            "acceptance_contract_complete",
                            0,
                        )
                    ),
                    not bool(
                        record.get(
                            "handoff_delivered",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "handoff_accepted",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "acceptance_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        record.get(
                            "tower_session_created",
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
                            "recording_gate_open",
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
                            "acceptance_record_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            acceptance_receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "source_handoff_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "authority_contract_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "session_prerequisites_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "evidence_requirements_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "decision_contract_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "acceptance_record_draft_recorded",
                            0,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "handoff_delivery_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "handoff_acceptance_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "acceptance_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        receipt.get(
                            "tower_session_creation_recorded",
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
                            "recording_gate_open_recorded",
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
                    acceptance_intake_verified,
                    authority_contract_verified,
                    session_contract_verified,
                    evidence_gate_verified,
                    decision_contract_verified,
                    acceptance_record_verified,
                    acceptance_receipt_verified,
                ]
            )

            closeout_intake_id = _id(
                "acceptance_closeout_intake",
                request_id,
            )

            authority_closeout_id = _id(
                "acceptance_authority_closeout",
                request_id,
            )

            session_closeout_id = _id(
                "acceptance_session_closeout",
                request_id,
            )

            evidence_freeze_id = _id(
                "acceptance_evidence_freeze",
                request_id,
            )

            decision_freeze_id = _id(
                "acceptance_decision_freeze",
                request_id,
            )

            closeout_record_id = _id(
                "acceptance_closeout_record",
                request_id,
            )

            closeout_receipt_id = _id(
                "acceptance_closeout_receipt",
                request_id,
            )

            _insert_row(
                connection,
                "closeout_intakes",
                {
                    "closeout_intake_id": (
                        closeout_intake_id
                    ),
                    "request_id": request_id,
                    "workflow_type": workflow_type,
                    "state": (
                        "acceptance_gate_evidence_verified_"
                        "eligible_for_closeout"
                    ),
                    "acceptance_intake_verified": int(
                        acceptance_intake_verified
                    ),
                    "authority_contract_verified": int(
                        authority_contract_verified
                    ),
                    "session_contract_verified": int(
                        session_contract_verified
                    ),
                    "evidence_gate_verified": int(
                        evidence_gate_verified
                    ),
                    "decision_contract_verified": int(
                        decision_contract_verified
                    ),
                    "acceptance_record_verified": int(
                        acceptance_record_verified
                    ),
                    "acceptance_receipt_verified": int(
                        acceptance_receipt_verified
                    ),
                    "eligible_for_acceptance_closeout": int(
                        eligible_for_closeout
                    ),
                    "handoff_delivered": 0,
                    "handoff_accepted": 0,
                    "acceptance_decision_recorded": 0,
                    "created_at": now,
                },
            )

            authority_payload = {
                "request_id": request_id,
                "requirements_sealed": True,
                "target_service": "tower",
                "tower_identity_required": True,
                "tower_permission_required": True,
                "tower_clearance_required": True,
                "tower_step_up_required": True,
                "exact_handoff_hash_binding_required": True,
                "acceptance_action_scope_required": True,
                "vault_acceptance_authority": False,
                "teller_acceptance_authority": False,
                "acceptance_authority_granted": False,
                "source_authority_contract_hash": (
                    authority.get(
                        "authority_contract_hash",
                        "",
                    )
                ),
            }

            authority_closeout_hash = _canonical_hash(
                authority_payload
            )

            _insert_row(
                connection,
                "authority_closeouts",
                {
                    "authority_closeout_id": (
                        authority_closeout_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_acceptance_authority_"
                        "requirements_sealed_not_granted"
                    ),
                    "requirements_sealed": 1,
                    "target_service": "tower",
                    "tower_identity_required": 1,
                    "tower_permission_required": 1,
                    "tower_clearance_required": 1,
                    "tower_step_up_required": 1,
                    "exact_handoff_hash_binding_required": 1,
                    "acceptance_action_scope_required": 1,
                    "vault_acceptance_authority": 0,
                    "teller_acceptance_authority": 0,
                    "acceptance_authority_granted": 0,
                    "source_authority_contract_hash": (
                        authority.get(
                            "authority_contract_hash",
                            "",
                        )
                    ),
                    "closeout_hash": (
                        authority_closeout_hash
                    ),
                    "created_at": now,
                },
            )

            session_payload = {
                "request_id": request_id,
                "requirements_sealed": True,
                "tower_acceptance_session_required": True,
                "tower_actor_reference_required": True,
                "tower_identity_receipt_required": True,
                "tower_permission_receipt_required": True,
                "tower_clearance_receipt_required": True,
                "tower_step_up_receipt_required": True,
                "source_packet_hash_required": True,
                "session_created": False,
                "session_started": False,
                "prerequisite_complete": False,
                "source_prerequisite_hash": session.get(
                    "prerequisite_hash",
                    "",
                ),
            }

            session_closeout_hash = _canonical_hash(
                session_payload
            )

            _insert_row(
                connection,
                "session_closeouts",
                {
                    "session_closeout_id": (
                        session_closeout_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_acceptance_session_"
                        "requirements_sealed_not_satisfied"
                    ),
                    "requirements_sealed": 1,
                    "tower_acceptance_session_required": 1,
                    "tower_actor_reference_required": 1,
                    "tower_identity_receipt_required": 1,
                    "tower_permission_receipt_required": 1,
                    "tower_clearance_receipt_required": 1,
                    "tower_step_up_receipt_required": 1,
                    "source_packet_hash_required": 1,
                    "session_created": 0,
                    "session_started": 0,
                    "prerequisite_complete": 0,
                    "source_prerequisite_hash": session.get(
                        "prerequisite_hash",
                        "",
                    ),
                    "closeout_hash": (
                        session_closeout_hash
                    ),
                    "created_at": now,
                },
            )

            evidence_payload = {
                "request_id": request_id,
                "requirements_frozen": True,
                "envelope_hash_required": True,
                "packet_hash_required": True,
                "receipt_hash_required": True,
                "identity_receipt_required": True,
                "permission_receipt_required": True,
                "clearance_receipt_required": True,
                "step_up_receipt_required": True,
                "idempotency_key_required": True,
                "supplied_reference_count": 0,
                "evidence_gate_complete": False,
                "source_evidence_gate_hash": evidence.get(
                    "evidence_gate_hash",
                    "",
                ),
            }

            evidence_freeze_hash = _canonical_hash(
                evidence_payload
            )

            _insert_row(
                connection,
                "evidence_requirement_freezes",
                {
                    "evidence_freeze_id": (
                        evidence_freeze_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "acceptance_evidence_requirements_"
                        "frozen_none_supplied"
                    ),
                    "requirements_frozen": 1,
                    "envelope_hash_required": 1,
                    "packet_hash_required": 1,
                    "receipt_hash_required": 1,
                    "identity_receipt_required": 1,
                    "permission_receipt_required": 1,
                    "clearance_receipt_required": 1,
                    "step_up_receipt_required": 1,
                    "idempotency_key_required": 1,
                    "supplied_reference_count": 0,
                    "evidence_gate_complete": 0,
                    "source_evidence_gate_hash": (
                        evidence.get(
                            "evidence_gate_hash",
                            "",
                        )
                    ),
                    "freeze_hash": (
                        evidence_freeze_hash
                    ),
                    "created_at": now,
                },
            )

            decision_payload = {
                "request_id": request_id,
                "contract_frozen": True,
                "allowed_decisions": ACCEPTANCE_DECISIONS,
                "required_fields": ACCEPTANCE_CONTRACT_FIELDS,
                "tower_only": True,
                "selected_acceptance_decision_present": False,
                "acceptance_decision_recorded": False,
                "owner_decision_recorded": False,
                "append_only_required": True,
                "mutation_allowed": False,
                "raw_material_allowed": False,
                "source_decision_contract_hash": decision.get(
                    "decision_contract_hash",
                    "",
                ),
            }

            decision_freeze_hash = _canonical_hash(
                decision_payload
            )

            _insert_row(
                connection,
                "decision_contract_freezes",
                {
                    "decision_freeze_id": (
                        decision_freeze_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_acceptance_decision_"
                        "contract_frozen_no_selection"
                    ),
                    "contract_frozen": 1,
                    "allowed_decisions_json": json.dumps(
                        ACCEPTANCE_DECISIONS,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "required_fields_json": json.dumps(
                        ACCEPTANCE_CONTRACT_FIELDS,
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    "allowed_decision_count": len(
                        ACCEPTANCE_DECISIONS
                    ),
                    "required_field_count": len(
                        ACCEPTANCE_CONTRACT_FIELDS
                    ),
                    "tower_only": 1,
                    "selected_acceptance_decision_present": 0,
                    "acceptance_decision_recorded": 0,
                    "owner_decision_recorded": 0,
                    "append_only_required": 1,
                    "mutation_allowed": 0,
                    "raw_material_allowed": 0,
                    "source_decision_contract_hash": (
                        decision.get(
                            "decision_contract_hash",
                            "",
                        )
                    ),
                    "freeze_hash": (
                        decision_freeze_hash
                    ),
                    "created_at": now,
                },
            )

            closeout_record_payload = {
                "request_id": request_id,
                "authority_closeout_id": (
                    authority_closeout_id
                ),
                "session_closeout_id": (
                    session_closeout_id
                ),
                "evidence_freeze_id": (
                    evidence_freeze_id
                ),
                "decision_freeze_id": (
                    decision_freeze_id
                ),
                "source_acceptance_record_hash": record.get(
                    "acceptance_record_hash",
                    "",
                ),
                "source_acceptance_receipt_hash": receipt.get(
                    "receipt_hash",
                    "",
                ),
                "closeout_package_complete": True,
                "eligible_for_future_delivery_preparation": True,
                "handoff_delivered": False,
                "handoff_accepted": False,
                "acceptance_decision_recorded": False,
                "tower_session_created": False,
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
                        "tower_acceptance_closeout_"
                        "record_draft_complete"
                    ),
                    "authority_closeout_id": (
                        authority_closeout_id
                    ),
                    "session_closeout_id": (
                        session_closeout_id
                    ),
                    "evidence_freeze_id": (
                        evidence_freeze_id
                    ),
                    "decision_freeze_id": (
                        decision_freeze_id
                    ),
                    "source_acceptance_record_hash": (
                        record.get(
                            "acceptance_record_hash",
                            "",
                        )
                    ),
                    "source_acceptance_receipt_hash": (
                        receipt.get(
                            "receipt_hash",
                            "",
                        )
                    ),
                    "closeout_package_complete": 1,
                    "eligible_for_future_delivery_preparation": 1,
                    "handoff_delivered": 0,
                    "handoff_accepted": 0,
                    "acceptance_decision_recorded": 0,
                    "tower_session_created": 0,
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
                    "closeout_record_hash": (
                        closeout_record_hash
                    ),
                    "created_at": now,
                },
            )

            closeout_receipt_payload = {
                "request_id": request_id,
                "closeout_record_id": closeout_record_id,
                "acceptance_gate_evidence_recorded": True,
                "authority_closeout_recorded": True,
                "session_closeout_recorded": True,
                "evidence_freeze_recorded": True,
                "decision_freeze_recorded": True,
                "closeout_record_draft_recorded": True,
                "handoff_delivery_recorded": False,
                "handoff_acceptance_recorded": False,
                "acceptance_decision_recorded": False,
                "tower_session_creation_recorded": False,
                "owner_decision_recorded": False,
                "recording_gate_open_recorded": False,
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
                        "tower_acceptance_closeout_"
                        "receipt_draft"
                    ),
                    "tower_controlled": 1,
                    "acceptance_gate_evidence_recorded": 1,
                    "authority_closeout_recorded": 1,
                    "session_closeout_recorded": 1,
                    "evidence_freeze_recorded": 1,
                    "decision_freeze_recorded": 1,
                    "closeout_record_draft_recorded": 1,
                    "handoff_delivery_recorded": 0,
                    "handoff_acceptance_recorded": 0,
                    "acceptance_decision_recorded": 0,
                    "tower_session_creation_recorded": 0,
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
                    "receipt_hash": (
                        closeout_receipt_hash
                    ),
                    "created_at": now,
                },
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_acceptance_gate_ready": bool(
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


def get_tower_handoff_acceptance_closeout_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 651,
        "title": (
            "Tower Handoff Acceptance Closeout Shell"
        ),
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "acceptance_closeout_only": True,
        "acceptance_requirements_sealed": True,
        "handoff_delivered": False,
        "handoff_accepted": False,
        "acceptance_decision_recorded": False,
        "tower_session_created": False,
        "owner_decision_recorded": False,
        "recording_gate_open": False,
        "go_decision_granted": False,
        "live_authorization_granted": False,
        "commit_point_open": False,
        "actual_restore_execution_allowed": False,
        "production_recovery_write_allowed": False,
    }


def get_acceptance_gate_evidence_closeout_intake_board(
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
        "gp": 652,
        "title": (
            "Acceptance Gate Evidence Closeout "
            "Intake Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "closeout_intakes": rows,
        "all_acceptance_intakes_verified": all(
            bool(row["acceptance_intake_verified"])
            for row in rows
        ),
        "all_authority_contracts_verified": all(
            bool(row["authority_contract_verified"])
            for row in rows
        ),
        "all_session_contracts_verified": all(
            bool(row["session_contract_verified"])
            for row in rows
        ),
        "all_evidence_gates_verified": all(
            bool(row["evidence_gate_verified"])
            for row in rows
        ),
        "all_decision_contracts_verified": all(
            bool(row["decision_contract_verified"])
            for row in rows
        ),
        "all_acceptance_records_verified": all(
            bool(row["acceptance_record_verified"])
            for row in rows
        ),
        "all_acceptance_receipts_verified": all(
            bool(row["acceptance_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_closeout": all(
            bool(
                row[
                    "eligible_for_acceptance_closeout"
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
        "no_acceptance_decisions_recorded": all(
            not bool(
                row["acceptance_decision_recorded"]
            )
            for row in rows
        ),
    }


def get_tower_acceptance_authority_requirement_closeout_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM authority_closeouts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 653,
        "title": (
            "Tower Acceptance Authority Requirement "
            "Closeout Board"
        ),
        "ready": True,
        "closeout_count": len(rows),
        "authority_closeouts": rows,
        "all_requirements_sealed": all(
            bool(row["requirements_sealed"])
            for row in rows
        ),
        "all_target_tower": all(
            row["target_service"] == "tower"
            for row in rows
        ),
        "all_tower_controls_required": all(
            bool(row["tower_identity_required"])
            and bool(row["tower_permission_required"])
            and bool(row["tower_clearance_required"])
            and bool(row["tower_step_up_required"])
            and bool(
                row[
                    "exact_handoff_hash_binding_required"
                ]
            )
            and bool(
                row[
                    "acceptance_action_scope_required"
                ]
            )
            for row in rows
        ),
        "no_vault_acceptance_authority": all(
            not bool(row["vault_acceptance_authority"])
            for row in rows
        ),
        "no_teller_acceptance_authority": all(
            not bool(
                row["teller_acceptance_authority"]
            )
            for row in rows
        ),
        "no_acceptance_authority_granted": all(
            not bool(
                row["acceptance_authority_granted"]
            )
            for row in rows
        ),
        "all_source_hashes_present": all(
            len(
                row["source_authority_contract_hash"]
            )
            == 64
            for row in rows
        ),
        "all_closeout_hashes_present": all(
            len(row["closeout_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_acceptance_session_requirement_closeout_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM session_closeouts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 654,
        "title": (
            "Tower Acceptance Session Requirement "
            "Closeout Board"
        ),
        "ready": True,
        "closeout_count": len(rows),
        "session_closeouts": rows,
        "all_requirements_sealed": all(
            bool(row["requirements_sealed"])
            for row in rows
        ),
        "all_session_requirements_present": all(
            bool(
                row[
                    "tower_acceptance_session_required"
                ]
            )
            and bool(
                row["tower_actor_reference_required"]
            )
            and bool(
                row["tower_identity_receipt_required"]
            )
            and bool(
                row["tower_permission_receipt_required"]
            )
            and bool(
                row["tower_clearance_receipt_required"]
            )
            and bool(
                row["tower_step_up_receipt_required"]
            )
            and bool(
                row["source_packet_hash_required"]
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


def get_acceptance_evidence_reference_requirement_freeze_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM evidence_requirement_freezes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 655,
        "title": (
            "Acceptance Evidence Reference Requirement "
            "Freeze Board"
        ),
        "ready": True,
        "freeze_count": len(rows),
        "evidence_requirement_freezes": rows,
        "all_requirements_frozen": all(
            bool(row["requirements_frozen"])
            for row in rows
        ),
        "all_reference_requirements_present": all(
            bool(row["envelope_hash_required"])
            and bool(row["packet_hash_required"])
            and bool(row["receipt_hash_required"])
            and bool(row["identity_receipt_required"])
            and bool(row["permission_receipt_required"])
            and bool(row["clearance_receipt_required"])
            and bool(row["step_up_receipt_required"])
            and bool(row["idempotency_key_required"])
            for row in rows
        ),
        "no_references_supplied": all(
            row["supplied_reference_count"] == 0
            for row in rows
        ),
        "no_evidence_gates_complete": all(
            not bool(row["evidence_gate_complete"])
            for row in rows
        ),
        "all_source_hashes_present": all(
            len(row["source_evidence_gate_hash"]) == 64
            for row in rows
        ),
        "all_freeze_hashes_present": all(
            len(row["freeze_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_acceptance_decision_contract_freeze_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM decision_contract_freezes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 656,
        "title": (
            "Tower Acceptance Decision Contract "
            "Freeze Board"
        ),
        "ready": True,
        "freeze_count": len(rows),
        "decision_contract_freezes": rows,
        "allowed_acceptance_decisions": (
            ACCEPTANCE_DECISIONS
        ),
        "required_acceptance_fields": (
            ACCEPTANCE_CONTRACT_FIELDS
        ),
        "all_contracts_frozen": all(
            bool(row["contract_frozen"])
            for row in rows
        ),
        "all_decision_enums_complete": all(
            row["allowed_decision_count"]
            == len(ACCEPTANCE_DECISIONS)
            for row in rows
        ),
        "all_required_fields_complete": all(
            row["required_field_count"]
            == len(ACCEPTANCE_CONTRACT_FIELDS)
            for row in rows
        ),
        "all_tower_only": all(
            bool(row["tower_only"])
            for row in rows
        ),
        "no_acceptance_selections_present": all(
            not bool(
                row[
                    "selected_acceptance_decision_present"
                ]
            )
            for row in rows
        ),
        "no_acceptance_decisions_recorded": all(
            not bool(
                row["acceptance_decision_recorded"]
            )
            for row in rows
        ),
        "no_owner_decisions_recorded": all(
            not bool(row["owner_decision_recorded"])
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
            len(
                row["source_decision_contract_hash"]
            )
            == 64
            for row in rows
        ),
        "all_freeze_hashes_present": all(
            len(row["freeze_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_acceptance_closeout_record_draft_board(
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
        "gp": 657,
        "title": (
            "Tower Acceptance Closeout "
            "Record Draft Board"
        ),
        "ready": True,
        "record_count": len(rows),
        "closeout_record_drafts": rows,
        "all_source_hashes_present": all(
            len(
                row["source_acceptance_record_hash"]
            )
            == 64
            and len(
                row["source_acceptance_receipt_hash"]
            )
            == 64
            for row in rows
        ),
        "all_closeout_packages_complete": all(
            bool(row["closeout_package_complete"])
            for row in rows
        ),
        "all_future_delivery_preparation_eligible": all(
            bool(
                row[
                    "eligible_for_future_delivery_preparation"
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
        "no_acceptance_decisions_recorded": all(
            not bool(
                row["acceptance_decision_recorded"]
            )
            for row in rows
        ),
        "no_tower_sessions_created": all(
            not bool(row["tower_session_created"])
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
        "all_record_hashes_present": all(
            len(row["closeout_record_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_acceptance_closeout_receipt_draft_ledger(
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
        "gp": 658,
        "title": (
            "Tower Acceptance Closeout "
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
                    "acceptance_gate_evidence_recorded"
                ]
            )
            and bool(
                row["authority_closeout_recorded"]
            )
            and bool(
                row["session_closeout_recorded"]
            )
            and bool(
                row["evidence_freeze_recorded"]
            )
            and bool(
                row["decision_freeze_recorded"]
            )
            and bool(
                row[
                    "closeout_record_draft_recorded"
                ]
            )
            for row in rows
        ),
        "no_delivery_acceptance_or_session_recorded": all(
            not bool(row["handoff_delivery_recorded"])
            and not bool(
                row["handoff_acceptance_recorded"]
            )
            and not bool(
                row["acceptance_decision_recorded"]
            )
            and not bool(
                row["tower_session_creation_recorded"]
            )
            for row in rows
        ),
        "no_owner_or_recovery_actions_recorded": all(
            not bool(row["owner_decision_recorded"])
            and not bool(
                row["recording_gate_open_recorded"]
            )
            and not bool(row["go_decision_recorded"])
            and not bool(
                row["live_authorization_recorded"]
            )
            and not bool(
                row["authorization_token_recorded"]
            )
            and not bool(row["commit_command_recorded"])
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


def get_tower_acceptance_closeout_safety_blocker_board(
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
        "gp": 659,
        "title": (
            "Tower Acceptance Closeout "
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


def get_tower_acceptance_closeout_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = (
        get_tower_handoff_acceptance_closeout_shell()
    )

    intakes = (
        get_acceptance_gate_evidence_closeout_intake_board()
    )

    authorities = (
        get_tower_acceptance_authority_requirement_closeout_board()
    )

    sessions = (
        get_tower_acceptance_session_requirement_closeout_board()
    )

    evidence = (
        get_acceptance_evidence_reference_requirement_freeze_board()
    )

    decisions = (
        get_tower_acceptance_decision_contract_freeze_board()
    )

    records = (
        get_tower_acceptance_closeout_record_draft_board()
    )

    receipts = (
        get_tower_acceptance_closeout_receipt_draft_ledger()
    )

    blockers = (
        get_tower_acceptance_closeout_safety_blocker_board()
    )

    checks = {
        "previous_acceptance_gate_ready": (
            initialized[
                "previous_acceptance_gate_ready"
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
        "acceptance_closeout_only": (
            DOCTRINE["acceptance_closeout_only"]
            is True
            and DOCTRINE[
                "acceptance_requirements_may_be_sealed"
            ]
            is True
            and DOCTRINE[
                "acceptance_execution_allowed"
            ]
            is False
            and DOCTRINE[
                "tower_is_only_handoff_acceptance_authority"
            ]
            is True
            and DOCTRINE[
                "vault_cannot_accept_its_own_handoff"
            ]
            is True
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "acceptance_gate_evidence_verified": (
            intakes[
                "all_acceptance_intakes_verified"
            ]
            is True
            and intakes[
                "all_authority_contracts_verified"
            ]
            is True
            and intakes[
                "all_session_contracts_verified"
            ]
            is True
            and intakes[
                "all_evidence_gates_verified"
            ]
            is True
            and intakes[
                "all_decision_contracts_verified"
            ]
            is True
            and intakes[
                "all_acceptance_records_verified"
            ]
            is True
            and intakes[
                "all_acceptance_receipts_verified"
            ]
            is True
            and intakes[
                "all_eligible_for_closeout"
            ]
            is True
        ),
        "handoff_and_acceptance_absent": (
            intakes["no_handoffs_delivered"]
            is True
            and intakes["no_handoffs_accepted"]
            is True
            and intakes[
                "no_acceptance_decisions_recorded"
            ]
            is True
        ),

        "authority_closeouts_present": (
            authorities["closeout_count"] >= 1
        ),
        "authority_requirements_sealed": (
            authorities[
                "all_requirements_sealed"
            ]
            is True
            and authorities["all_target_tower"]
            is True
            and authorities[
                "all_tower_controls_required"
            ]
            is True
            and authorities[
                "no_vault_acceptance_authority"
            ]
            is True
            and authorities[
                "no_teller_acceptance_authority"
            ]
            is True
            and authorities[
                "no_acceptance_authority_granted"
            ]
            is True
        ),

        "session_closeouts_present": (
            sessions["closeout_count"] >= 1
        ),
        "session_requirements_sealed": (
            sessions["all_requirements_sealed"]
            is True
            and sessions[
                "all_session_requirements_present"
            ]
            is True
        ),
        "session_requirements_unsatisfied": (
            sessions["no_sessions_created"]
            is True
            and sessions["no_sessions_started"]
            is True
            and sessions[
                "no_prerequisites_complete"
            ]
            is True
        ),

        "evidence_freezes_present": (
            evidence["freeze_count"] >= 1
        ),
        "evidence_requirements_frozen": (
            evidence["all_requirements_frozen"]
            is True
            and evidence[
                "all_reference_requirements_present"
            ]
            is True
        ),
        "evidence_references_unsupplied": (
            evidence["no_references_supplied"]
            is True
            and evidence[
                "no_evidence_gates_complete"
            ]
            is True
        ),

        "decision_freezes_present": (
            decisions["freeze_count"] >= 1
        ),
        "acceptance_decision_contract_frozen": (
            decisions["all_contracts_frozen"]
            is True
            and decisions[
                "all_decision_enums_complete"
            ]
            is True
            and decisions[
                "all_required_fields_complete"
            ]
            is True
            and decisions["all_tower_only"]
            is True
            and decisions[
                "all_append_only_required"
            ]
            is True
            and decisions["no_mutation_allowed"]
            is True
            and decisions[
                "no_raw_material_allowed"
            ]
            is True
        ),
        "acceptance_and_owner_decisions_absent": (
            decisions[
                "no_acceptance_selections_present"
            ]
            is True
            and decisions[
                "no_acceptance_decisions_recorded"
            ]
            is True
            and decisions[
                "no_owner_decisions_recorded"
            ]
            is True
        ),

        "closeout_records_present": (
            records["record_count"] >= 1
        ),
        "closeout_record_package_ready": (
            records["all_source_hashes_present"]
            is True
            and records[
                "all_closeout_packages_complete"
            ]
            is True
            and records[
                "all_future_delivery_preparation_eligible"
            ]
            is True
            and records["all_records_unfinalized"]
            is True
            and records["all_append_only"]
            is True
            and records["all_immutable"]
            is True
        ),
        "no_acceptance_or_recovery_actions": (
            records["no_handoffs_delivered"]
            is True
            and records["no_handoffs_accepted"]
            is True
            and records[
                "no_acceptance_decisions_recorded"
            ]
            is True
            and records[
                "no_tower_sessions_created"
            ]
            is True
            and records[
                "no_owner_decisions_recorded"
            ]
            is True
            and records[
                "no_recording_gates_open"
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
                "no_delivery_acceptance_or_session_recorded"
            ]
            is True
            and receipts[
                "no_owner_or_recovery_actions_recorded"
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
                LOCKS[
                    "acceptance_decision_recorded"
                ]
                is False,
                LOCKS["acceptance_gate_open"]
                is False,
                LOCKS[
                    "acceptance_execution_allowed"
                ]
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
                    "employee_vault_access_allowed"
                ]
                is False,
                LOCKS[
                    "customer_vault_access_allowed"
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
        "gp": 660,
        "title": (
            "Tower Acceptance Closeout "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else "Tower acceptance closeout blocked"
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "closeout_status": (
            "acceptance_gate_evidence_verified_"
            "acceptance_requirements_sealed_"
            "acceptance_evidence_unsupplied_"
            "handoff_not_delivered_or_accepted"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION TOWER HANDOFF "
            "DELIVERY PREPARATION LAYER / GP661-GP670"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no handoff delivery",
            "no handoff acceptance",
            "no acceptance decision recorded",
            "no Tower acceptance session created",
            "no Tower owner-review session started",
            "no owner authenticated or stepped up",
            "no owner/admin approval or dual receipt",
            "no owner selection or decision",
            "no owner-decision recording gate open",
            "no GO decision",
            "no recovery authorization or token",
            "no scope/window activation",
            "no execution window or commit point",
            "no real commit command",
            "no restore or production write",
            "no external provider connection",
            "no Teller-to-Vault direct call",
            "no prohibited person or public access",
            "no raw bytes, paths, URLs, or tokens",
            "no destructive action",
        ],
    }


def get_recovery_commit_owner_decision_tower_handoff_acceptance_closeout_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_tower_acceptance_closeout_readiness_checkpoint()
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


def validate_recovery_commit_owner_decision_tower_handoff_acceptance_closeout_layer(
) -> Dict[str, Any]:
    checkpoint = (
        get_tower_acceptance_closeout_readiness_checkpoint()
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
        get_tower_acceptance_closeout_readiness_checkpoint()
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
        "acceptance_requirements_sealed": True,
        "handoff_delivered": False,
        "handoff_accepted": False,
        "acceptance_decision_recorded": False,
        "tower_session_created": False,
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


def get_gp651_status():
    return _gp_status(651)


def get_gp652_status():
    return _gp_status(652)


def get_gp653_status():
    return _gp_status(653)


def get_gp654_status():
    return _gp_status(654)


def get_gp655_status():
    return _gp_status(655)


def get_gp656_status():
    return _gp_status(656)


def get_gp657_status():
    return _gp_status(657)


def get_gp658_status():
    return _gp_status(658)


def get_gp659_status():
    return _gp_status(659)


def get_gp660_status():
    return _gp_status(660)
