
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


SECTION = (
    "ARCHIVE VAULT — RECOVERY COMMIT OWNER DECISION "
    "TOWER HANDOFF ACCEPTANCE GATE / GP641-GP650"
)

LAYER_ID = (
    "vault_gp641_650_"
    "recovery_commit_owner_decision_tower_handoff_acceptance_gate"
)

READINESS_LABEL = (
    "Tower handoff acceptance gate contract ready"
)

CURRENT_RECOMMENDATION = (
    "NO_GO_HOLD_TOWER_HANDOFF_ACCEPTANCE_GATE_CLOSED"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = (
    DATA_DIR
    / "vault_recovery_commit_owner_decision_tower_handoff_acceptance_gate.sqlite"
)

try:
    from vault.owner_owned_file_storage_foundation_layer_service import (
        calculate_sha256_bytes,
    )

    from vault.recovery_commit_owner_decision_tower_handoff_layer_service import (
        ALLOWED_DECISION_VALUES,
        HANDOFF_ENVELOPE_FIELDS,
        RECORDING_CONTRACT_FIELDS,
        get_recording_closeout_package_intake_board,
        get_tower_handoff_envelope_contract_board,
        get_tower_owner_review_session_launch_prerequisite_board,
        get_owner_decision_input_handoff_contract_board,
        get_approval_receipt_reference_handoff_board,
        get_tower_owner_decision_handoff_packet_draft_board,
        get_tower_owner_decision_handoff_receipt_draft_ledger,
        validate_recovery_commit_owner_decision_tower_handoff_layer,
    )
except Exception as exc:
    raise RuntimeError(
        "GP641-GP650 requires the completed "
        "GP631-GP640 Tower handoff layer."
    ) from exc


_INIT_CACHE = None


ACCEPTANCE_DECISIONS = [
    "ACCEPT_HANDOFF",
    "REJECT_HANDOFF",
    "RETURN_FOR_REPAIR",
    "DEFER_ACCEPTANCE",
]


ACCEPTANCE_CONTRACT_FIELDS = [
    "acceptance_id",
    "handoff_packet_id",
    "request_id",
    "tower_actor_reference",
    "tower_identity_receipt_reference",
    "tower_permission_receipt_reference",
    "tower_clearance_receipt_reference",
    "tower_step_up_receipt_reference",
    "source_handoff_envelope_hash",
    "source_handoff_packet_hash",
    "source_handoff_receipt_hash",
    "acceptance_decision",
    "acceptance_reason_code",
    "acceptance_reason_summary",
    "idempotency_key",
    "accepted_at",
]


DOCTRINE = {
    "tower": "face_protocol_authority",
    "teller": "workflow_request_source",
    "vault": "sealed_memory",
    "correct_flow": (
        "Teller -> Tower -> Vault -> Tower -> Teller"
    ),
    "acceptance_gate_definition_only": True,
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
    "acceptance_gate_layer": True,
    "handoff_packet_verification_allowed": True,
    "acceptance_authority_contract_allowed": True,
    "acceptance_session_prerequisite_definition_allowed": True,
    "acceptance_evidence_reference_definition_allowed": True,
    "acceptance_decision_contract_allowed": True,
    "acceptance_record_drafts_allowed": True,
    "acceptance_receipt_drafts_allowed": True,

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
        "gp": 641,
        "title": "Tower Handoff Acceptance Gate Shell",
        "route": (
            "/vault/tower-handoff-acceptance-"
            "gate-shell.json"
        ),
    },
    {
        "gp": 642,
        "title": (
            "Tower Handoff Packet Intake "
            "Verification Board"
        ),
        "route": (
            "/vault/tower-handoff-packet-intake-"
            "verification-board.json"
        ),
    },
    {
        "gp": 643,
        "title": (
            "Tower Handoff Acceptance Authority "
            "Contract Board"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-authority-"
            "contract-board.json"
        ),
    },
    {
        "gp": 644,
        "title": (
            "Tower Acceptance Session "
            "Prerequisite Board"
        ),
        "route": (
            "/vault/tower-acceptance-session-"
            "prerequisite-board.json"
        ),
    },
    {
        "gp": 645,
        "title": (
            "Tower Handoff Acceptance Evidence "
            "Reference Gate"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-evidence-"
            "reference-gate.json"
        ),
    },
    {
        "gp": 646,
        "title": (
            "Tower Handoff Acceptance Decision "
            "Contract Board"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-decision-"
            "contract-board.json"
        ),
    },
    {
        "gp": 647,
        "title": (
            "Tower Handoff Acceptance "
            "Record Draft Board"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-"
            "record-draft-board.json"
        ),
    },
    {
        "gp": 648,
        "title": (
            "Tower Handoff Acceptance "
            "Receipt Draft Ledger"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-"
            "receipt-draft-ledger.json"
        ),
    },
    {
        "gp": 649,
        "title": (
            "Tower Handoff Acceptance "
            "Safety Blocker Board"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-"
            "safety-blocker-board.json"
        ),
    },
    {
        "gp": 650,
        "title": (
            "Tower Handoff Acceptance Gate "
            "Readiness Checkpoint"
        ),
        "route": (
            "/vault/tower-handoff-acceptance-"
            "gate-readiness.json"
        ),
    },
]


BLOCKERS = [
    (
        "no_handoff_delivery",
        "live_handoff_delivery",
        "Acceptance preparation cannot deliver the handoff.",
    ),
    (
        "no_handoff_acceptance",
        "live_handoff_acceptance",
        "Vault cannot accept its own handoff.",
    ),
    (
        "no_acceptance_decision_recording",
        "acceptance_decision_recording",
        "This layer defines the acceptance gate only.",
    ),
    (
        "no_tower_session_creation",
        "tower_session_creation",
        "Vault cannot create a Tower session.",
    ),
    (
        "no_owner_review_session_start",
        "owner_review_session_start",
        "Tower must start any future owner session.",
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
        "Vault cannot collect owner input.",
    ),
    (
        "no_owner_decision_recording",
        "owner_decision_recording",
        "Acceptance is not an owner decision.",
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
        "no_public_access",
        "public_vault_access",
        "Vault has no public access path.",
    ),
    (
        "no_raw_material",
        "raw_bytes_paths_urls_or_tokens",
        "Acceptance contracts use references and hashes only.",
    ),
    (
        "no_destructive_action",
        "delete_purge_release_or_move",
        "Acceptance preparation cannot destroy evidence.",
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
        get_recording_closeout_package_intake_board()
        .get("handoff_intakes", [])
    )

    envelope_rows = (
        get_tower_handoff_envelope_contract_board()
        .get("handoff_envelopes", [])
    )

    session_rows = (
        get_tower_owner_review_session_launch_prerequisite_board()
        .get("session_launch_prerequisites", [])
    )

    input_rows = (
        get_owner_decision_input_handoff_contract_board()
        .get("owner_input_contracts", [])
    )

    approval_rows = (
        get_approval_receipt_reference_handoff_board()
        .get("approval_reference_handoffs", [])
    )

    packet_rows = (
        get_tower_owner_decision_handoff_packet_draft_board()
        .get("handoff_packet_drafts", [])
    )

    receipt_rows = (
        get_tower_owner_decision_handoff_receipt_draft_ledger()
        .get("handoff_receipt_drafts", [])
    )

    envelopes = _by_request(envelope_rows)
    sessions = _by_request(session_rows)
    inputs = _by_request(input_rows)
    approvals = _by_request(approval_rows)
    packets = _by_request(packet_rows)
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
                "envelope": envelopes.get(
                    request_id,
                    {},
                ),
                "session": sessions.get(
                    request_id,
                    {},
                ),
                "input": inputs.get(
                    request_id,
                    {},
                ),
                "approval": approvals.get(
                    request_id,
                    {},
                ),
                "packet": packets.get(
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
        validate_recovery_commit_owner_decision_tower_handoff_layer()
    )

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS acceptance_intakes (
                acceptance_intake_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                handoff_intake_verified INTEGER NOT NULL,
                envelope_verified INTEGER NOT NULL,
                session_contract_verified INTEGER NOT NULL,
                owner_input_contract_verified INTEGER NOT NULL,
                approval_reference_contract_verified INTEGER NOT NULL,
                handoff_packet_verified INTEGER NOT NULL,
                handoff_receipt_verified INTEGER NOT NULL,
                eligible_for_acceptance_gate_review INTEGER NOT NULL,
                handoff_delivered INTEGER NOT NULL,
                handoff_accepted INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acceptance_authority_contracts (
                authority_contract_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
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
                authority_contract_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acceptance_session_prerequisites (
                acceptance_session_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
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
                prerequisite_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acceptance_evidence_gates (
                evidence_gate_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
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
                evidence_gate_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acceptance_decision_contracts (
                decision_contract_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
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
                decision_contract_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acceptance_record_drafts (
                acceptance_record_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                state TEXT NOT NULL,
                authority_contract_id TEXT NOT NULL,
                acceptance_session_id TEXT NOT NULL,
                evidence_gate_id TEXT NOT NULL,
                decision_contract_id TEXT NOT NULL,
                source_envelope_hash TEXT NOT NULL,
                source_packet_hash TEXT NOT NULL,
                source_receipt_hash TEXT NOT NULL,
                acceptance_contract_complete INTEGER NOT NULL,
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
                acceptance_record_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS acceptance_receipt_drafts (
                acceptance_receipt_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                acceptance_record_id TEXT NOT NULL,
                state TEXT NOT NULL,
                tower_controlled INTEGER NOT NULL,
                source_handoff_recorded INTEGER NOT NULL,
                authority_contract_recorded INTEGER NOT NULL,
                session_prerequisites_recorded INTEGER NOT NULL,
                evidence_requirements_recorded INTEGER NOT NULL,
                decision_contract_recorded INTEGER NOT NULL,
                acceptance_record_draft_recorded INTEGER NOT NULL,
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
            "acceptance_intakes",
            "acceptance_authority_contracts",
            "acceptance_session_prerequisites",
            "acceptance_evidence_gates",
            "acceptance_decision_contracts",
            "acceptance_record_drafts",
            "acceptance_receipt_drafts",
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
            envelope = source["envelope"]
            session = source["session"]
            owner_input = source["input"]
            approval = source["approval"]
            packet = source["packet"]
            receipt = source["receipt"]

            handoff_intake_verified = all(
                [
                    bool(
                        intake.get(
                            "closeout_intake_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "identity_closeout_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "approval_closeout_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "contract_freeze_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "boundary_closeout_verified",
                            0,
                        )
                    ),
                    bool(
                        intake.get(
                            "closeout_record_verified",
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
                            "eligible_for_tower_handoff_packaging",
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

            envelope_verified = all(
                [
                    envelope.get(
                        "target_service"
                    )
                    == "tower",
                    envelope.get(
                        "target_workflow"
                    )
                    == "owner_recovery_decision_review",
                    int(
                        envelope.get(
                            "required_field_count",
                            0,
                        )
                    )
                    == len(HANDOFF_ENVELOPE_FIELDS),
                    len(
                        envelope.get(
                            "source_package_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        envelope.get(
                            "source_closeout_record_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        envelope.get(
                            "source_closeout_receipt_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        envelope.get(
                            "tower_only",
                            0,
                        )
                    ),
                    bool(
                        envelope.get(
                            "references_only",
                            0,
                        )
                    ),
                    not bool(
                        envelope.get(
                            "raw_material_allowed",
                            1,
                        )
                    ),
                    not bool(
                        envelope.get(
                            "delivery_allowed",
                            1,
                        )
                    ),
                    not bool(
                        envelope.get(
                            "acceptance_allowed",
                            1,
                        )
                    ),
                    len(
                        envelope.get(
                            "envelope_hash",
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
                            "tower_session_type_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "owner_presence_required",
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
                            "owner_principal_reference_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "identity_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        session.get(
                            "step_up_receipt_reference_required",
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
                            "owner_authenticated",
                            1,
                        )
                    ),
                    not bool(
                        session.get(
                            "step_up_satisfied",
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

            owner_input_contract_verified = all(
                [
                    int(
                        owner_input.get(
                            "allowed_decision_count",
                            0,
                        )
                    )
                    == len(ALLOWED_DECISION_VALUES),
                    int(
                        owner_input.get(
                            "required_field_count",
                            0,
                        )
                    )
                    == len(RECORDING_CONTRACT_FIELDS),
                    bool(
                        owner_input.get(
                            "tower_ui_only",
                            0,
                        )
                    ),
                    not bool(
                        owner_input.get(
                            "vault_direct_input_allowed",
                            1,
                        )
                    ),
                    not bool(
                        owner_input.get(
                            "teller_direct_input_allowed",
                            1,
                        )
                    ),
                    not bool(
                        owner_input.get(
                            "owner_selection_present",
                            1,
                        )
                    ),
                    not bool(
                        owner_input.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    bool(
                        owner_input.get(
                            "decision_reason_required",
                            0,
                        )
                    ),
                    bool(
                        owner_input.get(
                            "idempotency_key_required",
                            0,
                        )
                    ),
                    bool(
                        owner_input.get(
                            "append_only_required",
                            0,
                        )
                    ),
                    not bool(
                        owner_input.get(
                            "mutation_allowed",
                            1,
                        )
                    ),
                    len(
                        owner_input.get(
                            "contract_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            approval_contract_verified = all(
                [
                    bool(
                        approval.get(
                            "identity_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "step_up_receipt_reference_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "owner_admin_approval_receipt_required",
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
                    bool(
                        approval.get(
                            "exact_scope_hash_reference_required",
                            0,
                        )
                    ),
                    bool(
                        approval.get(
                            "commit_window_hash_reference_required",
                            0,
                        )
                    ),
                    int(
                        approval.get(
                            "supplied_reference_count",
                            -1,
                        )
                    )
                    == 0,
                    not bool(
                        approval.get(
                            "reference_gate_complete",
                            1,
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
                    len(
                        approval.get(
                            "reference_handoff_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            handoff_packet_verified = all(
                [
                    len(
                        packet.get(
                            "source_closeout_record_hash",
                            "",
                        )
                    )
                    == 64,
                    len(
                        packet.get(
                            "source_closeout_receipt_hash",
                            "",
                        )
                    )
                    == 64,
                    bool(
                        packet.get(
                            "package_complete",
                            0,
                        )
                    ),
                    bool(
                        packet.get(
                            "eligible_for_future_tower_acceptance",
                            0,
                        )
                    ),
                    not bool(
                        packet.get(
                            "handoff_delivered",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "handoff_accepted",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "tower_session_created",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "owner_selection_present",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "owner_decision_recorded",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "recording_gate_open",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "go_decision_granted",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "live_authorization_granted",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "authorization_token_issued",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "commit_command_issued",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "actual_restore_allowed",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "production_write_allowed",
                            1,
                        )
                    ),
                    not bool(
                        packet.get(
                            "finalized",
                            1,
                        )
                    ),
                    bool(
                        packet.get(
                            "append_only",
                            0,
                        )
                    ),
                    not bool(
                        packet.get(
                            "mutable",
                            1,
                        )
                    ),
                    len(
                        packet.get(
                            "packet_hash",
                            "",
                        )
                    )
                    == 64,
                ]
            )

            handoff_receipt_verified = all(
                [
                    bool(
                        receipt.get(
                            "tower_controlled",
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
                            "envelope_contract_recorded",
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
                            "owner_input_contract_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "approval_references_recorded",
                            0,
                        )
                    ),
                    bool(
                        receipt.get(
                            "packet_draft_recorded",
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
                            "tower_session_creation_recorded",
                            1,
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

            eligible = all(
                [
                    handoff_intake_verified,
                    envelope_verified,
                    session_contract_verified,
                    owner_input_contract_verified,
                    approval_contract_verified,
                    handoff_packet_verified,
                    handoff_receipt_verified,
                ]
            )

            acceptance_intake_id = _id(
                "tower_acceptance_intake",
                request_id,
            )

            authority_contract_id = _id(
                "tower_acceptance_authority",
                request_id,
            )

            acceptance_session_id = _id(
                "tower_acceptance_session",
                request_id,
            )

            evidence_gate_id = _id(
                "tower_acceptance_evidence",
                request_id,
            )

            decision_contract_id = _id(
                "tower_acceptance_decision",
                request_id,
            )

            acceptance_record_id = _id(
                "tower_acceptance_record",
                request_id,
            )

            acceptance_receipt_id = _id(
                "tower_acceptance_receipt",
                request_id,
            )

            _insert_row(
                connection,
                "acceptance_intakes",
                {
                    "acceptance_intake_id": (
                        acceptance_intake_id
                    ),
                    "request_id": request_id,
                    "workflow_type": workflow_type,
                    "state": (
                        "handoff_packet_verified_"
                        "acceptance_gate_closed"
                    ),
                    "handoff_intake_verified": int(
                        handoff_intake_verified
                    ),
                    "envelope_verified": int(
                        envelope_verified
                    ),
                    "session_contract_verified": int(
                        session_contract_verified
                    ),
                    "owner_input_contract_verified": int(
                        owner_input_contract_verified
                    ),
                    "approval_reference_contract_verified": int(
                        approval_contract_verified
                    ),
                    "handoff_packet_verified": int(
                        handoff_packet_verified
                    ),
                    "handoff_receipt_verified": int(
                        handoff_receipt_verified
                    ),
                    "eligible_for_acceptance_gate_review": int(
                        eligible
                    ),
                    "handoff_delivered": 0,
                    "handoff_accepted": 0,
                    "created_at": now,
                },
            )

            authority_payload = {
                "request_id": request_id,
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
            }

            authority_hash = _canonical_hash(
                authority_payload
            )

            _insert_row(
                connection,
                "acceptance_authority_contracts",
                {
                    "authority_contract_id": (
                        authority_contract_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_acceptance_authority_"
                        "requirements_defined_not_granted"
                    ),
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
                    "authority_contract_hash": authority_hash,
                    "created_at": now,
                },
            )

            session_payload = {
                "request_id": request_id,
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
            }

            session_hash = _canonical_hash(
                session_payload
            )

            _insert_row(
                connection,
                "acceptance_session_prerequisites",
                {
                    "acceptance_session_id": (
                        acceptance_session_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_acceptance_session_"
                        "requirements_defined_not_satisfied"
                    ),
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
                    "prerequisite_hash": session_hash,
                    "created_at": now,
                },
            )

            evidence_payload = {
                "request_id": request_id,
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
            }

            evidence_hash = _canonical_hash(
                evidence_payload
            )

            _insert_row(
                connection,
                "acceptance_evidence_gates",
                {
                    "evidence_gate_id": evidence_gate_id,
                    "request_id": request_id,
                    "state": (
                        "acceptance_evidence_requirements_"
                        "defined_none_supplied"
                    ),
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
                    "evidence_gate_hash": evidence_hash,
                    "created_at": now,
                },
            )

            decision_payload = {
                "request_id": request_id,
                "allowed_decisions": ACCEPTANCE_DECISIONS,
                "required_fields": ACCEPTANCE_CONTRACT_FIELDS,
                "tower_only": True,
                "selected_acceptance_decision_present": False,
                "acceptance_decision_recorded": False,
                "owner_decision_recorded": False,
                "append_only_required": True,
                "mutation_allowed": False,
                "raw_material_allowed": False,
            }

            decision_hash = _canonical_hash(
                decision_payload
            )

            _insert_row(
                connection,
                "acceptance_decision_contracts",
                {
                    "decision_contract_id": (
                        decision_contract_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "acceptance_decision_contract_"
                        "defined_no_selection"
                    ),
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
                    "decision_contract_hash": decision_hash,
                    "created_at": now,
                },
            )

            record_payload = {
                "request_id": request_id,
                "authority_contract_id": authority_contract_id,
                "acceptance_session_id": acceptance_session_id,
                "evidence_gate_id": evidence_gate_id,
                "decision_contract_id": decision_contract_id,
                "source_envelope_hash": envelope.get(
                    "envelope_hash",
                    "",
                ),
                "source_packet_hash": packet.get(
                    "packet_hash",
                    "",
                ),
                "source_receipt_hash": receipt.get(
                    "receipt_hash",
                    "",
                ),
                "acceptance_contract_complete": True,
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

            record_hash = _canonical_hash(
                record_payload
            )

            _insert_row(
                connection,
                "acceptance_record_drafts",
                {
                    "acceptance_record_id": (
                        acceptance_record_id
                    ),
                    "request_id": request_id,
                    "state": (
                        "tower_acceptance_record_draft_"
                        "gate_closed"
                    ),
                    "authority_contract_id": (
                        authority_contract_id
                    ),
                    "acceptance_session_id": (
                        acceptance_session_id
                    ),
                    "evidence_gate_id": evidence_gate_id,
                    "decision_contract_id": (
                        decision_contract_id
                    ),
                    "source_envelope_hash": envelope.get(
                        "envelope_hash",
                        "",
                    ),
                    "source_packet_hash": packet.get(
                        "packet_hash",
                        "",
                    ),
                    "source_receipt_hash": receipt.get(
                        "receipt_hash",
                        "",
                    ),
                    "acceptance_contract_complete": 1,
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
                    "acceptance_record_hash": record_hash,
                    "created_at": now,
                },
            )

            receipt_payload = {
                "request_id": request_id,
                "acceptance_record_id": acceptance_record_id,
                "source_handoff_recorded": True,
                "authority_contract_recorded": True,
                "session_prerequisites_recorded": True,
                "evidence_requirements_recorded": True,
                "decision_contract_recorded": True,
                "acceptance_record_draft_recorded": True,
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

            receipt_hash = _canonical_hash(
                receipt_payload
            )

            _insert_row(
                connection,
                "acceptance_receipt_drafts",
                {
                    "acceptance_receipt_id": (
                        acceptance_receipt_id
                    ),
                    "request_id": request_id,
                    "acceptance_record_id": (
                        acceptance_record_id
                    ),
                    "state": (
                        "tower_acceptance_receipt_draft_"
                        "acceptance_not_recorded"
                    ),
                    "tower_controlled": 1,
                    "source_handoff_recorded": 1,
                    "authority_contract_recorded": 1,
                    "session_prerequisites_recorded": 1,
                    "evidence_requirements_recorded": 1,
                    "decision_contract_recorded": 1,
                    "acceptance_record_draft_recorded": 1,
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
                    "receipt_hash": receipt_hash,
                    "created_at": now,
                },
            )

        connection.commit()

    result = {
        "initialized": True,
        "previous_tower_handoff_layer_ready": bool(
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


def get_tower_handoff_acceptance_gate_shell(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    return {
        "section": SECTION,
        "layer_id": LAYER_ID,
        "gp": 641,
        "title": "Tower Handoff Acceptance Gate Shell",
        "ready": True,
        "initialized": initialized,
        "doctrine": DOCTRINE,
        "locks": LOCKS,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "acceptance_gate_definition_only": True,
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


def get_tower_handoff_packet_intake_verification_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_intakes
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 642,
        "title": (
            "Tower Handoff Packet Intake "
            "Verification Board"
        ),
        "ready": True,
        "intake_count": len(rows),
        "acceptance_intakes": rows,
        "all_handoff_intakes_verified": all(
            bool(row["handoff_intake_verified"])
            for row in rows
        ),
        "all_envelopes_verified": all(
            bool(row["envelope_verified"])
            for row in rows
        ),
        "all_session_contracts_verified": all(
            bool(row["session_contract_verified"])
            for row in rows
        ),
        "all_owner_input_contracts_verified": all(
            bool(
                row[
                    "owner_input_contract_verified"
                ]
            )
            for row in rows
        ),
        "all_approval_reference_contracts_verified": all(
            bool(
                row[
                    "approval_reference_contract_verified"
                ]
            )
            for row in rows
        ),
        "all_packets_verified": all(
            bool(row["handoff_packet_verified"])
            for row in rows
        ),
        "all_receipts_verified": all(
            bool(row["handoff_receipt_verified"])
            for row in rows
        ),
        "all_eligible_for_acceptance_review": all(
            bool(
                row[
                    "eligible_for_acceptance_gate_review"
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


def get_tower_handoff_acceptance_authority_contract_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_authority_contracts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 643,
        "title": (
            "Tower Handoff Acceptance Authority "
            "Contract Board"
        ),
        "ready": True,
        "contract_count": len(rows),
        "acceptance_authority_contracts": rows,
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
        "all_authority_hashes_present": all(
            len(row["authority_contract_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_acceptance_session_prerequisite_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_session_prerequisites
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 644,
        "title": (
            "Tower Acceptance Session "
            "Prerequisite Board"
        ),
        "ready": True,
        "session_count": len(rows),
        "acceptance_session_prerequisites": rows,
        "all_requirements_present": all(
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
        "all_prerequisite_hashes_present": all(
            len(row["prerequisite_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_handoff_acceptance_evidence_reference_gate(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_evidence_gates
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 645,
        "title": (
            "Tower Handoff Acceptance Evidence "
            "Reference Gate"
        ),
        "ready": True,
        "gate_count": len(rows),
        "acceptance_evidence_gates": rows,
        "all_evidence_requirements_present": all(
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
        "all_evidence_hashes_present": all(
            len(row["evidence_gate_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_handoff_acceptance_decision_contract_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_decision_contracts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 646,
        "title": (
            "Tower Handoff Acceptance Decision "
            "Contract Board"
        ),
        "ready": True,
        "contract_count": len(rows),
        "acceptance_decision_contracts": rows,
        "allowed_acceptance_decisions": (
            ACCEPTANCE_DECISIONS
        ),
        "required_acceptance_fields": (
            ACCEPTANCE_CONTRACT_FIELDS
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
        "all_contract_hashes_present": all(
            len(row["decision_contract_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_handoff_acceptance_record_draft_board(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_record_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 647,
        "title": (
            "Tower Handoff Acceptance "
            "Record Draft Board"
        ),
        "ready": True,
        "record_count": len(rows),
        "acceptance_record_drafts": rows,
        "all_source_hashes_present": all(
            len(row["source_envelope_hash"]) == 64
            and len(row["source_packet_hash"]) == 64
            and len(row["source_receipt_hash"]) == 64
            for row in rows
        ),
        "all_acceptance_contracts_complete": all(
            bool(row["acceptance_contract_complete"])
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
            len(row["acceptance_record_hash"]) == 64
            for row in rows
        ),
    }


def get_tower_handoff_acceptance_receipt_draft_ledger(
) -> Dict[str, Any]:
    initialize_layer()

    with _connect() as connection:
        rows = _rows(
            connection,
            """
            SELECT *
            FROM acceptance_receipt_drafts
            ORDER BY request_id
            """,
        )

    return {
        "section": SECTION,
        "gp": 648,
        "title": (
            "Tower Handoff Acceptance "
            "Receipt Draft Ledger"
        ),
        "ready": True,
        "receipt_count": len(rows),
        "acceptance_receipt_drafts": rows,
        "all_tower_controlled": all(
            bool(row["tower_controlled"])
            for row in rows
        ),
        "all_contract_components_recorded": all(
            bool(row["source_handoff_recorded"])
            and bool(row["authority_contract_recorded"])
            and bool(
                row["session_prerequisites_recorded"]
            )
            and bool(
                row["evidence_requirements_recorded"]
            )
            and bool(row["decision_contract_recorded"])
            and bool(
                row[
                    "acceptance_record_draft_recorded"
                ]
            )
            for row in rows
        ),
        "no_delivery_or_acceptance_recorded": all(
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


def get_tower_handoff_acceptance_safety_blocker_board(
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
        "gp": 649,
        "title": (
            "Tower Handoff Acceptance "
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


def get_tower_handoff_acceptance_gate_readiness_checkpoint(
) -> Dict[str, Any]:
    initialized = initialize_layer()

    shell = get_tower_handoff_acceptance_gate_shell()

    intakes = (
        get_tower_handoff_packet_intake_verification_board()
    )

    authorities = (
        get_tower_handoff_acceptance_authority_contract_board()
    )

    sessions = (
        get_tower_acceptance_session_prerequisite_board()
    )

    evidence = (
        get_tower_handoff_acceptance_evidence_reference_gate()
    )

    decisions = (
        get_tower_handoff_acceptance_decision_contract_board()
    )

    records = (
        get_tower_handoff_acceptance_record_draft_board()
    )

    receipts = (
        get_tower_handoff_acceptance_receipt_draft_ledger()
    )

    blockers = (
        get_tower_handoff_acceptance_safety_blocker_board()
    )

    checks = {
        "previous_tower_handoff_layer_ready": (
            initialized[
                "previous_tower_handoff_layer_ready"
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
        "acceptance_definition_only": (
            DOCTRINE[
                "acceptance_gate_definition_only"
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
            and DOCTRINE[
                "teller_cannot_accept_vault_handoff"
            ]
            is True
        ),

        "intakes_present": (
            intakes["intake_count"] >= 1
        ),
        "handoff_package_verified": (
            intakes[
                "all_handoff_intakes_verified"
            ]
            is True
            and intakes[
                "all_envelopes_verified"
            ]
            is True
            and intakes[
                "all_session_contracts_verified"
            ]
            is True
            and intakes[
                "all_owner_input_contracts_verified"
            ]
            is True
            and intakes[
                "all_approval_reference_contracts_verified"
            ]
            is True
            and intakes["all_packets_verified"]
            is True
            and intakes["all_receipts_verified"]
            is True
            and intakes[
                "all_eligible_for_acceptance_review"
            ]
            is True
        ),
        "handoff_not_delivered_or_accepted": (
            intakes["no_handoffs_delivered"]
            is True
            and intakes["no_handoffs_accepted"]
            is True
        ),

        "authority_contracts_present": (
            authorities["contract_count"] >= 1
        ),
        "tower_authority_contract_complete": (
            authorities["all_target_tower"]
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

        "acceptance_sessions_present": (
            sessions["session_count"] >= 1
        ),
        "acceptance_session_requirements_complete": (
            sessions["all_requirements_present"]
            is True
        ),
        "acceptance_session_not_started": (
            sessions["no_sessions_created"]
            is True
            and sessions["no_sessions_started"]
            is True
            and sessions[
                "no_prerequisites_complete"
            ]
            is True
        ),

        "evidence_gates_present": (
            evidence["gate_count"] >= 1
        ),
        "acceptance_evidence_contract_complete": (
            evidence[
                "all_evidence_requirements_present"
            ]
            is True
        ),
        "acceptance_evidence_unsupplied": (
            evidence["no_references_supplied"]
            is True
            and evidence[
                "no_evidence_gates_complete"
            ]
            is True
        ),

        "decision_contracts_present": (
            decisions["contract_count"] >= 1
        ),
        "acceptance_decision_contract_complete": (
            decisions[
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
        "acceptance_decision_absent": (
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

        "record_drafts_present": (
            records["record_count"] >= 1
        ),
        "acceptance_record_contract_ready": (
            records["all_source_hashes_present"]
            is True
            and records[
                "all_acceptance_contracts_complete"
            ]
            is True
            and records["all_records_unfinalized"]
            is True
            and records["all_append_only"]
            is True
            and records["all_immutable"]
            is True
        ),
        "acceptance_and_recovery_actions_absent": (
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

        "receipt_drafts_present": (
            receipts["receipt_count"] >= 1
        ),
        "receipt_drafts_safe": (
            receipts["all_tower_controlled"]
            is True
            and receipts[
                "all_contract_components_recorded"
            ]
            is True
            and receipts[
                "no_delivery_or_acceptance_recorded"
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
                LOCKS["handoff_delivered"] is False,
                LOCKS["handoff_accepted"] is False,
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
                    "owner_selection_present"
                ]
                is False,
                LOCKS[
                    "owner_decision_recorded"
                ]
                is False,
                LOCKS["recording_gate_open"]
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
        "gp": 650,
        "title": (
            "Tower Handoff Acceptance Gate "
            "Readiness Checkpoint"
        ),
        "ready": ready,
        "readiness_label": (
            READINESS_LABEL
            if ready
            else "Tower handoff acceptance gate blocked"
        ),
        "checks": checks,
        "current_recommendation": (
            CURRENT_RECOMMENDATION
        ),
        "acceptance_gate_status": (
            "handoff_packet_verified_"
            "tower_acceptance_contract_ready_"
            "acceptance_evidence_unsupplied_"
            "handoff_not_delivered_or_accepted"
        ),
        "next_recommended_layer": (
            "ARCHIVE VAULT — RECOVERY COMMIT "
            "OWNER DECISION TOWER HANDOFF "
            "ACCEPTANCE CLOSEOUT LAYER / GP651-GP660"
        ),
        "corridor_continues": True,
        "operational_readiness_gate_reached": False,
        "still_locked": [
            "no handoff delivery",
            "no handoff acceptance",
            "no acceptance decision recorded",
            "no Tower acceptance session created",
            "no Tower owner-review session started",
            "no owner authenticated",
            "no step-up satisfied",
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


def get_recovery_commit_owner_decision_tower_handoff_acceptance_home(
) -> Dict[str, Any]:
    checkpoint = (
        get_tower_handoff_acceptance_gate_readiness_checkpoint()
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


def validate_recovery_commit_owner_decision_tower_handoff_acceptance_gate(
) -> Dict[str, Any]:
    checkpoint = (
        get_tower_handoff_acceptance_gate_readiness_checkpoint()
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
        get_tower_handoff_acceptance_gate_readiness_checkpoint()
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


def get_gp641_status():
    return _gp_status(641)


def get_gp642_status():
    return _gp_status(642)


def get_gp643_status():
    return _gp_status(643)


def get_gp644_status():
    return _gp_status(644)


def get_gp645_status():
    return _gp_status(645)


def get_gp646_status():
    return _gp_status(646)


def get_gp647_status():
    return _gp_status(647)


def get_gp648_status():
    return _gp_status(648)


def get_gp649_status():
    return _gp_status(649)


def get_gp650_status():
    return _gp_status(650)
