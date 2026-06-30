"""
VAULT GIANT PACK 021 — Deepened Owner Packet Review

This pack deepens Vault's owner review layer after GP020.

Important truth:
- GP021 is not a storage unlock.
- It does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, public proof, seller/broker/trustee portals,
  financing decisions, legal advice, or Tower-owned permissions.
- It creates a deeper owner packet review board, packet detail records,
  decision desk, blocker matrix, and next-action queue.
- It keeps Vault moving aggressively after the GP020 readiness checkpoint.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, and external access.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.operational_readiness_checkpoint_service import get_operational_readiness_payload


PACK_ID = "VAULT_GP021"
PACK_NAME = "Deepened Owner Packet Review"
SCHEMA_VERSION = "vault.owner_packet_review_depth.v1"

REVIEW_PACKET_BLUEPRINTS = [
    {
        "packet_id": "owner_review_atm_route_acquisition",
        "title": "ATM Route Acquisition Packet",
        "lane": "SimpleeOnTheGo / ATM",
        "source_pack": "VAULT_GP017",
        "source_route": "/vault/atm-route-workspace",
        "priority": "high",
        "next_depth": "seller document gap drilldown",
    },
    {
        "packet_id": "owner_review_apartment_lender",
        "title": "Apartment Lender Packet",
        "lane": "SimpleeProperty / Apartment",
        "source_pack": "VAULT_GP018",
        "source_route": "/vault/apartment-lender-workspace",
        "priority": "high",
        "next_depth": "rent roll T12 NOI DSCR gap drilldown",
    },
    {
        "packet_id": "owner_review_trust_entity_authority",
        "title": "Trust/Entity Authority Packet",
        "lane": "Trust / Entity",
        "source_pack": "VAULT_GP019",
        "source_route": "/vault/trust-entity-workspace",
        "priority": "high",
        "next_depth": "authority and privacy gap drilldown",
    },
    {
        "packet_id": "owner_review_ob_manual_live_private_proof",
        "title": "OB Manual Live Private Proof Packet",
        "lane": "The Observatory / Manual Live",
        "source_pack": "VAULT_GP016",
        "source_route": "/vault/evidence-binder",
        "priority": "medium",
        "next_depth": "private proof packet review",
    },
    {
        "packet_id": "owner_review_soulaana_artist_ip",
        "title": "Soulaana Artist/IP Packet",
        "lane": "Soulaana / IP",
        "source_pack": "VAULT_GP016",
        "source_route": "/vault/evidence-binder",
        "priority": "medium",
        "next_depth": "reserved art and IP proof review",
    },
    {
        "packet_id": "owner_review_private_beta_onboarding",
        "title": "Private Beta Onboarding Packet",
        "lane": "Private Beta",
        "source_pack": "VAULT_GP016",
        "source_route": "/vault/evidence-binder",
        "priority": "medium",
        "next_depth": "beta access onboarding packet review",
    },
]

REVIEW_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body storage remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "EXTERNAL_ACCESS_DENIED": "External access is denied by default.",
    "UNREDACTED_EXPORT_LOCKED": "Unredacted export remains locked.",
    "RAW_EXPORT_LOCKED": "Raw export remains locked.",
    "PUBLIC_PROOF_LOCKED": "Public proof remains locked.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before packet actions apply.",
    "PORTAL_ACCESS_LOCKED": "Seller, broker, trustee, and external portals remain locked.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_RAW_VERIFICATION_CLAIM": "Vault does not claim raw document verification in this layer.",
    "NO_AUTO_PACKET_APPROVAL": "Auto packet approval is disabled.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

REVIEW_SECTIONS = [
    {
        "section_id": "packet_identity",
        "label": "Packet identity",
        "summary_safe": True,
        "tower_owned": False,
    },
    {
        "section_id": "requirement_gap_review",
        "label": "Requirement gap review",
        "summary_safe": True,
        "tower_owned": False,
    },
    {
        "section_id": "blocked_boundary_review",
        "label": "Blocked boundary review",
        "summary_safe": True,
        "tower_owned": True,
    },
    {
        "section_id": "owner_next_action_review",
        "label": "Owner next action review",
        "summary_safe": True,
        "tower_owned": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_owner_packet_review_payload() -> Dict[str, Any]:
    gp020 = get_operational_readiness_payload()

    review_packets = [_build_review_packet(item, gp020) for item in REVIEW_PACKET_BLUEPRINTS]
    review_detail_records = [_build_review_detail(packet) for packet in review_packets]
    decision_desk = _build_decision_desk(review_packets)
    blocker_matrix = _build_blocker_matrix(review_packets)
    owner_queue = _build_owner_queue(review_packets, decision_desk, blocker_matrix)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "deepened_owner_packet_review",
        },
        "review_truth": {
            "owner_packet_review_enabled": True,
            "metadata_only": True,
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
            "clouds_status": "parked_do_not_continue_from_vault_gp021",
            "safe_next_unlock": "GP022 can deepen packet detail/gap workflows without unlocking raw storage or external sharing.",
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
        "review_summary": {
            "room_title": "Vault Owner Packet Review",
            "route": "/vault/owner-packet-review",
            "json_route": "/vault/owner-packet-review.json",
            "board_route": "/vault/owner-packet-review-board.json",
            "detail_route": "/vault/owner-packet-review-detail.json",
            "decision_desk_route": "/vault/owner-packet-review-decision-desk.json",
            "blockers_route": "/vault/owner-packet-review-blockers.json",
            "owner_queue_route": "/vault/owner-packet-review-owner-queue.json",
            "gp021_status_route": "/vault/gp021-status.json",
            "review_packet_count": len(review_packets),
            "detail_record_count": len(review_detail_records),
            "decision_count": decision_desk["decision_count"],
            "blocker_count": blocker_matrix["blocker_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "review_board": {
            "review_packets": review_packets,
            "review_packet_count": len(review_packets),
            "high_priority_count": sum(1 for packet in review_packets if packet["priority"] == "high"),
            "medium_priority_count": sum(1 for packet in review_packets if packet["priority"] == "medium"),
            "ready_for_owner_review_count": sum(1 for packet in review_packets if packet["review_status"] == "READY_FOR_OWNER_REVIEW"),
            "clouds_status": "parked_do_not_continue_from_vault_gp021",
        },
        "review_detail_records": review_detail_records,
        "decision_desk": decision_desk,
        "blocker_matrix": blocker_matrix,
        "owner_review_state": owner_queue,
        "gp020_checkpoint_connection": {
            "gp020_pack_id": gp020["pack"]["id"],
            "gp020_ready": gp020["gp020_status"]["ready"],
            "gp020_safe_to_continue": gp020["gp020_status"]["safe_to_continue_to_gp021"],
            "gp020_vault_done": gp020["gp020_status"]["vault_done"],
            "gp020_readiness_score": gp020["readiness_score"]["score"],
        },
        "gp021_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp020_checkpoint_connected": True,
            "owner_packet_review_depth_ready": True,
            "safe_to_continue_to_gp022": True,
            "vault_done": False,
            "metadata_only_review": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "external_access_still_locked": True,
            "unredacted_export_still_locked": True,
            "raw_export_still_locked": True,
            "public_proof_still_locked": True,
            "portal_access_still_locked": True,
            "financing_decision_not_claimed": True,
            "legal_advice_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp021",
            "next_pack": "VAULT_GP022_PACKET_GAP_DETAIL_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _build_review_packet(blueprint: Dict[str, Any], gp020: Dict[str, Any]) -> Dict[str, Any]:
    sections = [
        {
            "section_id": f"{blueprint['packet_id']}__{section['section_id']}",
            "label": section["label"],
            "summary_safe": section["summary_safe"],
            "tower_owned": section["tower_owned"],
            "status": "ready_for_metadata_review",
            "raw_body_available": False,
            "unredacted_preview_allowed": False,
            "owner_confirmed": False,
        }
        for section in REVIEW_SECTIONS
    ]

    blocked_codes = [
        "RAW_FILE_BODY_LOCKED",
        "DIRECT_UPLOAD_LOCKED",
        "PERMANENT_STORAGE_NOT_CONFIGURED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_EXPORT_LOCKED",
        "RAW_EXPORT_LOCKED",
        "PUBLIC_PROOF_LOCKED",
        "OWNER_CONFIRMATION_REQUIRED",
        "PORTAL_ACCESS_LOCKED",
        "NO_AUTO_PACKET_APPROVAL",
        "CLOUDS_PARKED",
    ]

    if blueprint["priority"] == "high":
        blocked_codes.append("TOWER_CLEARANCE_REQUIRED")

    if blueprint["packet_id"] in {
        "owner_review_atm_route_acquisition",
        "owner_review_apartment_lender",
    }:
        blocked_codes.extend(["NO_FINANCING_DECISION", "NO_RAW_VERIFICATION_CLAIM"])

    if blueprint["packet_id"] == "owner_review_trust_entity_authority":
        blocked_codes.extend(["NO_LEGAL_ADVICE", "NO_RAW_VERIFICATION_CLAIM"])

    return {
        "packet_id": blueprint["packet_id"],
        "title": blueprint["title"],
        "lane": blueprint["lane"],
        "source_pack": blueprint["source_pack"],
        "source_route": blueprint["source_route"],
        "priority": blueprint["priority"],
        "review_status": "READY_FOR_OWNER_REVIEW",
        "review_status_label": "Ready for owner review",
        "next_depth": blueprint["next_depth"],
        "sections": sections,
        "section_count": len(sections),
        "blocked_codes": sorted(set(blocked_codes)),
        "blocked_labels": [REVIEW_BLOCK_CODES.get(code, code) for code in sorted(set(blocked_codes))],
        "owner_action": _owner_action_for_packet(blueprint),
        "preview_state": {
            "redacted_owner_preview_available": True,
            "raw_body_available": False,
            "raw_export_allowed": False,
            "unredacted_export_allowed": False,
            "external_share_allowed": False,
            "public_proof_allowed": False,
        },
        "tower_boundary": {
            "tower_guard_required": True,
            "tower_permission_owner": True,
            "vault_permission_owner": False,
            "step_up_required_for_sensitive_action": True,
            "external_access_default": "denied",
        },
        "checkpoint_connection": {
            "gp020_score": gp020["readiness_score"]["score"],
            "gp020_safe_to_continue": gp020["gp020_status"]["safe_to_continue_to_gp021"],
            "vault_done": gp020["gp020_status"]["vault_done"],
        },
    }


def _owner_action_for_packet(blueprint: Dict[str, Any]) -> str:
    actions = {
        "owner_review_atm_route_acquisition": "Review ATM seller document gaps, vault cash placeholders, and lender readiness without claiming financing or raw verification.",
        "owner_review_apartment_lender": "Review apartment rent roll/T12/NOI/DSCR gaps without claiming raw verification or lender submission.",
        "owner_review_trust_entity_authority": "Review trust/entity authority and privacy gaps without legal advice or legal sufficiency claims.",
        "owner_review_ob_manual_live_private_proof": "Review OB Manual Live private proof metadata without public proof exposure.",
        "owner_review_soulaana_artist_ip": "Review Soulaana artist/IP evidence while preserving reserved art and no-AI-character-art boundaries.",
        "owner_review_private_beta_onboarding": "Review private beta onboarding packet metadata while Tower keeps access authority.",
    }
    return actions.get(blueprint["packet_id"], "Review packet metadata and keep restricted actions locked.")


def _build_review_detail(packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "detail_id": f"OPRD-{packet['packet_id'].replace('owner_review_', '').upper()}",
        "packet_id": packet["packet_id"],
        "title": packet["title"],
        "lane": packet["lane"],
        "source_pack": packet["source_pack"],
        "source_route": packet["source_route"],
        "priority": packet["priority"],
        "review_status": packet["review_status"],
        "section_count": packet["section_count"],
        "sections_ready_count": sum(1 for section in packet["sections"] if section["status"] == "ready_for_metadata_review"),
        "blocked_code_count": len(packet["blocked_codes"]),
        "owner_action": packet["owner_action"],
        "metadata_detail_ready": True,
        "raw_body_detail_ready": False,
        "external_detail_ready": False,
        "safe_to_carry_to_gp022": True,
    }


def _build_decision_desk(review_packets: List[Dict[str, Any]]) -> Dict[str, Any]:
    decisions = []

    for packet in review_packets:
        decisions.append(
            {
                "decision_id": f"OPR-DECISION-{packet['packet_id'].replace('owner_review_', '').upper()}",
                "packet_id": packet["packet_id"],
                "title": packet["title"],
                "recommended_decision": "CONTINUE_METADATA_REVIEW",
                "owner_must_confirm": True,
                "tower_must_clear_sensitive_steps": "TOWER_CLEARANCE_REQUIRED" in packet["blocked_codes"],
                "auto_apply_allowed": False,
                "reason_auto_apply_blocked": "Owner packet decisions require review and Tower boundaries remain locked.",
                "safe_next_step": packet["next_depth"],
            }
        )

    return {
        "decisions": decisions,
        "decision_count": len(decisions),
        "owner_confirmation_required": True,
        "auto_apply_allowed": False,
        "financing_decision_allowed": False,
        "legal_decision_allowed": False,
        "external_share_decision_allowed": False,
    }


def _build_blocker_matrix(review_packets: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for packet in review_packets for code in packet["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": REVIEW_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]

    return {
        "blockers": blockers,
        "blocker_count": len(blockers),
        "all_blockers_safe": True,
        "all_restricted_paths_locked": True,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only owner review. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw file work until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before packet action.",
        "PORTAL_ACCESS_LOCKED": "Keep all seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_PACKET_APPROVAL": "Do not auto-approve packets.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP021.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_queue(
    review_packets: List[Dict[str, Any]],
    decision_desk: Dict[str, Any],
    blocker_matrix: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "OPR-ACTION-001",
            "label": "Review high-priority ATM, apartment, and trust/entity packets first.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OPR-ACTION-002",
            "label": "Identify packet gaps without claiming raw document verification.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OPR-ACTION-003",
            "label": "Keep raw storage, direct upload, raw export, and unredacted export locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OPR-ACTION-004",
            "label": "Keep seller/broker/trustee portals and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "OPR-ACTION-005",
            "label": "Continue Vault into GP022 with packet gap detail depth.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Owner Packet Review",
        "actions": actions,
        "action_count": len(actions),
        "review_packet_count": len(review_packets),
        "decision_count": decision_desk["decision_count"],
        "blocker_count": blocker_matrix["blocker_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review high-priority ATM, apartment, and trust/entity packets first.",
            "Use GP021 to identify gap details, not to unlock raw storage.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP022 packet gap detail.",
        ],
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_owner_packet_review_payload())


def get_owner_packet_review_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_truth": payload["review_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "review_summary": payload["review_summary"],
        "gp020_checkpoint_connection": payload["gp020_checkpoint_connection"],
    }


def get_owner_packet_review_board() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_board": payload["review_board"],
    }


def get_owner_packet_review_detail() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "review_detail_records": payload["review_detail_records"],
        "detail_record_count": len(payload["review_detail_records"]),
    }


def get_owner_packet_review_decision_desk() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "decision_desk": payload["decision_desk"],
    }


def get_owner_packet_review_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_matrix": payload["blocker_matrix"],
    }


def get_owner_packet_review_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp021_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp021_status": payload["gp021_status"],
        "review_truth": payload["review_truth"],
        "review_summary": payload["review_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp020_checkpoint_connection": payload["gp020_checkpoint_connection"],
    }


def render_owner_packet_review_page() -> str:
    payload = clone_payload()
    summary = payload["review_summary"]
    truth = payload["review_truth"]
    board = payload["review_board"]
    decision_desk = payload["decision_desk"]
    owner = payload["owner_review_state"]

    packet_cards = "\n".join(_render_packet_card(packet) for packet in board["review_packets"])
    decision_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(item["title"])}</strong>
            <span>{escape(item["recommended_decision"])} · {escape(item["safe_next_step"])}</span>
          </div>
          <div class="pill warn">Owner confirm</div>
        </div>
        """
        for item in decision_desk["decisions"]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Owner Packet Review · GP021</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 021</div>
        <h1>Owner Packet Review</h1>
        <p class="hero-copy">
          GP021 deepens the owner packet review surface after GP020. It helps review ATM, apartment,
          trust/entity, OB proof, Soulaana IP, and beta onboarding packets without unlocking raw storage,
          external access, public proof, unredacted exports, financing decisions, legal advice, or Tower-owned permissions.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["review_packet_count"]}</strong>
            <span>review packets</span>
          </div>
          <div class="metric">
            <strong>{summary["detail_record_count"]}</strong>
            <span>detail records</span>
          </div>
          <div class="metric">
            <strong>{summary["decision_count"]}</strong>
            <span>decisions</span>
          </div>
          <div class="metric">
            <strong>{summary["blocker_count"]}</strong>
            <span>blocked boundaries</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Owner review ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">High priority packets first</span>
          <span class="pill danger">Raw storage locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Packet Review Board</h2>
      <p>
        Review packet gaps and next actions without claiming raw document verification or external readiness.
      </p>
      <div class="grid">
        {packet_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Decision Desk</h2>
        <p>Decisions require owner confirmation and never auto-apply.</p>
        <div>
          {decision_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP021 keeps Vault moving into GP022 packet gap depth.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP021 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["board_route"])}</code>
        <code>{escape(summary["detail_route"])}</code>
        <code>{escape(summary["decision_desk_route"])}</code>
        <code>{escape(summary["blockers_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp021_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Review Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Raw storage:
        <code>{str(truth["raw_file_body_storage_enabled"]).lower()}</code>.
        External access:
        <code>{str(truth["external_access_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_packet_card(packet: Dict[str, Any]) -> str:
    priority_class = "warn" if packet["priority"] == "high" else "ok"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(packet["title"])}</div>
            <div class="meta">
              Packet: <code>{escape(packet["packet_id"])}</code><br>
              Lane: {escape(packet["lane"])}<br>
              Source: <code>{escape(packet["source_pack"])}</code><br>
              Next depth: {escape(packet["next_depth"])}
            </div>
          </div>
          <span class="pill {priority_class}">{escape(packet["priority"])}</span>
        </div>
      </article>
    """
