"""
VAULT GIANT PACK 038 — Receipt Review Close Staging

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP037 reviewed decision receipt staging by creating private
receipt close staging surfaces.

Purpose:
- Build receipt review close cards from receipt drafts.
- Build close readiness labels.
- Build missing acknowledgment checks.
- Build draft-vs-final warnings.
- Build Tower close gates.
- Build blocker close gates.
- Build no-execution close proof.
- Sort next close staging.
- Carry close staging forward to GP039.

Important truth:
- GP038 stages close review only.
- GP038 does not close receipts.
- GP038 does not finalize receipts.
- GP038 does not claim official receipt status.
- GP038 does not claim owner review happened.
- GP038 does not claim Tower gates were acknowledged.
- GP038 does not claim blockers were acknowledged.
- GP038 does not claim no-execution was confirmed.
- GP038 is not a raw file storage provider.
- GP038 does not unlock direct upload.
- GP038 does not create external packet delivery.
- GP038 does not export raw or unredacted packet bodies.
- GP038 does not create public proof.
- GP038 does not open seller/broker/trustee/external portals.
- GP038 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.reviewed_decision_receipt_staging_service import get_reviewed_decision_receipt_staging_payload


PACK_ID = "VAULT_GP038"
PACK_NAME = "Receipt Review Close Staging"
SCHEMA_VERSION = "vault.receipt_review_close_staging.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

MISSING_ACK_TYPES = [
    "owner_review",
    "tower_gate_ack",
    "blocker_ack",
    "no_execution_confirmation",
]

DRAFT_FINAL_WARNING_TYPES = [
    "receipt_draft_not_finalized",
    "official_receipt_not_claimed",
    "owner_review_not_claimed",
    "no_execution_not_confirmed",
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault stages receipt close review but does not execute actions.",
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
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_receipt_review_close_staging_payload() -> Dict[str, Any]:
    gp037 = get_reviewed_decision_receipt_staging_payload()

    receipt_drafts = gp037["receipt_drafts"]

    close_cards = [
        _build_close_card(draft)
        for draft in receipt_drafts
    ]

    close_readiness = _build_close_readiness(close_cards)
    missing_ack_checks = _build_missing_ack_checks(close_cards)
    draft_final_warnings = _build_draft_final_warnings(close_cards)
    tower_close_gates = _build_tower_close_gates(close_cards)
    blocker_close_gates = _build_blocker_close_gates(close_cards)
    no_execution_close_proof = _build_no_execution_close_proof(close_cards)
    next_close_staging = _build_next_close_staging(
        close_cards,
        missing_ack_checks,
        draft_final_warnings,
        no_execution_close_proof,
    )
    carry_forward = _build_carry_forward(close_cards, next_close_staging)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "receipt_review_close_staging",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "close_truth": {
            "receipt_review_close_staging_enabled": True,
            "close_cards_enabled": True,
            "close_readiness_labels_enabled": True,
            "missing_ack_checks_enabled": True,
            "draft_vs_final_warnings_enabled": True,
            "tower_close_gates_enabled": True,
            "blocker_close_gates_enabled": True,
            "no_execution_close_proof_enabled": True,
            "metadata_only": True,
            "private_close_staging_only": True,
            "close_staging_means_not_closed": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp038",
            "safe_next_unlock": "GP039 can deepen receipt close review summary without unlocking raw storage, external delivery, public proof, portals, export, finalization, close, approval, or execution.",
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
        "close_summary": {
            "room_title": "Vault Receipt Review Close Staging",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/receipt-review-close-staging",
            "json_route": "/vault/receipt-review-close-staging.json",
            "cards_route": "/vault/receipt-review-close-cards.json",
            "readiness_route": "/vault/receipt-review-close-readiness.json",
            "missing_ack_checks_route": "/vault/receipt-review-missing-ack-checks.json",
            "draft_final_warnings_route": "/vault/receipt-review-draft-final-warnings.json",
            "tower_close_gates_route": "/vault/receipt-review-tower-close-gates.json",
            "blocker_close_gates_route": "/vault/receipt-review-blocker-close-gates.json",
            "no_execution_close_proof_route": "/vault/receipt-review-no-execution-close-proof.json",
            "next_close_staging_route": "/vault/receipt-review-next-close-staging.json",
            "carry_forward_route": "/vault/receipt-review-close-carry-forward.json",
            "gp038_status_route": "/vault/gp038-status.json",
            "close_card_count": len(close_cards),
            "close_readiness_count": close_readiness["close_readiness_count"],
            "missing_ack_check_count": missing_ack_checks["missing_ack_check_count"],
            "draft_final_warning_count": draft_final_warnings["draft_final_warning_count"],
            "tower_close_gate_count": tower_close_gates["tower_close_gate_count"],
            "blocker_close_gate_count": blocker_close_gates["blocker_close_gate_count"],
            "no_execution_close_proof_count": no_execution_close_proof["no_execution_close_proof_count"],
            "next_close_staging_count": next_close_staging["next_close_staging_count"],
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
        "close_cards": close_cards,
        "close_readiness": close_readiness,
        "missing_ack_checks": missing_ack_checks,
        "draft_final_warnings": draft_final_warnings,
        "tower_close_gates": tower_close_gates,
        "blocker_close_gates": blocker_close_gates,
        "no_execution_close_proof": no_execution_close_proof,
        "next_close_staging": next_close_staging,
        "carry_forward": carry_forward,
        "gp037_connection": {
            "gp037_pack_id": gp037["pack"]["id"],
            "gp037_ready": gp037["gp037_status"]["ready"],
            "gp037_safe_to_continue": gp037["gp037_status"]["safe_to_continue_to_gp038"],
            "gp037_vault_done": gp037["gp037_status"]["vault_done"],
            "gp037_section": gp037["pack"]["section"],
            "gp037_receipt_draft_count": gp037["receipt_summary"]["receipt_draft_count"],
            "gp037_ack_receipt_preview_count": gp037["receipt_summary"]["ack_receipt_preview_count"],
            "gp037_no_execution_receipt_count": gp037["receipt_summary"]["no_execution_receipt_count"],
            "gp037_next_receipt_count": gp037["receipt_summary"]["next_receipt_count"],
        },
        "gp038_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp037_receipt_staging_connected": True,
            "receipt_review_close_staging_ready": True,
            "safe_to_continue_to_gp039": True,
            "vault_done": False,
            "metadata_only_close_staging": True,
            "private_close_staging_only": True,
            "close_cards_only": True,
            "receipt_close_disabled": True,
            "receipt_finalization_disabled": True,
            "official_receipt_claim_disabled": True,
            "owner_review_claim_disabled": True,
            "tower_ack_claim_disabled": True,
            "blocker_ack_claim_disabled": True,
            "no_execution_confirmation_claim_disabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp038",
            "next_pack": "VAULT_GP039_RECEIPT_CLOSE_SUMMARY_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_close_card(draft: Dict[str, Any]) -> Dict[str, Any]:
    active_codes = sorted(set(draft["blocked_codes"]) | {
        "RECEIPT_REVIEW_CLOSE_STAGING_PRIVATE_ONLY",
        "RECEIPT_CLOSE_NOT_ALLOWED",
    })

    missing_ack_types = list(MISSING_ACK_TYPES)
    warning_types = list(DRAFT_FINAL_WARNING_TYPES)

    return {
        "close_card_id": f"VRCC-{draft['priority_rank']:03d}",
        "close_stage_id": f"VRCS-{draft['priority_rank']:03d}",
        "receipt_draft_id": draft["receipt_draft_id"],
        "receipt_stage_id": draft["receipt_stage_id"],
        "review_card_id": draft["review_card_id"],
        "decision_prep_id": draft["decision_prep_id"],
        "priority_id": draft["priority_id"],
        "review_group_id": draft["review_group_id"],
        "packet_id": draft["packet_id"],
        "assembly_id": draft["assembly_id"],
        "lane": draft["lane"],
        "packet_title": draft["packet_title"],
        "priority_rank": draft["priority_rank"],
        "priority_band": draft["priority_band"],
        "readiness_label": draft["readiness_label"],
        "recommended_safe_option": draft["recommended_safe_option"],
        "close_readiness_label": "NOT_READY_TO_CLOSE_MISSING_ACKS_DRAFT_ONLY",
        "close_stage_status": "CLOSE_STAGING_READY_DRAFT_NOT_FINAL",
        "metadata_only": True,
        "private_close_staging_only": True,
        "receipt_type": "reviewed_decision_receipt_close_staging",
        "receipt_finalized": False,
        "receipt_closed": False,
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
        "tower_ack_required": True,
        "tower_acknowledged": False,
        "blocker_ack_required": True,
        "blocker_acknowledged": False,
        "no_execution_confirmation_required": True,
        "no_execution_confirmed": False,
        "missing_ack_count": len(missing_ack_types),
        "missing_ack_types": missing_ack_types,
        "draft_final_warning_count": len(warning_types),
        "draft_final_warning_types": warning_types,
        "detail_count": draft["detail_count"],
        "review_lane_count": draft["review_lane_count"],
        "redacted_preview_slot_count": draft["redacted_preview_slot_count"],
        "tower_gate_count": draft["tower_gate_count"],
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
        "safe_to_review_close_privately": True,
        "safe_to_close_receipt": False,
        "safe_to_finalize_receipt": False,
        "safe_to_deliver_externally": False,
        "safe_to_export": False,
        "safe_to_carry_to_gp039": True,
        "close_note": f"Close staging created for {draft['packet_title']}. This is not a closed or finalized receipt and does not claim review, acknowledgment, confirmation, approval, delivery, export, or execution.",
    }


def _build_close_readiness(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "close_readiness_id": f"VRCR-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "close_readiness_label": card["close_readiness_label"],
            "close_stage_status": card["close_stage_status"],
            "missing_ack_count": card["missing_ack_count"],
            "draft_final_warning_count": card["draft_final_warning_count"],
            "metadata_only": True,
            "safe_to_close_receipt": False,
            "safe_to_finalize_receipt": False,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_required": True,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp039": True,
        }
        for card in close_cards
    ]

    return {
        "close_readiness_items": items,
        "close_readiness_count": len(items),
        "not_ready_to_close_count": len(items),
        "ready_to_close_count": 0,
        "safe_to_close_receipt_count": 0,
        "safe_to_finalize_receipt_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_close_readiness": True,
    }


def _build_missing_ack_checks(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []

    for card in close_cards:
        for ack_type in card["missing_ack_types"]:
            items.append(
                {
                    "missing_ack_check_id": f"VRMA-{card['priority_rank']:03d}-{ack_type}",
                    "close_card_id": card["close_card_id"],
                    "receipt_draft_id": card["receipt_draft_id"],
                    "packet_id": card["packet_id"],
                    "packet_title": card["packet_title"],
                    "priority_rank": card["priority_rank"],
                    "ack_type": ack_type,
                    "ack_required": True,
                    "ack_present": False,
                    "ack_claimed": False,
                    "acknowledged": False,
                    "check_status": "MISSING_ACK_REQUIRED_FOR_FUTURE_CLOSE",
                    "metadata_only": True,
                    "receipt_closed": False,
                    "receipt_finalized": False,
                    "official_receipt_claimed": False,
                    "owner_review_required": True,
                    "owner_confirmed": False,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_carry_to_gp039": True,
                }
            )

    return {
        "missing_ack_check_items": items,
        "missing_ack_check_count": len(items),
        "missing_ack_type_count": len(MISSING_ACK_TYPES),
        "close_card_count": len(close_cards),
        "ack_present_count": 0,
        "ack_claimed_count": 0,
        "acknowledged_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "executes_action_count": 0,
        "safe_to_continue_missing_ack_checks": True,
    }


def _build_draft_final_warnings(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []

    for card in close_cards:
        for warning_type in card["draft_final_warning_types"]:
            items.append(
                {
                    "draft_final_warning_id": f"VRDFW-{card['priority_rank']:03d}-{warning_type}",
                    "close_card_id": card["close_card_id"],
                    "receipt_draft_id": card["receipt_draft_id"],
                    "packet_id": card["packet_id"],
                    "packet_title": card["packet_title"],
                    "priority_rank": card["priority_rank"],
                    "warning_type": warning_type,
                    "warning_status": "DRAFT_NOT_FINAL_WARNING_ACTIVE",
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
                    "safe_to_carry_to_gp039": True,
                }
            )

    return {
        "draft_final_warning_items": items,
        "draft_final_warning_count": len(items),
        "warning_type_count": len(DRAFT_FINAL_WARNING_TYPES),
        "close_card_count": len(close_cards),
        "receipt_draft_only_count": len(items),
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_review_claimed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "executes_action_count": 0,
        "safe_to_continue_draft_final_warnings": True,
    }


def _build_tower_close_gates(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_close_gate_id": f"VRTCG-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "tower_close_gate_status": "TOWER_CLOSE_GATES_REQUIRED_NOT_ACKNOWLEDGED",
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
            "safe_to_carry_to_gp039": True,
        }
        for card in close_cards
    ]

    return {
        "tower_close_gate_items": items,
        "tower_close_gate_count": len(items),
        "tower_ack_required_count": len(items),
        "tower_acknowledged_count": 0,
        "tower_ack_claimed_count": 0,
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "tower_export_lock_required_count": len(items),
        "vault_override_allowed_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_close_gates_preserve_authority": True,
    }


def _build_blocker_close_gates(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "blocker_close_gate_id": f"VRBCG-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "blocker_close_gate_status": "BLOCKER_CLOSE_GATES_ACTIVE_NOT_ACKNOWLEDGED",
            "blocker_ack_required": True,
            "blocker_acknowledged": False,
            "blocker_ack_claimed": False,
            "blocked_code_count": card["blocked_code_count"],
            "blocked_codes": card["blocked_codes"],
            "all_restricted_paths_locked": True,
            "safe_to_override_inside_vault": False,
            "raw_storage_allowed": False,
            "direct_upload_allowed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "portal_access_allowed": False,
            "execution_allowed": False,
            "metadata_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "safe_to_carry_to_gp039": True,
        }
        for card in close_cards
    ]

    active_codes = sorted({code for item in items for code in item["blocked_codes"]})

    return {
        "blocker_close_gate_items": items,
        "active_block_codes": active_codes,
        "blocker_close_gate_count": len(items),
        "active_block_code_count": len(active_codes),
        "blocker_ack_required_count": len(items),
        "blocker_acknowledged_count": 0,
        "blocker_ack_claimed_count": 0,
        "all_restricted_paths_locked": True,
        "safe_to_override_inside_vault_count": 0,
        "receipt_closed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_blocker_close_gates": True,
    }


def _build_no_execution_close_proof(close_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "no_execution_close_proof_id": f"VRNEC-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "no_execution_close_status": "NO_EXECUTION_CLOSE_PROOF_STAGED_NOT_CONFIRMED",
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
            "private_close_staging_only": True,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp039": True,
        }
        for card in close_cards
    ]

    return {
        "no_execution_close_proof_items": items,
        "no_execution_close_proof_count": len(items),
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
        "safe_to_continue_no_execution_close_proof": True,
    }


def _build_next_close_staging(
    close_cards: List[Dict[str, Any]],
    missing_ack_checks: Dict[str, Any],
    draft_final_warnings: Dict[str, Any],
    no_execution_close_proof: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_close_staging_id": f"VRCNX-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "readiness_label": card["readiness_label"],
            "close_readiness_label": card["close_readiness_label"],
            "next_close_status": "READY_FOR_GP039_CLOSE_SUMMARY_NOT_CLOSED",
            "metadata_only": True,
            "private_close_staging_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_claimed": False,
            "tower_ack_claimed": False,
            "blocker_ack_claimed": False,
            "no_execution_confirmation_claimed": False,
            "owner_review_required": True,
            "owner_reviewed": False,
            "tower_ack_required": True,
            "tower_acknowledged": False,
            "blocker_ack_required": True,
            "blocker_acknowledged": False,
            "no_execution_confirmation_required": True,
            "no_execution_confirmed": False,
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
            "safe_to_carry_to_gp039": True,
        }
        for card in close_cards
    ]

    items.append(
        {
            "next_close_staging_id": "VRCNX-998",
            "close_card_id": "BOUNDARY-LOCKS",
            "receipt_draft_id": "BOUNDARY-LOCKS",
            "packet_id": "ALL_PACKETS",
            "packet_title": "All Receipt Review Close Boundaries",
            "priority_rank": 998,
            "readiness_label": "CLOSE_BOUNDARIES_LOCKED",
            "close_readiness_label": "NOT_READY_TO_CLOSE_BOUNDARIES_LOCKED",
            "next_close_status": "BOUNDARY_LOCKED_NO_CLOSE_NO_FINALIZATION",
            "metadata_only": True,
            "private_close_staging_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_claimed": False,
            "tower_ack_claimed": False,
            "blocker_ack_claimed": False,
            "no_execution_confirmation_claimed": False,
            "owner_review_required": True,
            "owner_reviewed": False,
            "tower_ack_required": True,
            "tower_acknowledged": False,
            "blocker_ack_required": True,
            "blocker_acknowledged": False,
            "no_execution_confirmation_required": True,
            "no_execution_confirmed": False,
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
            "safe_to_carry_to_gp039": True,
        }
    )

    items.append(
        {
            "next_close_staging_id": "VRCNX-999",
            "close_card_id": "NEXT-GP039",
            "receipt_draft_id": "NEXT-GP039",
            "packet_id": "NEXT_VAULT_PACK",
            "packet_title": "GP039 Receipt Close Summary",
            "priority_rank": 999,
            "readiness_label": "READY_FOR_GP039",
            "close_readiness_label": "READY_FOR_NEXT_BUILD_NOT_CLOSED",
            "next_close_status": "NEXT_BUILD_READY",
            "metadata_only": True,
            "private_close_staging_only": True,
            "receipt_closed": False,
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "owner_review_claimed": False,
            "tower_ack_claimed": False,
            "blocker_ack_claimed": False,
            "no_execution_confirmation_claimed": False,
            "owner_review_required": True,
            "owner_reviewed": False,
            "tower_ack_required": True,
            "tower_acknowledged": False,
            "blocker_ack_required": True,
            "blocker_acknowledged": False,
            "no_execution_confirmation_required": True,
            "no_execution_confirmed": False,
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
            "safe_to_carry_to_gp039": True,
        }
    )

    sorted_items = sorted(items, key=lambda item: (item["priority_rank"], item["next_close_staging_id"]))

    return {
        "next_close_staging_items": sorted_items,
        "next_close_staging_count": len(sorted_items),
        "packet_close_count": len(close_cards),
        "boundary_close_count": 1,
        "next_build_close_count": 1,
        "missing_ack_check_count": missing_ack_checks["missing_ack_check_count"],
        "draft_final_warning_count": draft_final_warnings["draft_final_warning_count"],
        "no_execution_close_proof_count": no_execution_close_proof["no_execution_close_proof_count"],
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
        "safe_to_continue_next_close_staging": True,
        "next_owner_actions": [
            "Review receipt close cards in priority order.",
            "Treat close staging as private review only, not a closed or finalized receipt.",
            "Resolve missing acknowledgments before any future close layer.",
            "Keep draft-vs-final warnings visible.",
            "Keep Tower close gates and blocker close gates active.",
            "Keep no-execution close proof visible without claiming confirmation.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP039 receipt close summary.",
        ],
    }


def _build_carry_forward(close_cards: List[Dict[str, Any]], next_close_staging: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VRCC-CF-{card['priority_rank']:03d}",
            "close_card_id": card["close_card_id"],
            "receipt_draft_id": card["receipt_draft_id"],
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "priority_id": card["priority_id"],
            "review_group_id": card["review_group_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "readiness_label": card["readiness_label"],
            "close_readiness_label": card["close_readiness_label"],
            "carry_forward_status": "READY_FOR_GP039_RECEIPT_CLOSE_SUMMARY",
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
            "safe_to_carry_to_gp039": True,
        }
        for card in close_cards
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp039_count": len(items),
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
        "safe_to_carry_to_gp039": True,
        "next_close_staging_count": next_close_staging["next_close_staging_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_receipt_review_close_staging_payload())


def get_receipt_review_close_staging_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "close_truth": payload["close_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "close_summary": payload["close_summary"],
        "gp037_connection": payload["gp037_connection"],
    }


def get_receipt_review_close_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "close_cards": payload["close_cards"],
        "close_card_count": len(payload["close_cards"]),
    }


def get_receipt_review_close_readiness() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "close_readiness": payload["close_readiness"],
    }


def get_receipt_review_missing_ack_checks() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "missing_ack_checks": payload["missing_ack_checks"],
    }


def get_receipt_review_draft_final_warnings() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "draft_final_warnings": payload["draft_final_warnings"],
    }


def get_receipt_review_tower_close_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_close_gates": payload["tower_close_gates"],
    }


def get_receipt_review_blocker_close_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_close_gates": payload["blocker_close_gates"],
    }


def get_receipt_review_no_execution_close_proof() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_execution_close_proof": payload["no_execution_close_proof"],
    }


def get_receipt_review_next_close_staging() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_close_staging": payload["next_close_staging"],
    }


def get_receipt_review_close_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp038_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp038_status": payload["gp038_status"],
        "close_truth": payload["close_truth"],
        "close_summary": payload["close_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp037_connection": payload["gp037_connection"],
    }


def render_receipt_review_close_staging_page() -> str:
    payload = clone_payload()
    summary = payload["close_summary"]
    truth = payload["close_truth"]
    cards = payload["close_cards"]
    next_close = payload["next_close_staging"]

    card_html = "\n".join(_render_close_card(card) for card in cards)
    next_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['packet_title'])}</strong>
            <span>{escape(item['next_close_status'])} · closed: {str(item['receipt_closed']).lower()}</span>
          </div>
          <div class="pill {'danger' if item['priority_rank'] <= 3 or item['priority_rank'] == 998 else 'warn'}">Rank {item['priority_rank']}</div>
        </div>
        """
        for item in next_close["next_close_staging_items"][:10]
    )

    owner_actions = "\n".join(f"<li>{escape(action)}</li>" for action in next_close["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Receipt Review Close Staging · GP038</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 038</div>
        <h1>Receipt Review Close Staging</h1>
        <p class="hero-copy">
          GP038 turns reviewed-decision receipt drafts into close staging. It creates close cards,
          readiness labels, missing acknowledgment checks, draft-vs-final warnings, Tower close gates,
          blocker close gates, no-execution close proof, and carry-forward into GP039. Nothing closes here.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['close_card_count']}</strong>
            <span>close cards</span>
          </div>
          <div class="metric">
            <strong>{summary['missing_ack_check_count']}</strong>
            <span>missing ack checks</span>
          </div>
          <div class="metric">
            <strong>{summary['draft_final_warning_count']}</strong>
            <span>draft/final warnings</span>
          </div>
          <div class="metric">
            <strong>{summary['closed_receipt_count']}</strong>
            <span>closed receipts</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Close staging ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Not closed</span>
          <span class="pill danger">No finalized receipt</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Receipt Review Close Cards</h2>
      <p>
        Each receipt draft now has close staging. Nothing is closed, finalized, exported, delivered, approved, or executed.
      </p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Sorted Next Close Staging</h2>
        <p>Close staging stays in priority order while boundary close items remain visible.</p>
        <div>
          {next_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP038 prepares GP039 receipt close summary.</p>
        <ul>
          {owner_actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP038 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['cards_route'])}</code>
        <code>{escape(summary['readiness_route'])}</code>
        <code>{escape(summary['missing_ack_checks_route'])}</code>
        <code>{escape(summary['draft_final_warnings_route'])}</code>
        <code>{escape(summary['tower_close_gates_route'])}</code>
        <code>{escape(summary['blocker_close_gates_route'])}</code>
        <code>{escape(summary['no_execution_close_proof_route'])}</code>
        <code>{escape(summary['next_close_staging_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp038_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Close Truth</h2>
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


def _render_close_card(card: Dict[str, Any]) -> str:
    chip_class = "danger" if card["priority_rank"] <= 3 else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(card['packet_title'])}</div>
            <div class="meta">
              Close card: <code>{escape(card['close_card_id'])}</code><br>
              Rank: <code>{card['priority_rank']}</code><br>
              Status: <code>{escape(card['close_stage_status'])}</code><br>
              Closed: <code>{str(card['receipt_closed']).lower()}</code><br>
              Finalized: <code>{str(card['receipt_finalized']).lower()}</code>
            </div>
          </div>
          <span class="pill {chip_class}">Not closed</span>
        </div>
      </article>
    """
