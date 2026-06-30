"""
VAULT GIANT PACK 016 — Evidence Binder Builder

This pack turns GP015 metadata version lineage into owner-safe evidence binders.

Important truth:
- Evidence binders are metadata-only in GP016.
- No raw file bodies are stored, read, downloaded, copied, or previewed.
- No public proof is created.
- No external access is granted.
- No unredacted export is allowed.
- Binders are safe owner review surfaces that prepare the road for GP017 ATM Route Packet Workspace v2.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  and external access authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.version_history_replace_supersede_flow_service import get_version_history_payload


PACK_ID = "VAULT_GP016"
PACK_NAME = "Evidence Binder Builder"
SCHEMA_VERSION = "vault.evidence_binder_builder.v1"

BINDER_STATUSES = {
    "BINDER_METADATA_READY": "Binder metadata ready",
    "NEEDS_OWNER_REVIEW": "Needs owner review",
    "NEEDS_REDACTION_REVIEW": "Needs redaction review",
    "BLOCKED_TOWER_CLEARANCE": "Blocked by Tower clearance",
    "BLOCKED_STORAGE_PROVIDER": "Blocked by storage provider",
    "HELD_METADATA_ONLY": "Held metadata only",
}

BINDER_TYPES = {
    "atm_route_acquisition": "ATM Route Acquisition Evidence Binder",
    "apartment_lender_due_diligence": "Apartment Lender Due Diligence Evidence Binder",
    "trust_entity": "Trust / Entity Evidence Binder",
    "ob_manual_live_private_proof": "OB Manual Live Private Proof Evidence Binder",
    "soulaana_artist_ip": "Soulaana Artist / IP Evidence Binder",
    "private_beta_onboarding": "Private Beta Onboarding Evidence Binder",
}

BINDER_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive binder movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before binder completion.",
    "REDACTION_REVIEW_REQUIRED": "Redaction review is required before preview/export.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_PREVIEW_LOCKED": "Unredacted preview is locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof is locked.",
    "NO_RAW_BINDER_EXPORT": "Raw binder export is disabled.",
    "NO_AUTO_BINDER_COMPLETE": "Automatic binder completion is disabled.",
}

BINDER_BLUEPRINTS = [
    {
        "binder_id": "VEB-ATM-ROUTE-001",
        "binder_type": "atm_route_acquisition",
        "lane": "SimpleeOnTheGo / ATM",
        "packet_id": "atm_route_acquisition_packet",
        "owner_goal": "Prepare ATM route acquisition evidence for owner and lender-style review.",
        "next_workspace": "VAULT_GP017_ATM_ROUTE_PACKET_WORKSPACE_V2",
    },
    {
        "binder_id": "VEB-APT-LENDER-001",
        "binder_type": "apartment_lender_due_diligence",
        "lane": "SimpleeProperty / Apartment",
        "packet_id": "apartment_lender_due_diligence_packet",
        "owner_goal": "Prepare apartment lender due diligence evidence for lender packet review.",
        "next_workspace": "VAULT_GP018_APARTMENT_LENDER_PACKET_WORKSPACE_V2",
    },
    {
        "binder_id": "VEB-TRUST-ENTITY-001",
        "binder_type": "trust_entity",
        "lane": "Trust / Entity",
        "packet_id": "trust_entity_binder",
        "owner_goal": "Prepare trust and entity proof evidence for private owner review.",
        "next_workspace": "VAULT_GP019_TRUST_ENTITY_BINDER_WORKSPACE_V2",
    },
    {
        "binder_id": "VEB-OB-MANUAL-LIVE-001",
        "binder_type": "ob_manual_live_private_proof",
        "lane": "The Observatory / Manual Live",
        "packet_id": "ob_manual_live_private_proof_packet",
        "owner_goal": "Prepare private OB Manual Live proof evidence without public proof exposure.",
        "next_workspace": "VAULT_GP020_OPERATIONAL_READINESS_CHECKPOINT",
    },
    {
        "binder_id": "VEB-SOULAANA-IP-001",
        "binder_type": "soulaana_artist_ip",
        "lane": "Soulaana / IP",
        "packet_id": "soulaana_artist_ip_vault",
        "owner_goal": "Prepare Soulaana artist/IP evidence while preserving reserved art and no-AI-character-art boundaries.",
        "next_workspace": "VAULT_GP020_OPERATIONAL_READINESS_CHECKPOINT",
    },
    {
        "binder_id": "VEB-BETA-ONBOARD-001",
        "binder_type": "private_beta_onboarding",
        "lane": "Private Beta",
        "packet_id": "private_beta_onboarding_vault",
        "owner_goal": "Prepare private beta onboarding evidence while keeping Tower access authority locked.",
        "next_workspace": "VAULT_GP020_OPERATIONAL_READINESS_CHECKPOINT",
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_evidence_binder_payload() -> Dict[str, Any]:
    gp015 = get_version_history_payload()
    version_records = gp015["version_records"]
    lineage_items = gp015["version_lineage"]["lineage_items"]

    binders = [
        _build_binder(blueprint, version_records, lineage_items)
        for blueprint in BINDER_BLUEPRINTS
    ]

    binder_packets = _build_binder_packets(binders)
    requirement_coverage = _build_requirement_coverage(binders)
    export_preview = _build_safe_export_preview(binders)
    blocked_reasons = _build_blocked_reasons(binders)
    owner_state = _build_owner_state(binders, requirement_coverage, export_preview)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "metadata_evidence_binder_builder",
        },
        "binder_truth": {
            "binder_metadata_enabled": True,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "raw_binder_export_enabled": False,
            "redacted_export_preview_enabled": True,
            "unredacted_export_enabled": False,
            "public_proof_enabled": False,
            "external_access_enabled": False,
            "auto_binder_completion_enabled": False,
            "fake_binder_body_complete": False,
            "safe_next_unlock": "GP017 ATM Route Packet Workspace v2 can use binder metadata without raw file storage.",
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "raw_binder_export_allowed": False,
            "redacted_export_preview_allowed": True,
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
        "binder_summary": {
            "room_title": "Vault Evidence Binder Builder",
            "route": "/vault/evidence-binder",
            "json_route": "/vault/evidence-binder.json",
            "builder_route": "/vault/evidence-binder-builder.json",
            "packets_route": "/vault/evidence-binder-packets.json",
            "requirements_route": "/vault/evidence-binder-requirements.json",
            "export_preview_route": "/vault/evidence-binder-export-preview.json",
            "blocked_reasons_route": "/vault/evidence-binder-blocked-reasons.json",
            "gp016_status_route": "/vault/gp016-status.json",
            "binder_count": len(binders),
            "binder_packet_count": len(binder_packets["packet_items"]),
            "requirement_coverage_count": len(requirement_coverage["coverage_items"]),
            "redacted_export_preview_count": len(export_preview["preview_items"]),
            "raw_body_storage_enabled": False,
            "direct_upload_unlocked": False,
        },
        "evidence_binders": binders,
        "evidence_binder_packets": binder_packets,
        "evidence_binder_requirements": requirement_coverage,
        "evidence_binder_export_preview": export_preview,
        "evidence_binder_blocked_reasons": blocked_reasons,
        "owner_review_state": owner_state,
        "gp016_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp017": True,
            "next_pack": "VAULT_GP017_ATM_ROUTE_PACKET_WORKSPACE_V2",
            "gp015_version_lineage_connected": True,
            "evidence_binder_metadata_ready": True,
            "redacted_export_preview_only": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "raw_binder_export_still_locked": True,
            "public_proof_still_locked": True,
            "fake_binder_body_completion_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp016",
        },
    }

    return payload


def _build_binder(
    blueprint: Dict[str, Any],
    version_records: List[Dict[str, Any]],
    lineage_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    packet_id = blueprint["packet_id"]
    matching_versions = [record for record in version_records if record["packet_id"] == packet_id]
    matching_lineage = [item for item in lineage_items if item["packet_id"] == packet_id]

    status, blocked_codes, owner_action = _binder_status_from_versions(matching_versions)

    section_items = [
        _build_binder_section(record)
        for record in matching_versions
    ]

    if not section_items:
        section_items = [
            {
                "section_id": f"{blueprint['binder_id']}-EMPTY",
                "document_key": None,
                "version_id": None,
                "attachment_id": None,
                "requirement_id": None,
                "section_label": "No metadata version available yet",
                "section_status": "missing_metadata_version",
                "summary_safe": True,
                "body_available": False,
                "raw_preview_allowed": False,
                "redacted_preview_allowed": False,
                "owner_action": "Connect a metadata version record before binder completion.",
            }
        ]

    return {
        "binder_id": blueprint["binder_id"],
        "binder_type": blueprint["binder_type"],
        "binder_type_label": BINDER_TYPES[blueprint["binder_type"]],
        "lane": blueprint["lane"],
        "packet_id": packet_id,
        "owner_goal": blueprint["owner_goal"],
        "next_workspace": blueprint["next_workspace"],
        "binder_status": status,
        "binder_status_label": BINDER_STATUSES.get(status, status),
        "section_count": len(section_items),
        "version_ids": [record["version_id"] for record in matching_versions],
        "document_keys": [record["document_key"] for record in matching_versions],
        "lineage_ids": [item["lineage_id"] for item in matching_lineage],
        "sections": section_items,
        "binder_controls": {
            "owner_confirmation_required": True,
            "tower_clearance_required_for_sensitive_steps": True,
            "raw_body_storage_enabled": False,
            "direct_upload_allowed": False,
            "raw_download_allowed": False,
            "unredacted_preview_allowed": False,
            "redacted_export_preview_allowed": True,
            "external_access_allowed": False,
            "public_proof_allowed": False,
            "auto_complete_allowed": False,
        },
        "blocked_codes": blocked_codes,
        "blocked_labels": [BINDER_BLOCK_CODES.get(code, code) for code in blocked_codes],
        "owner_action": owner_action,
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_owner": True,
            "vault_permission_owner": False,
            "step_up_required_for_export_external_access": True,
            "external_access_default": "denied",
        },
        "redaction_boundary": {
            "summary_safe": True,
            "redaction_required_before_export": True,
            "redacted_preview_available": True,
            "unredacted_preview_allowed": False,
            "external_preview_allowed": False,
        },
    }


def _binder_status_from_versions(version_records: List[Dict[str, Any]]) -> tuple[str, List[str], str]:
    base_blocks = {
        "RAW_FILE_BODY_LOCKED",
        "DIRECT_UPLOAD_LOCKED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_PREVIEW_LOCKED",
        "PUBLIC_PROOF_LOCKED",
        "NO_RAW_BINDER_EXPORT",
        "NO_AUTO_BINDER_COMPLETE",
        "OWNER_CONFIRMATION_REQUIRED",
    }

    if not version_records:
        return (
            "HELD_METADATA_ONLY",
            sorted(base_blocks | {"PERMANENT_STORAGE_NOT_CONFIGURED"}),
            "Hold binder until a metadata version record exists.",
        )

    record_blocks = {code for record in version_records for code in record.get("blocked_codes", [])}

    if "TOWER_CLEARANCE_REQUIRED" in record_blocks:
        return (
            "BLOCKED_TOWER_CLEARANCE",
            sorted(base_blocks | {"TOWER_CLEARANCE_REQUIRED"}),
            "Keep binder metadata staged and wait for Tower clearance before sensitive movement.",
        )

    if "PERMANENT_STORAGE_NOT_CONFIGURED" in record_blocks:
        return (
            "BLOCKED_STORAGE_PROVIDER",
            sorted(base_blocks | {"PERMANENT_STORAGE_NOT_CONFIGURED"}),
            "Keep binder metadata-only until storage provider exists.",
        )

    if "REDACTION_REVIEW_REQUIRED" in record_blocks:
        return (
            "NEEDS_REDACTION_REVIEW",
            sorted(base_blocks | {"REDACTION_REVIEW_REQUIRED"}),
            "Route binder through redaction review before any export preview is treated as ready.",
        )

    return (
        "BINDER_METADATA_READY",
        sorted(base_blocks),
        "Review metadata binder and carry safe packet focus into the next Vault workspace.",
    )


def _build_binder_section(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "section_id": f"VBS-{record['attachment_id'].replace('VAT-', '')}",
        "document_key": record["document_key"],
        "version_id": record["version_id"],
        "attachment_id": record["attachment_id"],
        "review_id": record["review_id"],
        "classification_id": record["classification_id"],
        "intake_id": record["intake_id"],
        "requirement_id": record["requirement_id"],
        "section_label": record["predicted_document_label"],
        "section_status": "metadata_version_linked",
        "lineage_status": record["lineage_status"],
        "summary_safe": True,
        "body_available": False,
        "body_storage_uri": None,
        "raw_preview_allowed": False,
        "redacted_preview_allowed": True,
        "external_preview_allowed": False,
        "owner_action": "Review metadata section. Do not treat as raw file proof.",
    }


def _build_binder_packets(binders: List[Dict[str, Any]]) -> Dict[str, Any]:
    packet_items = []

    for binder in binders:
        packet_items.append(
            {
                "packet_binder_id": f"VBP-{binder['binder_id'].replace('VEB-', '')}",
                "binder_id": binder["binder_id"],
                "packet_id": binder["packet_id"],
                "binder_type": binder["binder_type"],
                "lane": binder["lane"],
                "section_count": binder["section_count"],
                "version_ids": binder["version_ids"],
                "ready_for_owner_packet_review": binder["section_count"] > 0,
                "ready_for_external_packet_share": False,
                "reason_external_share_blocked": "External access is denied by default and Tower-owned.",
            }
        )

    return {
        "packet_items": packet_items,
        "packet_count": len(packet_items),
        "ready_for_owner_packet_review_count": sum(
            1 for item in packet_items if item["ready_for_owner_packet_review"]
        ),
        "ready_for_external_packet_share_count": 0,
    }


def _build_requirement_coverage(binders: List[Dict[str, Any]]) -> Dict[str, Any]:
    coverage_items = []

    for binder in binders:
        requirement_ids = sorted({
            section["requirement_id"]
            for section in binder["sections"]
            if section.get("requirement_id")
        })

        coverage_items.append(
            {
                "coverage_id": f"VBC-{binder['binder_id'].replace('VEB-', '')}",
                "binder_id": binder["binder_id"],
                "packet_id": binder["packet_id"],
                "binder_type": binder["binder_type"],
                "requirement_ids": requirement_ids,
                "covered_requirement_count": len(requirement_ids),
                "metadata_sections_count": binder["section_count"],
                "coverage_status": "metadata_requirement_coverage_ready"
                if requirement_ids
                else "needs_metadata_requirement",
                "owner_confirmation_required": True,
                "auto_complete_allowed": False,
            }
        )

    return {
        "coverage_items": coverage_items,
        "coverage_count": len(coverage_items),
        "metadata_coverage_ready_count": sum(
            1 for item in coverage_items if item["coverage_status"] == "metadata_requirement_coverage_ready"
        ),
        "auto_complete_allowed": False,
    }


def _build_safe_export_preview(binders: List[Dict[str, Any]]) -> Dict[str, Any]:
    preview_items = []

    for binder in binders:
        preview_items.append(
            {
                "preview_id": f"VEP-{binder['binder_id'].replace('VEB-', '')}",
                "binder_id": binder["binder_id"],
                "packet_id": binder["packet_id"],
                "binder_type": binder["binder_type"],
                "redacted_preview_available": True,
                "raw_export_available": False,
                "unredacted_export_available": False,
                "external_preview_available": False,
                "public_proof_available": False,
                "section_count": binder["section_count"],
                "safe_preview_fields": [
                    "binder_id",
                    "packet_id",
                    "lane",
                    "section_label",
                    "requirement_id",
                    "version_id",
                    "document_key",
                    "status",
                ],
                "blocked_codes": [
                    "RAW_FILE_BODY_LOCKED",
                    "UNREDACTED_PREVIEW_LOCKED",
                    "EXTERNAL_ACCESS_DENIED",
                    "PUBLIC_PROOF_LOCKED",
                    "NO_RAW_BINDER_EXPORT",
                ],
            }
        )

    return {
        "preview_items": preview_items,
        "preview_count": len(preview_items),
        "redacted_preview_count": len(preview_items),
        "raw_export_count": 0,
        "unredacted_export_count": 0,
        "external_preview_count": 0,
        "public_proof_count": 0,
    }


def _build_blocked_reasons(binders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    active_codes = sorted({code for binder in binders for code in binder["blocked_codes"]})

    return [
        {
            "code": code,
            "label": BINDER_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code or "UPLOAD" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Build metadata binder only. Do not store or display raw body.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct raw upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold metadata binder until provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive binder movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before binder completion.",
        "REDACTION_REVIEW_REQUIRED": "Route through redaction before export preview is treated as ready.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied by default.",
        "UNREDACTED_PREVIEW_LOCKED": "Do not show unredacted preview.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "NO_RAW_BINDER_EXPORT": "Do not allow raw binder export.",
        "NO_AUTO_BINDER_COMPLETE": "Do not auto-complete binder.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_state(
    binders: List[Dict[str, Any]],
    requirement_coverage: Dict[str, Any],
    export_preview: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "review_room": "Vault Evidence Binder Builder",
        "owner_queue_count": len(binders),
        "binder_metadata_ready_count": sum(
            1 for binder in binders if binder["binder_status"] == "BINDER_METADATA_READY"
        ),
        "needs_owner_review_count": len(binders),
        "needs_tower_clearance_count": sum(
            1 for binder in binders if "TOWER_CLEARANCE_REQUIRED" in binder["blocked_codes"]
        ),
        "needs_redaction_review_count": sum(
            1 for binder in binders if "REDACTION_REVIEW_REQUIRED" in binder["blocked_codes"]
        ),
        "metadata_coverage_ready_count": requirement_coverage["metadata_coverage_ready_count"],
        "redacted_preview_count": export_preview["redacted_preview_count"],
        "raw_export_count": export_preview["raw_export_count"],
        "external_preview_count": export_preview["external_preview_count"],
        "safe_to_continue_to_gp017": True,
        "next_owner_actions": [
            "Review metadata evidence binders by lane.",
            "Confirm requirement coverage before workspace-specific packet work.",
            "Use only redacted preview fields for owner review.",
            "Keep raw file bodies, direct upload, external access, public proof, and unredacted exports locked.",
            "Carry ATM binder into GP017 ATM Route Packet Workspace v2.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_evidence_binder_payload())


def get_evidence_binder_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "binder_truth": payload["binder_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "binder_summary": payload["binder_summary"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_evidence_binder_builder() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "evidence_binders": payload["evidence_binders"],
        "binder_count": len(payload["evidence_binders"]),
    }


def get_evidence_binder_packets() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "evidence_binder_packets": payload["evidence_binder_packets"],
    }


def get_evidence_binder_requirements() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "evidence_binder_requirements": payload["evidence_binder_requirements"],
    }


def get_evidence_binder_export_preview() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "evidence_binder_export_preview": payload["evidence_binder_export_preview"],
    }


def get_evidence_binder_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "evidence_binder_blocked_reasons": payload["evidence_binder_blocked_reasons"],
        "blocked_reason_count": len(payload["evidence_binder_blocked_reasons"]),
    }


def get_gp016_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp016_status": payload["gp016_status"],
        "binder_summary": payload["binder_summary"],
        "binder_truth": payload["binder_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "owner_review_state": payload["owner_review_state"],
    }


def render_evidence_binder_page() -> str:
    payload = clone_payload()
    summary = payload["binder_summary"]
    truth = payload["binder_truth"]
    owner = payload["owner_review_state"]
    preview = payload["evidence_binder_export_preview"]

    cards = "\n".join(_render_binder_card(binder) for binder in payload["evidence_binders"])
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    preview_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["binder_id"])}</strong>
            <span>{escape(item["binder_type"])}</span>
          </div>
          <div class="pill ok">Redacted preview only</div>
        </div>
        """
        for item in preview["preview_items"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Evidence Binder Builder · GP016</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 016</div>
        <h1>Evidence Binder Builder</h1>
        <p class="hero-copy">
          GP016 turns metadata version lineage into evidence binders for owner review.
          It prepares packet workspaces without unlocking raw file bodies, direct upload,
          external access, public proof, raw exports, or unredacted previews.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["binder_count"]}</strong>
            <span>evidence binders</span>
          </div>
          <div class="metric">
            <strong>{summary["binder_packet_count"]}</strong>
            <span>packet records</span>
          </div>
          <div class="metric">
            <strong>{summary["requirement_coverage_count"]}</strong>
            <span>coverage records</span>
          </div>
          <div class="metric">
            <strong>{summary["redacted_export_preview_count"]}</strong>
            <span>redacted previews</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Metadata binder ready</span>
          <span class="pill ok">Redacted preview only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Raw body locked</span>
          <span class="pill danger">Public proof locked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Evidence Binders</h2>
      <p>
        Each binder is built from GP015 metadata version lineage. No private file body is read,
        stored, downloaded, copied, or previewed.
      </p>
      <div class="grid">
        {cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Redacted Export Preview Board</h2>
        <p>Only safe preview fields are available. Raw and unredacted exports stay locked.</p>
        <div>
          {preview_rows}
        </div>
      </div>
      <div>
        <h2>Owner Review</h2>
        <p>GP016 prepares the ATM binder for GP017 workspace depth.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP016 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["builder_route"])}</code>
        <code>{escape(summary["packets_route"])}</code>
        <code>{escape(summary["requirements_route"])}</code>
        <code>{escape(summary["export_preview_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp016_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Binder Truth</h2>
      <p>
        Metadata binders:
        <code>{str(truth["binder_metadata_enabled"]).lower()}</code>.
        Raw storage:
        <code>{str(truth["raw_file_body_storage_enabled"]).lower()}</code>.
        Public proof:
        <code>{str(truth["public_proof_enabled"]).lower()}</code>.
        Raw export:
        <code>{str(truth["raw_binder_export_enabled"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_binder_card(binder: Dict[str, Any]) -> str:
    blocked = binder.get("blocked_codes") or []
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
            <div class="title">{escape(binder["binder_type_label"])}</div>
            <div class="meta">
              Binder: <code>{escape(binder["binder_id"])}</code><br>
              Lane: {escape(binder["lane"])}<br>
              Packet: <code>{escape(binder["packet_id"])}</code><br>
              Sections: <code>{escape(str(binder["section_count"]))}</code><br>
              Next workspace: <code>{escape(binder["next_workspace"])}</code>
            </div>
          </div>
          <span class="pill warn">{escape(binder["binder_status_label"])}</span>
        </div>
        <div class="chips">{blocked_chips}</div>
        <div class="action">
          Goal: {escape(binder["owner_goal"])}<br>
          Owner action: {escape(binder["owner_action"])}
        </div>
      </article>
    """
