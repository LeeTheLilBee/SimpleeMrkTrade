"""
VAULT GIANT PACK 011 — Real Document Intake + Vault Inbox

This module starts the real Vault product body after GP001-GP010.

Boundaries:
- Vault owns document intake organization, packet linking, proof tracking,
  redaction readiness, owner review state, and safe registry surfaces.
- The Tower owns identity, permission, clearance, step-up, export locks,
  freeze/revoke, external access authority, and unlock decisions.
- Direct raw upload remains locked.
- File-body storage is not fake-complete. It stays blocked until a real provider
  and Tower clearance path exist.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List


PACK_ID = "VAULT_GP011"
PACK_NAME = "Real Document Intake + Vault Inbox"
PACK_ROUTE_PREFIX = "/vault"
SCHEMA_VERSION = "vault.document_intake.v1"

INTAKE_STATUSES = {
    "READY_FOR_OWNER_REVIEW": "Ready for owner review",
    "BLOCKED_PROVIDER": "Blocked by storage provider",
    "BLOCKED_TOWER": "Blocked by Tower clearance",
    "NEEDS_PACKET_LINK": "Needs packet link",
    "NEEDS_REQUIREMENT_MATCH": "Needs requirement match",
    "NEEDS_REDACTION_REVIEW": "Needs redaction review",
    "STAGED_METADATA_ONLY": "Staged metadata only",
}

DOCUMENT_CLASSES = {
    "ATM_ROUTE": "ATM Route Acquisition",
    "APARTMENT_LENDER": "Apartment Lender / Due Diligence",
    "TRUST_ENTITY": "Trust / Entity Proof",
    "OB_MANUAL_LIVE": "OB Manual Live Private Proof",
    "SOULAANA_IP": "Soulaana Artist / IP",
    "BETA_ONBOARDING": "Private Beta Onboarding",
    "GENERAL_OWNER_RECORD": "General Owner Record",
}

BLOCK_CODES = {
    "DIRECT_UPLOAD_LOCKED": "Direct raw upload is not unlocked.",
    "FILE_PROVIDER_NOT_CONFIGURED": "Permanent file-body storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive file movement.",
    "MISSING_PACKET_LINK": "Document must be linked to a Vault packet before completion.",
    "UNCLASSIFIED_DOCUMENT_TYPE": "Document type must be classified before filing.",
    "REDACTION_REQUIRED_BEFORE_EXPORT": "Redaction review is required before any export preview.",
    "EXTERNAL_ACCESS_DEFAULT_DENIED": "External access is denied by default.",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _record(
    intake_id: str,
    title: str,
    lane: str,
    document_class: str,
    status: str,
    packet_target: str,
    requirement_target: str,
    owner_action: str,
    blocked_codes: List[str] | None = None,
    sensitivity: str = "sensitive_metadata_only",
) -> Dict[str, Any]:
    blocked_codes = blocked_codes or []
    return {
        "intake_id": intake_id,
        "title": title,
        "lane": lane,
        "document_class": document_class,
        "document_class_label": DOCUMENT_CLASSES.get(document_class, document_class),
        "status": status,
        "status_label": INTAKE_STATUSES.get(status, status),
        "packet_target": packet_target,
        "requirement_target": requirement_target,
        "owner_action": owner_action,
        "blocked_codes": blocked_codes,
        "blocked_labels": [BLOCK_CODES.get(code, code) for code in blocked_codes],
        "sensitivity": sensitivity,
        "body_storage": {
            "file_body_attached": False,
            "file_body_storage_status": "blocked_until_provider_and_tower_clearance",
            "file_body_display_allowed": False,
            "raw_file_download_allowed": False,
        },
        "redaction": {
            "summary_safe": True,
            "body_redacted_until_review": True,
            "unredacted_export_allowed": False,
            "external_preview_allowed": False,
        },
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_source": "The Tower",
            "vault_permission_owner": False,
            "step_up_required_for_sensitive_actions": True,
        },
        "record_origin": "system_seed_registry_no_private_body",
    }


@lru_cache(maxsize=1)
def get_document_intake_payload() -> Dict[str, Any]:
    """
    Cached non-recursive GP011 payload.

    This is intentionally registry-first:
    it creates real intake workflow surfaces without pretending permanent file
    storage exists before provider configuration and Tower clearance.
    """

    intake_queue = [
        _record(
            intake_id="VIN-ATM-ROUTE-001",
            title="ATM route seller packet intake",
            lane="SimpleeOnTheGo / ATM",
            document_class="ATM_ROUTE",
            status="STAGED_METADATA_ONLY",
            packet_target="atm_route_acquisition_packet",
            requirement_target="seller_financials_and_route_list",
            owner_action="Review packet target and confirm required seller documents.",
            blocked_codes=["FILE_PROVIDER_NOT_CONFIGURED", "TOWER_CLEARANCE_REQUIRED"],
        ),
        _record(
            intake_id="VIN-APT-LENDER-001",
            title="Apartment lender due diligence intake",
            lane="SimpleeProperty / Apartment",
            document_class="APARTMENT_LENDER",
            status="NEEDS_REQUIREMENT_MATCH",
            packet_target="apartment_lender_due_diligence_packet",
            requirement_target="lender_packet_requirements",
            owner_action="Match incoming document type to lender requirement checklist.",
            blocked_codes=["FILE_PROVIDER_NOT_CONFIGURED"],
        ),
        _record(
            intake_id="VIN-TRUST-ENTITY-001",
            title="Trust and entity proof intake",
            lane="Trust / Entity",
            document_class="TRUST_ENTITY",
            status="NEEDS_REDACTION_REVIEW",
            packet_target="trust_entity_binder",
            requirement_target="trust_formation_and_entity_proof",
            owner_action="Confirm redacted summary before any owner-facing preview.",
            blocked_codes=["REDACTION_REQUIRED_BEFORE_EXPORT", "EXTERNAL_ACCESS_DEFAULT_DENIED"],
        ),
        _record(
            intake_id="VIN-OB-PROOF-001",
            title="OB Manual Live private proof intake",
            lane="The Observatory / Manual Live",
            document_class="OB_MANUAL_LIVE",
            status="READY_FOR_OWNER_REVIEW",
            packet_target="ob_manual_live_private_proof_packet",
            requirement_target="manual_live_receipt_chain",
            owner_action="Review private proof metadata and keep public proof locked.",
            blocked_codes=[],
        ),
        _record(
            intake_id="VIN-SOULAANA-IP-001",
            title="Soulaana artist and IP package intake",
            lane="Soulaana / IP",
            document_class="SOULAANA_IP",
            status="NEEDS_PACKET_LINK",
            packet_target="soulaana_artist_ip_vault",
            requirement_target="artist_package_and_reserved_art_slot",
            owner_action="Link staged record to Soulaana artist/IP packet.",
            blocked_codes=["MISSING_PACKET_LINK", "TOWER_CLEARANCE_REQUIRED"],
        ),
        _record(
            intake_id="VIN-BETA-ONBOARD-001",
            title="Private beta onboarding document intake",
            lane="Private Beta",
            document_class="BETA_ONBOARDING",
            status="BLOCKED_TOWER",
            packet_target="private_beta_onboarding_vault",
            requirement_target="nda_access_and_beta_clearance",
            owner_action="Wait for Tower clearance before intake completion.",
            blocked_codes=["TOWER_CLEARANCE_REQUIRED", "EXTERNAL_ACCESS_DEFAULT_DENIED"],
        ),
    ]

    blocked_intake_reasons = [
        {
            "code": code,
            "label": label,
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code else "Vault",
            "vault_response": _vault_response_for_block(code),
            "safe_to_override_inside_vault": False,
        }
        for code, label in BLOCK_CODES.items()
    ]

    owner_review_state = {
        "review_room": "Vault Inbox",
        "owner_queue_count": len(intake_queue),
        "ready_for_owner_review_count": sum(
            1 for item in intake_queue if item["status"] == "READY_FOR_OWNER_REVIEW"
        ),
        "blocked_count": sum(1 for item in intake_queue if item["blocked_codes"]),
        "needs_packet_link_count": sum(
            1 for item in intake_queue if item["status"] == "NEEDS_PACKET_LINK"
        ),
        "needs_requirement_match_count": sum(
            1 for item in intake_queue if item["status"] == "NEEDS_REQUIREMENT_MATCH"
        ),
        "needs_redaction_review_count": sum(
            1 for item in intake_queue if item["status"] == "NEEDS_REDACTION_REVIEW"
        ),
        "next_owner_actions": [
            "Review metadata-only intake records.",
            "Confirm packet target before filing.",
            "Match document class to requirement tracker.",
            "Keep raw body storage blocked until provider and Tower clearance exist.",
            "Keep external access denied by default.",
        ],
    }

    payload = {
        "pack": {
            "id": PACK_ID,
            "name": PACK_NAME,
            "schema_version": SCHEMA_VERSION,
            "generated_at": _now_iso(),
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_started": True,
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "controlled_staged_intake_enabled": True,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "sensitive_packet_body_in_summary_views": False,
            "broker_secret_storage_allowed": False,
            "ob_auto_execution_allowed": False,
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
        "storage_provider_state": {
            "provider_configured": False,
            "provider_name": None,
            "file_body_storage_status": "blocked_by_provider_and_tower_clearance",
            "metadata_registry_status": "ready",
            "fake_file_storage_complete": False,
            "next_unlock_requirement": "Configure permanent file-body storage provider and connect Tower clearance path.",
        },
        "inbox_summary": {
            "room_title": "Vault Inbox",
            "route": "/vault/inbox",
            "json_route": "/vault/inbox.json",
            "queue_route": "/vault/intake-queue.json",
            "records_route": "/vault/document-intake-records.json",
            "blocked_reasons_route": "/vault/blocked-intake-reasons.json",
            "owner_review_route": "/vault/owner-review-state.json",
            "total_intake_records": len(intake_queue),
            "real_registry_workflow_enabled": True,
            "raw_body_storage_enabled": False,
        },
        "intake_queue": intake_queue,
        "document_intake_records": intake_queue,
        "blocked_intake_reasons": blocked_intake_reasons,
        "owner_review_state": owner_review_state,
        "gp011_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp012": True,
            "next_pack": "VAULT_GP012_FILE_ATTACHMENT_REGISTRY_PACKET_LINKING",
            "blocked_items_are_explicit_not_fake_complete": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp011",
        },
    }

    return payload


def _vault_response_for_block(code: str) -> str:
    responses = {
        "DIRECT_UPLOAD_LOCKED": "Show staged intake metadata only. Do not unlock raw upload.",
        "FILE_PROVIDER_NOT_CONFIGURED": "Track intake record and packet target. Block file body storage.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower permission, clearance, or step-up result.",
        "MISSING_PACKET_LINK": "Hold in inbox until owner chooses a packet or creates one.",
        "UNCLASSIFIED_DOCUMENT_TYPE": "Hold for classifier or owner document type selection.",
        "REDACTION_REQUIRED_BEFORE_EXPORT": "Allow safe summary only. Block external previews.",
        "EXTERNAL_ACCESS_DEFAULT_DENIED": "Keep external access locked unless Tower grants access.",
    }
    return responses.get(code, "Hold intake safely and require owner review.")


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_document_intake_payload())


def get_inbox_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "storage_provider_state": payload["storage_provider_state"],
        "inbox_summary": payload["inbox_summary"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_intake_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "intake_queue": payload["intake_queue"],
        "queue_count": len(payload["intake_queue"]),
        "direct_raw_upload_unlocked": False,
    }


def get_document_intake_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "document_intake_records": payload["document_intake_records"],
        "record_count": len(payload["document_intake_records"]),
        "file_body_storage_status": payload["storage_provider_state"]["file_body_storage_status"],
    }


def get_blocked_intake_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocked_intake_reasons": payload["blocked_intake_reasons"],
        "blocked_reason_count": len(payload["blocked_intake_reasons"]),
    }


def get_owner_review_state() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp011_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp011_status": payload["gp011_status"],
        "inbox_summary": payload["inbox_summary"],
        "storage_provider_state": payload["storage_provider_state"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
    }


def render_vault_inbox_page() -> str:
    payload = clone_payload()
    summary = payload["inbox_summary"]
    queue = payload["intake_queue"]
    owner_state = payload["owner_review_state"]
    storage = payload["storage_provider_state"]

    cards = "\n".join(_render_intake_card(item) for item in queue)
    block_chips = "\n".join(
        f'<span class="vault-chip danger">{escape(reason["code"])}</span>'
        for reason in payload["blocked_intake_reasons"]
    )

    actions = "\n".join(
        f"<li>{escape(action)}</li>"
        for action in owner_state["next_owner_actions"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Inbox · GP011</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg0: #050712;
      --bg1: #080d1f;
      --panel: rgba(17, 24, 52, 0.78);
      --panel2: rgba(22, 32, 70, 0.72);
      --line: rgba(152, 170, 255, 0.22);
      --text: #e9efff;
      --muted: #9ba8d6;
      --gold: #f4cf7a;
      --violet: #a98cff;
      --cyan: #80e8ff;
      --danger: #ff8b9b;
      --ok: #9dffca;
      --shadow: rgba(0, 0, 0, 0.45);
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
        radial-gradient(circle at 12% 8%, rgba(169, 140, 255, 0.18), transparent 34%),
        radial-gradient(circle at 82% 0%, rgba(128, 232, 255, 0.14), transparent 28%),
        linear-gradient(135deg, var(--bg0), var(--bg1) 46%, #03040b);
    }}

    .vault-shell {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 34px 0 48px;
    }}

    .vault-hero {{
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 28px;
      background: linear-gradient(145deg, rgba(17, 24, 52, 0.92), rgba(8, 13, 31, 0.74));
      box-shadow: 0 28px 70px var(--shadow);
      position: relative;
      overflow: hidden;
    }}

    .vault-hero:before {{
      content: "";
      position: absolute;
      inset: -2px;
      background:
        radial-gradient(circle at 18% 0%, rgba(244, 207, 122, 0.18), transparent 28%),
        radial-gradient(circle at 92% 30%, rgba(128, 232, 255, 0.12), transparent 26%);
      pointer-events: none;
    }}

    .vault-hero-inner {{
      position: relative;
      z-index: 1;
    }}

    .eyebrow {{
      color: var(--gold);
      letter-spacing: .18em;
      text-transform: uppercase;
      font-size: 12px;
      font-weight: 800;
    }}

    h1 {{
      font-size: clamp(34px, 5vw, 62px);
      line-height: .94;
      margin: 14px 0 14px;
    }}

    .hero-copy {{
      color: var(--muted);
      font-size: 16px;
      max-width: 850px;
      line-height: 1.65;
    }}

    .vault-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 22px;
    }}

    .metric {{
      border: 1px solid var(--line);
      background: rgba(5, 8, 20, 0.46);
      border-radius: 20px;
      padding: 16px;
    }}

    .metric strong {{
      display: block;
      font-size: 26px;
      color: var(--text);
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

    .section p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }}

    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}

    .vault-chip {{
      display: inline-flex;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 7px 10px;
      font-size: 12px;
      font-weight: 750;
      color: var(--text);
      background: rgba(10, 16, 38, .72);
    }}

    .vault-chip.ok {{
      color: var(--ok);
      border-color: rgba(157, 255, 202, .32);
    }}

    .vault-chip.warn {{
      color: var(--gold);
      border-color: rgba(244, 207, 122, .32);
    }}

    .vault-chip.danger {{
      color: var(--danger);
      border-color: rgba(255, 139, 155, .32);
    }}

    .inbox-list {{
      display: grid;
      gap: 12px;
      margin-top: 16px;
    }}

    .intake-card {{
      border: 1px solid var(--line);
      background: var(--panel2);
      border-radius: 20px;
      padding: 16px;
    }}

    .intake-top {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: flex-start;
    }}

    .intake-title {{
      font-weight: 850;
      font-size: 16px;
    }}

    .intake-meta {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 7px;
      line-height: 1.55;
    }}

    .intake-action {{
      margin-top: 12px;
      color: var(--text);
      font-size: 14px;
      line-height: 1.55;
      border-left: 3px solid rgba(244, 207, 122, .7);
      padding-left: 12px;
    }}

    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }}

    ul {{
      margin: 14px 0 0;
      color: var(--muted);
      line-height: 1.75;
    }}

    code {{
      color: var(--cyan);
      background: rgba(0, 0, 0, .28);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 2px 6px;
    }}

    @media (max-width: 900px) {{
      .vault-grid,
      .two-col {{
        grid-template-columns: 1fr;
      }}

      .intake-top {{
        flex-direction: column;
      }}
    }}
  </style>
</head>
<body>
  <main class="vault-shell">
    <section class="vault-hero">
      <div class="vault-hero-inner">
        <div class="eyebrow">Archive Vault · Giant Pack 011</div>
        <h1>Vault Inbox</h1>
        <p class="hero-copy">
          Real document intake starts here. This room tracks incoming document records,
          packet targets, blocked reasons, owner review state, and storage boundaries.
          Raw file-body storage remains locked until a real provider and Tower clearance path exist.
        </p>

        <div class="vault-grid">
          <div class="metric">
            <strong>{summary["total_intake_records"]}</strong>
            <span>intake records</span>
          </div>
          <div class="metric">
            <strong>{owner_state["blocked_count"]}</strong>
            <span>blocked safely</span>
          </div>
          <div class="metric">
            <strong>{owner_state["ready_for_owner_review_count"]}</strong>
            <span>ready for review</span>
          </div>
          <div class="metric">
            <strong>Locked</strong>
            <span>raw upload + external access</span>
          </div>
        </div>

        <div class="chips">
          <span class="vault-chip ok">Metadata registry ready</span>
          <span class="vault-chip warn">File-body storage blocked</span>
          <span class="vault-chip warn">Tower clearance required</span>
          <span class="vault-chip danger">Direct raw upload locked</span>
          <span class="vault-chip danger">External access denied</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Inbox Queue</h2>
      <p>
        Every item below is safe metadata only. Vault is not pretending private file storage exists.
        The body-storage lane stays blocked until provider configuration and Tower authority are connected.
      </p>
      <div class="inbox-list">
        {cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Owner Review State</h2>
        <p>Next actions stay simple, visible, and locked inside Vault owner review.</p>
        <ul>
          {actions}
        </ul>
      </div>
      <div>
        <h2>Blocked Intake Reasons</h2>
        <p>These blocks are deliberate. They prevent fake completion and protect sensitive records.</p>
        <div class="chips">
          {block_chips}
        </div>
      </div>
    </section>

    <section class="section">
      <h2>GP011 JSON Endpoints</h2>
      <p>
        <code>/vault/inbox.json</code>
        <code>/vault/intake-queue.json</code>
        <code>/vault/document-intake-records.json</code>
        <code>/vault/blocked-intake-reasons.json</code>
        <code>/vault/owner-review-state.json</code>
        <code>/vault/gp011-status.json</code>
      </p>
    </section>

    <section class="section">
      <h2>Storage Truth</h2>
      <p>
        Provider configured:
        <code>{str(storage["provider_configured"]).lower()}</code>.
        File-body status:
        <code>{escape(storage["file_body_storage_status"])}</code>.
        This is correct for GP011.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_intake_card(item: Dict[str, Any]) -> str:
    blocked = item.get("blocked_codes") or []
    blocked_chips = "\n".join(
        f'<span class="vault-chip danger">{escape(code)}</span>'
        for code in blocked
    )
    if not blocked_chips:
        blocked_chips = '<span class="vault-chip ok">NO_BLOCK_CODE</span>'

    return f"""
      <article class="intake-card">
        <div class="intake-top">
          <div>
            <div class="intake-title">{escape(item["title"])}</div>
            <div class="intake-meta">
              ID: <code>{escape(item["intake_id"])}</code><br>
              Lane: {escape(item["lane"])}<br>
              Class: {escape(item["document_class_label"])}<br>
              Packet target: <code>{escape(item["packet_target"])}</code><br>
              Requirement: <code>{escape(item["requirement_target"])}</code>
            </div>
          </div>
          <span class="vault-chip warn">{escape(item["status_label"])}</span>
        </div>
        <div class="chips">{blocked_chips}</div>
        <div class="intake-action">
          Owner action: {escape(item["owner_action"])}
        </div>
      </article>
    """
