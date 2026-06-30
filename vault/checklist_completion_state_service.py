"""
VAULT GIANT PACK 028 — Checklist Completion State

CURRENT SECTION:
Archive Vault — Owner Action Receipt / Checklist Layer

This pack turns GP027 drawer checklist rows into completion-state records.

Important truth:
- GP028 is not an execution engine.
- GP028 does not auto-complete checklist rows.
- GP028 does not auto-confirm anything.
- GP028 does not mark owner confirmation complete.
- GP028 does not trigger execution after checklist review.
- GP028 does not create public proof.
- GP028 does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, seller/broker/trustee portals, financing decisions,
  legal advice, or Tower-owned permissions.
- Completion state means open / blocked / ready for owner review, not complete.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.action_receipt_detail_drawer_service import get_action_receipt_detail_drawer_payload


PACK_ID = "VAULT_GP028"
PACK_NAME = "Checklist Completion State"
SCHEMA_VERSION = "vault.checklist_completion_state.v1"

COMPLETION_STATUSES = {
    "OPEN_OWNER_REVIEW_REQUIRED": "Open — owner review required",
    "BLOCKED_BY_TOWER_GATE": "Blocked by Tower gate",
    "BLOCKED_BY_OWNER_CONFIRMATION": "Blocked by owner confirmation",
    "READY_TO_REVIEW_EXECUTION_BLOCKED": "Ready to review — execution blocked",
    "CARRY_FORWARD_READY": "Carry-forward ready",
}

COMPLETION_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "TOWER_STEP_UP_REQUIRED": "Tower step-up is required before sensitive action.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before closure.",
    "OWNER_REVIEW_REQUIRED": "Owner review is required before completion.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "NO_AUTO_ACTION_EXECUTION": "Automatic action execution is disabled.",
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault tracks completion state but does not execute actions.",
    "NO_AUTO_CONFIRMATION": "Automatic confirmation is disabled.",
    "NO_AUTO_COMPLETION": "Automatic checklist completion is disabled.",
    "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
    "NO_EXECUTION_AFTER_COMPLETION": "Checklist completion does not trigger execution.",
    "NO_PUBLIC_RECEIPT_PROOF": "Owner action receipts are private and not public proof.",
    "DETAIL_DRAWER_PRIVATE_ONLY": "Receipt detail drawer is private only.",
    "CHECKLIST_COMPLETION_PRIVATE_ONLY": "Checklist completion state is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_checklist_completion_state_payload() -> Dict[str, Any]:
    gp027 = get_action_receipt_detail_drawer_payload()

    drawer_records = gp027["drawer_records"]
    detail_checklist_rows = gp027["detail_checklist_rows"]
    tower_gate_details = gp027["tower_gate_detail"]["tower_gate_details"]

    completion_records = [
        _build_completion_record(drawer, detail_checklist_rows, tower_gate_details)
        for drawer in drawer_records
    ]

    completion_rows = [
        row
        for record in completion_records
        for row in record["completion_rows"]
    ]

    blocker_detail = _build_completion_blockers(completion_records, completion_rows)
    readiness = _build_completion_readiness(completion_records, completion_rows)
    carry_forward = _build_completion_carry_forward(completion_records)
    owner_queue = _build_owner_queue(completion_records, completion_rows, blocker_detail, readiness, carry_forward)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": [
                "VAULT_GP011",
                "VAULT_GP012",
                "VAULT_GP013",
                "VAULT_GP014",
                "VAULT_GP015",
                "VAULT_GP016",
                "VAULT_GP017",
                "VAULT_GP018",
                "VAULT_GP019",
                "VAULT_GP020",
                "VAULT_GP021",
                "VAULT_GP022",
                "VAULT_GP023",
                "VAULT_GP024",
                "VAULT_GP025",
                "VAULT_GP026",
                "VAULT_GP027",
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "checklist_completion_state",
            "section": "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER",
        },
        "completion_truth": {
            "checklist_completion_state_enabled": True,
            "metadata_only": True,
            "private_completion_state_only": True,
            "completion_means_status_tracking_not_done": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_enabled": False,
            "auto_confirmation_enabled": False,
            "execution_after_completion_enabled": False,
            "execution_after_confirmation_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "public_completion_proof_enabled": False,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "external_access_enabled": False,
            "unredacted_export_enabled": False,
            "raw_export_enabled": False,
            "public_proof_enabled": False,
            "portal_access_enabled": False,
            "financing_decision_enabled": False,
            "legal_advice_enabled": False,
            "raw_document_verification_claimed": False,
            "auto_packet_approval_enabled": False,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp028",
            "safe_next_unlock": "GP029 can deepen receipt chain review board without unlocking raw storage, external sharing, public proof, auto-completion, confirmation auto-run, or execution.",
        },
        "tower_authority": {
            "tower_owns_identity": True,
            "tower_owns_permissions": True,
            "tower_owns_clearance": True,
            "tower_owns_step_up": True,
            "tower_owns_export_locks": True,
            "tower_owns_freeze_revoke": True,
            "tower_owns_external_access": True,
            "tower_owns_portal_unlocks": True,
            "tower_owns_sensitive_visibility": True,
            "tower_owns_action_authority_gates": True,
            "vault_owns_tower_permissions": False,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "completion_summary": {
            "room_title": "Vault Checklist Completion State",
            "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
            "route": "/vault/checklist-completion-state",
            "json_route": "/vault/checklist-completion-state.json",
            "records_route": "/vault/checklist-completion-state-records.json",
            "rows_route": "/vault/checklist-completion-state-rows.json",
            "blockers_route": "/vault/checklist-completion-state-blockers.json",
            "readiness_route": "/vault/checklist-completion-state-readiness.json",
            "carry_forward_route": "/vault/checklist-completion-state-carry-forward.json",
            "owner_queue_route": "/vault/checklist-completion-state-owner-queue.json",
            "gp028_status_route": "/vault/gp028-status.json",
            "completion_record_count": len(completion_records),
            "completion_row_count": len(completion_rows),
            "open_row_count": sum(1 for row in completion_rows if row["status"] == "OPEN"),
            "blocked_row_count": sum(1 for row in completion_rows if row["blocked"]),
            "completed_row_count": 0,
            "auto_completed_row_count": 0,
            "readiness_item_count": readiness["readiness_item_count"],
            "blocker_count": blocker_detail["blocker_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "completion_records": completion_records,
        "completion_rows": completion_rows,
        "completion_blockers": blocker_detail,
        "completion_readiness": readiness,
        "completion_carry_forward": carry_forward,
        "owner_review_state": owner_queue,
        "gp027_connection": {
            "gp027_pack_id": gp027["pack"]["id"],
            "gp027_ready": gp027["gp027_status"]["ready"],
            "gp027_safe_to_continue": gp027["gp027_status"]["safe_to_continue_to_gp028"],
            "gp027_vault_done": gp027["gp027_status"]["vault_done"],
            "gp027_drawer_record_count": gp027["drawer_summary"]["drawer_record_count"],
            "gp027_detail_checklist_row_count": gp027["drawer_summary"]["detail_checklist_row_count"],
        },
        "gp028_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp027_detail_drawer_connected": True,
            "checklist_completion_state_ready": True,
            "safe_to_continue_to_gp029": True,
            "vault_done": False,
            "metadata_only_completion_state": True,
            "private_completion_state_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_disabled": True,
            "auto_confirmation_disabled": True,
            "execution_after_completion_disabled": True,
            "execution_after_confirmation_disabled": True,
            "execution_engine_disabled": True,
            "completion_public_proof_disabled": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "external_access_still_locked": True,
            "unredacted_export_still_locked": True,
            "raw_export_still_locked": True,
            "public_proof_still_locked": True,
            "portal_access_still_locked": True,
            "financing_decision_not_claimed": True,
            "legal_advice_not_claimed": True,
            "raw_verification_not_claimed": True,
            "auto_action_execution_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp028",
            "next_pack": "VAULT_GP029_RECEIPT_CHAIN_REVIEW_BOARD_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _rows_for_drawer(drawer: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if row["drawer_id"] == drawer["drawer_id"]]


def _tower_gate_for_drawer(drawer: Dict[str, Any], gates: List[Dict[str, Any]]) -> Dict[str, Any]:
    for gate in gates:
        if gate["drawer_id"] == drawer["drawer_id"]:
            return gate
    return {}


def _build_completion_record(
    drawer: Dict[str, Any],
    detail_checklist_rows: List[Dict[str, Any]],
    tower_gate_details: List[Dict[str, Any]],
) -> Dict[str, Any]:
    related_rows = _rows_for_drawer(drawer, detail_checklist_rows)
    tower_gate = _tower_gate_for_drawer(drawer, tower_gate_details)

    completion_rows = [
        _build_completion_row(drawer, row, idx + 1, tower_gate)
        for idx, row in enumerate(related_rows)
    ]

    blocked_codes = set(drawer.get("blocked_codes", []))
    blocked_codes.update({
        "CHECKLIST_COMPLETION_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_COMPLETION",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_COMPLETION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_PUBLIC_RECEIPT_PROOF",
        "CLOUDS_PARKED",
    })

    return {
        "completion_record_id": f"VCS-{drawer['drawer_id'].replace('VDD-', '')}",
        "drawer_id": drawer["drawer_id"],
        "ledger_id": drawer["ledger_id"],
        "receipt_id": drawer["receipt_id"],
        "prep_id": drawer["prep_id"],
        "source_step_id": drawer["source_step_id"],
        "plan_packet_id": drawer["plan_packet_id"],
        "title": drawer["title"],
        "lane": drawer["lane"],
        "completion_status": "OPEN_OWNER_REVIEW_REQUIRED",
        "completion_status_label": COMPLETION_STATUSES["OPEN_OWNER_REVIEW_REQUIRED"],
        "metadata_only": True,
        "private_completion_state_only": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_after_completion": False,
        "can_execute_after_confirmation": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "public_proof_allowed": False,
        "raw_body_available": False,
        "external_share_allowed": False,
        "raw_export_allowed": False,
        "unredacted_export_allowed": False,
        "tower_gate_observed": tower_gate.get("tower_gate_observed", True),
        "tower_clearance_required": tower_gate.get("tower_clearance_required", drawer["tower_clearance_required"]),
        "tower_step_up_required": tower_gate.get("tower_step_up_required", drawer["tower_step_up_required"]),
        "completion_rows": completion_rows,
        "completion_row_count": len(completion_rows),
        "open_row_count": sum(1 for row in completion_rows if row["status"] == "OPEN"),
        "blocked_row_count": sum(1 for row in completion_rows if row["blocked"]),
        "completed_row_count": 0,
        "auto_completed_row_count": 0,
        "ready_to_review": True,
        "ready_to_execute": False,
        "safe_to_carry_to_gp029": True,
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [COMPLETION_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Review checklist completion state for {drawer['title']} without completing, confirming, exporting, sharing, or executing.",
    }


def _build_completion_row(
    drawer: Dict[str, Any],
    detail_row: Dict[str, Any],
    sequence: int,
    tower_gate: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_codes = set(detail_row.get("blocked_codes", []))
    blocked_codes.update({
        "CHECKLIST_COMPLETION_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_COMPLETION",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_COMPLETION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    })

    if tower_gate.get("tower_clearance_required", drawer["tower_clearance_required"]):
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    row_status = "OPEN"
    completion_state = "OPEN_OWNER_REVIEW_REQUIRED"
    if "TOWER_CLEARANCE_REQUIRED" in blocked_codes:
        completion_state = "BLOCKED_BY_TOWER_GATE"
    elif "OWNER_CONFIRMATION_REQUIRED" in blocked_codes:
        completion_state = "BLOCKED_BY_OWNER_CONFIRMATION"

    return {
        "completion_row_id": f"VCR-{drawer['drawer_id'].replace('VDD-', '')}-{sequence:02d}",
        "completion_record_id": f"VCS-{drawer['drawer_id'].replace('VDD-', '')}",
        "drawer_id": drawer["drawer_id"],
        "ledger_id": drawer["ledger_id"],
        "receipt_id": drawer["receipt_id"],
        "prep_id": drawer["prep_id"],
        "detail_checklist_id": detail_row["detail_checklist_id"],
        "review_state_id": detail_row["review_state_id"],
        "state_type": detail_row["state_type"],
        "label": detail_row["label"],
        "sequence": sequence,
        "required": True,
        "status": row_status,
        "completion_state": completion_state,
        "completion_state_label": COMPLETION_STATUSES[completion_state],
        "blocked": True,
        "completed": False,
        "auto_completed": False,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_after_completion": False,
        "can_execute_after_confirmation": False,
        "can_execute_from_vault": False,
        "metadata_only": True,
        "public_proof_allowed": False,
        "external_share_allowed": False,
        "blocked_codes": sorted(blocked_codes),
    }


def _build_completion_blockers(
    completion_records: List[Dict[str, Any]],
    completion_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    active_codes = sorted(
        {code for record in completion_records for code in record["blocked_codes"]}
        | {code for row in completion_rows for code in row["blocked_codes"]}
    )

    blockers = [
        {
            "code": code,
            "label": COMPLETION_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_record_count": sum(1 for record in completion_records if code in record["blocked_codes"]),
            "affected_row_count": sum(1 for row in completion_rows if code in row["blocked_codes"]),
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]

    return {
        "blockers": blockers,
        "blocker_count": len(blockers),
        "all_blockers_safe": True,
        "auto_override_allowed": False,
        "all_restricted_paths_locked": True,
        "auto_completion_allowed": False,
        "auto_confirmation_allowed": False,
        "execution_after_completion_allowed": False,
        "execution_after_confirmation_allowed": False,
        "public_completion_proof_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only completion review. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "TOWER_STEP_UP_REQUIRED": "Tower must own step-up before sensitive action.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before closure.",
        "OWNER_REVIEW_REQUIRED": "Require owner review before completion.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault tracks completion state but does not execute actions.",
        "NO_AUTO_CONFIRMATION": "Do not auto-confirm owner actions.",
        "NO_AUTO_COMPLETION": "Do not auto-complete checklist rows.",
        "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
        "NO_EXECUTION_AFTER_COMPLETION": "Completion does not trigger execution.",
        "NO_PUBLIC_RECEIPT_PROOF": "Keep owner action receipts private.",
        "DETAIL_DRAWER_PRIVATE_ONLY": "Keep drawer private and metadata-only.",
        "CHECKLIST_COMPLETION_PRIVATE_ONLY": "Keep checklist completion state private.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP028.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_completion_readiness(
    completion_records: List[Dict[str, Any]],
    completion_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_items = [
        {
            "readiness_id": f"VCSR-{record['completion_record_id'].replace('VCS-', '')}",
            "completion_record_id": record["completion_record_id"],
            "drawer_id": record["drawer_id"],
            "ledger_id": record["ledger_id"],
            "receipt_id": record["receipt_id"],
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "readiness_status": "READY_TO_REVIEW_EXECUTION_BLOCKED",
            "open_row_count": record["open_row_count"],
            "blocked_row_count": record["blocked_row_count"],
            "completed_row_count": 0,
            "owner_review_required": True,
            "owner_confirmed": False,
            "auto_complete_allowed": False,
            "can_execute_from_vault": False,
            "safe_to_carry_to_gp029": True,
        }
        for record in completion_records
    ]

    return {
        "readiness_items": readiness_items,
        "readiness_item_count": len(readiness_items),
        "ready_to_review_count": len(readiness_items),
        "completion_allowed_count": 0,
        "execution_allowed_count": 0,
        "owner_confirmed_count": 0,
        "auto_completed_count": 0,
        "total_open_row_count": sum(1 for row in completion_rows if row["status"] == "OPEN"),
        "total_completed_row_count": 0,
        "safe_to_carry_to_gp029": True,
    }


def _build_completion_carry_forward(completion_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    carry_items = [
        {
            "completion_carry_forward_id": f"VCCF-{record['completion_record_id'].replace('VCS-', '')}",
            "completion_record_id": record["completion_record_id"],
            "drawer_id": record["drawer_id"],
            "ledger_id": record["ledger_id"],
            "receipt_id": record["receipt_id"],
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "carry_forward_status": "READY_FOR_GP029_RECEIPT_CHAIN_REVIEW_BOARD",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed_count": 0,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "execution_allowed": False,
            "public_proof_allowed": False,
            "safe_to_carry_to_gp029": True,
        }
        for record in completion_records
    ]

    return {
        "carry_forward_items": carry_items,
        "carry_forward_count": len(carry_items),
        "ready_for_gp029_count": len(carry_items),
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "auto_completed_count": 0,
        "execution_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "safe_to_carry_to_gp029": True,
    }


def _build_owner_queue(
    completion_records: List[Dict[str, Any]],
    completion_rows: List[Dict[str, Any]],
    blocker_detail: Dict[str, Any],
    readiness: Dict[str, Any],
    carry_forward: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "CCS-ACTION-001",
            "label": "Review checklist completion-state records.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CCS-ACTION-002",
            "label": "Keep checklist rows open until owner review.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CCS-ACTION-003",
            "label": "Keep auto-completion and auto-confirmation disabled.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CCS-ACTION-004",
            "label": "Keep Tower gate checks, step-up, portals, exports, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CCS-ACTION-005",
            "label": "Continue Vault into GP029 receipt chain review board.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Checklist Completion State",
        "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
        "actions": actions,
        "action_count": len(actions),
        "completion_record_count": len(completion_records),
        "completion_row_count": len(completion_rows),
        "blocker_count": blocker_detail["blocker_count"],
        "readiness_item_count": readiness["readiness_item_count"],
        "carry_forward_count": carry_forward["carry_forward_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review checklist completion-state records.",
            "Keep checklist rows open until owner review.",
            "Keep auto-completion and auto-confirmation disabled.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP029 receipt chain review board.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_checklist_completion_state_payload())


def get_checklist_completion_state_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "completion_truth": payload["completion_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "completion_summary": payload["completion_summary"],
        "gp027_connection": payload["gp027_connection"],
    }


def get_checklist_completion_state_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "completion_records": payload["completion_records"],
        "completion_record_count": len(payload["completion_records"]),
    }


def get_checklist_completion_state_rows() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "completion_rows": payload["completion_rows"],
        "completion_row_count": len(payload["completion_rows"]),
    }


def get_checklist_completion_state_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "completion_blockers": payload["completion_blockers"],
    }


def get_checklist_completion_state_readiness() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "completion_readiness": payload["completion_readiness"],
    }


def get_checklist_completion_state_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "completion_carry_forward": payload["completion_carry_forward"],
    }


def get_checklist_completion_state_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp028_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp028_status": payload["gp028_status"],
        "completion_truth": payload["completion_truth"],
        "completion_summary": payload["completion_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp027_connection": payload["gp027_connection"],
    }


def render_checklist_completion_state_page() -> str:
    payload = clone_payload()
    summary = payload["completion_summary"]
    truth = payload["completion_truth"]
    records = payload["completion_records"]
    readiness = payload["completion_readiness"]
    owner = payload["owner_review_state"]

    record_cards = "\n".join(_render_completion_card(record) for record in records[:9])
    readiness_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["title"])}</strong>
            <span>{escape(item["readiness_status"])} · open rows: {item["open_row_count"]} · completed rows: {item["completed_row_count"]}</span>
          </div>
          <div class="pill warn">Review ready</div>
        </div>
        """
        for item in readiness["readiness_items"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Checklist Completion State · GP028</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090d22;
      --panel: rgba(15, 23, 52, 0.84);
      --panel2: rgba(21, 32, 74, 0.76);
      --line: rgba(160, 179, 255, 0.24);
      --text: #eef3ff;
      --muted: #9da9d7;
      --gold: #f5d17e;
      --violet: #ad8dff;
      --cyan: #83eaff;
      --danger: #ff8c9c;
      --ok: #9dffca;
      --shadow: rgba(0, 0, 0, 0.50);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 13% 9%, rgba(173, 141, 255, 0.18), transparent 34%),
        radial-gradient(circle at 88% 5%, rgba(131, 234, 255, 0.13), transparent 30%),
        radial-gradient(circle at 70% 90%, rgba(245, 209, 126, 0.09), transparent 32%),
        linear-gradient(135deg, var(--bg0), var(--bg1) 52%, #03040b);
    }}

    .shell {{
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
      padding: 34px 0 48px;
    }}

    .hero {{
      border: 1px solid var(--line);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(145deg, rgba(15, 23, 52, 0.94), rgba(6, 10, 25, 0.74));
      box-shadow: 0 28px 74px var(--shadow);
      overflow: hidden;
      position: relative;
    }}

    .hero:before {{
      content: "";
      position: absolute;
      inset: -2px;
      background:
        radial-gradient(circle at 16% 0%, rgba(245, 209, 126, 0.18), transparent 28%),
        radial-gradient(circle at 94% 34%, rgba(131, 234, 255, 0.12), transparent 26%);
      pointer-events: none;
    }}

    .hero-inner {{
      position: relative;
      z-index: 1;
    }}

    .eyebrow {{
      color: var(--gold);
      letter-spacing: .18em;
      text-transform: uppercase;
      font-size: 12px;
      font-weight: 850;
    }}

    h1 {{
      margin: 14px 0 14px;
      font-size: clamp(34px, 5vw, 62px);
      line-height: .95;
    }}

    p {{
      color: var(--muted);
      line-height: 1.62;
    }}

    .hero-copy {{
      max-width: 920px;
      font-size: 16px;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 22px;
    }}

    .metric {{
      border: 1px solid var(--line);
      background: rgba(5, 8, 20, 0.48);
      border-radius: 20px;
      padding: 16px;
    }}

    .metric strong {{
      display: block;
      font-size: 26px;
    }}

    .metric span {{
      color: var(--muted);
      font-size: 13px;
    }}

    .section {{
      margin-top: 18px;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 24px;
      padding: 22px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, .28);
    }}

    .section h2 {{
      margin: 0 0 10px;
      font-size: 22px;
    }}

    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 800;
      color: var(--text);
      background: rgba(10, 16, 38, .72);
      white-space: nowrap;
    }}

    .pill.ok {{
      color: var(--ok);
      border-color: rgba(157, 255, 202, .32);
    }}

    .pill.warn {{
      color: var(--gold);
      border-color: rgba(245, 209, 126, .32);
    }}

    .pill.danger {{
      color: var(--danger);
      border-color: rgba(255, 140, 156, .32);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 16px;
    }}

    .card {{
      border: 1px solid var(--line);
      background: var(--panel2);
      border-radius: 20px;
      padding: 16px;
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }}

    .title {{
      font-weight: 900;
      font-size: 15px;
    }}

    .meta {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
      line-height: 1.55;
    }}

    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }}

    .status-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 12px 0;
      border-bottom: 1px solid rgba(160, 179, 255, .14);
    }}

    .status-row:last-child {{
      border-bottom: none;
    }}

    .status-row span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }}

    code {{
      color: var(--cyan);
      background: rgba(0, 0, 0, .28);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 2px 6px;
    }}

    ul {{
      margin: 14px 0 0;
      color: var(--muted);
      line-height: 1.75;
    }}

    @media (max-width: 1020px) {{
      .metrics,
      .grid,
      .two-col {{
        grid-template-columns: 1fr;
      }}

      .card-top,
      .status-row {{
        flex-direction: column;
        align-items: flex-start;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="hero-inner">
        <div class="eyebrow">Archive Vault · Giant Pack 028</div>
        <h1>Checklist Completion State</h1>
        <p class="hero-copy">
          GP028 turns action receipt drawer checklist rows into open/blocked/ready-to-review completion state.
          Completion state does not mean done. It keeps owner review required, auto-completion disabled,
          auto-confirmation disabled, execution blocked, raw storage locked, external sharing locked, and public proof disabled.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["completion_record_count"]}</strong>
            <span>completion records</span>
          </div>
          <div class="metric">
            <strong>{summary["completion_row_count"]}</strong>
            <span>completion rows</span>
          </div>
          <div class="metric">
            <strong>{summary["open_row_count"]}</strong>
            <span>open rows</span>
          </div>
          <div class="metric">
            <strong>{summary["completed_row_count"]}</strong>
            <span>completed rows</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Completion state ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Auto-complete disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Completion Records</h2>
      <p>
        Each record shows open and blocked checklist state without marking anything complete.
      </p>
      <div class="grid">
        {record_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Readiness Queue</h2>
        <p>Rows are ready for owner review, not execution.</p>
        <div>
          {readiness_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP028 prepares GP029 receipt chain review board.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP028 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["records_route"])}</code>
        <code>{escape(summary["rows_route"])}</code>
        <code>{escape(summary["blockers_route"])}</code>
        <code>{escape(summary["readiness_route"])}</code>
        <code>{escape(summary["carry_forward_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp028_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Completion Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Auto-completion:
        <code>{str(truth["auto_completion_enabled"]).lower()}</code>.
        Completed count:
        <code>{truth["completed_count"]}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_completion_card(record: Dict[str, Any]) -> str:
    status_class = "danger" if record["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record["title"])}</div>
            <div class="meta">
              Completion: <code>{escape(record["completion_record_id"])}</code><br>
              Drawer: <code>{escape(record["drawer_id"])}</code><br>
              Receipt: <code>{escape(record["receipt_id"])}</code><br>
              Open rows: <code>{record["open_row_count"]}</code><br>
              Completed rows: <code>{record["completed_row_count"]}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(record["completion_status"])}</span>
        </div>
      </article>
    """
