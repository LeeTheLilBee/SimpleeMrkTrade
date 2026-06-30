"""
VAULT GIANT PACK 024 — Owner Action Execution Prep

This pack turns GP023 action plans into execution-prep records.

Important truth:
- GP024 is not an execution engine.
- It does not execute actions automatically.
- It does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, public proof, seller/broker/trustee portals,
  financing decisions, legal advice, or Tower-owned permissions.
- It creates owner confirmation prep records, Tower gate checks, pre-execution blockers,
  execution receipt placeholders, and a safe action readiness queue.
- It keeps Vault moving aggressively after GP023.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, external access, and action authority gates.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.packet_action_plan_service import get_packet_action_plan_payload


PACK_ID = "VAULT_GP024"
PACK_NAME = "Owner Action Execution Prep"
SCHEMA_VERSION = "vault.owner_action_execution_prep.v1"

PREP_STATUSES = {
    "READY_FOR_OWNER_PREP_REVIEW": "Ready for owner prep review",
    "WAITING_OWNER_CONFIRMATION": "Waiting owner confirmation",
    "BLOCKED_BY_TOWER_GATE": "Blocked by Tower gate",
    "BLOCKED_BY_STORAGE_PROVIDER": "Blocked by storage provider",
    "HELD_METADATA_ONLY": "Held metadata only",
}

PREP_BLOCK_CODES = {
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
    "NO_ACTION_EXECUTION_FROM_VAULT": "Vault prepares actions but does not execute them.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

EXECUTION_PREP_PHASES = [
    {
        "phase_id": "owner_confirmation",
        "label": "Owner confirmation",
        "owner": "Vault",
        "tower_owned": False,
        "auto_run_allowed": False,
    },
    {
        "phase_id": "tower_gate_check",
        "label": "Tower gate check",
        "owner": "The Tower",
        "tower_owned": True,
        "auto_run_allowed": False,
    },
    {
        "phase_id": "blocked_reason_review",
        "label": "Blocked reason review",
        "owner": "Vault",
        "tower_owned": False,
        "auto_run_allowed": False,
    },
    {
        "phase_id": "receipt_placeholder",
        "label": "Receipt placeholder",
        "owner": "Vault",
        "tower_owned": False,
        "auto_run_allowed": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_owner_action_execution_prep_payload() -> Dict[str, Any]:
    gp023 = get_packet_action_plan_payload()
    action_plans = gp023["action_plan_board"]["action_plans"]
    action_steps = gp023["action_steps"]

    prep_records = [_build_prep_record(step, action_plans) for step in action_steps]
    confirmation_queue = _build_confirmation_queue(prep_records)
    tower_gate_matrix = _build_tower_gate_matrix(prep_records)
    receipt_placeholders = _build_receipt_placeholders(prep_records)
    blocked_prep = _build_blocked_prep(prep_records)
    readiness_queue = _build_readiness_queue(prep_records, confirmation_queue, tower_gate_matrix)
    owner_queue = _build_owner_queue(prep_records, readiness_queue, blocked_prep)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "owner_action_execution_prep",
        },
        "execution_prep_truth": {
            "owner_action_execution_prep_enabled": True,
            "metadata_only": True,
            "execution_engine_enabled": False,
            "auto_action_execution_enabled": False,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp024",
            "safe_next_unlock": "GP025 can deepen owner action receipts/checklists without unlocking raw storage or external sharing.",
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
        "execution_prep_summary": {
            "room_title": "Vault Owner Action Execution Prep",
            "route": "/vault/owner-action-execution-prep",
            "json_route": "/vault/owner-action-execution-prep.json",
            "records_route": "/vault/owner-action-execution-prep-records.json",
            "confirmation_route": "/vault/owner-action-execution-prep-confirmations.json",
            "tower_gates_route": "/vault/owner-action-execution-prep-tower-gates.json",
            "receipts_route": "/vault/owner-action-execution-prep-receipts.json",
            "blocked_route": "/vault/owner-action-execution-prep-blocked.json",
            "readiness_route": "/vault/owner-action-execution-prep-readiness.json",
            "owner_queue_route": "/vault/owner-action-execution-prep-owner-queue.json",
            "gp024_status_route": "/vault/gp024-status.json",
            "prep_record_count": len(prep_records),
            "confirmation_count": confirmation_queue["confirmation_count"],
            "tower_gate_count": tower_gate_matrix["gate_count"],
            "receipt_placeholder_count": receipt_placeholders["receipt_placeholder_count"],
            "blocked_prep_count": blocked_prep["blocked_prep_count"],
            "readiness_item_count": readiness_queue["readiness_item_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "execution_prep_records": prep_records,
        "confirmation_queue": confirmation_queue,
        "tower_gate_matrix": tower_gate_matrix,
        "receipt_placeholders": receipt_placeholders,
        "blocked_prep": blocked_prep,
        "readiness_queue": readiness_queue,
        "owner_review_state": owner_queue,
        "gp023_connection": {
            "gp023_pack_id": gp023["pack"]["id"],
            "gp023_ready": gp023["gp023_status"]["ready"],
            "gp023_safe_to_continue": gp023["gp023_status"]["safe_to_continue_to_gp024"],
            "gp023_vault_done": gp023["gp023_status"]["vault_done"],
            "gp023_action_step_count": gp023["action_summary"]["action_step_count"],
        },
        "gp024_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp023_packet_action_plan_connected": True,
            "owner_action_execution_prep_ready": True,
            "safe_to_continue_to_gp025": True,
            "vault_done": False,
            "metadata_only_execution_prep": True,
            "execution_engine_disabled": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp024",
            "next_pack": "VAULT_GP025_OWNER_ACTION_RECEIPTS_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_prep_record(step: Dict[str, Any], action_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    plan = _plan_for_step(step, action_plans)
    phase_records = [_build_phase_record(step, phase) for phase in EXECUTION_PREP_PHASES]

    blocked_codes = set(step.get("blocked_codes", []))
    blocked_codes.update({
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
        "CLOUDS_PARKED",
    })

    if step.get("tower_owned"):
        blocked_codes.update({"TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"})

    if step.get("raw_body_required"):
        blocked_codes.update({"RAW_FILE_BODY_LOCKED", "PERMANENT_STORAGE_NOT_CONFIGURED", "NO_RAW_VERIFICATION_CLAIM"})

    return {
        "prep_id": f"VEP-{step['step_id'].replace('VAS-', '')}",
        "source_step_id": step["step_id"],
        "source_gap_id": step.get("gap_id"),
        "plan_packet_id": step["plan_packet_id"],
        "plan_id": plan.get("plan_id"),
        "title": plan.get("title", step["plan_packet_id"]),
        "lane": plan.get("lane", "Unknown"),
        "action_type": step["action_type"],
        "action_type_label": step["action_type_label"],
        "label": step["label"],
        "sequence": step["sequence"],
        "prep_status": "READY_FOR_OWNER_PREP_REVIEW",
        "prep_status_label": PREP_STATUSES["READY_FOR_OWNER_PREP_REVIEW"],
        "metadata_only": True,
        "owner_required": True,
        "owner_confirmed": False,
        "tower_owned": bool(step.get("tower_owned")),
        "tower_clearance_required": bool(step.get("tower_owned")) or "TOWER_CLEARANCE_REQUIRED" in blocked_codes,
        "tower_step_up_required": bool(step.get("tower_owned")),
        "can_execute_from_vault": False,
        "auto_execute_allowed": False,
        "raw_body_required": bool(step.get("raw_body_required")),
        "raw_body_available": False,
        "external_share_allowed": False,
        "receipt_placeholder_required": True,
        "receipt_created": False,
        "phase_records": phase_records,
        "phase_count": len(phase_records),
        "blocked_codes": sorted(blocked_codes),
        "blocked_labels": [PREP_BLOCK_CODES.get(code, code) for code in sorted(blocked_codes)],
        "owner_note": step.get("owner_note", "Review action prep safely."),
    }


def _plan_for_step(step: Dict[str, Any], action_plans: List[Dict[str, Any]]) -> Dict[str, Any]:
    for plan in action_plans:
        if plan["packet_id"] == step["plan_packet_id"]:
            return plan
    return {}


def _build_phase_record(step: Dict[str, Any], phase: Dict[str, Any]) -> Dict[str, Any]:
    blocked_codes = [
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_ACTION_EXECUTION",
        "NO_ACTION_EXECUTION_FROM_VAULT",
    ]

    if phase["tower_owned"] or step.get("tower_owned"):
        blocked_codes.extend(["TOWER_CLEARANCE_REQUIRED", "TOWER_STEP_UP_REQUIRED"])

    if phase["phase_id"] == "receipt_placeholder":
        blocked_codes.append("RAW_EXPORT_LOCKED")

    return {
        "phase_record_id": f"{step['step_id']}__{phase['phase_id']}",
        "phase_id": phase["phase_id"],
        "label": phase["label"],
        "owner": phase["owner"],
        "tower_owned": phase["tower_owned"],
        "phase_status": "PREP_ONLY_NOT_EXECUTED",
        "owner_confirmed": False,
        "auto_run_allowed": phase["auto_run_allowed"],
        "can_execute_from_vault": False,
        "blocked_codes": sorted(set(blocked_codes)),
    }


def _build_confirmation_queue(prep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    confirmations = [
        {
            "confirmation_id": f"VOC-{record['prep_id'].replace('VEP-', '')}",
            "prep_id": record["prep_id"],
            "title": record["title"],
            "label": record["label"],
            "lane": record["lane"],
            "confirmation_status": "WAITING_OWNER_CONFIRMATION",
            "owner_confirmed": False,
            "auto_confirm_allowed": False,
            "can_execute_after_confirmation": False,
            "reason_execution_blocked": "Vault GP024 prepares the action but does not execute it.",
        }
        for record in prep_records
        if record["owner_required"]
    ]

    return {
        "confirmations": confirmations,
        "confirmation_count": len(confirmations),
        "waiting_owner_confirmation_count": len(confirmations),
        "owner_confirmed_count": 0,
        "auto_confirm_allowed": False,
        "execution_after_confirmation_allowed": False,
    }


def _build_tower_gate_matrix(prep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    gates = [
        {
            "gate_id": f"VTG-{record['prep_id'].replace('VEP-', '')}",
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "gate_type": "tower_clearance_and_step_up" if record["tower_clearance_required"] else "tower_guard_observed",
            "tower_owned": True,
            "gate_status": "LOCKED_OR_OBSERVED",
            "clearance_required": record["tower_clearance_required"],
            "step_up_required": record["tower_step_up_required"],
            "vault_can_override": False,
            "external_access_allowed": False,
            "export_allowed": False,
            "portal_access_allowed": False,
        }
        for record in prep_records
    ]

    return {
        "gates": gates,
        "gate_count": len(gates),
        "tower_owned_gate_count": len(gates),
        "clearance_required_count": sum(1 for gate in gates if gate["clearance_required"]),
        "step_up_required_count": sum(1 for gate in gates if gate["step_up_required"]),
        "vault_override_allowed_count": 0,
        "all_tower_gates_preserved": True,
    }


def _build_receipt_placeholders(prep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    placeholders = [
        {
            "receipt_placeholder_id": f"VRP-{record['prep_id'].replace('VEP-', '')}",
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "receipt_type": "owner_action_execution_prep_receipt",
            "receipt_status": "PLACEHOLDER_ONLY",
            "receipt_created": False,
            "raw_export_allowed": False,
            "unredacted_export_allowed": False,
            "public_proof_allowed": False,
            "owner_review_required": True,
        }
        for record in prep_records
        if record["receipt_placeholder_required"]
    ]

    return {
        "receipt_placeholders": placeholders,
        "receipt_placeholder_count": len(placeholders),
        "receipt_created_count": 0,
        "raw_export_allowed_count": 0,
        "unredacted_export_allowed_count": 0,
        "public_proof_allowed_count": 0,
        "owner_review_required": True,
    }


def _build_blocked_prep(prep_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for record in prep_records for code in record["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": PREP_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "TOWER_STEP_UP_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "affected_prep_count": sum(1 for record in prep_records if code in record["blocked_codes"]),
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]

    return {
        "blocked_prep": blockers,
        "blocked_prep_count": len(blockers),
        "all_blocked_prep_safe": True,
        "auto_override_allowed": False,
        "all_restricted_paths_locked": True,
        "execution_from_vault_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only execution prep. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "TOWER_STEP_UP_REQUIRED": "Tower must own step-up before sensitive action.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before action prep.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_ACTION_EXECUTION": "Do not auto-execute actions.",
        "NO_ACTION_EXECUTION_FROM_VAULT": "Vault prepares actions but does not execute them.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP024.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_readiness_queue(
    prep_records: List[Dict[str, Any]],
    confirmation_queue: Dict[str, Any],
    tower_gate_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    readiness_items = [
        {
            "readiness_id": f"VER-{record['prep_id'].replace('VEP-', '')}",
            "prep_id": record["prep_id"],
            "title": record["title"],
            "lane": record["lane"],
            "readiness_status": "PREP_READY_EXECUTION_BLOCKED",
            "owner_confirmation_ready": True,
            "owner_confirmed": False,
            "tower_gate_observed": True,
            "tower_clearance_required": record["tower_clearance_required"],
            "can_execute_from_vault": False,
            "safe_to_carry_to_gp025": True,
        }
        for record in prep_records
    ]

    return {
        "readiness_items": readiness_items,
        "readiness_item_count": len(readiness_items),
        "prep_ready_count": len(readiness_items),
        "execution_allowed_count": 0,
        "owner_confirmation_ready_count": confirmation_queue["confirmation_count"],
        "tower_gate_observed_count": tower_gate_matrix["gate_count"],
        "safe_to_carry_to_gp025": True,
    }


def _build_owner_queue(
    prep_records: List[Dict[str, Any]],
    readiness_queue: Dict[str, Any],
    blocked_prep: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "OAEP-ACTION-001",
            "label": "Review owner confirmation prep records.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAEP-ACTION-002",
            "label": "Confirm no Vault action executes automatically.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAEP-ACTION-003",
            "label": "Keep Tower gate checks, step-up, portals, exports, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAEP-ACTION-004",
            "label": "Review receipt placeholders without creating public proof or raw export.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OAEP-ACTION-005",
            "label": "Continue Vault into GP025 owner action receipts/checklists.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Owner Action Execution Prep",
        "actions": actions,
        "action_count": len(actions),
        "prep_record_count": len(prep_records),
        "readiness_item_count": readiness_queue["readiness_item_count"],
        "blocked_prep_count": blocked_prep["blocked_prep_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review owner confirmation prep records.",
            "Confirm no Vault action executes automatically.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP025 owner action receipts/checklists.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_owner_action_execution_prep_payload())


def get_owner_action_execution_prep_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "execution_prep_truth": payload["execution_prep_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "execution_prep_summary": payload["execution_prep_summary"],
        "gp023_connection": payload["gp023_connection"],
    }


def get_owner_action_execution_prep_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "execution_prep_records": payload["execution_prep_records"],
        "prep_record_count": len(payload["execution_prep_records"]),
    }


def get_owner_action_execution_prep_confirmations() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "confirmation_queue": payload["confirmation_queue"],
    }


def get_owner_action_execution_prep_tower_gates() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "tower_gate_matrix": payload["tower_gate_matrix"],
    }


def get_owner_action_execution_prep_receipts() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "receipt_placeholders": payload["receipt_placeholders"],
    }


def get_owner_action_execution_prep_blocked() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocked_prep": payload["blocked_prep"],
    }


def get_owner_action_execution_prep_readiness() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "readiness_queue": payload["readiness_queue"],
    }


def get_owner_action_execution_prep_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp024_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp024_status": payload["gp024_status"],
        "execution_prep_truth": payload["execution_prep_truth"],
        "execution_prep_summary": payload["execution_prep_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp023_connection": payload["gp023_connection"],
    }


def render_owner_action_execution_prep_page() -> str:
    payload = clone_payload()
    summary = payload["execution_prep_summary"]
    truth = payload["execution_prep_truth"]
    records = payload["execution_prep_records"]
    tower_gates = payload["tower_gate_matrix"]
    owner = payload["owner_review_state"]

    record_cards = "\n".join(_render_prep_record_card(record) for record in records[:9])
    gate_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(gate["title"])}</strong>
            <span>{escape(gate["gate_type"])} · clearance required: {str(gate["clearance_required"]).lower()}</span>
          </div>
          <div class="pill danger">Tower gate</div>
        </div>
        """
        for gate in tower_gates["gates"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Owner Action Execution Prep · GP024</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 024</div>
        <h1>Owner Action Execution Prep</h1>
        <p class="hero-copy">
          GP024 prepares owner action execution records without executing anything. It adds owner confirmations,
          Tower gate checks, receipt placeholders, readiness records, and blocked-prep reasons while keeping raw storage,
          direct upload, external access, portals, exports, public proof, financing decisions, legal advice, and raw verification claims locked.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["prep_record_count"]}</strong>
            <span>prep records</span>
          </div>
          <div class="metric">
            <strong>{summary["confirmation_count"]}</strong>
            <span>confirmations</span>
          </div>
          <div class="metric">
            <strong>{summary["tower_gate_count"]}</strong>
            <span>Tower gates</span>
          </div>
          <div class="metric">
            <strong>{summary["receipt_placeholder_count"]}</strong>
            <span>receipt placeholders</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Execution prep ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner confirmation required</span>
          <span class="pill danger">Execution disabled</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Execution Prep Records</h2>
      <p>
        These records prepare owner review. They do not execute actions.
      </p>
      <div class="grid">
        {record_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Tower Gate Matrix</h2>
        <p>Tower keeps clearance, step-up, external access, portals, and export authority.</p>
        <div>
          {gate_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP024 prepares GP025 owner action receipts/checklists.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP024 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["records_route"])}</code>
        <code>{escape(summary["confirmation_route"])}</code>
        <code>{escape(summary["tower_gates_route"])}</code>
        <code>{escape(summary["receipts_route"])}</code>
        <code>{escape(summary["blocked_route"])}</code>
        <code>{escape(summary["readiness_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp024_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Execution Prep Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Execution engine:
        <code>{str(truth["execution_engine_enabled"]).lower()}</code>.
        Auto execution:
        <code>{str(truth["auto_action_execution_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_prep_record_card(record: Dict[str, Any]) -> str:
    status_class = "danger" if record["tower_clearance_required"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record["title"])}</div>
            <div class="meta">
              Prep: <code>{escape(record["prep_id"])}</code><br>
              Step: <code>{escape(record["source_step_id"])}</code><br>
              Lane: {escape(record["lane"])}<br>
              Type: {escape(record["action_type_label"])}<br>
              Can execute: <code>{str(record["can_execute_from_vault"]).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(record["prep_status"])}</span>
        </div>
      </article>
    """
