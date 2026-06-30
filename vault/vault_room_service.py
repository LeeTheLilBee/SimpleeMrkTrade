"""Vault Giant Pack 002 room service.

This layer turns Archive Vault from a foundation/status layer into a usable
owner room with a packet board, document drawer, action queue, readiness panels,
blocked reasons, redacted view chips, and Clouds preview.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_readiness import get_readiness_score
from .vault_registry import PACKET_TEMPLATES, SAMPLE_DOCUMENT_RECORDS, SAMPLE_RECEIPTS
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard


PACKET_OWNER_NEXT_ACTIONS: Dict[str, str] = {
    "atm": "Use this packet when first two ATM route targets are evaluated.",
    "property": "Use this packet during parallel 4-5 building apartment search.",
    "trust": "Index trust/entity documents after Tower storage clearance is approved.",
    "observatory": "Link OB Manual Live Level 1 proof receipts when owner-reviewed live records begin.",
    "soulaana": "Attach artist package records, reserved art slot manifest, IP terms, and payment receipts.",
    "beta": "Use this packet for private beta invites, NDA, Tower clearance, and access scope.",
}


def _packet_status_for_lane(lane: str) -> Dict[str, Any]:
    """Return setup status for a packet lane.

    This is not pretending files are uploaded. GP002 says the packet framework is
    ready, direct upload is locked, and owner actions are ready.
    """

    if lane in {"atm", "property"}:
        urgency = "high"
        setup_status = "ready_for_target"
    elif lane in {"observatory", "trust"}:
        urgency = "high"
        setup_status = "ready_for_private_receipts"
    else:
        urgency = "medium"
        setup_status = "ready_for_indexing"

    return {
        "urgency": urgency,
        "setup_status": setup_status,
        "direct_upload_allowed": False,
        "redacted_view_default": True,
        "tower_guard_required": True,
    }


def get_packet_board_payload() -> Dict[str, Any]:
    cards: List[Dict[str, Any]] = []

    for index, template in enumerate(PACKET_TEMPLATES, start=1):
        lane_status = _packet_status_for_lane(template.business_lane)
        cards.append(
            {
                "board_position": index,
                "packet_id": template.packet_id,
                "packet_name": template.packet_name,
                "business_lane": template.business_lane,
                "owning_app": template.owning_app,
                "purpose": template.purpose,
                "status": template.status,
                "setup_status": lane_status["setup_status"],
                "urgency": lane_status["urgency"],
                "required_document_count": len(template.required_document_types),
                "required_receipt_count": len(template.required_receipt_types),
                "approval_chain": template.approval_chain,
                "readiness_weight": template.readiness_weight,
                "redaction_profile": template.redaction_profile,
                "direct_upload_allowed": lane_status["direct_upload_allowed"],
                "redacted_view_default": lane_status["redacted_view_default"],
                "tower_guard_required": lane_status["tower_guard_required"],
                "owner_next_action": PACKET_OWNER_NEXT_ACTIONS.get(
                    template.business_lane,
                    "Review packet requirements and attach approved records after Tower clearance.",
                ),
                "open_app_target": {
                    "label": "Open Vault Packet",
                    "route": f"/vault/packet-templates.json#{template.packet_id}",
                    "action_type": "vault_packet_review",
                },
            }
        )

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_packet_board",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "board_label": "Vault Packet Board",
        "summary": "Aggressive packet board for ATM, apartment, trust, OB proof, Soulaana, and beta records.",
        "card_count": len(cards),
        "cards": cards,
        "board_filters": [
            "all",
            "atm",
            "property",
            "trust",
            "observatory",
            "soulaana",
            "beta",
            "ready_for_target",
            "ready_for_private_receipts",
            "ready_for_indexing",
        ],
    }
    return attach_tower_guard(payload, "/vault/packet-board.json")


def _receipt_lookup() -> Dict[str, Dict[str, Any]]:
    return {receipt.receipt_id: receipt.to_dict() for receipt in SAMPLE_RECEIPTS}


def get_document_drawer_payload() -> Dict[str, Any]:
    receipt_map = _receipt_lookup()
    drawer_records: List[Dict[str, Any]] = []

    for record in SAMPLE_DOCUMENT_RECORDS:
        record_dict = record.to_dict()
        linked_receipts = [
            receipt_map[receipt_id]
            for receipt_id in record.linked_receipt_ids
            if receipt_id in receipt_map
        ]

        drawer_records.append(
            {
                **record_dict,
                "drawer_tabs": [
                    "Overview",
                    "Requirements",
                    "Receipts",
                    "Redaction",
                    "Freshness",
                    "Owner Next Action",
                ],
                "linked_receipts": linked_receipts,
                "drawer_status_chips": [
                    "Tower Guarded",
                    "Redacted Default",
                    "Direct Upload Locked",
                    f"Freshness {record.freshness_days}d",
                ],
                "sensitive_fields_hidden": REDACTION_POLICY["sensitive_fields"],
                "clouds_safe_summary": {
                    "title": record.title,
                    "business_lane": record.business_lane,
                    "status": record.status,
                    "summary": record.summary,
                    "next_action": record.next_action,
                },
            }
        )

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_document_drawer",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "drawer_label": "Vault Document Drawer",
        "record_count": len(drawer_records),
        "records": drawer_records,
        "redaction_default": "redacted",
        "direct_upload_allowed": False,
        "storage_provider": "not_connected",
    }
    return attach_tower_guard(payload, "/vault/document-drawer.json")


def get_owner_action_queue_payload() -> Dict[str, Any]:
    actions: List[Dict[str, Any]] = [
        {
            "action_id": "vault_action_storage_clearance",
            "label": "Approve Vault storage provider through Tower",
            "business_lane": "vault",
            "priority": "critical",
            "status": "blocked_until_tower_clearance",
            "owning_authority": "tower",
            "blocked_by": ["upload_provider_not_approved", "direct_upload_locked"],
            "why_it_matters": "Vault can index packets now, but real file uploads must wait for Tower-approved storage, retention, malware scanning, and permission boundaries.",
            "next_step": "Build storage clearance contract later; do not unlock raw uploads inside GP002.",
        },
        {
            "action_id": "vault_action_atm_packet_ready",
            "label": "Prepare first ATM route acquisition packet",
            "business_lane": "atm",
            "priority": "high",
            "status": "ready_for_target",
            "owning_authority": "owner",
            "blocked_by": [],
            "why_it_matters": "The ATM packet is ready for seller summaries, route machine lists, cashflow records, vault cash plan, loan preapproval, and owner review proof.",
            "next_step": "When route targets are chosen, attach approved document records to packet_atm_route_acquisition.",
        },
        {
            "action_id": "vault_action_property_packet_ready",
            "label": "Prepare apartment lender due-diligence packet",
            "business_lane": "property",
            "priority": "high",
            "status": "ready_for_target",
            "owning_authority": "owner",
            "blocked_by": [],
            "why_it_matters": "The apartment packet is ready for 4-5 building search diligence, lender packet preparation, rent roll, T12, inspections, and ownership proof.",
            "next_step": "Use during parallel apartment search while OB Manual Live Phase 1 develops.",
        },
        {
            "action_id": "vault_action_ob_manual_live_proof",
            "label": "Prepare OB Manual Live private proof chain",
            "business_lane": "observatory",
            "priority": "high",
            "status": "ready_for_private_receipts",
            "owning_authority": "owner_and_tower",
            "blocked_by": [],
            "why_it_matters": "OB proof stays private, owner-reviewed, Tower-guarded, and free of broker secrets or auto-execution exposure.",
            "next_step": "Link Manual Live alert receipts, broker checklist receipts, owner review notes, and trade tracking snapshots as they are created.",
        },
        {
            "action_id": "vault_action_trust_entity_index",
            "label": "Index trust/entity ownership records",
            "business_lane": "trust",
            "priority": "high",
            "status": "ready_for_indexing",
            "owning_authority": "owner_and_trustee",
            "blocked_by": ["direct_upload_locked"],
            "why_it_matters": "The trust/entity packet protects ownership, authority, operating agreements, bank summaries, and trustee records.",
            "next_step": "Keep index ready; upload actual files only after storage clearance.",
        },
        {
            "action_id": "vault_action_clouds_preview_ready",
            "label": "Expose Vault summary to The Clouds later",
            "business_lane": "clouds",
            "priority": "medium",
            "status": "clouds_source_ready",
            "owning_authority": "vault_to_clouds_handoff",
            "blocked_by": [],
            "why_it_matters": "The Clouds should see packet readiness, owner focus, blocked reasons, and redacted summaries without seeing sensitive details.",
            "next_step": "Clouds GP001 can read /vault/clouds-source.json and /vault/room.json after Clouds starts.",
        },
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_owner_action_queue",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "queue_label": "Vault Owner Action Queue",
        "action_count": len(actions),
        "actions": actions,
        "critical_count": sum(1 for action in actions if action["priority"] == "critical"),
        "high_count": sum(1 for action in actions if action["priority"] == "high"),
        "ready_count": sum(1 for action in actions if not action["blocked_by"]),
    }
    return attach_tower_guard(payload, "/vault/owner-action-queue.json")


def get_vault_room_payload() -> Dict[str, Any]:
    readiness = get_readiness_score()
    packet_board = get_packet_board_payload()
    document_drawer = get_document_drawer_payload()
    owner_queue = get_owner_action_queue_payload()

    payload = {
        "app_id": "archive_vault",
        "app_name": "Archive Vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_room",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "private_invite_only": True,
        "room_status": "ready",
        "readiness_score": readiness["score"],
        "readiness_label": readiness["label"],
        "room_sections": [
            {
                "section_id": "command_strip",
                "label": "Command Strip",
                "summary": "Readiness, Tower guard, direct upload lock, redacted view, and Clouds source state.",
            },
            {
                "section_id": "packet_board",
                "label": "Packet Board",
                "summary": "Aggressive acquisition/proof packet cards across all current Simplee lanes.",
            },
            {
                "section_id": "document_drawer",
                "label": "Document Drawer",
                "summary": "Private document indexes with linked receipts, freshness, redaction, and next action.",
            },
            {
                "section_id": "owner_action_queue",
                "label": "Owner Action Queue",
                "summary": "What the owner needs to review, prepare, or keep locked.",
            },
            {
                "section_id": "clouds_preview",
                "label": "Clouds Preview",
                "summary": "Summary-only handoff view for future Clouds command dashboard.",
            },
        ],
        "command_chips": [
            {"label": "Tower Guard", "value": "Required", "tone": "locked"},
            {"label": "Direct Upload", "value": "Locked", "tone": "locked"},
            {"label": "Redacted View", "value": "Default", "tone": "ready"},
            {"label": "Clouds Source", "value": "Ready", "tone": "ready"},
            {"label": "Packet Board", "value": str(packet_board["card_count"]), "tone": "ready"},
            {"label": "Owner Queue", "value": str(owner_queue["action_count"]), "tone": "ready"},
        ],
        "packet_board": packet_board,
        "document_drawer": document_drawer,
        "owner_action_queue": owner_queue,
        "clouds_preview": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "readiness_score": readiness["score"],
            "packet_card_count": packet_board["card_count"],
            "document_record_count": document_drawer["record_count"],
            "owner_action_count": owner_queue["action_count"],
            "sensitive_fields_hidden": REDACTION_POLICY["sensitive_fields"],
            "blocked_reasons": NO_DIRECT_UPLOAD_POLICY["blocked_now"],
        },
        "next_pack_recommendation": "Vault Giant Pack 003 should build ATM acquisition packet builder and apartment lender packet builder.",
    }
    return attach_tower_guard(payload, "/vault/room.json")


def get_vault_gp002_status_payload() -> Dict[str, Any]:
    room = get_vault_room_payload()
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp002_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 002",
        "built": [
            "real_vault_room_payload",
            "packet_board",
            "document_drawer",
            "owner_action_queue",
            "redacted_clouds_preview",
            "upgraded_vault_template",
            "vault_room_javascript",
            "dark_glass_css_refresh",
        ],
        "readiness_score": room["readiness_score"],
        "room_section_count": len(room["room_sections"]),
        "packet_card_count": room["packet_board"]["card_count"],
        "document_record_count": room["document_drawer"]["record_count"],
        "owner_action_count": room["owner_action_queue"]["action_count"],
        "safe_to_continue_to_gp003": True,
    }
    return attach_tower_guard(payload, "/vault/gp002-status.json")
