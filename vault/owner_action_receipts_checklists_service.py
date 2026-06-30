"""
VAULT GIANT PACK 025 — Owner Action Receipts / Checklists

NEW SECTION:
Archive Vault — Owner Action Receipt / Checklist Layer

This pack turns GP024 owner action execution-prep records into receipt/checklist depth.

Important truth:
- GP025 is not an execution engine.
- It does not execute actions automatically.
- It does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, public proof, seller/broker/trustee portals,
  financing decisions, legal advice, or Tower-owned permissions.
- It creates owner action receipt records, checklist rows, prep-to-receipt mapping,
  confirmation ledger seeds, receipt chain placeholders, blocked receipt reasons,
  and owner review status.
- It keeps Vault moving aggressively after GP024.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.owner_action_execution_prep_service import get_owner_action_execution_prep_payload


PACK_ID = "VAULT_GP025"
PACK_NAME = "Owner Action Receipts / Checklists"
SCHEMA_VERSION = "vault.owner_action_receipts_checklists.v1"

RECEIPT_STATUSES = {
    "RECEIPT_PLACEHOLDER_READY": "Receipt placeholder ready",
    "WAITING_OWNER_REVIEW": "Waiting owner review",
    "CHECKLIST_OPEN": "Checklist open",
    "BLOCKED_BY_TOWER_GATE": "Blocked by Tower gate",
    "HELD_METADATA_ONLY": "Held metadata only",
}

CHECKLIST_TYPES = {
    "owner_review": "Owner review",
    "tower_gate": "Tower gate",
    "blocked_reason": "Blocked reason",
    "receipt_placeholder": "Receipt placeholder",
    "carry_forward": "Carry forward",
}

RECEIPT_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "TOWER_STEP_UP_REQUIRED": "Tower step-up is required before sensitive action.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before action prep can move forward.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "NO_AUTO_ACTION_EXECUTION": "Automatic action execution is disabled.",
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault prepares and receipts actions but does not execute them.",
    "NO_PUBLIC_RECEIPT_PROOF": "Owner action receipts are private and not public proof.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

CHECKLIST_BLUEPRINTS = [
    {
        "checklist_type": "owner_review",
        "label": "Owner reviewed the prepared action",
        "tower_owned": False,
        "required": True,
    },
    {
        "checklist_type": "tower_gate",
        "label": "Tower gate status observed",
        "tower_owned": True,
        "required": True,
    },
    {
        "checklist_type": "blocked_reason",
        "label": "Blocked reasons preserved",
        "tower_owned": False,
        "required": True,
    },
    {
        "checklist_type": "receipt_placeholder",
        "label": "Receipt placeholder exists",
        "tower_owned": False,
        "required": True,
    },
    {
        "checklist_type": "carry_forward",
        "label": "Carry-forward status ready for next Vault depth",
        "tower_owned": False,
        "required": True,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_owner_action_receipts_payload() -> Dict[str, Any]:
    gp024 = get_owner_action_execution_prep_payload()
    prep_records = gp024["execution_prep_records"]

    receipt_records = [_build_receipt_record(record) for record in prep_records]
    checklist_rows = [
        row
        for receipt in receipt_records
        for row in receipt["checklist_rows"]
    ]
    prep_receipt_map = _build_prep_receipt_map(prep_records, receipt_records)
    confirmation_ledger = _build_confirmation_ledger(receipt_records)
    receipt_chain = _build_receipt_chain(receipt_records, checklist_rows)
    blocked_receipts = _build_blocked_receipts(receipt_records)
    owner_queue = _build_owner_queue(receipt_records, checklist_rows, blocked_receipts)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "owner_action_receipts_checklists",
            "section": "ARCHIVE_VAULT_OWNER_ACTION_RECEIPT_CHECKLIST_LAYER",
        },
        "receipt_truth": {
            "owner_action_receipts_enabled": True,
            "owner_action_checklists_enabled": True,
            "metadata_only": True,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
            "receipt_creation_is_placeholder_only": True,
            "private_receipt_only": True,
            "public_receipt_proof_enabled": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp025",
            "safe_next_unlock": "GP026 can deepen confirmation ledger without unlocking raw storage, external sharing, or execution.",
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
        "receipt_summary": {
            "room_title": "Vault Owner Action Receipts / Checklists",
            "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
            "route": "/vault/owner-action-receipts",
            "json_route": "/vault/owner-action-receipts.json",
            "records_route": "/vault/owner-action-receipt-records.json",
            "checklists_route": "/vault/owner-action-checklists.json",
            "map_route": "/vault/owner-action-prep-receipt-map.json",
            "confirmation_ledger_route": "/vault/owner-action-confirmation-ledger-seed.json",
            "chain_route": "/vault/owner-action-receipt-chain.json",
            "blocked_route": "/vault/owner-action-receipt-blocked.json",
            "owner_queue_route": "/vault/owner-action-receipt-owner-queue.json",
            "gp025_status_route": "/vault/gp025-status.json",
            "receipt_record_count": len(receipt_records),
            "checklist_row_count": len(checklist_rows),
            "prep_receipt_map_count": prep_receipt_map["mapping_count"],
            "confirmation_ledger_seed_count": confirmation_ledger["ledger_entry_count"],
            "receipt_chain_node_count": receipt_chain["chain_node_count"],
            "blocked_receipt_count": blocked_receipts["blocked_receipt_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "receipt_records": receipt_records,
        "checklist_rows": checklist_rows,
        "prep_receipt_map": prep_receipt_map,
        "confirmation_ledger_seed": confirmation_ledger,
        "receipt_chain": receipt_chain,
        "blocked_receipts": blocked_receipts,
        "owner_review_state": owner_queue,
        "gp024_connection": {
            "gp024_pack_id": gp024["pack"]["id"],
            "gp024_ready": gp024["gp024_status"]["ready"],
            "gp024_safe_to_continue": gp024["gp024_status"]["safe_to_continue_to_gp025"],
            "gp024_vault_done": gp024["gp024_status"]["vault_done"],
            "gp024_prep_record_count": gp024["execution_prep_summary"]["prep_record_count"],
        },
        "gp025_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp024_execution_prep_connected": True,
            "owner_action_receipts_ready": True,
            "owner_action_checklists_ready": True,
            "safe_to_continue_to_gp026": True,
            "vault_done": False,
            "metadata_only_receipts": True,
            "execution_engine_disabled": True,
            "receipt_creation_placeholder_only": True,
            "private_receipts_only": True,
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
            "public_receipt_proof_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp025",
            "next_pack": "VAULT_GP026_OWNER_CONFIRMATION_LEDGER_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_receipt_record(prep_record: Dict[str, Any]) -> Dict[str, Any]:
    blocked_codes = set(prep_record.get("blocked_codes", []))
    blocked_codes.update({
        "NO_PUBLIC_RECEIPT_PROOF",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "NO_AUTO_ACTION_EXECUTION",
        "CLOUDS_PARKED",
    })

    checklist_rows = [_build_checklist_row(prep_record, item, idx + 1) for idx, item in enumerate(CHECKLIST_BLUEPRINTS)]

    return {
        "receipt_id": f"VAR-{prep_record['prep_id'].replace('VEP-', '')}",
        "prep_id": prep_record["prep_id"],
        "source_step_id": prep_record["source_step_id"],
        "plan_packet_id": prep_record["plan_packet_id"],
        "plan_id": prep_record["plan_id"],
        "title": prep_record["title"],
        "lane": prep_record["lane"],
        "action_type": prep_record["action_type"],
        "action_type_label": prep_record["action_type_label"],
        "receipt_status": "RECEIPT_PLACEHOLDER_READY",
        "receipt_status_label": RECEIPT_STATUSES["RECEIPT_PLACEHOLDER_READY"],
        "metadata_only": True,
        "private_receipt_only": True,
        "public_proof_allowed": False,
        "receipt_created": False,
        "receipt_placeholder_ready": True,
        "owner_review_required": True,
        "owner_reviewed": False,
        "owner_confirmed": False,
        "tower_gate_observed": True,
        "tower_clearance_required": prep_record["tower_clearance_required"],
        "tower_step_up_required": prep_record["tower_step_up_required"],
        "can_execute_from_vault": False,
        "auto_execute_allowed": False,
        "raw_body_available": False,
        "external_share_allowed": False,
        "raw_export_allowed": False,
        "unredacted_export_allowed": False,
        "checklist_rows": checklist_rows,
        "checklist_row_count": len(checklist_rows),
        "checklist_complete_count": 0,
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [RECEIPT_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": f"Review receipt/checklist for {prep_record['title']} without executing or exporting.",
    }


def _build_checklist_row(prep_record: Dict[str, Any], blueprint: Dict[str, Any], sequence: int) -> Dict[str, Any]:
    blocked_codes = {
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    }

    if blueprint["tower_owned"] or prep_record.get("tower_clearance_required"):
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    if blueprint["checklist_type"] == "receipt_placeholder":
        blocked_codes.update({"NO_PUBLIC_RECEIPT_PROOF", "RAW_EXPORT_LOCKED", "UNREDACTED_EXPORT_LOCKED"})

    if blueprint["checklist_type"] == "blocked_reason":
        blocked_codes.update(prep_record.get("blocked_codes", []))

    return {
        "checklist_id": f"VAC-{prep_record['prep_id'].replace('VEP-', '')}-{sequence:02d}",
        "prep_id": prep_record["prep_id"],
        "receipt_id": f"VAR-{prep_record['prep_id'].replace('VEP-', '')}",
        "plan_packet_id": prep_record["plan_packet_id"],
        "title": prep_record["title"],
        "lane": prep_record["lane"],
        "checklist_type": blueprint["checklist_type"],
        "checklist_type_label": CHECKLIST_TYPES[blueprint["checklist_type"]],
        "label": blueprint["label"],
        "sequence": sequence,
        "required": blueprint["required"],
        "tower_owned": blueprint["tower_owned"],
        "status": "OPEN",
        "completed": False,
        "owner_review_required": True,
        "owner_confirmed": False,
        "can_auto_complete": False,
        "can_execute_from_vault": False,
        "metadata_only": True,
        "blocked_codes": sorted(blocked_codes),
    }


def _build_prep_receipt_map(prep_records: List[Dict[str, Any]], receipt_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    receipt_by_prep = {receipt["prep_id"]: receipt for receipt in receipt_records}

    mappings = [
        {
            "mapping_id": f"VPM-{record['prep_id'].replace('VEP-', '')}",
            "prep_id": record["prep_id"],
            "source_step_id": record["source_step_id"],
            "receipt_id": receipt_by_prep[record["prep_id"]]["receipt_id"],
            "plan_packet_id": record["plan_packet_id"],
            "lane": record["lane"],
            "mapping_status": "MAPPED_PLACEHOLDER_ONLY",
            "receipt_created": False,
            "can_execute_from_vault": False,
            "safe_to_carry_to_gp026": True,
        }
        for record in prep_records
    ]

    return {
        "mappings": mappings,
        "mapping_count": len(mappings),
        "all_prep_records_mapped": len(mappings) == len(prep_records),
        "receipt_created_count": 0,
        "execution_allowed_count": 0,
        "safe_to_carry_to_gp026": True,
    }


def _build_confirmation_ledger(receipt_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    entries = [
        {
            "ledger_entry_id": f"VCL-{receipt['receipt_id'].replace('VAR-', '')}",
            "receipt_id": receipt["receipt_id"],
            "prep_id": receipt["prep_id"],
            "title": receipt["title"],
            "lane": receipt["lane"],
            "ledger_status": "SEEDED_WAITING_OWNER_CONFIRMATION",
            "owner_reviewed": False,
            "owner_confirmed": False,
            "auto_confirm_allowed": False,
            "can_execute_after_confirmation": False,
            "public_proof_allowed": False,
        }
        for receipt in receipt_records
    ]

    return {
        "ledger_entries": entries,
        "ledger_entry_count": len(entries),
        "waiting_owner_confirmation_count": len(entries),
        "owner_confirmed_count": 0,
        "auto_confirm_allowed": False,
        "execution_after_confirmation_allowed": False,
        "safe_to_deepen_in_gp026": True,
    }


def _build_receipt_chain(receipt_records: List[Dict[str, Any]], checklist_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    checklist_count_by_receipt = {}
    for row in checklist_rows:
        checklist_count_by_receipt[row["receipt_id"]] = checklist_count_by_receipt.get(row["receipt_id"], 0) + 1

    nodes = [
        {
            "chain_node_id": f"VRC-{receipt['receipt_id'].replace('VAR-', '')}",
            "receipt_id": receipt["receipt_id"],
            "prep_id": receipt["prep_id"],
            "source_step_id": receipt["source_step_id"],
            "title": receipt["title"],
            "lane": receipt["lane"],
            "chain_status": "PLACEHOLDER_CHAIN_NODE",
            "checklist_row_count": checklist_count_by_receipt.get(receipt["receipt_id"], 0),
            "receipt_created": False,
            "raw_export_allowed": False,
            "unredacted_export_allowed": False,
            "public_proof_allowed": False,
            "external_share_allowed": False,
        }
        for receipt in receipt_records
    ]

    return {
        "chain_nodes": nodes,
        "chain_node_count": len(nodes),
        "placeholder_chain_node_count": len(nodes),
        "receipt_created_count": 0,
        "raw_export_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "external_share_allowed_count": 0,
    }


def _build_blocked_receipts(receipt_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for receipt in receipt_records for code in receipt["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": RECEIPT_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_receipt_count": sum(1 for receipt in receipt_records if code in receipt["blocked_codes"]),
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]

    return {
        "blocked_receipts": blockers,
        "blocked_receipt_count": len(blockers),
        "all_blocked_receipts_safe": True,
        "auto_override_allowed": False,
        "all_restricted_paths_locked": True,
        "execution_from_vault_allowed": False,
        "public_receipt_proof_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only receipt/checklist review. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "TOWER_STEP_UP_REQUIRED": "Tower must own step-up before sensitive action.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before receipt/checklist closure.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault receipts actions but does not execute them.",
        "NO_PUBLIC_RECEIPT_PROOF": "Keep owner action receipts private.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP025.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_queue(
    receipt_records: List[Dict[str, Any]],
    checklist_rows: List[Dict[str, Any]],
    blocked_receipts: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "OAR-ACTION-001",
            "label": "Review owner action receipt placeholders.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAR-ACTION-002",
            "label": "Review checklist rows without marking execution complete.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAR-ACTION-003",
            "label": "Keep Tower gate checks, step-up, portals, exports, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAR-ACTION-004",
            "label": "Keep owner action receipts private, not public proof.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAR-ACTION-005",
            "label": "Continue Vault into GP026 owner confirmation ledger.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Owner Action Receipts / Checklists",
        "section_header": "Archive Vault — Owner Action Receipt / Checklist Layer",
        "actions": actions,
        "action_count": len(actions),
        "receipt_record_count": len(receipt_records),
        "checklist_row_count": len(checklist_rows),
        "blocked_receipt_count": blocked_receipts["blocked_receipt_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review owner action receipt placeholders.",
            "Review checklist rows without marking execution complete.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP026 owner confirmation ledger.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_owner_action_receipts_payload())


def get_owner_action_receipts_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_truth": payload["receipt_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "receipt_summary": payload["receipt_summary"],
        "gp024_connection": payload["gp024_connection"],
    }


def get_owner_action_receipt_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_records": payload["receipt_records"],
        "receipt_record_count": len(payload["receipt_records"]),
    }


def get_owner_action_checklists() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "checklist_rows": payload["checklist_rows"],
        "checklist_row_count": len(payload["checklist_rows"]),
    }


def get_owner_action_prep_receipt_map() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "prep_receipt_map": payload["prep_receipt_map"],
    }


def get_owner_action_confirmation_ledger_seed() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "confirmation_ledger_seed": payload["confirmation_ledger_seed"],
    }


def get_owner_action_receipt_chain() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_chain": payload["receipt_chain"],
    }


def get_owner_action_receipt_blocked() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocked_receipts": payload["blocked_receipts"],
    }


def get_owner_action_receipt_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp025_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp025_status": payload["gp025_status"],
        "receipt_truth": payload["receipt_truth"],
        "receipt_summary": payload["receipt_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp024_connection": payload["gp024_connection"],
    }


def render_owner_action_receipts_page() -> str:
    payload = clone_payload()
    summary = payload["receipt_summary"]
    truth = payload["receipt_truth"]
    receipts = payload["receipt_records"]
    chain = payload["receipt_chain"]
    owner = payload["owner_review_state"]

    receipt_cards = "\n".join(_render_receipt_card(record) for record in receipts[:9])
    chain_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(node["title"])}</strong>
            <span>{escape(node["chain_status"])} · checklist rows: {node["checklist_row_count"]}</span>
          </div>
          <div class="pill warn">Private placeholder</div>
        </div>
        """
        for node in chain["chain_nodes"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Owner Action Receipts / Checklists · GP025</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 025</div>
        <h1>Owner Action Receipts / Checklists</h1>
        <p class="hero-copy">
          GP025 starts the Owner Action Receipt / Checklist Layer. It turns GP024 execution-prep records into
          private receipt placeholders, checklist rows, prep-to-receipt mapping, confirmation ledger seeds,
          and receipt chain placeholders without executing actions, unlocking raw storage, sharing externally,
          exporting raw/unredacted data, or creating public proof.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["receipt_record_count"]}</strong>
            <span>receipt records</span>
          </div>
          <div class="metric">
            <strong>{summary["checklist_row_count"]}</strong>
            <span>checklist rows</span>
          </div>
          <div class="metric">
            <strong>{summary["confirmation_ledger_seed_count"]}</strong>
            <span>ledger seeds</span>
          </div>
          <div class="metric">
            <strong>{summary["receipt_chain_node_count"]}</strong>
            <span>chain nodes</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Receipt layer started</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Private receipts only</span>
          <span class="pill danger">Execution disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Receipt Records</h2>
      <p>
        Each receipt is a private placeholder tied back to a GP024 execution-prep record.
      </p>
      <div class="grid">
        {receipt_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Receipt Chain</h2>
        <p>Receipt chain nodes are placeholders only. No raw export, public proof, or external sharing.</p>
        <div>
          {chain_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP025 prepares GP026 owner confirmation ledger depth.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP025 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["records_route"])}</code>
        <code>{escape(summary["checklists_route"])}</code>
        <code>{escape(summary["map_route"])}</code>
        <code>{escape(summary["confirmation_ledger_route"])}</code>
        <code>{escape(summary["chain_route"])}</code>
        <code>{escape(summary["blocked_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp025_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Receipt Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Private receipts only:
        <code>{str(truth["private_receipt_only"]).lower()}</code>.
        Public receipt proof:
        <code>{str(truth["public_receipt_proof_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_receipt_card(record: Dict[str, Any]) -> str:
    status_class = "danger" if record["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record["title"])}</div>
            <div class="meta">
              Receipt: <code>{escape(record["receipt_id"])}</code><br>
              Prep: <code>{escape(record["prep_id"])}</code><br>
              Lane: {escape(record["lane"])}<br>
              Checklist rows: <code>{record["checklist_row_count"]}</code><br>
              Public proof: <code>{str(record["public_proof_allowed"]).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(record["receipt_status"])}</span>
        </div>
      </article>
    """
