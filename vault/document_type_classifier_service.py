"""
VAULT GIANT PACK 013 — Document Type Classifier + Requirement Match

This pack adds the first real classifier/matcher layer after GP011-GP012.

Important truth:
- This is metadata-rule classification, not OCR and not file-body parsing.
- It uses intake IDs, packet links, requirement links, lanes, allowed file metadata slots,
  and Vault registry state.
- It does not pretend raw file bodies are available.
- It keeps direct upload, external access, unredacted preview, and file-body storage locked.
- Tower owns authority, clearance, step-up, export locks, freeze/revoke, and external access.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List, Tuple

from vault.file_attachment_registry_service import get_file_attachment_registry_payload


PACK_ID = "VAULT_GP013"
PACK_NAME = "Document Type Classifier + Requirement Match"
SCHEMA_VERSION = "vault.document_type_classifier.v1"

CLASSIFICATION_STATUSES = {
    "METADATA_RULE_MATCHED": "Metadata rule matched",
    "NEEDS_OWNER_CONFIRMATION": "Needs owner confirmation",
    "NEEDS_REQUIREMENT_REVIEW": "Needs requirement review",
    "BLOCKED_PROVIDER": "Blocked by storage provider",
    "BLOCKED_TOWER_CLEARANCE": "Blocked by Tower clearance",
    "READY_FOR_GP014_UPLOAD_REVIEW": "Ready for GP014 manual upload review",
}

REQUIREMENT_MATCH_STATUSES = {
    "MATCHED": "Matched",
    "PARTIAL_MATCH": "Partial match",
    "NEEDS_OWNER_CONFIRMATION": "Needs owner confirmation",
    "BLOCKED_TOWER": "Blocked by Tower",
    "BLOCKED_PROVIDER": "Blocked by provider",
}

CLASSIFIER_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body is locked.",
    "NO_OCR_OR_CONTENT_PARSE_YET": "No OCR or content body parsing is available in GP013.",
    "STORAGE_PROVIDER_NOT_CONFIGURED": "Permanent file-body storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive document movement.",
    "DIRECT_UPLOAD_STILL_LOCKED": "Direct upload is still locked.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before filing is treated as complete.",
    "REDACTION_REVIEW_REQUIRED": "Redaction review is required before export preview.",
}

DOCUMENT_TYPE_RULES = {
    "VAT-ATM-SELLER-PACKET-001": {
        "predicted_document_type": "atm_route_seller_packet",
        "label": "ATM Route Seller Packet",
        "confidence": 0.86,
        "signals": [
            "attachment_id:VAT-ATM",
            "packet:atm_route_acquisition_packet",
            "requirement:seller_financials_and_route_list",
            "lane:SimpleeOnTheGo / ATM",
        ],
    },
    "VAT-APT-LENDER-DD-001": {
        "predicted_document_type": "apartment_lender_due_diligence",
        "label": "Apartment Lender Due Diligence",
        "confidence": 0.84,
        "signals": [
            "attachment_id:VAT-APT",
            "packet:apartment_lender_due_diligence_packet",
            "requirement:lender_packet_requirements",
            "lane:SimpleeProperty / Apartment",
        ],
    },
    "VAT-TRUST-PROOF-001": {
        "predicted_document_type": "trust_entity_proof",
        "label": "Trust / Entity Proof",
        "confidence": 0.88,
        "signals": [
            "attachment_id:VAT-TRUST",
            "packet:trust_entity_binder",
            "requirement:trust_formation_and_entity_proof",
            "lane:Trust / Entity",
        ],
    },
    "VAT-OB-MANUAL-LIVE-001": {
        "predicted_document_type": "ob_manual_live_private_proof",
        "label": "OB Manual Live Private Proof",
        "confidence": 0.91,
        "signals": [
            "attachment_id:VAT-OB",
            "packet:ob_manual_live_private_proof_packet",
            "requirement:manual_live_receipt_chain",
            "lane:The Observatory / Manual Live",
        ],
    },
    "VAT-SOULAANA-IP-001": {
        "predicted_document_type": "soulaana_artist_ip_package",
        "label": "Soulaana Artist / IP Package",
        "confidence": 0.83,
        "signals": [
            "attachment_id:VAT-SOULAANA",
            "packet:soulaana_artist_ip_vault",
            "requirement:artist_package_and_reserved_art_slot",
            "lane:Soulaana / IP",
        ],
    },
    "VAT-BETA-NDA-001": {
        "predicted_document_type": "private_beta_nda_access_packet",
        "label": "Private Beta NDA / Access Packet",
        "confidence": 0.82,
        "signals": [
            "attachment_id:VAT-BETA",
            "packet:private_beta_onboarding_vault",
            "requirement:nda_access_and_beta_clearance",
            "lane:Private Beta",
        ],
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_document_type_classifier_payload() -> Dict[str, Any]:
    gp012 = get_file_attachment_registry_payload()
    attachment_slots = gp012["attachment_slots"]

    classification_records = [
        _build_classification_record(slot)
        for slot in attachment_slots
    ]

    requirement_matches = [
        record["requirement_match"]
        for record in classification_records
    ]

    review_queue = _build_classifier_review_queue(classification_records)
    blocked_reasons = _build_blocked_reasons(classification_records)
    classifier_board = _build_classifier_board(classification_records, requirement_matches)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP011", "VAULT_GP012"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "metadata_document_classifier_requirement_matcher",
        },
        "classifier_truth": {
            "classification_mode": "metadata_rules_only",
            "ocr_enabled": False,
            "file_body_parse_enabled": False,
            "content_extraction_enabled": False,
            "raw_body_required_for_gp013": False,
            "fake_content_analysis_complete": False,
            "safe_next_unlock": "GP014 manual upload review can use these classifier and requirement states without raw body storage.",
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
            "vault_owns_tower_permissions": False,
        },
        "classifier_summary": {
            "room_title": "Vault Document Classifier",
            "route": "/vault/document-classifier",
            "json_route": "/vault/document-classifier.json",
            "classifier_route": "/vault/document-type-classifier.json",
            "requirement_match_route": "/vault/requirement-match.json",
            "review_queue_route": "/vault/classifier-review-queue.json",
            "blocked_reasons_route": "/vault/classification-blocked-reasons.json",
            "gp013_status_route": "/vault/gp013-status.json",
            "classification_record_count": len(classification_records),
            "requirement_match_count": len(requirement_matches),
            "owner_review_queue_count": len(review_queue["review_items"]),
            "raw_body_storage_enabled": False,
            "ocr_enabled": False,
        },
        "classification_records": classification_records,
        "requirement_matches": requirement_matches,
        "classifier_review_queue": review_queue,
        "classification_blocked_reasons": blocked_reasons,
        "classifier_board": classifier_board,
        "gp013_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp014": True,
            "next_pack": "VAULT_GP014_MANUAL_UPLOAD_REVIEW_QUEUE",
            "gp012_attachment_slots_connected": True,
            "metadata_rule_classifier_ready": True,
            "requirement_matcher_ready": True,
            "ocr_or_body_parse_not_claimed": True,
            "raw_file_body_storage_still_locked": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp013",
        },
    }

    return payload


def _build_classification_record(slot: Dict[str, Any]) -> Dict[str, Any]:
    attachment_id = slot["attachment_id"]
    rule = DOCUMENT_TYPE_RULES.get(
        attachment_id,
        {
            "predicted_document_type": "general_owner_record",
            "label": "General Owner Record",
            "confidence": 0.62,
            "signals": [
                f"packet:{slot['packet_link']['packet_id']}",
                f"requirement:{slot['requirement_link']['requirement_id']}",
                f"lane:{slot['lane']}",
            ],
        },
    )

    status, match_status, blocked_codes, owner_action = _classify_status(slot, rule)
    requirement_match = _build_requirement_match(slot, rule, match_status)

    return {
        "classification_id": f"VCL-{attachment_id.replace('VAT-', '')}",
        "attachment_id": attachment_id,
        "intake_id": slot["intake_id"],
        "lane": slot["lane"],
        "packet_id": slot["packet_link"]["packet_id"],
        "requirement_id": slot["requirement_link"]["requirement_id"],
        "predicted_document_type": rule["predicted_document_type"],
        "predicted_document_label": rule["label"],
        "confidence": rule["confidence"],
        "confidence_label": _confidence_label(rule["confidence"]),
        "classification_status": status,
        "classification_status_label": CLASSIFICATION_STATUSES.get(status, status),
        "classification_basis": {
            "mode": "metadata_rules_only",
            "signals": rule["signals"],
            "file_body_used": False,
            "ocr_used": False,
            "content_parse_used": False,
            "body_storage_required": False,
        },
        "requirement_match": requirement_match,
        "blocked_codes": blocked_codes,
        "blocked_labels": [CLASSIFIER_BLOCK_CODES.get(code, code) for code in blocked_codes],
        "owner_action": owner_action,
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_owner": True,
            "vault_permission_owner": False,
            "step_up_required_for_classify_confirm_export": True,
            "external_access_default": "denied",
        },
        "redaction_boundary": {
            "summary_safe": True,
            "redaction_review_required_before_export": True,
            "unredacted_preview_allowed": False,
            "external_preview_allowed": False,
        },
    }


def _classify_status(slot: Dict[str, Any], rule: Dict[str, Any]) -> Tuple[str, str, List[str], str]:
    slot_status = slot["status"]
    blocked = set(slot.get("blocked_codes") or [])

    base_block_codes = {
        "RAW_FILE_BODY_LOCKED",
        "NO_OCR_OR_CONTENT_PARSE_YET",
        "EXTERNAL_ACCESS_DENIED",
        "OWNER_CONFIRMATION_REQUIRED",
    }

    if "TOWER_CLEARANCE_REQUIRED" in blocked or slot_status == "BLOCKED_TOWER_CLEARANCE":
        return (
            "BLOCKED_TOWER_CLEARANCE",
            "BLOCKED_TOWER",
            sorted(base_block_codes | {"TOWER_CLEARANCE_REQUIRED", "DIRECT_UPLOAD_STILL_LOCKED"}),
            "Hold classification as metadata-only until Tower clearance allows the next sensitive step.",
        )

    if "STORAGE_PROVIDER_NOT_CONFIGURED" in blocked or slot_status == "BLOCKED_PROVIDER":
        return (
            "BLOCKED_PROVIDER",
            "BLOCKED_PROVIDER",
            sorted(base_block_codes | {"STORAGE_PROVIDER_NOT_CONFIGURED"}),
            "Keep requirement match staged and do not claim file-body analysis.",
        )

    if slot_status == "NEEDS_REQUIREMENT_LINK":
        return (
            "NEEDS_REQUIREMENT_REVIEW",
            "PARTIAL_MATCH",
            sorted(base_block_codes | {"OWNER_CONFIRMATION_REQUIRED"}),
            "Review requirement link before treating this document as matched.",
        )

    if slot_status == "NEEDS_PACKET_LINK":
        return (
            "NEEDS_OWNER_CONFIRMATION",
            "NEEDS_OWNER_CONFIRMATION",
            sorted(base_block_codes | {"OWNER_CONFIRMATION_REQUIRED"}),
            "Confirm packet link before filing classification.",
        )

    if slot_status == "NEEDS_REDACTION_REVIEW":
        return (
            "NEEDS_OWNER_CONFIRMATION",
            "MATCHED",
            sorted(base_block_codes | {"REDACTION_REVIEW_REQUIRED"}),
            "Confirm classification and complete redaction review before any preview/export.",
        )

    return (
        "METADATA_RULE_MATCHED",
        "MATCHED",
        sorted(base_block_codes),
        "Confirm metadata-rule classification and carry into GP014 manual upload review.",
    )


def _build_requirement_match(
    slot: Dict[str, Any],
    rule: Dict[str, Any],
    match_status: str,
) -> Dict[str, Any]:
    requirement = slot["requirement_link"]
    packet = slot["packet_link"]

    return {
        "match_id": f"VRM-{slot['attachment_id'].replace('VAT-', '')}",
        "attachment_id": slot["attachment_id"],
        "intake_id": slot["intake_id"],
        "packet_id": packet["packet_id"],
        "packet_label": packet["packet_label"],
        "requirement_id": requirement["requirement_id"],
        "requirement_label": requirement["requirement_label"],
        "predicted_document_type": rule["predicted_document_type"],
        "predicted_document_label": rule["label"],
        "match_status": match_status,
        "match_status_label": REQUIREMENT_MATCH_STATUSES.get(match_status, match_status),
        "requirement_linked": requirement["requirement_linked"],
        "match_basis": {
            "metadata_rule": True,
            "packet_link_used": True,
            "requirement_link_used": True,
            "ocr_used": False,
            "body_content_used": False,
        },
        "ready_for_owner_confirmation": match_status in {
            "MATCHED",
            "PARTIAL_MATCH",
            "NEEDS_OWNER_CONFIRMATION",
        },
        "ready_for_auto_filing": False,
        "reason_auto_filing_blocked": "Owner confirmation and Tower boundaries required.",
    }


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.9:
        return "high_metadata_confidence"
    if confidence >= 0.8:
        return "medium_high_metadata_confidence"
    if confidence >= 0.65:
        return "medium_metadata_confidence"
    return "low_metadata_confidence"


def _build_classifier_review_queue(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    review_items = []

    for record in records:
        needs_review = (
            record["classification_status"] != "METADATA_RULE_MATCHED"
            or record["requirement_match"]["match_status"] != "MATCHED"
            or bool(record["blocked_codes"])
        )

        review_items.append(
            {
                "review_id": f"VCRQ-{record['attachment_id'].replace('VAT-', '')}",
                "classification_id": record["classification_id"],
                "attachment_id": record["attachment_id"],
                "intake_id": record["intake_id"],
                "predicted_document_label": record["predicted_document_label"],
                "classification_status": record["classification_status"],
                "requirement_match_status": record["requirement_match"]["match_status"],
                "needs_owner_review": needs_review,
                "blocked_codes": record["blocked_codes"],
                "owner_action": record["owner_action"],
                "tower_guard_required": True,
            }
        )

    return {
        "review_room": "Vault Document Classifier",
        "review_items": review_items,
        "review_count": len(review_items),
        "needs_owner_review_count": sum(1 for item in review_items if item["needs_owner_review"]),
        "next_owner_actions": [
            "Review metadata-rule classification results.",
            "Confirm packet and requirement matches before filing.",
            "Do not treat GP013 as OCR or body-content proof.",
            "Keep raw file bodies, direct upload, and external previews locked.",
            "Carry confirmed records into GP014 manual upload review queue.",
        ],
    }


def _build_blocked_reasons(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    active_codes = sorted({code for record in records for code in record["blocked_codes"]})

    return [
        {
            "code": code,
            "label": CLASSIFIER_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-rule classification only. Do not claim body analysis.",
        "NO_OCR_OR_CONTENT_PARSE_YET": "Do not run OCR or content parsing in GP013.",
        "STORAGE_PROVIDER_NOT_CONFIGURED": "Keep classifier result staged until storage provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive next steps.",
        "DIRECT_UPLOAD_STILL_LOCKED": "Do not unlock direct upload from classifier work.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied by default.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before filing is treated as complete.",
        "REDACTION_REVIEW_REQUIRED": "Require redaction review before preview/export.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_classifier_board(
    records: List[Dict[str, Any]],
    requirement_matches: List[Dict[str, Any]],
) -> Dict[str, Any]:
    status_counts: Dict[str, int] = {}
    match_counts: Dict[str, int] = {}

    for record in records:
        status_counts[record["classification_status"]] = status_counts.get(record["classification_status"], 0) + 1

    for match in requirement_matches:
        match_counts[match["match_status"]] = match_counts.get(match["match_status"], 0) + 1

    return {
        "classification_status_counts": status_counts,
        "requirement_match_status_counts": match_counts,
        "metadata_rule_matched_count": status_counts.get("METADATA_RULE_MATCHED", 0),
        "blocked_provider_count": status_counts.get("BLOCKED_PROVIDER", 0),
        "blocked_tower_count": status_counts.get("BLOCKED_TOWER_CLEARANCE", 0),
        "needs_owner_confirmation_count": status_counts.get("NEEDS_OWNER_CONFIRMATION", 0),
        "needs_requirement_review_count": status_counts.get("NEEDS_REQUIREMENT_REVIEW", 0),
        "ready_for_gp014_count": len(records),
        "safe_to_continue": True,
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_document_type_classifier_payload())


def get_document_classifier_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "classifier_truth": payload["classifier_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "classifier_summary": payload["classifier_summary"],
        "classifier_board": payload["classifier_board"],
    }


def get_document_type_classifier() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "classification_records": payload["classification_records"],
        "classification_record_count": len(payload["classification_records"]),
        "classifier_truth": payload["classifier_truth"],
    }


def get_requirement_match() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "requirement_matches": payload["requirement_matches"],
        "requirement_match_count": len(payload["requirement_matches"]),
    }


def get_classifier_review_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "classifier_review_queue": payload["classifier_review_queue"],
    }


def get_classification_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "classification_blocked_reasons": payload["classification_blocked_reasons"],
        "blocked_reason_count": len(payload["classification_blocked_reasons"]),
    }


def get_gp013_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp013_status": payload["gp013_status"],
        "classifier_summary": payload["classifier_summary"],
        "classifier_truth": payload["classifier_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "classifier_board": payload["classifier_board"],
    }


def render_document_classifier_page() -> str:
    payload = clone_payload()
    summary = payload["classifier_summary"]
    truth = payload["classifier_truth"]
    board = payload["classifier_board"]
    review = payload["classifier_review_queue"]

    cards = "\n".join(_render_classification_card(record) for record in payload["classification_records"])
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in review["next_owner_actions"])

    status_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(status)}</strong>
            <span>classification status</span>
          </div>
          <div class="pill warn">{count}</div>
        </div>
        """
        for status, count in sorted(board["classification_status_counts"].items())
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Document Classifier · GP013</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090d22;
      --panel: rgba(15, 23, 52, 0.82);
      --panel2: rgba(21, 32, 74, 0.74);
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
        <div class="eyebrow">Archive Vault · Giant Pack 013</div>
        <h1>Document Classifier</h1>
        <p class="hero-copy">
          GP013 classifies attachment slots and matches them to packet requirements using metadata rules only.
          It does not claim OCR, content extraction, or raw file-body analysis. Direct upload, external previews,
          unredacted exports, and permanent file storage stay locked behind provider setup and Tower authority.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["classification_record_count"]}</strong>
            <span>classification records</span>
          </div>
          <div class="metric">
            <strong>{summary["requirement_match_count"]}</strong>
            <span>requirement matches</span>
          </div>
          <div class="metric">
            <strong>{summary["owner_review_queue_count"]}</strong>
            <span>review queue items</span>
          </div>
          <div class="metric">
            <strong>Off</strong>
            <span>OCR + body parse</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Metadata rules ready</span>
          <span class="pill warn">Owner confirmation required</span>
          <span class="pill warn">Tower clearance required</span>
          <span class="pill danger">Direct upload locked</span>
          <span class="pill danger">OCR/body parse off</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Classification Records</h2>
      <p>
        Each result is based on attachment metadata, intake ID, packet link, requirement link, and lane.
        No private file body is read or displayed.
      </p>
      <div class="grid">
        {cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Classifier Board</h2>
        <p>Status counts show what needs owner/Tower action before filing completion.</p>
        <div>
          {status_rows}
        </div>
      </div>
      <div>
        <h2>Owner Review</h2>
        <p>GP013 prepares the road for GP014 manual upload review queue.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP013 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["classifier_route"])}</code>
        <code>{escape(summary["requirement_match_route"])}</code>
        <code>{escape(summary["review_queue_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp013_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Classifier Truth</h2>
      <p>
        Mode:
        <code>{escape(truth["classification_mode"])}</code>.
        OCR enabled:
        <code>{str(truth["ocr_enabled"]).lower()}</code>.
        File body parse enabled:
        <code>{str(truth["file_body_parse_enabled"]).lower()}</code>.
        Fake content analysis complete:
        <code>{str(truth["fake_content_analysis_complete"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_classification_card(record: Dict[str, Any]) -> str:
    blocked = record.get("blocked_codes") or []
    blocked_chips = "\n".join(
        f'<span class="pill danger">{escape(code)}</span>'
        for code in blocked
    )
    if not blocked_chips:
        blocked_chips = '<span class="pill ok">NO_BLOCK_CODE</span>'

    match = record["requirement_match"]

    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(record["predicted_document_label"])}</div>
            <div class="meta">
              Classification: <code>{escape(record["classification_id"])}</code><br>
              Attachment: <code>{escape(record["attachment_id"])}</code><br>
              Intake: <code>{escape(record["intake_id"])}</code><br>
              Packet: <code>{escape(record["packet_id"])}</code><br>
              Requirement: <code>{escape(record["requirement_id"])}</code><br>
              Confidence: <code>{escape(str(record["confidence"]))}</code>
            </div>
          </div>
          <span class="pill warn">{escape(record["classification_status_label"])}</span>
        </div>
        <div class="chips">{blocked_chips}</div>
        <div class="action">
          Requirement match: {escape(match["match_status_label"])}<br>
          Owner action: {escape(record["owner_action"])}
        </div>
      </article>
    """
