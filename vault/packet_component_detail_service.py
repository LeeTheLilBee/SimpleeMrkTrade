"""
VAULT GIANT PACK 032 — Packet Component Detail

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP031 controlled packet assembly by giving every component
its own detail record.

Purpose:
- Explain the component's requirement purpose.
- Explain what the requirement means.
- Link back to packet, assembly, receipt/reference context.
- Track redacted-preview state.
- Track Tower gate state.
- Track blockers.
- Track owner review state.
- Carry each detail record forward to GP033.

Important truth:
- GP032 is not a raw file storage provider.
- GP032 does not unlock direct upload.
- GP032 does not create external packet delivery.
- GP032 does not export raw or unredacted packet bodies.
- GP032 does not create public proof.
- GP032 does not open seller/broker/trustee/external portals.
- GP032 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Packet component detail means private metadata review only.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.controlled_packet_assembly_board_service import (
    get_controlled_packet_assembly_board_payload,
)


PACK_ID = "VAULT_GP032"
PACK_NAME = "Packet Component Detail"
SCHEMA_VERSION = "vault.packet_component_detail.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

COMPONENT_PURPOSES = {
    "requirement_summary": {
        "purpose": "Explain why this packet requires the component before owner review.",
        "meaning": "A metadata-only description of what must be present, not a raw document verification claim.",
        "reference_type": "requirement_reference",
    },
    "redacted_preview_slot": {
        "purpose": "Reserve a safe redacted-preview slot without showing raw body content.",
        "meaning": "Preview is allowed only as redacted owner-safe metadata. Raw body storage remains locked.",
        "reference_type": "redacted_preview_reference",
    },
    "receipt_chain_reference": {
        "purpose": "Connect packet assembly to prior receipt/checklist chain context.",
        "meaning": "A private metadata link to receipt chain review, not public receipt proof.",
        "reference_type": "receipt_chain_reference",
    },
    "owner_action_reference": {
        "purpose": "Connect packet assembly to owner action receipt context.",
        "meaning": "A private owner action reference, not an execution trigger or confirmation.",
        "reference_type": "owner_action_reference",
    },
    "tower_gate_status": {
        "purpose": "Show Tower gate status for sensitive movement.",
        "meaning": "Tower owns clearance, step-up, external access, export locks, portals, and action gates.",
        "reference_type": "tower_gate_reference",
    },
    "blocked_path_summary": {
        "purpose": "Summarize blocked paths before owner review.",
        "meaning": "External delivery, export, public proof, portals, raw storage, and direct upload remain locked.",
        "reference_type": "blocked_path_reference",
    },
    "carry_forward_marker": {
        "purpose": "Prepare this component detail for the next Vault product-depth pack.",
        "meaning": "Safe-to-carry metadata marker only. It does not complete, confirm, export, or execute.",
        "reference_type": "carry_forward_reference",
    },
}

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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault details packet components but does not execute actions.",
    "NO_EXTERNAL_PACKET_DELIVERY": "External packet delivery is disabled.",
    "NO_PACKET_EXPORT": "Packet export is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Controlled packet assembly is private only.",
    "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY": "Packet component detail is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_packet_component_detail_payload() -> Dict[str, Any]:
    gp031 = get_controlled_packet_assembly_board_payload()

    assembly_records = gp031["assembly_records"]
    component_rows = gp031["component_rows"]

    assembly_by_id = {record["assembly_id"]: record for record in assembly_records}

    detail_records = [
        _build_detail_record(component, assembly_by_id[component["assembly_id"]], index + 1)
        for index, component in enumerate(component_rows)
    ]

    requirement_meanings = _build_requirement_meanings(detail_records)
    redacted_preview_state = _build_redacted_preview_state(detail_records)
    tower_gate_state = _build_tower_gate_state(detail_records)
    blocker_wall = _build_blocker_wall(detail_records)
    owner_review = _build_owner_review_state(detail_records, blocker_wall)
    carry_forward = _build_carry_forward(detail_records, owner_review)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "packet_component_detail",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "detail_truth": {
            "packet_component_detail_enabled": True,
            "metadata_only": True,
            "private_detail_only": True,
            "detail_means_owner_review_not_delivery": True,
            "requirement_meaning_enabled": True,
            "linked_reference_enabled": True,
            "redacted_preview_status_enabled": True,
            "tower_gate_state_enabled": True,
            "owner_review_state_enabled": True,
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
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_enabled": False,
            "auto_confirmation_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "financing_decision_enabled": False,
            "legal_advice_enabled": False,
            "raw_document_verification_claimed": False,
            "auto_packet_approval_enabled": False,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp032",
            "safe_next_unlock": "GP033 can deepen packet review grouping without unlocking raw storage, external delivery, public proof, portals, export, auto-run, or execution.",
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
        "detail_summary": {
            "room_title": "Vault Packet Component Detail",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/packet-component-detail",
            "json_route": "/vault/packet-component-detail.json",
            "records_route": "/vault/packet-component-detail-records.json",
            "requirements_route": "/vault/packet-component-detail-requirements.json",
            "redacted_preview_route": "/vault/packet-component-detail-redacted-preview.json",
            "tower_gates_route": "/vault/packet-component-detail-tower-gates.json",
            "blockers_route": "/vault/packet-component-detail-blockers.json",
            "owner_queue_route": "/vault/packet-component-detail-owner-queue.json",
            "carry_forward_route": "/vault/packet-component-detail-carry-forward.json",
            "gp032_status_route": "/vault/gp032-status.json",
            "detail_record_count": len(detail_records),
            "requirement_meaning_count": requirement_meanings["requirement_meaning_count"],
            "redacted_preview_slot_count": redacted_preview_state["redacted_preview_slot_count"],
            "tower_gate_count": tower_gate_state["tower_gate_count"],
            "blocker_count": blocker_wall["blocker_count"],
            "owner_review_item_count": owner_review["owner_review_item_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "completed_count": 0,
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "detail_records": detail_records,
        "requirement_meanings": requirement_meanings,
        "redacted_preview_state": redacted_preview_state,
        "tower_gate_state": tower_gate_state,
        "blocker_wall": blocker_wall,
        "owner_review_state": owner_review,
        "carry_forward": carry_forward,
        "gp031_connection": {
            "gp031_pack_id": gp031["pack"]["id"],
            "gp031_ready": gp031["gp031_status"]["ready"],
            "gp031_safe_to_continue": gp031["gp031_status"]["safe_to_continue_to_gp032"],
            "gp031_vault_done": gp031["gp031_status"]["vault_done"],
            "gp031_section": gp031["pack"]["section"],
            "gp031_assembly_record_count": gp031["assembly_summary"]["assembly_record_count"],
            "gp031_component_row_count": gp031["assembly_summary"]["component_row_count"],
        },
        "gp032_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp031_assembly_connected": True,
            "packet_component_detail_ready": True,
            "safe_to_continue_to_gp033": True,
            "vault_done": False,
            "metadata_only_detail": True,
            "private_detail_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_disabled": True,
            "auto_confirmation_disabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp032",
            "next_pack": "VAULT_GP033_PACKET_REVIEW_GROUPING_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_detail_record(component: Dict[str, Any], assembly: Dict[str, Any], index: int) -> Dict[str, Any]:
    purpose = COMPONENT_PURPOSES[component["component_type"]]

    blocked_codes = set(component.get("blocked_codes", []))
    blocked_codes.update({
        "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY",
        "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_COMPLETION",
        "NO_AUTO_CONFIRMATION",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "NO_EXTERNAL_PACKET_DELIVERY",
        "NO_PACKET_EXPORT",
        "NO_FINANCING_DECISION",
        "NO_LEGAL_ADVICE",
        "NO_RAW_VERIFICATION_CLAIM",
        "CLOUDS_PARKED",
    })

    if component["component_type"] == "redacted_preview_slot":
        blocked_codes.update({
            "RAW_FILE_BODY_LOCKED",
            "DIRECT_UPLOAD_LOCKED",
            "UNREDACTED_EXPORT_LOCKED",
            "RAW_EXPORT_LOCKED",
            "PUBLIC_PACKET_PROOF_LOCKED",
        })

    if component["component_type"] == "tower_gate_status":
        blocked_codes.update({
            "TOWER_CLEARANCE_REQUIRED",
            "TOWER_STEP_UP_REQUIRED",
            "EXTERNAL_ACCESS_DENIED",
            "PORTAL_ACCESS_LOCKED",
        })

    return {
        "detail_id": f"VPD-{index:03d}",
        "component_id": component["component_id"],
        "assembly_id": component["assembly_id"],
        "packet_id": component["packet_id"],
        "lane": component["lane"],
        "component_type": component["component_type"],
        "component_label": component["label"],
        "packet_title": assembly["title"],
        "component_sequence": component["sequence"],
        "requirement_purpose": purpose["purpose"],
        "requirement_meaning": purpose["meaning"],
        "reference_type": purpose["reference_type"],
        "linked_reference_id": _linked_reference_id(component, assembly, purpose["reference_type"]),
        "linked_reference_label": _linked_reference_label(component, assembly),
        "detail_status": "OPEN_FOR_OWNER_REVIEW",
        "metadata_only": True,
        "private_detail_only": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "completed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "redacted_preview_state": _redacted_preview_state_for(component),
        "redacted_preview_only": component["component_type"] == "redacted_preview_slot",
        "raw_body_available": False,
        "raw_file_body_storage_enabled": False,
        "direct_upload_unlocked": False,
        "external_delivery_allowed": False,
        "external_access_allowed": False,
        "packet_export_allowed": False,
        "raw_export_allowed": False,
        "unredacted_export_allowed": False,
        "public_packet_proof_allowed": False,
        "portal_access_allowed": False,
        "tower_gate_observed": True,
        "tower_clearance_required": True,
        "tower_step_up_required": True,
        "tower_can_unlock_later": True,
        "vault_can_override_tower": False,
        "ready_for_owner_review": True,
        "ready_for_external_delivery": False,
        "ready_for_export": False,
        "safe_to_carry_to_gp033": True,
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Review {component['label']} for {assembly['title']} as private metadata only.",
    }


def _linked_reference_id(component: Dict[str, Any], assembly: Dict[str, Any], reference_type: str) -> str:
    return f"VREF-{reference_type.upper()}-{assembly['assembly_id']}-{component['component_id']}"


def _linked_reference_label(component: Dict[str, Any], assembly: Dict[str, Any]) -> str:
    return f"{assembly['title']} · {component['label']}"


def _redacted_preview_state_for(component: Dict[str, Any]) -> str:
    if component["component_type"] == "redacted_preview_slot":
        return "REDACTED_PREVIEW_SLOT_RESERVED_NO_RAW_BODY"
    return "NO_REDACTED_PREVIEW_REQUIRED_METADATA_ONLY"


def _build_requirement_meanings(detail_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "requirement_meaning_id": f"VRM-{record['detail_id'].replace('VPD-', '')}",
            "detail_id": record["detail_id"],
            "component_id": record["component_id"],
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "component_type": record["component_type"],
            "requirement_purpose": record["requirement_purpose"],
            "requirement_meaning": record["requirement_meaning"],
            "reference_type": record["reference_type"],
            "metadata_only": True,
            "raw_verification_claimed": False,
            "owner_review_required": True,
            "safe_to_carry_to_gp033": True,
        }
        for record in detail_records
    ]

    return {
        "requirement_meanings": items,
        "requirement_meaning_count": len(items),
        "raw_verification_claimed_count": 0,
        "metadata_only_count": len(items),
        "owner_review_required_count": len(items),
        "safe_to_continue_requirement_meanings": True,
    }


def _build_redacted_preview_state(detail_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "redacted_preview_id": f"VRP-{record['detail_id'].replace('VPD-', '')}",
            "detail_id": record["detail_id"],
            "component_id": record["component_id"],
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "component_type": record["component_type"],
            "redacted_preview_state": record["redacted_preview_state"],
            "redacted_preview_only": record["redacted_preview_only"],
            "raw_body_available": False,
            "raw_body_stored": False,
            "direct_upload_unlocked": False,
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "public_packet_proof_allowed": False,
            "metadata_only": True,
        }
        for record in detail_records
    ]

    return {
        "redacted_preview_items": items,
        "redacted_preview_count": len(items),
        "redacted_preview_slot_count": sum(1 for item in items if item["redacted_preview_only"]),
        "raw_body_available_count": 0,
        "raw_body_stored_count": 0,
        "direct_upload_unlocked_count": 0,
        "unredacted_export_allowed_count": 0,
        "raw_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_continue_redacted_preview": True,
    }


def _build_tower_gate_state(detail_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_gate_id": f"VTG-{record['detail_id'].replace('VPD-', '')}",
            "detail_id": record["detail_id"],
            "component_id": record["component_id"],
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "component_type": record["component_type"],
            "tower_gate_observed": True,
            "tower_clearance_required": True,
            "tower_step_up_required": True,
            "tower_owns_external_access": True,
            "tower_owns_export_locks": True,
            "tower_owns_portal_unlocks": True,
            "tower_owns_sensitive_visibility": True,
            "vault_can_override_tower": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "portal_access_allowed": False,
        }
        for record in detail_records
    ]

    return {
        "tower_gate_items": items,
        "tower_gate_count": len(items),
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "vault_override_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_gates_preserved": True,
    }


def _build_blocker_wall(detail_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for record in detail_records for code in record["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_detail_count": sum(1 for record in detail_records if code in record["blocked_codes"]),
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
        "raw_storage_allowed": False,
        "direct_upload_allowed": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "public_packet_proof_allowed": False,
        "portal_access_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only component detail. Do not display or store raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "PUBLIC_PACKET_PROOF_LOCKED": "Do not create public packet proof.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "TOWER_STEP_UP_REQUIRED": "Tower must own step-up before sensitive action.",
        "OWNER_REVIEW_REQUIRED": "Require owner review before any next step.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before closure.",
        "NO_AUTO_COMPLETION": "Do not auto-complete packet component detail.",
        "NO_AUTO_CONFIRMATION": "Do not auto-confirm owner actions.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault details components but does not execute actions.",
        "NO_EXTERNAL_PACKET_DELIVERY": "Do not deliver packets externally.",
        "NO_PACKET_EXPORT": "Do not export packets.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Keep controlled packet assembly private.",
        "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY": "Keep packet component detail private.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP032.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_review_state(detail_records: List[Dict[str, Any]], blocker_wall: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "owner_review_id": f"VPOR-{record['detail_id'].replace('VPD-', '')}",
            "detail_id": record["detail_id"],
            "component_id": record["component_id"],
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "component_type": record["component_type"],
            "packet_title": record["packet_title"],
            "component_label": record["component_label"],
            "review_status": "READY_FOR_OWNER_REVIEW_DELIVERY_BLOCKED",
            "owner_review_required": True,
            "owner_reviewed": False,
            "owner_confirmation_required": True,
            "owner_confirmed": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp033": True,
        }
        for record in detail_records
    ]

    return {
        "owner_review_items": items,
        "owner_review_item_count": len(items),
        "ready_for_owner_review_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "auto_completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "blocker_count": blocker_wall["blocker_count"],
        "safe_to_continue_owner_review": True,
        "next_owner_actions": [
            "Review packet component detail records.",
            "Use requirement purpose and requirement meaning to understand each component.",
            "Keep raw storage, direct upload, export, external delivery, public proof, and portals locked.",
            "Keep Tower-owned clearance and step-up gates intact.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP033 packet review grouping.",
        ],
    }


def _build_carry_forward(detail_records: List[Dict[str, Any]], owner_review: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VPD-CF-{record['detail_id'].replace('VPD-', '')}",
            "detail_id": record["detail_id"],
            "component_id": record["component_id"],
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "component_type": record["component_type"],
            "packet_title": record["packet_title"],
            "component_label": record["component_label"],
            "carry_forward_status": "READY_FOR_GP033_PACKET_REVIEW_GROUPING",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp033": True,
        }
        for record in detail_records
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp033_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_carry_to_gp033": True,
        "owner_review_item_count": owner_review["owner_review_item_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_packet_component_detail_payload())


def get_packet_component_detail_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "detail_truth": payload["detail_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "detail_summary": payload["detail_summary"],
        "gp031_connection": payload["gp031_connection"],
    }


def get_packet_component_detail_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "detail_records": payload["detail_records"],
        "detail_record_count": len(payload["detail_records"]),
    }


def get_packet_component_detail_requirements() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "requirement_meanings": payload["requirement_meanings"],
    }


def get_packet_component_detail_redacted_preview() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "redacted_preview_state": payload["redacted_preview_state"],
    }


def get_packet_component_detail_tower_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gate_state": payload["tower_gate_state"],
    }


def get_packet_component_detail_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_wall": payload["blocker_wall"],
    }


def get_packet_component_detail_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_packet_component_detail_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp032_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp032_status": payload["gp032_status"],
        "detail_truth": payload["detail_truth"],
        "detail_summary": payload["detail_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp031_connection": payload["gp031_connection"],
    }


def render_packet_component_detail_page() -> str:
    payload = clone_payload()
    summary = payload["detail_summary"]
    truth = payload["detail_truth"]
    detail_records = payload["detail_records"]
    owner = payload["owner_review_state"]

    record_cards = "\n".join(_render_detail_card(record) for record in detail_records[:12])
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Packet Component Detail · GP032</title>
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

      .card-top {{
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
        <div class="eyebrow">Archive Vault · Giant Pack 032</div>
        <h1>Packet Component Detail</h1>
        <p class="hero-copy">
          GP032 gives every controlled packet component a private detail record: purpose, meaning,
          linked reference, redacted-preview state, Tower gate state, blockers, owner review, and carry-forward.
          This is metadata-only review. No raw storage, direct upload, external delivery, export, public proof, or portals.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['detail_record_count']}</strong>
            <span>detail records</span>
          </div>
          <div class="metric">
            <strong>{summary['requirement_meaning_count']}</strong>
            <span>requirement meanings</span>
          </div>
          <div class="metric">
            <strong>{summary['redacted_preview_slot_count']}</strong>
            <span>redacted slots</span>
          </div>
          <div class="metric">
            <strong>{str(truth['packet_export_enabled']).lower()}</strong>
            <span>packet export</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Component detail ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">External delivery locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Component Detail Records</h2>
      <p>
        Each component gets purpose, meaning, linked reference, redacted-preview state, Tower gate, blockers, and carry-forward.
      </p>
      <div class="grid">
        {record_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Owner Actions</h2>
        <p>GP032 prepares GP033 packet review grouping.</p>
        <ul>
          {actions}
        </ul>
      </div>
      <div>
        <h2>GP032 JSON Endpoints</h2>
        <p>
          <code>{escape(summary['json_route'])}</code>
          <code>{escape(summary['records_route'])}</code>
          <code>{escape(summary['requirements_route'])}</code>
          <code>{escape(summary['redacted_preview_route'])}</code>
          <code>{escape(summary['tower_gates_route'])}</code>
          <code>{escape(summary['blockers_route'])}</code>
          <code>{escape(summary['owner_queue_route'])}</code>
          <code>{escape(summary['carry_forward_route'])}</code>
          <code>{escape(summary['gp032_status_route'])}</code>
        </p>
      </div>
    </section>

    <section class="section">
      <h2>Detail Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Raw storage:
        <code>{str(truth['raw_file_body_storage_enabled']).lower()}</code>.
        External delivery:
        <code>{str(truth['external_packet_delivery_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_detail_card(record: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record['component_label'])}</div>
            <div class="meta">
              Detail: <code>{escape(record['detail_id'])}</code><br>
              Assembly: <code>{escape(record['assembly_id'])}</code><br>
              Packet: <code>{escape(record['packet_id'])}</code><br>
              Type: {escape(record['component_type'])}<br>
              Export allowed: <code>{str(record['packet_export_allowed']).lower()}</code>
            </div>
          </div>
          <span class="pill warn">{escape(record['detail_status'])}</span>
        </div>
      </article>
    """
