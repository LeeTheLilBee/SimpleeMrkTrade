"""
VAULT GIANT PACK 018 — Apartment Lender Packet Workspace v2

This pack turns the GP016 apartment evidence binder into a real apartment lender
packet workspace.

Important truth:
- This is an owner review and lender-readiness workspace for apartment acquisition.
- It is metadata-only in GP018.
- It does not unlock raw file body storage, direct upload, lender sharing,
  seller/broker portal access, unredacted export, or external access.
- It does not make financing decisions.
- It does not claim rent rolls, T12, NOI, DSCR, appraisal, inspection, or title are verified by raw documents.
- It prepares the road for GP019 Trust/Entity Binder Workspace v2.
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


PACK_ID = "VAULT_GP018"
PACK_NAME = "Apartment Lender Packet Workspace v2"
SCHEMA_VERSION = "vault.apartment_lender_packet_workspace.v2"

WORKSPACE_STATUSES = {
    "APARTMENT_WORKSPACE_METADATA_READY": "Apartment workspace metadata ready",
    "NEEDS_OWNER_REVIEW": "Needs owner review",
    "NEEDS_SELLER_PACKET": "Needs seller packet",
    "NEEDS_LENDER_REQUIREMENT_REVIEW": "Needs lender requirement review",
    "NEEDS_TOWER_CLEARANCE": "Needs Tower clearance",
    "BLOCKED_STORAGE_PROVIDER": "Blocked by storage provider",
    "HELD_METADATA_ONLY": "Held metadata only",
}

APARTMENT_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before packet completion.",
    "SELLER_BROKER_PORTAL_LOCKED": "Seller/broker portal access is locked.",
    "EXTERNAL_LENDER_SHARE_LOCKED": "External lender sharing is locked.",
    "UNREDACTED_PREVIEW_LOCKED": "Unredacted preview is locked.",
    "RAW_EXPORT_LOCKED": "Raw export is locked.",
    "NO_AUTO_ACQUISITION_APPROVAL": "Auto acquisition approval is disabled.",
    "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
    "NO_RENT_ROLL_VERIFICATION_CLAIM": "Rent roll is not verified from raw documents in GP018.",
    "NO_T12_VERIFICATION_CLAIM": "T12/operating statement is not verified from raw documents in GP018.",
    "NO_NOI_DSCR_CLAIM": "NOI/DSCR are not final or verified in GP018.",
    "NO_APPRAISAL_INSPECTION_TITLE_CLAIM": "Appraisal, inspection, title, and survey are not verified in GP018.",
}

APARTMENT_PACKET_REQUIREMENTS = [
    {
        "requirement_id": "apt_rent_roll",
        "label": "Rent roll",
        "required": True,
        "source": "seller/lender packet metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "apt_t12_operating_statement",
        "label": "T12 operating statement",
        "required": True,
        "source": "seller/lender packet metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "apt_noi_dscr_snapshot",
        "label": "NOI / DSCR snapshot",
        "required": True,
        "source": "Vault generated metadata packet",
        "raw_body_required_later": False,
    },
    {
        "requirement_id": "apt_property_tax_insurance",
        "label": "Property tax and insurance",
        "required": True,
        "source": "due diligence metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "apt_title_survey",
        "label": "Title / survey",
        "required": True,
        "source": "closing due diligence metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "apt_inspection_capex",
        "label": "Inspection / capex notes",
        "required": True,
        "source": "inspection metadata",
        "raw_body_required_later": True,
    },
    {
        "requirement_id": "apt_lender_packet_requirements",
        "label": "Lender packet requirements",
        "required": True,
        "source": "GP016 metadata section",
        "raw_body_required_later": False,
    },
]

DUE_DILIGENCE_LANES = [
    {
        "lane_id": "apt_dd_property_identity",
        "label": "Property identity and unit count",
        "owner": "Vault",
        "tower_clearance_required": False,
    },
    {
        "lane_id": "apt_dd_seller_broker",
        "label": "Seller / broker package",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "apt_dd_rent_roll",
        "label": "Rent roll review",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "apt_dd_t12_noi",
        "label": "T12, NOI, and DSCR review",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "apt_dd_lender_packet",
        "label": "Bank/lender packet readiness",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "apt_dd_inspection_capex",
        "label": "Inspection, capex, and risk flags",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "apt_dd_title_survey",
        "label": "Title, survey, insurance, and taxes",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_apartment_lender_workspace_payload() -> Dict[str, Any]:
    gp016 = get_evidence_binder_payload()
    apartment_binder = _find_apartment_binder(gp016["evidence_binders"])
    apartment_packet = _build_apartment_packet(apartment_binder)
    due_diligence = _build_due_diligence(apartment_binder, apartment_packet)
    financial_review = _build_financial_review(apartment_binder, apartment_packet)
    owner_actions = _build_owner_actions(apartment_binder, due_diligence, financial_review)
    blocked_reasons = _build_blocked_reasons(apartment_binder, due_diligence, financial_review)
    readiness = _build_readiness(apartment_packet, due_diligence, financial_review, owner_actions)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "apartment_lender_packet_workspace_v2",
        },
        "workspace_truth": {
            "workspace_enabled": True,
            "metadata_only": True,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "seller_broker_portal_enabled": False,
            "external_lender_share_enabled": False,
            "raw_export_enabled": False,
            "unredacted_preview_enabled": False,
            "redacted_owner_preview_enabled": True,
            "auto_acquisition_approval_enabled": False,
            "financing_decision_enabled": False,
            "rent_roll_verified_from_raw_documents": False,
            "t12_verified_from_raw_documents": False,
            "noi_dscr_final_or_verified": False,
            "appraisal_inspection_title_verified": False,
            "fake_lender_packet_complete": False,
            "safe_next_unlock": "GP019 Trust/Entity Binder Workspace v2 can use shared binder/authority patterns without unlocking raw storage.",
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "seller_broker_portal_allowed": False,
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
            "tower_owns_seller_broker_portal_unlock": True,
            "tower_owns_lender_share_unlock": True,
            "vault_owns_tower_permissions": False,
        },
        "workspace_summary": {
            "room_title": "Vault Apartment Lender Packet Workspace",
            "route": "/vault/apartment-lender-workspace",
            "json_route": "/vault/apartment-lender-workspace.json",
            "packet_route": "/vault/apartment-lender-packet.json",
            "due_diligence_route": "/vault/apartment-due-diligence.json",
            "financial_review_route": "/vault/apartment-financial-review.json",
            "owner_actions_route": "/vault/apartment-owner-actions.json",
            "blocked_reasons_route": "/vault/apartment-blocked-reasons.json",
            "gp018_status_route": "/vault/gp018-status.json",
            "requirement_count": len(apartment_packet["requirements"]),
            "due_diligence_lane_count": len(due_diligence["lanes"]),
            "owner_action_count": len(owner_actions["actions"]),
            "blocked_reason_count": len(blocked_reasons),
            "metadata_only": True,
        },
        "apartment_lender_packet": apartment_packet,
        "apartment_due_diligence": due_diligence,
        "apartment_financial_review": financial_review,
        "apartment_owner_actions": owner_actions,
        "apartment_blocked_reasons": blocked_reasons,
        "apartment_readiness": readiness,
        "gp018_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp019": True,
            "next_pack": "VAULT_GP019_TRUST_ENTITY_BINDER_WORKSPACE_V2",
            "gp016_apartment_binder_connected": True,
            "apartment_lender_workspace_ready": True,
            "metadata_only_workspace": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "seller_broker_portal_still_locked": True,
            "external_lender_share_still_locked": True,
            "financing_decision_not_claimed": True,
            "rent_roll_verification_not_claimed": True,
            "t12_verification_not_claimed": True,
            "noi_dscr_verification_not_claimed": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp018",
        },
    }

    return payload


def _find_apartment_binder(binders: List[Dict[str, Any]]) -> Dict[str, Any]:
    for binder in binders:
        if binder["binder_id"] == "VEB-APT-LENDER-001":
            return binder

    return {
        "binder_id": "VEB-APT-LENDER-001",
        "binder_type": "apartment_lender_due_diligence",
        "binder_type_label": "Apartment Lender Due Diligence Evidence Binder",
        "lane": "SimpleeProperty / Apartment",
        "packet_id": "apartment_lender_due_diligence_packet",
        "section_count": 0,
        "version_ids": [],
        "document_keys": [],
        "lineage_ids": [],
        "sections": [],
        "binder_status": "HELD_METADATA_ONLY",
        "blocked_codes": ["PERMANENT_STORAGE_NOT_CONFIGURED"],
        "owner_action": "Connect apartment evidence binder metadata before workspace completion.",
    }


def _build_apartment_packet(apartment_binder: Dict[str, Any]) -> Dict[str, Any]:
    requirements = []

    binder_requirement_ids = {
        section.get("requirement_id")
        for section in apartment_binder.get("sections", [])
        if section.get("requirement_id")
    }

    for item in APARTMENT_PACKET_REQUIREMENTS:
        linked = (
            item["requirement_id"] in binder_requirement_ids
            or item["requirement_id"] == "apt_lender_packet_requirements"
            or item["requirement_id"] == "apt_noi_dscr_snapshot"
        )

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
                    "apt_rent_roll",
                    "apt_t12_operating_statement",
                    "apt_lender_packet_requirements",
                    "apt_title_survey",
                    "apt_inspection_capex",
                },
                "status": "metadata_available" if linked else "needs_metadata",
            }
        )

    return {
        "packet_id": "apartment_lender_packet_v2",
        "source_binder_id": apartment_binder["binder_id"],
        "source_packet_id": apartment_binder["packet_id"],
        "lane": "SimpleeProperty / Apartment",
        "workspace_status": "APARTMENT_WORKSPACE_METADATA_READY",
        "workspace_status_label": WORKSPACE_STATUSES["APARTMENT_WORKSPACE_METADATA_READY"],
        "property_target": "4_to_5_building_apartment_complex",
        "owner_strategy": "Prepare apartment lender packet metadata while searching in parallel with OB Manual Live Phase 1.",
        "requirements": requirements,
        "requirements_total": len(requirements),
        "requirements_metadata_available": sum(1 for item in requirements if item["metadata_available"]),
        "requirements_raw_body_available": 0,
        "seller_packet_truth": {
            "seller_packet_received_as_raw_body": False,
            "rent_roll_verified_from_raw_document": False,
            "t12_verified_from_raw_document": False,
            "seller_broker_portal_enabled": False,
            "external_lender_access_enabled": False,
            "fake_lender_packet_complete": False,
        },
        "binder_sections": apartment_binder.get("sections", []),
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


def _build_due_diligence(apartment_binder: Dict[str, Any], apartment_packet: Dict[str, Any]) -> Dict[str, Any]:
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

        if lane["lane_id"] == "apt_dd_rent_roll":
            blocked_codes.append("NO_RENT_ROLL_VERIFICATION_CLAIM")

        if lane["lane_id"] == "apt_dd_t12_noi":
            blocked_codes.extend(["NO_T12_VERIFICATION_CLAIM", "NO_NOI_DSCR_CLAIM"])

        if lane["lane_id"] in {"apt_dd_inspection_capex", "apt_dd_title_survey"}:
            blocked_codes.append("NO_APPRAISAL_INSPECTION_TITLE_CLAIM")

        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "label": lane["label"],
                "owner": lane["owner"],
                "tower_clearance_required": lane["tower_clearance_required"],
                "status": "metadata_review_ready",
                "raw_body_required_for_final_review": lane["lane_id"] in {
                    "apt_dd_rent_roll",
                    "apt_dd_t12_noi",
                    "apt_dd_lender_packet",
                    "apt_dd_inspection_capex",
                    "apt_dd_title_survey",
                },
                "raw_body_available": False,
                "owner_confirmed": False,
                "blocked_codes": sorted(set(blocked_codes)),
                "owner_action": _owner_action_for_due_diligence_lane(lane["lane_id"]),
            }
        )

    return {
        "workspace": "Apartment Due Diligence",
        "source_binder_id": apartment_binder["binder_id"],
        "source_packet_id": apartment_packet["packet_id"],
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
        "apt_dd_property_identity": "Confirm property identity, unit count, and target fit using metadata only.",
        "apt_dd_seller_broker": "Confirm seller/broker package requirements while portal access stays locked.",
        "apt_dd_rent_roll": "Review rent roll placeholders without claiming raw document verification.",
        "apt_dd_t12_noi": "Review T12/NOI/DSCR placeholders without treating them as final.",
        "apt_dd_lender_packet": "Prepare lender packet checklist while external lender sharing stays locked.",
        "apt_dd_inspection_capex": "Track inspection/capex risk flags without claiming inspection verification.",
        "apt_dd_title_survey": "Track title/survey/tax/insurance needs without claiming verification.",
    }
    return actions.get(lane_id, "Review lane metadata and keep sensitive actions locked.")


def _build_financial_review(apartment_binder: Dict[str, Any], apartment_packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "review_id": "APT-FIN-REVIEW-GP018",
        "source_binder_id": apartment_binder["binder_id"],
        "source_packet_id": apartment_packet["packet_id"],
        "financial_review_mode": "metadata_placeholders_only",
        "financing_decision_enabled": False,
        "bank_submission_enabled": False,
        "external_lender_share_enabled": False,
        "rent_roll_verified_from_raw_documents": False,
        "t12_verified_from_raw_documents": False,
        "noi_dscr_final_or_verified": False,
        "appraisal_inspection_title_verified": False,
        "loan_packet_tracking": {
            "enabled": True,
            "final_loan_amount_known": False,
            "raw_statement_support_available": False,
            "owner_note": "Track lender packet readiness as acquisition-review metadata only until seller/broker/lender documents are available through approved provider/Tower flow.",
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
                "field_id": "unit_count",
                "label": "Unit count",
                "value_status": "metadata_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "rent_roll_income",
                "label": "Rent roll income",
                "value_status": "placeholder_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "t12_expenses",
                "label": "T12 expenses",
                "value_status": "placeholder_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "noi",
                "label": "NOI",
                "value_status": "estimate_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "dscr",
                "label": "DSCR",
                "value_status": "estimate_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
            {
                "field_id": "lender_packet_readiness",
                "label": "Lender packet readiness",
                "value_status": "metadata_review_ready",
                "raw_support_available": False,
                "owner_confirmed": False,
            },
        ],
        "blocked_codes": [
            "NO_FINANCING_DECISION",
            "NO_RENT_ROLL_VERIFICATION_CLAIM",
            "NO_T12_VERIFICATION_CLAIM",
            "NO_NOI_DSCR_CLAIM",
            "NO_APPRAISAL_INSPECTION_TITLE_CLAIM",
            "EXTERNAL_LENDER_SHARE_LOCKED",
            "RAW_FILE_BODY_LOCKED",
            "OWNER_CONFIRMATION_REQUIRED",
        ],
    }


def _build_owner_actions(
    apartment_binder: Dict[str, Any],
    due_diligence: Dict[str, Any],
    financial_review: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "APT-ACTION-001",
            "label": "Confirm apartment lender packet metadata",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "APT-ACTION-002",
            "label": "List missing seller/broker packet documents",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "APT-ACTION-003",
            "label": "Track rent roll and T12 as placeholders",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "APT-ACTION-004",
            "label": "Keep lender sharing locked until Tower clearance",
            "status": "blocked_by_tower_boundary",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "APT-ACTION-005",
            "label": "Keep seller/broker portal locked",
            "status": "blocked_by_tower_boundary",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "APT-ACTION-006",
            "label": "Prepare next trust/entity authority review for acquisition packet",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Apartment Lender Packet Workspace",
        "source_binder_id": apartment_binder["binder_id"],
        "actions": actions,
        "action_count": len(actions),
        "owner_review_needed_count": sum(1 for action in actions if action["status"] == "owner_review_needed"),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review apartment lender packet metadata.",
            "Identify seller/broker documents still missing.",
            "Track rent roll, T12, NOI, and DSCR as placeholders only.",
            "Keep seller/broker portal, lender sharing, direct upload, and raw exports locked.",
            "Carry authority and entity needs into GP019 Trust/Entity Binder Workspace v2.",
        ],
    }


def _build_blocked_reasons(
    apartment_binder: Dict[str, Any],
    due_diligence: Dict[str, Any],
    financial_review: Dict[str, Any],
) -> List[Dict[str, Any]]:
    active_codes = set(apartment_binder.get("blocked_codes", []))
    for lane in due_diligence["lanes"]:
        active_codes.update(lane["blocked_codes"])
    active_codes.update(financial_review["blocked_codes"])
    active_codes.update({
        "SELLER_BROKER_PORTAL_LOCKED",
        "RAW_EXPORT_LOCKED",
        "UNREDACTED_PREVIEW_LOCKED",
        "NO_AUTO_ACQUISITION_APPROVAL",
    })

    return [
        {
            "code": code,
            "label": APARTMENT_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code or "PORTAL" in code or "UPLOAD" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in sorted(active_codes)
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only apartment packet review. Do not read or display raw body.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw document work until provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before packet completion.",
        "SELLER_BROKER_PORTAL_LOCKED": "Do not open seller/broker portal access from Vault.",
        "EXTERNAL_LENDER_SHARE_LOCKED": "Do not share with external lender from GP018.",
        "UNREDACTED_PREVIEW_LOCKED": "Do not show unredacted preview.",
        "RAW_EXPORT_LOCKED": "Do not export raw apartment packet.",
        "NO_AUTO_ACQUISITION_APPROVAL": "Do not auto-approve acquisition.",
        "NO_FINANCING_DECISION": "Vault does not make financing decisions.",
        "NO_RENT_ROLL_VERIFICATION_CLAIM": "Do not claim raw rent roll verification.",
        "NO_T12_VERIFICATION_CLAIM": "Do not claim raw T12 verification.",
        "NO_NOI_DSCR_CLAIM": "Do not claim final NOI/DSCR verification.",
        "NO_APPRAISAL_INSPECTION_TITLE_CLAIM": "Do not claim appraisal, inspection, title, or survey verification.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_readiness(
    apartment_packet: Dict[str, Any],
    due_diligence: Dict[str, Any],
    financial_review: Dict[str, Any],
    owner_actions: Dict[str, Any],
) -> Dict[str, Any]:
    metadata_ready = (
        apartment_packet["requirements_metadata_available"] >= 1
        and due_diligence["metadata_review_ready_count"] == due_diligence["lane_count"]
        and owner_actions["action_count"] >= 1
    )

    return {
        "workspace_readiness_label": "Apartment lender workspace metadata ready",
        "metadata_ready": metadata_ready,
        "raw_body_ready": False,
        "seller_broker_packet_complete": False,
        "lender_share_ready": False,
        "financing_decision_ready": False,
        "safe_to_continue_to_gp019": True,
        "reason_safe_to_continue": "GP018 creates apartment-specific lender packet workspace depth without unlocking restricted storage or sharing.",
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_apartment_lender_workspace_payload())


def get_apartment_lender_workspace_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "workspace_truth": payload["workspace_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "workspace_summary": payload["workspace_summary"],
        "apartment_readiness": payload["apartment_readiness"],
    }


def get_apartment_lender_packet() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "apartment_lender_packet": payload["apartment_lender_packet"],
    }


def get_apartment_due_diligence() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "apartment_due_diligence": payload["apartment_due_diligence"],
    }


def get_apartment_financial_review() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "apartment_financial_review": payload["apartment_financial_review"],
    }


def get_apartment_owner_actions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "apartment_owner_actions": payload["apartment_owner_actions"],
    }


def get_apartment_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "apartment_blocked_reasons": payload["apartment_blocked_reasons"],
        "blocked_reason_count": len(payload["apartment_blocked_reasons"]),
    }


def get_gp018_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp018_status": payload["gp018_status"],
        "workspace_summary": payload["workspace_summary"],
        "workspace_truth": payload["workspace_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "apartment_readiness": payload["apartment_readiness"],
    }


def render_apartment_lender_workspace_page() -> str:
    payload = clone_payload()
    summary = payload["workspace_summary"]
    truth = payload["workspace_truth"]
    packet = payload["apartment_lender_packet"]
    due_diligence = payload["apartment_due_diligence"]
    owner_actions = payload["apartment_owner_actions"]

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
  <title>Vault Apartment Lender Packet Workspace · GP018</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 018</div>
        <h1>Apartment Lender Packet Workspace</h1>
        <p class="hero-copy">
          GP018 turns the apartment evidence binder into a lender packet workspace.
          It tracks rent roll, T12, NOI/DSCR placeholders, due diligence lanes, and owner actions
          without unlocking raw upload, seller/broker portal, lender sharing, unredacted previews, or financing decisions.
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
          <span class="pill ok">Apartment metadata workspace ready</span>
          <span class="pill warn">NOI/DSCR placeholders</span>
          <span class="pill warn">Owner review required</span>
          <span class="pill danger">Lender share locked</span>
          <span class="pill danger">No financing decision</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Apartment Lender Packet Requirements</h2>
      <p>
        Requirements are metadata-only. Rent roll, T12, NOI, DSCR, title, inspection, and appraisal are not verified from raw documents in GP018.
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
        <p>GP018 prepares apartment lender review without claiming purchase, financing, or raw verification.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP018 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["packet_route"])}</code>
        <code>{escape(summary["due_diligence_route"])}</code>
        <code>{escape(summary["financial_review_route"])}</code>
        <code>{escape(summary["owner_actions_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp018_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Workspace Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Seller/broker portal:
        <code>{str(truth["seller_broker_portal_enabled"]).lower()}</code>.
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
