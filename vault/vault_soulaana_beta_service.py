"""Vault Giant Pack 005 Soulaana/IP and Private Beta vault services.

This pack builds:
- Soulaana Artist/IP Package Vault
- Private Beta Onboarding Vault
- Reserved art slot manifest
- Artist delivery and IP receipt chain
- NDA/invite/access scope beta onboarding records
- Tower-controlled beta access boundary
- Clouds-safe Soulaana/Beta summary source

Important boundary:
No AI-generated depictions of Black women or Soulaana character artwork are
created here. Vault uses reserved art slots, placeholders, manifests, scope
records, and IP/delivery receipt contracts only.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard


SOULAANA_RESERVED_ART_SLOTS: List[Dict[str, Any]] = [
    {
        "slot_id": "soulaana_reserved_slot_primary_symbol",
        "label": "Primary symbol / heraldry slot",
        "slot_type": "reserved_art_slot",
        "status": "reserved_no_ai_art",
        "artist_source": "human_artist_only",
        "allowed_asset_state": "placeholder_or_artist_delivered",
        "blocked_asset_state": "ai_generated_character_art",
        "sensitivity": "restricted",
        "summary": "Reserved for human artist-created Soulaana symbol/heraldry package.",
    },
    {
        "slot_id": "soulaana_reserved_slot_voice_guide_cover",
        "label": "Voice Guide cover slot",
        "slot_type": "reserved_art_slot",
        "status": "reserved_no_ai_art",
        "artist_source": "human_artist_only",
        "allowed_asset_state": "placeholder_or_artist_delivered",
        "blocked_asset_state": "ai_generated_character_art",
        "sensitivity": "restricted",
        "summary": "Reserved for future Soulaana Voice Guide cover art or abstract placeholder.",
    },
    {
        "slot_id": "soulaana_reserved_slot_canon_quotes_cover",
        "label": "100 Canon Quotes cover slot",
        "slot_type": "reserved_art_slot",
        "status": "reserved_no_ai_art",
        "artist_source": "human_artist_only",
        "allowed_asset_state": "placeholder_or_artist_delivered",
        "blocked_asset_state": "ai_generated_character_art",
        "sensitivity": "restricted",
        "summary": "Reserved for future 100 Canon Quotes book cover or abstract placeholder.",
    },
    {
        "slot_id": "soulaana_reserved_slot_delivery_manifest",
        "label": "Artist delivery manifest slot",
        "slot_type": "reserved_manifest_slot",
        "status": "template_ready",
        "artist_source": "human_artist_only",
        "allowed_asset_state": "signed_delivery_manifest",
        "blocked_asset_state": "untracked_delivery",
        "sensitivity": "high",
        "summary": "Tracks delivered pieces, dates, format, usage rights, and owner acceptance.",
    },
]

SOULAANA_PACKAGE_RECORDS: List[Dict[str, Any]] = [
    {
        "record_id": "soulaana_artist_scope_record",
        "label": "Artist scope record",
        "category": "artist_scope",
        "required": True,
        "status": "template_ready",
        "sensitivity": "restricted",
        "redaction_profile": "artist_scope_redaction",
        "blocked_reason": "direct_upload_locked",
        "summary": "Defines what the artist is creating, what is reserved, delivery expectations, and boundaries.",
    },
    {
        "record_id": "soulaana_ip_ownership_terms_record",
        "label": "IP ownership terms record",
        "category": "ip_terms",
        "required": True,
        "status": "template_ready",
        "sensitivity": "restricted",
        "redaction_profile": "ip_terms_redaction",
        "blocked_reason": "legal_review_pending",
        "summary": "Tracks ownership, licensing, usage, exclusivity, modification, and transfer terms.",
    },
    {
        "record_id": "soulaana_payment_receipt_record",
        "label": "Payment receipt record",
        "category": "payment",
        "required": True,
        "status": "template_ready",
        "sensitivity": "high",
        "redaction_profile": "payment_receipt_redaction",
        "blocked_reason": "payment_record_pending",
        "summary": "Tracks payment amount, date, method summary, linked agreement, and owner receipt.",
    },
    {
        "record_id": "soulaana_delivery_receipt_record",
        "label": "Delivery receipt record",
        "category": "delivery",
        "required": True,
        "status": "template_ready",
        "sensitivity": "high",
        "redaction_profile": "delivery_receipt_redaction",
        "blocked_reason": "delivery_pending",
        "summary": "Tracks delivered art package, format, acceptance, revisions, and final delivery state.",
    },
    {
        "record_id": "soulaana_no_ai_art_boundary_record",
        "label": "No AI character art boundary record",
        "category": "creative_boundary",
        "required": True,
        "status": "boundary_active",
        "sensitivity": "restricted",
        "redaction_profile": "creative_boundary_redaction",
        "blocked_reason": "none",
        "summary": "Preserves the boundary that Vault previews use placeholders, silhouettes, symbols, or reserved slots only.",
    },
    {
        "record_id": "soulaana_canon_reference_record",
        "label": "Canon reference record",
        "category": "canon",
        "required": True,
        "status": "doctrine_ready",
        "sensitivity": "restricted",
        "redaction_profile": "canon_reference_redaction",
        "blocked_reason": "none",
        "summary": "Tracks canon references such as message, voice guide, symbol guide, and future canon quote book.",
    },
]

SOULAANA_IP_RECEIPT_CHAIN: List[Dict[str, Any]] = [
    {
        "receipt_id": "soulaana_owner_scope_review_receipt",
        "label": "Owner scope review receipt",
        "receipt_type": "owner_review",
        "status": "template_ready",
        "required": True,
    },
    {
        "receipt_id": "soulaana_artist_agreement_receipt",
        "label": "Artist agreement receipt",
        "receipt_type": "agreement",
        "status": "template_ready",
        "required": True,
    },
    {
        "receipt_id": "soulaana_payment_receipt",
        "label": "Payment receipt",
        "receipt_type": "payment",
        "status": "template_ready",
        "required": True,
    },
    {
        "receipt_id": "soulaana_delivery_manifest_receipt",
        "label": "Delivery manifest receipt",
        "receipt_type": "delivery",
        "status": "template_ready",
        "required": True,
    },
    {
        "receipt_id": "soulaana_ip_boundary_receipt",
        "label": "IP boundary receipt",
        "receipt_type": "ip_boundary",
        "status": "template_ready",
        "required": True,
    },
    {
        "receipt_id": "soulaana_no_ai_art_boundary_receipt",
        "label": "No AI character art boundary receipt",
        "receipt_type": "creative_boundary",
        "status": "active",
        "required": True,
    },
]

BETA_ONBOARDING_RECORDS: List[Dict[str, Any]] = [
    {
        "record_id": "beta_invite_receipt_record",
        "label": "Private beta invite receipt",
        "category": "invite",
        "required": True,
        "status": "template_ready",
        "sensitivity": "medium",
        "redaction_profile": "beta_invite_redaction",
        "blocked_reason": "invite_not_sent",
        "summary": "Tracks invite source, invite scope, invite date, and owner-approved beta access intent.",
    },
    {
        "record_id": "beta_nda_acknowledgment_record",
        "label": "NDA acknowledgment record",
        "category": "nda",
        "required": True,
        "status": "template_ready",
        "sensitivity": "high",
        "redaction_profile": "nda_redaction",
        "blocked_reason": "nda_not_completed",
        "summary": "Tracks NDA status, version, acceptance timestamp, and linked beta tester identity.",
    },
    {
        "record_id": "beta_tower_clearance_snapshot_record",
        "label": "Tower clearance snapshot",
        "category": "tower_clearance",
        "required": True,
        "status": "template_ready",
        "sensitivity": "restricted",
        "redaction_profile": "tower_clearance_redaction",
        "blocked_reason": "tower_clearance_pending",
        "summary": "Tracks Tower-issued access status, role, clearance, expiration, and revocation state.",
    },
    {
        "record_id": "beta_access_scope_record",
        "label": "Access scope record",
        "category": "access_scope",
        "required": True,
        "status": "template_ready",
        "sensitivity": "restricted",
        "redaction_profile": "access_scope_redaction",
        "blocked_reason": "scope_not_granted",
        "summary": "Tracks what rooms, lanes, data, feedback tools, and proof views the beta tester can access.",
    },
    {
        "record_id": "beta_feedback_consent_record",
        "label": "Feedback consent record",
        "category": "feedback",
        "required": True,
        "status": "template_ready",
        "sensitivity": "medium",
        "redaction_profile": "feedback_consent_redaction",
        "blocked_reason": "feedback_consent_pending",
        "summary": "Tracks consent to collect bug reports, feedback, tester notes, and owner review summaries.",
    },
    {
        "record_id": "beta_revocation_freeze_record",
        "label": "Revocation / freeze record",
        "category": "revocation",
        "required": True,
        "status": "template_ready",
        "sensitivity": "restricted",
        "redaction_profile": "revocation_redaction",
        "blocked_reason": "none",
        "summary": "Tracks access removal, freeze, expiration, and undo/reinstate paths controlled by Tower.",
    },
]

BETA_ACCESS_BOUNDARIES: List[Dict[str, Any]] = [
    {"boundary_id": "invite_only", "label": "Invite only", "enforced": True},
    {"boundary_id": "nda_required", "label": "NDA required before access", "enforced": True},
    {"boundary_id": "tower_clearance_required", "label": "Tower clearance required", "enforced": True},
    {"boundary_id": "role_scoped_access", "label": "Role-scoped access only", "enforced": True},
    {"boundary_id": "redacted_default", "label": "Redacted default view", "enforced": True},
    {"boundary_id": "revocation_supported", "label": "Freeze/revoke supported", "enforced": True},
    {"boundary_id": "no_public_beta_routes", "label": "No public beta routes", "enforced": True},
]

BETA_ONBOARDING_FLOW: List[Dict[str, Any]] = [
    {
        "step_id": "beta_owner_invite",
        "label": "Owner invite decision",
        "status": "template_ready",
        "required": True,
        "owning_authority": "owner",
    },
    {
        "step_id": "beta_nda_acknowledgment",
        "label": "NDA acknowledgment",
        "status": "template_ready",
        "required": True,
        "owning_authority": "vault_record_tower_gate",
    },
    {
        "step_id": "beta_tower_clearance",
        "label": "Tower clearance",
        "status": "template_ready",
        "required": True,
        "owning_authority": "tower",
    },
    {
        "step_id": "beta_access_scope",
        "label": "Access scope assignment",
        "status": "template_ready",
        "required": True,
        "owning_authority": "tower",
    },
    {
        "step_id": "beta_feedback_consent",
        "label": "Feedback consent",
        "status": "template_ready",
        "required": True,
        "owning_authority": "vault_record",
    },
    {
        "step_id": "beta_revocation_check",
        "label": "Revocation / expiration check",
        "status": "template_ready",
        "required": True,
        "owning_authority": "tower",
    },
]


def _readiness(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    required = [item for item in items if item.get("required")]
    ready = [
        item for item in required
        if item.get("status") in {
            "template_ready",
            "boundary_active",
            "doctrine_ready",
            "active",
        }
    ]
    return {
        "required_count": len(required),
        "ready_template_count": len(ready),
        "setup_score": 100 if required and len(required) == len(ready) else 0,
        "evidence_attached_score": 0,
        "status": "vault_ready_evidence_locked",
    }


def get_soulaana_artist_ip_vault_payload() -> Dict[str, Any]:
    readiness = _readiness(SOULAANA_PACKAGE_RECORDS)
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "soulaana_artist_ip_vault",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "vault_id": "vault_soulaana_artist_ip_package",
        "vault_name": "Soulaana Artist/IP Package Vault",
        "business_lane": "soulaana",
        "status": "ready",
        "purpose": "Protect Soulaana artist scope, reserved art slots, IP terms, delivery receipts, payment proof, canon references, and no-AI-character-art boundary.",
        "reserved_art_slots": SOULAANA_RESERVED_ART_SLOTS,
        "package_records": SOULAANA_PACKAGE_RECORDS,
        "ip_receipt_chain": SOULAANA_IP_RECEIPT_CHAIN,
        "readiness": readiness,
        "creative_boundary": {
            "human_artist_only": True,
            "ai_generated_black_women_or_soulaana_character_art_allowed": False,
            "allowed_preview_assets": [
                "placeholder",
                "abstract_symbol",
                "reserved_art_slot",
                "artist_delivered_asset_after_acceptance",
            ],
            "blocked_preview_assets": [
                "ai_generated_character_art",
                "ai_generated_black_woman_depiction",
                "untracked_artist_delivery",
            ],
            "direct_upload_allowed": False,
            "redaction_default": "restricted",
        },
        "owner_next_action": "Use reserved slots and manifests only until the human artist package is delivered and accepted through receipts.",
    }
    return attach_tower_guard(payload, "/vault/soulaana-artist-ip-vault.json")


def get_private_beta_onboarding_vault_payload() -> Dict[str, Any]:
    readiness = _readiness(BETA_ONBOARDING_RECORDS)
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "private_beta_onboarding_vault",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "vault_id": "vault_private_beta_onboarding",
        "vault_name": "Private Beta Onboarding Vault",
        "business_lane": "beta",
        "status": "ready",
        "purpose": "Protect private beta invite, NDA, Tower clearance, access scope, feedback consent, revocation, and tester onboarding records.",
        "onboarding_records": BETA_ONBOARDING_RECORDS,
        "access_boundaries": BETA_ACCESS_BOUNDARIES,
        "onboarding_flow": BETA_ONBOARDING_FLOW,
        "readiness": readiness,
        "access_boundary": {
            "invite_only": True,
            "nda_required": True,
            "tower_clearance_required": True,
            "vault_owns_permissions": False,
            "tower_owns_permissions": True,
            "public_beta_routes_allowed": False,
            "direct_upload_allowed": False,
            "redaction_default": "beta_redacted",
        },
        "owner_next_action": "Use this vault when private beta testers are invited; Tower grants access and Vault preserves onboarding proof.",
    }
    return attach_tower_guard(payload, "/vault/private-beta-onboarding-vault.json")


def get_soulaana_beta_owner_queue_payload() -> Dict[str, Any]:
    actions = [
        {
            "action_id": "soulaana_artist_scope_ready",
            "label": "Prepare Soulaana artist scope packet",
            "business_lane": "soulaana",
            "priority": "high",
            "status": "template_ready",
            "blocked_by": ["direct_upload_locked"],
            "linked_vault": "vault_soulaana_artist_ip_package",
            "next_step": "Keep scope, delivery, payment, IP, and reserved art slot records ready for human artist workflow.",
        },
        {
            "action_id": "soulaana_no_ai_character_art_boundary",
            "label": "Keep Soulaana no-AI-character-art boundary active",
            "business_lane": "soulaana",
            "priority": "critical",
            "status": "boundary_active",
            "blocked_by": ["ai_generated_character_art_blocked"],
            "linked_vault": "vault_soulaana_artist_ip_package",
            "next_step": "Use placeholders, abstract symbols, reserved slots, or accepted artist-delivered assets only.",
        },
        {
            "action_id": "soulaana_ip_receipt_chain_ready",
            "label": "Prepare IP and delivery receipt chain",
            "business_lane": "soulaana",
            "priority": "high",
            "status": "template_ready",
            "blocked_by": ["legal_review_pending", "delivery_pending"],
            "linked_vault": "vault_soulaana_artist_ip_package",
            "next_step": "Track owner scope review, artist agreement, payment, delivery, IP boundary, and no-AI-art receipts.",
        },
        {
            "action_id": "beta_invite_packet_ready",
            "label": "Prepare private beta invite packet",
            "business_lane": "beta",
            "priority": "high",
            "status": "template_ready",
            "blocked_by": ["invite_not_sent"],
            "linked_vault": "vault_private_beta_onboarding",
            "next_step": "Use when owner-approved private beta testers are invited.",
        },
        {
            "action_id": "beta_tower_clearance_required",
            "label": "Require Tower clearance before beta access",
            "business_lane": "beta",
            "priority": "critical",
            "status": "boundary_active",
            "blocked_by": ["tower_clearance_pending"],
            "linked_vault": "vault_private_beta_onboarding",
            "next_step": "Do not let Vault issue access. Tower grants clearance, roles, expiration, revoke, and freeze.",
        },
        {
            "action_id": "clouds_soulaana_beta_summary_ready",
            "label": "Expose Soulaana/Beta summary to Clouds later",
            "business_lane": "clouds",
            "priority": "medium",
            "status": "summary_source_ready",
            "blocked_by": [],
            "linked_vault": "clouds_safe_soulaana_beta_source",
            "next_step": "Clouds can read readiness, boundaries, and owner focus without art files, NDA bodies, or sensitive tester details.",
        },
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "soulaana_beta_owner_queue",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "action_count": len(actions),
        "critical_count": sum(1 for action in actions if action["priority"] == "critical"),
        "high_count": sum(1 for action in actions if action["priority"] == "high"),
        "actions": actions,
    }
    return attach_tower_guard(payload, "/vault/soulaana-beta-owner-queue.json")


def get_soulaana_beta_vault_payload() -> Dict[str, Any]:
    soulaana = get_soulaana_artist_ip_vault_payload()
    beta = get_private_beta_onboarding_vault_payload()
    queue = get_soulaana_beta_owner_queue_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "soulaana_beta_vault",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "room_label": "Soulaana + Private Beta Vault",
        "status": "ready",
        "vaults": [
            soulaana,
            beta,
        ],
        "owner_queue": queue,
        "boundary": {
            "tower_permission_required": True,
            "direct_upload_allowed": False,
            "redaction_default": True,
            "public_beta_routes_allowed": False,
            "vault_owns_beta_permissions": False,
            "tower_owns_beta_permissions": True,
            "ai_generated_character_art_allowed": False,
            "reserved_art_slots_only_until_artist_delivery": True,
        },
        "clouds_safe_source": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "summaries": [
                {
                    "vault_id": soulaana["vault_id"],
                    "vault_name": soulaana["vault_name"],
                    "business_lane": soulaana["business_lane"],
                    "status": soulaana["status"],
                    "setup_score": soulaana["readiness"]["setup_score"],
                    "record_count": len(soulaana["package_records"]),
                    "reserved_art_slot_count": len(soulaana["reserved_art_slots"]),
                    "owner_next_action": soulaana["owner_next_action"],
                },
                {
                    "vault_id": beta["vault_id"],
                    "vault_name": beta["vault_name"],
                    "business_lane": beta["business_lane"],
                    "status": beta["status"],
                    "setup_score": beta["readiness"]["setup_score"],
                    "record_count": len(beta["onboarding_records"]),
                    "access_boundary_count": len(beta["access_boundaries"]),
                    "owner_next_action": beta["owner_next_action"],
                },
            ],
            "hidden_sensitive_fields": sorted(set(REDACTION_POLICY["sensitive_fields"] + [
                "artist_payment_details",
                "full_ip_agreement_body",
                "artist_private_contact",
                "beta_tester_private_contact",
                "nda_body",
                "tower_clearance_private_details",
                "unaccepted_artist_delivery_files",
            ])),
            "blocked_reasons": sorted(set(NO_DIRECT_UPLOAD_POLICY["blocked_now"] + [
                "ai_generated_character_art_blocked",
                "public_beta_routes_blocked",
                "vault_permission_authority_blocked",
                "nda_missing_blocks_access",
                "tower_clearance_pending",
            ])),
        },
        "next_pack_recommendation": "Vault Giant Pack 006 should build the Unified Vault Command Center linking all six packet vaults.",
    }
    return attach_tower_guard(payload, "/vault/soulaana-beta-vault.json")


def get_vault_gp005_status_payload() -> Dict[str, Any]:
    soulaana = get_soulaana_artist_ip_vault_payload()
    beta = get_private_beta_onboarding_vault_payload()
    combined = get_soulaana_beta_vault_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp005_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 005",
        "built": [
            "soulaana_artist_ip_package_vault",
            "reserved_art_slot_manifest",
            "soulaana_ip_receipt_chain",
            "no_ai_character_art_boundary",
            "private_beta_onboarding_vault",
            "beta_invite_nda_access_scope_records",
            "beta_tower_clearance_boundary",
            "soulaana_beta_owner_queue",
            "clouds_safe_soulaana_beta_source",
            "soulaana_beta_vault_ui",
        ],
        "soulaana_package_record_count": len(soulaana["package_records"]),
        "soulaana_reserved_art_slot_count": len(soulaana["reserved_art_slots"]),
        "soulaana_receipt_count": len(soulaana["ip_receipt_chain"]),
        "beta_onboarding_record_count": len(beta["onboarding_records"]),
        "beta_access_boundary_count": len(beta["access_boundaries"]),
        "owner_action_count": combined["owner_queue"]["action_count"],
        "soulaana_setup_score": soulaana["readiness"]["setup_score"],
        "beta_setup_score": beta["readiness"]["setup_score"],
        "direct_upload_allowed": False,
        "ai_generated_character_art_allowed": False,
        "vault_owns_beta_permissions": False,
        "safe_to_continue_to_gp006": True,
    }
    return attach_tower_guard(payload, "/vault/gp005-status.json")
