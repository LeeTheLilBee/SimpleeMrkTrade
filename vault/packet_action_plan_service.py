"""
VAULT GIANT PACK 023 — Packet Action Plan

This pack turns GP022 packet gaps into owner action plans.

Important truth:
- GP023 is not a storage unlock.
- It does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, public proof, seller/broker/trustee portals,
  financing decisions, legal advice, or Tower-owned permissions.
- It creates packet action plans, action steps, dependency lanes, owner priority order,
  and blocked-action reasons.
- It keeps Vault moving aggressively after GP022.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, and external access.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.packet_gap_detail_service import get_packet_gap_detail_payload


PACK_ID = "VAULT_GP023"
PACK_NAME = "Packet Action Plan"
SCHEMA_VERSION = "vault.packet_action_plan.v1"

ACTION_TYPES = {
    "review_metadata_gap": "Review metadata gap",
    "request_missing_detail": "Request missing detail",
    "hold_raw_support": "Hold raw support",
    "hold_external_share": "Hold external share",
    "tower_clearance_wait": "Wait for Tower clearance",
    "owner_confirm_next_step": "Owner confirm next step",
    "carry_forward_to_next_pack": "Carry forward to next pack",
}

ACTION_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before packet actions apply.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "NO_AUTO_ACTION_EXECUTION": "Automatic action execution is disabled.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

BASE_ACTION_STEPS = [
    {
        "action_type": "review_metadata_gap",
        "label": "Review metadata gap details",
        "owner_required": True,
        "tower_owned": False,
        "can_auto_execute": False,
    },
    {
        "action_type": "owner_confirm_next_step",
        "label": "Confirm next owner action",
        "owner_required": True,
        "tower_owned": False,
        "can_auto_execute": False,
    },
    {
        "action_type": "hold_raw_support",
        "label": "Keep raw support locked",
        "owner_required": False,
        "tower_owned": True,
        "can_auto_execute": False,
    },
    {
        "action_type": "hold_external_share",
        "label": "Keep external sharing locked",
        "owner_required": False,
        "tower_owned": True,
        "can_auto_execute": False,
    },
]

PACKET_ACTION_HINTS = {
    "owner_review_atm_route_acquisition": {
        "priority_rank": 1,
        "action_focus": "ATM seller packet gaps, machine list, route economics, vault cash placeholder, lender readiness",
        "next_pack_focus": "ATM seller packet action checklist",
    },
    "owner_review_apartment_lender": {
        "priority_rank": 2,
        "action_focus": "Apartment rent roll, T12, NOI/DSCR, lender packet, property due diligence gaps",
        "next_pack_focus": "Apartment lender packet action checklist",
    },
    "owner_review_trust_entity_authority": {
        "priority_rank": 3,
        "action_focus": "Trust/entity authority, acquisition authority, beneficiary privacy, bank/lender authority gaps",
        "next_pack_focus": "Trust/entity authority action checklist",
    },
    "owner_review_ob_manual_live_private_proof": {
        "priority_rank": 4,
        "action_focus": "OB Manual Live private proof packet metadata gaps",
        "next_pack_focus": "OB private proof action checklist",
    },
    "owner_review_soulaana_artist_ip": {
        "priority_rank": 5,
        "action_focus": "Soulaana artist/IP proof and reserved art boundary gaps",
        "next_pack_focus": "Soulaana IP action checklist",
    },
    "owner_review_private_beta_onboarding": {
        "priority_rank": 6,
        "action_focus": "Private beta onboarding packet and Tower access authority gaps",
        "next_pack_focus": "Private beta action checklist",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_packet_action_plan_payload() -> Dict[str, Any]:
    gp022 = get_packet_gap_detail_payload()
    gap_board = gp022["gap_board"]
    review_packets = gap_board["review_packets"]
    gap_records = gap_board["gap_records"]

    action_plans = [_build_action_plan(packet, gap_records) for packet in review_packets]
    action_steps = [step for plan in action_plans for step in plan["action_steps"]]
    dependency_lanes = _build_dependency_lanes(action_plans)
    priority_queue = _build_priority_queue(action_plans)
    blocked_actions = _build_blocked_actions(action_steps)
    owner_queue = _build_owner_queue(action_plans, priority_queue, blocked_actions)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "packet_action_plan",
        },
        "action_truth": {
            "packet_action_plan_enabled": True,
            "metadata_only": True,
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
            "auto_action_execution_enabled": False,
            "auto_packet_approval_enabled": False,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp023",
            "safe_next_unlock": "GP024 can deepen owner action execution prep without unlocking raw storage or external sharing.",
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
        "action_summary": {
            "room_title": "Vault Packet Action Plan",
            "route": "/vault/packet-action-plan",
            "json_route": "/vault/packet-action-plan.json",
            "board_route": "/vault/packet-action-plan-board.json",
            "steps_route": "/vault/packet-action-plan-steps.json",
            "dependencies_route": "/vault/packet-action-plan-dependencies.json",
            "priority_route": "/vault/packet-action-plan-priority.json",
            "blocked_route": "/vault/packet-action-plan-blocked.json",
            "owner_queue_route": "/vault/packet-action-plan-owner-queue.json",
            "gp023_status_route": "/vault/gp023-status.json",
            "action_plan_count": len(action_plans),
            "action_step_count": len(action_steps),
            "dependency_lane_count": len(dependency_lanes["lanes"]),
            "priority_item_count": len(priority_queue["priority_items"]),
            "blocked_action_count": blocked_actions["blocked_action_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "action_plan_board": {
            "action_plans": action_plans,
            "action_plan_count": len(action_plans),
            "high_priority_plan_count": sum(1 for plan in action_plans if plan["priority_rank"] <= 3),
            "ready_for_owner_action_count": sum(1 for plan in action_plans if plan["plan_status"] == "READY_FOR_OWNER_ACTION_REVIEW"),
            "auto_execute_allowed_count": 0,
            "clouds_status": "parked_do_not_continue_from_vault_gp023",
        },
        "action_steps": action_steps,
        "dependency_lanes": dependency_lanes,
        "priority_queue": priority_queue,
        "blocked_actions": blocked_actions,
        "owner_review_state": owner_queue,
        "gp022_connection": {
            "gp022_pack_id": gp022["pack"]["id"],
            "gp022_ready": gp022["gp022_status"]["ready"],
            "gp022_safe_to_continue": gp022["gp022_status"]["safe_to_continue_to_gp023"],
            "gp022_vault_done": gp022["gp022_status"]["vault_done"],
            "gp022_gap_record_count": gp022["gap_summary"]["gap_record_count"],
        },
        "gp023_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp022_packet_gap_detail_connected": True,
            "packet_action_plan_ready": True,
            "safe_to_continue_to_gp024": True,
            "vault_done": False,
            "metadata_only_action_plan": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp023",
            "next_pack": "VAULT_GP024_OWNER_ACTION_EXECUTION_PREP_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_action_plan(packet: Dict[str, Any], gap_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    related_gaps = [gap for gap in gap_records if gap["packet_id"] == packet["packet_id"]]
    hint = PACKET_ACTION_HINTS.get(packet["packet_id"], {
        "priority_rank": 99,
        "action_focus": "Packet action review",
        "next_pack_focus": "Next packet action detail",
    })

    steps = [_build_action_step(packet, gap, idx + 1) for idx, gap in enumerate(related_gaps)]
    steps.extend(_build_base_steps(packet, len(steps)))

    return {
        "plan_id": f"VAP-{packet['packet_id'].replace('owner_review_', '').upper()}",
        "packet_id": packet["packet_id"],
        "title": packet["title"],
        "lane": packet["lane"],
        "source_pack": packet["source_pack"],
        "source_route": packet["source_route"],
        "priority": packet["priority"],
        "priority_rank": hint["priority_rank"],
        "action_focus": hint["action_focus"],
        "next_pack_focus": hint["next_pack_focus"],
        "plan_status": "READY_FOR_OWNER_ACTION_REVIEW",
        "gap_count": len(related_gaps),
        "action_step_count": len(steps),
        "owner_required_step_count": sum(1 for step in steps if step["owner_required"]),
        "tower_owned_step_count": sum(1 for step in steps if step["tower_owned"]),
        "auto_execute_allowed_count": 0,
        "action_steps": steps,
        "plan_truth": {
            "metadata_only": True,
            "raw_body_available": False,
            "external_share_allowed": False,
            "auto_execute_allowed": False,
            "financing_decision_allowed": False,
            "legal_advice_allowed": False,
            "raw_verification_claim_allowed": False,
        },
        "owner_action": f"Review {packet['title']} action plan and choose the next safe metadata step.",
    }


def _build_action_step(packet: Dict[str, Any], gap: Dict[str, Any], index: int) -> Dict[str, Any]:
    action_type = _action_type_for_gap(gap)
    blocked_codes = set(gap.get("blocked_codes", []))
    blocked_codes.update({
        "RAW_FILE_BODY_LOCKED",
        "DIRECT_UPLOAD_LOCKED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_EXPORT_LOCKED",
        "RAW_EXPORT_LOCKED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_ACTION_EXECUTION",
        "CLOUDS_PARKED",
    })

    return {
        "step_id": f"VAS-{packet['packet_id'].replace('owner_review_', '').upper()}-{index:02d}",
        "plan_packet_id": packet["packet_id"],
        "gap_id": gap["gap_id"],
        "action_type": action_type,
        "action_type_label": ACTION_TYPES.get(action_type, action_type),
        "label": _label_for_action_type(action_type, gap),
        "sequence": index,
        "status": "READY_FOR_OWNER_ACTION_REVIEW",
        "owner_required": action_type in {"review_metadata_gap", "request_missing_detail", "owner_confirm_next_step", "carry_forward_to_next_pack"},
        "tower_owned": gap["tower_owned"] or action_type in {"hold_raw_support", "hold_external_share", "tower_clearance_wait"},
        "can_auto_execute": False,
        "raw_body_required": gap["raw_body_required_to_close"],
        "raw_body_available": False,
        "external_share_allowed": False,
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [ACTION_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": gap["owner_action"],
    }


def _action_type_for_gap(gap: Dict[str, Any]) -> str:
    if gap["gap_type"] == "missing_metadata_detail":
        return "request_missing_detail"
    if gap["gap_type"] == "raw_document_support_locked":
        return "hold_raw_support"
    if gap["gap_type"] == "tower_clearance_required":
        return "tower_clearance_wait"
    if gap["gap_type"] == "external_share_locked":
        return "hold_external_share"
    if gap["gap_type"] == "owner_confirmation_required":
        return "owner_confirm_next_step"
    return "review_metadata_gap"


def _label_for_action_type(action_type: str, gap: Dict[str, Any]) -> str:
    labels = {
        "review_metadata_gap": f"Review: {gap['label']}",
        "request_missing_detail": f"Request/review detail: {gap['label']}",
        "hold_raw_support": "Keep raw support locked and mark provider/Tower path needed",
        "hold_external_share": "Keep external share locked and use owner-only redacted review",
        "tower_clearance_wait": "Wait for Tower clearance before sensitive movement",
        "owner_confirm_next_step": "Owner confirms the next safe metadata action",
        "carry_forward_to_next_pack": "Carry forward to the next Vault depth pack",
    }
    return labels.get(action_type, gap["label"])


def _build_base_steps(packet: Dict[str, Any], current_count: int) -> List[Dict[str, Any]]:
    steps = []
    for idx, base in enumerate(BASE_ACTION_STEPS, start=current_count + 1):
        blocked_codes = {
            "RAW_FILE_BODY_LOCKED",
            "DIRECT_UPLOAD_LOCKED",
            "EXTERNAL_ACCESS_DENIED",
            "UNREDACTED_EXPORT_LOCKED",
            "RAW_EXPORT_LOCKED",
            "OWNER_CONFIRMATION_REQUIRED",
            "NO_AUTO_ACTION_EXECUTION",
            "CLOUDS_PARKED",
        }

        if base["tower_owned"]:
            blocked_codes.add("TOWER_CLEARANCE_REQUIRED")

        steps.append(
            {
                "step_id": f"VAS-{packet['packet_id'].replace('owner_review_', '').upper()}-{idx:02d}",
                "plan_packet_id": packet["packet_id"],
                "gap_id": None,
                "action_type": base["action_type"],
                "action_type_label": ACTION_TYPES[base["action_type"]],
                "label": base["label"],
                "sequence": idx,
                "status": "READY_FOR_OWNER_ACTION_REVIEW",
                "owner_required": base["owner_required"],
                "tower_owned": base["tower_owned"],
                "can_auto_execute": base["can_auto_execute"],
                "raw_body_required": base["action_type"] == "hold_raw_support",
                "raw_body_available": False,
                "external_share_allowed": False,
                "blocked_codes": sorted(blocked_codes),
                "blocked_labels": [ACTION_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
                "owner_note": "Base packet action step. Keep restricted paths locked.",
            }
        )
    return steps


def _build_dependency_lanes(action_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    lanes = [
        {
            "lane_id": "dependency_owner_review",
            "label": "Owner review dependency",
            "owner": "Vault",
            "step_count": sum(plan["owner_required_step_count"] for plan in action_plans),
            "blocked": False,
            "tower_owned": False,
        },
        {
            "lane_id": "dependency_tower_clearance",
            "label": "Tower clearance dependency",
            "owner": "The Tower",
            "step_count": sum(plan["tower_owned_step_count"] for plan in action_plans),
            "blocked": True,
            "tower_owned": True,
        },
        {
            "lane_id": "dependency_storage_provider",
            "label": "Storage provider dependency",
            "owner": "Vault/Tower boundary",
            "step_count": sum(1 for plan in action_plans for step in plan["action_steps"] if step["raw_body_required"]),
            "blocked": True,
            "tower_owned": True,
        },
        {
            "lane_id": "dependency_external_share",
            "label": "External share dependency",
            "owner": "The Tower",
            "step_count": sum(1 for plan in action_plans for step in plan["action_steps"] if "EXTERNAL_ACCESS_DENIED" in step["blocked_codes"]),
            "blocked": True,
            "tower_owned": True,
        },
    ]

    return {
        "lanes": lanes,
        "lane_count": len(lanes),
        "blocked_lane_count": sum(1 for lane in lanes if lane["blocked"]),
        "tower_owned_lane_count": sum(1 for lane in lanes if lane["tower_owned"]),
        "all_restricted_dependencies_locked": True,
    }


def _build_priority_queue(action_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_plans = sorted(action_plans, key=lambda item: item["priority_rank"])

    priority_items = [
        {
            "priority_id": f"VAPQ-{idx:02d}",
            "plan_id": plan["plan_id"],
            "packet_id": plan["packet_id"],
            "title": plan["title"],
            "lane": plan["lane"],
            "priority_rank": plan["priority_rank"],
            "priority": plan["priority"],
            "action_focus": plan["action_focus"],
            "next_pack_focus": plan["next_pack_focus"],
            "owner_review_required": True,
            "auto_execute_allowed": False,
        }
        for idx, plan in enumerate(sorted_plans, start=1)
    ]

    return {
        "priority_items": priority_items,
        "priority_item_count": len(priority_items),
        "first_priority_packet_id": priority_items[0]["packet_id"] if priority_items else None,
        "owner_review_required": True,
        "auto_execute_allowed": False,
    }


def _build_blocked_actions(action_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for step in action_steps for code in step["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": ACTION_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_step_count": sum(1 for step in action_steps if code in step["blocked_codes"]),
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]

    return {
        "blocked_actions": blockers,
        "blocked_action_count": len(blockers),
        "all_blocked_actions_safe": True,
        "auto_override_allowed": False,
        "all_restricted_paths_locked": True,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only action planning. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before packet action.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP023.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_queue(
    action_plans: List[Dict[str, Any]],
    priority_queue: Dict[str, Any],
    blocked_actions: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "PAP-ACTION-001",
            "label": "Open the first high-priority action plan.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PAP-ACTION-002",
            "label": "Choose the next metadata action without unlocking raw support.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PAP-ACTION-003",
            "label": "Keep Tower-owned clearance, export, portal, and external share paths locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PAP-ACTION-004",
            "label": "Do not claim financing, legal, or raw verification completion.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PAP-ACTION-005",
            "label": "Continue Vault into GP024 owner action execution prep.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Packet Action Plan",
        "actions": actions,
        "action_count": len(actions),
        "action_plan_count": len(action_plans),
        "priority_item_count": priority_queue["priority_item_count"],
        "blocked_action_count": blocked_actions["blocked_action_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Open the first high-priority action plan.",
            "Choose the next metadata action without unlocking raw support.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP024 owner action execution prep.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_packet_action_plan_payload())


def get_packet_action_plan_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_truth": payload["action_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "action_summary": payload["action_summary"],
        "gp022_connection": payload["gp022_connection"],
    }


def get_packet_action_plan_board() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_plan_board": payload["action_plan_board"],
    }


def get_packet_action_plan_steps() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "action_steps": payload["action_steps"],
        "action_step_count": len(payload["action_steps"]),
    }


def get_packet_action_plan_dependencies() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "dependency_lanes": payload["dependency_lanes"],
    }


def get_packet_action_plan_priority() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "priority_queue": payload["priority_queue"],
    }


def get_packet_action_plan_blocked() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocked_actions": payload["blocked_actions"],
    }


def get_packet_action_plan_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp023_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp023_status": payload["gp023_status"],
        "action_truth": payload["action_truth"],
        "action_summary": payload["action_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp022_connection": payload["gp022_connection"],
    }


def render_packet_action_plan_page() -> str:
    payload = clone_payload()
    summary = payload["action_summary"]
    truth = payload["action_truth"]
    board = payload["action_plan_board"]
    priority = payload["priority_queue"]
    owner = payload["owner_review_state"]

    plan_cards = "\n".join(_render_plan_card(plan) for plan in board["action_plans"])
    priority_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["title"])}</strong>
            <span>Rank {item["priority_rank"]} · {escape(item["action_focus"])}</span>
          </div>
          <div class="pill {'warn' if item["priority_rank"] <= 3 else 'ok'}">Priority {item["priority_rank"]}</div>
        </div>
        """
        for item in priority["priority_items"]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Packet Action Plan · GP023</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 023</div>
        <h1>Packet Action Plan</h1>
        <p class="hero-copy">
          GP023 turns packet gaps into ordered owner action plans. It shows what to review first,
          which steps are blocked, which dependencies are Tower-owned, and what carries into GP024
          without unlocking raw storage, external access, public proof, unredacted exports, financing decisions,
          legal advice, or raw verification claims.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["action_plan_count"]}</strong>
            <span>action plans</span>
          </div>
          <div class="metric">
            <strong>{summary["action_step_count"]}</strong>
            <span>action steps</span>
          </div>
          <div class="metric">
            <strong>{summary["priority_item_count"]}</strong>
            <span>priority items</span>
          </div>
          <div class="metric">
            <strong>{summary["blocked_action_count"]}</strong>
            <span>blocked actions</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Action planning ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Auto execution disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Action Plan Board</h2>
      <p>
        Every packet has a safe action plan. No action auto-executes and no restricted path unlocks.
      </p>
      <div class="grid">
        {plan_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Priority Queue</h2>
        <p>High-priority ATM, apartment, and trust/entity packets stay first.</p>
        <div>
          {priority_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP023 prepares GP024 owner action execution prep.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP023 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["board_route"])}</code>
        <code>{escape(summary["steps_route"])}</code>
        <code>{escape(summary["dependencies_route"])}</code>
        <code>{escape(summary["priority_route"])}</code>
        <code>{escape(summary["blocked_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp023_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Action Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Raw storage:
        <code>{str(truth["raw_file_body_storage_enabled"]).lower()}</code>.
        Auto execution:
        <code>{str(truth["auto_action_execution_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_plan_card(plan: Dict[str, Any]) -> str:
    priority_class = "warn" if plan["priority_rank"] <= 3 else "ok"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(plan["title"])}</div>
            <div class="meta">
              Plan: <code>{escape(plan["plan_id"])}</code><br>
              Lane: {escape(plan["lane"])}<br>
              Rank: <code>{plan["priority_rank"]}</code><br>
              Steps: <code>{plan["action_step_count"]}</code><br>
              Focus: {escape(plan["action_focus"])}
            </div>
          </div>
          <span class="pill {priority_class}">Rank {plan["priority_rank"]}</span>
        </div>
      </article>
    """
