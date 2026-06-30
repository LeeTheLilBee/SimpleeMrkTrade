"""
VAULT GIANT PACK 015 — Version History + Replace/Supersede Flow

This pack creates Vault's metadata-only document version history layer.

Important truth:
- This is not raw file storage.
- This does not unlock direct upload.
- This does not replace, delete, or supersede real file bodies.
- It creates controlled version metadata records, lineage state, replace/supersede decisions,
  and owner confirmation queues.
- GP015 prepares the road for GP016 Evidence Binder Builder.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  and external access authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List, Tuple

from vault.manual_upload_review_queue_service import get_manual_upload_review_payload


PACK_ID = "VAULT_GP015"
PACK_NAME = "Version History + Replace/Supersede Flow"
SCHEMA_VERSION = "vault.version_history_replace_supersede.v1"

VERSION_STATUSES = {
    "VERSION_METADATA_READY": "Version metadata ready",
    "HELD_METADATA_ONLY": "Held metadata only",
    "NEEDS_OWNER_CONFIRMATION": "Needs owner confirmation",
    "NEEDS_REDACTION_REVIEW": "Needs redaction review",
    "BLOCKED_TOWER_CLEARANCE": "Blocked by Tower clearance",
    "BLOCKED_STORAGE_PROVIDER": "Blocked by storage provider",
}

VERSION_ACTIONS = {
    "CREATE_INITIAL_VERSION": "Create initial version",
    "HOLD_METADATA_ONLY": "Hold metadata only",
    "MARK_REPLACEMENT_CANDIDATE": "Mark replacement candidate",
    "MARK_SUPERSEDE_CANDIDATE": "Mark supersede candidate",
    "SEND_TO_REDACTION_REVIEW": "Send to redaction review",
    "REQUEST_TOWER_CLEARANCE": "Request Tower clearance",
}

LINEAGE_STATUSES = {
    "ACTIVE_INITIAL_METADATA_VERSION": "Active initial metadata version",
    "PENDING_REPLACEMENT": "Pending replacement",
    "PENDING_SUPERSEDE": "Pending supersede",
    "HELD_FOR_REVIEW": "Held for review",
    "BLOCKED": "Blocked",
}

VERSION_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive version movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before version decisions apply.",
    "REDACTION_REVIEW_REQUIRED": "Redaction review is required before preview/export.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_PREVIEW_LOCKED": "Unredacted preview is locked.",
    "NO_AUTO_REPLACE": "Automatic replace is disabled.",
    "NO_AUTO_SUPERSEDE": "Automatic supersede is disabled.",
    "NO_DESTRUCTIVE_DELETE": "Destructive delete is disabled.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_version_history_payload() -> Dict[str, Any]:
    gp014 = get_manual_upload_review_payload()
    review_items = gp014["manual_upload_review_queue"]["review_items"]

    version_records = [
        _build_version_record(item)
        for item in review_items
    ]

    replace_supersede_flow = _build_replace_supersede_flow(version_records)
    lineage = _build_version_lineage(version_records)
    blocked_reasons = _build_blocked_reasons(version_records)
    owner_state = _build_owner_state(version_records, replace_supersede_flow, lineage)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP011", "VAULT_GP012", "VAULT_GP013", "VAULT_GP014"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "version_history_replace_supersede_metadata",
        },
        "version_truth": {
            "version_metadata_enabled": True,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "replace_flow_enabled_metadata_only": True,
            "supersede_flow_enabled_metadata_only": True,
            "destructive_delete_enabled": False,
            "auto_replace_enabled": False,
            "auto_supersede_enabled": False,
            "download_enabled": False,
            "unredacted_preview_enabled": False,
            "external_access_enabled": False,
            "fake_version_body_complete": False,
            "safe_next_unlock": "GP016 Evidence Binder Builder can use metadata version lineage without raw file storage.",
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
        "version_summary": {
            "room_title": "Vault Version History",
            "route": "/vault/version-history",
            "json_route": "/vault/version-history.json",
            "version_records_route": "/vault/version-records.json",
            "replace_supersede_route": "/vault/replace-supersede-flow.json",
            "lineage_route": "/vault/version-lineage.json",
            "blocked_reasons_route": "/vault/version-blocked-reasons.json",
            "gp015_status_route": "/vault/gp015-status.json",
            "version_record_count": len(version_records),
            "lineage_count": len(lineage["lineage_items"]),
            "replace_candidate_count": replace_supersede_flow["replace_candidate_count"],
            "supersede_candidate_count": replace_supersede_flow["supersede_candidate_count"],
            "raw_body_storage_enabled": False,
            "direct_upload_unlocked": False,
        },
        "version_records": version_records,
        "replace_supersede_flow": replace_supersede_flow,
        "version_lineage": lineage,
        "version_blocked_reasons": blocked_reasons,
        "owner_review_state": owner_state,
        "gp015_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp016": True,
            "next_pack": "VAULT_GP016_EVIDENCE_BINDER_BUILDER",
            "gp014_manual_review_records_connected": True,
            "version_metadata_ready": True,
            "replace_supersede_metadata_flow_ready": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "fake_version_body_completion_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp015",
        },
    }

    return payload


def _build_version_record(item: Dict[str, Any]) -> Dict[str, Any]:
    version_status, version_action, lineage_status, blocked_codes, owner_action = _version_state_from_review_item(item)

    version_id = f"VVER-{item['attachment_id'].replace('VAT-', '')}-V001"
    document_key = f"VDOC-{item['attachment_id'].replace('VAT-', '')}"

    return {
        "version_id": version_id,
        "document_key": document_key,
        "review_id": item["review_id"],
        "classification_id": item["classification_id"],
        "attachment_id": item["attachment_id"],
        "intake_id": item["intake_id"],
        "lane": item["lane"],
        "packet_id": item["packet_id"],
        "requirement_id": item["requirement_id"],
        "predicted_document_type": item["predicted_document_type"],
        "predicted_document_label": item["predicted_document_label"],
        "version_number": 1,
        "version_label": "v1 metadata-only",
        "version_status": version_status,
        "version_status_label": VERSION_STATUSES.get(version_status, version_status),
        "recommended_version_action": version_action,
        "recommended_version_action_label": VERSION_ACTIONS.get(version_action, version_action),
        "lineage_status": lineage_status,
        "lineage_status_label": LINEAGE_STATUSES.get(lineage_status, lineage_status),
        "source_review_status": item["review_status"],
        "source_recommended_decision": item["recommended_decision"],
        "body_state": {
            "body_present": False,
            "body_hash": None,
            "body_storage_uri": None,
            "body_write_allowed": False,
            "body_read_allowed": False,
            "direct_upload_allowed": False,
            "provider_configured": False,
        },
        "replace_supersede_state": {
            "can_mark_replacement_candidate": True,
            "can_mark_supersede_candidate": True,
            "auto_replace_allowed": False,
            "auto_supersede_allowed": False,
            "destructive_delete_allowed": False,
            "requires_owner_confirmation": True,
            "requires_tower_clearance_for_sensitive_steps": True,
        },
        "blocked_codes": blocked_codes,
        "blocked_labels": [VERSION_BLOCK_CODES.get(code, code) for code in blocked_codes],
        "owner_action": owner_action,
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_owner": True,
            "vault_permission_owner": False,
            "step_up_required_for_replace_supersede_export": True,
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


def _version_state_from_review_item(item: Dict[str, Any]) -> Tuple[str, str, str, List[str], str]:
    review_status = item["review_status"]
    decision = item["recommended_decision"]
    review_blocks = set(item.get("blocked_codes") or [])

    base_blocks = {
        "RAW_FILE_BODY_LOCKED",
        "DIRECT_UPLOAD_LOCKED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_PREVIEW_LOCKED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_REPLACE",
        "NO_AUTO_SUPERSEDE",
        "NO_DESTRUCTIVE_DELETE",
    }

    if "TOWER_CLEARANCE_REQUIRED" in review_blocks or review_status == "BLOCKED_TOWER_CLEARANCE":
        return (
            "BLOCKED_TOWER_CLEARANCE",
            "REQUEST_TOWER_CLEARANCE",
            "BLOCKED",
            sorted(base_blocks | {"TOWER_CLEARANCE_REQUIRED"}),
            "Hold version metadata and request Tower clearance before sensitive version movement.",
        )

    if "PERMANENT_STORAGE_NOT_CONFIGURED" in review_blocks or review_status == "BLOCKED_STORAGE_PROVIDER":
        return (
            "BLOCKED_STORAGE_PROVIDER",
            "HOLD_METADATA_ONLY",
            "HELD_FOR_REVIEW",
            sorted(base_blocks | {"PERMANENT_STORAGE_NOT_CONFIGURED"}),
            "Hold metadata-only version record until storage provider exists.",
        )

    if "REDACTION_CONFIRMATION_REQUIRED" in review_blocks or review_status == "NEEDS_REDACTION_CONFIRMATION":
        return (
            "NEEDS_REDACTION_REVIEW",
            "SEND_TO_REDACTION_REVIEW",
            "HELD_FOR_REVIEW",
            sorted(base_blocks | {"REDACTION_REVIEW_REQUIRED"}),
            "Route version metadata through redaction review before binder/export use.",
        )

    if review_status in {"NEEDS_PACKET_CONFIRMATION", "NEEDS_REQUIREMENT_CONFIRMATION"}:
        return (
            "NEEDS_OWNER_CONFIRMATION",
            "MARK_REPLACEMENT_CANDIDATE",
            "PENDING_REPLACEMENT",
            sorted(base_blocks),
            "Confirm packet/requirement match before replacement or supersede decision is applied.",
        )

    if decision == "READY_FOR_VERSION_FLOW":
        return (
            "VERSION_METADATA_READY",
            "CREATE_INITIAL_VERSION",
            "ACTIVE_INITIAL_METADATA_VERSION",
            sorted(base_blocks),
            "Create initial metadata version and carry lineage into GP016 evidence binder builder.",
        )

    return (
        "HELD_METADATA_ONLY",
        "HOLD_METADATA_ONLY",
        "HELD_FOR_REVIEW",
        sorted(base_blocks),
        "Hold metadata-only version state until owner confirms the next step.",
    )


def _build_replace_supersede_flow(version_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    flow_items = []

    for record in version_records:
        candidate_type = _candidate_type_for_record(record)

        flow_items.append(
            {
                "flow_id": f"VRS-{record['attachment_id'].replace('VAT-', '')}",
                "version_id": record["version_id"],
                "document_key": record["document_key"],
                "attachment_id": record["attachment_id"],
                "packet_id": record["packet_id"],
                "requirement_id": record["requirement_id"],
                "candidate_type": candidate_type,
                "current_version_number": record["version_number"],
                "replacement_version_number": 2 if candidate_type == "replacement_candidate" else None,
                "supersedes_version_id": record["version_id"] if candidate_type == "supersede_candidate" else None,
                "owner_must_confirm": True,
                "tower_must_clear_sensitive_steps": True,
                "auto_apply_allowed": False,
                "destructive_delete_allowed": False,
                "body_copy_allowed": False,
                "reason_body_copy_blocked": "Raw file body storage remains locked.",
            }
        )

    return {
        "flow_items": flow_items,
        "flow_count": len(flow_items),
        "replace_candidate_count": sum(1 for item in flow_items if item["candidate_type"] == "replacement_candidate"),
        "supersede_candidate_count": sum(1 for item in flow_items if item["candidate_type"] == "supersede_candidate"),
        "hold_metadata_only_count": sum(1 for item in flow_items if item["candidate_type"] == "hold_metadata_only"),
        "auto_apply_allowed": False,
        "destructive_delete_allowed": False,
        "owner_confirmation_required": True,
    }


def _candidate_type_for_record(record: Dict[str, Any]) -> str:
    if record["recommended_version_action"] == "MARK_REPLACEMENT_CANDIDATE":
        return "replacement_candidate"
    if record["recommended_version_action"] == "MARK_SUPERSEDE_CANDIDATE":
        return "supersede_candidate"
    if record["recommended_version_action"] == "CREATE_INITIAL_VERSION":
        return "initial_version"
    return "hold_metadata_only"


def _build_version_lineage(version_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    lineage_items = []

    for record in version_records:
        lineage_items.append(
            {
                "lineage_id": f"VLN-{record['attachment_id'].replace('VAT-', '')}",
                "document_key": record["document_key"],
                "active_version_id": record["version_id"],
                "active_version_number": record["version_number"],
                "known_version_ids": [record["version_id"]],
                "lineage_status": record["lineage_status"],
                "lineage_status_label": record["lineage_status_label"],
                "packet_id": record["packet_id"],
                "requirement_id": record["requirement_id"],
                "has_body_storage": False,
                "has_external_access": False,
                "safe_for_evidence_binder_metadata": True,
                "requires_owner_review_before_export": True,
            }
        )

    return {
        "lineage_items": lineage_items,
        "lineage_count": len(lineage_items),
        "active_initial_count": sum(
            1 for item in lineage_items if item["lineage_status"] == "ACTIVE_INITIAL_METADATA_VERSION"
        ),
        "pending_replacement_count": sum(
            1 for item in lineage_items if item["lineage_status"] == "PENDING_REPLACEMENT"
        ),
        "pending_supersede_count": sum(
            1 for item in lineage_items if item["lineage_status"] == "PENDING_SUPERSEDE"
        ),
        "blocked_count": sum(
            1 for item in lineage_items if item["lineage_status"] == "BLOCKED"
        ),
        "safe_to_continue_to_gp016": True,
    }


def _build_blocked_reasons(version_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    active_codes = sorted({code for record in version_records for code in record["blocked_codes"]})

    return [
        {
            "code": code,
            "label": VERSION_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code or "UPLOAD" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Track metadata version only. Do not store or display raw body.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct raw upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold metadata-only lineage until provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive version movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before version decision applies.",
        "REDACTION_REVIEW_REQUIRED": "Route through redaction before preview/export.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied by default.",
        "UNREDACTED_PREVIEW_LOCKED": "Do not show unredacted preview.",
        "NO_AUTO_REPLACE": "Do not auto-replace versions.",
        "NO_AUTO_SUPERSEDE": "Do not auto-supersede versions.",
        "NO_DESTRUCTIVE_DELETE": "Never destructively delete version records.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_state(
    version_records: List[Dict[str, Any]],
    replace_supersede_flow: Dict[str, Any],
    lineage: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "review_room": "Vault Version History",
        "owner_queue_count": len(version_records),
        "needs_owner_confirmation_count": sum(
            1 for record in version_records if "OWNER_CONFIRMATION_REQUIRED" in record["blocked_codes"]
        ),
        "needs_tower_clearance_count": sum(
            1 for record in version_records if "TOWER_CLEARANCE_REQUIRED" in record["blocked_codes"]
        ),
        "needs_redaction_review_count": sum(
            1 for record in version_records if "REDACTION_REVIEW_REQUIRED" in record["blocked_codes"]
        ),
        "replace_candidate_count": replace_supersede_flow["replace_candidate_count"],
        "supersede_candidate_count": replace_supersede_flow["supersede_candidate_count"],
        "lineage_safe_to_continue_to_gp016": lineage["safe_to_continue_to_gp016"],
        "auto_apply_allowed": replace_supersede_flow["auto_apply_allowed"],
        "destructive_delete_allowed": replace_supersede_flow["destructive_delete_allowed"],
        "next_owner_actions": [
            "Review initial metadata version records.",
            "Confirm replacement or supersede candidates before applying lineage changes.",
            "Keep destructive delete disabled.",
            "Keep raw file bodies, direct upload, external access, and unredacted previews locked.",
            "Carry safe metadata lineage into GP016 Evidence Binder Builder.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_version_history_payload())


def get_version_history_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "version_truth": payload["version_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "version_summary": payload["version_summary"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_version_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "version_records": payload["version_records"],
        "version_record_count": len(payload["version_records"]),
    }


def get_replace_supersede_flow() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "replace_supersede_flow": payload["replace_supersede_flow"],
    }


def get_version_lineage() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "version_lineage": payload["version_lineage"],
    }


def get_version_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "version_blocked_reasons": payload["version_blocked_reasons"],
        "blocked_reason_count": len(payload["version_blocked_reasons"]),
    }


def get_gp015_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp015_status": payload["gp015_status"],
        "version_summary": payload["version_summary"],
        "version_truth": payload["version_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "owner_review_state": payload["owner_review_state"],
    }


def render_version_history_page() -> str:
    payload = clone_payload()
    summary = payload["version_summary"]
    truth = payload["version_truth"]
    owner = payload["owner_review_state"]
    lineage = payload["version_lineage"]
    flow = payload["replace_supersede_flow"]

    cards = "\n".join(_render_version_card(record) for record in payload["version_records"])
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    flow_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["candidate_type"])}</strong>
            <span>{escape(item["document_key"])}</span>
          </div>
          <div class="pill warn">{escape(item["version_id"])}</div>
        </div>
        """
        for item in flow["flow_items"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Version History · GP015</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 015</div>
        <h1>Version History</h1>
        <p class="hero-copy">
          GP015 creates metadata-only version records, lineage, and replace/supersede review flow.
          It prepares Vault for evidence binders without unlocking raw file storage, direct upload,
          unredacted previews, destructive delete, or external access.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["version_record_count"]}</strong>
            <span>version records</span>
          </div>
          <div class="metric">
            <strong>{summary["lineage_count"]}</strong>
            <span>lineage records</span>
          </div>
          <div class="metric">
            <strong>{summary["replace_candidate_count"]}</strong>
            <span>replace candidates</span>
          </div>
          <div class="metric">
            <strong>{summary["supersede_candidate_count"]}</strong>
            <span>supersede candidates</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Metadata versioning ready</span>
          <span class="pill warn">Owner confirmation required</span>
          <span class="pill warn">Tower clearance required</span>
          <span class="pill danger">Raw body locked</span>
          <span class="pill danger">Destructive delete disabled</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Version Records</h2>
      <p>
        Each record is metadata-only and connected to the GP014 manual upload review queue.
        No private file body is read, written, downloaded, or previewed.
      </p>
      <div class="grid">
        {cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Replace / Supersede Flow</h2>
        <p>Replacement and supersede decisions require owner confirmation and never auto-apply.</p>
        <div>
          {flow_rows}
        </div>
      </div>
      <div>
        <h2>Owner Review</h2>
        <p>GP015 prepares clean metadata lineage for GP016 Evidence Binder Builder.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP015 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["version_records_route"])}</code>
        <code>{escape(summary["replace_supersede_route"])}</code>
        <code>{escape(summary["lineage_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp015_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Version Truth</h2>
      <p>
        Metadata versioning:
        <code>{str(truth["version_metadata_enabled"]).lower()}</code>.
        Raw storage enabled:
        <code>{str(truth["raw_file_body_storage_enabled"]).lower()}</code>.
        Auto replace:
        <code>{str(truth["auto_replace_enabled"]).lower()}</code>.
        Destructive delete:
        <code>{str(truth["destructive_delete_enabled"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_version_card(record: Dict[str, Any]) -> str:
    blocked = record.get("blocked_codes") or []
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
            <div class="title">{escape(record["predicted_document_label"])}</div>
            <div class="meta">
              Version: <code>{escape(record["version_id"])}</code><br>
              Document: <code>{escape(record["document_key"])}</code><br>
              Review: <code>{escape(record["review_id"])}</code><br>
              Attachment: <code>{escape(record["attachment_id"])}</code><br>
              Packet: <code>{escape(record["packet_id"])}</code><br>
              Requirement: <code>{escape(record["requirement_id"])}</code>
            </div>
          </div>
          <span class="pill warn">{escape(record["version_status_label"])}</span>
        </div>
        <div class="chips">{blocked_chips}</div>
        <div class="action">
          Version action: {escape(record["recommended_version_action_label"])}<br>
          Owner action: {escape(record["owner_action"])}
        </div>
      </article>
    """
