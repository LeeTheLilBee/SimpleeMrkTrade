"""
VAULT GIANT PACK 022 — Packet Gap Detail

This pack deepens GP021 owner packet review into packet-by-packet gap detail.

Important truth:
- GP022 is not a storage unlock.
- It does not unlock raw file body storage, direct upload, external sharing,
  unredacted export, raw export, public proof, seller/broker/trustee portals,
  financing decisions, legal advice, or Tower-owned permissions.
- It creates gap records, requirement gap drilldowns, blocker detail, and owner next-action detail.
- It keeps Vault moving aggressively after GP021.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  sensitive visibility, portals, and external access.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.owner_packet_review_depth_service import get_owner_packet_review_payload


PACK_ID = "VAULT_GP022"
PACK_NAME = "Packet Gap Detail"
SCHEMA_VERSION = "vault.packet_gap_detail.v1"

GAP_TYPES = {
    "missing_metadata_detail": "Missing metadata detail",
    "raw_document_support_locked": "Raw document support locked",
    "tower_clearance_required": "Tower clearance required",
    "owner_confirmation_required": "Owner confirmation required",
    "external_share_locked": "External share locked",
    "verification_claim_blocked": "Verification claim blocked",
}

GAP_BLOCK_CODES = {
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
    "NO_AUTO_GAP_CLOSE": "Auto gap close is disabled.",
    "CLOUDS_PARKED": "Clouds remains parked.",
}

BASE_GAP_BLUEPRINTS = [
    {
        "gap_type": "raw_document_support_locked",
        "label": "Raw document support is locked",
        "severity": "locked",
        "tower_owned": True,
    },
    {
        "gap_type": "owner_confirmation_required",
        "label": "Owner confirmation required",
        "severity": "review",
        "tower_owned": False,
    },
    {
        "gap_type": "external_share_locked",
        "label": "External sharing is locked",
        "severity": "locked",
        "tower_owned": True,
    },
]

PACKET_SPECIFIC_GAPS = {
    "owner_review_atm_route_acquisition": [
        {
            "gap_type": "missing_metadata_detail",
            "label": "Seller machine list / route economics detail needs owner drilldown",
            "severity": "review",
            "tower_owned": False,
        },
        {
            "gap_type": "verification_claim_blocked",
            "label": "Seller financial verification claim blocked until raw support exists",
            "severity": "blocked",
            "tower_owned": False,
        },
    ],
    "owner_review_apartment_lender": [
        {
            "gap_type": "missing_metadata_detail",
            "label": "Rent roll / T12 / NOI / DSCR detail needs owner drilldown",
            "severity": "review",
            "tower_owned": False,
        },
        {
            "gap_type": "verification_claim_blocked",
            "label": "Rent roll and T12 verification claim blocked until raw support exists",
            "severity": "blocked",
            "tower_owned": False,
        },
    ],
    "owner_review_trust_entity_authority": [
        {
            "gap_type": "missing_metadata_detail",
            "label": "Trust/entity authority detail needs owner drilldown",
            "severity": "review",
            "tower_owned": False,
        },
        {
            "gap_type": "verification_claim_blocked",
            "label": "Legal sufficiency and authority verification claims blocked",
            "severity": "blocked",
            "tower_owned": False,
        },
    ],
    "owner_review_ob_manual_live_private_proof": [
        {
            "gap_type": "missing_metadata_detail",
            "label": "Private proof packet detail needs owner drilldown",
            "severity": "review",
            "tower_owned": False,
        },
    ],
    "owner_review_soulaana_artist_ip": [
        {
            "gap_type": "missing_metadata_detail",
            "label": "Artist/IP proof detail needs owner drilldown",
            "severity": "review",
            "tower_owned": False,
        },
    ],
    "owner_review_private_beta_onboarding": [
        {
            "gap_type": "missing_metadata_detail",
            "label": "Private beta access/onboarding detail needs owner drilldown",
            "severity": "review",
            "tower_owned": False,
        },
    ],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_packet_gap_detail_payload() -> Dict[str, Any]:
    gp021 = get_owner_packet_review_payload()
    review_packets = gp021["review_board"]["review_packets"]

    gap_records = [_build_gap_record(packet, gap) for packet in review_packets for gap in _gaps_for_packet(packet)]
    requirement_drilldowns = [_build_requirement_drilldown(packet, gap_records) for packet in review_packets]
    blocker_detail = _build_blocker_detail(gap_records)
    owner_queue = _build_owner_queue(review_packets, gap_records, blocker_detail)
    gap_board = _build_gap_board(review_packets, gap_records, requirement_drilldowns)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "packet_gap_detail",
        },
        "gap_truth": {
            "packet_gap_detail_enabled": True,
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
            "auto_gap_close_enabled": False,
            "clouds_should_continue": False,
            "clouds_status": "parked_do_not_continue_from_vault_gp022",
            "safe_next_unlock": "GP023 can deepen packet action planning without unlocking raw storage or external sharing.",
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
        "gap_summary": {
            "room_title": "Vault Packet Gap Detail",
            "route": "/vault/packet-gap-detail",
            "json_route": "/vault/packet-gap-detail.json",
            "board_route": "/vault/packet-gap-detail-board.json",
            "records_route": "/vault/packet-gap-detail-records.json",
            "requirements_route": "/vault/packet-gap-detail-requirements.json",
            "blockers_route": "/vault/packet-gap-detail-blockers.json",
            "owner_queue_route": "/vault/packet-gap-detail-owner-queue.json",
            "gp022_status_route": "/vault/gp022-status.json",
            "review_packet_count": len(review_packets),
            "gap_record_count": len(gap_records),
            "requirement_drilldown_count": len(requirement_drilldowns),
            "blocker_count": blocker_detail["blocker_count"],
            "owner_action_count": owner_queue["action_count"],
            "metadata_only": True,
        },
        "gap_board": gap_board,
        "gap_records": gap_records,
        "requirement_drilldowns": requirement_drilldowns,
        "blocker_detail": blocker_detail,
        "owner_review_state": owner_queue,
        "gp021_connection": {
            "gp021_pack_id": gp021["pack"]["id"],
            "gp021_ready": gp021["gp021_status"]["ready"],
            "gp021_safe_to_continue": gp021["gp021_status"]["safe_to_continue_to_gp022"],
            "gp021_vault_done": gp021["gp021_status"]["vault_done"],
            "gp021_packet_count": gp021["review_board"]["review_packet_count"],
        },
        "gp022_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "gp021_owner_packet_review_connected": True,
            "packet_gap_detail_ready": True,
            "safe_to_continue_to_gp023": True,
            "vault_done": False,
            "metadata_only_gap_detail": True,
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
            "auto_gap_close_disabled": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp022",
            "next_pack": "VAULT_GP023_PACKET_ACTION_PLAN_OR_NEXT_VAULT_PRODUCT_DEPTH",
        },
    }

    return payload


def _gaps_for_packet(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    gaps = list(BASE_GAP_BLUEPRINTS)
    gaps.extend(PACKET_SPECIFIC_GAPS.get(packet["packet_id"], []))

    if "TOWER_CLEARANCE_REQUIRED" in packet.get("blocked_codes", []):
        gaps.append(
            {
                "gap_type": "tower_clearance_required",
                "label": "Tower clearance required before sensitive action",
                "severity": "locked",
                "tower_owned": True,
            }
        )

    return gaps


def _build_gap_record(packet: Dict[str, Any], gap: Dict[str, Any]) -> Dict[str, Any]:
    gap_id = f"VGD-{packet['packet_id'].replace('owner_review_', '').upper()}-{gap['gap_type'].upper()}"

    blocked_codes = [
        "RAW_FILE_BODY_LOCKED",
        "DIRECT_UPLOAD_LOCKED",
        "EXTERNAL_ACCESS_DENIED",
        "UNREDACTED_EXPORT_LOCKED",
        "RAW_EXPORT_LOCKED",
        "OWNER_CONFIRMATION_REQUIRED",
        "NO_AUTO_GAP_CLOSE",
        "CLOUDS_PARKED",
    ]

    if gap["tower_owned"] or gap["gap_type"] in {"tower_clearance_required", "external_share_locked"}:
        blocked_codes.append("TOWER_CLEARANCE_REQUIRED")

    if gap["gap_type"] == "raw_document_support_locked":
        blocked_codes.extend(["PERMANENT_STORAGE_NOT_CONFIGURED", "NO_RAW_VERIFICATION_CLAIM"])

    if gap["gap_type"] == "external_share_locked":
        blocked_codes.extend(["PORTAL_ACCESS_LOCKED", "PUBLIC_PROOF_LOCKED"])

    if gap["gap_type"] == "verification_claim_blocked":
        blocked_codes.append("NO_RAW_VERIFICATION_CLAIM")

    if packet["packet_id"] in {"owner_review_atm_route_acquisition", "owner_review_apartment_lender"}:
        blocked_codes.append("NO_FINANCING_DECISION")

    if packet["packet_id"] == "owner_review_trust_entity_authority":
        blocked_codes.append("NO_LEGAL_ADVICE")

    return {
        "gap_id": gap_id,
        "packet_id": packet["packet_id"],
        "packet_title": packet["title"],
        "lane": packet["lane"],
        "priority": packet["priority"],
        "gap_type": gap["gap_type"],
        "gap_type_label": GAP_TYPES.get(gap["gap_type"], gap["gap_type"]),
        "label": gap["label"],
        "severity": gap["severity"],
        "tower_owned": gap["tower_owned"],
        "review_status": "OPEN_FOR_OWNER_REVIEW",
        "metadata_detail_ready": True,
        "raw_body_required_to_close": gap["gap_type"] in {"raw_document_support_locked", "verification_claim_blocked"},
        "raw_body_available": False,
        "external_share_allowed": False,
        "owner_confirmed": False,
        "auto_close_allowed": False,
        "blocked_codes": sorted(set(blocked_codes)),
        "blocked_labels": [GAP_BLOCK_CODES.get(code, code) for code in sorted(set(blocked_codes))],
        "owner_action": _owner_action_for_gap(packet, gap),
    }


def _owner_action_for_gap(packet: Dict[str, Any], gap: Dict[str, Any]) -> str:
    if gap["gap_type"] == "missing_metadata_detail":
        return f"Review missing metadata detail for {packet['title']} and decide what detail to drill down next."
    if gap["gap_type"] == "raw_document_support_locked":
        return "Keep raw support marked locked until provider/Tower path exists."
    if gap["gap_type"] == "tower_clearance_required":
        return "Wait for Tower clearance before sensitive packet movement."
    if gap["gap_type"] == "owner_confirmation_required":
        return "Owner must confirm the next review action before applying changes."
    if gap["gap_type"] == "external_share_locked":
        return "Keep external sharing locked; use redacted owner preview only."
    if gap["gap_type"] == "verification_claim_blocked":
        return "Do not claim raw verification; keep as metadata review only."
    return "Review gap safely without unlocking restricted paths."


def _build_requirement_drilldown(packet: Dict[str, Any], gap_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    related_gaps = [gap for gap in gap_records if gap["packet_id"] == packet["packet_id"]]
    open_count = sum(1 for gap in related_gaps if gap["review_status"] == "OPEN_FOR_OWNER_REVIEW")
    locked_count = sum(1 for gap in related_gaps if gap["severity"] == "locked")
    blocked_count = sum(1 for gap in related_gaps if gap["severity"] == "blocked")

    return {
        "drilldown_id": f"VDR-{packet['packet_id'].replace('owner_review_', '').upper()}",
        "packet_id": packet["packet_id"],
        "title": packet["title"],
        "lane": packet["lane"],
        "priority": packet["priority"],
        "source_route": packet["source_route"],
        "source_pack": packet["source_pack"],
        "gap_ids": [gap["gap_id"] for gap in related_gaps],
        "gap_count": len(related_gaps),
        "open_gap_count": open_count,
        "locked_gap_count": locked_count,
        "blocked_gap_count": blocked_count,
        "metadata_drilldown_ready": True,
        "raw_body_drilldown_ready": False,
        "external_drilldown_ready": False,
        "owner_review_required": True,
        "safe_to_carry_to_gp023": True,
    }


def _build_blocker_detail(gap_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    active_codes = sorted({code for gap in gap_records for code in gap["blocked_codes"]})

    blockers = [
        {
            "code": code,
            "label": GAP_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if code in {
                "DIRECT_UPLOAD_LOCKED",
                "EXTERNAL_ACCESS_DENIED",
                "UNREDACTED_EXPORT_LOCKED",
                "RAW_EXPORT_LOCKED",
                "TOWER_CLEARANCE_REQUIRED",
                "PORTAL_ACCESS_LOCKED",
            } else "Vault",
            "safe_to_override_inside_vault": False,
            "affected_gap_count": sum(1 for gap in gap_records if code in gap["blocked_codes"]),
            "vault_response": _vault_response_for_block(code),
        }
        for code in active_codes
    ]

    return {
        "blockers": blockers,
        "blocker_count": len(blockers),
        "all_blockers_safe": True,
        "all_restricted_paths_locked": True,
        "auto_override_allowed": False,
    }


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only gap review. Do not display raw bodies.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw support until provider exists.",
        "EXTERNAL_ACCESS_DENIED": "Keep external access denied.",
        "UNREDACTED_EXPORT_LOCKED": "Do not allow unredacted export.",
        "RAW_EXPORT_LOCKED": "Do not allow raw export.",
        "PUBLIC_PROOF_LOCKED": "Do not create public proof.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before gap action.",
        "PORTAL_ACCESS_LOCKED": "Keep seller/broker/trustee/external portals locked.",
        "NO_FINANCING_DECISION": "Do not make financing decisions.",
        "NO_LEGAL_ADVICE": "Do not provide legal advice.",
        "NO_RAW_VERIFICATION_CLAIM": "Do not claim raw document verification.",
        "NO_AUTO_GAP_CLOSE": "Do not auto-close gaps.",
        "CLOUDS_PARKED": "Do not continue Clouds from Vault GP022.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_owner_queue(
    review_packets: List[Dict[str, Any]],
    gap_records: List[Dict[str, Any]],
    blocker_detail: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "PGD-ACTION-001",
            "label": "Open high-priority packet gap details first.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PGD-ACTION-002",
            "label": "Separate metadata gaps from raw-document support gaps.",
            "status": "ready_for_owner_review",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PGD-ACTION-003",
            "label": "Keep direct upload, raw export, unredacted export, and external sharing locked.",
            "status": "boundary_locked",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PGD-ACTION-004",
            "label": "Do not claim financing, legal, or raw verification completion.",
            "status": "truth_boundary_locked",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "PGD-ACTION-005",
            "label": "Continue Vault into GP023 with packet action planning.",
            "status": "next_build_ready",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Packet Gap Detail",
        "actions": actions,
        "action_count": len(actions),
        "review_packet_count": len(review_packets),
        "gap_record_count": len(gap_records),
        "blocker_count": blocker_detail["blocker_count"],
        "owner_review_needed_count": sum(1 for action in actions if action["status"] in {"ready_for_owner_review", "next_build_ready"}),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review high-priority packet gaps first.",
            "Separate metadata gaps from raw-document support gaps.",
            "Keep Tower-owned permissions and external sharing locked.",
            "Do not switch to Clouds from this checkpoint.",
            "Continue Vault into GP023 packet action planning.",
        ],
    }


def _build_gap_board(
    review_packets: List[Dict[str, Any]],
    gap_records: List[Dict[str, Any]],
    requirement_drilldowns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "review_packets": review_packets,
        "gap_records": gap_records,
        "requirement_drilldowns": requirement_drilldowns,
        "review_packet_count": len(review_packets),
        "gap_record_count": len(gap_records),
        "high_priority_gap_count": sum(1 for gap in gap_records if gap["priority"] == "high"),
        "locked_gap_count": sum(1 for gap in gap_records if gap["severity"] == "locked"),
        "blocked_gap_count": sum(1 for gap in gap_records if gap["severity"] == "blocked"),
        "metadata_detail_ready_count": sum(1 for gap in gap_records if gap["metadata_detail_ready"]),
        "raw_body_available_count": 0,
        "external_share_allowed_count": 0,
        "clouds_status": "parked_do_not_continue_from_vault_gp022",
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_packet_gap_detail_payload())


def get_packet_gap_detail_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gap_truth": payload["gap_truth"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gap_summary": payload["gap_summary"],
        "gp021_connection": payload["gp021_connection"],
    }


def get_packet_gap_detail_board() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gap_board": payload["gap_board"],
    }


def get_packet_gap_detail_records() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gap_records": payload["gap_records"],
        "gap_record_count": len(payload["gap_records"]),
    }


def get_packet_gap_detail_requirements() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "requirement_drilldowns": payload["requirement_drilldowns"],
        "requirement_drilldown_count": len(payload["requirement_drilldowns"]),
    }


def get_packet_gap_detail_blockers() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "blocker_detail": payload["blocker_detail"],
    }


def get_packet_gap_detail_owner_queue() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "owner_review_state": payload["owner_review_state"],
    }


def get_gp022_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp022_status": payload["gp022_status"],
        "gap_truth": payload["gap_truth"],
        "gap_summary": payload["gap_summary"],
        "tower_authority": payload["tower_authority"],
        "vault_boundary": payload["vault_boundary"],
        "gp021_connection": payload["gp021_connection"],
    }


def render_packet_gap_detail_page() -> str:
    payload = clone_payload()
    summary = payload["gap_summary"]
    truth = payload["gap_truth"]
    board = payload["gap_board"]
    owner = payload["owner_review_state"]

    packet_cards = "\n".join(_render_packet_gap_card(packet, board["gap_records"]) for packet in board["review_packets"])
    gap_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(gap["packet_title"])}</strong>
            <span>{escape(gap["gap_type_label"])} · {escape(gap["label"])}</span>
          </div>
          <div class="pill {'danger' if gap["severity"] in {"blocked", "locked"} else 'warn'}">{escape(gap["severity"])}</div>
        </div>
        """
        for gap in board["gap_records"][:12]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Packet Gap Detail · GP022</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 022</div>
        <h1>Packet Gap Detail</h1>
        <p class="hero-copy">
          GP022 turns owner packet review into packet-by-packet gap detail. It shows what is missing,
          what is blocked, what needs owner review, and what stays Tower-locked without unlocking raw storage,
          external access, public proof, unredacted exports, financing decisions, legal advice, or raw verification claims.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["review_packet_count"]}</strong>
            <span>review packets</span>
          </div>
          <div class="metric">
            <strong>{summary["gap_record_count"]}</strong>
            <span>gap records</span>
          </div>
          <div class="metric">
            <strong>{summary["requirement_drilldown_count"]}</strong>
            <span>drilldowns</span>
          </div>
          <div class="metric">
            <strong>{summary["blocker_count"]}</strong>
            <span>blockers</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Gap detail ready</span>
          <span class="pill ok">Metadata only</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Raw support locked</span>
          <span class="pill danger">Clouds parked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Packet Gap Board</h2>
      <p>
        Gap records separate metadata gaps from raw-support gaps and Tower-owned blockers.
      </p>
      <div class="grid">
        {packet_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Open Gap Detail</h2>
        <p>These are review-safe gap records. No raw bodies or external shares are unlocked.</p>
        <div>
          {gap_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP022 prepares GP023 packet action planning.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP022 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["board_route"])}</code>
        <code>{escape(summary["records_route"])}</code>
        <code>{escape(summary["requirements_route"])}</code>
        <code>{escape(summary["blockers_route"])}</code>
        <code>{escape(summary["owner_queue_route"])}</code>
        <code>{escape(summary["gp022_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Gap Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Raw storage:
        <code>{str(truth["raw_file_body_storage_enabled"]).lower()}</code>.
        Auto gap close:
        <code>{str(truth["auto_gap_close_enabled"]).lower()}</code>.
        Clouds should continue:
        <code>{str(truth["clouds_should_continue"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_packet_gap_card(packet: Dict[str, Any], gap_records: List[Dict[str, Any]]) -> str:
    related = [gap for gap in gap_records if gap["packet_id"] == packet["packet_id"]]
    locked = sum(1 for gap in related if gap["severity"] == "locked")
    blocked = sum(1 for gap in related if gap["severity"] == "blocked")
    priority_class = "warn" if packet["priority"] == "high" else "ok"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(packet["title"])}</div>
            <div class="meta">
              Packet: <code>{escape(packet["packet_id"])}</code><br>
              Lane: {escape(packet["lane"])}<br>
              Gaps: <code>{len(related)}</code><br>
              Locked: <code>{locked}</code> · Blocked: <code>{blocked}</code>
            </div>
          </div>
          <span class="pill {priority_class}">{escape(packet["priority"])}</span>
        </div>
      </article>
    """
