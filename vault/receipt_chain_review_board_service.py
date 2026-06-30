"""
VAULT GIANT PACK 029 — Receipt Chain Review Board

CURRENT SECTION:
Archive Vault — Owner Action Receipt / Checklist Layer

This pack pulls GP028 checklist completion state into a receipt chain review board.

Important truth:
- GP029 is not an execution engine.
- GP029 does not auto-complete checklist rows.
- GP029 does not auto-confirm anything.
- GP029 does not mark owner confirmation complete.
- GP029 does not trigger execution after review, completion, or confirmation.
- GP029 does not create public proof.
- GP029 does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, seller/broker/trustee portals, financing decisions,
  legal advice, or Tower-owned permissions.
- Receipt chain review means grouped private metadata review, not completion.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.checklist_completion_state_service import get_checklist_completion_state_payload


PACK_ID = "VAULT_GP029"
PACK_NAME = "Receipt Chain Review Board"
SCHEMA_VERSION = "vault.receipt_chain_review_board.v1"

BOARD_STATUSES = {
    "OPEN_FOR_CHAIN_REVIEW": "Open for chain review",
    "BLOCKED_BY_TOWER_GATE": "Blocked by Tower gate",
    "BLOCKED_BY_OWNER_REVIEW": "Blocked by owner review",
    "READY_FOR_OWNER_REVIEW_EXECUTION_BLOCKED": "Ready for owner review — execution blocked",
    "CARRY_FORWARD_READY": "Carry-forward ready",
}

REVIEW_LANES = [
    {
        "lane_id": "receipt_chain_owner_review",
        "label": "Owner Review",
        "owner": "Vault",
        "tower_owned": False,
    },
    {
        "lane_id": "receipt_chain_tower_gate",
        "label": "Tower Gate",
        "owner": "The Tower",
        "tower_owned": True,
    },
    {
        "lane_id": "receipt_chain_completion_state",
        "label": "Completion State",
        "owner": "Vault",
        "tower_owned": False,
    },
    {
        "lane_id": "receipt_chain_blockers",
        "label": "Blockers",
        "owner": "Vault/Tower boundary",
        "tower_owned": False,
    },
    {
        "lane_id": "receipt_chain_carry_forward",
        "label": "Carry Forward",
        "owner": "Vault",
        "tower_owned": False,
    },
]

BOARD_BLOCK_CODES = {
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault reviews receipt chains but does not execute actions.",
    "NO_AUTO_CONFIRMATION": "Automatic confirmation is disabled.",
    "NO_AUTO_COMPLETION": "Automatic checklist completion is disabled.",
    "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
    "NO_EXECUTION_AFTER_COMPLETION": "Checklist completion does not trigger execution.",
    "NO_PUBLIC_RECEIPT_PROOF": "Owner action receipts are private and not public proof.",
    "DETAIL_DRAWER_PRIVATE_ONLY": "Receipt detail drawer is private only.",
    "CHECKLIST_COMPLETION_PRIVATE_ONLY": "Checklist completion state is private only.",
    "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY": "Receipt chain review board is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_receipt_chain_review_board_payload() -> Dict[str, Any]:
    gp028 = get_checklist_completion_state_payload()

    completion_records = gp028["completion_records"]
    completion_rows = gp028["completion_rows"]
    readiness_items = gp028["completion_readiness"]["readiness_items"]
    carry_forward_items = gp028["completion_carry_forward"]["carry_forward_items"]

    board_records = [
        _build_board_record(record, completion_rows, readiness_items, carry_forward_items)
        for record in completion_records
    ]

    chain_rows = [
        row
        for record in board_records
        for row in record["chain_rows"]
    ]

    review_lanes = _build_review_lanes(board_records, chain_rows)
    priority_queue = _build_priority_queue(board_records)
    completion_summary = _build_board_completion_summary(board_records, chain_rows)
    blockers = _build_board_blockers(board_records, chain_rows)
    carry_forward = _build_board_carry_forward(board_records)
    owner_queue = _build_owner_queue(board_records, chain_rows, review_lanes, blockers, carry_forward)

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
                "VAULT_GP028",
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "receipt_chain_review_board",
            "section": "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER",
        },
        "board_truth": {
            "receipt_chain_review_board_enabled": True,
            "metadata_only": True,
            "private_board_only": True,
            "receipt_chain_review_means_grouped_review_not_done": True,
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
            "public_board_proof_enabled": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp029",
            "safe_next_unlock": "GP030 can close this receipt/checklist layer as a readiness checkpoint without unlocking raw storage, external sharing, public proof, auto-completion, confirmation auto-run, or execution.",
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
        "board_summary": {
            "room_title": "Vault Receipt Chain Review Board",
            "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
            "route": "/vault/receipt-chain-review-board",
            "json_route": "/vault/receipt-chain-review-board.json",
            "records_route": "/vault/receipt-chain-review-board-records.json",
            "rows_route": "/vault/receipt-chain-review-board-rows.json",
            "lanes_route": "/vault/receipt-chain-review-board-lanes.json",
            "priority_route": "/vault/receipt-chain-review-board-priority.json",
            "completion_summary_route": "/vault/receipt-chain-review-board-completion-summary.json",
            "blockers_route": "/vault/receipt-chain-review-board-blockers.json",
            "carry_forward_route": "/vault/receipt-chain-review-board-carry-forward.json",
            "owner_queue_route": "/vault/receipt-chain-review-board-owner-queue.json",
            "gp029_status_route": "/vault/gp029-status.json",
            "board_record_count": len(board_records),
            "chain_row_count": len(chain_rows),
            "review_lane_count": review_lanes["lane_count"],
            "priority_item_count": priority_queue["priority_item_count"],
            "open_row_count": sum(1 for row in chain_rows if row["status"] == "OPEN"),
            "blocked_row_count": sum(1 for row in chain_rows if row["blocked"]),
            "completed_row_count": 0,
            "auto_completed_row_count": 0,
            "blocker_count": blockers["blocker_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "board_records": board_records,
        "chain_rows": chain_rows,
        "review_lanes": review_lanes,
        "priority_queue": priority_queue,
        "board_completion_summary": completion_summary,
        "board_blockers": blockers,
        "board_carry_forward": carry_forward,
        "owner_review_state": owner_queue,
        "gp028_connection": {
            "gp028_pack_id": gp028["pack"]["id"],
            "gp028_ready": gp028["gp028_status"]["ready"],
            "gp028_safe_to_continue": gp028["gp028_status"]["safe_to_continue_to_gp029"],
            "gp028_vault_done": gp028["gp028_status"]["vault_done"],
            "gp028_completion_record_count": gp028["completion_summary"]["completion_record_count"],
            "gp028_completion_row_count": gp028["completion_summary"]["completion_row_count"],
        },
        "gp029_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp028_completion_state_connected": True,
            "receipt_chain_review_board_ready": True,
            "safe_to_continue_to_gp030": True,
            "vault_done": False,
            "metadata_only_board": True,
            "private_board_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_disabled": True,
            "auto_confirmation_disabled": True,
            "execution_after_completion_disabled": True,
            "execution_after_confirmation_disabled": True,
            "execution_engine_disabled": True,
            "board_public_proof_disabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp029",
            "next_pack": "VAULT_GP030_OWNER_ACTION_RECEIPT_READINESS_CHECKPOINT_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _rows_for_completion_record(record: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if row["completion_record_id"] == record["completion_record_id"]]


def _readiness_for_completion_record(record: Dict[str, Any], readiness_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    for item in readiness_items:
        if item["completion_record_id"] == record["completion_record_id"]:
            return item
    return {}


def _carry_forward_for_completion_record(record: Dict[str, Any], carry_forward_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    for item in carry_forward_items:
        if item["completion_record_id"] == record["completion_record_id"]:
            return item
    return {}


def _build_board_record(
    completion_record: Dict[str, Any],
    completion_rows: List[Dict[str, Any]],
    readiness_items: List[Dict[str, Any]],
    carry_forward_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    related_rows = _rows_for_completion_record(completion_record, completion_rows)
    readiness = _readiness_for_completion_record(completion_record, readiness_items)
    carry_forward = _carry_forward_for_completion_record(completion_record, carry_forward_items)

    chain_rows = [
        _build_chain_row(completion_record, row, idx + 1)
        for idx, row in enumerate(related_rows)
    ]

    blocked_codes = set(completion_record.get("blocked_codes", []))
    blocked_codes.update({
        "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY",
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
        "board_record_id": f"VRB-{completion_record['completion_record_id'].replace('VCS-', '')}",
        "completion_record_id": completion_record["completion_record_id"],
        "drawer_id": completion_record["drawer_id"],
        "ledger_id": completion_record["ledger_id"],
        "receipt_id": completion_record["receipt_id"],
        "prep_id": completion_record["prep_id"],
        "source_step_id": completion_record["source_step_id"],
        "plan_packet_id": completion_record["plan_packet_id"],
        "title": completion_record["title"],
        "lane": completion_record["lane"],
        "board_status": "OPEN_FOR_CHAIN_REVIEW",
        "board_status_label": BOARD_STATUSES["OPEN_FOR_CHAIN_REVIEW"],
        "metadata_only": True,
        "private_board_only": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_after_review": False,
        "can_execute_after_completion": False,
        "can_execute_after_confirmation": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "public_proof_allowed": False,
        "raw_body_available": False,
        "external_share_allowed": False,
        "raw_export_allowed": False,
        "unredacted_export_allowed": False,
        "tower_gate_observed": completion_record["tower_gate_observed"],
        "tower_clearance_required": completion_record["tower_clearance_required"],
        "tower_step_up_required": completion_record["tower_step_up_required"],
        "readiness": readiness,
        "carry_forward": carry_forward,
        "chain_rows": chain_rows,
        "chain_row_count": len(chain_rows),
        "open_row_count": sum(1 for row in chain_rows if row["status"] == "OPEN"),
        "blocked_row_count": sum(1 for row in chain_rows if row["blocked"]),
        "completed_row_count": 0,
        "auto_completed_row_count": 0,
        "ready_for_owner_review": True,
        "ready_to_execute": False,
        "safe_to_carry_to_gp030": True,
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [BOARD_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Review receipt chain for {completion_record['title']} without completing, confirming, exporting, sharing, or executing.",
    }


def _build_chain_row(completion_record: Dict[str, Any], completion_row: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    blocked_codes = set(completion_row.get("blocked_codes", []))
    blocked_codes.update({
        "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_COMPLETION",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_COMPLETION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    })

    if completion_record.get("tower_clearance_required", False):
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    return {
        "chain_row_id": f"VBR-{completion_record['completion_record_id'].replace('VCS-', '')}-{sequence:02d}",
        "board_record_id": f"VRB-{completion_record['completion_record_id'].replace('VCS-', '')}",
        "completion_record_id": completion_record["completion_record_id"],
        "completion_row_id": completion_row["completion_row_id"],
        "drawer_id": completion_record["drawer_id"],
        "ledger_id": completion_record["ledger_id"],
        "receipt_id": completion_record["receipt_id"],
        "prep_id": completion_record["prep_id"],
        "state_type": completion_row["state_type"],
        "label": completion_row["label"],
        "sequence": sequence,
        "status": "OPEN",
        "board_state": "OPEN_FOR_CHAIN_REVIEW",
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


def _build_review_lanes(board_records: List[Dict[str, Any]], chain_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    lanes = []
    for lane in REVIEW_LANES:
        if lane["lane_id"] == "receipt_chain_tower_gate":
            affected_count = sum(1 for record in board_records if record["tower_clearance_required"] or record["tower_step_up_required"])
            blocked = True
        elif lane["lane_id"] == "receipt_chain_completion_state":
            affected_count = len(chain_rows)
            blocked = True
        elif lane["lane_id"] == "receipt_chain_carry_forward":
            affected_count = len(board_records)
            blocked = False
        else:
            affected_count = len(board_records)
            blocked = True

        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "label": lane["label"],
                "owner": lane["owner"],
                "tower_owned": lane["tower_owned"],
                "affected_record_count": affected_count,
                "lane_status": "LOCKED_OR_REVIEW_ONLY" if blocked else "CARRY_FORWARD_READY",
                "blocked": blocked,
                "auto_complete_allowed": False,
                "auto_confirm_allowed": False,
                "execution_allowed": False,
                "external_share_allowed": False,
            }
        )

    return {
        "lanes": lanes,
        "lane_count": len(lanes),
        "blocked_lane_count": sum(1 for lane in lanes if lane["blocked"]),
        "tower_owned_lane_count": sum(1 for lane in lanes if lane["tower_owned"]),
        "execution_allowed_count": 0,
        "all_review_lanes_private": True,
    }


def _build_priority_queue(board_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_records = sorted(
        board_records,
        key=lambda record: (
            0 if "atm" in record["plan_packet_id"] else
            1 if "apartment" in record["plan_packet_id"] else
            2 if "trust" in record["plan_packet_id"] else
            3,
            record["title"],
        )
    )

    priority_items = [
        {
            "priority_id": f"RCB-P{idx:03d}",
            "board_record_id": record["board_record_id"],
            "completion_record_id": record["completion_record_id"],
            "drawer_id": record["drawer_id"],
            "ledger_id": record["ledger_id"],
            "receipt_id": record["receipt_id"],
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "priority_rank": idx,
            "priority_reason": _priority_reason(record),
            "owner_review_required": True,
            "owner_confirmed": False,
            "auto_complete_allowed": False,
            "can_execute_from_vault": False,
            "safe_to_carry_to_gp030": True,
        }
        for idx, record in enumerate(sorted_records, start=1)
    ]

    return {
        "priority_items": priority_items,
        "priority_item_count": len(priority_items),
        "first_priority_receipt_id": priority_items[0]["receipt_id"] if priority_items else None,
        "owner_review_required": True,
        "auto_complete_allowed": False,
        "execution_allowed_count": 0,
        "safe_to_carry_to_gp030": True,
    }


def _priority_reason(record: Dict[str, Any]) -> str:
    packet_id = record.get("plan_packet_id") or ""
    if "atm" in packet_id:
        return "ATM acquisition packet receipts stay first."
    if "apartment" in packet_id:
        return "Apartment lender packet receipts stay second."
    if "trust" in packet_id:
        return "Trust/entity authority receipts stay third."
    return "General receipt chain review priority."


def _build_board_completion_summary(board_records: List[Dict[str, Any]], chain_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "summary_id": "RCB-COMPLETION-SUMMARY",
        "board_record_count": len(board_records),
        "chain_row_count": len(chain_rows),
        "open_row_count": sum(1 for row in chain_rows if row["status"] == "OPEN"),
        "blocked_row_count": sum(1 for row in chain_rows if row["blocked"]),
        "completed_row_count": 0,
        "auto_completed_row_count": 0,
        "owner_review_required_count": len(board_records),
        "owner_confirmed_count": 0,
        "ready_for_owner_review_count": sum(1 for record in board_records if record["ready_for_owner_review"]),
        "ready_to_execute_count": 0,
        "execution_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "completion_truth": "Receipt chain review summarizes completion state but does not mark anything complete.",
    }


def _build_board_blockers(board_records: List[Dict[str, Any]], chain_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted(
        {code for record in board_records for code in record["blocked_codes"]}
        | {code for row in chain_rows for code in row["blocked_codes"]}
    )

    blockers = [
        {
            "code": code,
            "label": BOARD_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_board_record_count": sum(1 for record in board_records if code in record["blocked_codes"]),
            "affected_chain_row_count": sum(1 for row in chain_rows if code in row["blocked_codes"]),
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
        "execution_after_review_allowed": False,
        "execution_after_completion_allowed": False,
        "execution_after_confirmation_allowed": False,
        "public_board_proof_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only receipt chain review. Do not display raw bodies.",
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
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault reviews receipt chains but does not execute actions.",
        "NO_AUTO_CONFIRMATION": "Do not auto-confirm owner actions.",
        "NO_AUTO_COMPLETION": "Do not auto-complete checklist rows.",
        "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
        "NO_EXECUTION_AFTER_COMPLETION": "Completion does not trigger execution.",
        "NO_PUBLIC_RECEIPT_PROOF": "Keep owner action receipts private.",
        "DETAIL_DRAWER_PRIVATE_ONLY": "Keep drawer private and metadata-only.",
        "CHECKLIST_COMPLETION_PRIVATE_ONLY": "Keep checklist completion state private.",
        "RECEIPT_CHAIN_REVIEW_PRIVATE_ONLY": "Keep receipt chain review board private.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP029.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_board_carry_forward(board_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    carry_items = [
        {
            "board_carry_forward_id": f"RCB-CF-{record['board_record_id'].replace('VRB-', '')}",
            "board_record_id": record["board_record_id"],
            "completion_record_id": record["completion_record_id"],
            "drawer_id": record["drawer_id"],
            "ledger_id": record["ledger_id"],
            "receipt_id": record["receipt_id"],
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "carry_forward_status": "READY_FOR_GP030_OWNER_ACTION_RECEIPT_READINESS_CHECKPOINT",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed_count": 0,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "execution_allowed": False,
            "public_proof_allowed": False,
            "safe_to_carry_to_gp030": True,
        }
        for record in board_records
    ]

    return {
        "carry_forward_items": carry_items,
        "carry_forward_count": len(carry_items),
        "ready_for_gp030_count": len(carry_items),
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "auto_completed_count": 0,
        "execution_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "safe_to_carry_to_gp030": True,
    }


def _build_owner_queue(
    board_records: List[Dict[str, Any]],
    chain_rows: List[Dict[str, Any]],
    review_lanes: Dict[str, Any],
    blockers: Dict[str, Any],
    carry_forward: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "RCB-ACTION-001",
            "label": "Review receipt chain board records.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "RCB-ACTION-002",
            "label": "Review open and blocked chain rows without marking completion.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "RCB-ACTION-003",
            "label": "Use priority queue for owner review order.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "RCB-ACTION-004",
            "label": "Keep Tower gate checks, step-up, portals, exports, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "RCB-ACTION-005",
            "label": "Continue Vault into GP030 owner action receipt readiness checkpoint.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Receipt Chain Review Board",
        "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
        "actions": actions,
        "action_count": len(actions),
        "board_record_count": len(board_records),
        "chain_row_count": len(chain_rows),
        "review_lane_count": review_lanes["lane_count"],
        "blocker_count": blockers["blocker_count"],
        "carry_forward_count": carry_forward["carry_forward_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review receipt chain board records.",
            "Review open and blocked chain rows without marking completion.",
            "Use priority queue for owner review order.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP030 owner action receipt readiness checkpoint.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_receipt_chain_review_board_payload())


def get_receipt_chain_review_board_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "board_truth": payload["board_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "board_summary": payload["board_summary"],
        "gp028_connection": payload["gp028_connection"],
    }


def get_receipt_chain_review_board_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "board_records": payload["board_records"],
        "board_record_count": len(payload["board_records"]),
    }


def get_receipt_chain_review_board_rows() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "chain_rows": payload["chain_rows"],
        "chain_row_count": len(payload["chain_rows"]),
    }


def get_receipt_chain_review_board_lanes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_lanes": payload["review_lanes"],
    }


def get_receipt_chain_review_board_priority() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "priority_queue": payload["priority_queue"],
    }


def get_receipt_chain_review_board_completion_summary() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "board_completion_summary": payload["board_completion_summary"],
    }


def get_receipt_chain_review_board_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "board_blockers": payload["board_blockers"],
    }


def get_receipt_chain_review_board_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "board_carry_forward": payload["board_carry_forward"],
    }


def get_receipt_chain_review_board_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp029_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp029_status": payload["gp029_status"],
        "board_truth": payload["board_truth"],
        "board_summary": payload["board_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp028_connection": payload["gp028_connection"],
    }


def render_receipt_chain_review_board_page() -> str:
    payload = clone_payload()
    summary = payload["board_summary"]
    truth = payload["board_truth"]
    board_records = payload["board_records"]
    priority = payload["priority_queue"]
    owner = payload["owner_review_state"]

    record_cards = "\n".join(_render_board_card(record) for record in board_records[:9])
    priority_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["title"])}</strong>
            <span>{escape(item["priority_reason"])} · rank {item["priority_rank"]}</span>
          </div>
          <div class="pill warn">Priority {item["priority_rank"]}</div>
        </div>
        """
        for item in priority["priority_items"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Receipt Chain Review Board · GP029</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 029</div>
        <h1>Receipt Chain Review Board</h1>
        <p class="hero-copy">
          GP029 groups private receipt, drawer, ledger, checklist, completion, blocker, and carry-forward state into
          one review board. It keeps the board metadata-only and private. Review does not mean complete, confirm,
          execute, export, share, or create public proof.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["board_record_count"]}</strong>
            <span>board records</span>
          </div>
          <div class="metric">
            <strong>{summary["chain_row_count"]}</strong>
            <span>chain rows</span>
          </div>
          <div class="metric">
            <strong>{summary["review_lane_count"]}</strong>
            <span>review lanes</span>
          </div>
          <div class="metric">
            <strong>{summary["completed_row_count"]}</strong>
            <span>completed rows</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Review board ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Execution disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Board Records</h2>
      <p>
        Each board record groups one receipt chain for owner review without marking anything complete.
      </p>
      <div class="grid">
        {record_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Priority Queue</h2>
        <p>ATM, apartment, and trust/entity receipt chains stay high-priority.</p>
        <div>
          {priority_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP029 prepares GP030 owner action receipt readiness checkpoint.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP029 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["records_route"])}</code>
        <code>{escape(summary["rows_route"])}</code>
        <code>{escape(summary["lanes_route"])}</code>
        <code>{escape(summary["priority_route"])}</code>
        <code>{escape(summary["completion_summary_route"])}</code>
        <code>{escape(summary["blockers_route"])}</code>
        <code>{escape(summary["carry_forward_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp029_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Board Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Completed count:
        <code>{truth["completed_count"]}</code>.
        Execution engine:
        <code>{str(truth["execution_engine_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_board_card(record: Dict[str, Any]) -> str:
    status_class = "danger" if record["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record["title"])}</div>
            <div class="meta">
              Board: <code>{escape(record["board_record_id"])}</code><br>
              Completion: <code>{escape(record["completion_record_id"])}</code><br>
              Receipt: <code>{escape(record["receipt_id"])}</code><br>
              Open rows: <code>{record["open_row_count"]}</code><br>
              Completed rows: <code>{record["completed_row_count"]}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(record["board_status"])}</span>
        </div>
      </article>
    """
