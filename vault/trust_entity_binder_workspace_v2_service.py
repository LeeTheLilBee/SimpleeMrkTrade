"""
VAULT GIANT PACK 019 — Trust/Entity Binder Workspace v2

This pack turns the GP016 Trust/Entity evidence binder into a real authority,
entity, and proof workspace.

Important truth:
- This is an owner review workspace for trust/entity authority and acquisition packet support.
- It is metadata-only in GP019.
- It does not unlock raw file body storage, direct upload, trustee portal access,
  bank/lender/entity external sharing, unredacted export, or external access.
- It does not provide legal advice or claim legal sufficiency.
- It does not claim notarized trust, EIN, LLC, banking, trustee authority, beneficiary data,
  or acquisition authority are verified from raw documents.
- It prepares the road for GP020 Vault Operational Readiness Checkpoint.
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


PACK_ID = "VAULT_GP019"
PACK_NAME = "Trust/Entity Binder Workspace v2"
SCHEMA_VERSION = "vault.trust_entity_binder_workspace.v2"

WORKSPACE_STATUSES = {
    "TRUST_ENTITY_WORKSPACE_METADATA_READY": "Trust/entity workspace metadata ready",
    "NEEDS_OWNER_REVIEW": "Needs owner review",
    "NEEDS_AUTHORITY_REVIEW": "Needs authority review",
    "NEEDS_ENTITY_PACKET_REVIEW": "Needs entity packet review",
    "NEEDS_TOWER_CLEARANCE": "Needs Tower clearance",
    "BLOCKED_STORAGE_PROVIDER": "Blocked by storage provider",
    "HELD_METADATA_ONLY": "Held metadata only",
}

TRUST_ENTITY_BLOCK_CODES = {
    "RAW_FILE_BODY_LOCKED": "Raw file body remains locked.",
    "DIRECT_UPLOAD_LOCKED": "Direct upload remains locked.",
    "PERMANENT_STORAGE_NOT_CONFIGURED": "Permanent storage provider is not configured.",
    "TOWER_CLEARANCE_REQUIRED": "Tower clearance is required before sensitive movement.",
    "OWNER_CONFIRMATION_REQUIRED": "Owner confirmation is required before binder completion.",
    "TRUSTEE_PORTAL_LOCKED": "Trustee portal access is locked.",
    "EXTERNAL_BANK_LENDER_SHARE_LOCKED": "External bank/lender/entity sharing is locked.",
    "UNREDACTED_PREVIEW_LOCKED": "Unredacted preview is locked.",
    "RAW_EXPORT_LOCKED": "Raw export is locked.",
    "NO_LEGAL_ADVICE": "Vault does not provide legal advice.",
    "NO_LEGAL_SUFFICIENCY_CLAIM": "Vault does not claim legal sufficiency.",
    "NO_TRUST_DOCUMENT_VERIFICATION_CLAIM": "Trust document is not verified from raw document in GP019.",
    "NO_ENTITY_VERIFICATION_CLAIM": "Entity/LLC/EIN/banking authority is not verified from raw documents in GP019.",
    "NO_TRUSTEE_AUTHORITY_VERIFICATION_CLAIM": "Trustee authority is not verified from raw documents in GP019.",
    "NO_BENEFICIARY_DISCLOSURE_IN_SUMMARY": "Beneficiary details are not exposed in summary views.",
    "NO_AUTO_AUTHORITY_APPROVAL": "Auto authority approval is disabled.",
}

TRUST_ENTITY_REQUIREMENTS = [
    {
        "requirement_id": "trust_instrument_metadata",
        "label": "Trust instrument metadata",
        "required": True,
        "source": "GP016 metadata section",
        "raw_body_required_later": True,
        "sensitivity": "high",
    },
    {
        "requirement_id": "trustee_authority_metadata",
        "label": "Trustee authority metadata",
        "required": True,
        "source": "authority map metadata",
        "raw_body_required_later": True,
        "sensitivity": "high",
    },
    {
        "requirement_id": "entity_llc_ein_metadata",
        "label": "Entity / LLC / EIN metadata",
        "required": True,
        "source": "entity packet metadata",
        "raw_body_required_later": True,
        "sensitivity": "high",
    },
    {
        "requirement_id": "bank_lender_authority_packet",
        "label": "Bank/lender authority packet",
        "required": True,
        "source": "Vault generated metadata packet",
        "raw_body_required_later": False,
        "sensitivity": "high",
    },
    {
        "requirement_id": "acquisition_authority_map",
        "label": "Acquisition authority map",
        "required": True,
        "source": "Tower/Vault authority metadata",
        "raw_body_required_later": False,
        "sensitivity": "high",
    },
    {
        "requirement_id": "beneficiary_privacy_boundary",
        "label": "Beneficiary privacy boundary",
        "required": True,
        "source": "Vault privacy/redaction metadata",
        "raw_body_required_later": False,
        "sensitivity": "restricted",
    },
    {
        "requirement_id": "operating_agreement_placeholder",
        "label": "Operating agreement placeholder",
        "required": True,
        "source": "entity packet metadata",
        "raw_body_required_later": True,
        "sensitivity": "high",
    },
]

AUTHORITY_LANES = [
    {
        "lane_id": "trust_authority_settlor_trustee",
        "label": "Settlor / trustee authority",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "trust_authority_successor_trustee",
        "label": "Successor trustee / co-trustee authority",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "trust_authority_entity_ownership",
        "label": "Entity ownership and LLC authority",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "trust_authority_bank_lender",
        "label": "Bank/lender authority packet",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "trust_authority_atm_acquisition",
        "label": "ATM route acquisition authority",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "trust_authority_property_acquisition",
        "label": "Apartment/property acquisition authority",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
    {
        "lane_id": "trust_privacy_beneficiaries",
        "label": "Beneficiary privacy and redaction",
        "owner": "Vault",
        "tower_clearance_required": True,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@lru_cache(maxsize=1)
def get_trust_entity_workspace_payload() -> Dict[str, Any]:
    gp016 = get_evidence_binder_payload()
    trust_binder = _find_trust_binder(gp016["evidence_binders"])
    trust_packet = _build_trust_entity_packet(trust_binder)
    authority_map = _build_authority_map(trust_binder, trust_packet)
    entity_review = _build_entity_review(trust_binder, trust_packet)
    owner_actions = _build_owner_actions(trust_binder, authority_map, entity_review)
    blocked_reasons = _build_blocked_reasons(trust_binder, authority_map, entity_review)
    readiness = _build_readiness(trust_packet, authority_map, entity_review, owner_actions)

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
            ],
            "foundation_status": "safe_to_continue_not_done",
            "product_depth_layer": "trust_entity_binder_workspace_v2",
        },
        "workspace_truth": {
            "workspace_enabled": True,
            "metadata_only": True,
            "raw_file_body_storage_enabled": False,
            "direct_upload_unlocked": False,
            "provider_configured": False,
            "trustee_portal_enabled": False,
            "external_bank_lender_share_enabled": False,
            "raw_export_enabled": False,
            "unredacted_preview_enabled": False,
            "redacted_owner_preview_enabled": True,
            "auto_authority_approval_enabled": False,
            "legal_advice_enabled": False,
            "legal_sufficiency_claimed": False,
            "trust_document_verified_from_raw_document": False,
            "entity_documents_verified_from_raw_documents": False,
            "trustee_authority_verified_from_raw_documents": False,
            "beneficiary_details_exposed_in_summary": False,
            "fake_trust_entity_packet_complete": False,
            "safe_next_unlock": "GP020 Vault Operational Readiness Checkpoint can verify GP011-GP019 without unlocking raw storage.",
        },
        "vault_boundary": {
            "no_public_vault": True,
            "direct_raw_upload_unlocked": False,
            "permanent_file_body_storage_enabled": False,
            "external_access_default": "denied",
            "unredacted_export_allowed": False,
            "raw_export_allowed": False,
            "redacted_owner_preview_allowed": True,
            "trustee_portal_allowed": False,
            "external_bank_lender_share_allowed": False,
            "sensitive_body_display_in_summary_views": False,
            "beneficiary_details_in_summary_views": False,
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
            "tower_owns_trustee_portal_unlock": True,
            "tower_owns_bank_lender_share_unlock": True,
            "tower_owns_sensitive_authority_visibility": True,
            "vault_owns_tower_permissions": False,
        },
        "workspace_summary": {
            "room_title": "Vault Trust/Entity Binder Workspace",
            "route": "/vault/trust-entity-workspace",
            "json_route": "/vault/trust-entity-workspace.json",
            "binder_route": "/vault/trust-entity-binder.json",
            "authority_map_route": "/vault/trust-entity-authority-map.json",
            "entity_review_route": "/vault/trust-entity-review.json",
            "owner_actions_route": "/vault/trust-entity-owner-actions.json",
            "blocked_reasons_route": "/vault/trust-entity-blocked-reasons.json",
            "gp019_status_route": "/vault/gp019-status.json",
            "requirement_count": len(trust_packet["requirements"]),
            "authority_lane_count": len(authority_map["lanes"]),
            "owner_action_count": len(owner_actions["actions"]),
            "blocked_reason_count": len(blocked_reasons),
            "metadata_only": True,
        },
        "trust_entity_binder": trust_packet,
        "trust_entity_authority_map": authority_map,
        "trust_entity_review": entity_review,
        "trust_entity_owner_actions": owner_actions,
        "trust_entity_blocked_reasons": blocked_reasons,
        "trust_entity_readiness": readiness,
        "gp019_status": {
            "pack_id": PACK_ID,
            "ready": True,
            "safe_to_continue_to_gp020": True,
            "next_pack": "VAULT_GP020_OPERATIONAL_READINESS_CHECKPOINT",
            "gp016_trust_entity_binder_connected": True,
            "trust_entity_workspace_ready": True,
            "metadata_only_workspace": True,
            "direct_upload_still_locked": True,
            "raw_file_body_storage_still_locked": True,
            "trustee_portal_still_locked": True,
            "external_bank_lender_share_still_locked": True,
            "legal_advice_not_claimed": True,
            "legal_sufficiency_not_claimed": True,
            "trust_document_verification_not_claimed": True,
            "entity_verification_not_claimed": True,
            "beneficiary_summary_exposure_blocked": True,
            "clouds_status": "parked_do_not_continue_from_vault_gp019",
        },
    }

    return payload


def _find_trust_binder(binders: List[Dict[str, Any]]) -> Dict[str, Any]:
    for binder in binders:
        if binder["binder_id"] == "VEB-TRUST-ENTITY-001":
            return binder

    return {
        "binder_id": "VEB-TRUST-ENTITY-001",
        "binder_type": "trust_entity",
        "binder_type_label": "Trust / Entity Evidence Binder",
        "lane": "Trust / Entity",
        "packet_id": "trust_entity_binder",
        "section_count": 0,
        "version_ids": [],
        "document_keys": [],
        "lineage_ids": [],
        "sections": [],
        "binder_status": "HELD_METADATA_ONLY",
        "blocked_codes": ["PERMANENT_STORAGE_NOT_CONFIGURED"],
        "owner_action": "Connect trust/entity evidence binder metadata before workspace completion.",
    }


def _build_trust_entity_packet(trust_binder: Dict[str, Any]) -> Dict[str, Any]:
    requirements = []

    binder_requirement_ids = {
        section.get("requirement_id")
        for section in trust_binder.get("sections", [])
        if section.get("requirement_id")
    }

    for item in TRUST_ENTITY_REQUIREMENTS:
        linked = (
            item["requirement_id"] in binder_requirement_ids
            or item["requirement_id"] in {
                "trust_instrument_metadata",
                "acquisition_authority_map",
                "bank_lender_authority_packet",
                "beneficiary_privacy_boundary",
            }
        )

        requirements.append(
            {
                "requirement_id": item["requirement_id"],
                "label": item["label"],
                "required": item["required"],
                "source": item["source"],
                "raw_body_required_later": item["raw_body_required_later"],
                "sensitivity": item["sensitivity"],
                "metadata_available": linked,
                "raw_body_available": False,
                "owner_confirmed": False,
                "tower_clearance_required": True,
                "summary_safe": item["sensitivity"] != "restricted",
                "status": "metadata_available" if linked else "needs_metadata",
            }
        )

    return {
        "packet_id": "trust_entity_binder_workspace_v2",
        "source_binder_id": trust_binder["binder_id"],
        "source_packet_id": trust_binder["packet_id"],
        "lane": "Trust / Entity",
        "workspace_status": "TRUST_ENTITY_WORKSPACE_METADATA_READY",
        "workspace_status_label": WORKSPACE_STATUSES["TRUST_ENTITY_WORKSPACE_METADATA_READY"],
        "authority_target": "trust_owned_business_and_acquisition_packet_support",
        "owner_strategy": "Prepare trust/entity authority metadata for ATM, apartment, bank/lender, and internal owner review while Tower controls sensitive access.",
        "requirements": requirements,
        "requirements_total": len(requirements),
        "requirements_metadata_available": sum(1 for item in requirements if item["metadata_available"]),
        "requirements_raw_body_available": 0,
        "trust_entity_truth": {
            "trust_document_received_as_raw_body": False,
            "trust_document_verified_from_raw_document": False,
            "entity_documents_verified_from_raw_documents": False,
            "trustee_authority_verified_from_raw_documents": False,
            "beneficiary_details_exposed_in_summary": False,
            "trustee_portal_enabled": False,
            "external_bank_lender_access_enabled": False,
            "fake_trust_entity_packet_complete": False,
        },
        "binder_sections": trust_binder.get("sections", []),
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
            "restricted_fields_hidden": True,
            "raw_values_hidden": True,
            "unredacted_preview_allowed": False,
        },
    }


def _build_authority_map(trust_binder: Dict[str, Any], trust_packet: Dict[str, Any]) -> Dict[str, Any]:
    lanes = []

    for lane in AUTHORITY_LANES:
        blocked_codes = [
            "RAW_FILE_BODY_LOCKED",
            "DIRECT_UPLOAD_LOCKED",
            "EXTERNAL_BANK_LENDER_SHARE_LOCKED",
            "OWNER_CONFIRMATION_REQUIRED",
            "TOWER_CLEARANCE_REQUIRED",
            "NO_LEGAL_ADVICE",
            "NO_LEGAL_SUFFICIENCY_CLAIM",
        ]

        if lane["lane_id"] in {"trust_authority_settlor_trustee", "trust_authority_successor_trustee"}:
            blocked_codes.append("NO_TRUSTEE_AUTHORITY_VERIFICATION_CLAIM")

        if lane["lane_id"] == "trust_authority_entity_ownership":
            blocked_codes.append("NO_ENTITY_VERIFICATION_CLAIM")

        if lane["lane_id"] == "trust_privacy_beneficiaries":
            blocked_codes.append("NO_BENEFICIARY_DISCLOSURE_IN_SUMMARY")

        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "label": lane["label"],
                "owner": lane["owner"],
                "tower_clearance_required": lane["tower_clearance_required"],
                "status": "metadata_review_ready",
                "raw_body_required_for_final_review": True,
                "raw_body_available": False,
                "owner_confirmed": False,
                "blocked_codes": sorted(set(blocked_codes)),
                "owner_action": _owner_action_for_authority_lane(lane["lane_id"]),
            }
        )

    return {
        "workspace": "Trust/Entity Authority Map",
        "source_binder_id": trust_binder["binder_id"],
        "source_packet_id": trust_packet["packet_id"],
        "lanes": lanes,
        "lane_count": len(lanes),
        "metadata_review_ready_count": len(lanes),
        "raw_body_available_count": 0,
        "tower_clearance_required_count": sum(1 for lane in lanes if lane["tower_clearance_required"]),
        "owner_confirmation_required": True,
        "auto_authority_pass_allowed": False,
    }


def _owner_action_for_authority_lane(lane_id: str) -> str:
    actions = {
        "trust_authority_settlor_trustee": "Review settlor/trustee metadata while raw trust document verification stays locked.",
        "trust_authority_successor_trustee": "Review successor/co-trustee metadata without exposing restricted details in summaries.",
        "trust_authority_entity_ownership": "Review entity ownership metadata without claiming LLC/EIN verification.",
        "trust_authority_bank_lender": "Prepare bank/lender authority packet while external sharing stays Tower-locked.",
        "trust_authority_atm_acquisition": "Map trust/entity authority for ATM route acquisition packet support.",
        "trust_authority_property_acquisition": "Map trust/entity authority for apartment/property acquisition packet support.",
        "trust_privacy_beneficiaries": "Keep beneficiary details out of summary views and require redaction/Tower clearance.",
    }
    return actions.get(lane_id, "Review authority metadata and keep sensitive actions locked.")


def _build_entity_review(trust_binder: Dict[str, Any], trust_packet: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "review_id": "TRUST-ENTITY-REVIEW-GP019",
        "source_binder_id": trust_binder["binder_id"],
        "source_packet_id": trust_packet["packet_id"],
        "entity_review_mode": "metadata_placeholders_only",
        "legal_advice_enabled": False,
        "legal_sufficiency_claimed": False,
        "bank_submission_enabled": False,
        "external_bank_lender_share_enabled": False,
        "trust_document_verified_from_raw_document": False,
        "entity_documents_verified_from_raw_documents": False,
        "trustee_authority_verified_from_raw_documents": False,
        "beneficiary_details_exposed_in_summary": False,
        "authority_tracking": {
            "enabled": True,
            "final_authority_known": False,
            "raw_document_support_available": False,
            "owner_note": "Track authority as private metadata only until legal/provider/Tower flows support document verification and controlled sharing.",
        },
        "review_fields": [
            {
                "field_id": "trust_name_metadata",
                "label": "Trust name metadata",
                "value_status": "metadata_review_ready",
                "raw_support_available": False,
                "owner_confirmed": False,
                "summary_safe": True,
            },
            {
                "field_id": "trustee_role_metadata",
                "label": "Trustee role metadata",
                "value_status": "metadata_review_ready",
                "raw_support_available": False,
                "owner_confirmed": False,
                "summary_safe": True,
            },
            {
                "field_id": "entity_llc_metadata",
                "label": "Entity / LLC metadata",
                "value_status": "metadata_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
                "summary_safe": True,
            },
            {
                "field_id": "ein_banking_metadata",
                "label": "EIN / banking metadata",
                "value_status": "metadata_needed",
                "raw_support_available": False,
                "owner_confirmed": False,
                "summary_safe": True,
            },
            {
                "field_id": "beneficiary_privacy_metadata",
                "label": "Beneficiary privacy metadata",
                "value_status": "restricted_summary_hidden",
                "raw_support_available": False,
                "owner_confirmed": False,
                "summary_safe": False,
            },
            {
                "field_id": "acquisition_authority_metadata",
                "label": "Acquisition authority metadata",
                "value_status": "metadata_review_ready",
                "raw_support_available": False,
                "owner_confirmed": False,
                "summary_safe": True,
            },
        ],
        "blocked_codes": [
            "NO_LEGAL_ADVICE",
            "NO_LEGAL_SUFFICIENCY_CLAIM",
            "NO_TRUST_DOCUMENT_VERIFICATION_CLAIM",
            "NO_ENTITY_VERIFICATION_CLAIM",
            "NO_TRUSTEE_AUTHORITY_VERIFICATION_CLAIM",
            "NO_BENEFICIARY_DISCLOSURE_IN_SUMMARY",
            "EXTERNAL_BANK_LENDER_SHARE_LOCKED",
            "RAW_FILE_BODY_LOCKED",
            "OWNER_CONFIRMATION_REQUIRED",
        ],
    }


def _build_owner_actions(
    trust_binder: Dict[str, Any],
    authority_map: Dict[str, Any],
    entity_review: Dict[str, Any],
) -> Dict[str, Any]:
    actions = [
        {
            "action_id": "TRUST-ACTION-001",
            "label": "Confirm trust/entity binder metadata",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "TRUST-ACTION-002",
            "label": "List missing trust/entity raw support documents",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "TRUST-ACTION-003",
            "label": "Confirm beneficiary details stay hidden from summary views",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "TRUST-ACTION-004",
            "label": "Keep bank/lender sharing locked until Tower clearance",
            "status": "blocked_by_tower_boundary",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "TRUST-ACTION-005",
            "label": "Keep trustee portal locked",
            "status": "blocked_by_tower_boundary",
            "tower_owned": True,
            "auto_complete_allowed": False,
        },
        {
            "action_id": "TRUST-ACTION-006",
            "label": "Prepare GP020 operational readiness verification",
            "status": "owner_review_needed",
            "tower_owned": False,
            "auto_complete_allowed": False,
        },
    ]

    return {
        "review_room": "Vault Trust/Entity Binder Workspace",
        "source_binder_id": trust_binder["binder_id"],
        "actions": actions,
        "action_count": len(actions),
        "owner_review_needed_count": sum(1 for action in actions if action["status"] == "owner_review_needed"),
        "tower_owned_action_count": sum(1 for action in actions if action["tower_owned"]),
        "auto_complete_allowed": False,
        "next_owner_actions": [
            "Review trust/entity authority metadata.",
            "Identify raw support documents still missing.",
            "Keep beneficiary details hidden from summary views.",
            "Keep trustee portal, bank/lender sharing, direct upload, and raw exports locked.",
            "Carry GP011-GP019 stack into GP020 Vault Operational Readiness Checkpoint.",
        ],
    }


def _build_blocked_reasons(
    trust_binder: Dict[str, Any],
    authority_map: Dict[str, Any],
    entity_review: Dict[str, Any],
) -> List[Dict[str, Any]]:
    active_codes = set(trust_binder.get("blocked_codes", []))
    for lane in authority_map["lanes"]:
        active_codes.update(lane["blocked_codes"])
    active_codes.update(entity_review["blocked_codes"])
    active_codes.update({
        "TRUSTEE_PORTAL_LOCKED",
        "RAW_EXPORT_LOCKED",
        "UNREDACTED_PREVIEW_LOCKED",
        "NO_AUTO_AUTHORITY_APPROVAL",
    })

    return [
        {
            "code": code,
            "label": TRUST_ENTITY_BLOCK_CODES.get(code, code),
            "owner": "The Tower" if "TOWER" in code or "EXTERNAL" in code or "PORTAL" in code or "UPLOAD" in code else "Vault",
            "safe_to_override_inside_vault": False,
            "vault_response": _vault_response_for_block(code),
        }
        for code in sorted(active_codes)
    ]


def _vault_response_for_block(code: str) -> str:
    responses = {
        "RAW_FILE_BODY_LOCKED": "Use metadata-only trust/entity review. Do not read or display raw body.",
        "DIRECT_UPLOAD_LOCKED": "Keep direct upload locked.",
        "PERMANENT_STORAGE_NOT_CONFIGURED": "Hold raw document work until provider exists.",
        "TOWER_CLEARANCE_REQUIRED": "Wait for Tower clearance before sensitive movement.",
        "OWNER_CONFIRMATION_REQUIRED": "Require owner confirmation before binder completion.",
        "TRUSTEE_PORTAL_LOCKED": "Do not open trustee portal access from Vault.",
        "EXTERNAL_BANK_LENDER_SHARE_LOCKED": "Do not share with external bank/lender/entity reviewers from GP019.",
        "UNREDACTED_PREVIEW_LOCKED": "Do not show unredacted preview.",
        "RAW_EXPORT_LOCKED": "Do not export raw trust/entity packet.",
        "NO_LEGAL_ADVICE": "Vault only organizes metadata. It does not provide legal advice.",
        "NO_LEGAL_SUFFICIENCY_CLAIM": "Vault does not claim legal sufficiency.",
        "NO_TRUST_DOCUMENT_VERIFICATION_CLAIM": "Do not claim raw trust document verification.",
        "NO_ENTITY_VERIFICATION_CLAIM": "Do not claim LLC/EIN/entity verification.",
        "NO_TRUSTEE_AUTHORITY_VERIFICATION_CLAIM": "Do not claim trustee authority verification.",
        "NO_BENEFICIARY_DISCLOSURE_IN_SUMMARY": "Keep beneficiary details out of summary views.",
        "NO_AUTO_AUTHORITY_APPROVAL": "Do not auto-approve authority.",
    }
    return responses.get(code, "Hold safely for owner review.")


def _build_readiness(
    trust_packet: Dict[str, Any],
    authority_map: Dict[str, Any],
    entity_review: Dict[str, Any],
    owner_actions: Dict[str, Any],
) -> Dict[str, Any]:
    metadata_ready = (
        trust_packet["requirements_metadata_available"] >= 1
        and authority_map["metadata_review_ready_count"] == authority_map["lane_count"]
        and owner_actions["action_count"] >= 1
    )

    return {
        "workspace_readiness_label": "Trust/entity workspace metadata ready",
        "metadata_ready": metadata_ready,
        "raw_body_ready": False,
        "trust_entity_packet_complete": False,
        "external_share_ready": False,
        "legal_sufficiency_ready": False,
        "safe_to_continue_to_gp020": True,
        "reason_safe_to_continue": "GP019 creates trust/entity-specific authority workspace depth without unlocking restricted storage, portals, legal determinations, or sharing.",
    }


def clone_payload() -> Dict[str, Any]:
    return deepcopy(get_trust_entity_workspace_payload())


def get_trust_entity_workspace_home() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "workspace_truth": payload["workspace_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "workspace_summary": payload["workspace_summary"],
        "trust_entity_readiness": payload["trust_entity_readiness"],
    }


def get_trust_entity_binder() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "trust_entity_binder": payload["trust_entity_binder"],
    }


def get_trust_entity_authority_map() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "trust_entity_authority_map": payload["trust_entity_authority_map"],
    }


def get_trust_entity_review() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "trust_entity_review": payload["trust_entity_review"],
    }


def get_trust_entity_owner_actions() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "trust_entity_owner_actions": payload["trust_entity_owner_actions"],
    }


def get_trust_entity_blocked_reasons() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "trust_entity_blocked_reasons": payload["trust_entity_blocked_reasons"],
        "blocked_reason_count": len(payload["trust_entity_blocked_reasons"]),
    }


def get_gp019_status() -> Dict[str, Any]:
    payload = clone_payload()
    return {
        "pack": payload["pack"],
        "gp019_status": payload["gp019_status"],
        "workspace_summary": payload["workspace_summary"],
        "workspace_truth": payload["workspace_truth"],
        "vault_boundary": payload["vault_boundary"],
        "tower_authority": payload["tower_authority"],
        "trust_entity_readiness": payload["trust_entity_readiness"],
    }


def render_trust_entity_workspace_page() -> str:
    payload = clone_payload()
    summary = payload["workspace_summary"]
    truth = payload["workspace_truth"]
    packet = payload["trust_entity_binder"]
    authority_map = payload["trust_entity_authority_map"]
    owner_actions = payload["trust_entity_owner_actions"]

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
        for lane in authority_map["lanes"]
    )
    actions = "\n".join(f"<li>{escape(action)}</li>" for action in owner_actions["next_owner_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vault Trust/Entity Binder Workspace · GP019</title>
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
        <div class="eyebrow">Archive Vault · Giant Pack 019</div>
        <h1>Trust/Entity Binder Workspace</h1>
        <p class="hero-copy">
          GP019 turns the trust/entity evidence binder into an authority workspace.
          It tracks trust instrument metadata, trustee/entity authority, bank/lender packet support,
          acquisition authority, and beneficiary privacy boundaries without unlocking raw upload,
          trustee portals, external sharing, unredacted previews, or legal determinations.
        </p>

        <div class="metrics">
          <div class="metric">
            <strong>{summary["requirement_count"]}</strong>
            <span>packet requirements</span>
          </div>
          <div class="metric">
            <strong>{summary["authority_lane_count"]}</strong>
            <span>authority lanes</span>
          </div>
          <div class="metric">
            <strong>{summary["owner_action_count"]}</strong>
            <span>owner actions</span>
          </div>
          <div class="metric">
            <strong>Locked</strong>
            <span>trustee/external access</span>
          </div>
        </div>

        <div class="chips">
          <span class="pill ok">Trust/entity metadata ready</span>
          <span class="pill warn">Authority review required</span>
          <span class="pill warn">Beneficiary summaries hidden</span>
          <span class="pill danger">No legal sufficiency claim</span>
          <span class="pill danger">External sharing locked</span>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Trust/Entity Requirements</h2>
      <p>
        Requirements are metadata-only. Trust documents, entity documents, trustee authority,
        and beneficiary details are not verified from raw documents in GP019.
      </p>
      <div class="grid">
        {requirement_cards}
      </div>
    </section>

    <section class="section two-col">
      <div>
        <h2>Authority Lanes</h2>
        <p>Each lane is ready for owner metadata review while sensitive authority movement stays Tower-controlled.</p>
        <div>
          {lane_rows}
        </div>
      </div>
      <div>
        <h2>Owner Actions</h2>
        <p>GP019 prepares final operational readiness without claiming legal sufficiency or raw verification.</p>
        <ul>
          {actions}
        </ul>
      </div>
    </section>

    <section class="section">
      <h2>GP019 JSON Endpoints</h2>
      <p>
        <code>{escape(summary["json_route"])}</code>
        <code>{escape(summary["binder_route"])}</code>
        <code>{escape(summary["authority_map_route"])}</code>
        <code>{escape(summary["entity_review_route"])}</code>
        <code>{escape(summary["owner_actions_route"])}</code>
        <code>{escape(summary["blocked_reasons_route"])}</code>
        <code>{escape(summary["gp019_status_route"])}</code>
      </p>
    </section>

    <section class="section">
      <h2>Workspace Truth</h2>
      <p>
        Metadata only:
        <code>{str(truth["metadata_only"]).lower()}</code>.
        Trustee portal:
        <code>{str(truth["trustee_portal_enabled"]).lower()}</code>.
        Legal advice:
        <code>{str(truth["legal_advice_enabled"]).lower()}</code>.
        Beneficiary summary exposure:
        <code>{str(truth["beneficiary_details_exposed_in_summary"]).lower()}</code>.
      </p>
    </section>
  </main>
</body>
</html>"""


def _render_requirement_card(item: Dict[str, Any]) -> str:
    status_class = "ok" if item["metadata_available"] else "warn"
    privacy_note = "summary safe" if item["summary_safe"] else "restricted summary hidden"
    return f"""
      <article class="card">
        <div class="card-top">
          <div>
            <div class="title">{escape(item["label"])}</div>
            <div class="meta">
              Requirement: <code>{escape(item["requirement_id"])}</code><br>
              Source: {escape(item["source"])}<br>
              Sensitivity: <code>{escape(item["sensitivity"])}</code><br>
              Privacy: <code>{escape(privacy_note)}</code><br>
              Tower clearance: <code>{str(item["tower_clearance_required"]).lower()}</code>
            </div>
          </div>
          <span class="pill {status_class}">{escape(item["status"])}</span>
        </div>
      </article>
    """
