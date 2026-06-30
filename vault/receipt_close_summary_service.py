"""
VAULT GIANT PACK 039 — Receipt Close Summary

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP038 receipt review close staging by creating private summary
surfaces for the controlled packet assembly layer before the GP040 section checkpoint.

Purpose:
- Build a receipt close summary board from close cards.
- Summarize unresolved close blockers.
- Summarize receipt-not-final warnings.
- Summarize Tower/owner close readiness.
- Summarize no-execution proof.
- Roll up GP031-GP038 controlled packet assembly progress.
- Sort next summary items.
- Carry forward into GP040.

Important truth:
- GP039 summarizes close staging only.
- GP039 does not close receipts.
- GP039 does not finalize receipts.
- GP039 does not claim official receipt status.
- GP039 does not claim owner review happened.
- GP039 does not claim Tower gates were acknowledged.
- GP039 does not claim blockers were acknowledged.
- GP039 does not claim no-execution was confirmed.
- GP039 is not a raw file storage provider.
- GP039 does not unlock direct upload.
- GP039 does not create external packet delivery.
- GP039 does not export raw or unredacted packet bodies.
- GP039 does not create public proof.
- GP039 does not open seller/broker/trustee/external portals.
- GP039 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.receipt_review_close_staging_service import get_receipt_review_close_staging_payload


PACK_ID = "VAULT_GP039"
PACK_NAME = "Receipt Close Summary"
SCHEMA_VERSION = "vault.receipt_close_summary.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

CONTROLLED_PACKET_PACKS = [
    {
        "pack_id": "VAULT_GP031",
        "name": "Controlled Packet Assembly Board",
        "layer": "packet_assembly_board",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP032",
        "name": "Packet Assembly Detail",
        "layer": "packet_assembly_detail",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP033",
        "name": "Packet Review Grouping",
        "layer": "packet_review_grouping",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP034",
        "name": "Packet Review Priority",
        "layer": "packet_review_priority",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP035",
        "name": "Packet Review Decision Prep",
        "layer": "packet_review_decision_prep",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP036",
        "name": "Owner Decision Review",
        "layer": "owner_decision_review",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP037",
        "name": "Reviewed Decision Receipt Staging",
        "layer": "reviewed_decision_receipt_staging",
        "ready": True,
        "safe_to_continue": True,
    },
    {
        "pack_id": "VAULT_GP038",
        "name": "Receipt Review Close Staging",
        "layer": "receipt_review_close_staging",
        "ready": True,
        "safe_to_continue": True,
    },
]

BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "PUBLIC_PACKET_PROOF_LOCKED": "Public packet proof remains locked.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "TOWER_STEP_UP_REQUIRED": "Tower step-up is required before sensitive action.",
    "OWNER_REVIEW_REQUIRED": "Owner review is required.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before closure.",
    "NO_AUTO_COMPLETION": "Automatic checklist completion is disabled.",
    "NO_AUTO_CONFIRMATION": "Automatic confirmation is disabled.",
    "NO_AUTO_ACTION_EXECUTION": "Automatic action execution is disabled.",
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault summarizes close review but does not execute actions.",
    "NO_EXTERNAL_PACKET_DELIVERY": "External packet delivery is disabled.",
    "NO_PACKET_EXPORT": "Packet export is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Controlled packet assembly is private only.",
    "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY": "Packet component detail is private only.",
    "PACKET_REVIEW_GROUPING_PRIVATE_ONLY": "Packet review grouping is private only.",
    "PACKET_REVIEW_PRIORITY_PRIVATE_ONLY": "Packet review priority is private only.",
    "PACKET_REVIEW_DECISION_PREP_PRIVATE_ONLY": "Packet review decision prep is private only.",
    "OWNER_DECISION_REVIEW_PRIVATE_ONLY": "Owner decision review is private only.",
    "REVIEWED_DECISION_RECEIPT_STAGING_PRIVATE_ONLY": "Reviewed decision receipt staging is private only.",
    "RECEIPT_DRAFT_NOT_FINALIZED": "Receipt draft is staged but not finalized.",
    "RECEIPT_REVIEW_CLOSE_STAGING_PRIVATE_ONLY": "Receipt review close staging is private only.",
    "RECEIPT_CLOSE_NOT_ALLOWED": "Receipt close is not allowed in this layer.",
    "RECEIPT_CLOSE_SUMMARY_PRIVATE_ONLY": "Receipt close summary is private only.",
    "RECEIPT_CLOSE_SUMMARY_NOT_SECTION_CHECKPOINT": "Receipt close summary is not the GP040 section checkpoint.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_receipt_close_summary_payload() -> Dict[str, Any]:
    gp038 = get_receipt_review_close_staging_payload()

    close_cards = gp038["close_cards"]

    summary_board = _build_summary_board(close_cards)
    unresolved_blockers = _build_unresolved_blockers(close_cards)
    not_final_warnings = _build_not_final_warnings(close_cards)
    tower_owner_readiness = _build_tower_owner_readiness(close_cards)
    no_execution_summary = _build_no_execution_summary(close_cards)
    controlled_rollup = _build_controlled_rollup(gp038)
    next_summary = _build_next_summary(
        summary_board,
        unresolved_blockers,
        not_final_warnings,
        tower_owner_readiness,
        no_execution_summary,
        controlled_rollup,
    )
    carry_forward = _build_carry_forward(summary_board, next_summary)

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
                "VAULT_GP029",
                "VAULT_GP030",
                "VAULT_GP031",
                "VAULT_GP032",
                "VAULT_GP033",
                "VAULT_GP034",
                "VAULT_GP035",
                "VAULT_GP036",
                "VAULT_GP037",
                "VAULT_GP038",
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "receipt_close_summary",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "summary_truth": {
            "receipt_close_summary_enabled": True,
            "summary_board_enabled": True,
            "unresolved_close_blockers_enabled": True,
            "receipt_not_final_warnings_enabled": True,
            "tower_owner_close_readiness_enabled": True,
            "no_execution_summary_proof_enabled": True,
            "controlled_packet_assembly_rollup_enabled": True,
            "metadata_only": True,
            "private_summary_only": True,
            "summary_means_not_checkpoint": True,
            "summary_means_not_closed": True,
            "receipt_close_enabled": False,
            "receipt_finalization_enabled": False,
            "finalized_receipt_count": 0,
            "closed_receipt_count": 0,
            "official_receipt_claimed_count": 0,
            "owner_review_claimed_count": 0,
            "tower_ack_claimed_count": 0,
            "blocker_ack_claimed_count": 0,
            "no_execution_confirmation_claimed_count": 0,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "external_packet_delivery_enabled": False,
            "external_access_enabled": False,
            "packet_export_enabled": False,
            "unredacted_export_enabled": False,
            "raw_export_enabled": False,
            "public_packet_proof_enabled": False,
            "public_proof_enabled": False,
            "portal_access_enabled": False,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
            "completed_count": 0,
            "auto_completion_enabled": False,
            "auto_confirmation_enabled": False,
            "approval_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "financing_decision_enabled": False,
            "legal_advice_enabled": False,
            "raw_document_verification_claimed": False,
            "auto_packet_approval_enabled": False,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp039",
            "safe_next_unlock": "GP040 should checkpoint GP031-GP039 section readiness without unlocking raw storage, external delivery, public proof, portals, export, finalization, close, approval, or execution.",
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
            "external_packet_delivery_allowed": False,
            "packet_export_allowed": False,
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "public_packet_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "summary_routes": {
            "room_title": "Vault Receipt Close Summary",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/receipt-close-summary",
            "json_route": "/vault/receipt-close-summary.json",
            "board_route": "/vault/receipt-close-summary-board.json",
            "unresolved_blockers_route": "/vault/receipt-close-unresolved-blockers.json",
            "not_final_warnings_route": "/vault/receipt-close-not-final-warnings.json",
            "tower_owner_readiness_route": "/vault/receipt-close-tower-owner-readiness.json",
            "no_execution_summary_proof_route": "/vault/receipt-close-no-execution-summary-proof.json",
            "controlled_rollup_route": "/vault/controlled-packet-assembly-rollup.json",
            "next_summary_route": "/vault/receipt-close-next-summary.json",
            "carry_forward_route": "/vault/receipt-close-carry-forward.json",
            "gp039_status_route": "/vault/gp039-status.json",
        },
        "summary_counts": {
            "summary_board_count": summary_board["summary_board_count"],
            "unresolved_blocker_count": unresolved_blockers["unresolved_blocker_count"],
            "active_block_code_count": unresolved_blockers["active_block_code_count"],
            "not_final_warning_count": not_final_warnings["not_final_warning_count"],
            "tower_owner_readiness_count": tower_owner_readiness["tower_owner_readiness_count"],
            "no_execution_summary_count": no_execution_summary["no_execution_summary_count"],
            "controlled_rollup_pack_count": controlled_rollup["controlled_rollup_pack_count"],
            "next_summary_count": next_summary["next_summary_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "closed_receipt_count": 0,
            "finalized_receipt_count": 0,
            "official_receipt_claimed_count": 0,
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
            "completed_count": 0,
            "metadata_only": True,
        },
        "summary_board": summary_board,
        "unresolved_blockers": unresolved_blockers,
        "not_final_warnings": not_final_warnings,
        "tower_owner_readiness": tower_owner_readiness,
        "no_execution_summary": no_execution_summary,
        "controlled_rollup": controlled_rollup,
        "next_summary": next_summary,
        "carry_forward": carry_forward,
        "gp038_connection": {
            "gp038_pack_id": gp038["pack"]["id"],
            "gp038_ready": gp038["gp038_status"]["ready"],
            "gp038_safe_to_continue": gp038["gp038_status"]["safe_to_continue_to_gp039"],
            "gp038_vault_done": gp038["gp038_status"]["vault_done"],
            "gp038_section": gp038["pack"]["section"],
            "gp038_close_card_count": gp038["close_summary"]["close_card_count"],
            "gp038_missing_ack_check_count": gp038["close_summary"]["missing_ack_check_count"],
            "gp038_draft_final_warning_count": gp038["close_summary"]["draft_final_warning_count"],
            "gp038_next_close_staging_count": gp038["close_summary"]["next_close_staging_count"],
        },
        "gp039_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp038_close_staging_connected": True,
            "receipt_close_summary_ready": True,
            "safe_to_continue_to_gp040": True,
            "vault_done": False,
            "metadata_only_summary": True,
            "private_summary_only": True,
            "summary_board_only": True,
            "receipt_close_disabled": True,
            "receipt_finalization_disabled": True,
            "official_receipt_claim_disabled": True,
            "owner_review_claim_disabled": True,
            "tower_ack_claim_disabled": True,
            "blocker_ack_claim_disabled": True,
            "no_execution_confirmation_claim_disabled": True,
            "section_checkpoint_not_yet_built": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
            "closed_receipt_count": 0,
            "finalized_receipt_count": 0,
            "completed_count": 0,
            "auto_completion_disabled": True,
            "auto_confirmation_disabled": True,
            "approval_disabled": True,
            "execution_engine_disabled": True,
            "auto_action_execution_disabled": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "external_delivery_still_locked": True,
            "external_access_still_locked": True,
            "packet_export_still_locked": True,
            "unredacted_export_still_locked": True,
            "raw_export_still_locked": True,
            "public_proof_still_locked": True,
            "public_packet_proof_disabled": True,
            "portal_access_still_locked": True,
            "financing_decision_not_claimed": True,
            "legal_advice_not_claimed": True,
            "raw_verification_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp039",
            "next_pack": "VAULT_GP040_CONTROLLED_PACKET_ASSEMBLY_READINESS_CHECKPOINT",
        },
    }

    return payload


def _build_summary_board(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []

    for card in close_cards:
        active_codes = sorted(set(card["blocked_codes"]) | {
            "RECEIPT_CLOSE_SUMMARY_PRIVATE_ONLY",
            "RECEIPT_CLOSE_SUMMARY_NOT_SECTION_CHECKPOINT",
        })

        items.append(
            {
                "summary_item_id": f"VRCSB-{card['priority_rank']:03d}",
                "close_card_id": card["close_card_id"],
                "close_stage_id": card["close_stage_id"],
                "receipt_draft_id": card["receipt_draft_id"],
                "review_card_id": card["review_card_id"],
                "decision_prep_id": card["decision_prep_id"],
                "priority_id": card["priority_id"],
                "review_group_id": card["review_group_id"],
                "packet_id": card["packet_id"],
                "assembly_id": card["assembly_id"],
                "lane": card["lane"],
                "packet_title": card["packet_title"],
                "priority_rank": card["priority_rank"],
                "priority_band": card["priority_band"],
                "readiness_label": card["readiness_label"],
                "close_readiness_label": card["close_readiness_label"],
                "summary_status": "SUMMARY_READY_NOT_CLOSED_NOT_FINAL",
                "metadata_only": True,
                "private_summary_only": True,
                "receipt_closed": False,
                "receipt_finalized": False,
                "official_receipt_claimed": False,
                "owner_review_claimed": False,
                "tower_ack_claimed": False,
                "blocker_ack_claimed": False,
                "no_execution_confirmation_claimed": False,
                "owner_review_required": True,
                "owner_reviewed": False,
                "owner_confirmation_required": True,
                "owner_confirmed": False,
                "decision_selected": False,
                "selected_decision_code": None,
                "completed": False,
                "auto_complete_allowed": False,
                "auto_confirm_allowed": False,
                "approval_allowed": False,
                "can_execute_from_vault": False,
                "execution_engine_enabled": False,
                "missing_ack_count": card["missing_ack_count"],
                "draft_final_warning_count": card["draft_final_warning_count"],
                "blocked_code_count": len(active_codes),
                "blocked_codes": active_codes,
                "blocked_labels": [BLOCK_CODES.get(code, code) for code in active_codes],
                "raw_body_available_count": 0,
                "raw_file_body_storage_enabled": False,
                "direct_upload_unlocked": False,
                "external_delivery_allowed": False,
                "external_access_allowed": False,
                "packet_export_allowed": False,
                "raw_export_allowed": False,
                "unredacted_export_allowed": False,
                "public_packet_proof_allowed": False,
                "portal_access_allowed": False,
                "tower_clearance_required": True,
                "tower_step_up_required": True,
                "vault_can_override_tower": False,
                "safe_to_close_receipt": False,
                "safe_to_finalize_receipt": False,
                "safe_to_deliver_externally": False,
                "safe_to_export": False,
                "safe_to_carry_to_gp040": True,
                "summary_note": f"Summary item for {card['packet_title']} remains not closed and not finalized.",
            }
        )

    return {
        "summary_board_items": items,
        "summary_board_count": len(items),
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_review_claimed_count": 0,
        "tower_ack_claimed_count": 0,
        "blocker_ack_claimed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
        "owner_review_required_count": len(items),
        "missing_ack_total": sum(item["missing_ack_count"] for item in items),
        "draft_final_warning_total": sum(item["draft_final_warning_count"] for item in items),
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_summary_board": True,
    }


def _build_unresolved_blockers(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []

    gp039_summary_block_codes = {
        "RECEIPT_CLOSE_SUMMARY_PRIVATE_ONLY",
        "RECEIPT_CLOSE_SUMMARY_NOT_SECTION_CHECKPOINT",
    }

    for card in close_cards:
        blocked_codes = sorted(set(card["blocked_codes"]) | gp039_summary_block_codes)

        items.append(
            {
                "unresolved_blocker_id": f"VRCUB-{card['priority_rank']:03d}",
                "close_card_id": card["close_card_id"],
                "receipt_draft_id": card["receipt_draft_id"],
                "packet_id": card["packet_id"],
                "packet_title": card["packet_title"],
                "priority_rank": card["priority_rank"],
                "blocker_status": "UNRESOLVED_CLOSE_BLOCKERS_ACTIVE",
                "blocked_code_count": len(blocked_codes),
                "blocked_codes": blocked_codes,
                "metadata_only": True,
                "all_restricted_paths_locked": True,
                "safe_to_override_inside_vault": False,
                "raw_storage_allowed": False,
                "direct_upload_allowed": False,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "public_packet_proof_allowed": False,
                "portal_access_allowed": False,
                "execution_allowed": False,
                "receipt_closed": False,
                "receipt_finalized": False,
                "official_receipt_claimed": False,
                "safe_to_carry_to_gp040": True,
            }
        )

    active_codes = sorted({code for item in items for code in item["blocked_codes"]})

    return {
        "unresolved_blocker_items": items,
        "active_block_codes": active_codes,
        "unresolved_blocker_count": len(items),
        "active_block_code_count": len(active_codes),
        "all_restricted_paths_locked": True,
        "safe_to_override_inside_vault_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_unresolved_blockers": True,
    }


def _build_not_final_warnings(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []

    for card in close_cards:
        for warning_type in card["draft_final_warning_types"]:
            items.append(
                {
                    "not_final_warning_id": f"VRCNFW-{card['priority_rank']:03d}-{warning_type}",
                    "close_card_id": card["close_card_id"],
                    "receipt_draft_id": card["receipt_draft_id"],
                    "packet_id": card["packet_id"],
                    "packet_title": card["packet_title"],
                    "priority_rank": card["priority_rank"],
                    "warning_type": warning_type,
                    "warning_status": "RECEIPT_NOT_FINAL_WARNING_ACTIVE",
                    "metadata_only": True,
                    "receipt_draft_only": True,
                    "receipt_closed": False,
                    "receipt_finalized": False,
                    "official_receipt_claimed": False,
                    "owner_review_claimed": False,
                    "no_execution_confirmation_claimed": False,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_carry_to_gp040": True,
                }
            )

    return {
        "not_final_warning_items": items,
        "not_final_warning_count": len(items),
        "warning_type_count": len({item["warning_type"] for item in items}),
        "receipt_draft_only_count": len(items),
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_review_claimed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "executes_action_count": 0,
        "safe_to_continue_not_final_warnings": True,
    }


def _build_tower_owner_readiness(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_owner_readiness_id": f"VRCTOR-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "readiness_status": "OWNER_AND_TOWER_NOT_READY_TO_CLOSE",
            "owner_review_required": True,
            "owner_reviewed": False,
            "owner_confirmation_required": True,
            "owner_confirmed": False,
            "tower_ack_required": True,
            "tower_acknowledged": False,
            "tower_ack_claimed": False,
            "tower_clearance_required": True,
            "tower_step_up_required": True,
            "tower_export_lock_required": True,
            "tower_external_access_required": True,
            "tower_portal_unlock_required": True,
            "tower_sensitive_visibility_required": True,
            "vault_can_override_tower": False,
            "metadata_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "portal_access_allowed": False,
            "safe_to_carry_to_gp040": True,
        }
        for card in close_cards
    ]

    return {
        "tower_owner_readiness_items": items,
        "tower_owner_readiness_count": len(items),
        "owner_review_required_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "tower_ack_required_count": len(items),
        "tower_acknowledged_count": 0,
        "tower_ack_claimed_count": 0,
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "vault_override_allowed_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_owner_readiness_preserved": True,
    }


def _build_no_execution_summary(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "no_execution_summary_id": f"VRCNES-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "no_execution_summary_status": "NO_EXECUTION_SUMMARY_PROOF_VISIBLE_NOT_CONFIRMED",
            "no_execution_confirmation_required": True,
            "no_execution_confirmed": False,
            "no_execution_confirmation_claimed": False,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "auto_action_execution_enabled": False,
            "execution_engine_enabled": False,
            "approval_allowed": False,
            "financing_decision_enabled": False,
            "legal_advice_enabled": False,
            "raw_document_verification_claimed": False,
            "auto_packet_approval_enabled": False,
            "metadata_only": True,
            "private_summary_only": True,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp040": True,
        }
        for card in close_cards
    ]

    return {
        "no_execution_summary_items": items,
        "no_execution_summary_count": len(items),
        "no_execution_confirmation_required_count": len(items),
        "no_execution_confirmed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "auto_action_execution_enabled_count": 0,
        "execution_engine_enabled_count": 0,
        "approval_allowed_count": 0,
        "financing_decision_enabled_count": 0,
        "legal_advice_enabled_count": 0,
        "raw_document_verification_claimed_count": 0,
        "auto_packet_approval_enabled_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_no_execution_summary": True,
    }


def _build_controlled_rollup(gp038: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for index, pack in enumerate(CONTROLLED_PACKET_PACKS, start=31):
        items.append(
            {
                "rollup_id": f"VCPR-{index:03d}",
                "pack_id": pack["pack_id"],
                "pack_name": pack["name"],
                "product_depth_layer": pack["layer"],
                "section": SECTION_ID,
                "section_range": SECTION_RANGE,
                "present": True,
                "ready": pack["ready"],
                "safe_to_continue": pack["safe_to_continue"],
                "foundation_status": "safe_to_continue_not_done",
                "vault_done": False,
                "metadata_only_private_layer": True,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "public_packet_proof_allowed": False,
                "execution_allowed": False,
            }
        )

    return {
        "controlled_rollup_items": items,
        "controlled_rollup_pack_count": len(items),
        "expected_pack_count": 8,
        "present_pack_count": len(items),
        "ready_pack_count": sum(1 for item in items if item["ready"]),
        "safe_to_continue_pack_count": sum(1 for item in items if item["safe_to_continue"]),
        "all_expected_packs_present": True,
        "all_expected_packs_ready": True,
        "all_expected_packs_safe_to_continue": True,
        "vault_done": False,
        "gp038_connection_ready": gp038["gp038_status"]["ready"] is True,
        "gp038_connection_safe_to_continue": gp038["gp038_status"]["safe_to_continue_to_gp039"] is True,
        "ready_for_gp040_section_checkpoint": True,
        "clouds_should_continue": False,
    }


def _build_next_summary(
    summary_board: Dict[str, Any],
    unresolved_blockers: Dict[str, Any],
    not_final_warnings: Dict[str, Any],
    tower_owner_readiness: Dict[str, Any],
    no_execution_summary: Dict[str, Any],
    controlled_rollup: Dict[str, Any],
) -> Dict[str, Any]:
    items = []

    for item in summary_board["summary_board_items"]:
        items.append(
            {
                "next_summary_id": f"VRCSNX-{item['priority_rank']:03d}",
                "summary_item_id": item["summary_item_id"],
                "close_card_id": item["close_card_id"],
                "receipt_draft_id": item["receipt_draft_id"],
                "packet_id": item["packet_id"],
                "packet_title": item["packet_title"],
                "priority_rank": item["priority_rank"],
                "summary_status": "READY_FOR_GP040_SECTION_CHECKPOINT_NOT_CLOSED",
                "metadata_only": True,
                "private_summary_only": True,
                "receipt_closed": False,
                "receipt_finalized": False,
                "official_receipt_claimed": False,
                "owner_review_claimed": False,
                "tower_ack_claimed": False,
                "blocker_ack_claimed": False,
                "no_execution_confirmation_claimed": False,
                "owner_review_required": True,
                "owner_reviewed": False,
                "decision_selected": False,
                "owner_confirmed": False,
                "completed": False,
                "auto_complete_allowed": False,
                "auto_confirm_allowed": False,
                "approval_allowed": False,
                "can_execute_from_vault": False,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "public_packet_proof_allowed": False,
                "safe_to_carry_to_gp040": True,
            }
        )

    items.append(
        {
            "next_summary_id": "VRCSNX-998",
            "summary_item_id": "BOUNDARY-LOCKS",
            "close_card_id": "BOUNDARY-LOCKS",
            "receipt_draft_id": "BOUNDARY-LOCKS",
            "packet_id": "ALL_PACKETS",
            "packet_title": "All Receipt Close Summary Boundaries",
            "priority_rank": 998,
            "summary_status": "BOUNDARY_LOCKED_NO_CLOSE_NO_FINALIZATION",
            "metadata_only": True,
            "private_summary_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_claimed": False,
            "tower_ack_claimed": False,
            "blocker_ack_claimed": False,
            "no_execution_confirmation_claimed": False,
            "owner_review_required": True,
            "owner_reviewed": False,
            "decision_selected": False,
            "owner_confirmed": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "approval_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp040": True,
        }
    )

    items.append(
        {
            "next_summary_id": "VRCSNX-999",
            "summary_item_id": "NEXT-GP040",
            "close_card_id": "NEXT-GP040",
            "receipt_draft_id": "NEXT-GP040",
            "packet_id": "NEXT_VAULT_PACK",
            "packet_title": "GP040 Controlled Packet Assembly Readiness Checkpoint",
            "priority_rank": 999,
            "summary_status": "NEXT_BUILD_READY",
            "metadata_only": True,
            "private_summary_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_claimed": False,
            "tower_ack_claimed": False,
            "blocker_ack_claimed": False,
            "no_execution_confirmation_claimed": False,
            "owner_review_required": True,
            "owner_reviewed": False,
            "decision_selected": False,
            "owner_confirmed": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "approval_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp040": True,
        }
    )

    sorted_items = sorted(items, key=lambda item: (item["priority_rank"], item["next_summary_id"]))

    return {
        "next_summary_items": sorted_items,
        "next_summary_count": len(sorted_items),
        "packet_summary_count": summary_board["summary_board_count"],
        "boundary_summary_count": 1,
        "next_build_summary_count": 1,
        "unresolved_blocker_count": unresolved_blockers["unresolved_blocker_count"],
        "not_final_warning_count": not_final_warnings["not_final_warning_count"],
        "tower_owner_readiness_count": tower_owner_readiness["tower_owner_readiness_count"],
        "no_execution_summary_count": no_execution_summary["no_execution_summary_count"],
        "controlled_rollup_pack_count": controlled_rollup["controlled_rollup_pack_count"],
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_review_claimed_count": 0,
        "tower_ack_claimed_count": 0,
        "blocker_ack_claimed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
        "owner_review_required_count": len(sorted_items),
        "decision_selected_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_continue_next_summary": True,
        "next_owner_actions": [
            "Review the receipt close summary board.",
            "Keep unresolved close blockers visible.",
            "Keep receipt-not-final warnings visible.",
            "Keep Tower and owner close readiness unresolved until future gates exist.",
            "Keep no-execution summary proof visible without claiming confirmation.",
            "Use GP040 as the controlled packet assembly readiness checkpoint.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP040.",
        ],
    }


def _build_carry_forward(summary_board: Dict[str, Any], next_summary: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VRCS-CF-{item['priority_rank']:03d}",
            "summary_item_id": item["summary_item_id"],
            "close_card_id": item["close_card_id"],
            "receipt_draft_id": item["receipt_draft_id"],
            "review_card_id": item["review_card_id"],
            "decision_prep_id": item["decision_prep_id"],
            "priority_id": item["priority_id"],
            "review_group_id": item["review_group_id"],
            "packet_id": item["packet_id"],
            "packet_title": item["packet_title"],
            "priority_rank": item["priority_rank"],
            "carry_forward_status": "READY_FOR_GP040_CONTROLLED_PACKET_ASSEMBLY_READINESS_CHECKPOINT",
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_claimed": False,
            "tower_ack_claimed": False,
            "blocker_ack_claimed": False,
            "no_execution_confirmation_claimed": False,
            "owner_reviewed": False,
            "tower_acknowledged": False,
            "blocker_acknowledged": False,
            "no_execution_confirmed": False,
            "owner_confirmed": False,
            "decision_selected": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp040": True,
        }
        for item in summary_board["summary_board_items"]
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp040_count": len(items),
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_review_claimed_count": 0,
        "tower_ack_claimed_count": 0,
        "blocker_ack_claimed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
        "owner_reviewed_count": 0,
        "tower_acknowledged_count": 0,
        "blocker_acknowledged_count": 0,
        "no_execution_confirmed_count": 0,
        "owner_confirmed_count": 0,
        "decision_selected_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_carry_to_gp040": True,
        "next_summary_count": next_summary["next_summary_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_receipt_close_summary_payload())


def get_receipt_close_summary_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "summary_truth": payload["summary_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "summary_routes": payload["summary_routes"],
        "summary_counts": payload["summary_counts"],
        "gp038_connection": payload["gp038_connection"],
    }


def get_receipt_close_summary_board() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "summary_board": payload["summary_board"],
    }


def get_receipt_close_unresolved_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "unresolved_blockers": payload["unresolved_blockers"],
    }


def get_receipt_close_not_final_warnings() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "not_final_warnings": payload["not_final_warnings"],
    }


def get_receipt_close_tower_owner_readiness() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_owner_readiness": payload["tower_owner_readiness"],
    }


def get_receipt_close_no_execution_summary_proof() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_execution_summary": payload["no_execution_summary"],
    }


def get_controlled_packet_assembly_rollup() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "controlled_rollup": payload["controlled_rollup"],
    }


def get_receipt_close_next_summary() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_summary": payload["next_summary"],
    }


def get_receipt_close_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp039_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp039_status": payload["gp039_status"],
        "summary_truth": payload["summary_truth"],
        "summary_routes": payload["summary_routes"],
        "summary_counts": payload["summary_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp038_connection": payload["gp038_connection"],
    }


def render_receipt_close_summary_page() -> str:
    payload = clone_payload()
    routes = payload["summary_routes"]
    counts = payload["summary_counts"]
    truth = payload["summary_truth"]
    board = payload["summary_board"]
    next_summary = payload["next_summary"]

    card_html = "\n".join(_render_summary_card(item) for item in board["summary_board_items"])
    next_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['packet_title'])}</strong>
            <span>{escape(item['summary_status'])} · closed: {str(item['receipt_closed']).lower()}</span>
          </div>
          <div class="pill {'danger' if item['priority_rank'] <= 3 or item['priority_rank'] == 998 else 'warn'}">Rank {item['priority_rank']}</div>
        </div>
        """
        for item in next_summary["next_summary_items"][:10]
    )

    owner_actions = "\n".join(f"<li>{escape(action)}</li>" for action in next_summary["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Receipt Close Summary · GP039</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 039</div>
        <h1>Receipt Close Summary</h1>
        <p class="hero-copy">
          GP039 summarizes the controlled packet assembly close-staging layer before GP040.
          It creates a summary board, unresolved close blockers, receipt-not-final warnings,
          Tower/owner readiness, no-execution summary proof, GP031–GP038 rollup, and carry-forward into GP040.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['summary_board_count']}</strong>
            <span>summary board items</span>
          </div>
          <div class="metric">
            <strong>{counts['unresolved_blocker_count']}</strong>
            <span>unresolved blockers</span>
          </div>
          <div class="metric">
            <strong>{counts['not_final_warning_count']}</strong>
            <span>not-final warnings</span>
          </div>
          <div class="metric">
            <strong>{counts['closed_receipt_count']}</strong>
            <span>closed receipts</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Close summary ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">GP040 next</span>
          <span class="pill danger">No close claim</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Receipt Close Summary Board</h2>
      <p>
        Each close-staging card is summarized. Nothing is closed, finalized, exported, delivered, approved, or executed.
      </p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Sorted Next Summary</h2>
        <p>Summary items stay in priority order while the GP040 checkpoint stays visible.</p>
        <div>
          {next_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP039 prepares GP040 controlled packet assembly readiness checkpoint.</p>
        <ul>
          {owner_actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP039 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['board_route'])}</code>
        <code>{escape(routes['unresolved_blockers_route'])}</code>
        <code>{escape(routes['not_final_warnings_route'])}</code>
        <code>{escape(routes['tower_owner_readiness_route'])}</code>
        <code>{escape(routes['no_execution_summary_proof_route'])}</code>
        <code>{escape(routes['controlled_rollup_route'])}</code>
        <code>{escape(routes['next_summary_route'])}</code>
        <code>{escape(routes['carry_forward_route'])}</code>
        <code>{escape(routes['gp039_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Summary Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Receipt close enabled:
        <code>{str(truth['receipt_close_enabled']).lower()}</code>.
        Finalization enabled:
        <code>{str(truth['receipt_finalization_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_summary_card(item: Dict[str, Any]) -> str:
    chip_class = "danger" if item["priority_rank"] <= 3 else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['packet_title'])}</div>
            <div class="meta">
              Summary: <code>{escape(item['summary_item_id'])}</code><br>
              Rank: <code>{item['priority_rank']}</code><br>
              Status: <code>{escape(item['summary_status'])}</code><br>
              Closed: <code>{str(item['receipt_closed']).lower()}</code><br>
              Finalized: <code>{str(item['receipt_finalized']).lower()}</code>
            </div>
          </div>
          <span class="pill {chip_class}">Summary</span>
        </div>
      </article>
    """
