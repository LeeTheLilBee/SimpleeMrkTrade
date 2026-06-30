"""Vault Giant Pack 008 Receipt Chain Console + Freeze/Revoke/Undo Wall.

This pack adds the control/proof layer over the Vault foundation:
- unified receipt chain console
- approval chain console
- freeze / revoke / undo wall
- receipt timeline
- blocked decision review
- Clouds-safe receipt/control source

Boundary:
Vault can preserve receipts, approval intent, freeze/revoke/undo states, and
control summaries. Vault does not become Tower, does not approve legal/financial
items, does not unlock direct upload, and does not expose sensitive document bodies.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_command_center_service import get_unified_vault_command_center_payload
from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard
from .vault_tracking_service import get_requirement_tracker_payload, get_vault_search_tracker_payload


RECEIPT_CHAIN_RECORDS: List[Dict[str, Any]] = [
    {
        "receipt_id": "receipt_vault_gp001_build",
        "label": "Vault GP001 build receipt",
        "receipt_type": "build",
        "business_lane": "vault",
        "source_pack": "gp001",
        "source_route": "/vault/status.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "archive_vault_core_foundation",
        "approval_scope": "foundation_contracts",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Archive Vault core foundation, contracts, packet templates, and Tower boundary created.",
    },
    {
        "receipt_id": "receipt_vault_gp002_room",
        "label": "Vault GP002 room receipt",
        "receipt_type": "build",
        "business_lane": "vault",
        "source_pack": "gp002",
        "source_route": "/vault/room.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "vault_room_interface",
        "approval_scope": "room_interface",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Vault room, packet board, document drawer, owner queue, and Clouds preview created.",
    },
    {
        "receipt_id": "receipt_vault_gp003_acquisition",
        "label": "Vault GP003 acquisition builders receipt",
        "receipt_type": "build",
        "business_lane": "atm_property",
        "source_pack": "gp003",
        "source_route": "/vault/acquisition-builders.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "acquisition_builders",
        "approval_scope": "atm_property_packet_builders",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "ATM route and apartment lender packet builders created.",
    },
    {
        "receipt_id": "receipt_vault_gp004_trust_ob",
        "label": "Vault GP004 trust and OB proof receipt",
        "receipt_type": "build",
        "business_lane": "trust_observatory",
        "source_pack": "gp004",
        "source_route": "/vault/trust-ob-vault.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "trust_ob_vaults",
        "approval_scope": "trust_entity_and_ob_private_proof",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Trust/entity packet vault and OB Manual Live private proof vault created.",
    },
    {
        "receipt_id": "receipt_vault_gp005_soulaana_beta",
        "label": "Vault GP005 Soulaana and beta receipt",
        "receipt_type": "build",
        "business_lane": "soulaana_beta",
        "source_pack": "gp005",
        "source_route": "/vault/soulaana-beta-vault.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "soulaana_beta_vaults",
        "approval_scope": "artist_ip_and_private_beta_onboarding",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Soulaana Artist/IP vault and Private Beta onboarding vault created.",
    },
    {
        "receipt_id": "receipt_vault_gp006_command_center",
        "label": "Vault GP006 command center receipt",
        "receipt_type": "build",
        "business_lane": "vault",
        "source_pack": "gp006",
        "source_route": "/vault/command-center.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "unified_vault_command_center",
        "approval_scope": "six_lane_command_foundation",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Unified six-lane Vault command center created.",
    },
    {
        "receipt_id": "receipt_vault_gp007_search_tracker",
        "label": "Vault GP007 search and tracker receipt",
        "receipt_type": "build",
        "business_lane": "vault",
        "source_pack": "gp007",
        "source_route": "/vault/search-tracker.json",
        "status": "active",
        "actor": "owner_build_session",
        "linked_object": "search_requirement_expiration_freshness",
        "approval_scope": "tracking_layer",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Vault search, requirement tracker, expiration wall, and freshness wall created.",
    },
    {
        "receipt_id": "receipt_tower_guard_boundary",
        "label": "Tower guard boundary receipt",
        "receipt_type": "security_boundary",
        "business_lane": "vault",
        "source_pack": "gp001_gp008",
        "source_route": "/vault/command-center.json",
        "status": "active",
        "actor": "tower_boundary_contract",
        "linked_object": "tower_permission_authority",
        "approval_scope": "identity_clearance_permissions_step_up",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Tower remains the authority for identity, permissions, clearance, step-up, export locks, freeze, revoke, and audit.",
    },
    {
        "receipt_id": "receipt_no_direct_upload_boundary",
        "label": "No direct upload boundary receipt",
        "receipt_type": "security_boundary",
        "business_lane": "vault",
        "source_pack": "gp001_gp008",
        "source_route": "/vault/no-direct-upload.json",
        "status": "active",
        "actor": "tower_boundary_contract",
        "linked_object": "direct_upload_lock",
        "approval_scope": "storage_malware_retention_permission_boundary",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Direct uploads remain locked until Tower-approved storage, scanning, retention, and permissions exist.",
    },
    {
        "receipt_id": "receipt_redacted_view_boundary",
        "label": "Redacted view boundary receipt",
        "receipt_type": "privacy_boundary",
        "business_lane": "vault",
        "source_pack": "gp001_gp008",
        "source_route": "/vault/redacted-view-policy.json",
        "status": "active",
        "actor": "vault_privacy_contract",
        "linked_object": "redacted_view_policy",
        "approval_scope": "sensitive_field_visibility",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Vault defaults to redacted views and Clouds gets summary-only data.",
    },
    {
        "receipt_id": "receipt_ob_no_auto_execution_boundary",
        "label": "OB no-auto-execution boundary receipt",
        "receipt_type": "execution_boundary",
        "business_lane": "observatory",
        "source_pack": "gp004_gp008",
        "source_route": "/vault/ob-manual-live-proof-vault.json",
        "status": "active",
        "actor": "ob_vault_boundary",
        "linked_object": "manual_live_level_1_boundary",
        "approval_scope": "no_broker_api_no_order_submit_no_auto_execution",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "OB Manual Live proof is private and does not unlock broker API read, order submit, or automated execution.",
    },
    {
        "receipt_id": "receipt_soulaana_no_ai_character_art_boundary",
        "label": "Soulaana no-AI-character-art boundary receipt",
        "receipt_type": "creative_boundary",
        "business_lane": "soulaana",
        "source_pack": "gp005_gp008",
        "source_route": "/vault/soulaana-artist-ip-vault.json",
        "status": "active",
        "actor": "creative_boundary_contract",
        "linked_object": "reserved_art_slots",
        "approval_scope": "human_artist_only_reserved_art_slots",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": False,
        "summary": "Vault uses placeholders, symbols, manifests, and reserved slots only until human artist delivery.",
    },
    {
        "receipt_id": "receipt_beta_tower_access_boundary",
        "label": "Private beta Tower access boundary receipt",
        "receipt_type": "access_boundary",
        "business_lane": "beta",
        "source_pack": "gp005_gp008",
        "source_route": "/vault/private-beta-onboarding-vault.json",
        "status": "active",
        "actor": "tower_boundary_contract",
        "linked_object": "private_beta_access",
        "approval_scope": "invite_nda_tower_clearance_role_scope_revoke",
        "revocation_status": "active",
        "freeze_status": "not_frozen",
        "undo_available": True,
        "summary": "Private beta access requires invite, NDA, Tower clearance, role scope, expiration, and revocation path.",
    },
]


APPROVAL_CHAIN_RECORDS: List[Dict[str, Any]] = [
    {
        "chain_id": "approval_atm_acquisition",
        "label": "ATM acquisition approval chain",
        "business_lane": "atm",
        "required_roles": ["owner", "tower", "trustee", "financial", "legal"],
        "status": "template_ready",
        "source_route": "/vault/atm-route-builder.json",
        "export_locked": True,
        "step_up_required": True,
        "summary": "Used before route acquisition packet export, lender review, or purchase decision.",
    },
    {
        "chain_id": "approval_property_due_diligence",
        "label": "Apartment lender due diligence approval chain",
        "business_lane": "property",
        "required_roles": ["owner", "tower", "trustee", "financial", "legal"],
        "status": "template_ready",
        "source_route": "/vault/apartment-lender-builder.json",
        "export_locked": True,
        "step_up_required": True,
        "summary": "Used before lender packet export, due diligence decision, or property acquisition action.",
    },
    {
        "chain_id": "approval_trust_entity",
        "label": "Trust/entity approval chain",
        "business_lane": "trust",
        "required_roles": ["owner", "tower", "trustee", "legal"],
        "status": "template_ready",
        "source_route": "/vault/trust-entity-vault.json",
        "export_locked": True,
        "step_up_required": True,
        "summary": "Used for trust/entity records, authority, ownership summaries, and sensitive legal documents.",
    },
    {
        "chain_id": "approval_ob_manual_live_proof",
        "label": "OB Manual Live proof approval chain",
        "business_lane": "observatory",
        "required_roles": ["owner", "tower", "compliance"],
        "status": "template_ready",
        "source_route": "/vault/ob-manual-live-proof-vault.json",
        "export_locked": True,
        "step_up_required": True,
        "summary": "Used for Manual Live proof receipts while preserving no-auto-execution and no-public-proof boundaries.",
    },
    {
        "chain_id": "approval_soulaana_artist_ip",
        "label": "Soulaana Artist/IP approval chain",
        "business_lane": "soulaana",
        "required_roles": ["owner", "tower", "legal"],
        "status": "template_ready",
        "source_route": "/vault/soulaana-artist-ip-vault.json",
        "export_locked": True,
        "step_up_required": True,
        "summary": "Used for artist scope, IP terms, payment receipt, delivery receipt, and reserved art slot acceptance.",
    },
    {
        "chain_id": "approval_private_beta_onboarding",
        "label": "Private beta onboarding approval chain",
        "business_lane": "beta",
        "required_roles": ["owner", "tower"],
        "status": "template_ready",
        "source_route": "/vault/private-beta-onboarding-vault.json",
        "export_locked": True,
        "step_up_required": True,
        "summary": "Used for invite, NDA, Tower clearance, access scope, feedback consent, and revocation proof.",
    },
]


FREEZE_REVOKE_UNDO_RULES: List[Dict[str, Any]] = [
    {
        "rule_id": "freeze_direct_upload_unlock",
        "label": "Freeze direct upload unlock",
        "business_lane": "vault",
        "control_type": "freeze",
        "status": "active",
        "trigger": "Any attempt to enable raw direct upload before Tower storage clearance.",
        "effect": "Block upload action and route owner to Tower storage clearance review.",
        "undo_allowed": False,
        "tower_required": True,
    },
    {
        "rule_id": "freeze_unredacted_clouds_display",
        "label": "Freeze unredacted Clouds display",
        "business_lane": "clouds",
        "control_type": "freeze",
        "status": "active",
        "trigger": "Any attempt to send sensitive fields to Clouds.",
        "effect": "Clouds receives summary-only redacted source map.",
        "undo_allowed": False,
        "tower_required": True,
    },
    {
        "rule_id": "revoke_beta_access",
        "label": "Revoke private beta access",
        "business_lane": "beta",
        "control_type": "revoke",
        "status": "template_ready",
        "trigger": "Owner or Tower revokes beta invite, NDA, clearance, or access scope.",
        "effect": "Freeze beta access, preserve revocation receipt, and remove scoped access through Tower.",
        "undo_allowed": True,
        "tower_required": True,
    },
    {
        "rule_id": "freeze_ob_auto_execution_path",
        "label": "Freeze OB auto-execution path",
        "business_lane": "observatory",
        "control_type": "freeze",
        "status": "active",
        "trigger": "Any attempt to treat Vault proof as broker execution authority.",
        "effect": "Block automation path and preserve Manual Live Level 1 proof boundary.",
        "undo_allowed": False,
        "tower_required": True,
    },
    {
        "rule_id": "freeze_public_proof_publish",
        "label": "Freeze public proof publishing",
        "business_lane": "observatory",
        "control_type": "freeze",
        "status": "active",
        "trigger": "Any attempt to publish OB proof publicly.",
        "effect": "Keep proof private and owner/Tower controlled.",
        "undo_allowed": False,
        "tower_required": True,
    },
    {
        "rule_id": "freeze_ai_character_art_preview",
        "label": "Freeze AI Soulaana character art preview",
        "business_lane": "soulaana",
        "control_type": "freeze",
        "status": "active",
        "trigger": "Any attempt to add AI-generated Soulaana/Black woman character artwork.",
        "effect": "Use placeholder, abstract symbol, reserved slot, or accepted human-artist asset only.",
        "undo_allowed": False,
        "tower_required": False,
    },
    {
        "rule_id": "revoke_lender_packet_export",
        "label": "Revoke lender packet export",
        "business_lane": "property",
        "control_type": "revoke",
        "status": "template_ready",
        "trigger": "Owner, Tower, legal, or financial review blocks packet export.",
        "effect": "Freeze export, preserve blocked decision reason, and require re-review.",
        "undo_allowed": True,
        "tower_required": True,
    },
    {
        "rule_id": "revoke_atm_deal_room_access",
        "label": "Revoke ATM deal room access",
        "business_lane": "atm",
        "control_type": "revoke",
        "status": "template_ready",
        "trigger": "Seller, lender, or external party access becomes stale, unsafe, or no longer approved.",
        "effect": "Remove external access through Tower and preserve revocation receipt.",
        "undo_allowed": True,
        "tower_required": True,
    },
    {
        "rule_id": "undo_owner_packet_draft",
        "label": "Undo owner packet draft",
        "business_lane": "vault",
        "control_type": "undo",
        "status": "template_ready",
        "trigger": "Owner wants to roll back a draft packet note before export or formal approval.",
        "effect": "Preserve prior version and restore previous draft state.",
        "undo_allowed": True,
        "tower_required": False,
    },
]


def _receipt_summary() -> Dict[str, int]:
    return {
        "receipt_count": len(RECEIPT_CHAIN_RECORDS),
        "active_count": sum(1 for item in RECEIPT_CHAIN_RECORDS if item["status"] == "active"),
        "undo_available_count": sum(1 for item in RECEIPT_CHAIN_RECORDS if item["undo_available"]),
        "frozen_count": sum(1 for item in RECEIPT_CHAIN_RECORDS if item["freeze_status"] == "frozen"),
        "revoked_count": sum(1 for item in RECEIPT_CHAIN_RECORDS if item["revocation_status"] == "revoked"),
    }


def get_receipt_chain_console_payload() -> Dict[str, Any]:
    summary = _receipt_summary()
    receipt_types = sorted({item["receipt_type"] for item in RECEIPT_CHAIN_RECORDS})
    lanes = sorted({item["business_lane"] for item in RECEIPT_CHAIN_RECORDS})

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "receipt_chain_console",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        **summary,
        "receipt_types": receipt_types,
        "business_lanes": lanes,
        "receipts": RECEIPT_CHAIN_RECORDS,
        "boundary": {
            "receipts_are_private": True,
            "redacted_view_default": True,
            "direct_upload_allowed": False,
            "tower_guard_required": True,
            "clouds_view": "summary_only_redacted",
        },
    }
    return attach_tower_guard(payload, "/vault/receipt-chain-console.json")


def get_approval_chain_console_payload() -> Dict[str, Any]:
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "approval_chain_console",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "chain_count": len(APPROVAL_CHAIN_RECORDS),
        "chains": APPROVAL_CHAIN_RECORDS,
        "role_count": len(sorted({role for chain in APPROVAL_CHAIN_RECORDS for role in chain["required_roles"]})),
        "export_locked_count": sum(1 for chain in APPROVAL_CHAIN_RECORDS if chain["export_locked"]),
        "step_up_required_count": sum(1 for chain in APPROVAL_CHAIN_RECORDS if chain["step_up_required"]),
        "boundary": {
            "vault_records_approval_chain": True,
            "tower_enforces_roles": True,
            "vault_owns_permissions": False,
            "exports_locked_by_default": True,
        },
    }
    return attach_tower_guard(payload, "/vault/approval-chain-console.json")


def get_freeze_revoke_undo_wall_payload() -> Dict[str, Any]:
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "freeze_revoke_undo_wall",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "rule_count": len(FREEZE_REVOKE_UNDO_RULES),
        "active_rule_count": sum(1 for rule in FREEZE_REVOKE_UNDO_RULES if rule["status"] == "active"),
        "template_rule_count": sum(1 for rule in FREEZE_REVOKE_UNDO_RULES if rule["status"] == "template_ready"),
        "undo_allowed_count": sum(1 for rule in FREEZE_REVOKE_UNDO_RULES if rule["undo_allowed"]),
        "tower_required_count": sum(1 for rule in FREEZE_REVOKE_UNDO_RULES if rule["tower_required"]),
        "rules": FREEZE_REVOKE_UNDO_RULES,
        "control_types": sorted({rule["control_type"] for rule in FREEZE_REVOKE_UNDO_RULES}),
        "boundary": {
            "freeze_supported": True,
            "revoke_supported": True,
            "undo_supported_for_safe_drafts": True,
            "dangerous_unlocks_have_no_undo": True,
            "tower_required_for_access_controls": True,
        },
    }
    return attach_tower_guard(payload, "/vault/freeze-revoke-undo-wall.json")


def get_blocked_decision_review_payload() -> Dict[str, Any]:
    command = get_unified_vault_command_center_payload()
    requirements = get_requirement_tracker_payload()
    tracker = get_vault_search_tracker_payload()

    blocked_decisions: List[Dict[str, Any]] = []

    for reason in command["boundary_wall"]["blocked_reasons"]:
        blocked_decisions.append(
            {
                "blocked_decision_id": f"blocked_{reason}",
                "blocked_reason": reason,
                "source": "boundary_wall",
                "status": "active",
                "owner_action": "Review only if owner intentionally wants to change the boundary. Default is keep blocked.",
                "tower_required": True,
            }
        )

    for item in requirements["requirements"]:
        if item["blocked_reason"] not in {"none", ""}:
            blocked_decisions.append(
                {
                    "blocked_decision_id": f"blocked_req_{item['requirement_id']}",
                    "blocked_reason": item["blocked_reason"],
                    "source": item["source_route"],
                    "business_lane": item["business_lane"],
                    "status": item["status"],
                    "owner_action": "Attach evidence or resolve prerequisite only after Tower clearance and owner review.",
                    "tower_required": item["tower_guard_required"],
                }
            )

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "blocked_decision_review",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "blocked_decision_count": len(blocked_decisions),
        "blocked_decisions": blocked_decisions,
        "search_tracker_record_count": tracker["search_index"]["record_count"],
        "boundary": {
            "default_action": "keep_blocked",
            "owner_can_review": True,
            "tower_required_for_unlock": True,
            "dangerous_unlocks_blocked": True,
        },
    }
    return attach_tower_guard(payload, "/vault/blocked-decision-review.json")


def get_receipt_control_center_payload() -> Dict[str, Any]:
    receipts = get_receipt_chain_console_payload()
    approvals = get_approval_chain_console_payload()
    freeze_wall = get_freeze_revoke_undo_wall_payload()
    blocked_review = get_blocked_decision_review_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "receipt_control_center",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "room_label": "Vault Receipt Chain + Control Center",
        "status": "ready",
        "receipt_chain_console": {
            "receipt_count": receipts["receipt_count"],
            "active_count": receipts["active_count"],
            "undo_available_count": receipts["undo_available_count"],
            "frozen_count": receipts["frozen_count"],
            "revoked_count": receipts["revoked_count"],
            "receipt_types": receipts["receipt_types"],
            "business_lanes": receipts["business_lanes"],
        },
        "approval_chain_console": {
            "chain_count": approvals["chain_count"],
            "role_count": approvals["role_count"],
            "export_locked_count": approvals["export_locked_count"],
            "step_up_required_count": approvals["step_up_required_count"],
        },
        "freeze_revoke_undo_wall": {
            "rule_count": freeze_wall["rule_count"],
            "active_rule_count": freeze_wall["active_rule_count"],
            "template_rule_count": freeze_wall["template_rule_count"],
            "undo_allowed_count": freeze_wall["undo_allowed_count"],
            "tower_required_count": freeze_wall["tower_required_count"],
            "control_types": freeze_wall["control_types"],
        },
        "blocked_decision_review": {
            "blocked_decision_count": blocked_review["blocked_decision_count"],
            "default_action": blocked_review["boundary"]["default_action"],
        },
        "boundary": {
            "tower_guard_required": True,
            "vault_owns_permissions": False,
            "direct_upload_allowed": False,
            "redacted_view_default": True,
            "clouds_view": "summary_only_redacted",
            "dangerous_unlocks_default_blocked": True,
        },
        "clouds_safe_source": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "receipt_count": receipts["receipt_count"],
            "approval_chain_count": approvals["chain_count"],
            "control_rule_count": freeze_wall["rule_count"],
            "blocked_decision_count": blocked_review["blocked_decision_count"],
            "hidden_sensitive_fields": REDACTION_POLICY["sensitive_fields"],
            "blocked_reasons": NO_DIRECT_UPLOAD_POLICY["blocked_now"],
        },
        "next_pack_recommendation": "Vault Giant Pack 009 should build Export Lock Console + Redacted Packet Preview.",
    }
    return attach_tower_guard(payload, "/vault/receipt-control-center.json")


def get_vault_gp008_status_payload() -> Dict[str, Any]:
    center = get_receipt_control_center_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp008_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 008",
        "built": [
            "receipt_chain_console",
            "approval_chain_console",
            "freeze_revoke_undo_wall",
            "blocked_decision_review",
            "clouds_safe_receipt_control_source",
            "receipt_control_center_ui",
            "gp008_status_endpoint",
        ],
        "receipt_count": center["receipt_chain_console"]["receipt_count"],
        "approval_chain_count": center["approval_chain_console"]["chain_count"],
        "control_rule_count": center["freeze_revoke_undo_wall"]["rule_count"],
        "blocked_decision_count": center["blocked_decision_review"]["blocked_decision_count"],
        "direct_upload_allowed": False,
        "vault_owns_permissions": False,
        "clouds_safe": center["clouds_safe_source"]["safe_for_clouds"],
        "safe_to_continue_to_gp009": True,
    }
    return attach_tower_guard(payload, "/vault/gp008-status.json")
