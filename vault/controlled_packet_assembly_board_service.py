"""
VAULT GIANT PACK 031 — Controlled Packet Assembly Board

NEW SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack starts the next Vault product-depth section after GP030.

Purpose:
- Build a controlled packet assembly board for owner review.
- Group packets by business/mission lane.
- Connect each assembly record back to GP030 readiness.
- Prepare redacted, metadata-only packet structures for future review.
- Keep every restricted path locked.

Important truth:
- GP031 is not a raw file storage provider.
- GP031 does not unlock direct upload.
- GP031 does not create external packet delivery.
- GP031 does not export raw or unredacted packet bodies.
- GP031 does not create public proof.
- GP031 does not open seller/broker/trustee/external portals.
- GP031 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Controlled packet assembly means private metadata assembly for owner review only.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.owner_action_receipt_readiness_checkpoint_service import (
    get_owner_action_receipt_readiness_checkpoint_payload,
)


PACK_ID = "VAULT_GP031"
PACK_NAME = "Controlled Packet Assembly Board"
SCHEMA_VERSION = "vault.controlled_packet_assembly_board.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

PACKET_ASSEMBLY_DEFINITIONS = [
    {
        "packet_id": "ATM_ROUTE_ACQUISITION_PACKET",
        "lane": "atm_route",
        "title": "ATM Route Acquisition Packet",
        "priority": 1,
        "tower_clearance_required": True,
    },
    {
        "packet_id": "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "lane": "apartment_lender",
        "title": "Apartment Lender / Due Diligence Packet",
        "priority": 2,
        "tower_clearance_required": True,
    },
    {
        "packet_id": "TRUST_ENTITY_AUTHORITY_PACKET",
        "lane": "trust_entity",
        "title": "Trust / Entity Authority Packet",
        "priority": 3,
        "tower_clearance_required": True,
    },
    {
        "packet_id": "OB_MANUAL_LIVE_PROOF_PACKET",
        "lane": "ob_manual_live",
        "title": "OB Manual Live Private Proof Packet",
        "priority": 4,
        "tower_clearance_required": True,
    },
    {
        "packet_id": "SOULAANA_ARTIST_IP_PACKET",
        "lane": "soulaana_ip",
        "title": "Soulaana Artist / IP Packet",
        "priority": 5,
        "tower_clearance_required": True,
    },
    {
        "packet_id": "PRIVATE_BETA_ONBOARDING_PACKET",
        "lane": "private_beta",
        "title": "Private Beta Onboarding Packet",
        "priority": 6,
        "tower_clearance_required": True,
    },
    {
        "packet_id": "OWNER_ACTION_RECEIPT_PACKET",
        "lane": "owner_action_receipts",
        "title": "Owner Action Receipt Packet",
        "priority": 7,
        "tower_clearance_required": True,
    },
]

COMPONENT_BLUEPRINTS = [
    {
        "component_type": "requirement_summary",
        "label": "Requirement summary",
        "required": True,
        "tower_owned": False,
    },
    {
        "component_type": "redacted_preview_slot",
        "label": "Redacted preview slot",
        "required": True,
        "tower_owned": False,
    },
    {
        "component_type": "receipt_chain_reference",
        "label": "Receipt chain reference",
        "required": True,
        "tower_owned": False,
    },
    {
        "component_type": "owner_action_reference",
        "label": "Owner action reference",
        "required": True,
        "tower_owned": False,
    },
    {
        "component_type": "tower_gate_status",
        "label": "Tower gate status",
        "required": True,
        "tower_owned": True,
    },
    {
        "component_type": "blocked_path_summary",
        "label": "Blocked path summary",
        "required": True,
        "tower_owned": False,
    },
    {
        "component_type": "carry_forward_marker",
        "label": "Carry-forward marker",
        "required": True,
        "tower_owned": False,
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault assembles packets but does not execute actions.",
    "NO_EXTERNAL_PACKET_DELIVERY": "External packet delivery is disabled.",
    "NO_PACKET_EXPORT": "Packet export is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Controlled packet assembly is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_controlled_packet_assembly_board_payload() -> Dict[str, Any]:
    gp030 = get_owner_action_receipt_readiness_checkpoint_payload()

    assembly_records = [
        _build_assembly_record(defn, gp030)
        for defn in PACKET_ASSEMBLY_DEFINITIONS
    ]

    component_rows = [
        component
        for record in assembly_records
        for component in record["component_rows"]
    ]

    lane_board = _build_lane_board(assembly_records, component_rows)
    blocker_wall = _build_blocker_wall(assembly_records, component_rows)
    readiness = _build_assembly_readiness(assembly_records, component_rows, blocker_wall)
    carry_forward = _build_carry_forward(assembly_records, readiness)
    owner_queue = _build_owner_queue(assembly_records, lane_board, blocker_wall, carry_forward)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "controlled_packet_assembly_board",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "assembly_truth": {
            "controlled_packet_assembly_enabled": True,
            "metadata_only": True,
            "private_assembly_only": True,
            "assembly_means_owner_review_not_delivery": True,
            "redacted_preview_slots_allowed": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp031",
            "safe_next_unlock": "GP032 can deepen packet component detail without unlocking raw storage, external delivery, public proof, portals, export, auto-run, or execution.",
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
        "assembly_summary": {
            "room_title": "Vault Controlled Packet Assembly Board",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/controlled-packet-assembly",
            "json_route": "/vault/controlled-packet-assembly.json",
            "records_route": "/vault/controlled-packet-assembly-records.json",
            "components_route": "/vault/controlled-packet-assembly-components.json",
            "lanes_route": "/vault/controlled-packet-assembly-lanes.json",
            "blockers_route": "/vault/controlled-packet-assembly-blockers.json",
            "readiness_route": "/vault/controlled-packet-assembly-readiness.json",
            "owner_queue_route": "/vault/controlled-packet-assembly-owner-queue.json",
            "carry_forward_route": "/vault/controlled-packet-assembly-carry-forward.json",
            "gp031_status_route": "/vault/gp031-status.json",
            "assembly_record_count": len(assembly_records),
            "component_row_count": len(component_rows),
            "lane_count": lane_board["lane_count"],
            "blocker_count": blocker_wall["blocker_count"],
            "readiness_item_count": readiness["readiness_item_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "owner_action_count": owner_queue["action_count"],
            "completed_count": 0,
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "assembly_records": assembly_records,
        "component_rows": component_rows,
        "lane_board": lane_board,
        "blocker_wall": blocker_wall,
        "assembly_readiness": readiness,
        "carry_forward": carry_forward,
        "owner_review_state": owner_queue,
        "gp030_connection": {
            "gp030_pack_id": gp030["pack"]["id"],
            "gp030_ready": gp030["gp030_status"]["ready"],
            "gp030_safe_to_continue": gp030["gp030_status"]["safe_to_continue_to_gp031"],
            "gp030_vault_done": gp030["gp030_status"]["vault_done"],
            "gp030_section_closed": gp030["gp030_status"]["section_closed_as_checkpoint"],
            "gp030_section_safe_to_continue": gp030["gp030_status"]["section_safe_to_continue"],
            "gp030_total_review_row_count": gp030["checkpoint_summary"]["total_review_row_count"],
        },
        "gp031_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "new_section_started": True,
            "section_id": SECTION_ID,
            "gp030_readiness_connected": True,
            "controlled_packet_assembly_board_ready": True,
            "safe_to_continue_to_gp032": True,
            "vault_done": False,
            "metadata_only_assembly": True,
            "private_assembly_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp031",
            "next_pack": "VAULT_GP032_PACKET_COMPONENT_DETAIL_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_assembly_record(defn: Dict[str, Any], gp030: Dict[str, Any]) -> Dict[str, Any]:
    blocked_codes = {
        "RAW_FILE_BODY_LOCKED",
        "DIRECT_UPLOAD_LOCKED",
        "PERMANENT_STORAGE_NOT_CONFIGURED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_EXPORT_LOCKED",
        "RAW_EXPORT_LOCKED",
        "PUBLIC_PROOF_LOCKED",
        "PUBLIC_PACKET_PROOF_LOCKED",
        "PORTAL_ACCESS_LOCKED",
        "TOWER_CLEARANCE_REQUIRED",
        "TOWER_STEP_UP_REQUIRED",
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
        "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY",
        "CLOUDS_PARKED",
    }

    assembly_id = f"VPA-{defn['priority']:03d}"
    component_rows = [
        _build_component_row(assembly_id, defn, component, index + 1)
        for index, component in enumerate(COMPONENT_BLUEPRINTS)
    ]

    return {
        "assembly_id": assembly_id,
        "packet_id": defn["packet_id"],
        "lane": defn["lane"],
        "title": defn["title"],
        "priority": defn["priority"],
        "source_checkpoint_id": gp030["pack"]["id"],
        "source_section": gp030["pack"]["section"],
        "assembly_status": "ASSEMBLY_BOARD_OPEN_OWNER_REVIEW",
        "metadata_only": True,
        "private_assembly_only": True,
        "owner_review_required": True,
        "owner_confirmation_required": True,
        "owner_reviewed": False,
        "owner_confirmed": False,
        "completed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "redacted_preview_slot_ready": True,
        "raw_body_included": False,
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
        "tower_clearance_required": defn["tower_clearance_required"],
        "tower_step_up_required": True,
        "component_rows": component_rows,
        "component_row_count": len(component_rows),
        "open_component_count": len(component_rows),
        "completed_component_count": 0,
        "blocked_component_count": len(component_rows),
        "ready_for_owner_review": True,
        "ready_for_external_delivery": False,
        "ready_for_export": False,
        "safe_to_carry_to_gp032": True,
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Assemble {defn['title']} as private metadata-only packet review. Do not export, share, upload raw bodies, or deliver externally.",
    }


def _build_component_row(
    assembly_id: str,
    defn: Dict[str, Any],
    component: Dict[str, Any],
    sequence: int,
) -> Dict[str, Any]:
    blocked_codes = {
        "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_COMPLETION",
        "NO_AUTO_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "NO_EXTERNAL_PACKET_DELIVERY",
        "NO_PACKET_EXPORT",
        "CLOUDS_PARKED",
    }

    if component["tower_owned"] or defn["tower_clearance_required"]:
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    if component["component_type"] == "redacted_preview_slot":
        blocked_codes.update({"RAW_FILE_BODY_LOCKED", "UNREDACTED_EXPORT_LOCKED", "RAW_EXPORT_LOCKED"})

    if component["component_type"] == "blocked_path_summary":
        blocked_codes.update({"DIRECT_UPLOAD_LOCKED", "EXTERNAL_ACCESS_DENIED", "PUBLIC_PACKET_PROOF_LOCKED", "PORTAL_ACCESS_LOCKED"})

    return {
        "component_id": f"VPC-{defn['priority']:03d}-{sequence:02d}",
        "assembly_id": assembly_id,
        "packet_id": defn["packet_id"],
        "lane": defn["lane"],
        "component_type": component["component_type"],
        "label": component["label"],
        "sequence": sequence,
        "required": component["required"],
        "tower_owned": component["tower_owned"],
        "status": "OPEN",
        "blocked": True,
        "completed": False,
        "auto_completed": False,
        "metadata_only": True,
        "redacted_preview_only": component["component_type"] == "redacted_preview_slot",
        "raw_body_available": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "public_packet_proof_allowed": False,
        "owner_review_required": True,
        "owner_confirmed": False,
        "can_execute_from_vault": False,
        "blocked_codes": sorted(blocked_codes),
    }


def _build_lane_board(assembly_records: List[Dict[str, Any]], component_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    lanes = []
    for record in assembly_records:
        lane_components = [row for row in component_rows if row["assembly_id"] == record["assembly_id"]]
        lanes.append(
            {
                "lane_id": f"assembly_lane_{record['lane']}",
                "packet_id": record["packet_id"],
                "title": record["title"],
                "lane": record["lane"],
                "priority": record["priority"],
                "assembly_id": record["assembly_id"],
                "lane_status": "OPEN_OWNER_REVIEW_REQUIRED",
                "component_count": len(lane_components),
                "open_component_count": sum(1 for row in lane_components if row["status"] == "OPEN"),
                "completed_component_count": 0,
                "blocked_component_count": sum(1 for row in lane_components if row["blocked"]),
                "metadata_only": True,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "public_packet_proof_allowed": False,
                "tower_clearance_required": record["tower_clearance_required"],
                "safe_to_carry_to_gp032": True,
            }
        )

    return {
        "lanes": lanes,
        "lane_count": len(lanes),
        "open_lane_count": len(lanes),
        "completed_lane_count": 0,
        "blocked_lane_count": sum(1 for lane in lanes if lane["blocked_component_count"] > 0),
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "all_lanes_metadata_only": True,
        "safe_to_continue_lane_board": True,
    }


def _build_blocker_wall(assembly_records: List[Dict[str, Any]], component_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted(
        {code for record in assembly_records for code in record["blocked_codes"]}
        | {code for row in component_rows for code in row["blocked_codes"]}
    )

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
            "affected_assembly_count": sum(1 for record in assembly_records if code in record["blocked_codes"]),
            "affected_component_count": sum(1 for row in component_rows if code in row["blocked_codes"]),
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
        "RAW_FILE_BODY_LOCKED": "Use metadata-only packet assembly. Do not display or store raw bodies.",
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
        "NO_AUTO_COMPLETION": "Do not auto-complete packet assembly.",
        "NO_AUTO_CONFIRMATION": "Do not auto-confirm owner actions.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault assembles packets but does not execute actions.",
        "NO_EXTERNAL_PACKET_DELIVERY": "Do not deliver packets externally.",
        "NO_PACKET_EXPORT": "Do not export packets.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "CONTROLLED_PACKET_ASSEMBLY_PRIVATE_ONLY": "Keep controlled packet assembly private.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP031.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_assembly_readiness(
    assembly_records: List[Dict[str, Any]],
    component_rows: List[Dict[str, Any]],
    blocker_wall: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "readiness_id": f"VPAR-{record['assembly_id'].replace('VPA-', '')}",
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "title": record["title"],
            "lane": record["lane"],
            "priority": record["priority"],
            "readiness_status": "READY_FOR_OWNER_REVIEW_EXTERNAL_DELIVERY_BLOCKED",
            "component_count": record["component_row_count"],
            "open_component_count": record["open_component_count"],
            "completed_component_count": 0,
            "blocked_component_count": record["blocked_component_count"],
            "owner_review_required": True,
            "owner_confirmed": False,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp032": True,
        }
        for record in assembly_records
    ]

    return {
        "readiness_items": items,
        "readiness_item_count": len(items),
        "ready_for_owner_review_count": len(items),
        "completed_count": 0,
        "owner_confirmed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "blocked_component_count": sum(record["blocked_component_count"] for record in assembly_records),
        "blocker_count": blocker_wall["blocker_count"],
        "safe_to_continue_to_gp032": True,
    }


def _build_carry_forward(
    assembly_records: List[Dict[str, Any]],
    readiness: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": f"VPA-CF-{record['assembly_id'].replace('VPA-', '')}",
            "assembly_id": record["assembly_id"],
            "packet_id": record["packet_id"],
            "title": record["title"],
            "lane": record["lane"],
            "carry_forward_status": "READY_FOR_GP032_PACKET_COMPONENT_DETAIL",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "completed_count": 0,
            "external_delivery_allowed": False,
            "packet_export_allowed": False,
            "public_packet_proof_allowed": False,
            "safe_to_carry_to_gp032": True,
        }
        for record in assembly_records
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_gp032_count": len(items),
        "owner_confirmed_count": 0,
        "completed_count": 0,
        "external_delivery_allowed_count": 0,
        "packet_export_allowed_count": 0,
        "public_packet_proof_allowed_count": 0,
        "safe_to_carry_to_gp032": True,
        "readiness_item_count": readiness["readiness_item_count"],
    }


def _build_owner_queue(
    assembly_records: List[Dict[str, Any]],
    lane_board: Dict[str, Any],
    blocker_wall: Dict[str, Any],
    carry_forward: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "CPA-ACTION-001",
            "label": "Review controlled packet assembly board.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CPA-ACTION-002",
            "label": "Review packet lanes without exporting or delivering externally.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CPA-ACTION-003",
            "label": "Keep raw storage, direct upload, export, external sharing, and portals locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CPA-ACTION-004",
            "label": "Keep packet assembly private and metadata-only.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "CPA-ACTION-005",
            "label": "Continue Vault into GP032 packet component detail.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Controlled Packet Assembly Board",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "actions": actions,
        "action_count": len(actions),
        "assembly_record_count": len(assembly_records),
        "lane_count": lane_board["lane_count"],
        "blocker_count": blocker_wall["blocker_count"],
        "carry_forward_count": carry_forward["carry_forward_count"],
        "ready_action_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "external_delivery_allowed": False,
        "packet_export_allowed": False,
        "public_packet_proof_allowed": False,
        "next_owner_actions": [
            "Review controlled packet assembly board.",
            "Review packet lanes without exporting or delivering externally.",
            "Keep raw storage, direct upload, export, external sharing, and portals locked.",
            "Keep packet assembly private and metadata-only.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP032 packet component detail.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_controlled_packet_assembly_board_payload())


def get_controlled_packet_assembly_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "assembly_truth": payload["assembly_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "assembly_summary": payload["assembly_summary"],
        "gp030_connection": payload["gp030_connection"],
    }


def get_controlled_packet_assembly_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "assembly_records": payload["assembly_records"],
        "assembly_record_count": len(payload["assembly_records"]),
    }


def get_controlled_packet_assembly_components() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "component_rows": payload["component_rows"],
        "component_row_count": len(payload["component_rows"]),
    }


def get_controlled_packet_assembly_lanes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "lane_board": payload["lane_board"],
    }


def get_controlled_packet_assembly_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_wall": payload["blocker_wall"],
    }


def get_controlled_packet_assembly_readiness() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "assembly_readiness": payload["assembly_readiness"],
    }


def get_controlled_packet_assembly_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_controlled_packet_assembly_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp031_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp031_status": payload["gp031_status"],
        "assembly_truth": payload["assembly_truth"],
        "assembly_summary": payload["assembly_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp030_connection": payload["gp030_connection"],
    }


def render_controlled_packet_assembly_page() -> str:
    payload = clone_payload()
    summary = payload["assembly_summary"]
    truth = payload["assembly_truth"]
    records = payload["assembly_records"]
    lanes = payload["lane_board"]
    owner = payload["owner_review_state"]

    record_cards = "\n".join(_render_assembly_card(record) for record in records)
    lane_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(lane['title'])}</strong>
            <span>{escape(lane['lane_status'])} · components: {lane['component_count']} · export: {str(lane['packet_export_allowed']).lower()}</span>
          </div>
          <div class="pill warn">Priority {lane['priority']}</div>
        </div>
        """
        for lane in lanes["lanes"]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Controlled Packet Assembly Board · GP031</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 031 · New Section</div>
        <h1>Controlled Packet Assembly Board</h1>
        <p class="hero-copy">
          GP031 starts the Controlled Packet Assembly Layer. Vault now groups packet assemblies for owner review:
          ATM route, apartment lender, trust/entity, OB private proof, Soulaana IP, private beta onboarding,
          and owner action receipts. This is metadata-only, private, redacted-preview-ready, and not external delivery.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary['assembly_record_count']}</strong>
            <span>assembly packets</span>
          </div>
          <div class="metric">
            <strong>{summary['component_row_count']}</strong>
            <span>component rows</span>
          </div>
          <div class="metric">
            <strong>{summary['lane_count']}</strong>
            <span>packet lanes</span>
          </div>
          <div class="metric">
            <strong>{str(truth['external_packet_delivery_enabled']).lower()}</strong>
            <span>external delivery</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">New section started</span>
          <span class="pill ok">Assembly board ready</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Export locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Assembly Records</h2>
      <p>
        Each packet is a private metadata assembly record with redacted preview slots only.
      </p>
      <div class="grid">
        {record_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Packet Lanes</h2>
        <p>All lanes are owner-review only. No export, no external delivery, no portals.</p>
        <div>
          {lane_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP031 prepares GP032 packet component detail.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP031 JSON Endpoints</h2>
      <p>
        <code>{escape(summary['json_route'])}</code>
        <code>{escape(summary['records_route'])}</code>
        <code>{escape(summary['components_route'])}</code>
        <code>{escape(summary['lanes_route'])}</code>
        <code>{escape(summary['blockers_route'])}</code>
        <code>{escape(summary['readiness_route'])}</code>
        <code>{escape(summary['owner_queue_route'])}</code>
        <code>{escape(summary['carry_forward_route'])}</code>
        <code>{escape(summary['gp031_status_route'])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Assembly Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth['metadata_only']).lower()}</code>.
        Packet export:
        <code>{str(truth['packet_export_enabled']).lower()}</code>.
        External delivery:
        <code>{str(truth['external_packet_delivery_enabled']).lower()}</code>.
        Clouds should continue:
        <code>{str(truth['clouds_should_continue']).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_assembly_card(record: Dict[str, Any]) -> str:
    status_class = "danger" if record["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record['title'])}</div>
            <div class="meta">
              Assembly: <code>{escape(record['assembly_id'])}</code><br>
              Packet: <code>{escape(record['packet_id'])}</code><br>
              Lane: {escape(record['lane'])}<br>
              Components: <code>{record['component_row_count']}</code><br>
              Export allowed: <code>{str(record['packet_export_allowed']).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(record['assembly_status'])}</span>
        </div>
      </article>
    """
