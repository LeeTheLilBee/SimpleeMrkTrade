"""
VAULT GIANT PACK 035 — Packet Review Decision Prep

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP034 packet review priority by preparing private owner
decision surfaces.

Purpose:
- Build decision prep records from packet priority records.
- Define safe owner decision options.
- Define unsafe/locked decision paths.
- Label readiness state.
- Build owner decision prompts.
- Build Tower gate requirements.
- Build blocker-based decision limits.
- Sort next decisions.
- Carry decision prep forward to GP036.

Important truth:
- GP035 is not a raw file storage provider.
- GP035 does not unlock direct upload.
- GP035 does not create external packet delivery.
- GP035 does not export raw or unredacted packet bodies.
- GP035 does not create public proof.
- GP035 does not open seller/broker/trustee/external portals.
- GP035 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Packet review decision prep means private metadata preparation for owner review only.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.packet_review_priority_service import get_packet_review_priority_payload


PACK_ID = "VAULT_GP035"
PACK_NAME = "Packet Review Decision Prep"
SCHEMA_VERSION = "vault.packet_review_decision_prep.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

SAFE_DECISION_OPTIONS = [
    {
        "option_code": "OWNER_REVIEW_NOW",
        "label": "Review now",
        "description": "Owner can review the packet priority bundle privately.",
        "requires_tower_clearance": False,
        "requires_tower_step_up": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "executes_action": False,
    },
    {
        "option_code": "HOLD_FOR_TOWER_GATE",
        "label": "Hold for Tower gate",
        "description": "Hold the packet until Tower clearance or step-up is available.",
        "requires_tower_clearance": True,
        "requires_tower_step_up": True,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "executes_action": False,
    },
    {
        "option_code": "HOLD_FOR_BLOCKER_RESOLUTION",
        "label": "Hold for blocker resolution",
        "description": "Hold the packet because restricted paths remain locked.",
        "requires_tower_clearance": False,
        "requires_tower_step_up": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "executes_action": False,
    },
    {
        "option_code": "CARRY_FORWARD_TO_GP036",
        "label": "Carry forward",
        "description": "Carry safe decision prep state into GP036.",
        "requires_tower_clearance": False,
        "requires_tower_step_up": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "executes_action": False,
    },
]

UNSAFE_DECISION_OPTIONS = [
    "APPROVE_EXTERNAL_DELIVERY",
    "EXPORT_PACKET",
    "EXPORT_UNREDACTED_PACKET",
    "EXPORT_RAW_PACKET",
    "UNLOCK_DIRECT_UPLOAD",
    "UNLOCK_RAW_FILE_BODY_STORAGE",
    "OPEN_EXTERNAL_PORTAL",
    "CREATE_PUBLIC_PROOF",
    "CREATE_PUBLIC_PACKET_PROOF",
    "AUTO_COMPLETE_PACKET",
    "AUTO_CONFIRM_OWNER_DECISION",
    "EXECUTE_ACTION_FROM_VAULT",
    "MAKE_FINANCING_DECISION",
    "GIVE_LEGAL_ADVICE",
    "CLAIM_RAW_DOCUMENT_VERIFICATION",
    "CONTINUE_CLOUDS_FROM_VAULT",
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault prepares decisions but does not execute actions.",
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
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_packet_review_decision_prep_payload() -> Dict[str, Any]:
    gp034 = get_packet_review_priority_payload()

    priority_records = gp034["priority_records"]
    decision_records = [
        _build_decision_record(record)
        for record in priority_records
    ]

    decision_options = _build_decision_options(decision_records)
    readiness_labels = _build_readiness_labels(decision_records)
    owner_prompts = _build_owner_prompts(decision_records)
    tower_requirements = _build_tower_requirements(decision_records)
    blocker_limits = _build_blocker_limits(decision_records)
    decision_paths = _build_decision_paths(decision_records)
    next_decisions = _build_next_decisions(decision_records, blocker_limits, tower_requirements)
    carry_forward = _build_carry_forward(decision_records, next_decisions)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "packet_review_decision_prep",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "decision_truth": {
            "packet_review_decision_prep_enabled": True,
            "metadata_only": True,
            "private_decision_prep_only": True,
            "decision_prep_means_owner_review_not_approval": True,
            "safe_decision_options_enabled": True,
            "unsafe_decision_paths_locked": True,
            "readiness_labels_enabled": True,
            "owner_decision_prompts_enabled": True,
            "tower_gate_requirements_enabled": True,
            "blocker_based_limits_enabled": True,
            "next_decision_sorting_enabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp035",
            "safe_next_unlock": "GP036 can deepen owner decision review without unlocking raw storage, external delivery, public proof, portals, export, auto-run, or execution.",
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
        "decision_summary": {
            "room_title": "Vault Packet Review Decision Prep",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/packet-review-decision-prep",
            "json_route": "/vault/packet-review-decision-prep.json",
            "records_route": "/vault/packet-review-decision-prep-records.json",
            "options_route": "/vault/packet-review-decision-prep-options.json",
            "readiness_route": "/vault/packet-review-decision-prep-readiness.json",
            "prompts_route": "/vault/packet-review-decision-prep-prompts.json",
            "tower_requirements_route": "/vault/packet-review-decision-prep-tower-requirements.json",
            "blocker_limits_route": "/vault/packet-review-decision-prep-blocker-limits.json",
            "paths_route": "/vault/packet-review-decision-prep-paths.json",
            "next_decisions_route": "/vault/packet-review-decision-prep-next-decisions.json",
            "carry_forward_route": "/vault/packet-review-decision-prep-carry-forward.json",
            "gp035_status_route": "/vault/gp035-status.json",
            "decision_record_count": len(decision_records),
            "safe_option_count": decision_options["safe_option_count"],
            "unsafe_option_count": decision_options["unsafe_option_count"],
            "readiness_label_count": readiness_labels["readiness_label_count"],
            "owner_prompt_count": owner_prompts["owner_prompt_count"],
            "tower_requirement_count": tower_requirements["tower_requirement_count"],
            "blocker_limit_count": blocker_limits["blocker_limit_count"],
            "decision_path_count": decision_paths["decision_path_count"],
            "next_decision_count": next_decisions["next_decision_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "completed_count": 0,
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "decision_records": decision_records,
        "decision_options": decision_options,
        "readiness_labels": readiness_labels,
        "owner_prompts": owner_prompts,
        "tower_requirements": tower_requirements,
        "blocker_limits": blocker_limits,
        "decision_paths": decision_paths,
        "next_decisions": next_decisions,
        "carry_forward": carry_forward,
        "gp034_connection": {
            "gp034_pack_id": gp034["pack"]["id"],
            "gp034_ready": gp034["gp034_status"]["ready"],
            "gp034_safe_to_continue": gp034["gp034_status"]["safe_to_continue_to_gp035"],
            "gp034_vault_done": gp034["gp034_status"]["vault_done"],
            "gp034_section": gp034["pack"]["section"],
            "gp034_priority_record_count": gp034["priority_summary"]["priority_record_count"],
            "gp034_next_action_count": gp034["priority_summary"]["next_action_count"],
            "gp034_priority_reason_count": gp034["priority_summary"]["priority_reason_count"],
        },
        "gp035_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp034_priority_connected": True,
            "packet_review_decision_prep_ready": True,
            "safe_to_continue_to_gp036": True,
            "vault_done": False,
            "metadata_only_decision_prep": True,
            "private_decision_prep_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp035",
            "next_pack": "VAULT_GP036_OWNER_DECISION_REVIEW_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_decision_record(priority: Dict[str, Any]) -> Dict[str, Any]:
    active_codes = sorted(set(priority["blocked_codes"]) | {"PACKET_REVIEW_DECISION_PREP_PRIVATE_ONLY"})

    return {
        "decision_prep_id": f"VDR-{priority['priority_rank']:03d}",
        "priority_id": priority["priority_id"],
        "review_group_id": priority["review_group_id"],
        "packet_id": priority["packet_id"],
        "assembly_id": priority["assembly_id"],
        "lane": priority["lane"],
        "packet_title": priority["packet_title"],
        "priority_rank": priority["priority_rank"],
        "priority_band": priority["priority_band"],
        "blocker_severity": priority["blocker_severity"],
        "tower_gate_urgency": priority["tower_gate_urgency"],
        "readiness_label": _readiness_label_for(priority),
        "decision_prep_status": "READY_FOR_OWNER_DECISION_PREP_NO_EXECUTION",
        "safe_decision_options": [option["option_code"] for option in SAFE_DECISION_OPTIONS],
        "unsafe_decision_options": list(UNSAFE_DECISION_OPTIONS),
        "recommended_safe_option": _recommended_safe_option(priority),
        "owner_prompt": _owner_prompt_for(priority),
        "metadata_only": True,
        "private_decision_prep_only": True,
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
        "detail_count": priority["detail_count"],
        "review_lane_count": priority["review_lane_count"],
        "redacted_preview_slot_count": priority["redacted_preview_slot_count"],
        "tower_gate_count": priority["tower_gate_count"],
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
        "safe_to_carry_to_gp036": True,
        "owner_note": f"Prepare decision for {priority['packet_title']} without approving, exporting, delivering, or executing.",
    }


def _readiness_label_for(priority: Dict[str, Any]) -> str:
    if priority["priority_rank"] <= 2:
        return "OWNER_FOCUS_READY_CRITICAL_BLOCKERS_TOWER_LOCKED"
    if priority["priority_rank"] == 3:
        return "OWNER_FOCUS_READY_AUTHORITY_BLOCKERS_TOWER_LOCKED"
    if priority["blocker_severity"] == "high":
        return "PRIVATE_REVIEW_READY_HIGH_BLOCKERS"
    return "PRIVATE_REVIEW_READY_MEDIUM_BLOCKERS"


def _recommended_safe_option(priority: Dict[str, Any]) -> str:
    if priority["tower_gate_urgency"] == "high":
        return "HOLD_FOR_TOWER_GATE"
    if priority["blocker_severity"] in {"critical", "high"}:
        return "HOLD_FOR_BLOCKER_RESOLUTION"
    return "OWNER_REVIEW_NOW"


def _owner_prompt_for(priority: Dict[str, Any]) -> str:
    return (
        f"Review {priority['packet_title']} privately. "
        f"Priority rank {priority['priority_rank']} is based on {priority['priority_band']}, "
        f"blocker severity {priority['blocker_severity']}, and Tower urgency {priority['tower_gate_urgency']}. "
        "Do not export, deliver externally, unlock raw files, open portals, auto-confirm, or execute."
    )


def _build_decision_options(decision_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    safe_items = []
    unsafe_items = []

    for record in decision_records:
        for option in SAFE_DECISION_OPTIONS:
            safe_items.append(
                {
                    "decision_option_id": f"VDO-{record['priority_rank']:03d}-{option['option_code']}",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "packet_title": record["packet_title"],
                    "priority_rank": record["priority_rank"],
                    "option_code": option["option_code"],
                    "label": option["label"],
                    "description": option["description"],
                    "requires_tower_clearance": option["requires_tower_clearance"],
                    "requires_tower_step_up": option["requires_tower_step_up"],
                    "safe_option": True,
                    "metadata_only": True,
                    "external_delivery_allowed": option["external_delivery_allowed"],
                    "packet_export_allowed": option["packet_export_allowed"],
                    "executes_action": option["executes_action"],
                    "owner_review_required": True,
                    "safe_to_carry_to_gp036": True,
                }
            )

        for option_code in UNSAFE_DECISION_OPTIONS:
            unsafe_items.append(
                {
                    "unsafe_option_id": f"VUDO-{record['priority_rank']:03d}-{option_code}",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "packet_title": record["packet_title"],
                    "priority_rank": record["priority_rank"],
                    "option_code": option_code,
                    "safe_option": False,
                    "locked": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "owner_review_required": True,
                    "safe_to_override_inside_vault": False,
                }
            )

    return {
        "safe_decision_options": safe_items,
        "unsafe_decision_options": unsafe_items,
        "safe_option_count": len(safe_items),
        "unsafe_option_count": len(unsafe_items),
        "decision_record_count": len(decision_records),
        "safe_option_per_packet_count": len(SAFE_DECISION_OPTIONS),
        "unsafe_option_per_packet_count": len(UNSAFE_DECISION_OPTIONS),
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "executes_action_count": 0,
        "unsafe_locked_count": len(unsafe_items),
        "safe_to_continue_decision_options": True,
    }


def _build_readiness_labels(decision_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "readiness_id": f"VDRL-{record['priority_rank']:03d}",
            "decision_prep_id": record["decision_prep_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "readiness_label": record["readiness_label"],
            "recommended_safe_option": record["recommended_safe_option"],
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
        for record in decision_records
    ]

    return {
        "readiness_items": items,
        "readiness_label_count": len(items),
        "owner_review_required_count": len(items),
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_readiness_labels": True,
    }


def _build_owner_prompts(decision_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "owner_prompt_id": f"VDP-{record['priority_rank']:03d}",
            "decision_prep_id": record["decision_prep_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "prompt": record["owner_prompt"],
            "recommended_safe_option": record["recommended_safe_option"],
            "prompt_status": "READY_FOR_OWNER_REVIEW_NO_AUTO_CONFIRM",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "auto_confirm_allowed": False,
            "executes_action": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
        for record in decision_records
    ]

    return {
        "owner_prompt_items": items,
        "owner_prompt_count": len(items),
        "auto_confirm_allowed_count": 0,
        "executes_action_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_owner_prompts": True,
    }


def _build_tower_requirements(decision_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_requirement_id": f"VDTR-{record['priority_rank']:03d}",
            "decision_prep_id": record["decision_prep_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "tower_gate_urgency": record["tower_gate_urgency"],
            "tower_clearance_required": True,
            "tower_step_up_required": True,
            "tower_export_lock_required": True,
            "tower_external_access_required": True,
            "tower_portal_unlock_required": True,
            "tower_sensitive_visibility_required": True,
            "vault_can_override_tower": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "portal_access_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
        for record in decision_records
    ]

    return {
        "tower_requirement_items": items,
        "tower_requirement_count": len(items),
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "tower_export_lock_required_count": len(items),
        "vault_override_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_requirements_preserved": True,
    }


def _build_blocker_limits(decision_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "blocker_limit_id": f"VDBL-{record['priority_rank']:03d}",
            "decision_prep_id": record["decision_prep_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "blocker_severity": record["blocker_severity"],
            "blocked_code_count": record["blocked_code_count"],
            "blocked_codes": record["blocked_codes"],
            "decision_limit_status": "LIMITED_TO_PRIVATE_OWNER_REVIEW",
            "all_restricted_paths_locked": True,
            "safe_to_override_inside_vault": False,
            "raw_storage_allowed": False,
            "direct_upload_allowed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "portal_access_allowed": False,
            "execution_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
        for record in decision_records
    ]

    active_codes = sorted({code for item in items for code in item["blocked_codes"]})

    return {
        "blocker_limit_items": items,
        "active_block_codes": active_codes,
        "blocker_limit_count": len(items),
        "active_block_code_count": len(active_codes),
        "critical_limit_count": sum(1 for item in items if item["blocker_severity"] == "critical"),
        "high_limit_count": sum(1 for item in items if item["blocker_severity"] == "high"),
        "medium_limit_count": sum(1 for item in items if item["blocker_severity"] == "medium"),
        "all_restricted_paths_locked": True,
        "safe_to_override_inside_vault_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "execution_allowed_count": 0,
        "safe_to_continue_blocker_limits": True,
    }


def _build_decision_paths(decision_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    safe_paths = []
    unsafe_paths = []

    for record in decision_records:
        safe_paths.extend(
            [
                {
                    "path_id": f"VDSP-{record['priority_rank']:03d}-REVIEW",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "path_code": "PRIVATE_OWNER_REVIEW",
                    "path_label": "Private owner review",
                    "safe_path": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_carry_to_gp036": True,
                },
                {
                    "path_id": f"VDSP-{record['priority_rank']:03d}-HOLD",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "path_code": "HOLD_LOCKED_PATHS",
                    "path_label": "Hold locked paths",
                    "safe_path": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_carry_to_gp036": True,
                },
                {
                    "path_id": f"VDSP-{record['priority_rank']:03d}-CARRY",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "path_code": "CARRY_FORWARD_TO_GP036",
                    "path_label": "Carry forward to GP036",
                    "safe_path": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_carry_to_gp036": True,
                },
            ]
        )

        unsafe_paths.extend(
            [
                {
                    "path_id": f"VDUP-{record['priority_rank']:03d}-EXPORT",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "path_code": "EXPORT_OR_DELIVER",
                    "path_label": "Export or deliver externally",
                    "safe_path": False,
                    "locked": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_override_inside_vault": False,
                },
                {
                    "path_id": f"VDUP-{record['priority_rank']:03d}-RAW",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "path_code": "UNLOCK_RAW_OR_DIRECT_UPLOAD",
                    "path_label": "Unlock raw storage or direct upload",
                    "safe_path": False,
                    "locked": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_override_inside_vault": False,
                },
                {
                    "path_id": f"VDUP-{record['priority_rank']:03d}-EXECUTE",
                    "decision_prep_id": record["decision_prep_id"],
                    "packet_id": record["packet_id"],
                    "path_code": "EXECUTE_OR_APPROVE",
                    "path_label": "Execute, approve, finance, advise, or verify raw documents",
                    "safe_path": False,
                    "locked": True,
                    "metadata_only": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "executes_action": False,
                    "safe_to_override_inside_vault": False,
                },
            ]
        )

    return {
        "safe_decision_paths": safe_paths,
        "unsafe_decision_paths": unsafe_paths,
        "safe_path_count": len(safe_paths),
        "unsafe_path_count": len(unsafe_paths),
        "decision_path_count": len(safe_paths) + len(unsafe_paths),
        "locked_unsafe_path_count": len(unsafe_paths),
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "executes_action_count": 0,
        "safe_to_continue_decision_paths": True,
    }


def _build_next_decisions(
    decision_records: List[Dict[str, Any]],
    blocker_limits: Dict[str, Any],
    tower_requirements: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "next_decision_id": f"VDN-{record['priority_rank']:03d}",
            "decision_prep_id": record["decision_prep_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "priority_band": record["priority_band"],
            "readiness_label": record["readiness_label"],
            "recommended_safe_option": record["recommended_safe_option"],
            "blocker_severity": record["blocker_severity"],
            "tower_gate_urgency": record["tower_gate_urgency"],
            "next_decision_status": "READY_FOR_OWNER_DECISION_REVIEW_NO_EXECUTION",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "decision_selected": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "approval_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
        for record in decision_records
    ]

    items.append(
        {
            "next_decision_id": "VDN-998",
            "decision_prep_id": "BOUNDARY-LOCKS",
            "packet_id": "ALL_PACKETS",
            "packet_title": "All Packet Decision Boundaries",
            "priority_rank": 998,
            "priority_band": "BOUNDARY",
            "readiness_label": "BOUNDARIES_LOCKED",
            "recommended_safe_option": "HOLD_FOR_BLOCKER_RESOLUTION",
            "blocker_severity": "critical",
            "tower_gate_urgency": "high",
            "next_decision_status": "BOUNDARY_LOCKED_NO_OVERRIDE",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "decision_selected": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "approval_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
    )

    items.append(
        {
            "next_decision_id": "VDN-999",
            "decision_prep_id": "NEXT-GP036",
            "packet_id": "NEXT_VAULT_PACK",
            "packet_title": "GP036 Owner Decision Review",
            "priority_rank": 999,
            "priority_band": "NEXT_BUILD",
            "readiness_label": "READY_FOR_GP036",
            "recommended_safe_option": "CARRY_FORWARD_TO_GP036",
            "blocker_severity": "medium",
            "tower_gate_urgency": "medium",
            "next_decision_status": "NEXT_BUILD_READY",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "decision_selected": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "approval_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
    )

    sorted_items = sorted(items, key=lambda item: (item["priority_rank"], item["next_decision_id"]))

    return {
        "next_decision_items": sorted_items,
        "next_decision_count": len(sorted_items),
        "packet_decision_count": len(decision_records),
        "boundary_decision_count": 1,
        "next_build_decision_count": 1,
        "owner_review_required_count": len(sorted_items),
        "decision_selected_count": 0,
        "completed_count": 0,
        "owner_confirmed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "blocker_limit_count": blocker_limits["blocker_limit_count"],
        "tower_requirement_count": tower_requirements["tower_requirement_count"],
        "safe_to_continue_next_decisions": True,
        "next_owner_actions": [
            "Review packet decision prep in priority order.",
            "Use safe decision options only: review now, hold for Tower gate, hold for blockers, or carry forward.",
            "Treat export, external delivery, raw unlock, public proof, portals, auto-confirmation, and execution as locked unsafe paths.",
            "Keep Tower-owned clearance and step-up requirements intact.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP036 owner decision review.",
        ],
    }


def _build_carry_forward(
    decision_records: List[Dict[str, Any]],
    next_decisions: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VDR-CF-{record['priority_rank']:03d}",
            "decision_prep_id": record["decision_prep_id"],
            "priority_id": record["priority_id"],
            "review_group_id": record["review_group_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "readiness_label": record["readiness_label"],
            "recommended_safe_option": record["recommended_safe_option"],
            "carry_forward_status": "READY_FOR_GP036_OWNER_DECISION_REVIEW",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "decision_selected": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp036": True,
        }
        for record in decision_records
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp036_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "decision_selected_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_carry_to_gp036": True,
        "next_decision_count": next_decisions["next_decision_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_packet_review_decision_prep_payload())


def get_packet_review_decision_prep_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_truth": payload["decision_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "decision_summary": payload["decision_summary"],
        "gp034_connection": payload["gp034_connection"],
    }


def get_packet_review_decision_prep_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_records": payload["decision_records"],
        "decision_record_count": len(payload["decision_records"]),
    }


def get_packet_review_decision_prep_options() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_options": payload["decision_options"],
    }


def get_packet_review_decision_prep_readiness() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "readiness_labels": payload["readiness_labels"],
    }


def get_packet_review_decision_prep_prompts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_prompts": payload["owner_prompts"],
    }


def get_packet_review_decision_prep_tower_requirements() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_requirements": payload["tower_requirements"],
    }


def get_packet_review_decision_prep_blocker_limits() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_limits": payload["blocker_limits"],
    }


def get_packet_review_decision_prep_paths() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_paths": payload["decision_paths"],
    }


def get_packet_review_decision_prep_next_decisions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_decisions": payload["next_decisions"],
    }


def get_packet_review_decision_prep_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp035_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp035_status": payload["gp035_status"],
        "decision_truth": payload["decision_truth"],
        "decision_summary": payload["decision_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp034_connection": payload["gp034_connection"],
    }


def render_packet_review_decision_prep_page() -> str:
    payload = clone_payload()
    summary = payload["decision_summary"]
    truth = payload["decision_truth"]
    records = payload["decision_records"]
    next_decisions = payload["next_decisions"]

    decision_cards = "\n".join(_render_decision_card(record) for record in records)
    next_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['packet_title'])}</strong>
            <span>{escape(item['next_decision_status'])} · option: {escape(item['recommended_safe_option'])}</span>
          </div>
          <div class="pill {'danger' if item['priority_rank'] <= 3 or item['priority_rank'] == 998 else 'warn'}">Rank {item['priority_rank']}</div>
        </div>
        """
        for item in next_decisions["next_decision_items"][:10]
    )

    owner_actions = "\n".join(f"<li>{escape(action)}</li>" for action in next_decisions["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Packet Review Decision Prep · GP035</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 035</div>
        <h1>Packet Review Decision Prep</h1>
        <p class="hero-copy">
          GP035 turns packet review priority into decision prep. It creates safe decision options,
          readiness labels, owner prompts, Tower gate requirements, blocker-based limits, safe/unsafe
          decision paths, sorted next decisions, and carry-forward into GP036. This stays metadata-only and private.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['decision_record_count']}</strong>
            <span>decision records</span>
          </div>
          <div class="metric">
            <strong>{summary['safe_option_count']}</strong>
            <span>safe options</span>
          </div>
          <div class="metric">
            <strong>{summary['unsafe_option_count']}</strong>
            <span>locked unsafe options</span>
          </div>
          <div class="metric">
            <strong>{str(truth['external_packet_delivery_enabled']).lower()}</strong>
            <span>external delivery</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Decision prep ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner decision review</span>
          <span class="pill danger">Unsafe paths locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Decision Prep Records</h2>
      <p>
        Each packet priority record now has decision prep, readiness, prompts, safe options, and locked unsafe paths.
      </p>
      <div class="grid">
        {decision_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Sorted Next Decisions</h2>
        <p>Owner decisions are sorted by packet priority while locked boundaries stay visible.</p>
        <div>
          {next_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP035 prepares GP036 owner decision review.</p>
        <ul>
          {owner_actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP035 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['records_route'])}</code>
        <code>{escape(summary['options_route'])}</code>
        <code>{escape(summary['readiness_route'])}</code>
        <code>{escape(summary['prompts_route'])}</code>
        <code>{escape(summary['tower_requirements_route'])}</code>
        <code>{escape(summary['blocker_limits_route'])}</code>
        <code>{escape(summary['paths_route'])}</code>
        <code>{escape(summary['next_decisions_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp035_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Decision Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Approval enabled:
        <code>{str(truth['auto_packet_approval_enabled']).lower()}</code>.
        Execution:
        <code>{str(truth['execution_engine_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_decision_card(record: Dict[str, Any]) -> str:
    chip_class = "danger" if record["priority_rank"] <= 3 else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record['packet_title'])}</div>
            <div class="meta">
              Decision: <code>{escape(record['decision_prep_id'])}</code><br>
              Rank: <code>{record['priority_rank']}</code><br>
              Readiness: <code>{escape(record['readiness_label'])}</code><br>
              Recommended: <code>{escape(record['recommended_safe_option'])}</code><br>
              Export allowed: <code>{str(record['packet_export_allowed']).lower()}</code>
            </div>
          </div>
          <span class="pill {chip_class}">Rank {record['priority_rank']}</span>
        </div>
      </article>
    """
