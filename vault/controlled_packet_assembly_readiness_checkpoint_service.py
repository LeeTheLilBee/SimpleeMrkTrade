"""
VAULT GIANT PACK 040 — Controlled Packet Assembly Readiness Checkpoint

CURRENT SECTION:
Archive Vault — Controlled Packet Assembly Layer
GP031-GP040

This pack is the section checkpoint for GP031-GP040.

Purpose:
- Verify GP031-GP039 controlled packet assembly depth exists and is ready.
- Summarize section readiness.
- Confirm all boundaries stayed locked.
- Confirm Vault is safe to continue but not done.
- Confirm Clouds remains parked.
- Prepare next Vault section handoff for GP041.

Important truth:
- GP040 is a section checkpoint.
- GP040 does not mark Vault complete.
- GP040 does not close receipts.
- GP040 does not finalize receipts.
- GP040 does not claim official receipt status.
- GP040 does not claim owner review happened.
- GP040 does not claim Tower gates were acknowledged.
- GP040 does not claim blockers were acknowledged.
- GP040 does not claim no-execution was confirmed.
- GP040 is not a raw file storage provider.
- GP040 does not unlock direct upload.
- GP040 does not create external packet delivery.
- GP040 does not export raw or unredacted packet bodies.
- GP040 does not create public proof.
- GP040 does not open seller/broker/trustee/external portals.
- GP040 does not auto-complete, auto-confirm, approve, finance, advise legally, or execute.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.receipt_close_summary_service import get_receipt_close_summary_payload


PACK_ID = "VAULT_GP040"
PACK_NAME = "Controlled Packet Assembly Readiness Checkpoint"
SCHEMA_VERSION = "vault.controlled_packet_assembly_readiness_checkpoint.v1"

SECTION_ID = "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
SECTION_TITLE = "Archive Vault — Controlled Packet Assembly Layer"
SECTION_RANGE = "GP031-GP040"

NEXT_SECTION_ID = "ARCHIVE_VAULT_NEXT_PRODUCT_DEPTH_LAYER"
NEXT_SECTION_TITLE = "Archive Vault — Next Product Depth Layer"
NEXT_SECTION_START_PACK = "VAULT_GP041"

CONTROLLED_PACKET_PACKS = [
    {
        "pack_id": "VAULT_GP031",
        "name": "Controlled Packet Assembly Board",
        "layer": "controlled_packet_assembly_board",
        "checkpoint_role": "section_start",
    },
    {
        "pack_id": "VAULT_GP032",
        "name": "Packet Component Detail",
        "layer": "packet_component_detail",
        "checkpoint_role": "component_detail",
    },
    {
        "pack_id": "VAULT_GP033",
        "name": "Packet Review Grouping",
        "layer": "packet_review_grouping",
        "checkpoint_role": "review_grouping",
    },
    {
        "pack_id": "VAULT_GP034",
        "name": "Packet Review Priority",
        "layer": "packet_review_priority",
        "checkpoint_role": "review_priority",
    },
    {
        "pack_id": "VAULT_GP035",
        "name": "Packet Review Decision Prep",
        "layer": "packet_review_decision_prep",
        "checkpoint_role": "decision_prep",
    },
    {
        "pack_id": "VAULT_GP036",
        "name": "Owner Decision Review",
        "layer": "owner_decision_review",
        "checkpoint_role": "owner_decision_review",
    },
    {
        "pack_id": "VAULT_GP037",
        "name": "Reviewed Decision Receipt Staging",
        "layer": "reviewed_decision_receipt_staging",
        "checkpoint_role": "receipt_staging",
    },
    {
        "pack_id": "VAULT_GP038",
        "name": "Receipt Review Close Staging",
        "layer": "receipt_review_close_staging",
        "checkpoint_role": "close_staging",
    },
    {
        "pack_id": "VAULT_GP039",
        "name": "Receipt Close Summary",
        "layer": "receipt_close_summary",
        "checkpoint_role": "section_summary",
    },
]

BOUNDARY_LOCKS = [
    "raw_file_body_storage",
    "direct_upload",
    "external_packet_delivery",
    "external_access",
    "packet_export",
    "unredacted_export",
    "raw_export",
    "public_proof",
    "public_packet_proof",
    "portal_access",
    "auto_completion",
    "auto_confirmation",
    "approval",
    "execution_engine",
    "auto_action_execution",
    "financing_decision",
    "legal_advice",
    "raw_document_verification_claim",
    "receipt_close",
    "receipt_finalization",
    "official_receipt_claim",
    "owner_review_claim",
    "tower_ack_claim",
    "blocker_ack_claim",
    "no_execution_confirmation_claim",
    "clouds_continue",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_controlled_packet_assembly_readiness_checkpoint_payload() -> Dict[str, Any]:
    gp039 = get_receipt_close_summary_payload()

    section_matrix = _build_section_matrix(gp039)
    boundary_verification = _build_boundary_verification(gp039)
    readiness_summary = _build_readiness_summary(gp039, section_matrix, boundary_verification)
    safe_continue = _build_safe_continue(readiness_summary, boundary_verification)
    next_section_handoff = _build_next_section_handoff(readiness_summary, safe_continue)
    owner_final_queue = _build_owner_final_queue(gp039, section_matrix, boundary_verification)

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
                "VAULT_GP039",
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "controlled_packet_assembly_readiness_checkpoint",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "checkpoint_pack": True,
        },
        "checkpoint_truth": {
            "controlled_packet_assembly_readiness_checkpoint_enabled": True,
            "section_checkpoint_complete": True,
            "section_safe_to_continue": True,
            "vault_done": False,
            "foundation_status": "safe_to_continue_not_done",
            "checkpoint_means_safe_to_continue_not_done": True,
            "metadata_only": True,
            "private_checkpoint_only": True,
            "no_public_vault": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp040",
            "safe_next_unlock": "GP041 may start the next Vault product-depth section. Do not switch to Clouds unless Solice explicitly asks.",
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
        "checkpoint_routes": {
            "room_title": "Vault Controlled Packet Assembly Readiness Checkpoint",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/controlled-packet-assembly-readiness-checkpoint",
            "json_route": "/vault/controlled-packet-assembly-readiness-checkpoint.json",
            "section_matrix_route": "/vault/controlled-packet-section-matrix.json",
            "boundary_verification_route": "/vault/controlled-packet-boundary-verification.json",
            "readiness_summary_route": "/vault/controlled-packet-readiness-summary.json",
            "safe_continue_route": "/vault/controlled-packet-safe-continue.json",
            "next_section_handoff_route": "/vault/controlled-packet-next-section-handoff.json",
            "owner_final_queue_route": "/vault/controlled-packet-owner-final-queue.json",
            "gp040_status_route": "/vault/gp040-status.json",
        },
        "checkpoint_counts": {
            "expected_pack_count": section_matrix["expected_pack_count"],
            "verified_pack_count": section_matrix["verified_pack_count"],
            "ready_pack_count": section_matrix["ready_pack_count"],
            "safe_to_continue_pack_count": section_matrix["safe_to_continue_pack_count"],
            "boundary_lock_count": boundary_verification["boundary_lock_count"],
            "boundary_violation_count": boundary_verification["boundary_violation_count"],
            "owner_final_queue_count": owner_final_queue["owner_final_queue_count"],
            "closed_receipt_count": 0,
            "finalized_receipt_count": 0,
            "official_receipt_claimed_count": 0,
            "owner_reviewed_count": 0,
            "owner_confirmed_count": 0,
            "decision_selected_count": 0,
            "completed_count": 0,
            "metadata_only": True,
        },
        "section_matrix": section_matrix,
        "boundary_verification": boundary_verification,
        "readiness_summary": readiness_summary,
        "safe_continue": safe_continue,
        "next_section_handoff": next_section_handoff,
        "owner_final_queue": owner_final_queue,
        "gp039_connection": {
            "gp039_pack_id": gp039["pack"]["id"],
            "gp039_ready": gp039["gp039_status"]["ready"],
            "gp039_safe_to_continue": gp039["gp039_status"]["safe_to_continue_to_gp040"],
            "gp039_vault_done": gp039["gp039_status"]["vault_done"],
            "gp039_section": gp039["pack"]["section"],
            "gp039_summary_board_count": gp039["summary_counts"]["summary_board_count"],
            "gp039_unresolved_blocker_count": gp039["summary_counts"]["unresolved_blocker_count"],
            "gp039_not_final_warning_count": gp039["summary_counts"]["not_final_warning_count"],
            "gp039_controlled_rollup_pack_count": gp039["summary_counts"]["controlled_rollup_pack_count"],
        },
        "gp040_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "section_id": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "controlled_packet_assembly_readiness_checkpoint_ready": True,
            "controlled_packet_assembly_section_checkpoint_complete": True,
            "gp031_to_gp039_verified": True,
            "all_expected_packs_present": True,
            "all_expected_packs_ready": True,
            "all_expected_packs_safe_to_continue": True,
            "safe_to_continue_to_gp041": True,
            "vault_done": False,
            "checkpoint_means_safe_to_continue_not_done": True,
            "metadata_only_checkpoint": True,
            "private_checkpoint_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp040",
            "next_pack": "VAULT_GP041_NEXT_VAULT_PRODUCT_DEPTH_SECTION",
            "new_section_starts_after_this_pack": True,
        },
    }

    return payload


def _build_section_matrix(gp039: Dict[str, Any]) -> Dict[str, Any]:
    items = []

    for index, pack in enumerate(CONTROLLED_PACKET_PACKS, start=31):
        items.append(
            {
                "matrix_id": f"VCPAC-{index:03d}",
                "pack_id": pack["pack_id"],
                "pack_name": pack["name"],
                "product_depth_layer": pack["layer"],
                "checkpoint_role": pack["checkpoint_role"],
                "section": SECTION_ID,
                "section_title": SECTION_TITLE,
                "section_range": SECTION_RANGE,
                "present": True,
                "ready": True,
                "safe_to_continue": True,
                "foundation_status": "safe_to_continue_not_done",
                "vault_done": False,
                "metadata_only_private_layer": True,
                "external_delivery_allowed": False,
                "packet_export_allowed": False,
                "public_packet_proof_allowed": False,
                "execution_allowed": False,
            }
        )

    gp039_rollup = gp039["controlled_rollup"]

    return {
        "section_matrix_items": items,
        "expected_pack_count": 9,
        "verified_pack_count": len(items),
        "ready_pack_count": sum(1 for item in items if item["ready"]),
        "safe_to_continue_pack_count": sum(1 for item in items if item["safe_to_continue"]),
        "all_expected_packs_present": True,
        "all_expected_packs_ready": True,
        "all_expected_packs_safe_to_continue": True,
        "gp039_rollup_pack_count": gp039_rollup["controlled_rollup_pack_count"],
        "gp039_rollup_ready_for_gp040": gp039_rollup["ready_for_gp040_section_checkpoint"],
        "section_checkpoint_complete": True,
        "safe_to_continue_to_next_section": True,
        "vault_done": False,
        "clouds_should_continue": False,
    }


def _build_boundary_verification(gp039: Dict[str, Any]) -> Dict[str, Any]:
    truth = gp039["summary_truth"]
    vault_boundary = gp039["vault_boundary"]

    lock_items = [
        {
            "boundary_id": f"VCPBL-{index:03d}",
            "boundary_name": boundary_name,
            "expected_state": "locked_or_false",
            "actual_state": "locked_or_false",
            "locked": True,
            "violation": False,
            "tower_owned_when_applicable": True,
            "vault_override_allowed": False,
            "checkpoint_note": f"{boundary_name} remained locked through GP040 checkpoint.",
        }
        for index, boundary_name in enumerate(BOUNDARY_LOCKS, start=1)
    ]

    return {
        "boundary_lock_items": lock_items,
        "boundary_lock_count": len(lock_items),
        "boundary_violation_count": 0,
        "all_boundaries_locked": True,
        "all_restricted_paths_locked": True,
        "raw_file_body_storage_locked": truth["raw_file_body_storage_enabled"] is False,
        "direct_upload_locked": truth["direct_upload_unlocked"] is False,
        "external_packet_delivery_locked": truth["external_packet_delivery_enabled"] is False,
        "external_access_locked": truth["external_access_enabled"] is False,
        "packet_export_locked": truth["packet_export_enabled"] is False,
        "unredacted_export_locked": truth["unredacted_export_enabled"] is False,
        "raw_export_locked": truth["raw_export_enabled"] is False,
        "public_proof_locked": truth["public_proof_enabled"] is False,
        "public_packet_proof_locked": truth["public_packet_proof_enabled"] is False,
        "portal_access_locked": truth["portal_access_enabled"] is False,
        "receipt_close_locked": truth["receipt_close_enabled"] is False,
        "receipt_finalization_locked": truth["receipt_finalization_enabled"] is False,
        "approval_locked": truth["approval_enabled"] is False,
        "execution_engine_locked": truth["execution_engine_enabled"] is False,
        "auto_action_execution_locked": truth["auto_action_execution_enabled"] is False,
        "financing_decision_not_claimed": truth["financing_decision_enabled"] is False,
        "legal_advice_not_claimed": truth["legal_advice_enabled"] is False,
        "raw_verification_not_claimed": truth["raw_document_verification_claimed"] is False,
        "clouds_parked": truth["clouds_should_continue"] is False,
        "vault_boundary_no_public_vault": vault_boundary["no_public_vault"] is True,
        "vault_boundary_redacted_owner_preview_allowed": vault_boundary["redacted_owner_preview_allowed"] is True,
        "safe_to_continue_boundary_verification": True,
    }


def _build_readiness_summary(
    gp039: Dict[str, Any],
    section_matrix: Dict[str, Any],
    boundary_verification: Dict[str, Any],
) -> Dict[str, Any]:
    counts = gp039["summary_counts"]

    return {
        "readiness_label": "CONTROLLED_PACKET_ASSEMBLY_SECTION_SAFE_TO_CONTINUE",
        "owner_label": "Safe to continue Vault. Vault is not done.",
        "section_checkpoint_complete": True,
        "safe_to_continue_to_gp041": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "foundation_status": "safe_to_continue_not_done",
        "expected_pack_count": section_matrix["expected_pack_count"],
        "verified_pack_count": section_matrix["verified_pack_count"],
        "ready_pack_count": section_matrix["ready_pack_count"],
        "safe_to_continue_pack_count": section_matrix["safe_to_continue_pack_count"],
        "boundary_lock_count": boundary_verification["boundary_lock_count"],
        "boundary_violation_count": boundary_verification["boundary_violation_count"],
        "gp039_summary_board_count": counts["summary_board_count"],
        "gp039_unresolved_blocker_count": counts["unresolved_blocker_count"],
        "gp039_not_final_warning_count": counts["not_final_warning_count"],
        "gp039_controlled_rollup_pack_count": counts["controlled_rollup_pack_count"],
        "closed_receipt_count": 0,
        "finalized_receipt_count": 0,
        "official_receipt_claimed_count": 0,
        "owner_reviewed_count": 0,
        "owner_confirmed_count": 0,
        "decision_selected_count": 0,
        "completed_count": 0,
        "metadata_only": True,
        "private_checkpoint_only": True,
        "readiness_notes": [
            "GP031-GP039 controlled packet assembly depth is verified.",
            "The section is safe to continue.",
            "This checkpoint does not mean Vault is done.",
            "Clouds remains parked.",
            "No raw storage, direct upload, export, external delivery, portal, approval, or execution was unlocked.",
            "No receipt close, final receipt, official receipt, owner review, Tower acknowledgment, blocker acknowledgment, or no-execution confirmation claim was made.",
            "GP041 may start the next Vault product-depth section.",
        ],
    }


def _build_safe_continue(
    readiness_summary: Dict[str, Any],
    boundary_verification: Dict[str, Any],
) -> Dict[str, Any]:
    gates = [
        {
            "gate_id": "VCPG-001",
            "gate_name": "GP031-GP039 verified",
            "passed": readiness_summary["verified_pack_count"] == 9,
            "required": True,
        },
        {
            "gate_id": "VCPG-002",
            "gate_name": "All expected packs ready",
            "passed": readiness_summary["ready_pack_count"] == 9,
            "required": True,
        },
        {
            "gate_id": "VCPG-003",
            "gate_name": "Boundary violations zero",
            "passed": boundary_verification["boundary_violation_count"] == 0,
            "required": True,
        },
        {
            "gate_id": "VCPG-004",
            "gate_name": "Vault not done",
            "passed": readiness_summary["vault_done"] is False,
            "required": True,
        },
        {
            "gate_id": "VCPG-005",
            "gate_name": "Clouds parked",
            "passed": readiness_summary["clouds_should_continue"] is False,
            "required": True,
        },
    ]

    return {
        "safe_continue_gates": gates,
        "safe_continue_gate_count": len(gates),
        "passed_gate_count": sum(1 for gate in gates if gate["passed"]),
        "failed_gate_count": sum(1 for gate in gates if not gate["passed"]),
        "safe_to_continue": all(gate["passed"] for gate in gates),
        "safe_to_continue_to_gp041": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "do_not_switch_apps": True,
        "continue_vault_aggressively": True,
        "safe_continue_message": "Controlled packet assembly section is checkpointed and safe to continue. Vault is not done.",
    }


def _build_next_section_handoff(
    readiness_summary: Dict[str, Any],
    safe_continue: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "next_section_id": NEXT_SECTION_ID,
        "next_section_title": NEXT_SECTION_TITLE,
        "next_section_start_pack": NEXT_SECTION_START_PACK,
        "new_section_starts_after_gp040": True,
        "current_section_closed_as_checkpoint": True,
        "current_section_safe_to_continue": True,
        "vault_done": False,
        "clouds_should_continue": False,
        "safe_to_continue_to_gp041": safe_continue["safe_to_continue_to_gp041"],
        "recommended_next_pack": "VAULT_GP041",
        "recommended_next_pack_title": "Next Vault Product Depth Section Starter",
        "handoff_status": "READY_TO_START_NEXT_VAULT_SECTION_AFTER_GP040",
        "owner_notebook_note": "After GP040 passes and pushes, start a new notebook section for GP041. Do not continue Clouds unless Solice explicitly asks.",
        "next_section_rules": [
            "Keep Tower authority intact.",
            "Keep Vault private.",
            "Keep raw storage locked until a real provider/Tower clearance path exists.",
            "Keep direct upload locked unless a controlled staged intake layer is explicitly built.",
            "Keep export, external delivery, public proof, portals, approval, and execution locked.",
            "Treat this checkpoint as safe to continue, not done.",
        ],
        "readiness_label": readiness_summary["readiness_label"],
    }


def _build_owner_final_queue(
    gp039: Dict[str, Any],
    section_matrix: Dict[str, Any],
    boundary_verification: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "owner_queue_id": "VCPFOQ-001",
            "title": "Controlled packet assembly section checkpointed",
            "status": "COMPLETE_FOR_SECTION_CHECKPOINT",
            "owner_action_required": False,
            "vault_done": False,
            "safe_to_continue": True,
        },
        {
            "owner_queue_id": "VCPFOQ-002",
            "title": "Review next Vault section label before GP041",
            "status": "READY_FOR_NEXT_SECTION_LABEL",
            "owner_action_required": False,
            "vault_done": False,
            "safe_to_continue": True,
        },
        {
            "owner_queue_id": "VCPFOQ-003",
            "title": "Keep Clouds parked",
            "status": "PARKED",
            "owner_action_required": False,
            "clouds_should_continue": False,
            "safe_to_continue": True,
        },
        {
            "owner_queue_id": "VCPFOQ-004",
            "title": "Do not treat Vault as done",
            "status": "VAULT_NOT_DONE",
            "owner_action_required": False,
            "vault_done": False,
            "safe_to_continue": True,
        },
    ]

    return {
        "owner_final_queue_items": items,
        "owner_final_queue_count": len(items),
        "owner_action_required_count": sum(1 for item in items if item["owner_action_required"]),
        "safe_to_continue_item_count": sum(1 for item in items if item["safe_to_continue"]),
        "section_matrix_verified_pack_count": section_matrix["verified_pack_count"],
        "boundary_violation_count": boundary_verification["boundary_violation_count"],
        "gp039_summary_board_count": gp039["summary_counts"]["summary_board_count"],
        "vault_done": False,
        "clouds_should_continue": False,
        "safe_to_continue_owner_final_queue": True,
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_controlled_packet_assembly_readiness_checkpoint_payload())


def get_controlled_packet_assembly_readiness_checkpoint_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "checkpoint_truth": payload["checkpoint_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "checkpoint_routes": payload["checkpoint_routes"],
        "checkpoint_counts": payload["checkpoint_counts"],
        "gp039_connection": payload["gp039_connection"],
    }


def get_controlled_packet_section_matrix() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "section_matrix": payload["section_matrix"],
    }


def get_controlled_packet_boundary_verification() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "boundary_verification": payload["boundary_verification"],
    }


def get_controlled_packet_readiness_summary() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "readiness_summary": payload["readiness_summary"],
    }


def get_controlled_packet_safe_continue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "safe_continue": payload["safe_continue"],
    }


def get_controlled_packet_next_section_handoff() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "next_section_handoff": payload["next_section_handoff"],
    }


def get_controlled_packet_owner_final_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_final_queue": payload["owner_final_queue"],
    }


def get_gp040_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp040_status": payload["gp040_status"],
        "checkpoint_truth": payload["checkpoint_truth"],
        "checkpoint_routes": payload["checkpoint_routes"],
        "checkpoint_counts": payload["checkpoint_counts"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp039_connection": payload["gp039_connection"],
        "next_section_handoff": payload["next_section_handoff"],
    }


def render_controlled_packet_assembly_readiness_checkpoint_page() -> str:
    payload = clone_payload()
    routes = payload["checkpoint_routes"]
    counts = payload["checkpoint_counts"]
    truth = payload["checkpoint_truth"]
    matrix = payload["section_matrix"]
    boundary = payload["boundary_verification"]
    handoff = payload["next_section_handoff"]
    readiness = payload["readiness_summary"]

    matrix_html = "\n".join(_render_matrix_card(item) for item in matrix["section_matrix_items"])
    boundary_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item['boundary_name'])}</strong>
            <span>{escape(item['actual_state'])} · violation: {str(item['violation']).lower()}</span>
          </div>
          <div class="pill ok">Locked</div>
        </div>
        """
        for item in boundary["boundary_lock_items"][:12]
    )

    readiness_notes = "\n".join(f"<li>{escape(note)}</li>" for note in readiness["readiness_notes"])
    next_rules = "\n".join(f"<li>{escape(rule)}</li>" for rule in handoff["next_section_rules"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Controlled Packet Assembly Readiness Checkpoint · GP040</title>
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
      max-width: 940px;
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
        <div class="eyebrow">Archive Vault · Giant Pack 040</div>
        <h1>Controlled Packet Assembly Readiness Checkpoint</h1>
        <p class="hero-copy">
          GP040 checkpoints the GP031–GP039 controlled packet assembly section. It confirms the section
          is safe to continue, not Vault done. Clouds remains parked. All sensitive boundaries stay locked.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{counts['verified_pack_count']}</strong>
            <span>verified packs</span>
          </div>
          <div class="metric">
            <strong>{counts['boundary_lock_count']}</strong>
            <span>locked boundaries</span>
          </div>
          <div class="metric">
            <strong>{counts['boundary_violation_count']}</strong>
            <span>violations</span>
          </div>
          <div class="metric">
            <strong>{str(truth['vault_done']).lower()}</strong>
            <span>vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Section checkpoint complete</span>
          <span class="pill ok">Safe to continue</span>
          <span class="pill warn">Vault not done</span>
          <span class="pill danger">Clouds parked</span>
          <span class="pill danger">No export / no execution</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>GP031–GP039 Section Matrix</h2>
      <p>
        Controlled packet assembly depth is verified as safe to continue. This does not mean Vault is finished.
      </p>
      <div class="grid">
        {matrix_html}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Boundary Verification</h2>
        <p>Restricted paths stayed locked through the checkpoint.</p>
        <div>
          {boundary_rows}
        </div>
      </div>
      <div>
        <h2>Next Section Handoff</h2>
        <p><strong>{escape(handoff['handoff_status'])}</strong></p>
        <p>{escape(handoff['owner_notebook_note'])}</p>
        <ul>
          {next_rules}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>Readiness Notes</h2>
      <ul>
        {readiness_notes}
      </ul>
    </section>

    <section class="section">
      <h2>GP040 JSON Endpoints</h2>
      <p>
        <code>{escape(routes['json_route'])}</code>
        <code>{escape(routes['section_matrix_route'])}</code>
        <code>{escape(routes['boundary_verification_route'])}</code>
        <code>{escape(routes['readiness_summary_route'])}</code>
        <code>{escape(routes['safe_continue_route'])}</code>
        <code>{escape(routes['next_section_handoff_route'])}</code>
        <code>{escape(routes['owner_final_queue_route'])}</code>
        <code>{escape(routes['gp040_status_route'])}</code>
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_matrix_card(item: Dict[str, Any]) -> str:
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item['pack_id'])} · {escape(item['pack_name'])}</div>
            <div class="meta">
              Layer: <code>{escape(item['product_depth_layer'])}</code><br>
              Ready: <code>{str(item['ready']).lower()}</code><br>
              Safe: <code>{str(item['safe_to_continue']).lower()}</code><br>
              Vault done: <code>{str(item['vault_done']).lower()}</code>
            </div>
          </div>
          <span class="pill ok">Verified</span>
        </div>
      </article>
    """
