"""
VAULT GIANT PACK 027 — Action Receipt Detail Drawer

CURRENT SECTION:
Archive Vault — Owner Action Receipt / Checklist Layer

This pack turns GP026 owner confirmation ledger entries into a detail drawer layer.

Important truth:
- GP027 is not an execution engine.
- GP027 does not auto-confirm anything.
- GP027 does not create public proof.
- GP027 does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, seller/broker/trustee portals, financing decisions,
  legal advice, or Tower-owned permissions.
- The drawer is metadata-only and private.
- It shows one opened receipt in context: receipt, ledger entry, review state rows,
  blockers, Tower gate state, carry-forward state, and owner next action.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.owner_confirmation_ledger_service import get_owner_confirmation_ledger_payload


PACK_ID = "VAULT_GP027"
PACK_NAME = "Action Receipt Detail Drawer"
SCHEMA_VERSION = "vault.action_receipt_detail_drawer.v1"

DRAWER_STATUSES = {
    "OPEN_FOR_OWNER_REVIEW": "Open for owner review",
    "WAITING_OWNER_CONFIRMATION": "Waiting owner confirmation",
    "TOWER_GATE_LOCKED": "Tower gate locked",
    "DETAIL_READY_METADATA_ONLY": "Detail ready metadata only",
    "CARRY_FORWARD_READY": "Carry-forward ready",
}

DRAWER_PANEL_TYPES = {
    "receipt_context": "Receipt context",
    "ledger_context": "Ledger context",
    "review_state": "Review state",
    "tower_gate": "Tower gate",
    "blockers": "Blockers",
    "carry_forward": "Carry forward",
    "owner_next_action": "Owner next action",
}

DRAWER_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "TOWER_STEP_UP_REQUIRED": "Tower step-up is required before sensitive action.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before closure.",
    "OWNER_REVIEW_REQUIRED": "Owner review is required before confirmation.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "NO_AUTO_ACTION_EXECUTION": "Automatic action execution is disabled.",
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault receipts and confirms review but does not execute actions.",
    "NO_AUTO_CONFIRMATION": "Automatic confirmation is disabled.",
    "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
    "NO_PUBLIC_RECEIPT_PROOF": "Owner action receipts are private and not public proof.",
    "DETAIL_DRAWER_PRIVATE_ONLY": "Receipt detail drawer is private only.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

PANEL_BLUEPRINTS = [
    {
        "panel_type": "receipt_context",
        "label": "Receipt context",
        "required": True,
        "tower_owned": False,
    },
    {
        "panel_type": "ledger_context",
        "label": "Ledger context",
        "required": True,
        "tower_owned": False,
    },
    {
        "panel_type": "review_state",
        "label": "Review state",
        "required": True,
        "tower_owned": False,
    },
    {
        "panel_type": "tower_gate",
        "label": "Tower gate",
        "required": True,
        "tower_owned": True,
    },
    {
        "panel_type": "blockers",
        "label": "Blockers",
        "required": True,
        "tower_owned": False,
    },
    {
        "panel_type": "carry_forward",
        "label": "Carry forward",
        "required": True,
        "tower_owned": False,
    },
    {
        "panel_type": "owner_next_action",
        "label": "Owner next action",
        "required": True,
        "tower_owned": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_action_receipt_detail_drawer_payload() -> Dict[str, Any]:
    gp026 = get_owner_confirmation_ledger_payload()

    ledger_entries = gp026["ledger_entries"]
    review_state_rows = gp026["review_state_rows"]
    receipt_links = gp026["receipt_links"]["links"]
    blockers = gp026["confirmation_blockers"]["blockers"]
    carry_forward_items = gp026["carry_forward_trail"]["carry_forward_items"]

    drawer_records = [
        _build_drawer_record(
            entry=entry,
            review_state_rows=review_state_rows,
            receipt_links=receipt_links,
            blockers=blockers,
            carry_forward_items=carry_forward_items,
        )
        for entry in ledger_entries
    ]

    drawer_panels = [
        panel
        for record in drawer_records
        for panel in record["drawer_panels"]
    ]

    checklist_rows = [
        row
        for record in drawer_records
        for row in record["detail_checklist_rows"]
    ]

    tower_gate_detail = _build_tower_gate_detail(drawer_records)
    blocker_detail = _build_drawer_blocker_detail(drawer_records)
    carry_forward_detail = _build_drawer_carry_forward(drawer_records)
    owner_queue = _build_owner_queue(drawer_records, drawer_panels, blocker_detail, carry_forward_detail)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "action_receipt_detail_drawer",
            "section": "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER",
        },
        "drawer_truth": {
            "action_receipt_detail_drawer_enabled": True,
            "metadata_only": True,
            "private_drawer_only": True,
            "drawer_can_show_sensitive_body": False,
            "drawer_can_execute_action": False,
            "drawer_can_auto_confirm": False,
            "drawer_can_create_public_proof": False,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "auto_confirmation_enabled": False,
            "execution_after_confirmation_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "public_ledger_proof_enabled": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp027",
            "safe_next_unlock": "GP028 can deepen checklist completion state without unlocking raw storage, external sharing, public proof, confirmation auto-run, or execution.",
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
        "drawer_summary": {
            "room_title": "Vault Action Receipt Detail Drawer",
            "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
            "route": "/vault/action-receipt-detail-drawer",
            "json_route": "/vault/action-receipt-detail-drawer.json",
            "records_route": "/vault/action-receipt-detail-drawer-records.json",
            "panels_route": "/vault/action-receipt-detail-drawer-panels.json",
            "checklist_route": "/vault/action-receipt-detail-drawer-checklist.json",
            "tower_gates_route": "/vault/action-receipt-detail-drawer-tower-gates.json",
            "blockers_route": "/vault/action-receipt-detail-drawer-blockers.json",
            "carry_forward_route": "/vault/action-receipt-detail-drawer-carry-forward.json",
            "owner_queue_route": "/vault/action-receipt-detail-drawer-owner-queue.json",
            "gp027_status_route": "/vault/gp027-status.json",
            "drawer_record_count": len(drawer_records),
            "drawer_panel_count": len(drawer_panels),
            "detail_checklist_row_count": len(checklist_rows),
            "tower_gate_detail_count": tower_gate_detail["tower_gate_detail_count"],
            "blocker_count": blocker_detail["blocker_count"],
            "carry_forward_count": carry_forward_detail["carry_forward_count"],
            "owner_action_count": owner_queue["action_count"],
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "drawer_records": drawer_records,
        "drawer_panels": drawer_panels,
        "detail_checklist_rows": checklist_rows,
        "tower_gate_detail": tower_gate_detail,
        "drawer_blocker_detail": blocker_detail,
        "drawer_carry_forward": carry_forward_detail,
        "owner_review_state": owner_queue,
        "gp026_connection": {
            "gp026_pack_id": gp026["pack"]["id"],
            "gp026_ready": gp026["gp026_status"]["ready"],
            "gp026_safe_to_continue": gp026["gp026_status"]["safe_to_continue_to_gp027"],
            "gp026_vault_done": gp026["gp026_status"]["vault_done"],
            "gp026_ledger_entry_count": gp026["confirmation_summary"]["ledger_entry_count"],
            "gp026_review_state_row_count": gp026["confirmation_summary"]["review_state_row_count"],
        },
        "gp027_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp026_confirmation_ledger_connected": True,
            "action_receipt_detail_drawer_ready": True,
            "safe_to_continue_to_gp028": True,
            "vault_done": False,
            "metadata_only_drawer": True,
            "private_drawer_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "auto_confirmation_disabled": True,
            "execution_after_confirmation_disabled": True,
            "execution_engine_disabled": True,
            "drawer_execution_disabled": True,
            "drawer_public_proof_disabled": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "external_access_still_locked": True,
            "unredacted_export_still_locked": True,
            "raw_export_still_locked": True,
            "public_proof_still_locked": True,
            "public_ledger_proof_disabled": True,
            "portal_access_still_locked": True,
            "financing_decision_not_claimed": True,
            "legal_advice_not_claimed": True,
            "raw_verification_not_claimed": True,
            "auto_action_execution_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp027",
            "next_pack": "VAULT_GP028_CHECKLIST_COMPLETION_STATE_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _review_rows_for_entry(entry: Dict[str, Any], review_state_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in review_state_rows if row["ledger_id"] == entry["ledger_id"]]


def _receipt_link_for_entry(entry: Dict[str, Any], receipt_links: List[Dict[str, Any]]) -> Dict[str, Any]:
    for link in receipt_links:
        if link["ledger_id"] == entry["ledger_id"]:
            return link
    return {}


def _carry_forward_for_entry(entry: Dict[str, Any], carry_forward_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    for item in carry_forward_items:
        if item["ledger_id"] == entry["ledger_id"]:
            return item
    return {}


def _build_drawer_record(
    entry: Dict[str, Any],
    review_state_rows: List[Dict[str, Any]],
    receipt_links: List[Dict[str, Any]],
    blockers: List[Dict[str, Any]],
    carry_forward_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    related_review_rows = _review_rows_for_entry(entry, review_state_rows)
    receipt_link = _receipt_link_for_entry(entry, receipt_links)
    carry_forward = _carry_forward_for_entry(entry, carry_forward_items)

    blocked_codes = set(entry.get("blocked_codes", []))
    blocked_codes.update({
        "DETAIL_DRAWER_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_PUBLIC_RECEIPT_PROOF",
        "CLOUDS_PARKED",
    })

    panels = [_build_drawer_panel(entry, receipt_link, carry_forward, panel, idx + 1) for idx, panel in enumerate(PANEL_BLUEPRINTS)]
    checklist_rows = [_build_detail_checklist_row(entry, row, idx + 1) for idx, row in enumerate(related_review_rows)]

    affected_blockers = [
        {
            "code": blocker["code"],
            "label": blocker["label"],
            "owner": blocker["owner"],
            "safe_to_override_inside_vault": False,
        }
        for blocker in blockers
        if blocker["code"] in blocked_codes
    ]

    return {
        "drawer_id": f"VDD-{entry['ledger_id'].replace('VOL-', '')}",
        "ledger_id": entry["ledger_id"],
        "receipt_id": entry["receipt_id"],
        "prep_id": entry["prep_id"],
        "source_step_id": entry["source_step_id"],
        "plan_packet_id": entry["plan_packet_id"],
        "plan_id": entry["plan_id"],
        "title": entry["title"],
        "lane": entry["lane"],
        "drawer_status": "OPEN_FOR_OWNER_REVIEW",
        "drawer_status_label": DRAWER_STATUSES["OPEN_FOR_OWNER_REVIEW"],
        "metadata_only": True,
        "private_drawer_only": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmation_required": True,
        "owner_confirmed": False,
        "auto_confirm_allowed": False,
        "can_execute_after_confirmation": False,
        "can_execute_from_vault": False,
        "execution_engine_enabled": False,
        "public_proof_allowed": False,
        "public_ledger_proof_allowed": False,
        "raw_body_available": False,
        "external_share_allowed": False,
        "raw_export_allowed": False,
        "unredacted_export_allowed": False,
        "tower_gate_observed": entry["tower_gate_observed"],
        "tower_clearance_required": entry["tower_clearance_required"],
        "tower_step_up_required": entry["tower_step_up_required"],
        "receipt_link": receipt_link,
        "carry_forward": carry_forward,
        "drawer_panels": panels,
        "drawer_panel_count": len(panels),
        "detail_checklist_rows": checklist_rows,
        "detail_checklist_row_count": len(checklist_rows),
        "affected_blockers": affected_blockers,
        "affected_blocker_count": len(affected_blockers),
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [DRAWER_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Open receipt detail drawer for {entry['title']} without executing, confirming, exporting, or sharing.",
        "safe_to_carry_to_gp028": True,
    }


def _build_drawer_panel(
    entry: Dict[str, Any],
    receipt_link: Dict[str, Any],
    carry_forward: Dict[str, Any],
    blueprint: Dict[str, Any],
    sequence: int,
) -> Dict[str, Any]:
    blocked_codes = {
        "DETAIL_DRAWER_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    }

    if blueprint["tower_owned"] or entry["tower_clearance_required"]:
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    if blueprint["panel_type"] in {"receipt_context", "ledger_context"}:
        blocked_codes.add("NO_PUBLIC_RECEIPT_PROOF")

    if blueprint["panel_type"] == "tower_gate":
        blocked_codes.update({"EXTERNAL_ACCESS_DENIED", "PORTAL_ACCESS_LOCKED"})

    if blueprint["panel_type"] == "blockers":
        blocked_codes.update(entry.get("blocked_codes", []))

    return {
        "panel_id": f"VDP-{entry['ledger_id'].replace('VOL-', '')}-{sequence:02d}",
        "drawer_id": f"VDD-{entry['ledger_id'].replace('VOL-', '')}",
        "ledger_id": entry["ledger_id"],
        "receipt_id": entry["receipt_id"],
        "prep_id": entry["prep_id"],
        "panel_type": blueprint["panel_type"],
        "panel_type_label": DRAWER_PANEL_TYPES[blueprint["panel_type"]],
        "label": blueprint["label"],
        "sequence": sequence,
        "required": blueprint["required"],
        "tower_owned": blueprint["tower_owned"],
        "panel_status": "OPEN_METADATA_ONLY",
        "metadata_only": True,
        "can_show_raw_body": False,
        "can_execute_from_vault": False,
        "can_auto_confirm": False,
        "public_proof_allowed": False,
        "receipt_linked": bool(receipt_link),
        "carry_forward_ready": bool(carry_forward.get("safe_to_carry_to_gp027", False)),
        "blocked_codes": sorted(blocked_codes),
    }


def _build_detail_checklist_row(entry: Dict[str, Any], review_row: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    blocked_codes = set(review_row.get("blocked_codes", []))
    blocked_codes.update({
        "DETAIL_DRAWER_PRIVATE_ONLY",
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    })

    return {
        "detail_checklist_id": f"VDC-{entry['ledger_id'].replace('VOL-', '')}-{sequence:02d}",
        "drawer_id": f"VDD-{entry['ledger_id'].replace('VOL-', '')}",
        "ledger_id": entry["ledger_id"],
        "receipt_id": entry["receipt_id"],
        "prep_id": entry["prep_id"],
        "review_state_id": review_row["review_state_id"],
        "state_type": review_row["state_type"],
        "label": review_row["label"],
        "sequence": sequence,
        "required": True,
        "status": "OPEN",
        "completed": False,
        "owner_review_required": True,
        "owner_confirmed": False,
        "auto_complete_allowed": False,
        "auto_confirm_allowed": False,
        "can_execute_from_vault": False,
        "metadata_only": True,
        "blocked_codes": sorted(blocked_codes),
    }


def _build_tower_gate_detail(drawer_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    gate_rows = [
        {
            "tower_gate_detail_id": f"VDG-{record['drawer_id'].replace('VDD-', '')}",
            "drawer_id": record["drawer_id"],
            "ledger_id": record["ledger_id"],
            "receipt_id": record["receipt_id"],
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "tower_gate_observed": record["tower_gate_observed"],
            "tower_clearance_required": record["tower_clearance_required"],
            "tower_step_up_required": record["tower_step_up_required"],
            "tower_owned": True,
            "vault_can_override": False,
            "external_access_allowed": False,
            "portal_access_allowed": False,
            "export_allowed": False,
        }
        for record in drawer_records
    ]

    return {
        "tower_gate_details": gate_rows,
        "tower_gate_detail_count": len(gate_rows),
        "tower_owned_gate_count": len(gate_rows),
        "clearance_required_count": sum(1 for row in gate_rows if row["tower_clearance_required"]),
        "step_up_required_count": sum(1 for row in gate_rows if row["tower_step_up_required"]),
        "vault_override_allowed_count": 0,
        "all_tower_gates_preserved": True,
    }


def _build_drawer_blocker_detail(drawer_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for record in drawer_records for code in record["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": DRAWER_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_drawer_count": sum(1 for record in drawer_records if code in record["blocked_codes"]),
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
        "auto_confirmation_allowed": False,
        "execution_after_confirmation_allowed": False,
        "public_drawer_proof_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only drawer review. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "TOWER_STEP_UP_REQUIRED": "Tower must own step-up before sensitive action.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before closure.",
        "OWNER_REVIEW_REQUIRED": "Require owner review before confirmation.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault shows receipt detail but does not execute actions.",
        "NO_AUTO_CONFIRMATION": "Do not auto-confirm owner actions.",
        "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
        "NO_PUBLIC_RECEIPT_PROOF": "Keep owner action receipts private.",
        "DETAIL_DRAWER_PRIVATE_ONLY": "Keep drawer private and metadata-only.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP027.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_drawer_carry_forward(drawer_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    carry_items = [
        {
            "drawer_carry_forward_id": f"VDF-{record['drawer_id'].replace('VDD-', '')}",
            "drawer_id": record["drawer_id"],
            "ledger_id": record["ledger_id"],
            "receipt_id": record["receipt_id"],
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "carry_forward_status": "READY_FOR_GP028_CHECKLIST_COMPLETION_STATE",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "auto_confirm_allowed": False,
            "execution_allowed": False,
            "public_proof_allowed": False,
            "safe_to_carry_to_gp028": True,
        }
        for record in drawer_records
    ]

    return {
        "carry_forward_items": carry_items,
        "carry_forward_count": len(carry_items),
        "ready_for_gp028_count": len(carry_items),
        "owner_confirmed_count": 0,
        "execution_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "safe_to_carry_to_gp028": True,
    }


def _build_owner_queue(
    drawer_records: List[Dict[str, Any]],
    drawer_panels: List[Dict[str, Any]],
    blocker_detail: Dict[str, Any],
    carry_forward_detail: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "ARDD-ACTION-001",
            "label": "Open action receipt detail drawer records for owner review.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ARDD-ACTION-002",
            "label": "Review drawer panels without auto-confirming anything.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ARDD-ACTION-003",
            "label": "Keep Tower gate checks, step-up, portals, exports, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ARDD-ACTION-004",
            "label": "Keep drawer private and metadata-only.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ARDD-ACTION-005",
            "label": "Continue Vault into GP028 checklist completion state.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Action Receipt Detail Drawer",
        "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
        "actions": actions,
        "action_count": len(actions),
        "drawer_record_count": len(drawer_records),
        "drawer_panel_count": len(drawer_panels),
        "blocker_count": blocker_detail["blocker_count"],
        "carry_forward_count": carry_forward_detail["carry_forward_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Open action receipt detail drawer records for owner review.",
            "Review drawer panels without auto-confirming anything.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Keep drawer private and metadata-only.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP028 checklist completion state.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_action_receipt_detail_drawer_payload())


def get_action_receipt_detail_drawer_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "drawer_truth": payload["drawer_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "drawer_summary": payload["drawer_summary"],
        "gp026_connection": payload["gp026_connection"],
    }


def get_action_receipt_detail_drawer_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "drawer_records": payload["drawer_records"],
        "drawer_record_count": len(payload["drawer_records"]),
    }


def get_action_receipt_detail_drawer_panels() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "drawer_panels": payload["drawer_panels"],
        "drawer_panel_count": len(payload["drawer_panels"]),
    }


def get_action_receipt_detail_drawer_checklist() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "detail_checklist_rows": payload["detail_checklist_rows"],
        "detail_checklist_row_count": len(payload["detail_checklist_rows"]),
    }


def get_action_receipt_detail_drawer_tower_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gate_detail": payload["tower_gate_detail"],
    }


def get_action_receipt_detail_drawer_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "drawer_blocker_detail": payload["drawer_blocker_detail"],
    }


def get_action_receipt_detail_drawer_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "drawer_carry_forward": payload["drawer_carry_forward"],
    }


def get_action_receipt_detail_drawer_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp027_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp027_status": payload["gp027_status"],
        "drawer_truth": payload["drawer_truth"],
        "drawer_summary": payload["drawer_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp026_connection": payload["gp026_connection"],
    }


def render_action_receipt_detail_drawer_page() -> str:
    payload = clone_payload()
    summary = payload["drawer_summary"]
    truth = payload["drawer_truth"]
    drawer_records = payload["drawer_records"]
    tower_gate = payload["tower_gate_detail"]
    owner = payload["owner_review_state"]

    drawer_cards = "\n".join(_render_drawer_card(record) for record in drawer_records[:9])
    gate_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(row["title"])}</strong>
            <span>clearance required: {str(row["tower_clearance_required"]).lower()} · vault override: {str(row["vault_can_override"]).lower()}</span>
          </div>
          <div class="pill danger">Tower gate</div>
        </div>
        """
        for row in tower_gate["tower_gate_details"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Action Receipt Detail Drawer · GP027</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 027</div>
        <h1>Action Receipt Detail Drawer</h1>
        <p class="hero-copy">
          GP027 gives each owner action receipt a private detail drawer. The drawer ties together receipt context,
          ledger context, review-state rows, blockers, Tower gate status, carry-forward state, and owner next action
          without executing, auto-confirming, showing raw bodies, exporting, sharing, or creating public proof.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["drawer_record_count"]}</strong>
            <span>drawer records</span>
          </div>
          <div class="metric">
            <strong>{summary["drawer_panel_count"]}</strong>
            <span>drawer panels</span>
          </div>
          <div class="metric">
            <strong>{summary["detail_checklist_row_count"]}</strong>
            <span>detail checklist rows</span>
          </div>
          <div class="metric">
            <strong>{summary["tower_gate_detail_count"]}</strong>
            <span>Tower gate details</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Detail drawer ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Auto-confirm disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Drawer Records</h2>
      <p>
        Each drawer is private, metadata-only, and tied to one receipt/ledger/prep record chain.
      </p>
      <div class="grid">
        {drawer_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Tower Gate Detail</h2>
        <p>Tower owns clearance, step-up, external access, portals, and export authority.</p>
        <div>
          {gate_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP027 prepares GP028 checklist completion state.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP027 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["records_route"])}</code>
        <code>{escape(summary["panels_route"])}</code>
        <code>{escape(summary["checklist_route"])}</code>
        <code>{escape(summary["tower_gates_route"])}</code>
        <code>{escape(summary["blockers_route"])}</code>
        <code>{escape(summary["carry_forward_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp027_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Drawer Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Auto-confirm:
        <code>{str(truth["auto_confirmation_enabled"]).lower()}</code>.
        Drawer execution:
        <code>{str(truth["drawer_can_execute_action"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_drawer_card(record: Dict[str, Any]) -> str:
    status_class = "danger" if record["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record["title"])}</div>
            <div class="meta">
              Drawer: <code>{escape(record["drawer_id"])}</code><br>
              Ledger: <code>{escape(record["ledger_id"])}</code><br>
              Receipt: <code>{escape(record["receipt_id"])}</code><br>
              Panels: <code>{record["drawer_panel_count"]}</code><br>
              Can execute: <code>{str(record["can_execute_from_vault"]).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(record["drawer_status"])}</span>
        </div>
      </article>
    """
