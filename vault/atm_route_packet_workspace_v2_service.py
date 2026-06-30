"""
VAULT GIANT PACK 017 — ATM Route Packet Workspace v2

This pack turns the GP016 ATM evidence binder into a real ATM route packet workspace.

Important truth:
- This is an owner review and due diligence workspace for ATM route acquisition.
- It is metadata-only in GP017.
- It does not unlock raw file body storage, direct upload, seller portal access,
  lender sharing, unredacted export, or external access.
- It does not make financing decisions.
- It does not claim seller financials are verified by raw statements.
- It prepares the road for GP018 Apartment Lender Packet Workspace v2.
- Tower owns identity, permissions, clearance, step-up, export locks, freeze/revoke,
  and external access authority.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from html import escape
from typing import Any, Dict, List

from vault.evidence_binder_builder_service import get_evidence_binder_payload


PACK_ID = "VAULT_GP017"
PACK_NAME = "ATM Route Packet Workspace v2"
SCHEMA_VERSION = "vault.atm_route_packet_workspace.v2"

WORKSPACE_STATUSES = {
    "ATM_WORKSPACE_METADATA_READY": "ATM workspace metadata ready",
    "NEEDS_OWNER_REVIEW": "Needs owner review",
    "NEEDS_SELLER_PACKET": "Needs seller packet",
    "NEEDS_FINANCIAL_REVIEW": "Needs financial review",
    "NEEDS_TOWER_CLEARANCE": "Needs Tower clearance",
    "BLOCKED_STORAGE_PROVIDER": "Blocked by storage provider",
    "HELD_METADATA_ONLY": "Held metadata only",
}

ATM_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before packet completion.",
    "SELLER_PORTAL_LOCKED": "Seller portal access is locked.",
    "EXTERNAL_LENDER_SHARE_LOCKED": "External lender sharing is locked.",
    "UNREDACTED_PREVIEW_LOCKED": "Unredacted preview is locked.",
    "RAW_EXPORT_LOCKED": "Raw export is locked.",
    "NO_AUTO_ACQUISITION_APPROVAL": "Auto acquisition approval is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_SELLER_FINANCIAL_VERIFICATION_CLAIM": "Seller financials are not verified from raw statements in GP017.",
}

ATM_PACKET_REQUIREMENTS = [
    {
        "requirement_id": "atm_route_seller_financials",
        "label": "Seller financials",
        "required": True,
        "source": "GP016 metadata section",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "atm_route_machine_list",
        "label": "Machine list and locations",
        "required": True,
        "source": "seller packet metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "atm_route_cash_load_history",
        "label": "Cash load / vault cash history",
        "required": True,
        "source": "seller packet metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "atm_route_processor_statements",
        "label": "Processor statements",
        "required": True,
        "source": "seller packet metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "atm_route_service_contracts",
        "label": "Service contracts / site agreements",
        "required": True,
        "source": "seller packet metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "atm_route_bank_lender_packet",
        "label": "Bank/lender acquisition packet",
        "required": True,
        "source": "Vault generated metadata packet",
        "raw_body_required_later": False,
    },
]

DUE_DILIGENCE_LANES = [
    {
        "lane_id": "atm_dd_seller_identity",
        "label": "Seller / entity identity",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "atm_dd_route_quality",
        "label": "Route quality and machine count",
        "owner": "Vault",
        "tower_clearance_required": False,
    },
    {
        "lane_id": "atm_dd_cash_flow",
        "label": "Cash flow and surcharge review",
        "owner": "Vault",
        "tower_clearance_required": False,
    },
    {
        "lane_id": "atm_dd_vault_cash",
        "label": "Vault cash requirement",
        "owner": "Vault",
        "tower_clearance_required": False,
    },
    {
        "lane_id": "atm_dd_bank_packet",
        "label": "Bank/lender packet readiness",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "atm_dd_risk_flags",
        "label": "Risk flags and blocked reasons",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_atm_route_workspace_payload() -> Dict[str, Any]:
    gp016 = get_evidence_binder_payload()
    atm_binder = _find_atm_binder(gp016["evidence_binders"])
    atm_packet = _build_atm_packet(atm_binder)
    due_diligence = _build_due_diligence(atm_binder, atm_packet)
    financial_review = _build_financial_review(atm_binder, atm_packet)
    owner_actions = _build_owner_actions(atm_binder, due_diligence, financial_review)
    blocked_reasons = _build_blocked_reasons(atm_binder, due_diligence, financial_review)
    readiness = _build_readiness(atm_packet, due_diligence, financial_review, owner_actions)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "atm_route_packet_workspace_v2",
        },
        "workspace_truth": {
            "workspace_enabled": True,
            "metadata_only": True,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "seller_portal_enabled": False,
            "external_lender_share_enabled": False,
            "raw_export_enabled": False,
            "unredacted_preview_enabled": False,
            "redacted_owner_preview_enabled": True,
            "auto_acquisition_approval_enabled": False,
            "financing_decision_enabled": False,
            "seller_financials_verified_from_raw_statements": False,
            "fake_seller_packet_complete": False,
            "safe_next_unlock": "GP018 Apartment Lender Packet Workspace v2 can use shared lender/due-diligence patterns without unlocking raw storage.",
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "seller_portal_allowed": False,
            "external_lender_share_allowed": False,
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
            "tower_owns_seller_portal_unlock": True,
            "vault_owns_tower_permissions": False,
        },
        "workspace_summary": {
            "room_title": "Vault ATM Route Packet Workspace",
            "route": "/vault/atm-route-workspace",
            "json_route": "/vault/atm-route-workspace.json",
            "packet_route": "/vault/atm-route-packet.json",
            "due_diligence_route": "/vault/atm-route-due-diligence.json",
            "financial_review_route": "/vault/atm-route-financial-review.json",
            "owner_actions_route": "/vault/atm-route-owner-actions.json",
            "blocked_reasons_route": "/vault/atm-route-blocked-reasons.json",
            "gp017_status_route": "/vault/gp017-status.json",
            "requirement_count": len(atm_packet["requirements"]),
            "due_diligence_lane_count": len(due_diligence["lanes"]),
            "owner_action_count": len(owner_actions["actions"]),
            "blocked_reason_count": len(blocked_reasons),
            "metadata_only": True,
        },
        "atm_route_packet": atm_packet,
        "atm_route_due_diligence": due_diligence,
        "atm_route_financial_review": financial_review,
        "atm_route_owner_actions": owner_actions,
        "atm_route_blocked_reasons": blocked_reasons,
        "atm_route_readiness": readiness,
        "gp017_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp018": True,
            "next_pack": "VAULT_GP018_APARTMENT_LENDER_PACKET_WORKSPACE_V2",
            "gp016_atm_binder_connected": True,
            "atm_route_workspace_ready": True,
            "metadata_only_workspace": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "seller_portal_still_locked": True,
            "external_lender_share_still_locked": True,
            "financing_decision_not_claimed": True,
            "seller_financial_verification_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp017",
        },
    }

    return payload


def _find_atm_binder(binders: List[Dict[str, Any]]) -> Dict[str, Any]:
    for binder in binders:
        if binder["binder_id"] == "VEB-ATM-ROUTE-001":
            return binder

    return {
        "binder_id": "VEB-ATM-ROUTE-001",
        "binder_type": "atm_route_acquisition",
        "binder_type_label": "ATM Route Acquisition Evidence Binder",
        "lane": "SimpleeOnTheGo / ATM",
        "packet_id": "atm_route_acquisition_packet",
        "section_count": 0,
        "version_ids": [],
        "document_keys": [],
        "lineage_ids": [],
        "sections": [],
        "binder_status": "HELD_METADATA_ONLY",
        "blocked_codes": ["PERMANENT_STORAGE_NOT_CONFIGURED"],
        "owner_action": "Connect ATM evidence binder metadata before workspace completion.",
    }


def _build_atm_packet(atm_binder: Dict[str, Any]) -> Dict[str, Any]:
    requirements = []

    binder_requirement_ids = {
        section.get("requirement_id")
        for section in atm_binder.get("sections", [])
        if section.get("requirement_id")
    }

    for item in ATM_PACKET_REQUIREMENTS:
        linked = item["requirement_id"] in binder_requirement_ids or item["requirement_id"] == "atm_route_seller_financials"

        requirements.append(
            {
                "requirement_id": item["requirement_id"],
                "label": item["label"],
                "required": item["required"],
                "source": item["source"],
                "raw_body_required_later": item["raw_body_required_later"],
                "metadata_available": linked,
                "raw_body_available": False,
                "owner_confirmed": False,
                "tower_clearance_required": item["requirement_id"] in {
                    "atm_route_seller_financials",
                    "atm_route_processor_statements",
                    "atm_route_bank_lender_packet",
                },
                "status": "metadata_available" if linked else "needs_metadata",
            }
        )

    return {
        "packet_id": "atm_route_acquisition_packet_v2",
        "source_binder_id": atm_binder["binder_id"],
        "source_packet_id": atm_binder["packet_id"],
        "lane": "SimpleeOnTheGo / ATM",
        "workspace_status": "ATM_WORKSPACE_METADATA_READY",
        "workspace_status_label": WORKSPACE_STATUSES["ATM_WORKSPACE_METADATA_READY"],
        "route_target": "two_small_atm_routes_or_route_businesses",
        "owner_strategy": "Prepare clean review packet for buying two smaller ATM routes/businesses, with vault cash needs tracked separately.",
        "requirements": requirements,
        "requirements_total": len(requirements),
        "requirements_metadata_available": sum(1 for item in requirements if item["metadata_available"]),
        "requirements_raw_body_available": 0,
        "seller_packet_truth": {
            "seller_packet_received_as_raw_body": False,
            "seller_financials_verified_from_raw_statement": False,
            "seller_portal_enabled": False,
            "external_seller_access_enabled": False,
            "fake_seller_packet_complete": False,
        },
        "binder_sections": atm_binder.get("sections", []),
        "redacted_owner_preview": {
            "available": True,
            "safe_fields": [
                "packet_id",
                "binder_id",
                "requirement_id",
                "requirement_label",
                "metadata_status",
                "owner_action",
                "blocked_reason",
            ],
            "raw_values_hidden": True,
            "unredacted_preview_allowed": False,
        },
    }


def _build_due_diligence(atm_binder: Dict[str, Any], atm_packet: Dict[str, Any]) -> Dict[str, Any]:
    lanes = []

    for lane in DUE_DILIGENCE_LANES:
        blocked_codes = [
            "RAW_FILE_BODY_LOCKED",
            "DIRECT_UPLOAD_LOCKED",
            "EXTERNAL_LENDER_SHARE_LOCKED",
            "OWNER_CONFIRMATION_REQUIRED",
        ]

        if lane["tower_clearance_required"]:
            blocked_codes.append("TOWER_CLEARANCE_REQUIRED")

        if lane["lane_id"] in {"atm_dd_cash_flow", "atm_dd_vault_cash"}:
            blocked_codes.append("NO_SELLER_FINANCIAL_VERIFICATION_CLAIM")

        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "label": lane["label"],
                "owner": lane["owner"],
                "tower_clearance_required": lane["tower_clearance_required"],
                "status": "metadata_review_ready",
                "raw_body_required_for_final_review": lane["lane_id"] in {
                    "atm_dd_cash_flow",
                    "atm_dd_vault_cash",
                    "atm_dd_bank_packet",
                },
                "raw_body_available": False,
                "owner_confirmed": False,
                "blocked_codes": sorted(set(blocked_codes)),
                "owner_action": _owner_action_for_due_diligence_lane(lane["lane_id"]),
            }
        )

    return {
        "workspace": "ATM Route Due Diligence",
        "source_binder_id": atm_binder["binder_id"],
        "source_packet_id": atm_packet["packet_id"],
        "lanes": lanes,
        "lane_count": len(lanes),
        "metadata_review_ready_count": len(lanes),
        "raw_body_available_count": 0,
        "tower_clearance_required_count": sum(1 for lane in lanes if lane["tower_clearance_required"]),
        "owner_confirmation_required": True,
        "auto_due_diligence_pass_allowed": False,
    }


def _owner_action_for_due_diligence_lane(lane_id: str) -> str:
    actions = {
        "atm_dd_seller_identity": "Confirm seller/entity identity requirements and wait for Tower clearance before external movement.",
        "atm_dd_route_quality": "Review machine count, location quality, and route fit using metadata only.",
        "atm_dd_cash_flow": "Review cash-flow placeholders without claiming raw statement verification.",
        "atm_dd_vault_cash": "Estimate vault cash requirement range without treating it as final financing.",
        "atm_dd_bank_packet": "Prepare lender packet checklist while external lender sharing stays locked.",
        "atm_dd_risk_flags": "Review blocked reasons and decide what remains unresolved.",
    }
    return actions.get(lane_id, "Review lane metadata and keep sensitive actions locked.")


def _build_financial_review(atm_binder: Dict[str, Any], atm_packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "review_id": "ATM-FIN-REVIEW-GP017",
        "source_binder_id": atm_binder["binder_id"],
        "source_packet_id": atm_packet["packet_id"],
        "financial_review_mode": "metadata_placeholders_only",
        "financing_decision_enabled": False,
        "bank_submission_enabled": False,
        "external_lender_share_enabled": False,
        "seller_financials_verified_from_raw_statements": False,
        "vault_cash_tracking": {
            "enabled": True,
            "final_amount_known": False,
            "raw_statement_support_available": False,
            "owner_note": "Track vault cash requirement as acquisition-review metadata only until seller/bank documents are available through approved provider/Tower flow.",
        },
        "review_fields": [
            {
                "field_id": "asking_price",
                "label": "Seller asking price",
                "value_status": "placeholder_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "monthly_gross_surcharge",
                "label": "Monthly gross surcharge",
                "value_status": "placeholder_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "monthly_net_income",
                "label": "Monthly net income",
                "value_status": "placeholder_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "vault_cash_requirement",
                "label": "Vault cash requirement",
                "value_status": "estimate_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "loan_packet_readiness",
                "label": "Loan packet readiness",
                "value_status": "metadata_review_ready",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
        ],
        "blocked_codes": [
            "NO_FINANCING_DECISION",
            "NO_SELLER_FINANCIAL_VERIFICATION_CLAIM",
            "EXTERNAL_LENDER_SHARE_LOCKED",
            "RAW_FILE_BODY_LOCKED",
            "OWNER_CONFIRMATION_REQUIRED",
        ],
    }


def _build_owner_actions(
    atm_binder: Dict[str, Any],
    due_diligence: Dict[str, Any],
    financial_review: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "ATM-ACTION-001",
            "label": "Confirm ATM route acquisition packet metadata",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ATM-ACTION-002",
            "label": "List missing seller packet documents",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ATM-ACTION-003",
            "label": "Track vault cash requirement as placeholder",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ATM-ACTION-004",
            "label": "Keep lender sharing locked until Tower clearance",
            "status": "blocked_by_tower_boundary",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ATM-ACTION-005",
            "label": "Keep seller portal locked",
            "status": "blocked_by_tower_boundary",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "ATM-ACTION-006",
            "label": "Prepare next owner review notes for route acquisition",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault ATM Route Packet Workspace",
        "source_binder_id": atm_binder["binder_id"],
        "actions": actions,
        "action_count": len(actions),
        "owner_review_needed_count": sum(1 for action in actions if action["status"] == "owner_review_needed"),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review ATM route packet metadata.",
            "Identify seller documents still missing.",
            "Track vault cash requirement as an estimate/placeholder only.",
            "Keep seller portal, lender sharing, direct upload, and raw exports locked.",
            "Carry workspace pattern into GP018 Apartment Lender Packet Workspace v2.",
        ],
    }


def _build_blocked_reasons(
    atm_binder: Dict[str, Any],
    due_diligence: Dict[str, Any],
    financial_review: Dict[str, Any],
) -> List[Dict[str, Any]]:
    active_codes = set(atm_binder.get("blocked_codes", []))
    for lane in due_diligence["lanes"]:
        active_codes.update(lane["blocked_codes"])
    active_codes.update(financial_review["blocked_codes"])
    active_codes.update({
        "SELLER_PORTAL_LOCKED",
        "RAW_EXPORT_LOCKED",
        "UNREDACTED_PREVIEW_LOCKED",
        "NO_AUTO_ACQUISITION_APPROVAL",
    })

    return [
        {
            "code": code,
            "label": ATM_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code or "PORTAL" in code or "UPLOAD" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in sorted(active_codes)
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only ATM packet review. Do not read or display raw body.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw document work until provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before packet completion.",
        "SELLER_PORTAL_LOCKED": "Do not open seller portal access from Vault.",
        "EXTERNAL_LENDER_SHARE_LOCKED": "Do not share with external lender from GP017.",
        "UNREDACTED_PREVIEW_LOCKED": "Do not show unredacted preview.",
        "RAW_EXPORT_LOCKED": "Do not export raw ATM packet.",
        "NO_AUTO_ACQUISITION_APPROVAL": "Do not auto-approve acquisition.",
        "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
        "NO_SELLER_FINANCIAL_VERIFICATION_CLAIM": "Do not claim raw seller financial verification.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_readiness(
    atm_packet: Dict[str, Any],
    due_diligence: Dict[str, Any],
    financial_review: Dict[str, Any],
    owner_actions: Dict[str, Any],
) -> Dict[str, Any]:
    metadata_ready = (
        atm_packet["requirements_metadata_available"] >= 1
        and due_diligence["metadata_review_ready_count"] == due_diligence["lane_count"]
        and owner_actions["action_count"] >= 1
    )

    return {
        "workspace_readiness_label": "ATM route workspace metadata ready",
        "metadata_ready": metadata_ready,
        "raw_body_ready": False,
        "seller_packet_complete": False,
        "lender_share_ready": False,
        "financing_decision_ready": False,
        "safe_to_continue_to_gp018": True,
        "reason_safe_to_continue": "GP017 creates ATM-specific metadata workspace depth without unlocking restricted storage or sharing.",
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_atm_route_workspace_payload())


def get_atm_route_workspace_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "workspace_truth": payload["workspace_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "workspace_summary": payload["workspace_summary"],
        "atm_route_readiness": payload["atm_route_readiness"],
    }


def get_atm_route_packet() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "atm_route_packet": payload["atm_route_packet"],
    }


def get_atm_route_due_diligence() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "atm_route_due_diligence": payload["atm_route_due_diligence"],
    }


def get_atm_route_financial_review() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "atm_route_financial_review": payload["atm_route_financial_review"],
    }


def get_atm_route_owner_actions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "atm_route_owner_actions": payload["atm_route_owner_actions"],
    }


def get_atm_route_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "atm_route_blocked_reasons": payload["atm_route_blocked_reasons"],
        "blocked_reason_count": len(payload["atm_route_blocked_reasons"]),
    }


def get_gp017_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp017_status": payload["gp017_status"],
        "workspace_summary": payload["workspace_summary"],
        "workspace_truth": payload["workspace_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "atm_route_readiness": payload["atm_route_readiness"],
    }


def render_atm_route_workspace_page() -> str:
    payload = clone_payload()
    summary = payload["workspace_summary"]
    truth = payload["workspace_truth"]
    packet = payload["atm_route_packet"]
    due_diligence = payload["atm_route_due_diligence"]
    financial_review = payload["atm_route_financial_review"]
    owner_actions = payload["atm_route_owner_actions"]

    requirement_cards = "\n".join(_render_requirement_card(item) for item in packet["requirements"])
    lane_rows = "\n".join(
        f"""
        <div class="status-row">
          <div>
            <strong>{escape(lane["label"])}</strong>
            <span>{escape(lane["lane_id"])}</span>
          </div>
          <div class="pill warn">{escape(lane["status"])}</div>
        </div>
        """
        for lane in due_diligence["lanes"]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner_actions["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault ATM Route Packet Workspace · GP017</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 017</div>
        <h1>ATM Route Packet Workspace</h1>
        <p class="hero-copy">
          GP017 turns the ATM evidence binder into a focused route acquisition workspace.
          It tracks seller packet needs, due diligence lanes, vault cash placeholders, and owner actions
          without unlocking raw upload, seller portal, lender sharing, unredacted previews, or financing decisions.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["requirement_count"]}</strong>
            <span>packet requirements</span>
          </div>
          <div class="metric">
            <strong>{summary["due_diligence_lane_count"]}</strong>
            <span>due diligence lanes</span>
          </div>
          <div class="metric">
            <strong>{summary["owner_action_count"]}</strong>
            <span>owner actions</span>
          </div>
          <div class="metric">
            <strong>Locked</strong>
            <span>seller/lender access</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">ATM metadata workspace ready</span>
          <span class="pill warn">Vault cash placeholder</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Seller portal locked</span>
          <span class="pill danger">No financing decision</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>ATM Packet Requirements</h2>
      <p>
        Requirements are metadata-only. Seller financials are not verified from raw statements in GP017.
      </p>
      <div class="grid">
        {requirement_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Due Diligence Lanes</h2>
        <p>Each lane is ready for owner metadata review while sensitive movement stays Tower-controlled.</p>
        <div>
          {lane_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP017 prepares ATM acquisition review without claiming purchase, financing, or raw verification.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP017 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["packet_route"])}</code>
        <code>{escape(summary["due_diligence_route"])}</code>
        <code>{escape(summary["financial_review_route"])}</code>
        <code>{escape(summary["owner_actions_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp017_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Workspace Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Seller portal:
        <code>{str(truth["seller_portal_enabled"]).lower()}</code>.
        Lender share:
        <code>{str(truth["external_lender_share_enabled"]).lower()}</code>.
        Financing decision:
        <code>{str(truth["financing_decision_enabled"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_requirement_card(item: Dict[str, Any]) -> str:
    status_class = "ok" if item["metadata_available"] else "warn"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item["label"])}</div>
            <div class="meta">
              Requirement: <code>{escape(item["requirement_id"])}</code><br>
              Source: {escape(item["source"])}<br>
              Raw body later: <code>{str(item["raw_body_required_later"]).lower()}</code><br>
              Tower clearance: <code>{str(item["tower_clearance_required"]).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(item["status"])}</span>
        </div>
      </article>
    """
