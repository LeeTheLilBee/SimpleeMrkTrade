"""Vault Giant Pack 009 Export Lock Console + Redacted Packet Preview.

This pack adds the outward-facing safety layer:
- export lock console
- redacted packet preview
- packet export request queue
- external access review wall
- lender/share/export boundary
- Clouds-safe export summary source

Boundary:
Vault can preview safe summaries and prepare export requests. Vault does not
unlock exports, direct uploads, external sharing, lender sharing, beta sharing,
or unredacted packet bodies without Tower clearance and the required approval chain.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_command_center_service import get_unified_vault_command_center_payload
from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_receipt_control_service import get_approval_chain_console_payload, get_receipt_control_center_payload
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard
from .vault_tracking_service import get_vault_search_tracker_payload


EXPORT_LOCK_RECORDS: List[Dict[str, Any]] = [
    {
        "export_id": "export_atm_lender_packet",
        "label": "ATM lender packet export",
        "business_lane": "atm",
        "target_audience": "lender_or_bank",
        "source_route": "/vault/atm-route-builder.json",
        "approval_chain": "approval_atm_acquisition",
        "status": "locked_pending_target_and_approval",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": True,
        "blocked_reasons": ["target_not_selected", "direct_upload_locked", "tower_step_up_needed"],
        "summary": "ATM packet can be previewed in redacted form, but lender export stays locked until target, evidence, owner approval, and Tower clearance exist.",
    },
    {
        "export_id": "export_property_lender_packet",
        "label": "Apartment lender packet export",
        "business_lane": "property",
        "target_audience": "lender_or_bank",
        "source_route": "/vault/apartment-lender-builder.json",
        "approval_chain": "approval_property_due_diligence",
        "status": "locked_pending_target_and_approval",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": True,
        "blocked_reasons": ["target_not_selected", "lender_not_selected", "direct_upload_locked", "tower_step_up_needed"],
        "summary": "Apartment lender export stays locked until property target, due diligence evidence, owner approval, and Tower clearance exist.",
    },
    {
        "export_id": "export_trust_entity_summary",
        "label": "Trust/entity summary export",
        "business_lane": "trust",
        "target_audience": "legal_financial_lender",
        "source_route": "/vault/trust-entity-vault.json",
        "approval_chain": "approval_trust_entity",
        "status": "locked_sensitive",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": True,
        "blocked_reasons": ["sensitive_fields_redacted", "direct_upload_locked", "legal_review_pending"],
        "summary": "Trust/entity summary can show authority and purpose, but beneficiary, bank, and full legal bodies stay hidden.",
    },
    {
        "export_id": "export_ob_private_proof_packet",
        "label": "OB private proof packet export",
        "business_lane": "observatory",
        "target_audience": "owner_compliance_private_review",
        "source_route": "/vault/ob-manual-live-proof-vault.json",
        "approval_chain": "approval_ob_manual_live_proof",
        "status": "locked_private_proof_only",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": True,
        "blocked_reasons": ["public_proof_blocked", "broker_secret_storage_blocked", "auto_execution_blocked"],
        "summary": "OB proof export is private only and never includes broker secrets, broker API access, order submit authority, or public proof.",
    },
    {
        "export_id": "export_soulaana_artist_ip_packet",
        "label": "Soulaana Artist/IP packet export",
        "business_lane": "soulaana",
        "target_audience": "legal_artist_owner_review",
        "source_route": "/vault/soulaana-artist-ip-vault.json",
        "approval_chain": "approval_soulaana_artist_ip",
        "status": "locked_pending_artist_delivery_and_legal_review",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": True,
        "blocked_reasons": ["direct_upload_locked", "legal_review_pending", "ai_generated_character_art_blocked"],
        "summary": "Soulaana packet export keeps art slots reserved and blocks AI character art; artist/IP records require owner/legal review.",
    },
    {
        "export_id": "export_private_beta_onboarding_packet",
        "label": "Private beta onboarding packet export",
        "business_lane": "beta",
        "target_audience": "owner_tower_private_beta_review",
        "source_route": "/vault/private-beta-onboarding-vault.json",
        "approval_chain": "approval_private_beta_onboarding",
        "status": "locked_pending_invite_nda_tower_clearance",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": True,
        "blocked_reasons": ["invite_not_sent", "nda_missing_blocks_access", "tower_clearance_pending"],
        "summary": "Private beta packet export stays locked until invite, NDA, Tower clearance, role scope, and revocation path exist.",
    },
    {
        "export_id": "export_clouds_vault_summary",
        "label": "Clouds Vault summary source",
        "business_lane": "clouds",
        "target_audience": "clouds_owner_dashboard",
        "source_route": "/vault/command-center.json",
        "approval_chain": "tower_summary_handoff",
        "status": "summary_only_allowed",
        "locked": False,
        "step_up_required": False,
        "tower_clearance_required": True,
        "owner_approval_required": False,
        "redacted_preview_available": True,
        "blocked_reasons": ["unredacted_clouds_display_blocked"],
        "summary": "Clouds may receive summary-only redacted Vault status, counts, readiness, blocked reasons, and owner focus.",
    },
    {
        "export_id": "export_external_party_access",
        "label": "External party access export",
        "business_lane": "vault",
        "target_audience": "external_party",
        "source_route": "/vault/receipt-control-center.json",
        "approval_chain": "tower_external_access_review",
        "status": "locked_by_default",
        "locked": True,
        "step_up_required": True,
        "tower_clearance_required": True,
        "owner_approval_required": True,
        "redacted_preview_available": False,
        "blocked_reasons": ["external_access_not_approved", "tower_step_up_needed", "export_locked"],
        "summary": "External party access is locked by default and requires owner intent, Tower clearance, scope, expiration, and revocation path.",
    },
]


REDACTED_PACKET_PREVIEWS: List[Dict[str, Any]] = [
    {
        "preview_id": "preview_atm_route_packet",
        "label": "ATM Route Acquisition Preview",
        "business_lane": "atm",
        "source_route": "/vault/atm-route-builder.json",
        "preview_status": "redacted_preview_ready",
        "visible_fields": [
            "packet_name",
            "business_lane",
            "machine_count_summary",
            "route_market_summary",
            "required_document_status",
            "owner_next_action",
            "blocked_reasons",
        ],
        "hidden_fields": [
            "seller_private_contact",
            "full_cashflow_statement",
            "processor_details",
            "bank_details",
            "loan_private_terms",
            "raw_site_contract_body",
        ],
        "watermark": "REDACTED ATM PACKET PREVIEW — NOT EXPORT APPROVED",
        "export_allowed": False,
        "owner_next_action": "Choose target, attach evidence after storage clearance, then request approval chain review.",
    },
    {
        "preview_id": "preview_property_lender_packet",
        "label": "Apartment Lender Packet Preview",
        "business_lane": "property",
        "source_route": "/vault/apartment-lender-builder.json",
        "preview_status": "redacted_preview_ready",
        "visible_fields": [
            "packet_name",
            "business_lane",
            "property_summary_placeholder",
            "required_document_status",
            "risk_flags",
            "owner_next_action",
            "blocked_reasons",
        ],
        "hidden_fields": [
            "full_rent_roll",
            "full_t12",
            "tenant_details",
            "bank_details",
            "loan_private_terms",
            "seller_private_contact",
        ],
        "watermark": "REDACTED PROPERTY PACKET PREVIEW — NOT EXPORT APPROVED",
        "export_allowed": False,
        "owner_next_action": "Select property target, collect diligence, then request lender/export approval chain.",
    },
    {
        "preview_id": "preview_trust_entity_packet",
        "label": "Trust / Entity Packet Preview",
        "business_lane": "trust",
        "source_route": "/vault/trust-entity-vault.json",
        "preview_status": "redacted_preview_ready",
        "visible_fields": [
            "packet_name",
            "entity_lane_summary",
            "authority_summary",
            "required_document_status",
            "approval_chain_status",
            "owner_next_action",
        ],
        "hidden_fields": [
            "beneficiary_details",
            "bank_account_numbers",
            "full_legal_document_body",
            "tax_identity_details",
            "trustee_private_contact",
        ],
        "watermark": "REDACTED TRUST/ENTITY PREVIEW — NOT LEGAL EXPORT",
        "export_allowed": False,
        "owner_next_action": "Keep summary redacted until legal/Tower review approves a specific export scope.",
    },
    {
        "preview_id": "preview_ob_manual_live_proof",
        "label": "OB Manual Live Proof Preview",
        "business_lane": "observatory",
        "source_route": "/vault/ob-manual-live-proof-vault.json",
        "preview_status": "private_redacted_preview_ready",
        "visible_fields": [
            "manual_live_level",
            "proof_type_status",
            "owner_review_status",
            "risk_boundary_status",
            "tracking_snapshot_status",
            "blocked_reasons",
        ],
        "hidden_fields": [
            "broker_credentials",
            "broker_account_number",
            "broker_api_key",
            "order_submit_token",
            "full_position_identifier",
            "private_owner_notes_unredacted",
        ],
        "watermark": "PRIVATE OB PROOF PREVIEW — NO AUTO EXECUTION — NO PUBLIC PROOF",
        "export_allowed": False,
        "owner_next_action": "Link real Manual Live receipts only after owner-reviewed live records exist.",
    },
    {
        "preview_id": "preview_soulaana_artist_ip_packet",
        "label": "Soulaana Artist/IP Preview",
        "business_lane": "soulaana",
        "source_route": "/vault/soulaana-artist-ip-vault.json",
        "preview_status": "reserved_slot_preview_ready",
        "visible_fields": [
            "reserved_art_slots",
            "package_record_status",
            "ip_receipt_chain_status",
            "creative_boundary_status",
            "owner_next_action",
        ],
        "hidden_fields": [
            "artist_payment_details",
            "artist_private_contact",
            "full_ip_agreement_body",
            "unaccepted_artist_delivery_files",
            "private_legal_notes",
        ],
        "watermark": "SOULAANA RESERVED SLOT PREVIEW — NO AI CHARACTER ART",
        "export_allowed": False,
        "owner_next_action": "Use reserved slots until human artist delivery is accepted through receipts.",
    },
    {
        "preview_id": "preview_private_beta_onboarding_packet",
        "label": "Private Beta Onboarding Preview",
        "business_lane": "beta",
        "source_route": "/vault/private-beta-onboarding-vault.json",
        "preview_status": "redacted_preview_ready",
        "visible_fields": [
            "invite_status",
            "nda_status",
            "tower_clearance_status",
            "access_scope_status",
            "revocation_status",
            "owner_next_action",
        ],
        "hidden_fields": [
            "beta_tester_private_contact",
            "nda_body",
            "tower_clearance_private_details",
            "feedback_private_notes",
            "tester_identity_sensitive_fields",
        ],
        "watermark": "PRIVATE BETA PREVIEW — TOWER ACCESS REQUIRED",
        "export_allowed": False,
        "owner_next_action": "Use when testers are invited; Tower grants access and Vault preserves onboarding proof.",
    },
]


EXTERNAL_ACCESS_POLICIES: List[Dict[str, Any]] = [
    {
        "policy_id": "external_access_default_deny",
        "label": "External access default deny",
        "status": "active",
        "summary": "No external party receives Vault packet access by default.",
    },
    {
        "policy_id": "external_access_scope_required",
        "label": "External access scope required",
        "status": "active",
        "summary": "Any external viewer must have defined lane, packet, field, expiration, and revocation scope.",
    },
    {
        "policy_id": "external_access_tower_clearance_required",
        "label": "Tower clearance required",
        "status": "active",
        "summary": "Tower must grant access and preserve audit receipt before external viewing.",
    },
    {
        "policy_id": "external_access_redacted_only",
        "label": "Redacted only by default",
        "status": "active",
        "summary": "External previews default to redacted summaries unless owner/Tower approves a narrower exception.",
    },
    {
        "policy_id": "external_access_expiration_required",
        "label": "Expiration required",
        "status": "active",
        "summary": "External access must expire and support freeze/revoke.",
    },
]


def get_export_lock_console_payload() -> Dict[str, Any]:
    approval_console = get_approval_chain_console_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "export_lock_console",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "export_record_count": len(EXPORT_LOCK_RECORDS),
        "locked_export_count": sum(1 for item in EXPORT_LOCK_RECORDS if item["locked"]),
        "summary_allowed_count": sum(1 for item in EXPORT_LOCK_RECORDS if not item["locked"]),
        "step_up_required_count": sum(1 for item in EXPORT_LOCK_RECORDS if item["step_up_required"]),
        "tower_clearance_required_count": sum(1 for item in EXPORT_LOCK_RECORDS if item["tower_clearance_required"]),
        "owner_approval_required_count": sum(1 for item in EXPORT_LOCK_RECORDS if item["owner_approval_required"]),
        "exports": EXPORT_LOCK_RECORDS,
        "approval_chain_count": approval_console["chain_count"],
        "boundary": {
            "exports_locked_by_default": True,
            "direct_upload_allowed": False,
            "unredacted_export_allowed": False,
            "tower_guard_required": True,
            "owner_approval_required_for_sensitive_export": True,
            "clouds_summary_allowed": True,
        },
    }
    return attach_tower_guard(payload, "/vault/export-lock-console.json")


def get_redacted_packet_preview_payload() -> Dict[str, Any]:
    preview_lanes = sorted({preview["business_lane"] for preview in REDACTED_PACKET_PREVIEWS})
    hidden_fields = sorted({field for preview in REDACTED_PACKET_PREVIEWS for field in preview["hidden_fields"]})

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "redacted_packet_preview",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "preview_count": len(REDACTED_PACKET_PREVIEWS),
        "preview_lanes": preview_lanes,
        "hidden_field_count": len(hidden_fields),
        "hidden_fields": hidden_fields,
        "previews": REDACTED_PACKET_PREVIEWS,
        "boundary": {
            "redacted_preview_available": True,
            "unredacted_preview_allowed": False,
            "export_allowed_from_preview": False,
            "watermark_required": True,
            "sensitive_body_hidden": True,
            "clouds_preview_allowed": True,
        },
    }
    return attach_tower_guard(payload, "/vault/redacted-packet-preview.json")


def get_packet_export_request_queue_payload() -> Dict[str, Any]:
    requests = []

    for export in EXPORT_LOCK_RECORDS:
        requests.append(
            {
                "request_id": f"request_{export['export_id']}",
                "export_id": export["export_id"],
                "label": export["label"],
                "business_lane": export["business_lane"],
                "target_audience": export["target_audience"],
                "status": "not_requested" if export["locked"] else "summary_handoff_allowed",
                "approval_chain": export["approval_chain"],
                "blocked_reasons": export["blocked_reasons"],
                "owner_action": "Create request only when target, scope, approval chain, Tower clearance, and redacted preview are ready.",
                "tower_guard_required": export["tower_clearance_required"],
                "owner_approval_required": export["owner_approval_required"],
                "redacted_preview_available": export["redacted_preview_available"],
            }
        )

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "packet_export_request_queue",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "request_count": len(requests),
        "not_requested_count": sum(1 for item in requests if item["status"] == "not_requested"),
        "summary_handoff_allowed_count": sum(1 for item in requests if item["status"] == "summary_handoff_allowed"),
        "requests": requests,
        "boundary": {
            "request_does_not_equal_approval": True,
            "tower_clearance_required": True,
            "approval_chain_required": True,
            "direct_upload_allowed": False,
        },
    }
    return attach_tower_guard(payload, "/vault/packet-export-request-queue.json")


def get_external_access_review_payload() -> Dict[str, Any]:
    export_console = get_export_lock_console_payload()
    review_items = []

    for export in EXPORT_LOCK_RECORDS:
        if export["target_audience"] in {"external_party", "lender_or_bank", "legal_financial_lender", "legal_artist_owner_review"}:
            review_items.append(
                {
                    "review_id": f"external_review_{export['export_id']}",
                    "export_id": export["export_id"],
                    "label": export["label"],
                    "business_lane": export["business_lane"],
                    "target_audience": export["target_audience"],
                    "status": "review_required",
                    "blocked_reasons": export["blocked_reasons"],
                    "required_controls": [
                        "owner_intent",
                        "tower_clearance",
                        "scope_limit",
                        "redacted_preview",
                        "expiration",
                        "revocation_path",
                    ],
                }
            )

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "external_access_review",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "status": "ready",
        "review_item_count": len(review_items),
        "review_items": review_items,
        "policies": EXTERNAL_ACCESS_POLICIES,
        "policy_count": len(EXTERNAL_ACCESS_POLICIES),
        "locked_export_count": export_console["locked_export_count"],
        "boundary": {
            "external_access_default_deny": True,
            "tower_clearance_required": True,
            "expiration_required": True,
            "revocation_supported": True,
            "redacted_only_by_default": True,
        },
    }
    return attach_tower_guard(payload, "/vault/external-access-review.json")


def get_export_preview_center_payload() -> Dict[str, Any]:
    command = get_unified_vault_command_center_payload()
    tracking = get_vault_search_tracker_payload()
    receipt_control = get_receipt_control_center_payload()
    export_console = get_export_lock_console_payload()
    previews = get_redacted_packet_preview_payload()
    request_queue = get_packet_export_request_queue_payload()
    external_review = get_external_access_review_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "export_preview_center",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "room_label": "Vault Export Lock + Redacted Preview Center",
        "status": "ready",
        "export_lock_console": {
            "export_record_count": export_console["export_record_count"],
            "locked_export_count": export_console["locked_export_count"],
            "summary_allowed_count": export_console["summary_allowed_count"],
            "step_up_required_count": export_console["step_up_required_count"],
            "tower_clearance_required_count": export_console["tower_clearance_required_count"],
            "owner_approval_required_count": export_console["owner_approval_required_count"],
        },
        "redacted_packet_preview": {
            "preview_count": previews["preview_count"],
            "preview_lanes": previews["preview_lanes"],
            "hidden_field_count": previews["hidden_field_count"],
        },
        "packet_export_request_queue": {
            "request_count": request_queue["request_count"],
            "not_requested_count": request_queue["not_requested_count"],
            "summary_handoff_allowed_count": request_queue["summary_handoff_allowed_count"],
        },
        "external_access_review": {
            "review_item_count": external_review["review_item_count"],
            "policy_count": external_review["policy_count"],
        },
        "command_center_summary": {
            "lane_count": command["lane_count"],
            "route_count": command["route_count"],
            "owner_action_count": command["owner_action_count"],
        },
        "tracking_summary": {
            "record_count": tracking["search_index"]["record_count"],
            "requirement_count": tracking["requirement_tracker"]["requirement_count"],
            "blocked_count": tracking["requirement_tracker"]["blocked_count"],
        },
        "receipt_control_summary": {
            "receipt_count": receipt_control["receipt_chain_console"]["receipt_count"],
            "approval_chain_count": receipt_control["approval_chain_console"]["chain_count"],
            "control_rule_count": receipt_control["freeze_revoke_undo_wall"]["rule_count"],
        },
        "boundary": {
            "exports_locked_by_default": True,
            "direct_upload_allowed": False,
            "unredacted_export_allowed": False,
            "external_access_default_deny": True,
            "tower_guard_required": True,
            "redacted_preview_only": True,
            "clouds_view": "summary_only_redacted",
        },
        "clouds_safe_source": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "export_record_count": export_console["export_record_count"],
            "locked_export_count": export_console["locked_export_count"],
            "preview_count": previews["preview_count"],
            "request_count": request_queue["request_count"],
            "external_review_item_count": external_review["review_item_count"],
            "hidden_sensitive_fields": sorted(set(REDACTION_POLICY["sensitive_fields"] + previews["hidden_fields"])),
            "blocked_reasons": sorted(set(NO_DIRECT_UPLOAD_POLICY["blocked_now"] + [
                "export_locked",
                "external_access_not_approved",
                "unredacted_export_blocked",
                "tower_step_up_needed",
            ])),
        },
        "next_pack_recommendation": "Vault Giant Pack 010 should build Final Vault Readiness Checkpoint + Clouds handoff contract.",
    }
    return attach_tower_guard(payload, "/vault/export-preview-center.json")


def get_vault_gp009_status_payload() -> Dict[str, Any]:
    center = get_export_preview_center_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp009_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 009",
        "built": [
            "export_lock_console",
            "redacted_packet_preview",
            "packet_export_request_queue",
            "external_access_review",
            "clouds_safe_export_source",
            "export_preview_center_ui",
            "gp009_status_endpoint",
        ],
        "export_record_count": center["export_lock_console"]["export_record_count"],
        "locked_export_count": center["export_lock_console"]["locked_export_count"],
        "redacted_preview_count": center["redacted_packet_preview"]["preview_count"],
        "export_request_count": center["packet_export_request_queue"]["request_count"],
        "external_review_item_count": center["external_access_review"]["review_item_count"],
        "direct_upload_allowed": False,
        "unredacted_export_allowed": False,
        "external_access_default_deny": True,
        "clouds_safe": center["clouds_safe_source"]["safe_for_clouds"],
        "safe_to_continue_to_gp010": True,
    }
    return attach_tower_guard(payload, "/vault/gp009-status.json")
