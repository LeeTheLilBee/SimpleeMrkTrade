"""
VAULT GIANT PACK 033 — Packet Review Grouping

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack deepens GP032 packet component detail by grouping detail records into
per-packet owner-review bundles.

Purpose:
- Group packet component detail records by packet.
- Create owner-review lanes for each packet bundle.
- Group redacted-preview status by packet.
- Group Tower gate status by packet.
- Group blockers by packet.
- Carry packet review groups forward to GP034.

Important truth:
- GP033 is not a raw file storage provider.
- GP033 does not unlock direct upload.
- GP033 does not create external packet delivery.
- GP033 does not export raw or unredacted packet bodies.
- GP033 does not create public proof.
- GP033 does not open seller/broker/trustee/external portals.
- GP033 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Packet review grouping means private metadata grouping for owner review only.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.packet_component_detail_service import get_packet_component_detail_payload


PACK_ID = "VAULT_GP033"
PACK_NAME = "Packet Review Grouping"
SCHEMA_VERSION = "vault.packet_review_grouping.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault groups packet review but does not execute actions.",
    "NO_EXTERNAL_PACKET_DELIVERY": "External packet delivery is disabled.",
    "NO_PACKET_EXPORT": "Packet export is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Controlled packet assembly is private only.",
    "PACKET_COMPONENT_DETAIL_PRIVATE_ONLY": "Packet component detail is private only.",
    "PACKET_REVIEW_GROUPING_PRIVATE_ONLY": "Packet review grouping is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

REVIEW_LANE_TYPES = [
    {
        "lane_type": "requirements",
        "label": "Requirements",
        "description": "Requirement summaries and meanings for owner review.",
        "tower_owned": False,
    },
    {
        "lane_type": "redacted_preview",
        "label": "Redacted Preview",
        "description": "Redacted-preview slots only; no raw body content.",
        "tower_owned": False,
    },
    {
        "lane_type": "receipt_references",
        "label": "Receipt References",
        "description": "Receipt and owner-action references, private metadata only.",
        "tower_owned": False,
    },
    {
        "lane_type": "tower_gates",
        "label": "Tower Gates",
        "description": "Tower clearance, step-up, export locks, portals, and sensitive visibility.",
        "tower_owned": True,
    },
    {
        "lane_type": "blocked_paths",
        "label": "Blocked Paths",
        "description": "Locked paths that cannot be overridden inside Vault.",
        "tower_owned": False,
    },
    {
        "lane_type": "carry_forward",
        "label": "Carry Forward",
        "description": "Safe-to-carry markers into GP034.",
        "tower_owned": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_packet_review_grouping_payload() -> Dict[str, Any]:
    gp032 = get_packet_component_detail_payload()

    detail_records = gp032["detail_records"]
    grouped = _group_details_by_packet(detail_records)

    review_groups = [
        _build_review_group(packet_id, records, index + 1)
        for index, (packet_id, records) in enumerate(sorted(grouped.items(), key=lambda item: item[0]))
    ]

    review_lanes = _build_review_lanes(review_groups)
    redacted_grouping = _build_redacted_preview_grouping(review_groups)
    tower_gate_grouping = _build_tower_gate_grouping(review_groups)
    blocker_grouping = _build_blocker_grouping(review_groups)
    owner_review = _build_owner_review_state(review_groups, review_lanes, blocker_grouping)
    carry_forward = _build_carry_forward(review_groups, owner_review)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "packet_review_grouping",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "grouping_truth": {
            "packet_review_grouping_enabled": True,
            "metadata_only": True,
            "private_grouping_only": True,
            "grouping_means_owner_review_not_delivery": True,
            "review_lanes_enabled": True,
            "redacted_preview_grouping_enabled": True,
            "tower_gate_grouping_enabled": True,
            "blocker_grouping_enabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp033",
            "safe_next_unlock": "GP034 can deepen packet review priority without unlocking raw storage, external delivery, public proof, portals, export, auto-run, or execution.",
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
        "grouping_summary": {
            "room_title": "Vault Packet Review Grouping",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/packet-review-grouping",
            "json_route": "/vault/packet-review-grouping.json",
            "groups_route": "/vault/packet-review-grouping-groups.json",
            "lanes_route": "/vault/packet-review-grouping-lanes.json",
            "redacted_preview_route": "/vault/packet-review-grouping-redacted-preview.json",
            "tower_gates_route": "/vault/packet-review-grouping-tower-gates.json",
            "blockers_route": "/vault/packet-review-grouping-blockers.json",
            "owner_queue_route": "/vault/packet-review-grouping-owner-queue.json",
            "carry_forward_route": "/vault/packet-review-grouping-carry-forward.json",
            "gp033_status_route": "/vault/gp033-status.json",
            "review_group_count": len(review_groups),
            "detail_record_count": sum(group["detail_count"] for group in review_groups),
            "review_lane_count": review_lanes["review_lane_count"],
            "redacted_preview_group_count": redacted_grouping["redacted_preview_group_count"],
            "tower_gate_group_count": tower_gate_grouping["tower_gate_group_count"],
            "blocker_group_count": blocker_grouping["blocker_group_count"],
            "owner_review_item_count": owner_review["owner_review_item_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "completed_count": 0,
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "review_groups": review_groups,
        "review_lanes": review_lanes,
        "redacted_preview_grouping": redacted_grouping,
        "tower_gate_grouping": tower_gate_grouping,
        "blocker_grouping": blocker_grouping,
        "owner_review_state": owner_review,
        "carry_forward": carry_forward,
        "gp032_connection": {
            "gp032_pack_id": gp032["pack"]["id"],
            "gp032_ready": gp032["gp032_status"]["ready"],
            "gp032_safe_to_continue": gp032["gp032_status"]["safe_to_continue_to_gp033"],
            "gp032_vault_done": gp032["gp032_status"]["vault_done"],
            "gp032_section": gp032["pack"]["section"],
            "gp032_detail_record_count": gp032["detail_summary"]["detail_record_count"],
            "gp032_requirement_meaning_count": gp032["detail_summary"]["requirement_meaning_count"],
            "gp032_redacted_preview_slot_count": gp032["detail_summary"]["redacted_preview_slot_count"],
        },
        "gp033_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "gp032_component_detail_connected": True,
            "packet_review_grouping_ready": True,
            "safe_to_continue_to_gp034": True,
            "vault_done": False,
            "metadata_only_grouping": True,
            "private_grouping_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp033",
            "next_pack": "VAULT_GP034_PACKET_REVIEW_PRIORITY_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _group_details_by_packet(detail_records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in detail_records:
        grouped[record["packet_id"]].append(record)
    for packet_id in grouped:
        grouped[packet_id] = sorted(grouped[packet_id], key=lambda record: record["component_sequence"])
    return dict(grouped)


def _build_review_group(packet_id: str, records: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
    first = records[0]
    active_codes = sorted({code for record in records for code in record["blocked_codes"]} | {"PACKET_REVIEW_GROUPING_PRIVATE_ONLY"})

    redacted_items = [record for record in records if record["redacted_preview_only"]]
    tower_gate_items = [record for record in records if record["tower_clearance_required"] or record["tower_step_up_required"]]

    return {
        "review_group_id": f"VPG-{index:03d}",
        "packet_id": packet_id,
        "assembly_id": first["assembly_id"],
        "lane": first["lane"],
        "packet_title": first["packet_title"],
        "review_group_status": "OPEN_FOR_OWNER_REVIEW_DELIVERY_BLOCKED",
        "metadata_only": True,
        "private_grouping_only": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "completed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "detail_ids": [record["detail_id"] for record in records],
        "component_ids": [record["component_id"] for record in records],
        "component_types": [record["component_type"] for record in records],
        "detail_count": len(records),
        "redacted_preview_slot_count": len(redacted_items),
        "tower_gate_count": len(tower_gate_items),
        "blocked_code_count": len(active_codes),
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
        "ready_for_owner_review": True,
        "ready_for_external_delivery": False,
        "ready_for_export": False,
        "safe_to_carry_to_gp034": True,
        "blocked_codes": active_codes,
        "blocked_labels": [BLOCK_CODES.get(code, code) for code in active_codes],
        "owner_note": f"Review {first['packet_title']} as a grouped private metadata packet review. Do not export, share, deliver, or unlock raw content.",
    }


def _build_review_lanes(review_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    lanes = []
    for group in review_groups:
        for lane_def in REVIEW_LANE_TYPES:
            lanes.append(
                {
                    "review_lane_id": f"VPL-{group['review_group_id'].replace('VPG-', '')}-{lane_def['lane_type']}",
                    "review_group_id": group["review_group_id"],
                    "packet_id": group["packet_id"],
                    "assembly_id": group["assembly_id"],
                    "packet_title": group["packet_title"],
                    "lane_type": lane_def["lane_type"],
                    "label": lane_def["label"],
                    "description": lane_def["description"],
                    "tower_owned": lane_def["tower_owned"],
                    "lane_status": "OPEN_FOR_OWNER_REVIEW",
                    "metadata_only": True,
                    "owner_review_required": True,
                    "owner_reviewed": False,
                    "completed": False,
                    "auto_complete_allowed": False,
                    "external_delivery_allowed": False,
                    "packet_export_allowed": False,
                    "public_packet_proof_allowed": False,
                    "safe_to_carry_to_gp034": True,
                }
            )

    return {
        "review_lanes": lanes,
        "review_lane_count": len(lanes),
        "lane_type_count": len(REVIEW_LANE_TYPES),
        "packet_group_count": len(review_groups),
        "tower_owned_lane_count": sum(1 for lane in lanes if lane["tower_owned"]),
        "owner_review_required_count": len(lanes),
        "completed_lane_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "all_lanes_metadata_only": True,
        "safe_to_continue_review_lanes": True,
    }


def _build_redacted_preview_grouping(review_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    groups = [
        {
            "redacted_preview_group_id": f"VRPG-{group['review_group_id'].replace('VPG-', '')}",
            "review_group_id": group["review_group_id"],
            "packet_id": group["packet_id"],
            "assembly_id": group["assembly_id"],
            "packet_title": group["packet_title"],
            "redacted_preview_slot_count": group["redacted_preview_slot_count"],
            "redacted_preview_state": "REDACTED_PREVIEW_GROUP_RESERVED_NO_RAW_BODY",
            "metadata_only": True,
            "raw_body_available": False,
            "raw_body_stored": False,
            "direct_upload_unlocked": False,
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "public_packet_proof_allowed": False,
            "owner_review_required": True,
            "safe_to_carry_to_gp034": True,
        }
        for group in review_groups
    ]

    return {
        "redacted_preview_groups": groups,
        "redacted_preview_group_count": len(groups),
        "total_redacted_preview_slot_count": sum(group["redacted_preview_slot_count"] for group in groups),
        "raw_body_available_count": 0,
        "raw_body_stored_count": 0,
        "direct_upload_unlocked_count": 0,
        "unredacted_export_allowed_count": 0,
        "raw_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_continue_redacted_preview_grouping": True,
    }


def _build_tower_gate_grouping(review_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    groups = [
        {
            "tower_gate_group_id": f"VTGG-{group['review_group_id'].replace('VPG-', '')}",
            "review_group_id": group["review_group_id"],
            "packet_id": group["packet_id"],
            "assembly_id": group["assembly_id"],
            "packet_title": group["packet_title"],
            "tower_gate_count": group["tower_gate_count"],
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
            "safe_to_carry_to_gp034": True,
        }
        for group in review_groups
    ]

    return {
        "tower_gate_groups": groups,
        "tower_gate_group_count": len(groups),
        "tower_clearance_required_count": len(groups),
        "tower_step_up_required_count": len(groups),
        "vault_override_allowed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "portal_access_allowed_count": 0,
        "all_tower_gate_groups_preserved": True,
    }


def _build_blocker_grouping(review_groups: List[Dict[str, Any]]) -> Dict[str, Any]:
    groups = [
        {
            "blocker_group_id": f"VBG-{group['review_group_id'].replace('VPG-', '')}",
            "review_group_id": group["review_group_id"],
            "packet_id": group["packet_id"],
            "assembly_id": group["assembly_id"],
            "packet_title": group["packet_title"],
            "blocked_code_count": group["blocked_code_count"],
            "blocked_codes": group["blocked_codes"],
            "blocked_labels": group["blocked_labels"],
            "all_restricted_paths_locked": True,
            "safe_to_override_inside_vault": False,
            "raw_storage_allowed": False,
            "direct_upload_allowed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "portal_access_allowed": False,
            "safe_to_carry_to_gp034": True,
        }
        for group in review_groups
    ]

    active_codes = sorted({code for group in groups for code in group["blocked_codes"]})

    return {
        "blocker_groups": groups,
        "active_block_codes": active_codes,
        "blocker_group_count": len(groups),
        "active_block_code_count": len(active_codes),
        "all_blocker_groups_safe": True,
        "auto_override_allowed": False,
        "all_restricted_paths_locked": True,
        "raw_storage_allowed": False,
        "direct_upload_allowed": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "public_packet_proof_allowed": False,
        "portal_access_allowed": False,
    }


def _build_owner_review_state(
    review_groups: List[Dict[str, Any]],
    review_lanes: Dict[str, Any],
    blocker_grouping: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "owner_review_id": f"VPG-OR-{group['review_group_id'].replace('VPG-', '')}",
            "review_group_id": group["review_group_id"],
            "packet_id": group["packet_id"],
            "assembly_id": group["assembly_id"],
            "packet_title": group["packet_title"],
            "review_status": "READY_FOR_OWNER_REVIEW_DELIVERY_BLOCKED",
            "detail_count": group["detail_count"],
            "redacted_preview_slot_count": group["redacted_preview_slot_count"],
            "tower_gate_count": group["tower_gate_count"],
            "blocked_code_count": group["blocked_code_count"],
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
            "safe_to_carry_to_gp034": True,
        }
        for group in review_groups
    ]

    return {
        "owner_review_items": items,
        "owner_review_item_count": len(items),
        "ready_for_owner_review_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "auto_completed_count": 0,
        "review_lane_count": review_lanes["review_lane_count"],
        "blocker_group_count": blocker_grouping["blocker_group_count"],
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_continue_owner_review": True,
        "next_owner_actions": [
            "Review packet review groups.",
            "Review requirements, redacted preview, receipt references, Tower gates, blockers, and carry-forward lanes.",
            "Keep raw storage, direct upload, export, external delivery, public proof, and portals locked.",
            "Keep Tower-owned clearance and step-up gates intact.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP034 packet review priority.",
        ],
    }


def _build_carry_forward(review_groups: List[Dict[str, Any]], owner_review: Dict[str, Any]) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VPG-CF-{group['review_group_id'].replace('VPG-', '')}",
            "review_group_id": group["review_group_id"],
            "packet_id": group["packet_id"],
            "assembly_id": group["assembly_id"],
            "packet_title": group["packet_title"],
            "carry_forward_status": "READY_FOR_GP034_PACKET_REVIEW_PRIORITY",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp034": True,
        }
        for group in review_groups
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp034_count": len(items),
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_carry_to_gp034": True,
        "owner_review_item_count": owner_review["owner_review_item_count"],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_packet_review_grouping_payload())


def get_packet_review_grouping_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "grouping_truth": payload["grouping_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "grouping_summary": payload["grouping_summary"],
        "gp032_connection": payload["gp032_connection"],
    }


def get_packet_review_grouping_groups() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_groups": payload["review_groups"],
        "review_group_count": len(payload["review_groups"]),
    }


def get_packet_review_grouping_lanes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_lanes": payload["review_lanes"],
    }


def get_packet_review_grouping_redacted_preview() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "redacted_preview_grouping": payload["redacted_preview_grouping"],
    }


def get_packet_review_grouping_tower_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gate_grouping": payload["tower_gate_grouping"],
    }


def get_packet_review_grouping_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_grouping": payload["blocker_grouping"],
    }


def get_packet_review_grouping_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_packet_review_grouping_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp033_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp033_status": payload["gp033_status"],
        "grouping_truth": payload["grouping_truth"],
        "grouping_summary": payload["grouping_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp032_connection": payload["gp032_connection"],
    }


def render_packet_review_grouping_page() -> str:
    payload = clone_payload()
    summary = payload["grouping_summary"]
    truth = payload["grouping_truth"]
    groups = payload["review_groups"]
    lanes = payload["review_lanes"]
    owner = payload["owner_review_state"]

    group_cards = "\n".join(_render_group_card(group) for group in groups)
    lane_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(lane['label'])}</strong>
            <span>{escape(lane['packet_title'])} · {escape(lane['lane_status'])}</span>
          </div>
          <div class="pill {'danger' if lane['tower_owned'] else 'warn'}">{'Tower lane' if lane['tower_owned'] else 'Review lane'}</div>
        </div>
        """
        for lane in lanes["review_lanes"][:18]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Packet Review Grouping · GP033</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 033</div>
        <h1>Packet Review Grouping</h1>
        <p class="hero-copy">
          GP033 groups GP032 packet component detail into per-packet owner-review bundles.
          Each group carries requirement lanes, redacted-preview grouping, Tower gate grouping,
          blocker grouping, owner review state, and carry-forward readiness into GP034.
          This stays metadata-only and private.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['review_group_count']}</strong>
            <span>review groups</span>
          </div>
          <div class="metric">
            <strong>{summary['detail_record_count']}</strong>
            <span>detail records grouped</span>
          </div>
          <div class="metric">
            <strong>{summary['review_lane_count']}</strong>
            <span>review lanes</span>
          </div>
          <div class="metric">
            <strong>{str(truth['external_packet_delivery_enabled']).lower()}</strong>
            <span>external delivery</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Grouping ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Packet export locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Packet Review Groups</h2>
      <p>
        Each packet group carries component detail, redacted-preview state, Tower gates, blockers, and carry-forward.
      </p>
      <div class="grid">
        {group_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Review Lanes</h2>
        <p>Owner-review lanes stay private and metadata-only.</p>
        <div>
          {lane_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP033 prepares GP034 packet review priority.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP033 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['groups_route'])}</code>
        <code>{escape(summary['lanes_route'])}</code>
        <code>{escape(summary['redacted_preview_route'])}</code>
        <code>{escape(summary['tower_gates_route'])}</code>
        <code>{escape(summary['blockers_route'])}</code>
        <code>{escape(summary['owner_queue_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp033_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Grouping Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Packet export:
        <code>{str(truth['packet_export_enabled']).lower()}</code>.
        Public packet proof:
        <code>{str(truth['public_packet_proof_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_group_card(group: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(group['packet_title'])}</div>
            <div class="meta">
              Group: <code>{escape(group['review_group_id'])}</code><br>
              Packet: <code>{escape(group['packet_id'])}</code><br>
              Details: <code>{group['detail_count']}</code><br>
              Redacted slots: <code>{group['redacted_preview_slot_count']}</code><br>
              Export allowed: <code>{str(group['packet_export_allowed']).lower()}</code>
            </div>
          </div>
          <span class="pill warn">{escape(group['review_group_status'])}</span>
        </div>
      </article>
    """
