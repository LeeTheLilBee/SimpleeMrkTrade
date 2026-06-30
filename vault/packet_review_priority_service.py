"""
VAULT GIANT PACK 034 — Packet Review Priority

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP033 packet review grouping by adding priority logic.

Purpose:
- Rank packet review groups.
- Add priority reason codes.
- Build owner focus order.
- Build blocker severity.
- Build Tower-gate urgency.
- Sort next actions into GP035.
- Carry priority state forward.

Important truth:
- GP034 is not a raw file storage provider.
- GP034 does not unlock direct upload.
- GP034 does not create external packet delivery.
- GP034 does not export raw or unredacted packet bodies.
- GP034 does not create public proof.
- GP034 does not open seller/broker/trustee/external portals.
- GP034 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Packet review priority means private metadata prioritization for owner review only.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.packet_review_grouping_service import get_packet_review_grouping_payload


PACK_ID = "VAULT_GP034"
PACK_NAME = "Packet Review Priority"
SCHEMA_VERSION = "vault.packet_review_priority.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

PACKET_PRIORITY_RULES = {
    "ATM_ROUTE_ACQUISITION_PACKET": {
        "rank": 1,
        "priority_band": "P1_OWNER_FOCUS",
        "reason_codes": [
            "ATM_ROUTE_ACQUISITION_FIRST",
            "CAPITAL_DEPLOYMENT_SEQUENCE",
            "TOWER_CLEARANCE_REQUIRED",
            "EXTERNAL_DELIVERY_BLOCKED",
        ],
        "owner_focus_reason": "ATM route acquisition packet stays first because it supports the next capital deployment path.",
        "blocker_severity": "critical",
        "tower_gate_urgency": "high",
    },
    "APARTMENT_LENDER_DUE_DILIGENCE_PACKET": {
        "rank": 2,
        "priority_band": "P1_OWNER_FOCUS",
        "reason_codes": [
            "APARTMENT_LENDER_PACKET_SECOND",
            "DUE_DILIGENCE_SEQUENCE",
            "TOWER_CLEARANCE_REQUIRED",
            "EXTERNAL_DELIVERY_BLOCKED",
        ],
        "owner_focus_reason": "Apartment lender/due diligence packet stays second because it supports property acquisition readiness.",
        "blocker_severity": "critical",
        "tower_gate_urgency": "high",
    },
    "TRUST_ENTITY_AUTHORITY_PACKET": {
        "rank": 3,
        "priority_band": "P1_OWNER_FOCUS",
        "reason_codes": [
            "TRUST_ENTITY_AUTHORITY_PACKET_THIRD",
            "AUTHORITY_CHAIN_REQUIRED",
            "TOWER_CLEARANCE_REQUIRED",
            "PORTAL_ACCESS_LOCKED",
        ],
        "owner_focus_reason": "Trust/entity authority packet stays third because ownership and authority proof must stay clean.",
        "blocker_severity": "high",
        "tower_gate_urgency": "high",
    },
    "OB_MANUAL_LIVE_PROOF_PACKET": {
        "rank": 4,
        "priority_band": "P2_PRIVATE_PROOF",
        "reason_codes": [
            "OB_MANUAL_LIVE_PRIVATE_PROOF",
            "NO_PUBLIC_PROOF",
            "TOWER_CLEARANCE_REQUIRED",
            "EXTERNAL_DELIVERY_BLOCKED",
        ],
        "owner_focus_reason": "OB Manual Live proof packet stays private and prioritized after acquisition/authority packets.",
        "blocker_severity": "high",
        "tower_gate_urgency": "medium",
    },
    "SOULAANA_ARTIST_IP_PACKET": {
        "rank": 5,
        "priority_band": "P2_PRIVATE_PROOF",
        "reason_codes": [
            "SOULAANA_ARTIST_IP_BOUNDARY",
            "NO_AI_CHARACTER_ART",
            "TOWER_CLEARANCE_REQUIRED",
            "PUBLIC_PACKET_PROOF_LOCKED",
        ],
        "owner_focus_reason": "Soulaana artist/IP packet stays protected with art and IP boundaries locked.",
        "blocker_severity": "high",
        "tower_gate_urgency": "medium",
    },
    "PRIVATE_BETA_ONBOARDING_PACKET": {
        "rank": 6,
        "priority_band": "P3_BETA_OPS",
        "reason_codes": [
            "PRIVATE_BETA_ONBOARDING",
            "PRIVATE_ACCESS_ONLY",
            "TOWER_CLEARANCE_REQUIRED",
            "PORTAL_ACCESS_LOCKED",
        ],
        "owner_focus_reason": "Private beta onboarding packet stays below acquisition and proof packets.",
        "blocker_severity": "medium",
        "tower_gate_urgency": "medium",
    },
    "OWNER_ACTION_RECEIPT_PACKET": {
        "rank": 7,
        "priority_band": "P3_BETA_OPS",
        "reason_codes": [
            "OWNER_ACTION_RECEIPT_CONTEXT",
            "RECEIPT_CHAIN_REVIEWED",
            "NO_AUTO_COMPLETION",
            "NO_AUTO_CONFIRMATION",
        ],
        "owner_focus_reason": "Owner action receipt packet carries supporting review state into the next priority board.",
        "blocker_severity": "medium",
        "tower_gate_urgency": "medium",
    },
}

BLOCKER_SEVERITY_ORDER = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
}

TOWER_URGENCY_ORDER = {
    "high": 1,
    "medium": 2,
    "low": 3,
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault prioritizes packet review but does not execute actions.",
    "NO_EXTERNAL_PACKET_DELIVERY": "External packet delivery is disabled.",
    "NO_PACKET_EXPORT": "Packet export is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Controlled packet assembly is private only.",
    "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY": "Packet component detail is private only.",
    "PACKET_REVIEW_GROUPING_PRIVATE_ONLY": "Packet review grouping is private only.",
    "PACKET_REVIEW_PRIORITY_PRIVATE_ONLY": "Packet review priority is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_packet_review_priority_payload() -> Dict[str, Any]:
    gp033 = get_packet_review_grouping_payload()

    review_groups = gp033["review_groups"]

    priority_records = [
        _build_priority_record(group)
        for group in review_groups
    ]

    priority_records = sorted(
        priority_records,
        key=lambda record: (
            record["priority_rank"],
            BLOCKER_SEVERITY_ORDER[record["blocker_severity"]],
            TOWER_URGENCY_ORDER[record["tower_gate_urgency"]],
            record["packet_id"],
        ),
    )

    priority_reasons = _build_priority_reasons(priority_records)
    owner_focus_order = _build_owner_focus_order(priority_records)
    blocker_severity = _build_blocker_severity(priority_records)
    tower_urgency = _build_tower_urgency(priority_records)
    next_actions = _build_next_actions(priority_records, blocker_severity, tower_urgency)
    carry_forward = _build_carry_forward(priority_records, next_actions)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "packet_review_priority",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "priority_truth": {
            "packet_review_priority_enabled": True,
            "metadata_only": True,
            "private_priority_only": True,
            "priority_means_owner_focus_not_delivery": True,
            "priority_ranking_enabled": True,
            "reason_codes_enabled": True,
            "owner_focus_order_enabled": True,
            "blocker_severity_enabled": True,
            "tower_gate_urgency_enabled": True,
            "next_action_sorting_enabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp034",
            "safe_next_unlock": "GP035 can deepen packet review decision prep without unlocking raw storage, external delivery, public proof, portals, export, auto-run, or execution.",
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
        "priority_summary": {
            "room_title": "Vault Packet Review Priority",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/packet-review-priority",
            "json_route": "/vault/packet-review-priority.json",
            "records_route": "/vault/packet-review-priority-records.json",
            "reasons_route": "/vault/packet-review-priority-reasons.json",
            "owner_focus_route": "/vault/packet-review-priority-owner-focus.json",
            "blocker_severity_route": "/vault/packet-review-priority-blocker-severity.json",
            "tower_urgency_route": "/vault/packet-review-priority-tower-urgency.json",
            "next_actions_route": "/vault/packet-review-priority-next-actions.json",
            "carry_forward_route": "/vault/packet-review-priority-carry-forward.json",
            "gp034_status_route": "/vault/gp034-status.json",
            "priority_record_count": len(priority_records),
            "priority_reason_count": priority_reasons["priority_reason_count"],
            "owner_focus_item_count": owner_focus_order["owner_focus_item_count"],
            "blocker_severity_item_count": blocker_severity["blocker_severity_item_count"],
            "tower_urgency_item_count": tower_urgency["tower_urgency_item_count"],
            "next_action_count": next_actions["next_action_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "completed_count": 0,
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "priority_records": priority_records,
        "priority_reasons": priority_reasons,
        "owner_focus_order": owner_focus_order,
        "blocker_severity": blocker_severity,
        "tower_urgency": tower_urgency,
        "next_actions": next_actions,
        "carry_forward": carry_forward,
        "gp033_connection": {
            "gp033_pack_id": gp033["pack"]["id"],
            "gp033_ready": gp033["gp033_status"]["ready"],
            "gp033_safe_to_continue": gp033["gp033_status"]["safe_to_continue_to_gp034"],
            "gp033_vault_done": gp033["gp033_status"]["vault_done"],
            "gp033_section": gp033["pack"]["section"],
            "gp033_review_group_count": gp033["grouping_summary"]["review_group_count"],
            "gp033_review_lane_count": gp033["grouping_summary"]["review_lane_count"],
            "gp033_detail_record_count": gp033["grouping_summary"]["detail_record_count"],
        },
        "gp034_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp033_review_grouping_connected": True,
            "packet_review_priority_ready": True,
            "safe_to_continue_to_gp035": True,
            "vault_done": False,
            "metadata_only_priority": True,
            "private_priority_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp034",
            "next_pack": "VAULT_GP035_PACKET_REVIEW_DECISION_PREP_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_priority_record(group: Dict[str, Any]) -> Dict[str, Any]:
    rule = PACKET_PRIORITY_RULES[group["packet_id"]]
    active_codes = sorted(set(group["blocked_codes"]) | {"PACKET_REVIEW_PRIORITY_PRIVATE_ONLY"})

    return {
        "priority_id": f"VPR-{rule['rank']:03d}",
        "review_group_id": group["review_group_id"],
        "packet_id": group["packet_id"],
        "assembly_id": group["assembly_id"],
        "lane": group["lane"],
        "packet_title": group["packet_title"],
        "priority_rank": rule["rank"],
        "priority_band": rule["priority_band"],
        "reason_codes": rule["reason_codes"],
        "owner_focus_reason": rule["owner_focus_reason"],
        "blocker_severity": rule["blocker_severity"],
        "blocker_severity_rank": BLOCKER_SEVERITY_ORDER[rule["blocker_severity"]],
        "tower_gate_urgency": rule["tower_gate_urgency"],
        "tower_gate_urgency_rank": TOWER_URGENCY_ORDER[rule["tower_gate_urgency"]],
        "priority_status": "READY_FOR_OWNER_FOCUS_EXTERNAL_DELIVERY_BLOCKED",
        "metadata_only": True,
        "private_priority_only": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "completed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "detail_count": group["detail_count"],
        "review_lane_count": 6,
        "redacted_preview_slot_count": group["redacted_preview_slot_count"],
        "tower_gate_count": group["tower_gate_count"],
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
        "ready_for_owner_focus": True,
        "ready_for_external_delivery": False,
        "ready_for_export": False,
        "safe_to_carry_to_gp035": True,
        "owner_note": f"Focus on {group['packet_title']} at priority rank {rule['rank']}. Do not export, share, deliver, or unlock raw content.",
    }


def _build_priority_reasons(priority_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    reason_items = []
    for record in priority_records:
        for index, code in enumerate(record["reason_codes"], start=1):
            reason_items.append(
                {
                    "reason_id": f"VPRR-{record['priority_rank']:03d}-{index:02d}",
                    "priority_id": record["priority_id"],
                    "review_group_id": record["review_group_id"],
                    "packet_id": record["packet_id"],
                    "packet_title": record["packet_title"],
                    "priority_rank": record["priority_rank"],
                    "reason_code": code,
                    "reason_label": _reason_label(code),
                    "metadata_only": True,
                    "owner_review_required": True,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "safe_to_carry_to_gp035": True,
                }
            )

    return {
        "priority_reason_items": reason_items,
        "priority_reason_count": len(reason_items),
        "packet_count": len(priority_records),
        "metadata_only_count": len(reason_items),
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_priority_reasons": True,
    }


def _reason_label(code: str) -> str:
    return code.replace("_", " ").title()


def _build_owner_focus_order(priority_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "owner_focus_id": f"VPFO-{record['priority_rank']:03d}",
            "priority_id": record["priority_id"],
            "review_group_id": record["review_group_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "priority_band": record["priority_band"],
            "owner_focus_reason": record["owner_focus_reason"],
            "focus_status": "READY_FOR_OWNER_FOCUS_ONLY",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed": False,
            "auto_complete_allowed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp035": True,
        }
        for record in priority_records
    ]

    return {
        "owner_focus_items": items,
        "owner_focus_item_count": len(items),
        "first_focus_packet_id": items[0]["packet_id"] if items else None,
        "last_focus_packet_id": items[-1]["packet_id"] if items else None,
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "safe_to_continue_owner_focus": True,
    }


def _build_blocker_severity(priority_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "blocker_severity_id": f"VBS-{record['priority_rank']:03d}",
            "priority_id": record["priority_id"],
            "review_group_id": record["review_group_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "blocker_severity": record["blocker_severity"],
            "blocker_severity_rank": record["blocker_severity_rank"],
            "blocked_code_count": record["blocked_code_count"],
            "blocked_codes": record["blocked_codes"],
            "all_restricted_paths_locked": True,
            "safe_to_override_inside_vault": False,
            "raw_storage_allowed": False,
            "direct_upload_allowed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "portal_access_allowed": False,
            "safe_to_carry_to_gp035": True,
        }
        for record in priority_records
    ]

    return {
        "blocker_severity_items": items,
        "blocker_severity_item_count": len(items),
        "critical_count": sum(1 for item in items if item["blocker_severity"] == "critical"),
        "high_count": sum(1 for item in items if item["blocker_severity"] == "high"),
        "medium_count": sum(1 for item in items if item["blocker_severity"] == "medium"),
        "all_restricted_paths_locked": True,
        "safe_to_override_inside_vault_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_continue_blocker_severity": True,
    }


def _build_tower_urgency(priority_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = [
        {
            "tower_urgency_id": f"VTU-{record['priority_rank']:03d}",
            "priority_id": record["priority_id"],
            "review_group_id": record["review_group_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "tower_gate_urgency": record["tower_gate_urgency"],
            "tower_gate_urgency_rank": record["tower_gate_urgency_rank"],
            "tower_gate_count": record["tower_gate_count"],
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
            "safe_to_carry_to_gp035": True,
        }
        for record in priority_records
    ]

    return {
        "tower_urgency_items": items,
        "tower_urgency_item_count": len(items),
        "high_urgency_count": sum(1 for item in items if item["tower_gate_urgency"] == "high"),
        "medium_urgency_count": sum(1 for item in items if item["tower_gate_urgency"] == "medium"),
        "tower_clearance_required_count": len(items),
        "tower_step_up_required_count": len(items),
        "vault_override_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_urgency_preserved": True,
    }


def _build_next_actions(
    priority_records: List[Dict[str, Any]],
    blocker_severity: Dict[str, Any],
    tower_urgency: Dict[str, Any],
) -> Dict[str, Any]:
    actions = []

    for record in priority_records:
        actions.append(
            {
                "next_action_id": f"VPNX-{record['priority_rank']:03d}",
                "priority_id": record["priority_id"],
                "review_group_id": record["review_group_id"],
                "packet_id": record["packet_id"],
                "packet_title": record["packet_title"],
                "priority_rank": record["priority_rank"],
                "priority_band": record["priority_band"],
                "action_label": f"Review {record['packet_title']} priority bundle.",
                "action_reason": record["owner_focus_reason"],
                "blocker_severity": record["blocker_severity"],
                "tower_gate_urgency": record["tower_gate_urgency"],
                "action_status": "READY_FOR_OWNER_REVIEW_NO_EXECUTION",
                "metadata_only": True,
                "owner_review_required": True,
                "owner_confirmed": False,
                "completed": False,
                "auto_complete_allowed": False,
                "auto_confirm_allowed": False,
                "can_execute_from_vault": False,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "public_packet_proof_allowed": False,
                "safe_to_carry_to_gp035": True,
            }
        )

    actions.append(
        {
            "next_action_id": "VPNX-998",
            "priority_id": "BOUNDARY-LOCKS",
            "review_group_id": "ALL",
            "packet_id": "ALL_PACKETS",
            "packet_title": "All Packet Review Priority Boundaries",
            "priority_rank": 998,
            "priority_band": "BOUNDARY",
            "action_label": "Keep raw storage, direct upload, export, external delivery, public proof, and portals locked.",
            "action_reason": "Restricted paths remain locked across GP034.",
            "blocker_severity": "critical",
            "tower_gate_urgency": "high",
            "action_status": "BOUNDARY_LOCKED",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp035": True,
        }
    )

    actions.append(
        {
            "next_action_id": "VPNX-999",
            "priority_id": "NEXT-GP035",
            "review_group_id": "NEXT",
            "packet_id": "NEXT_VAULT_PACK",
            "packet_title": "GP035 Packet Review Decision Prep",
            "priority_rank": 999,
            "priority_band": "NEXT_BUILD",
            "action_label": "Continue Vault into GP035 packet review decision prep.",
            "action_reason": "GP034 priority state is safe to carry forward.",
            "blocker_severity": "medium",
            "tower_gate_urgency": "medium",
            "action_status": "NEXT_BUILD_READY",
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmed": False,
            "completed": False,
            "auto_complete_allowed": False,
            "auto_confirm_allowed": False,
            "can_execute_from_vault": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp035": True,
        }
    )

    sorted_actions = sorted(
        actions,
        key=lambda action: (
            action["priority_rank"],
            BLOCKER_SEVERITY_ORDER.get(action["blocker_severity"], 9),
            TOWER_URGENCY_ORDER.get(action["tower_gate_urgency"], 9),
            action["next_action_id"],
        ),
    )

    return {
        "next_actions": sorted_actions,
        "next_action_count": len(sorted_actions),
        "packet_action_count": len(priority_records),
        "boundary_action_count": 1,
        "next_build_action_count": 1,
        "owner_review_required_count": len(sorted_actions),
        "completed_count": 0,
        "owner_confirmed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "blocker_severity_item_count": blocker_severity["blocker_severity_item_count"],
        "tower_urgency_item_count": tower_urgency["tower_urgency_item_count"],
        "safe_to_continue_next_actions": True,
        "next_owner_actions": [
            "Review packet review priority order.",
            "Start with ATM route acquisition, apartment lender due diligence, and trust/entity authority packets.",
            "Use blocker severity and Tower-gate urgency to understand what is blocked.",
            "Keep raw storage, direct upload, export, external delivery, public proof, and portals locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP035 packet review decision prep.",
        ],
    }


def _build_carry_forward(
    priority_records: List[Dict[str, Any]],
    next_actions: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VPR-CF-{record['priority_rank']:03d}",
            "priority_id": record["priority_id"],
            "review_group_id": record["review_group_id"],
            "packet_id": record["packet_id"],
            "packet_title": record["packet_title"],
            "priority_rank": record["priority_rank"],
            "priority_band": record["priority_band"],
            "blocker_severity": record["blocker_severity"],
            "tower_gate_urgency": record["tower_gate_urgency"],
            "carry_forward_status": "READY_FOR_GP035_PACKET_REVIEW_DECISION_PREP",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp035": True,
        }
        for record in priority_records
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp035_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_carry_to_gp035": True,
        "next_action_count": next_actions["next_action_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_packet_review_priority_payload())


def get_packet_review_priority_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "priority_truth": payload["priority_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "priority_summary": payload["priority_summary"],
        "gp033_connection": payload["gp033_connection"],
    }


def get_packet_review_priority_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "priority_records": payload["priority_records"],
        "priority_record_count": len(payload["priority_records"]),
    }


def get_packet_review_priority_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "priority_reasons": payload["priority_reasons"],
    }


def get_packet_review_priority_owner_focus() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_focus_order": payload["owner_focus_order"],
    }


def get_packet_review_priority_blocker_severity() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_severity": payload["blocker_severity"],
    }


def get_packet_review_priority_tower_urgency() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_urgency": payload["tower_urgency"],
    }


def get_packet_review_priority_next_actions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_actions": payload["next_actions"],
    }


def get_packet_review_priority_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp034_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp034_status": payload["gp034_status"],
        "priority_truth": payload["priority_truth"],
        "priority_summary": payload["priority_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp033_connection": payload["gp033_connection"],
    }


def render_packet_review_priority_page() -> str:
    payload = clone_payload()
    summary = payload["priority_summary"]
    truth = payload["priority_truth"]
    records = payload["priority_records"]
    next_actions = payload["next_actions"]

    priority_cards = "\n".join(_render_priority_card(record) for record in records)
    action_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(action['action_label'])}</strong>
            <span>{escape(action['action_status'])} · severity: {escape(action['blocker_severity'])} · tower: {escape(action['tower_gate_urgency'])}</span>
          </div>
          <div class="pill {'danger' if action['priority_rank'] <= 3 or action['priority_rank'] == 998 else 'warn'}">Rank {action['priority_rank']}</div>
        </div>
        """
        for action in next_actions["next_actions"][:10]
    )

    owner_actions = "\n".join(f"<li>{escape(action)}</li>" for action in next_actions["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Packet Review Priority · GP034</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 034</div>
        <h1>Packet Review Priority</h1>
        <p class="hero-copy">
          GP034 adds priority logic on top of GP033 packet review grouping. It ranks packet bundles,
          explains reason codes, sorts owner focus order, scores blocker severity, marks Tower-gate urgency,
          and carries next-action priority into GP035. This stays metadata-only and private.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['priority_record_count']}</strong>
            <span>priority records</span>
          </div>
          <div class="metric">
            <strong>{summary['priority_reason_count']}</strong>
            <span>reason codes</span>
          </div>
          <div class="metric">
            <strong>{summary['next_action_count']}</strong>
            <span>next actions</span>
          </div>
          <div class="metric">
            <strong>{str(truth['packet_export_enabled']).lower()}</strong>
            <span>packet export</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Priority ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner focus order</span>
          <span class="pill danger">External delivery locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Priority Records</h2>
      <p>
        Packets are ranked for owner focus without export, external delivery, execution, portals, or public proof.
      </p>
      <div class="grid">
        {priority_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Sorted Next Actions</h2>
        <p>Priority, blocker severity, and Tower-gate urgency sort the next actions.</p>
        <div>
          {action_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP034 prepares GP035 packet review decision prep.</p>
        <ul>
          {owner_actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP034 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['records_route'])}</code>
        <code>{escape(summary['reasons_route'])}</code>
        <code>{escape(summary['owner_focus_route'])}</code>
        <code>{escape(summary['blocker_severity_route'])}</code>
        <code>{escape(summary['tower_urgency_route'])}</code>
        <code>{escape(summary['next_actions_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp034_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Priority Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        External delivery:
        <code>{str(truth['external_packet_delivery_enabled']).lower()}</code>.
        Public packet proof:
        <code>{str(truth['public_packet_proof_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_priority_card(record: Dict[str, Any]) -> str:
    chip_class = "danger" if record["priority_rank"] <= 3 else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record['packet_title'])}</div>
            <div class="meta">
              Priority: <code>{escape(record['priority_id'])}</code><br>
              Rank: <code>{record['priority_rank']}</code><br>
              Band: <code>{escape(record['priority_band'])}</code><br>
              Severity: <code>{escape(record['blocker_severity'])}</code><br>
              Tower urgency: <code>{escape(record['tower_gate_urgency'])}</code><br>
              Export allowed: <code>{str(record['packet_export_allowed']).lower()}</code>
            </div>
          </div>
          <span class="pill {chip_class}">Rank {record['priority_rank']}</span>
        </div>
      </article>
    """
