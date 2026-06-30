"""
VAULT GIANT PACK 026 — Owner Confirmation Ledger

CURRENT SECTION:
Archive Vault — Owner Action Receipt / Checklist Layer

This pack deepens GP025 confirmation ledger seeds into a real owner confirmation ledger.

Important truth:
- GP026 is not an execution engine.
- GP026 does not auto-confirm anything.
- Owner confirmation records stay waiting/open until Solice reviews them.
- Confirmation does not trigger execution.
- It does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, public proof, seller/broker/trustee portals,
  financing decisions, legal advice, or Tower-owned permissions.
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


PACK_ID = "VAULT_GP026"
PACK_NAME = "Owner Confirmation Ledger"
SCHEMA_VERSION = "vault.owner_confirmation_ledger.v1"

CONFIRMATION_STATUSES = {
    "WAITING_OWNER_REVIEW": "Waiting owner review",
    "WAITING_OWNER_CONFIRMATION": "Waiting owner confirmation",
    "BLOCKED_BY_TOWER_GATE": "Blocked by Tower gate",
    "HELD_METADATA_ONLY": "Held metadata only",
    "CARRY_FORWARD_READY": "Carry-forward ready",
}

CONFIRMATION_BLOCK_CODES = {
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
    "CLOUDS_PARKED": "Clouds remains parked.",
}

REVIEW_STATE_ROWS = [
    {
        "state_type": "owner_review",
        "label": "Owner review pending",
        "required": True,
        "tower_owned": False,
    },
    {
        "state_type": "owner_confirmation",
        "label": "Owner confirmation pending",
        "required": True,
        "tower_owned": False,
    },
    {
        "state_type": "tower_gate_observation",
        "label": "Tower gate observed",
        "required": True,
        "tower_owned": True,
    },
    {
        "state_type": "execution_block",
        "label": "Execution remains blocked",
        "required": True,
        "tower_owned": False,
    },
    {
        "state_type": "carry_forward",
        "label": "Carry-forward prepared",
        "required": True,
        "tower_owned": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_owner_confirmation_ledger_payload() -> Dict[str, Any]:
    gp025 = get_owner_action_receipts_payload()

    receipt_records = gp025["receipt_records"]
    ledger_seed = gp025["confirmation_ledger_seed"]["ledger_entries"]

    ledger_entries = [_build_ledger_entry(seed, receipt_records) for seed in ledger_seed]
    review_states = [
        row
        for entry in ledger_entries
        for row in entry["review_state_rows"]
    ]
    receipt_links = _build_receipt_links(ledger_entries, receipt_records)
    blockers = _build_confirmation_blockers(ledger_entries)
    carry_forward = _build_carry_forward_trail(ledger_entries)
    owner_queue = _build_owner_queue(ledger_entries, review_states, blockers, carry_forward)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "owner_confirmation_ledger",
            "section": "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER",
        },
        "confirmation_truth": {
            "owner_confirmation_ledger_enabled": True,
            "metadata_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "auto_confirmation_enabled": False,
            "execution_after_confirmation_enabled": False,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "private_ledger_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp026",
            "safe_next_unlock": "GP027 can deepen action receipt detail drawer without unlocking raw storage, external sharing, confirmation auto-run, or execution.",
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
        "confirmation_summary": {
            "room_title": "Vault Owner Confirmation Ledger",
            "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
            "route": "/vault/owner-confirmation-ledger",
            "json_route": "/vault/owner-confirmation-ledger.json",
            "entries_route": "/vault/owner-confirmation-ledger-entries.json",
            "review_state_route": "/vault/owner-confirmation-ledger-review-state.json",
            "receipt_links_route": "/vault/owner-confirmation-ledger-receipt-links.json",
            "blockers_route": "/vault/owner-confirmation-ledger-blockers.json",
            "carry_forward_route": "/vault/owner-confirmation-ledger-carry-forward.json",
            "owner_queue_route": "/vault/owner-confirmation-ledger-owner-queue.json",
            "gp026_status_route": "/vault/gp026-status.json",
            "ledger_entry_count": len(ledger_entries),
            "review_state_row_count": len(review_states),
            "receipt_link_count": receipt_links["receipt_link_count"],
            "blocker_count": blockers["blocker_count"],
            "carry_forward_count": carry_forward["carry_forward_count"],
            "owner_action_count": owner_queue["action_count"],
            "owner_confirmed_count": 0,
            "metadata_only": True,
        },
        "ledger_entries": ledger_entries,
        "review_state_rows": review_states,
        "receipt_links": receipt_links,
        "confirmation_blockers": blockers,
        "carry_forward_trail": carry_forward,
        "owner_review_state": owner_queue,
        "gp025_connection": {
            "gp025_pack_id": gp025["pack"]["id"],
            "gp025_ready": gp025["gp025_status"]["ready"],
            "gp025_safe_to_continue": gp025["gp025_status"]["safe_to_continue_to_gp026"],
            "gp025_vault_done": gp025["gp025_status"]["vault_done"],
            "gp025_receipt_record_count": gp025["receipt_summary"]["receipt_record_count"],
            "gp025_confirmation_ledger_seed_count": gp025["receipt_summary"]["confirmation_ledger_seed_count"],
        },
        "gp026_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp025_receipts_connected": True,
            "owner_confirmation_ledger_ready": True,
            "safe_to_continue_to_gp027": True,
            "vault_done": False,
            "metadata_only_ledger": True,
            "private_ledger_only": True,
            "owner_review_required": True,
            "owner_confirmation_required": True,
            "owner_confirmed_count": 0,
            "auto_confirmation_disabled": True,
            "execution_after_confirmation_disabled": True,
            "execution_engine_disabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp026",
            "next_pack": "VAULT_GP027_ACTION_RECEIPT_DETAIL_DRAWER_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _receipt_by_id(receipt_records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {receipt["receipt_id"]: receipt for receipt in receipt_records}


def _build_ledger_entry(seed: Dict[str, Any], receipt_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    receipt_lookup = _receipt_by_id(receipt_records)
    receipt = receipt_lookup.get(seed["receipt_id"], {})

    blocked_codes = set(receipt.get("blocked_codes", []))
    blocked_codes.update({
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_PUBLIC_RECEIPT_PROOF",
        "CLOUDS_PARKED",
    })

    review_state_rows = [_build_review_state_row(seed, receipt, row, idx + 1) for idx, row in enumerate(REVIEW_STATE_ROWS)]

    return {
        "ledger_id": f"VOL-{seed['ledger_entry_id'].replace('VCL-', '')}",
        "seed_ledger_entry_id": seed["ledger_entry_id"],
        "receipt_id": seed["receipt_id"],
        "prep_id": seed["prep_id"],
        "plan_packet_id": receipt.get("plan_packet_id"),
        "plan_id": receipt.get("plan_id"),
        "source_step_id": receipt.get("source_step_id"),
        "title": seed["title"],
        "lane": seed["lane"],
        "ledger_status": "WAITING_OWNER_REVIEW",
        "ledger_status_label": CONFIRMATION_STATUSES["WAITING_OWNER_REVIEW"],
        "metadata_only": True,
        "private_ledger_only": True,
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
        "tower_gate_observed": receipt.get("tower_gate_observed", True),
        "tower_clearance_required": receipt.get("tower_clearance_required", False),
        "tower_step_up_required": receipt.get("tower_step_up_required", False),
        "review_state_rows": review_state_rows,
        "review_state_row_count": len(review_state_rows),
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [CONFIRMATION_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Review confirmation ledger entry for {seed['title']} without executing any action.",
    }


def _build_review_state_row(
    seed: Dict[str, Any],
    receipt: Dict[str, Any],
    blueprint: Dict[str, Any],
    sequence: int,
) -> Dict[str, Any]:
    blocked_codes = {
        "OWNER_REVIEW_REQUIRED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_CONFIRMATION",
        "NO_EXECUTION_AFTER_CONFIRMATION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    }

    if blueprint["tower_owned"] or receipt.get("tower_clearance_required", False):
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    if blueprint["state_type"] == "execution_block":
        blocked_codes.update({"NO_AUTO_ACTION_EXECUTION", "NO_EXECUTION_AFTER_CONFIRMATION"})

    if blueprint["state_type"] == "carry_forward":
        blocked_codes.add("NO_PUBLIC_RECEIPT_PROOF")

    return {
        "review_state_id": f"VRS-{seed['ledger_entry_id'].replace('VCL-', '')}-{sequence:02d}",
        "ledger_id": f"VOL-{seed['ledger_entry_id'].replace('VCL-', '')}",
        "receipt_id": seed["receipt_id"],
        "prep_id": seed["prep_id"],
        "title": seed["title"],
        "lane": seed["lane"],
        "state_type": blueprint["state_type"],
        "label": blueprint["label"],
        "sequence": sequence,
        "required": blueprint["required"],
        "tower_owned": blueprint["tower_owned"],
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


def _build_receipt_links(ledger_entries: List[Dict[str, Any]], receipt_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    receipt_lookup = _receipt_by_id(receipt_records)

    links = [
        {
            "link_id": f"VLR-{entry['ledger_id'].replace('VOL-', '')}",
            "ledger_id": entry["ledger_id"],
            "receipt_id": entry["receipt_id"],
            "prep_id": entry["prep_id"],
            "source_step_id": entry["source_step_id"],
            "plan_packet_id": entry["plan_packet_id"],
            "title": entry["title"],
            "lane": entry["lane"],
            "link_status": "LEDGER_LINKED_TO_PRIVATE_RECEIPT",
            "receipt_exists": entry["receipt_id"] in receipt_lookup,
            "receipt_created": receipt_lookup.get(entry["receipt_id"], {}).get("receipt_created", False),
            "public_proof_allowed": False,
            "external_share_allowed": False,
            "safe_to_carry_to_gp027": True,
        }
        for entry in ledger_entries
    ]

    return {
        "links": links,
        "receipt_link_count": len(links),
        "all_ledger_entries_linked": all(item["receipt_exists"] for item in links),
        "receipt_created_count": sum(1 for item in links if item["receipt_created"]),
        "public_proof_allowed_count": 0,
        "external_share_allowed_count": 0,
        "safe_to_carry_to_gp027": True,
    }


def _build_confirmation_blockers(ledger_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for entry in ledger_entries for code in entry["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": CONFIRMATION_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_ledger_count": sum(1 for entry in ledger_entries if code in entry["blocked_codes"]),
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
        "public_ledger_proof_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only confirmation ledger review. Do not display raw bodies.",
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
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault confirms review but does not execute actions.",
        "NO_AUTO_CONFIRMATION": "Do not auto-confirm owner actions.",
        "NO_EXECUTION_AFTER_CONFIRMATION": "Confirmation does not trigger execution.",
        "NO_PUBLIC_RECEIPT_PROOF": "Keep owner action receipts private.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP026.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_carry_forward_trail(ledger_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    carry_items = [
        {
            "carry_forward_id": f"VCF-{entry['ledger_id'].replace('VOL-', '')}",
            "ledger_id": entry["ledger_id"],
            "receipt_id": entry["receipt_id"],
            "prep_id": entry["prep_id"],
            "title": entry["title"],
            "lane": entry["lane"],
            "carry_forward_status": "READY_FOR_GP027_DETAIL_DRAWER",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "auto_confirm_allowed": False,
            "execution_allowed": False,
            "public_proof_allowed": False,
            "safe_to_carry_to_gp027": True,
        }
        for entry in ledger_entries
    ]

    return {
        "carry_forward_items": carry_items,
        "carry_forward_count": len(carry_items),
        "ready_for_gp027_count": len(carry_items),
        "owner_confirmed_count": 0,
        "execution_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "safe_to_carry_to_gp027": True,
    }


def _build_owner_queue(
    ledger_entries: List[Dict[str, Any]],
    review_states: List[Dict[str, Any]],
    blockers: Dict[str, Any],
    carry_forward: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "OCL-ACTION-001",
            "label": "Review owner confirmation ledger entries.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OCL-ACTION-002",
            "label": "Keep auto-confirmation disabled.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OCL-ACTION-003",
            "label": "Confirm that owner confirmation does not execute any action.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OCL-ACTION-004",
            "label": "Keep Tower gate checks, step-up, portals, exports, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OCL-ACTION-005",
            "label": "Continue Vault into GP027 action receipt detail drawer.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Owner Confirmation Ledger",
        "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
        "actions": actions,
        "action_count": len(actions),
        "ledger_entry_count": len(ledger_entries),
        "review_state_row_count": len(review_states),
        "blocker_count": blockers["blocker_count"],
        "carry_forward_count": carry_forward["carry_forward_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review owner confirmation ledger entries.",
            "Keep auto-confirmation disabled.",
            "Confirm that owner confirmation does not execute any action.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP027 action receipt detail drawer.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_owner_confirmation_ledger_payload())


def get_owner_confirmation_ledger_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "confirmation_truth": payload["confirmation_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "confirmation_summary": payload["confirmation_summary"],
        "gp025_connection": payload["gp025_connection"],
    }


def get_owner_confirmation_ledger_entries() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "ledger_entries": payload["ledger_entries"],
        "ledger_entry_count": len(payload["ledger_entries"]),
    }


def get_owner_confirmation_ledger_review_state() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_state_rows": payload["review_state_rows"],
        "review_state_row_count": len(payload["review_state_rows"]),
    }


def get_owner_confirmation_ledger_receipt_links() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_links": payload["receipt_links"],
    }


def get_owner_confirmation_ledger_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "confirmation_blockers": payload["confirmation_blockers"],
    }


def get_owner_confirmation_ledger_carry_forward() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "carry_forward_trail": payload["carry_forward_trail"],
    }


def get_owner_confirmation_ledger_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp026_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp026_status": payload["gp026_status"],
        "confirmation_truth": payload["confirmation_truth"],
        "confirmation_summary": payload["confirmation_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp025_connection": payload["gp025_connection"],
    }


def render_owner_confirmation_ledger_page() -> str:
    payload = clone_payload()
    summary = payload["confirmation_summary"]
    truth = payload["confirmation_truth"]
    ledger_entries = payload["ledger_entries"]
    carry_forward = payload["carry_forward_trail"]
    owner = payload["owner_review_state"]

    ledger_cards = "\n".join(_render_ledger_card(entry) for entry in ledger_entries[:9])
    carry_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["title"])}</strong>
            <span>{escape(item["carry_forward_status"])} · execution allowed: {str(item["execution_allowed"]).lower()}</span>
          </div>
          <div class="pill warn">Carry forward</div>
        </div>
        """
        for item in carry_forward["carry_forward_items"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Owner Confirmation Ledger · GP026</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 026</div>
        <h1>Owner Confirmation Ledger</h1>
        <p class="hero-copy">
          GP026 deepens GP025 ledger seeds into a real owner confirmation ledger. It tracks owner-review state,
          receipt links, confirmation blockers, and carry-forward trails without auto-confirming anything,
          executing actions, unlocking raw storage, sharing externally, exporting raw/unredacted data, or creating public proof.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["ledger_entry_count"]}</strong>
            <span>ledger entries</span>
          </div>
          <div class="metric">
            <strong>{summary["review_state_row_count"]}</strong>
            <span>review states</span>
          </div>
          <div class="metric">
            <strong>{summary["receipt_link_count"]}</strong>
            <span>receipt links</span>
          </div>
          <div class="metric">
            <strong>{summary["carry_forward_count"]}</strong>
            <span>carry-forward rows</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Confirmation ledger ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Auto-confirm disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Ledger Entries</h2>
      <p>
        Each ledger entry links a private receipt placeholder to owner-review and confirmation state.
      </p>
      <div class="grid">
        {ledger_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Carry-Forward Trail</h2>
        <p>Carry-forward rows prepare GP027 detail drawers. No confirmation triggers execution.</p>
        <div>
          {carry_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP026 prepares GP027 action receipt detail drawer depth.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP026 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["entries_route"])}</code>
        <code>{escape(summary["review_state_route"])}</code>
        <code>{escape(summary["receipt_links_route"])}</code>
        <code>{escape(summary["blockers_route"])}</code>
        <code>{escape(summary["carry_forward_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp026_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Confirmation Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Auto-confirm:
        <code>{str(truth["auto_confirmation_enabled"]).lower()}</code>.
        Execution after confirmation:
        <code>{str(truth["execution_after_confirmation_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_ledger_card(entry: Dict[str, Any]) -> str:
    status_class = "danger" if entry["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(entry["title"])}</div>
            <div class="meta">
              Ledger: <code>{escape(entry["ledger_id"])}</code><br>
              Receipt: <code>{escape(entry["receipt_id"])}</code><br>
              Lane: {escape(entry["lane"])}<br>
              Owner confirmed: <code>{str(entry["owner_confirmed"]).lower()}</code><br>
              Can execute: <code>{str(entry["can_execute_from_vault"]).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(entry["ledger_status"])}</span>
        </div>
      </article>
    """
