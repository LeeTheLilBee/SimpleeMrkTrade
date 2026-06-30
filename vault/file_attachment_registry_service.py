"""
VAULT GIANT PACK 012 — File Attachment Registry + Packet Linking

This pack builds the real attachment metadata layer that comes after GP011.

Important boundary:
- This is not permanent raw file storage.
- This is the safe metadata registry that links staged attachment slots to:
  intake records, packets, requirements, owner review state, and redaction state.
- File bodies remain locked until a real storage provider and Tower clearance path exist.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.document_intake_service import get_document_intake_payload


PACK_ID = "VAULT_GP012"
PACK_NAME = "File Attachment Registry + Packet Linking"
SCHEMA_VERSION = "vault.file_attachment_registry.v1"

ATTACHMENT_STATUSES = {
    "SLOT_READY_METADATA_ONLY": "Slot ready · metadata only",
    "PACKET_LINKED": "Packet linked",
    "NEEDS_PACKET_LINK": "Needs packet link",
    "NEEDS_REQUIREMENT_LINK": "Needs requirement link",
    "BLOCKED_PROVIDER": "Blocked by storage provider",
    "BLOCKED_TOWER_CLEARANCE": "Blocked by Tower clearance",
    "NEEDS_REDACTION_REVIEW": "Needs redaction review",
}

PACKET_LINK_STATUSES = {
    "LINKED": "Linked",
    "PENDING_OWNER_CONFIRMATION": "Pending owner confirmation",
    "BLOCKED_TOWER": "Blocked by Tower",
    "MISSING_REQUIREMENT": "Missing requirement",
}

ATTACHMENT_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body is locked.",
    "STORAGE_PROVIDER_NOT_CONFIGURED": "Permanent file-body storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive file movement.",
    "DIRECT_UPLOAD_STILL_LOCKED": "Direct upload is still locked.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "PACKET_LINK_REQUIRED": "Attachment must be linked to a Vault packet.",
    "REQUIREMENT_LINK_REQUIRED": "Attachment must be linked to a requirement checklist item.",
    "REDACTION_REVIEW_REQUIRED": "Redaction review is required before export preview.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _attachment_slot(
    attachment_id: str,
    intake_id: str,
    packet_id: str,
    packet_label: str,
    requirement_id: str,
    requirement_label: str,
    lane: str,
    title: str,
    status: str,
    packet_link_status: str,
    blocked_codes: List[str],
    owner_action: str,
    allowed_extensions: List[str] | None = None,
) -> Dict[str, Any]:
    allowed_extensions = allowed_extensions or ["pdf", "png", "jpg", "jpeg", "csv", "xlsx", "docx"]

    return {
        "attachment_id": attachment_id,
        "intake_id": intake_id,
        "lane": lane,
        "title": title,
        "status": status,
        "status_label": ATTACHMENT_STATUSES.get(status, status),
        "packet_link": {
            "packet_id": packet_id,
            "packet_label": packet_label,
            "packet_link_status": packet_link_status,
            "packet_link_status_label": PACKET_LINK_STATUSES.get(packet_link_status, packet_link_status),
        },
        "requirement_link": {
            "requirement_id": requirement_id,
            "requirement_label": requirement_label,
            "requirement_linked": bool(requirement_id and requirement_id != "unlinked"),
        },
        "attachment_metadata": {
            "original_filename": None,
            "display_filename": f"{attachment_id}.metadata-slot",
            "mime_type": None,
            "size_bytes": None,
            "sha256": None,
            "allowed_extensions": allowed_extensions,
            "body_present": False,
            "metadata_only": True,
        },
        "storage_state": {
            "raw_body_storage_enabled": False,
            "provider_configured": False,
            "provider_name": None,
            "storage_uri": None,
            "download_allowed": False,
            "preview_allowed": False,
            "upload_allowed_from_vault": False,
            "storage_blocked_reason": "provider_and_tower_clearance_required",
        },
        "redaction_state": {
            "redaction_required": True,
            "redacted_preview_available": False,
            "unredacted_preview_allowed": False,
            "external_preview_allowed": False,
            "summary_safe": True,
        },
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_owner": True,
            "vault_permission_owner": False,
            "step_up_required_for_attach_replace_export": True,
            "external_access_default": "denied",
        },
        "blocked_codes": blocked_codes,
        "blocked_labels": [ATTACHMENT_BLOCK_CODES.get(code, code) for code in blocked_codes],
        "owner_action": owner_action,
    }


@lru_cache(maxsize=1)
def get_file_attachment_registry_payload() -> Dict[str, Any]:
    gp011 = get_document_intake_payload()
    gp011_queue = gp011["intake_queue"]

    slots = [
        _attachment_slot(
            attachment_id="VAT-ATM-SELLER-PACKET-001",
            intake_id="VIN-ATM-ROUTE-001",
            packet_id="atm_route_acquisition_packet",
            packet_label="ATM Route Acquisition Packet",
            requirement_id="seller_financials_and_route_list",
            requirement_label="Seller financials and route list",
            lane="SimpleeOnTheGo / ATM",
            title="ATM seller packet attachment slot",
            status="BLOCKED_PROVIDER",
            packet_link_status="PENDING_OWNER_CONFIRMATION",
            blocked_codes=[
                "RAW_FILE_BODY_LOCKED",
                "STORAGE_PROVIDER_NOT_CONFIGURED",
                "TOWER_CLEARANCE_REQUIRED",
            ],
            owner_action="Confirm seller packet target, then keep file body blocked until provider/Tower clearance exists.",
        ),
        _attachment_slot(
            attachment_id="VAT-APT-LENDER-DD-001",
            intake_id="VIN-APT-LENDER-001",
            packet_id="apartment_lender_due_diligence_packet",
            packet_label="Apartment Lender Due Diligence Packet",
            requirement_id="lender_packet_requirements",
            requirement_label="Lender packet requirements",
            lane="SimpleeProperty / Apartment",
            title="Apartment lender due diligence attachment slot",
            status="NEEDS_REQUIREMENT_LINK",
            packet_link_status="LINKED",
            blocked_codes=[
                "RAW_FILE_BODY_LOCKED",
                "STORAGE_PROVIDER_NOT_CONFIGURED",
                "REQUIREMENT_LINK_REQUIRED",
            ],
            owner_action="Match the attachment to the lender requirement checklist before filing.",
        ),
        _attachment_slot(
            attachment_id="VAT-TRUST-PROOF-001",
            intake_id="VIN-TRUST-ENTITY-001",
            packet_id="trust_entity_binder",
            packet_label="Trust / Entity Binder",
            requirement_id="trust_formation_and_entity_proof",
            requirement_label="Trust formation and entity proof",
            lane="Trust / Entity",
            title="Trust entity proof attachment slot",
            status="NEEDS_REDACTION_REVIEW",
            packet_link_status="LINKED",
            blocked_codes=[
                "RAW_FILE_BODY_LOCKED",
                "REDACTION_REVIEW_REQUIRED",
                "EXTERNAL_ACCESS_DENIED",
            ],
            owner_action="Review redaction state before any binder preview.",
        ),
        _attachment_slot(
            attachment_id="VAT-OB-MANUAL-LIVE-001",
            intake_id="VIN-OB-PROOF-001",
            packet_id="ob_manual_live_private_proof_packet",
            packet_label="OB Manual Live Private Proof Packet",
            requirement_id="manual_live_receipt_chain",
            requirement_label="Manual Live receipt chain",
            lane="The Observatory / Manual Live",
            title="OB Manual Live private proof attachment slot",
            status="PACKET_LINKED",
            packet_link_status="LINKED",
            blocked_codes=[
                "RAW_FILE_BODY_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
            ],
            owner_action="Keep proof private and linked to receipt chain. Public proof remains locked.",
        ),
        _attachment_slot(
            attachment_id="VAT-SOULAANA-IP-001",
            intake_id="VIN-SOULAANA-IP-001",
            packet_id="soulaana_artist_ip_vault",
            packet_label="Soulaana Artist / IP Vault",
            requirement_id="artist_package_and_reserved_art_slot",
            requirement_label="Artist package and reserved art slot",
            lane="Soulaana / IP",
            title="Soulaana artist/IP attachment slot",
            status="NEEDS_PACKET_LINK",
            packet_link_status="PENDING_OWNER_CONFIRMATION",
            blocked_codes=[
                "RAW_FILE_BODY_LOCKED",
                "PACKET_LINK_REQUIRED",
                "TOWER_CLEARANCE_REQUIRED",
            ],
            owner_action="Confirm Soulaana packet link while preserving no-AI-character-art boundary.",
        ),
        _attachment_slot(
            attachment_id="VAT-BETA-NDA-001",
            intake_id="VIN-BETA-ONBOARD-001",
            packet_id="private_beta_onboarding_vault",
            packet_label="Private Beta Onboarding Vault",
            requirement_id="nda_access_and_beta_clearance",
            requirement_label="NDA access and beta clearance",
            lane="Private Beta",
            title="Private beta NDA/access attachment slot",
            status="BLOCKED_TOWER_CLEARANCE",
            packet_link_status="BLOCKED_TOWER",
            blocked_codes=[
                "RAW_FILE_BODY_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "DIRECT_UPLOAD_STILL_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
            ],
            owner_action="Wait for Tower clearance before completing attachment flow.",
        ),
    ]

    packet_links = _build_packet_links(slots)
    requirement_links = _build_requirement_links(slots)
    orphan_state = _build_orphan_state(gp011_queue, slots)
    owner_review = _build_owner_review_state(slots, packet_links, orphan_state)

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "depends_on": ["VAULT_GP011"],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "attachment_metadata_registry",
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "controlled_metadata_attachment_slots_enabled": True,
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
        "storage_truth": {
            "provider_configured": False,
            "provider_name": None,
            "file_body_storage_status": "blocked_by_provider_and_tower_clearance",
            "attachment_metadata_registry_status": "ready",
            "fake_storage_complete": False,
            "safe_next_unlock": "GP013 classifier and requirement match can continue without raw body storage.",
        },
        "registry_summary": {
            "room_title": "Vault Attachment Registry",
            "route": "/vault/attachments",
            "json_route": "/vault/attachments.json",
            "registry_route": "/vault/file-attachment-registry.json",
            "packet_links_route": "/vault/packet-links.json",
            "requirement_links_route": "/vault/attachment-requirement-links.json",
            "orphan_state_route": "/vault/attachment-orphan-state.json",
            "gp012_status_route": "/vault/gp012-status.json",
            "attachment_slot_count": len(slots),
            "packet_link_count": len(packet_links),
            "requirement_link_count": len(requirement_links),
            "raw_body_storage_enabled": False,
        },
        "attachment_slots": slots,
        "packet_links": packet_links,
        "requirement_links": requirement_links,
        "orphan_state": orphan_state,
        "owner_review_state": owner_review,
        "gp012_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp013": True,
            "next_pack": "VAULT_GP013_DOCUMENT_TYPE_CLASSIFIER_REQUIREMENT_MATCH",
            "gp011_intake_records_connected": True,
            "attachment_registry_metadata_only": True,
            "raw_file_body_storage_still_locked": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp012",
        },
    }

    return payload


def _build_packet_links(slots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    links: Dict[str, Dict[str, Any]] = {}

    for slot in slots:
        packet = slot["packet_link"]
        packet_id = packet["packet_id"]
        links.setdefault(
            packet_id,
            {
                "packet_id": packet_id,
                "packet_label": packet["packet_label"],
                "linked_attachment_ids": [],
                "lanes": [],
                "link_statuses": [],
                "tower_guard_required": True,
                "external_access_default": "denied",
            },
        )
        links[packet_id]["linked_attachment_ids"].append(slot["attachment_id"])
        links[packet_id]["lanes"].append(slot["lane"])
        links[packet_id]["link_statuses"].append(packet["packet_link_status"])

    output = []
    for packet_id, item in links.items():
        statuses = set(item["link_statuses"])
        item["linked_attachment_count"] = len(item["linked_attachment_ids"])
        item["lanes"] = sorted(set(item["lanes"]))
        item["packet_ready_for_completion"] = statuses == {"LINKED"}
        item["needs_owner_or_tower_action"] = not item["packet_ready_for_completion"]
        output.append(item)

    return output


def _build_requirement_links(slots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "attachment_id": slot["attachment_id"],
            "intake_id": slot["intake_id"],
            "packet_id": slot["packet_link"]["packet_id"],
            "requirement_id": slot["requirement_link"]["requirement_id"],
            "requirement_label": slot["requirement_link"]["requirement_label"],
            "requirement_linked": slot["requirement_link"]["requirement_linked"],
            "ready_for_gp013_classifier": True,
            "needs_requirement_match": not slot["requirement_link"]["requirement_linked"]
            or slot["status"] == "NEEDS_REQUIREMENT_LINK",
        }
        for slot in slots
    ]


def _build_orphan_state(gp011_queue: List[Dict[str, Any]], slots: List[Dict[str, Any]]) -> Dict[str, Any]:
    intake_ids = {item["intake_id"] for item in gp011_queue}
    linked_intake_ids = {slot["intake_id"] for slot in slots}

    intake_without_attachment_slot = sorted(intake_ids - linked_intake_ids)
    attachment_without_intake = sorted(linked_intake_ids - intake_ids)

    return {
        "intake_without_attachment_slot": intake_without_attachment_slot,
        "attachment_without_intake": attachment_without_intake,
        "orphan_intake_count": len(intake_without_attachment_slot),
        "orphan_attachment_count": len(attachment_without_intake),
        "orphan_safe_to_continue": len(attachment_without_intake) == 0,
        "owner_action": "Resolve orphan records before permanent storage unlock.",
    }


def _build_owner_review_state(
    slots: List[Dict[str, Any]],
    packet_links: List[Dict[str, Any]],
    orphan_state: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_count = sum(1 for slot in slots if slot["blocked_codes"])
    needs_packet_link = sum(1 for slot in slots if slot["status"] == "NEEDS_PACKET_LINK")
    needs_requirement_link = sum(1 for slot in slots if slot["status"] == "NEEDS_REQUIREMENT_LINK")
    needs_redaction_review = sum(1 for slot in slots if slot["status"] == "NEEDS_REDACTION_REVIEW")

    return {
        "review_room": "Vault Attachment Registry",
        "attachment_slot_count": len(slots),
        "blocked_attachment_count": blocked_count,
        "needs_packet_link_count": needs_packet_link,
        "needs_requirement_link_count": needs_requirement_link,
        "needs_redaction_review_count": needs_redaction_review,
        "packet_links_needing_action": [
            packet["packet_id"]
            for packet in packet_links
            if packet["needs_owner_or_tower_action"]
        ],
        "orphan_state": orphan_state,
        "next_owner_actions": [
            "Confirm attachment slots are linked to the correct packet.",
            "Confirm requirement checklist links before classifier work.",
            "Keep raw file-body storage blocked until provider and Tower clearance exist.",
            "Keep external access denied by default.",
            "Do not unlock direct upload from GP012.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_file_attachment_registry_payload())


def get_attachments_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "storage_truth": payload["storage_truth"],
        "registry_summary": payload["registry_summary"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_file_attachment_registry() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "attachment_slots": payload["attachment_slots"],
        "attachment_slot_count": len(payload["attachment_slots"]),
        "storage_truth": payload["storage_truth"],
    }


def get_packet_links() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "packet_links": payload["packet_links"],
        "packet_link_count": len(payload["packet_links"]),
    }


def get_attachment_requirement_links() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "requirement_links": payload["requirement_links"],
        "requirement_link_count": len(payload["requirement_links"]),
    }


def get_attachment_orphan_state() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "orphan_state": payload["orphan_state"],
    }


def get_gp012_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp012_status": payload["gp012_status"],
        "registry_summary": payload["registry_summary"],
        "storage_truth": payload["storage_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
    }


def render_attachment_registry_page() -> str:
    payload = clone_payload()
    summary = payload["registry_summary"]
    owner = payload["owner_review_state"]
    storage = payload["storage_truth"]
    slots = payload["attachment_slots"]

    cards = "\n".join(_render_attachment_card(slot) for slot in slots)
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    packet_rows = "\n".join(
        f"""
        <div class="link-row">
          <div>
            <strong>{escape(packet["packet_label"])}</strong>
            <span>{escape(packet["packet_id"])}</span>
          </div>
          <div class="pill {'ok' if packet["packet_ready_for_completion"] else 'warn'}">
            {'Ready' if packet["packet_ready_for_completion"] else 'Needs action'}
          </div>
        </div>
        """
        for packet in payload["packet_links"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Attachment Registry · GP012</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #040612;
      --bg1: #090f24;
      --panel: rgba(15, 23, 52, 0.80);
      --panel2: rgba(20, 31, 72, 0.74);
      --line: rgba(159, 178, 255, 0.23);
      --text: #edf2ff;
      --muted: #9ba8d6;
      --gold: #f5d07c;
      --violet: #aa8cff;
      --cyan: #83eaff;
      --danger: #ff8c9c;
      --ok: #9dffca;
      --shadow: rgba(0, 0, 0, 0.48);
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
        radial-gradient(circle at 14% 8%, rgba(170, 140, 255, 0.18), transparent 34%),
        radial-gradient(circle at 88% 4%, rgba(131, 234, 255, 0.13), transparent 30%),
        radial-gradient(circle at 70% 88%, rgba(245, 208, 124, 0.08), transparent 32%),
        linear-gradient(135deg, var(--bg0), var(--bg1) 52%, #03040b);
    }}

    .shell {{
      width: min(1200px, calc(100% - 32px));
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
        radial-gradient(circle at 16% 0%, rgba(245, 208, 124, 0.18), transparent 28%),
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
      max-width: 880px;
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
      border-color: rgba(245, 208, 124, .32);
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
      border-left: 3px solid rgba(245, 208, 124, .7);
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

    .link-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 12px 0;
      border-bottom: 1px solid rgba(159, 178, 255, .14);
    }}

    .link-row:last-child {{
      border-bottom: none;
    }}

    .link-row span {{
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
      .link-row {{
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
        <div class="eyebrow">Archive Vault · Giant Pack 012</div>
        <h1>Attachment Registry</h1>
        <p class="hero-copy">
          GP012 connects GP011 intake records to packet attachment slots and requirement links.
          This is real product depth, but still metadata-only. Raw file bodies, direct upload,
          downloads, and external access remain locked until provider configuration and Tower clearance exist.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["attachment_slot_count"]}</strong>
            <span>attachment slots</span>
          </div>
          <div class="metric">
            <strong>{summary["packet_link_count"]}</strong>
            <span>packet links</span>
          </div>
          <div class="metric">
            <strong>{summary["requirement_link_count"]}</strong>
            <span>requirement links</span>
          </div>
          <div class="metric">
            <strong>Locked</strong>
            <span>raw file storage</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Metadata registry ready</span>
          <span class="pill warn">Provider not configured</span>
          <span class="pill warn">Tower clearance required</span>
          <span class="pill danger">Direct upload locked</span>
          <span class="pill danger">External access denied</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Attachment Slots</h2>
      <p>
        Every slot is linked to an intake record and packet target. File body fields stay empty by design.
      </p>
      <div class="grid">
        {cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Packet Link Board</h2>
        <p>Packets show whether owner/Tower action is still needed.</p>
        <div>
          {packet_rows}
        </div>
      </div>
      <div>
        <h2>Owner Review</h2>
        <p>GP012 prepares the road for classifier and requirement matching in GP013.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP012 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["registry_route"])}</code>
        <code>{escape(summary["packet_links_route"])}</code>
        <code>{escape(summary["requirement_links_route"])}</code>
        <code>{escape(summary["orphan_state_route"])}</code>
        <code>{escape(summary["gp012_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Storage Truth</h2>
      <p>
        Provider configured:
        <code>{str(storage["provider_configured"]).lower()}</code>.
        File-body status:
        <code>{escape(storage["file_body_storage_status"])}</code>.
        Fake storage complete:
        <code>{str(storage["fake_storage_complete"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_attachment_card(slot: Dict[str, Any]) -> str:
    blocked = slot.get("blocked_codes") or []
    blocked_chips = "\n".join(
        f'<span class="pill danger">{escape(code)}</span>'
        for code in blocked
    )
    if not blocked_chips:
        blocked_chips = '<span class="pill ok">NO_BLOCK_CODE</span>'

    packet = slot["packet_link"]
    requirement = slot["requirement_link"]

    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(slot["title"])}</div>
            <div class="meta">
              Attachment: <code>{escape(slot["attachment_id"])}</code><br>
              Intake: <code>{escape(slot["intake_id"])}</code><br>
              Lane: {escape(slot["lane"])}<br>
              Packet: <code>{escape(packet["packet_id"])}</code><br>
              Requirement: <code>{escape(requirement["requirement_id"])}</code>
            </div>
          </div>
          <span class="pill warn">{escape(slot["status_label"])}</span>
        </div>
        <div class="chips">{blocked_chips}</div>
        <div class="action">
          Owner action: {escape(slot["owner_action"])}
        </div>
      </article>
    """
