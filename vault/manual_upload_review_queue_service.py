"""
VAULT GIANT PACK 014 — Manual Upload Review Queue

This pack creates the owner-facing manual upload review layer after GP013.

Important truth:
- This is a review queue for staged upload decisions.
- It does not unlock direct raw upload.
- It does not configure permanent file-body storage.
- It does not provide raw download, unredacted preview, or external access.
- It prepares records for later version/replace/supersede flows.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  and external access authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List, Tuple

from vault.document_type_classifier_service import get_document_type_classifier_payload


PACK_ID = "VAULT_GP014"
PACK_NAME = "Manual Upload Review Queue"
SCHEMA_VERSION = "vault.manual_upload_review_queue.v1"

REVIEW_STATUSES = {
    "READY_FOR_OWNER_UPLOAD_REVIEW": "Ready for owner upload review",
    "NEEDS_PACKET_CONFIRMATION": "Needs packet confirmation",
    "NEEDS_REQUIREMENT_CONFIRMATION": "Needs requirement confirmation",
    "NEEDS_REDACTION_CONFIRMATION": "Needs redaction confirmation",
    "BLOCKED_TOWER_CLEARANCE": "Blocked by Tower clearance",
    "BLOCKED_STORAGE_PROVIDER": "Blocked by storage provider",
    "HELD_METADATA_ONLY": "Held metadata only",
}

REVIEW_DECISIONS = {
    "HOLD_METADATA_ONLY": "Hold metadata only",
    "REQUEST_TOWER_CLEARANCE": "Request Tower clearance",
    "CONFIRM_PACKET_REQUIREMENT_MATCH": "Confirm packet and requirement match",
    "SEND_TO_REDACTION_REVIEW": "Send to redaction review",
    "READY_FOR_VERSION_FLOW": "Ready for GP015 version flow",
    "DO_NOT_FILE": "Do not file",
}

UPLOAD_REVIEW_BLOCK_CODES = {
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "RAW_FILE_BODY_LOCKED": "Raw file body remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive upload completion.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before filing.",
    "REDACTION_CONFIRMATION_REQUIRED": "Redaction confirmation is required before preview/export.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_PREVIEW_LOCKED": "Unredacted preview is locked.",
    "NO_AUTO_FILE_COMPLETION": "Auto-file completion is disabled.",
}

UPLOAD_REVIEW_CHECKLIST = [
    {
        "check_id": "VUR-CHECK-001",
        "label": "Confirm intake record is connected.",
        "required": True,
        "tower_owned": False,
    },
    {
        "check_id": "VUR-CHECK-002",
        "label": "Confirm attachment metadata slot is connected.",
        "required": True,
        "tower_owned": False,
    },
    {
        "check_id": "VUR-CHECK-003",
        "label": "Confirm classifier prediction is metadata-only.",
        "required": True,
        "tower_owned": False,
    },
    {
        "check_id": "VUR-CHECK-004",
        "label": "Confirm packet and requirement match.",
        "required": True,
        "tower_owned": False,
    },
    {
        "check_id": "VUR-CHECK-005",
        "label": "Confirm redaction review requirement.",
        "required": True,
        "tower_owned": False,
    },
    {
        "check_id": "VUR-CHECK-006",
        "label": "Confirm Tower clearance before sensitive movement.",
        "required": True,
        "tower_owned": True,
    },
    {
        "check_id": "VUR-CHECK-007",
        "label": "Confirm direct upload remains locked.",
        "required": True,
        "tower_owned": True,
    },
    {
        "check_id": "VUR-CHECK-008",
        "label": "Confirm external access remains denied.",
        "required": True,
        "tower_owned": True,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_manual_upload_review_payload() -> Dict[str, Any]:
    gp013 = get_document_type_classifier_payload()
    classification_records = gp013["classification_records"]

    review_items = [
        _build_review_item(record)
        for record in classification_records
    ]

    decision_board = _build_decision_board(review_items)
    blocked_reasons = _build_blocked_reasons(review_items)
    checklist_state = _build_checklist_state(review_items)
    owner_queue = _build_owner_queue(review_items, decision_board, checklist_state)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP011", "VAULT_GP012", "VAULT_GP013"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "manual_upload_review_owner_queue",
        },
        "manual_upload_truth": {
            "manual_review_enabled": True,
            "direct_upload_unlocked": False,
            "raw_file_body_storage_enabled": False,
            "provider_configured": False,
            "upload_body_write_enabled": False,
            "download_enabled": False,
            "unredacted_preview_enabled": False,
            "external_access_enabled": False,
            "auto_file_completion_enabled": False,
            "fake_upload_complete": False,
            "safe_next_unlock": "GP015 version history and replace/supersede flow can use review decisions without raw upload storage.",
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "sensitive_body_display_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "public_ob_proof_allowed": False,
            "ai_generated_soulaana_or_black_woman_character_art_allowed": False,
        },
        "tower_authority": {
            "tower_owns_identity": True,
            "tower_owns_permissions": True,
            "tower_owns_clearance": True,
            "tower_owns_step_up": True,
            "tower_owns_export_locks": True,
            "tower_owns_freeze_revoke": True,
            "tower_owns_external_access": True,
            "vault_owns_tower_permissions": False,
        },
        "review_summary": {
            "room_title": "Vault Manual Upload Review",
            "route": "/vault/manual-upload-review",
            "json_route": "/vault/manual-upload-review.json",
            "queue_route": "/vault/manual-upload-review-queue.json",
            "decisions_route": "/vault/upload-review-decisions.json",
            "checklist_route": "/vault/upload-review-checklist.json",
            "blocked_reasons_route": "/vault/upload-review-blocked-reasons.json",
            "gp014_status_route": "/vault/gp014-status.json",
            "review_item_count": len(review_items),
            "decision_count": len(decision_board["decision_items"]),
            "blocked_reason_count": len(blocked_reasons),
            "checklist_count": len(UPLOAD_REVIEW_CHECKLIST),
            "raw_body_storage_enabled": False,
            "direct_upload_unlocked": False,
        },
        "manual_upload_review_queue": {
            "review_room": "Vault Manual Upload Review",
            "review_items": review_items,
            "review_count": len(review_items),
            "needs_owner_review_count": sum(1 for item in review_items if item["needs_owner_review"]),
            "needs_tower_clearance_count": sum(1 for item in review_items if item["needs_tower_clearance"]),
            "ready_for_gp015_count": sum(1 for item in review_items if item["ready_for_gp015_version_flow"]),
        },
        "upload_review_decisions": decision_board,
        "upload_review_checklist": checklist_state,
        "upload_review_blocked_reasons": blocked_reasons,
        "owner_review_state": owner_queue,
        "gp014_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp015": True,
            "next_pack": "VAULT_GP015_VERSION_HISTORY_REPLACE_SUPERSEDE_FLOW",
            "gp013_classifier_records_connected": True,
            "manual_review_queue_ready": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "fake_upload_completion_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp014",
        },
    }

    return payload


def _build_review_item(record: Dict[str, Any]) -> Dict[str, Any]:
    status, decision, blocked_codes, owner_action = _review_state_from_classifier(record)

    checks = _build_item_checks(record, blocked_codes)

    return {
        "review_id": f"VUR-{record['attachment_id'].replace('VAT-', '')}",
        "classification_id": record["classification_id"],
        "attachment_id": record["attachment_id"],
        "intake_id": record["intake_id"],
        "lane": record["lane"],
        "packet_id": record["packet_id"],
        "requirement_id": record["requirement_id"],
        "predicted_document_type": record["predicted_document_type"],
        "predicted_document_label": record["predicted_document_label"],
        "classification_status": record["classification_status"],
        "requirement_match_status": record["requirement_match"]["match_status"],
        "review_status": status,
        "review_status_label": REVIEW_STATUSES.get(status, status),
        "recommended_decision": decision,
        "recommended_decision_label": REVIEW_DECISIONS.get(decision, decision),
        "needs_owner_review": True,
        "needs_tower_clearance": "TOWER_CLEARANCE_REQUIRED" in blocked_codes,
        "needs_redaction_confirmation": "REDACTION_CONFIRMATION_REQUIRED" in blocked_codes,
        "ready_for_gp015_version_flow": decision in {
            "CONFIRM_PACKET_REQUIREMENT_MATCH",
            "SEND_TO_REDACTION_REVIEW",
            "READY_FOR_VERSION_FLOW",
            "HOLD_METADATA_ONLY",
        },
        "manual_review_checks": checks,
        "checks_required_count": len(checks),
        "checks_passed_count": sum(1 for check in checks if check["passed"]),
        "blocked_codes": blocked_codes,
        "blocked_labels": [UPLOAD_REVIEW_BLOCK_CODES.get(code, code) for code in blocked_codes],
        "owner_action": owner_action,
        "upload_body_state": {
            "body_present": False,
            "body_write_allowed": False,
            "body_read_allowed": False,
            "direct_upload_allowed": False,
            "provider_configured": False,
            "storage_uri": None,
        },
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_owner": True,
            "vault_permission_owner": False,
            "step_up_required_for_upload_confirm_replace_export": True,
            "external_access_default": "denied",
        },
        "redaction_boundary": {
            "summary_safe": True,
            "redaction_required_before_preview": True,
            "redacted_preview_available": False,
            "unredacted_preview_allowed": False,
            "external_preview_allowed": False,
        },
    }


def _review_state_from_classifier(record: Dict[str, Any]) -> Tuple[str, str, List[str], str]:
    classifier_status = record["classification_status"]
    match_status = record["requirement_match"]["match_status"]
    classifier_blocks = set(record.get("blocked_codes") or [])

    base_blocks = {
        "DIRECT_UPLOAD_LOCKED",
        "RAW_FILE_BODY_LOCKED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_PREVIEW_LOCKED",
        "NO_AUTO_FILE_COMPLETION",
        "OWNER_CONFIRMATION_REQUIRED",
    }

    if "TOWER_CLEARANCE_REQUIRED" in classifier_blocks or classifier_status == "BLOCKED_TOWER_CLEARANCE":
        return (
            "BLOCKED_TOWER_CLEARANCE",
            "REQUEST_TOWER_CLEARANCE",
            sorted(base_blocks | {"TOWER_CLEARANCE_REQUIRED"}),
            "Request or wait for Tower clearance before upload completion can move forward.",
        )

    if "STORAGE_PROVIDER_NOT_CONFIGURED" in classifier_blocks or classifier_status == "BLOCKED_PROVIDER":
        return (
            "BLOCKED_STORAGE_PROVIDER",
            "HOLD_METADATA_ONLY",
            sorted(base_blocks | {"PERMANENT_STORAGE_NOT_CONFIGURED"}),
            "Hold metadata-only review state until a storage provider is configured.",
        )

    if classifier_status == "NEEDS_REQUIREMENT_REVIEW" or match_status == "PARTIAL_MATCH":
        return (
            "NEEDS_REQUIREMENT_CONFIRMATION",
            "CONFIRM_PACKET_REQUIREMENT_MATCH",
            sorted(base_blocks),
            "Confirm the requirement link before this record can continue to version flow.",
        )

    if classifier_status == "NEEDS_OWNER_CONFIRMATION" or match_status == "NEEDS_OWNER_CONFIRMATION":
        return (
            "NEEDS_PACKET_CONFIRMATION",
            "CONFIRM_PACKET_REQUIREMENT_MATCH",
            sorted(base_blocks),
            "Confirm packet and requirement match before manual upload review is treated as complete.",
        )

    if "REDACTION_REVIEW_REQUIRED" in classifier_blocks:
        return (
            "NEEDS_REDACTION_CONFIRMATION",
            "SEND_TO_REDACTION_REVIEW",
            sorted(base_blocks | {"REDACTION_CONFIRMATION_REQUIRED"}),
            "Confirm redaction path before preview/export and carry this into GP015 version flow.",
        )

    return (
        "READY_FOR_OWNER_UPLOAD_REVIEW",
        "READY_FOR_VERSION_FLOW",
        sorted(base_blocks),
        "Confirm metadata-only upload review and carry this record into GP015 version flow.",
    )


def _build_item_checks(record: Dict[str, Any], blocked_codes: List[str]) -> List[Dict[str, Any]]:
    classifier_basis = record["classification_basis"]
    requirement_match = record["requirement_match"]

    checks = [
        {
            "check_id": "VUR-CHECK-001",
            "label": "Confirm intake record is connected.",
            "passed": bool(record["intake_id"]),
            "required": True,
            "tower_owned": False,
        },
        {
            "check_id": "VUR-CHECK-002",
            "label": "Confirm attachment metadata slot is connected.",
            "passed": bool(record["attachment_id"]),
            "required": True,
            "tower_owned": False,
        },
        {
            "check_id": "VUR-CHECK-003",
            "label": "Confirm classifier prediction is metadata-only.",
            "passed": (
                classifier_basis["mode"] == "metadata_rules_only"
                and classifier_basis["file_body_used"] is False
                and classifier_basis["ocr_used"] is False
                and classifier_basis["content_parse_used"] is False
            ),
            "required": True,
            "tower_owned": False,
        },
        {
            "check_id": "VUR-CHECK-004",
            "label": "Confirm packet and requirement match.",
            "passed": bool(record["packet_id"] and record["requirement_id"]),
            "required": True,
            "tower_owned": False,
        },
        {
            "check_id": "VUR-CHECK-005",
            "label": "Confirm redaction review requirement.",
            "passed": True,
            "required": True,
            "tower_owned": False,
        },
        {
            "check_id": "VUR-CHECK-006",
            "label": "Confirm Tower clearance before sensitive movement.",
            "passed": "TOWER_CLEARANCE_REQUIRED" not in blocked_codes,
            "required": True,
            "tower_owned": True,
        },
        {
            "check_id": "VUR-CHECK-007",
            "label": "Confirm direct upload remains locked.",
            "passed": "DIRECT_UPLOAD_LOCKED" in blocked_codes,
            "required": True,
            "tower_owned": True,
        },
        {
            "check_id": "VUR-CHECK-008",
            "label": "Confirm external access remains denied.",
            "passed": "EXTERNAL_ACCESS_DENIED" in blocked_codes,
            "required": True,
            "tower_owned": True,
        },
    ]

    if requirement_match["ready_for_auto_filing"] is True:
        checks.append(
            {
                "check_id": "VUR-CHECK-009",
                "label": "Auto filing must remain disabled.",
                "passed": False,
                "required": True,
                "tower_owned": True,
            }
        )

    return checks


def _build_decision_board(review_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    decision_items = []
    decision_counts: Dict[str, int] = {}

    for item in review_items:
        decision = item["recommended_decision"]
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

        decision_items.append(
            {
                "decision_id": f"VUD-{item['attachment_id'].replace('VAT-', '')}",
                "review_id": item["review_id"],
                "attachment_id": item["attachment_id"],
                "recommended_decision": decision,
                "recommended_decision_label": item["recommended_decision_label"],
                "owner_must_confirm": True,
                "tower_must_clear": item["needs_tower_clearance"],
                "ready_for_gp015_version_flow": item["ready_for_gp015_version_flow"],
                "auto_apply_allowed": False,
                "reason_auto_apply_blocked": "Manual owner confirmation and Tower boundaries required.",
            }
        )

    return {
        "decision_items": decision_items,
        "decision_count": len(decision_items),
        "decision_counts": decision_counts,
        "auto_apply_allowed": False,
        "owner_confirmation_required": True,
    }


def _build_checklist_state(review_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_checks = sum(len(item["manual_review_checks"]) for item in review_items)
    passed_checks = sum(item["checks_passed_count"] for item in review_items)
    tower_owned_checks = sum(
        1
        for item in review_items
        for check in item["manual_review_checks"]
        if check["tower_owned"]
    )

    return {
        "checklist_template": UPLOAD_REVIEW_CHECKLIST,
        "total_review_checks": total_checks,
        "passed_review_checks": passed_checks,
        "tower_owned_check_count": tower_owned_checks,
        "all_checks_auto_complete": False,
        "owner_confirmation_required": True,
        "tower_clearance_required_for_sensitive_steps": True,
    }


def _build_blocked_reasons(review_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    active_codes = sorted({code for item in review_items for code in item["blocked_codes"]})

    return [
        {
            "code": code,
            "label": UPLOAD_REVIEW_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code or "UPLOAD" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "DIRECT_UPLOAD_LOCKED": "Keep direct raw upload locked. Use review metadata only.",
        "RAW_FILE_BODY_LOCKED": "Do not display or store raw file bodies.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold upload review metadata until provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive upload movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before filing completion.",
        "REDACTION_CONFIRMATION_REQUIRED": "Send to redaction review before preview/export.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied by default.",
        "UNREDACTED_PREVIEW_LOCKED": "Do not show unredacted preview.",
        "NO_AUTO_FILE_COMPLETION": "Keep manual review required. Do not auto-complete filing.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_queue(
    review_items: List[Dict[str, Any]],
    decision_board: Dict[str, Any],
    checklist_state: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "review_room": "Vault Manual Upload Review",
        "owner_queue_count": len(review_items),
        "needs_owner_review_count": sum(1 for item in review_items if item["needs_owner_review"]),
        "needs_tower_clearance_count": sum(1 for item in review_items if item["needs_tower_clearance"]),
        "ready_for_gp015_count": sum(1 for item in review_items if item["ready_for_gp015_version_flow"]),
        "auto_apply_allowed": decision_board["auto_apply_allowed"],
        "all_checks_auto_complete": checklist_state["all_checks_auto_complete"],
        "next_owner_actions": [
            "Review each staged upload record before filing completion.",
            "Confirm packet and requirement match.",
            "Send redaction-sensitive records to redaction review.",
            "Keep direct upload and raw file body storage locked.",
            "Carry confirmed metadata-only records into GP015 version history flow.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_manual_upload_review_payload())


def get_manual_upload_review_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "manual_upload_truth": payload["manual_upload_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "review_summary": payload["review_summary"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_manual_upload_review_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "manual_upload_review_queue": payload["manual_upload_review_queue"],
    }


def get_upload_review_decisions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "upload_review_decisions": payload["upload_review_decisions"],
    }


def get_upload_review_checklist() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "upload_review_checklist": payload["upload_review_checklist"],
    }


def get_upload_review_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "upload_review_blocked_reasons": payload["upload_review_blocked_reasons"],
        "blocked_reason_count": len(payload["upload_review_blocked_reasons"]),
    }


def get_gp014_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp014_status": payload["gp014_status"],
        "review_summary": payload["review_summary"],
        "manual_upload_truth": payload["manual_upload_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "owner_review_state": payload["owner_review_state"],
    }


def render_manual_upload_review_page() -> str:
    payload = clone_payload()
    summary = payload["review_summary"]
    truth = payload["manual_upload_truth"]
    queue = payload["manual_upload_review_queue"]
    owner = payload["owner_review_state"]
    decisions = payload["upload_review_decisions"]

    cards = "\n".join(_render_review_card(item) for item in queue["review_items"])
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    decision_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(decision)}</strong>
            <span>recommended decision</span>
          </div>
          <div class="pill warn">{count}</div>
        </div>
        """
        for decision, count in sorted(decisions["decision_counts"].items())
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Manual Upload Review · GP014</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090d22;
      --panel: rgba(15, 23, 52, 0.83);
      --panel2: rgba(21, 32, 74, 0.75);
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
      width: min(1220px, calc(100% - 32px));
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
      max-width: 900px;
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
      grid-template-columns: repeat(2, minmax(0, 1fr));
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
      font-size: 16px;
    }}

    .meta {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
      line-height: 1.55;
    }}

    .action {{
      margin-top: 12px;
      color: var(--text);
      font-size: 14px;
      line-height: 1.55;
      border-left: 3px solid rgba(245, 209, 126, .7);
      padding-left: 12px;
    }}

    code {{
      color: var(--cyan);
      background: rgba(0, 0, 0, .28);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 2px 6px;
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

    ul {{
      margin: 14px 0 0;
      color: var(--muted);
      line-height: 1.75;
    }}

    @media (max-width: 920px) {{
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
        <div class="eyebrow">Archive Vault · Giant Pack 014</div>
        <h1>Manual Upload Review</h1>
        <p class="hero-copy">
          GP014 turns classifier results into an owner-facing manual upload review queue.
          It prepares decisions for version history without unlocking raw upload, permanent storage,
          unredacted previews, downloads, or external access.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["review_item_count"]}</strong>
            <span>review items</span>
          </div>
          <div class="metric">
            <strong>{summary["decision_count"]}</strong>
            <span>decision records</span>
          </div>
          <div class="metric">
            <strong>{summary["checklist_count"]}</strong>
            <span>review checks</span>
          </div>
          <div class="metric">
            <strong>Locked</strong>
            <span>direct upload</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Manual review ready</span>
          <span class="pill warn">Owner confirmation required</span>
          <span class="pill warn">Tower clearance required</span>
          <span class="pill danger">Raw body locked</span>
          <span class="pill danger">External access denied</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Review Queue</h2>
      <p>
        Each item is a metadata-only review record connected to GP013 classifier output.
        No private file body is read, written, downloaded, or previewed.
      </p>
      <div class="grid">
        {cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Decision Board</h2>
        <p>Recommended decisions require owner confirmation and never auto-apply.</p>
        <div>
          {decision_rows}
        </div>
      </div>
      <div>
        <h2>Owner Review</h2>
        <p>GP014 prepares confirmed records for GP015 version history and replace/supersede flow.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP014 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["queue_route"])}</code>
        <code>{escape(summary["decisions_route"])}</code>
        <code>{escape(summary["checklist_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp014_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Upload Truth</h2>
      <p>
        Manual review enabled:
        <code>{str(truth["manual_review_enabled"]).lower()}</code>.
        Direct upload unlocked:
        <code>{str(truth["direct_upload_unlocked"]).lower()}</code>.
        Raw storage enabled:
        <code>{str(truth["raw_file_body_storage_enabled"]).lower()}</code>.
        Fake upload complete:
        <code>{str(truth["fake_upload_complete"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_review_card(item: Dict[str, Any]) -> str:
    blocked = item.get("blocked_codes") or []
    blocked_chips = "\n".join(
        f'<span class="pill danger">{escape(code)}</span>'
        for code in blocked
    )
    if not blocked_chips:
        blocked_chips = '<span class="pill ok">NO_BLOCK_CODE</span>'

    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item["predicted_document_label"])}</div>
            <div class="meta">
              Review: <code>{escape(item["review_id"])}</code><br>
              Classification: <code>{escape(item["classification_id"])}</code><br>
              Attachment: <code>{escape(item["attachment_id"])}</code><br>
              Intake: <code>{escape(item["intake_id"])}</code><br>
              Packet: <code>{escape(item["packet_id"])}</code><br>
              Requirement: <code>{escape(item["requirement_id"])}</code>
            </div>
          </div>
          <span class="pill warn">{escape(item["review_status_label"])}</span>
        </div>
        <div class="chips">{blocked_chips}</div>
        <div class="action">
          Recommended decision: {escape(item["recommended_decision_label"])}<br>
          Owner action: {escape(item["owner_action"])}
        </div>
      </article>
    """
