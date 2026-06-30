"""
VAULT GIANT PACK 036 — Owner Decision Review

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP035 packet review decision prep by creating private owner
decision review surfaces.

Purpose:
- Build owner decision review cards from decision prep records.
- Track review status without auto-confirming.
- Preview safe decision selection without selecting anything.
- Require Tower gate acknowledgment.
- Require blocker acknowledgment.
- Require no-execution confirmation.
- Sort next owner reviews.
- Carry owner review state forward to GP037.

Important truth:
- GP036 is not a raw file storage provider.
- GP036 does not unlock direct upload.
- GP036 does not create external packet delivery.
- GP036 does not export raw or unredacted packet bodies.
- GP036 does not create public proof.
- GP036 does not open seller/broker/trustee/external portals.
- GP036 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Owner decision review means private metadata review only.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.packet_review_decision_prep_service import get_packet_review_decision_prep_payload


PACK_ID = "VAULT_GP036"
PACK_NAME = "Owner Decision Review"
SCHEMA_VERSION = "vault.owner_decision_review.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

OWNER_REVIEW_STEPS = [
    "review_packet_context",
    "review_recommended_safe_option",
    "acknowledge_tower_gates",
    "acknowledge_blockers",
    "confirm_no_execution",
    "carry_forward_to_gp037",
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault reviews owner decisions but does not execute actions.",
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
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_owner_decision_review_payload() -> Dict[str, Any]:
    gp035 = get_packet_review_decision_prep_payload()

    decision_records = gp035["decision_records"]

    review_cards = [
        _build_review_card(record)
        for record in decision_records
    ]

    review_status = _build_review_status(review_cards)
    selection_preview = _build_selection_preview(review_cards)
    tower_ack = _build_tower_ack(review_cards)
    blocker_ack = _build_blocker_ack(review_cards)
    no_execution = _build_no_execution(review_cards)
    next_reviews = _build_next_reviews(review_cards, tower_ack, blocker_ack, no_execution)
    carry_forward = _build_carry_forward(review_cards, next_reviews)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "owner_decision_review",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "review_truth": {
            "owner_decision_review_enabled": True,
            "metadata_only": True,
            "private_owner_review_only": True,
            "review_means_owner_visibility_not_approval": True,
            "review_cards_enabled": True,
            "safe_selection_preview_enabled": True,
            "tower_gate_ack_enabled": True,
            "blocker_ack_enabled": True,
            "no_execution_confirmation_enabled": True,
            "next_review_sorting_enabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp036",
            "safe_next_unlock": "GP037 can deepen reviewed-decision receipt staging without unlocking raw storage, external delivery, public proof, portals, export, auto-run, approval, or execution.",
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
        "review_summary": {
            "room_title": "Vault Owner Decision Review",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/owner-decision-review",
            "json_route": "/vault/owner-decision-review.json",
            "cards_route": "/vault/owner-decision-review-cards.json",
            "status_route": "/vault/owner-decision-review-status.json",
            "selection_preview_route": "/vault/owner-decision-review-selection-preview.json",
            "tower_ack_route": "/vault/owner-decision-review-tower-ack.json",
            "blocker_ack_route": "/vault/owner-decision-review-blocker-ack.json",
            "no_execution_route": "/vault/owner-decision-review-no-execution.json",
            "next_reviews_route": "/vault/owner-decision-review-next-reviews.json",
            "carry_forward_route": "/vault/owner-decision-review-carry-forward.json",
            "gp036_status_route": "/vault/gp036-status.json",
            "review_card_count": len(review_cards),
            "review_status_count": review_status["review_status_count"],
            "selection_preview_count": selection_preview["selection_preview_count"],
            "tower_ack_count": tower_ack["tower_ack_count"],
            "blocker_ack_count": blocker_ack["blocker_ack_count"],
            "no_execution_confirmation_count": no_execution["no_execution_confirmation_count"],
            "next_review_count": next_reviews["next_review_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
            "completed_count": 0,
            "metadata_only": True,
        },
        "review_cards": review_cards,
        "review_status": review_status,
        "selection_preview": selection_preview,
        "tower_ack": tower_ack,
        "blocker_ack": blocker_ack,
        "no_execution": no_execution,
        "next_reviews": next_reviews,
        "carry_forward": carry_forward,
        "gp035_connection": {
            "gp035_pack_id": gp035["pack"]["id"],
            "gp035_ready": gp035["gp035_status"]["ready"],
            "gp035_safe_to_continue": gp035["gp035_status"]["safe_to_continue_to_gp036"],
            "gp035_vault_done": gp035["gp035_status"]["vault_done"],
            "gp035_section": gp035["pack"]["section"],
            "gp035_decision_record_count": gp035["decision_summary"]["decision_record_count"],
            "gp035_safe_option_count": gp035["decision_summary"]["safe_option_count"],
            "gp035_unsafe_option_count": gp035["decision_summary"]["unsafe_option_count"],
            "gp035_next_decision_count": gp035["decision_summary"]["next_decision_count"],
        },
        "gp036_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp035_decision_prep_connected": True,
            "owner_decision_review_ready": True,
            "safe_to_continue_to_gp037": True,
            "vault_done": False,
            "metadata_only_review": True,
            "private_owner_review_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp036",
            "next_pack": "VAULT_GP037_REVIEWED_DECISION_RECEIPT_STAGING_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_review_card(record: Dict[str, Any]) -> Dict[str, Any]:
    active_codes = sorted(set(record["blocked_codes"]) | {"OWNER_DECISION_REVIEW_PRIVATE_ONLY"})

    return {
        "review_card_id": f"VODR-{record['priority_rank']:03d}",
        "decision_prep_id": record["decision_prep_id"],
        "priority_id": record["priority_id"],
        "review_group_id": record["review_group_id"],
        "packet_id": record["packet_id"],
        "assembly_id": record["assembly_id"],
        "lane": record["lane"],
        "packet_title": record["packet_title"],
        "priority_rank": record["priority_rank"],
        "priority_band": record["priority_band"],
        "readiness_label": record["readiness_label"],
        "recommended_safe_option": record["recommended_safe_option"],
        "owner_prompt": record["owner_prompt"],
        "review_card_status": "READY_FOR_OWNER_REVIEW_NO_DECISION_SELECTED",
        "review_steps": list(OWNER_REVIEW_STEPS),
        "metadata_only": True,
        "private_owner_review_only": True,
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
        "detail_count": record["detail_count"],
        "review_lane_count": record["review_lane_count"],
        "redacted_preview_slot_count": record["redacted_preview_slot_count"],
        "tower_gate_count": record["tower_gate_count"],
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
        "safe_to_review_privately": True,
        "safe_to_deliver_externally": False,
        "safe_to_export": False,
        "safe_to_carry_to_gp037": True,
        "owner_note": f"Review {record['packet_title']} privately. No selection, approval, export, delivery, or execution occurs in GP036.",
    }


def _build_review_status(review_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "review_status_id": f"VODRS-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "review_card_status": card["review_card_status"],
            "owner_review_required": True,
            "owner_reviewed": False,
            "owner_confirmed": False,
            "decision_selected": False,
            "completed": False,
            "metadata_only": True,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "can_execute_from_vault": False,
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    return {
        "review_status_items": items,
        "review_status_count": len(items),
        "owner_review_required_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "decision_selected_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_review_status": True,
    }


def _build_selection_preview(review_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "selection_preview_id": f"VODSP-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "recommended_safe_option": card["recommended_safe_option"],
            "selection_preview_status": "SAFE_SELECTION_PREVIEW_ONLY_NOT_SELECTED",
            "safe_selection_preview": True,
            "decision_selected": False,
            "selected_decision_code": None,
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "auto_confirm_allowed": False,
            "approval_allowed": False,
            "executes_action": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    return {
        "selection_preview_items": items,
        "selection_preview_count": len(items),
        "safe_selection_preview_count": len(items),
        "decision_selected_count": 0,
        "owner_confirmed_count": 0,
        "auto_confirm_allowed_count": 0,
        "approval_allowed_count": 0,
        "executes_action_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_selection_preview": True,
    }


def _build_tower_ack(review_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_ack_id": f"VODTA-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "tower_ack_status": "TOWER_GATES_VISIBLE_NOT_ACKNOWLEDGED",
            "tower_ack_required": True,
            "tower_acknowledged": False,
            "tower_clearance_required": True,
            "tower_step_up_required": True,
            "tower_export_lock_required": True,
            "tower_external_access_required": True,
            "tower_portal_unlock_required": True,
            "tower_sensitive_visibility_required": True,
            "vault_can_override_tower": False,
            "metadata_only": True,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "portal_access_allowed": False,
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    return {
        "tower_ack_items": items,
        "tower_ack_count": len(items),
        "tower_ack_required_count": len(items),
        "tower_acknowledged_count": 0,
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "tower_export_lock_required_count": len(items),
        "vault_override_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_acks_preserve_authority": True,
    }


def _build_blocker_ack(review_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "blocker_ack_id": f"VODBA-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "blocker_ack_status": "BLOCKERS_VISIBLE_NOT_ACKNOWLEDGED",
            "blocker_ack_required": True,
            "blocker_acknowledged": False,
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
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    active_codes = sorted({code for item in items for code in item["blocked_codes"]})

    return {
        "blocker_ack_items": items,
        "active_block_codes": active_codes,
        "blocker_ack_count": len(items),
        "active_block_code_count": len(active_codes),
        "blocker_ack_required_count": len(items),
        "blocker_acknowledged_count": 0,
        "all_restricted_paths_locked": True,
        "safe_to_override_inside_vault_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_blocker_ack": True,
    }


def _build_no_execution(review_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "no_execution_id": f"VODNE-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "no_execution_status": "NO_EXECUTION_CONFIRMATION_REQUIRED_NOT_CONFIRMED",
            "no_execution_confirmation_required": True,
            "no_execution_confirmed": False,
            "auto_action_execution_enabled": False,
            "execution_engine_enabled": False,
            "approval_allowed": False,
            "financing_decision_enabled": False,
            "legal_advice_enabled": False,
            "raw_document_verification_claimed": False,
            "auto_packet_approval_enabled": False,
            "metadata_only": True,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    return {
        "no_execution_items": items,
        "no_execution_confirmation_count": len(items),
        "no_execution_confirmation_required_count": len(items),
        "no_execution_confirmed_count": 0,
        "auto_action_execution_enabled_count": 0,
        "execution_engine_enabled_count": 0,
        "approval_allowed_count": 0,
        "financing_decision_enabled_count": 0,
        "legal_advice_enabled_count": 0,
        "raw_document_verification_claimed_count": 0,
        "auto_packet_approval_enabled_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_no_execution": True,
    }


def _build_next_reviews(
    review_cards: List[Dict[str, Any]],
    tower_ack: Dict[str, Any],
    blocker_ack: Dict[str, Any],
    no_execution: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_review_id": f"VODNR-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "readiness_label": card["readiness_label"],
            "recommended_safe_option": card["recommended_safe_option"],
            "next_review_status": "READY_FOR_OWNER_REVIEW_NO_EXECUTION",
            "metadata_only": True,
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
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    items.append(
        {
            "next_review_id": "VODNR-998",
            "review_card_id": "BOUNDARY-LOCKS",
            "decision_prep_id": "BOUNDARY-LOCKS",
            "packet_id": "ALL_PACKETS",
            "packet_title": "All Owner Decision Review Boundaries",
            "priority_rank": 998,
            "readiness_label": "BOUNDARIES_LOCKED",
            "recommended_safe_option": "HOLD_FOR_BLOCKER_RESOLUTION",
            "next_review_status": "BOUNDARY_LOCKED_NO_OVERRIDE",
            "metadata_only": True,
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
            "safe_to_carry_to_gp037": True,
        }
    )

    items.append(
        {
            "next_review_id": "VODNR-999",
            "review_card_id": "NEXT-GP037",
            "decision_prep_id": "NEXT-GP037",
            "packet_id": "NEXT_VAULT_PACK",
            "packet_title": "GP037 Reviewed Decision Receipt Staging",
            "priority_rank": 999,
            "readiness_label": "READY_FOR_GP037",
            "recommended_safe_option": "CARRY_FORWARD_TO_GP037",
            "next_review_status": "NEXT_BUILD_READY",
            "metadata_only": True,
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
            "safe_to_carry_to_gp037": True,
        }
    )

    sorted_items = sorted(items, key=lambda item: (item["priority_rank"], item["next_review_id"]))

    return {
        "next_review_items": sorted_items,
        "next_review_count": len(sorted_items),
        "packet_review_count": len(review_cards),
        "boundary_review_count": 1,
        "next_build_review_count": 1,
        "owner_review_required_count": len(sorted_items),
        "owner_reviewed_count": 0,
        "tower_ack_count": tower_ack["tower_ack_count"],
        "blocker_ack_count": blocker_ack["blocker_ack_count"],
        "no_execution_confirmation_count": no_execution["no_execution_confirmation_count"],
        "decision_selected_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_continue_next_reviews": True,
        "next_owner_actions": [
            "Review owner decision cards in priority order.",
            "Preview safe decision selection only; do not select, approve, export, deliver, or execute.",
            "Acknowledge Tower gates before any future sensitive movement.",
            "Acknowledge blockers before any future decision closure.",
            "Confirm no execution is allowed from Vault.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP037 reviewed decision receipt staging.",
        ],
    }


def _build_carry_forward(review_cards: List[Dict[str, Any]], next_reviews: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VODR-CF-{card['priority_rank']:03d}",
            "review_card_id": card["review_card_id"],
            "decision_prep_id": card["decision_prep_id"],
            "priority_id": card["priority_id"],
            "review_group_id": card["review_group_id"],
            "packet_id": card["packet_id"],
            "packet_title": card["packet_title"],
            "priority_rank": card["priority_rank"],
            "readiness_label": card["readiness_label"],
            "recommended_safe_option": card["recommended_safe_option"],
            "carry_forward_status": "READY_FOR_GP037_REVIEWED_DECISION_RECEIPT_STAGING",
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
            "safe_to_carry_to_gp037": True,
        }
        for card in review_cards
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp037_count": len(items),
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
        "safe_to_carry_to_gp037": True,
        "next_review_count": next_reviews["next_review_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_owner_decision_review_payload())


def get_owner_decision_review_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_truth": payload["review_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "review_summary": payload["review_summary"],
        "gp035_connection": payload["gp035_connection"],
    }


def get_owner_decision_review_cards() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_cards": payload["review_cards"],
        "review_card_count": len(payload["review_cards"]),
    }


def get_owner_decision_review_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_status": payload["review_status"],
    }


def get_owner_decision_review_selection_preview() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "selection_preview": payload["selection_preview"],
    }


def get_owner_decision_review_tower_ack() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_ack": payload["tower_ack"],
    }


def get_owner_decision_review_blocker_ack() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_ack": payload["blocker_ack"],
    }


def get_owner_decision_review_no_execution() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_execution": payload["no_execution"],
    }


def get_owner_decision_review_next_reviews() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_reviews": payload["next_reviews"],
    }


def get_owner_decision_review_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp036_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp036_status": payload["gp036_status"],
        "review_truth": payload["review_truth"],
        "review_summary": payload["review_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp035_connection": payload["gp035_connection"],
    }


def render_owner_decision_review_page() -> str:
    payload = clone_payload()
    summary = payload["review_summary"]
    truth = payload["review_truth"]
    cards = payload["review_cards"]
    next_reviews = payload["next_reviews"]

    card_html = "\n".join(_render_review_card(card) for card in cards)
    next_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['packet_title'])}</strong>
            <span>{escape(item['next_review_status'])} · option: {escape(item['recommended_safe_option'])}</span>
          </div>
          <div class="pill {'danger' if item['priority_rank'] <= 3 or item['priority_rank'] == 998 else 'warn'}">Rank {item['priority_rank']}</div>
        </div>
        """
        for item in next_reviews["next_review_items"][:10]
    )

    owner_actions = "\n".join(f"<li>{escape(action)}</li>" for action in next_reviews["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Owner Decision Review · GP036</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 036</div>
        <h1>Owner Decision Review</h1>
        <p class="hero-copy">
          GP036 turns decision prep into private owner decision review. It creates owner review cards,
          safe selection previews, Tower gate acknowledgment, blocker acknowledgment, no-execution confirmation,
          sorted next reviews, and carry-forward into GP037. This stays metadata-only and private.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['review_card_count']}</strong>
            <span>review cards</span>
          </div>
          <div class="metric">
            <strong>{summary['selection_preview_count']}</strong>
            <span>safe previews</span>
          </div>
          <div class="metric">
            <strong>{summary['no_execution_confirmation_count']}</strong>
            <span>no-execution confirmations</span>
          </div>
          <div class="metric">
            <strong>{str(truth['approval_enabled']).lower()}</strong>
            <span>approval enabled</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Owner review ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">No selection made</span>
          <span class="pill danger">No execution</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Owner Decision Review Cards</h2>
      <p>
        Each decision prep record now has a private review card with no approval, no export, no delivery, and no execution.
      </p>
      <div class="grid">
        {card_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Sorted Next Reviews</h2>
        <p>Owner reviews are sorted by priority while boundaries stay visible.</p>
        <div>
          {next_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP036 prepares GP037 reviewed decision receipt staging.</p>
        <ul>
          {owner_actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP036 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['cards_route'])}</code>
        <code>{escape(summary['status_route'])}</code>
        <code>{escape(summary['selection_preview_route'])}</code>
        <code>{escape(summary['tower_ack_route'])}</code>
        <code>{escape(summary['blocker_ack_route'])}</code>
        <code>{escape(summary['no_execution_route'])}</code>
        <code>{escape(summary['next_reviews_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp036_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Review Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Decision selected:
        <code>{truth['decision_selected_count']}</code>.
        Execution:
        <code>{str(truth['execution_engine_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_review_card(card: Dict[str, Any]) -> str:
    chip_class = "danger" if card["priority_rank"] <= 3 else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(card['packet_title'])}</div>
            <div class="meta">
              Review: <code>{escape(card['review_card_id'])}</code><br>
              Rank: <code>{card['priority_rank']}</code><br>
              Recommended: <code>{escape(card['recommended_safe_option'])}</code><br>
              Decision selected: <code>{str(card['decision_selected']).lower()}</code><br>
              Execution allowed: <code>{str(card['can_execute_from_vault']).lower()}</code>
            </div>
          </div>
          <span class="pill {chip_class}">Rank {card['priority_rank']}</span>
        </div>
      </article>
    """
