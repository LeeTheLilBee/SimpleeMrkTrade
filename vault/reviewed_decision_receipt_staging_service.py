"""
VAULT GIANT PACK 037 — Reviewed Decision Receipt Staging

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP036 owner decision review by staging private receipt drafts.

Purpose:
- Stage reviewed-decision receipt drafts from owner decision review cards.
- Stage acknowledgment receipt previews.
- Stage no-execution receipt proof.
- Stage Tower-gate receipt references.
- Stage blocker receipt references.
- Sort next receipt staging.
- Carry receipt staging forward to GP038.

Important truth:
- GP037 stages receipt drafts only.
- GP037 does not finalize receipts.
- GP037 does not claim owner review happened.
- GP037 does not claim Tower gates were acknowledged.
- GP037 does not claim blockers were acknowledged.
- GP037 does not claim no-execution was confirmed.
- GP037 is not a raw file storage provider.
- GP037 does not unlock direct upload.
- GP037 does not create external packet delivery.
- GP037 does not export raw or unredacted packet bodies.
- GP037 does not create public proof.
- GP037 does not open seller/broker/trustee/external portals.
- GP037 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.owner_decision_review_service import get_owner_decision_review_payload


PACK_ID = "VAULT_GP037"
PACK_NAME = "Reviewed Decision Receipt Staging"
SCHEMA_VERSION = "vault.reviewed_decision_receipt_staging.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

ACK_TYPES = [
    {
        "ack_type": "tower_gate_ack",
        "label": "Tower Gate Acknowledgment Preview",
        "required": True,
    },
    {
        "ack_type": "blocker_ack",
        "label": "Blocker Acknowledgment Preview",
        "required": True,
    },
    {
        "ack_type": "no_execution_ack",
        "label": "No-Execution Confirmation Preview",
        "required": True,
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault stages receipt drafts but does not execute actions.",
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
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_reviewed_decision_receipt_staging_payload() -> Dict[str, Any]:
    gp036 = get_owner_decision_review_payload()

    review_cards = gp036["review_cards"]

    receipt_drafts = [
        _build_receipt_draft(card)
        for card in review_cards
    ]

    ack_receipt_previews = _build_ack_receipt_previews(receipt_drafts)
    no_execution_proof = _build_no_execution_proof(receipt_drafts)
    tower_receipt_refs = _build_tower_receipt_refs(receipt_drafts)
    blocker_receipt_refs = _build_blocker_receipt_refs(receipt_drafts)
    next_receipts = _build_next_receipts(receipt_drafts, ack_receipt_previews, no_execution_proof)
    carry_forward = _build_carry_forward(receipt_drafts, next_receipts)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "reviewed_decision_receipt_staging",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "receipt_truth": {
            "reviewed_decision_receipt_staging_enabled": True,
            "receipt_drafts_enabled": True,
            "ack_receipt_previews_enabled": True,
            "no_execution_receipt_proof_enabled": True,
            "tower_gate_receipt_refs_enabled": True,
            "blocker_receipt_refs_enabled": True,
            "metadata_only": True,
            "private_receipt_staging_only": True,
            "receipt_staging_means_draft_not_final": True,
            "receipt_finalization_enabled": False,
            "finalized_receipt_count": 0,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp037",
            "safe_next_unlock": "GP038 can deepen receipt review/close staging without unlocking raw storage, external delivery, public proof, portals, export, auto-run, approval, or execution.",
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
        "receipt_summary": {
            "room_title": "Vault Reviewed Decision Receipt Staging",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/reviewed-decision-receipt-staging",
            "json_route": "/vault/reviewed-decision-receipt-staging.json",
            "drafts_route": "/vault/reviewed-decision-receipt-drafts.json",
            "ack_previews_route": "/vault/reviewed-decision-ack-receipt-previews.json",
            "no_execution_proof_route": "/vault/reviewed-decision-no-execution-proof.json",
            "tower_refs_route": "/vault/reviewed-decision-tower-receipt-refs.json",
            "blocker_refs_route": "/vault/reviewed-decision-blocker-receipt-refs.json",
            "next_receipts_route": "/vault/reviewed-decision-next-receipts.json",
            "carry_forward_route": "/vault/reviewed-decision-receipt-carry-forward.json",
            "gp037_status_route": "/vault/gp037-status.json",
            "receipt_draft_count": len(receipt_drafts),
            "ack_receipt_preview_count": ack_receipt_previews["ack_receipt_preview_count"],
            "no_execution_receipt_count": no_execution_proof["no_execution_receipt_count"],
            "tower_receipt_ref_count": tower_receipt_refs["tower_receipt_ref_count"],
            "blocker_receipt_ref_count": blocker_receipt_refs["blocker_receipt_ref_count"],
            "next_receipt_count": next_receipts["next_receipt_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "finalized_receipt_count": 0,
            "official_receipt_claimed_count": 0,
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
            "completed_count": 0,
            "metadata_only": True,
        },
        "receipt_drafts": receipt_drafts,
        "ack_receipt_previews": ack_receipt_previews,
        "no_execution_proof": no_execution_proof,
        "tower_receipt_refs": tower_receipt_refs,
        "blocker_receipt_refs": blocker_receipt_refs,
        "next_receipts": next_receipts,
        "carry_forward": carry_forward,
        "gp036_connection": {
            "gp036_pack_id": gp036["pack"]["id"],
            "gp036_ready": gp036["gp036_status"]["ready"],
            "gp036_safe_to_continue": gp036["gp036_status"]["safe_to_continue_to_gp037"],
            "gp036_vault_done": gp036["gp036_status"]["vault_done"],
            "gp036_section": gp036["pack"]["section"],
            "gp036_review_card_count": gp036["review_summary"]["review_card_count"],
            "gp036_selection_preview_count": gp036["review_summary"]["selection_preview_count"],
            "gp036_no_execution_confirmation_count": gp036["review_summary"]["no_execution_confirmation_count"],
            "gp036_next_review_count": gp036["review_summary"]["next_review_count"],
        },
        "gp037_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp036_owner_decision_review_connected": True,
            "reviewed_decision_receipt_staging_ready": True,
            "safe_to_continue_to_gp038": True,
            "vault_done": False,
            "metadata_only_receipt_staging": True,
            "private_receipt_staging_only": True,
            "receipt_drafts_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp037",
            "next_pack": "VAULT_GP038_RECEIPT_REVIEW_CLOSE_STAGING_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_receipt_draft(card: Dict[str, Any]) -> Dict[str, Any]:
    active_codes = sorted(set(card["blocked_codes"]) | {
        "REVIEWED_DECISION_RECEIPT_STAGING_PRIVATE_ONLY",
        "RECEIPT_DRAFT_NOT_FINALIZED",
    })

    return {
        "receipt_draft_id": f"VRDR-{card['priority_rank']:03d}",
        "receipt_stage_id": f"VRST-{card['priority_rank']:03d}",
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
        "recommended_safe_option": card["recommended_safe_option"],
        "receipt_draft_status": "RECEIPT_DRAFT_STAGED_NOT_FINALIZED",
        "receipt_type": "reviewed_decision_receipt_draft",
        "metadata_only": True,
        "private_receipt_staging_only": True,
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
        "tower_ack_required": True,
        "tower_acknowledged": False,
        "blocker_ack_required": True,
        "blocker_acknowledged": False,
        "no_execution_confirmation_required": True,
        "no_execution_confirmed": False,
        "detail_count": card["detail_count"],
        "review_lane_count": card["review_lane_count"],
        "redacted_preview_slot_count": card["redacted_preview_slot_count"],
        "tower_gate_count": card["tower_gate_count"],
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
        "safe_to_finalize_receipt": False,
        "safe_to_deliver_externally": False,
        "safe_to_export": False,
        "safe_to_carry_to_gp038": True,
        "receipt_note": f"Draft receipt staged for {card['packet_title']}. This is not a finalized receipt and does not claim review, acknowledgment, confirmation, approval, delivery, export, or execution.",
    }


def _build_ack_receipt_previews(receipt_drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = []

    for draft in receipt_drafts:
        for ack in ACK_TYPES:
            items.append(
                {
                    "ack_receipt_preview_id": f"VRAP-{draft['priority_rank']:03d}-{ack['ack_type']}",
                    "receipt_draft_id": draft["receipt_draft_id"],
                    "review_card_id": draft["review_card_id"],
                    "packet_id": draft["packet_id"],
                    "packet_title": draft["packet_title"],
                    "priority_rank": draft["priority_rank"],
                    "ack_type": ack["ack_type"],
                    "ack_label": ack["label"],
                    "ack_required": ack["required"],
                    "ack_claimed": False,
                    "acknowledged": False,
                    "preview_status": "ACK_RECEIPT_PREVIEW_ONLY_NOT_ACKNOWLEDGED",
                    "metadata_only": True,
                    "private_receipt_staging_only": True,
                    "receipt_finalized": False,
                    "official_receipt_claimed": False,
                    "owner_review_required": True,
                    "owner_confirmed": False,
                    "completed": False,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_carry_to_gp038": True,
                }
            )

    return {
        "ack_receipt_preview_items": items,
        "ack_receipt_preview_count": len(items),
        "ack_type_count": len(ACK_TYPES),
        "receipt_draft_count": len(receipt_drafts),
        "ack_claimed_count": 0,
        "acknowledged_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "executes_action_count": 0,
        "safe_to_continue_ack_receipt_previews": True,
    }


def _build_no_execution_proof(receipt_drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "no_execution_receipt_id": f"VRNE-{draft['priority_rank']:03d}",
            "receipt_draft_id": draft["receipt_draft_id"],
            "review_card_id": draft["review_card_id"],
            "packet_id": draft["packet_id"],
            "packet_title": draft["packet_title"],
            "priority_rank": draft["priority_rank"],
            "no_execution_receipt_status": "NO_EXECUTION_PROOF_STAGED_NOT_CONFIRMED",
            "no_execution_confirmation_required": True,
            "no_execution_confirmed": False,
            "no_execution_confirmation_claimed": False,
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
            "private_receipt_staging_only": True,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp038": True,
        }
        for draft in receipt_drafts
    ]

    return {
        "no_execution_receipt_items": items,
        "no_execution_receipt_count": len(items),
        "no_execution_confirmation_required_count": len(items),
        "no_execution_confirmed_count": 0,
        "no_execution_confirmation_claimed_count": 0,
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
        "safe_to_continue_no_execution_proof": True,
    }


def _build_tower_receipt_refs(receipt_drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_receipt_ref_id": f"VRTR-{draft['priority_rank']:03d}",
            "receipt_draft_id": draft["receipt_draft_id"],
            "review_card_id": draft["review_card_id"],
            "packet_id": draft["packet_id"],
            "packet_title": draft["packet_title"],
            "priority_rank": draft["priority_rank"],
            "tower_receipt_ref_status": "TOWER_GATE_RECEIPT_REFERENCE_STAGED_NOT_ACKNOWLEDGED",
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
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "portal_access_allowed": False,
            "safe_to_carry_to_gp038": True,
        }
        for draft in receipt_drafts
    ]

    return {
        "tower_receipt_ref_items": items,
        "tower_receipt_ref_count": len(items),
        "tower_ack_required_count": len(items),
        "tower_acknowledged_count": 0,
        "tower_ack_claimed_count": 0,
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "tower_export_lock_required_count": len(items),
        "vault_override_allowed_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_receipt_refs_preserve_authority": True,
    }


def _build_blocker_receipt_refs(receipt_drafts: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "blocker_receipt_ref_id": f"VRBR-{draft['priority_rank']:03d}",
            "receipt_draft_id": draft["receipt_draft_id"],
            "review_card_id": draft["review_card_id"],
            "packet_id": draft["packet_id"],
            "packet_title": draft["packet_title"],
            "priority_rank": draft["priority_rank"],
            "blocker_receipt_ref_status": "BLOCKER_RECEIPT_REFERENCE_STAGED_NOT_ACKNOWLEDGED",
            "blocker_ack_required": True,
            "blocker_acknowledged": False,
            "blocker_ack_claimed": False,
            "blocked_code_count": draft["blocked_code_count"],
            "blocked_codes": draft["blocked_codes"],
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
            "receipt_finalized": False,
            "official_receipt_claimed": False,
            "safe_to_carry_to_gp038": True,
        }
        for draft in receipt_drafts
    ]

    active_codes = sorted({code for item in items for code in item["blocked_codes"]})

    return {
        "blocker_receipt_ref_items": items,
        "active_block_codes": active_codes,
        "blocker_receipt_ref_count": len(items),
        "active_block_code_count": len(active_codes),
        "blocker_ack_required_count": len(items),
        "blocker_acknowledged_count": 0,
        "blocker_ack_claimed_count": 0,
        "all_restricted_paths_locked": True,
        "safe_to_override_inside_vault_count": 0,
        "receipt_finalized_count": 0,
        "official_receipt_claimed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_blocker_receipt_refs": True,
    }


def _build_next_receipts(
    receipt_drafts: List[Dict[str, Any]],
    ack_receipt_previews: Dict[str, Any],
    no_execution_proof: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_receipt_id": f"VRNX-{draft['priority_rank']:03d}",
            "receipt_draft_id": draft["receipt_draft_id"],
            "review_card_id": draft["review_card_id"],
            "packet_id": draft["packet_id"],
            "packet_title": draft["packet_title"],
            "priority_rank": draft["priority_rank"],
            "readiness_label": draft["readiness_label"],
            "recommended_safe_option": draft["recommended_safe_option"],
            "next_receipt_status": "READY_FOR_RECEIPT_REVIEW_STAGING_NOT_FINALIZED",
            "metadata_only": True,
            "private_receipt_staging_only": True,
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
            "safe_to_carry_to_gp038": True,
        }
        for draft in receipt_drafts
    ]

    items.append(
        {
            "next_receipt_id": "VRNX-998",
            "receipt_draft_id": "BOUNDARY-LOCKS",
            "review_card_id": "BOUNDARY-LOCKS",
            "packet_id": "ALL_PACKETS",
            "packet_title": "All Reviewed Decision Receipt Boundaries",
            "priority_rank": 998,
            "readiness_label": "RECEIPT_BOUNDARIES_LOCKED",
            "recommended_safe_option": "HOLD_FOR_BLOCKER_RESOLUTION",
            "next_receipt_status": "BOUNDARY_LOCKED_NO_FINALIZATION",
            "metadata_only": True,
            "private_receipt_staging_only": True,
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
            "safe_to_carry_to_gp038": True,
        }
    )

    items.append(
        {
            "next_receipt_id": "VRNX-999",
            "receipt_draft_id": "NEXT-GP038",
            "review_card_id": "NEXT-GP038",
            "packet_id": "NEXT_VAULT_PACK",
            "packet_title": "GP038 Receipt Review Close Staging",
            "priority_rank": 999,
            "readiness_label": "READY_FOR_GP038",
            "recommended_safe_option": "CARRY_FORWARD_TO_GP038",
            "next_receipt_status": "NEXT_BUILD_READY",
            "metadata_only": True,
            "private_receipt_staging_only": True,
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
            "safe_to_carry_to_gp038": True,
        }
    )

    sorted_items = sorted(items, key=lambda item: (item["priority_rank"], item["next_receipt_id"]))

    return {
        "next_receipt_items": sorted_items,
        "next_receipt_count": len(sorted_items),
        "packet_receipt_count": len(receipt_drafts),
        "boundary_receipt_count": 1,
        "next_build_receipt_count": 1,
        "ack_receipt_preview_count": ack_receipt_previews["ack_receipt_preview_count"],
        "no_execution_receipt_count": no_execution_proof["no_execution_receipt_count"],
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
        "safe_to_continue_next_receipts": True,
        "next_owner_actions": [
            "Review staged receipt drafts in priority order.",
            "Treat receipt drafts as previews only, not finalized receipts.",
            "Do not claim owner review, Tower acknowledgment, blocker acknowledgment, or no-execution confirmation yet.",
            "Keep raw storage, direct upload, export, external delivery, public proof, portals, approval, and execution locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP038 receipt review close staging.",
        ],
    }


def _build_carry_forward(receipt_drafts: List[Dict[str, Any]], next_receipts: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VRDR-CF-{draft['priority_rank']:03d}",
            "receipt_draft_id": draft["receipt_draft_id"],
            "review_card_id": draft["review_card_id"],
            "decision_prep_id": draft["decision_prep_id"],
            "priority_id": draft["priority_id"],
            "review_group_id": draft["review_group_id"],
            "packet_id": draft["packet_id"],
            "packet_title": draft["packet_title"],
            "priority_rank": draft["priority_rank"],
            "readiness_label": draft["readiness_label"],
            "recommended_safe_option": draft["recommended_safe_option"],
            "carry_forward_status": "READY_FOR_GP038_RECEIPT_REVIEW_CLOSE_STAGING",
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
            "safe_to_carry_to_gp038": True,
        }
        for draft in receipt_drafts
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp038_count": len(items),
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
        "safe_to_carry_to_gp038": True,
        "next_receipt_count": next_receipts["next_receipt_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_reviewed_decision_receipt_staging_payload())


def get_reviewed_decision_receipt_staging_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_truth": payload["receipt_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "receipt_summary": payload["receipt_summary"],
        "gp036_connection": payload["gp036_connection"],
    }


def get_reviewed_decision_receipt_drafts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_drafts": payload["receipt_drafts"],
        "receipt_draft_count": len(payload["receipt_drafts"]),
    }


def get_reviewed_decision_ack_receipt_previews() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "ack_receipt_previews": payload["ack_receipt_previews"],
    }


def get_reviewed_decision_no_execution_proof() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "no_execution_proof": payload["no_execution_proof"],
    }


def get_reviewed_decision_tower_receipt_refs() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_receipt_refs": payload["tower_receipt_refs"],
    }


def get_reviewed_decision_blocker_receipt_refs() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_receipt_refs": payload["blocker_receipt_refs"],
    }


def get_reviewed_decision_next_receipts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_receipts": payload["next_receipts"],
    }


def get_reviewed_decision_receipt_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp037_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp037_status": payload["gp037_status"],
        "receipt_truth": payload["receipt_truth"],
        "receipt_summary": payload["receipt_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp036_connection": payload["gp036_connection"],
    }


def render_reviewed_decision_receipt_staging_page() -> str:
    payload = clone_payload()
    summary = payload["receipt_summary"]
    truth = payload["receipt_truth"]
    drafts = payload["receipt_drafts"]
    next_receipts = payload["next_receipts"]

    draft_html = "\n".join(_render_receipt_draft_card(draft) for draft in drafts)
    next_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['packet_title'])}</strong>
            <span>{escape(item['next_receipt_status'])} · finalized: {str(item['receipt_finalized']).lower()}</span>
          </div>
          <div class="pill {'danger' if item['priority_rank'] <= 3 or item['priority_rank'] == 998 else 'warn'}">Rank {item['priority_rank']}</div>
        </div>
        """
        for item in next_receipts["next_receipt_items"][:10]
    )

    owner_actions = "\n".join(f"<li>{escape(action)}</li>" for action in next_receipts["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Reviewed Decision Receipt Staging · GP037</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 037</div>
        <h1>Reviewed Decision Receipt Staging</h1>
        <p class="hero-copy">
          GP037 stages private receipt drafts from owner decision review. It creates reviewed-decision
          receipt drafts, acknowledgment receipt previews, no-execution receipt proof, Tower-gate receipt references,
          blocker receipt references, sorted next receipts, and carry-forward into GP038. These are drafts only.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['receipt_draft_count']}</strong>
            <span>receipt drafts</span>
          </div>
          <div class="metric">
            <strong>{summary['ack_receipt_preview_count']}</strong>
            <span>ack previews</span>
          </div>
          <div class="metric">
            <strong>{summary['no_execution_receipt_count']}</strong>
            <span>no-execution receipts</span>
          </div>
          <div class="metric">
            <strong>{summary['finalized_receipt_count']}</strong>
            <span>finalized receipts</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Receipt drafts staged</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Not finalized</span>
          <span class="pill danger">No official claim</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Reviewed Decision Receipt Drafts</h2>
      <p>
        Each owner review card now has a private receipt draft. Nothing is finalized, exported, delivered, approved, or executed.
      </p>
      <div class="grid">
        {draft_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Sorted Next Receipts</h2>
        <p>Receipt drafts stay in priority order while boundary receipts remain visible.</p>
        <div>
          {next_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP037 prepares GP038 receipt review close staging.</p>
        <ul>
          {owner_actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP037 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['drafts_route'])}</code>
        <code>{escape(summary['ack_previews_route'])}</code>
        <code>{escape(summary['no_execution_proof_route'])}</code>
        <code>{escape(summary['tower_refs_route'])}</code>
        <code>{escape(summary['blocker_refs_route'])}</code>
        <code>{escape(summary['next_receipts_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp037_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Receipt Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Finalization enabled:
        <code>{str(truth['receipt_finalization_enabled']).lower()}</code>.
        Official receipt claims:
        <code>{truth['official_receipt_claimed_count']}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_receipt_draft_card(draft: Dict[str, Any]) -> str:
    chip_class = "danger" if draft["priority_rank"] <= 3 else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(draft['packet_title'])}</div>
            <div class="meta">
              Draft: <code>{escape(draft['receipt_draft_id'])}</code><br>
              Rank: <code>{draft['priority_rank']}</code><br>
              Status: <code>{escape(draft['receipt_draft_status'])}</code><br>
              Finalized: <code>{str(draft['receipt_finalized']).lower()}</code><br>
              Official claim: <code>{str(draft['official_receipt_claimed']).lower()}</code>
            </div>
          </div>
          <span class="pill {chip_class}">Draft only</span>
        </div>
      </article>
    """
