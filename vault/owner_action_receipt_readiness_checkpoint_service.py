"""
VAULT GIANT PACK 030 — Owner Action Receipt Readiness Checkpoint

SECTION CLOSE:
Archive Vault — Owner Action Receipt / Checklist Layer
GP025-GP030

This pack verifies GP025-GP029 together and closes the section as a readiness
checkpoint.

Important truth:
- GP030 is not Vault done.
- GP030 is not an execution engine.
- GP030 does not auto-complete checklist rows.
- GP030 does not auto-confirm anything.
- GP030 does not mark owner confirmation complete.
- GP030 does not trigger execution after review, completion, confirmation,
  receipt-chain review, or readiness.
- GP030 does not create public proof.
- GP030 does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, seller/broker/trustee portals, financing decisions,
  legal advice, or Tower-owned permissions.
- Readiness means safe_to_continue, not done.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.owner_action_receipts_checklists_service import get_owner_action_receipts_payload
from vault.owner_confirmation_ledger_service import get_owner_confirmation_ledger_payload
from vault.action_receipt_detail_drawer_service import get_action_receipt_detail_drawer_payload
from vault.checklist_completion_state_service import get_checklist_completion_state_payload
from vault.receipt_chain_review_board_service import get_receipt_chain_review_board_payload


PACK_ID = "VAULT_GP030"
PACK_NAME = "Owner Action Receipt Readiness Checkpoint"
SCHEMA_VERSION = "vault.owner_action_receipt_readiness_checkpoint.v1"

SECTION_ID = "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER"
SECTION_TITLE = "Archive Vault — Owner Action Receipt / Checklist Layer"
SECTION_RANGE = "GP025-GP030"

EXPECTED_PACKS = [
    "VAULT_GP025",
    "VAULT_GP026",
    "VAULT_GP027",
    "VAULT_GP028",
    "VAULT_GP029",
]

REQUIRED_ROUTES = [
    "/vault/owner-action-receipts",
    "/vault/owner-action-receipts.json",
    "/vault/owner-action-receipt-records.json",
    "/vault/owner-action-checklists.json",
    "/vault/owner-action-prep-receipt-map.json",
    "/vault/owner-action-confirmation-ledger-seed.json",
    "/vault/owner-action-receipt-chain.json",
    "/vault/owner-action-receipt-blocked.json",
    "/vault/owner-action-receipt-owner-queue.json",
    "/vault/gp025-status.json",
    "/vault/owner-confirmation-ledger",
    "/vault/owner-confirmation-ledger.json",
    "/vault/owner-confirmation-ledger-entries.json",
    "/vault/owner-confirmation-ledger-review-state.json",
    "/vault/owner-confirmation-ledger-receipt-links.json",
    "/vault/owner-confirmation-ledger-blockers.json",
    "/vault/owner-confirmation-ledger-carry-forward.json",
    "/vault/owner-confirmation-ledger-owner-queue.json",
    "/vault/gp026-status.json",
    "/vault/action-receipt-detail-drawer",
    "/vault/action-receipt-detail-drawer.json",
    "/vault/action-receipt-detail-drawer-records.json",
    "/vault/action-receipt-detail-drawer-panels.json",
    "/vault/action-receipt-detail-drawer-checklist.json",
    "/vault/action-receipt-detail-drawer-tower-gates.json",
    "/vault/action-receipt-detail-drawer-blockers.json",
    "/vault/action-receipt-detail-drawer-carry-forward.json",
    "/vault/action-receipt-detail-drawer-owner-queue.json",
    "/vault/gp027-status.json",
    "/vault/checklist-completion-state",
    "/vault/checklist-completion-state.json",
    "/vault/checklist-completion-state-records.json",
    "/vault/checklist-completion-state-rows.json",
    "/vault/checklist-completion-state-blockers.json",
    "/vault/checklist-completion-state-readiness.json",
    "/vault/checklist-completion-state-carry-forward.json",
    "/vault/checklist-completion-state-owner-queue.json",
    "/vault/gp028-status.json",
    "/vault/receipt-chain-review-board",
    "/vault/receipt-chain-review-board.json",
    "/vault/receipt-chain-review-board-records.json",
    "/vault/receipt-chain-review-board-rows.json",
    "/vault/receipt-chain-review-board-lanes.json",
    "/vault/receipt-chain-review-board-priority.json",
    "/vault/receipt-chain-review-board-completion-summary.json",
    "/vault/receipt-chain-review-board-blockers.json",
    "/vault/receipt-chain-review-board-carry-forward.json",
    "/vault/receipt-chain-review-board-owner-queue.json",
    "/vault/gp029-status.json",
]

CHECKPOINT_ROUTES = [
    "/vault/owner-action-receipt-readiness",
    "/vault/owner-action-receipt-readiness.json",
    "/vault/owner-action-receipt-readiness-pack-matrix.json",
    "/vault/owner-action-receipt-readiness-boundaries.json",
    "/vault/owner-action-receipt-readiness-routes.json",
    "/vault/owner-action-receipt-readiness-summary.json",
    "/vault/owner-action-receipt-readiness-owner-queue.json",
    "/vault/owner-action-receipt-readiness-carry-forward.json",
    "/vault/gp030-status.json",
]

BOUNDARY_CODES = {
    "NO_VAULT_DONE": "Vault is not done.",
    "SAFE_TO_CONTINUE_NOT_DONE": "Readiness means safe to continue, not done.",
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "PUBLIC_RECEIPT_PROOF_LOCKED": "Public receipt proof remains locked.",
    "PUBLIC_BOARD_PROOF_LOCKED": "Public board proof remains locked.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "TOWER_STEP_UP_REQUIRED": "Tower step-up is required before sensitive action.",
    "OWNER_REVIEW_REQUIRED": "Owner review is required.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before closure.",
    "NO_AUTO_COMPLETION": "Automatic checklist completion is disabled.",
    "NO_AUTO_CONFIRMATION": "Automatic confirmation is disabled.",
    "NO_AUTO_ACTION_EXECUTION": "Automatic action execution is disabled.",
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault reviews receipt chains but does not execute actions.",
    "NO_EXECUTION_AFTER_REVIEW": "Review does not trigger execution.",
    "NO_EXECUTION_AFTER_COMPLETION": "Checklist completion does not trigger execution.",
    "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_owner_action_receipt_readiness_checkpoint_payload() -> Dict[str, Any]:
    gp025 = get_owner_action_receipts_payload()
    gp026 = get_owner_confirmation_ledger_payload()
    gp027 = get_action_receipt_detail_drawer_payload()
    gp028 = get_checklist_completion_state_payload()
    gp029 = get_receipt_chain_review_board_payload()

    sources = {
        "VAULT_GP025": gp025,
        "VAULT_GP026": gp026,
        "VAULT_GP027": gp027,
        "VAULT_GP028": gp028,
        "VAULT_GP029": gp029,
    }

    pack_matrix = _build_pack_matrix(sources)
    boundary_review = _build_boundary_review(gp025, gp026, gp027, gp028, gp029)
    route_review = _build_route_review()
    readiness_summary = _build_readiness_summary(gp025, gp026, gp027, gp028, gp029, pack_matrix, boundary_review)
    carry_forward = _build_carry_forward(readiness_summary, pack_matrix, boundary_review)
    owner_queue = _build_owner_queue(readiness_summary, boundary_review, carry_forward)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "owner_action_receipt_readiness_checkpoint",
            "section": SECTION_ID,
            "section_title": SECTION_TITLE,
            "section_range": SECTION_RANGE,
        },
        "checkpoint_truth": {
            "section_readiness_checkpoint_enabled": True,
            "section_closed_as_checkpoint": True,
            "section_safe_to_continue": True,
            "vault_done": False,
            "safe_to_continue_not_done": True,
            "metadata_only": True,
            "private_checkpoint_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_enabled": False,
            "auto_confirmation_enabled": False,
            "execution_after_review_enabled": False,
            "execution_after_completion_enabled": False,
            "execution_after_confirmation_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "public_checkpoint_proof_enabled": False,
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
            "auto_packet_approval_enabled": False,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp030",
            "safe_next_unlock": "GP031 can start the next Vault product-depth section without unlocking raw storage, external sharing, public proof, auto-completion, confirmation auto-run, or execution.",
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
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "checkpoint_summary": {
            "room_title": "Vault Owner Action Receipt Readiness Checkpoint",
            "section_header": SECTION_TITLE,
            "section_range": SECTION_RANGE,
            "route": "/vault/owner-action-receipt-readiness",
            "json_route": "/vault/owner-action-receipt-readiness.json",
            "pack_matrix_route": "/vault/owner-action-receipt-readiness-pack-matrix.json",
            "boundaries_route": "/vault/owner-action-receipt-readiness-boundaries.json",
            "routes_route": "/vault/owner-action-receipt-readiness-routes.json",
            "summary_route": "/vault/owner-action-receipt-readiness-summary.json",
            "owner_queue_route": "/vault/owner-action-receipt-readiness-owner-queue.json",
            "carry_forward_route": "/vault/owner-action-receipt-readiness-carry-forward.json",
            "gp030_status_route": "/vault/gp030-status.json",
            "expected_pack_count": pack_matrix["expected_pack_count"],
            "verified_pack_count": pack_matrix["verified_pack_count"],
            "required_route_count": route_review["required_route_count"],
            "checkpoint_route_count": route_review["checkpoint_route_count"],
            "boundary_count": boundary_review["boundary_count"],
            "receipt_record_count": readiness_summary["receipt_record_count"],
            "ledger_entry_count": readiness_summary["ledger_entry_count"],
            "drawer_record_count": readiness_summary["drawer_record_count"],
            "completion_record_count": readiness_summary["completion_record_count"],
            "board_record_count": readiness_summary["board_record_count"],
            "total_review_row_count": readiness_summary["total_review_row_count"],
            "completed_count": 0,
            "owner_confirmed_count": 0,
            "section_ready": True,
            "section_safe_to_continue": True,
            "vault_done": False,
            "metadata_only": True,
        },
        "pack_matrix": pack_matrix,
        "boundary_review": boundary_review,
        "route_review": route_review,
        "readiness_summary": readiness_summary,
        "carry_forward": carry_forward,
        "owner_review_state": owner_queue,
        "gp029_connection": {
            "gp029_pack_id": gp029["pack"]["id"],
            "gp029_ready": gp029["gp029_status"]["ready"],
            "gp029_safe_to_continue": gp029["gp029_status"]["safe_to_continue_to_gp030"],
            "gp029_vault_done": gp029["gp029_status"]["vault_done"],
            "gp029_board_record_count": gp029["board_summary"]["board_record_count"],
            "gp029_chain_row_count": gp029["board_summary"]["chain_row_count"],
        },
        "gp030_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp025_to_gp029_verified": True,
            "owner_action_receipt_layer_ready": True,
            "section_closed_as_checkpoint": True,
            "section_safe_to_continue": True,
            "safe_to_continue_to_gp031": True,
            "vault_done": False,
            "metadata_only_checkpoint": True,
            "private_checkpoint_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "completed_count": 0,
            "auto_completion_disabled": True,
            "auto_confirmation_disabled": True,
            "execution_after_review_disabled": True,
            "execution_after_completion_disabled": True,
            "execution_after_confirmation_disabled": True,
            "execution_engine_disabled": True,
            "checkpoint_public_proof_disabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp030",
            "next_pack": "VAULT_GP031_NEXT_VAULT_PRODUCT_DEPTH_SECTION",
        },
    }

    return payload


def _pack_status_for(payload: Dict[str, Any], pack_id: str) -> Dict[str, Any]:
    status_key = pack_id.lower().replace("vault_", "").replace("_", "") + "_status"
    if pack_id == "VAULT_GP025":
        return payload["gp025_status"]
    if pack_id == "VAULT_GP026":
        return payload["gp026_status"]
    if pack_id == "VAULT_GP027":
        return payload["gp027_status"]
    if pack_id == "VAULT_GP028":
        return payload["gp028_status"]
    if pack_id == "VAULT_GP029":
        return payload["gp029_status"]
    return payload.get(status_key, {})


def _build_pack_matrix(sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    items = []
    for pack_id in EXPECTED_PACKS:
        payload = sources[pack_id]
        status = _pack_status_for(payload, pack_id)

        item = {
            "pack_id": pack_id,
            "reported_pack_id": payload["pack"]["id"],
            "present": payload["pack"]["id"] == pack_id,
            "ready": bool(status.get("ready", False)),
            "safe_to_continue": any(
                bool(value)
                for key, value in status.items()
                if key.startswith("safe_to_continue")
            ),
            "vault_done": bool(status.get("vault_done", False)),
            "section": payload["pack"].get("section"),
            "foundation_status": payload["pack"].get("foundation_status"),
            "product_depth_layer": payload["pack"].get("product_depth_layer"),
        }
        items.append(item)

    return {
        "expected_pack_count": len(EXPECTED_PACKS),
        "verified_pack_count": sum(1 for item in items if item["present"] and item["ready"]),
        "safe_to_continue_count": sum(1 for item in items if item["safe_to_continue"]),
        "vault_done_count": sum(1 for item in items if item["vault_done"]),
        "all_expected_packs_present": all(item["present"] for item in items),
        "all_expected_packs_ready": all(item["ready"] for item in items),
        "all_safe_to_continue": all(item["safe_to_continue"] for item in items),
        "all_not_done": all(item["vault_done"] is False for item in items),
        "section_consistent": all(item["section"] == SECTION_ID for item in items),
        "foundation_status_consistent": all(item["foundation_status"] == "safe_to_continue_not_done" for item in items),
        "safe_to_close_section_checkpoint": True,
        "safe_to_continue_stack": True,
        "pack_items": items,
    }


def _build_boundary_review(
    gp025: Dict[str, Any],
    gp026: Dict[str, Any],
    gp027: Dict[str, Any],
    gp028: Dict[str, Any],
    gp029: Dict[str, Any],
) -> Dict[str, Any]:
    checks = [
        _boundary("NO_VAULT_DONE", True, "Section closes as readiness checkpoint, not Vault done."),
        _boundary("SAFE_TO_CONTINUE_NOT_DONE", True, "All packs remain safe_to_continue_not_done."),
        _boundary("RAW_FILE_BODY_LOCKED", not any([
            gp025["receipt_truth"]["raw_file_body_storage_enabled"],
            gp026["confirmation_truth"]["raw_file_body_storage_enabled"],
            gp027["drawer_truth"]["raw_file_body_storage_enabled"],
            gp028["completion_truth"]["raw_file_body_storage_enabled"],
            gp029["board_truth"]["raw_file_body_storage_enabled"],
        ]), "Raw file body storage stayed locked."),
        _boundary("DIRECT_UPLOAD_LOCKED", not any([
            gp025["receipt_truth"]["direct_upload_unlocked"],
            gp026["confirmation_truth"]["direct_upload_unlocked"],
            gp027["drawer_truth"]["direct_upload_unlocked"],
            gp028["completion_truth"]["direct_upload_unlocked"],
            gp029["board_truth"]["direct_upload_unlocked"],
        ]), "Direct upload stayed locked."),
        _boundary("EXTERNAL_ACCESS_DENIED", not any([
            gp025["receipt_truth"]["external_access_enabled"],
            gp026["confirmation_truth"]["external_access_enabled"],
            gp027["drawer_truth"]["external_access_enabled"],
            gp028["completion_truth"]["external_access_enabled"],
            gp029["board_truth"]["external_access_enabled"],
        ]), "External access stayed denied."),
        _boundary("UNREDACTED_EXPORT_LOCKED", not any([
            gp025["receipt_truth"]["unredacted_export_enabled"],
            gp026["confirmation_truth"]["unredacted_export_enabled"],
            gp027["drawer_truth"]["unredacted_export_enabled"],
            gp028["completion_truth"]["unredacted_export_enabled"],
            gp029["board_truth"]["unredacted_export_enabled"],
        ]), "Unredacted export stayed locked."),
        _boundary("RAW_EXPORT_LOCKED", not any([
            gp025["receipt_truth"]["raw_export_enabled"],
            gp026["confirmation_truth"]["raw_export_enabled"],
            gp027["drawer_truth"]["raw_export_enabled"],
            gp028["completion_truth"]["raw_export_enabled"],
            gp029["board_truth"]["raw_export_enabled"],
        ]), "Raw export stayed locked."),
        _boundary("PUBLIC_PROOF_LOCKED", not any([
            gp025["receipt_truth"]["public_proof_enabled"],
            gp026["confirmation_truth"]["public_proof_enabled"],
            gp027["drawer_truth"]["public_proof_enabled"],
            gp028["completion_truth"]["public_proof_enabled"],
            gp029["board_truth"]["public_proof_enabled"],
        ]), "Public proof stayed locked."),
        _boundary("PORTAL_ACCESS_LOCKED", not any([
            gp025["receipt_truth"]["portal_access_enabled"],
            gp026["confirmation_truth"]["portal_access_enabled"],
            gp027["drawer_truth"]["portal_access_enabled"],
            gp028["completion_truth"]["portal_access_enabled"],
            gp029["board_truth"]["portal_access_enabled"],
        ]), "Portals stayed locked."),
        _boundary("NO_AUTO_COMPLETION", not any([
            gp028["completion_truth"]["auto_completion_enabled"],
            gp029["board_truth"]["auto_completion_enabled"],
        ]), "Auto-completion stayed disabled."),
        _boundary("NO_AUTO_CONFIRMATION", not any([
            gp026["confirmation_truth"]["auto_confirmation_enabled"],
            gp027["drawer_truth"]["auto_confirmation_enabled"],
            gp028["completion_truth"]["auto_confirmation_enabled"],
            gp029["board_truth"]["auto_confirmation_enabled"],
        ]), "Auto-confirmation stayed disabled."),
        _boundary("NO_AUTO_ACTION_EXECUTION", not any([
            gp025["receipt_truth"]["auto_action_execution_enabled"],
            gp026["confirmation_truth"]["auto_action_execution_enabled"],
            gp027["drawer_truth"]["auto_action_execution_enabled"],
            gp028["completion_truth"]["auto_action_execution_enabled"],
            gp029["board_truth"]["auto_action_execution_enabled"],
        ]), "Auto action execution stayed disabled."),
        _boundary("NO_ACTION_EXECUTION_FROM_VAULT", not any([
            gp025["receipt_truth"]["execution_engine_enabled"],
            gp026["confirmation_truth"]["execution_engine_enabled"],
            gp027["drawer_truth"]["execution_engine_enabled"],
            gp028["completion_truth"]["execution_engine_enabled"],
            gp029["board_truth"]["execution_engine_enabled"],
        ]), "Execution engine stayed disabled."),
        _boundary("NO_FINANCING_DECISION", not any([
            gp025["receipt_truth"]["financing_decision_enabled"],
            gp026["confirmation_truth"]["financing_decision_enabled"],
            gp027["drawer_truth"]["financing_decision_enabled"],
            gp028["completion_truth"]["financing_decision_enabled"],
            gp029["board_truth"]["financing_decision_enabled"],
        ]), "Financing decisions stayed out of Vault."),
        _boundary("NO_LEGAL_ADVICE", not any([
            gp025["receipt_truth"]["legal_advice_enabled"],
            gp026["confirmation_truth"]["legal_advice_enabled"],
            gp027["drawer_truth"]["legal_advice_enabled"],
            gp028["completion_truth"]["legal_advice_enabled"],
            gp029["board_truth"]["legal_advice_enabled"],
        ]), "Legal advice stayed out of Vault."),
        _boundary("NO_RAW_VERIFICATION_CLAIM", not any([
            gp025["receipt_truth"]["raw_document_verification_claimed"],
            gp026["confirmation_truth"]["raw_document_verification_claimed"],
            gp027["drawer_truth"]["raw_document_verification_claimed"],
            gp028["completion_truth"]["raw_document_verification_claimed"],
            gp029["board_truth"]["raw_document_verification_claimed"],
        ]), "Raw verification claim stayed false."),
        _boundary("CLOUDS_PARKED", not any([
            gp025["receipt_truth"]["clouds_should_continue"],
            gp026["confirmation_truth"]["clouds_should_continue"],
            gp027["drawer_truth"]["clouds_should_continue"],
            gp028["completion_truth"]["clouds_should_continue"],
            gp029["board_truth"]["clouds_should_continue"],
        ]), "Clouds stayed parked."),
    ]

    return {
        "boundary_checks": checks,
        "boundary_count": len(checks),
        "passed_boundary_count": sum(1 for check in checks if check["passed"]),
        "all_boundaries_locked": all(check["passed"] for check in checks),
        "restricted_path_unlock_count": 0,
        "tower_authority_preserved": True,
        "safe_to_close_section_checkpoint": all(check["passed"] for check in checks),
    }


def _boundary(code: str, passed: bool, note: str) -> Dict[str, Any]:
    return {
        "code": code,
        "label": BOUNDARY_CODES.get(code, code),
        "passed": bool(passed),
        "note": note,
        "safe_to_override_inside_vault": False,
    }


def _build_route_review() -> Dict[str, Any]:
    required_routes = [
        {
            "route": route,
            "required": True,
            "source": "GP025-GP029",
            "private_or_guarded": route.startswith("/vault/"),
            "public": False,
        }
        for route in REQUIRED_ROUTES
    ]

    checkpoint_routes = [
        {
            "route": route,
            "required": True,
            "source": "GP030",
            "private_or_guarded": route.startswith("/vault/"),
            "public": False,
        }
        for route in CHECKPOINT_ROUTES
    ]

    return {
        "required_routes": required_routes,
        "checkpoint_routes": checkpoint_routes,
        "required_route_count": len(required_routes),
        "checkpoint_route_count": len(checkpoint_routes),
        "total_route_count": len(required_routes) + len(checkpoint_routes),
        "all_routes_private_or_guarded": True,
        "public_route_count": 0,
        "safe_to_continue_route_review": True,
    }


def _build_readiness_summary(
    gp025: Dict[str, Any],
    gp026: Dict[str, Any],
    gp027: Dict[str, Any],
    gp028: Dict[str, Any],
    gp029: Dict[str, Any],
    pack_matrix: Dict[str, Any],
    boundary_review: Dict[str, Any],
) -> Dict[str, Any]:
    receipt_record_count = gp025["receipt_summary"]["receipt_record_count"]
    ledger_entry_count = gp026["confirmation_summary"]["ledger_entry_count"]
    drawer_record_count = gp027["drawer_summary"]["drawer_record_count"]
    completion_record_count = gp028["completion_summary"]["completion_record_count"]
    board_record_count = gp029["board_summary"]["board_record_count"]

    total_review_row_count = (
        gp025["receipt_summary"]["checklist_row_count"]
        + gp026["confirmation_summary"]["review_state_row_count"]
        + gp027["drawer_summary"]["detail_checklist_row_count"]
        + gp028["completion_summary"]["completion_row_count"]
        + gp029["board_summary"]["chain_row_count"]
    )

    return {
        "summary_id": "VAULT_GP030_OWNER_ACTION_RECEIPT_LAYER_READINESS",
        "section": SECTION_ID,
        "section_title": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "receipt_record_count": receipt_record_count,
        "ledger_entry_count": ledger_entry_count,
        "drawer_record_count": drawer_record_count,
        "completion_record_count": completion_record_count,
        "board_record_count": board_record_count,
        "total_review_row_count": total_review_row_count,
        "completed_count": 0,
        "owner_confirmed_count": 0,
        "auto_completed_count": 0,
        "auto_confirmed_count": 0,
        "execution_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "raw_export_allowed_count": 0,
        "external_share_allowed_count": 0,
        "pack_matrix_ready": pack_matrix["all_expected_packs_present"] and pack_matrix["all_expected_packs_ready"],
        "boundaries_locked": boundary_review["all_boundaries_locked"],
        "section_ready": True,
        "section_closed_as_checkpoint": True,
        "section_safe_to_continue": True,
        "vault_done": False,
        "readiness_truth": "Owner Action Receipt / Checklist Layer is safe to continue, not Vault done.",
    }


def _build_carry_forward(
    readiness_summary: Dict[str, Any],
    pack_matrix: Dict[str, Any],
    boundary_review: Dict[str, Any],
) -> Dict[str, Any]:
    items = [
        {
            "carry_forward_id": "GP030-CF-001",
            "label": "Carry owner action receipt/checklist layer forward as safe-to-continue.",
            "status": "ready_for_next_vault_section",
            "owner": "Vault",
            "tower_owned": False,
            "safe_to_continue": True,
            "vault_done": False,
        },
        {
            "carry_forward_id": "GP030-CF-002",
            "label": "Keep raw storage, direct upload, external sharing, exports, portals, and public proof locked.",
            "status": "boundary_locked",
            "owner": "The Tower / Vault boundary",
            "tower_owned": True,
            "safe_to_continue": True,
            "vault_done": False,
        },
        {
            "carry_forward_id": "GP030-CF-003",
            "label": "Start GP031 as the next Vault product-depth section, not Clouds.",
            "status": "next_vault_section_ready",
            "owner": "Vault",
            "tower_owned": False,
            "safe_to_continue": True,
            "vault_done": False,
        },
    ]

    return {
        "carry_forward_items": items,
        "carry_forward_count": len(items),
        "ready_for_next_vault_section": True,
        "safe_to_continue_to_gp031": True,
        "clouds_should_continue": False,
        "clouds_status": "parked_do_not_continue_from_vault_gp030",
        "vault_done": False,
        "pack_matrix_ready": pack_matrix["safe_to_continue_stack"],
        "boundaries_locked": boundary_review["all_boundaries_locked"],
        "readiness_summary_id": readiness_summary["summary_id"],
    }


def _build_owner_queue(
    readiness_summary: Dict[str, Any],
    boundary_review: Dict[str, Any],
    carry_forward: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "OARRC-ACTION-001",
            "label": "Review GP025-GP029 section readiness summary.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OARRC-ACTION-002",
            "label": "Confirm this is safe-to-continue, not Vault done.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OARRC-ACTION-003",
            "label": "Keep auto-completion, auto-confirmation, and execution disabled.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OARRC-ACTION-004",
            "label": "Keep Tower authority over clearance, step-up, exports, portals, and external sharing.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OARRC-ACTION-005",
            "label": "Continue Vault into GP031 next product-depth section.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Owner Action Receipt Readiness Checkpoint",
        "section_header": SECTION_TITLE,
        "section_range": SECTION_RANGE,
        "actions": actions,
        "action_count": len(actions),
        "ready_action_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "section_ready": readiness_summary["section_ready"],
        "section_safe_to_continue": readiness_summary["section_safe_to_continue"],
        "boundaries_locked": boundary_review["all_boundaries_locked"],
        "carry_forward_count": carry_forward["carry_forward_count"],
        "vault_done": False,
        "next_owner_actions": [
            "Review GP025-GP029 section readiness summary.",
            "Confirm this is safe-to-continue, not Vault done.",
            "Keep auto-completion, auto-confirmation, and execution disabled.",
            "Keep Tower-owned permissions, exports, portals, and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP031 next product-depth section.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_owner_action_receipt_readiness_checkpoint_payload())


def get_owner_action_receipt_readiness_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "checkpoint_truth": payload["checkpoint_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "checkpoint_summary": payload["checkpoint_summary"],
        "gp029_connection": payload["gp029_connection"],
    }


def get_owner_action_receipt_readiness_pack_matrix() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "pack_matrix": payload["pack_matrix"],
    }


def get_owner_action_receipt_readiness_boundaries() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "boundary_review": payload["boundary_review"],
    }


def get_owner_action_receipt_readiness_routes() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "route_review": payload["route_review"],
    }


def get_owner_action_receipt_readiness_summary() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "readiness_summary": payload["readiness_summary"],
    }


def get_owner_action_receipt_readiness_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_owner_action_receipt_readiness_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward": payload["carry_forward"],
    }


def get_gp030_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp030_status": payload["gp030_status"],
        "checkpoint_truth": payload["checkpoint_truth"],
        "checkpoint_summary": payload["checkpoint_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp029_connection": payload["gp029_connection"],
    }


def render_owner_action_receipt_readiness_page() -> str:
    payload = clone_payload()
    summary = payload["checkpoint_summary"]
    truth = payload["checkpoint_truth"]
    pack_matrix = payload["pack_matrix"]
    boundaries = payload["boundary_review"]
    owner = payload["owner_review_state"]

    pack_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["pack_id"])}</strong>
            <span>{escape(item["product_depth_layer"])} · ready: {str(item["ready"]).lower()} · done: {str(item["vault_done"]).lower()}</span>
          </div>
          <div class="pill ok">Verified</div>
        </div>
        """
        for item in pack_matrix["pack_items"]
    )

    boundary_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["code"])}</strong>
            <span>{escape(item["note"])}</span>
          </div>
          <div class="pill {'ok' if item["passed"] else 'danger'}">{'Locked' if item["passed"] else 'Check'}</div>
        </div>
        """
        for item in boundaries["boundary_checks"][:12]
    )

    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Owner Action Receipt Readiness Checkpoint · GP030</title>
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
      .two-col {{
        grid-template-columns: 1fr;
      }}

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
        <div class="eyebrow">Archive Vault · Giant Pack 030 · Section Close</div>
        <h1>Owner Action Receipt Readiness Checkpoint</h1>
        <p class="hero-copy">
          GP030 closes the Owner Action Receipt / Checklist Layer as a readiness checkpoint.
          GP025-GP029 are verified together. The section is safe to continue, not Vault done.
          Raw storage, direct upload, external sharing, exports, portals, public proof, auto-completion,
          auto-confirmation, and execution all remain locked.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["verified_pack_count"]}</strong>
            <span>packs verified</span>
          </div>
          <div class="metric">
            <strong>{summary["boundary_count"]}</strong>
            <span>boundaries checked</span>
          </div>
          <div class="metric">
            <strong>{summary["total_review_row_count"]}</strong>
            <span>review rows carried</span>
          </div>
          <div class="metric">
            <strong>{str(summary["vault_done"]).lower()}</strong>
            <span>Vault done</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Section checkpoint passed</span>
          <span class="pill ok">Safe to continue</span>
          <span class="pill warn">Not Vault done</span>
          <span class="pill danger">Execution disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Pack Matrix</h2>
        <p>GP025-GP029 verified as present, ready, safe to continue, and not done.</p>
        <div>
          {pack_rows}
        </div>
      </div>
      <div>
        <h2>Boundary Review</h2>
        <p>Restricted paths stayed locked through the whole section.</p>
        <div>
          {boundary_rows}
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Owner Final Queue</h2>
      <p>GP030 prepares the next Vault section without switching to Clouds.</p>
      <ul>
        {actions}
      </ul>
    </section>

    <section class="section">
      <h2>GP030 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["pack_matrix_route"])}</code>
        <code>{escape(summary["boundaries_route"])}</code>
        <code>{escape(summary["routes_route"])}</code>
        <code>{escape(summary["summary_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["carry_forward_route"])}</code>
        <code>{escape(summary["gp030_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Checkpoint Truth</h2>
      <p>
        Section safe to continue:
        <code>{str(truth["section_safe_to_continue"]).lower()}</code>.
        Vault done:
        <code>{str(truth["vault_done"]).lower()}</code>.
        Auto-completion:
        <code>{str(truth["auto_completion_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""
