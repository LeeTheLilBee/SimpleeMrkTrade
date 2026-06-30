"""Vault Giant Pack 004 trust/entity and OB proof vault services.

This pack builds the ownership/proof side of Archive Vault:
- Trust / Entity Packet Vault
- OB Manual Live Proof Vault
- Approval and authority matrix
- Privacy and redaction boundaries
- Owner proof queue
- Clouds-safe trust/OB source

Boundary:
Vault preserves indexes, packet structure, proof chains, approval records,
redacted summaries, and readiness. Vault does not replace attorneys, financial
professionals, brokerage systems, Tower permission authority, or OB execution.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard


TRUST_ENTITY_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "document_id": "trust_instrument_index",
        "label": "Trust instrument index",
        "category": "trust",
        "required": True,
        "sensitivity": "restricted",
        "status": "index_ready_upload_locked",
        "redaction_profile": "trust_max_redaction",
        "approval_roles": ["owner", "trustee", "legal", "tower"],
        "freshness_days": 365,
        "summary": "Tracks the primary trust instrument without exposing full legal body in normal views.",
        "blocked_reason": "direct_upload_locked",
    },
    {
        "document_id": "llc_operating_agreement_index",
        "label": "LLC operating agreement index",
        "category": "entity",
        "required": True,
        "sensitivity": "high",
        "status": "index_ready_upload_locked",
        "redaction_profile": "entity_high_redaction",
        "approval_roles": ["owner", "legal", "tower"],
        "freshness_days": 365,
        "summary": "Tracks entity operating agreements and ownership authority records.",
        "blocked_reason": "direct_upload_locked",
    },
    {
        "document_id": "ein_tax_identity_index",
        "label": "EIN / tax identity index",
        "category": "entity",
        "required": True,
        "sensitivity": "restricted",
        "status": "index_ready_upload_locked",
        "redaction_profile": "tax_identity_redaction",
        "approval_roles": ["owner", "financial", "legal", "tower"],
        "freshness_days": 365,
        "summary": "Tracks EIN and entity tax identity references with restricted visibility.",
        "blocked_reason": "direct_upload_locked",
    },
    {
        "document_id": "bank_account_summary_index",
        "label": "Bank account summary index",
        "category": "financial",
        "required": True,
        "sensitivity": "restricted",
        "status": "summary_only_ready",
        "redaction_profile": "bank_max_redaction",
        "approval_roles": ["owner", "financial", "tower"],
        "freshness_days": 30,
        "summary": "Tracks account existence and lane purpose without exposing account numbers.",
        "blocked_reason": "sensitive_fields_redacted",
    },
    {
        "document_id": "trustee_authority_index",
        "label": "Trustee authority index",
        "category": "authority",
        "required": True,
        "sensitivity": "restricted",
        "status": "index_ready_upload_locked",
        "redaction_profile": "trustee_authority_redaction",
        "approval_roles": ["owner", "trustee", "legal", "tower"],
        "freshness_days": 180,
        "summary": "Tracks trustee roles, successor authority, and approval boundaries.",
        "blocked_reason": "direct_upload_locked",
    },
    {
        "document_id": "beneficiary_summary_redacted_index",
        "label": "Beneficiary summary redacted index",
        "category": "beneficiary",
        "required": True,
        "sensitivity": "restricted",
        "status": "redacted_summary_ready",
        "redaction_profile": "beneficiary_max_redaction",
        "approval_roles": ["owner", "legal", "tower"],
        "freshness_days": 365,
        "summary": "Tracks beneficiary summary in redacted form only.",
        "blocked_reason": "sensitive_fields_redacted",
    },
    {
        "document_id": "mission_account_funding_sequence_index",
        "label": "Mission account funding sequence index",
        "category": "capital_stewardship",
        "required": True,
        "sensitivity": "high",
        "status": "doctrine_ready",
        "redaction_profile": "mission_capital_redaction",
        "approval_roles": ["owner", "tower", "financial"],
        "freshness_days": 30,
        "summary": "Tracks Trust-first funding sequence and mission account disbursement doctrine.",
        "blocked_reason": "financial_review_pending",
    },
]

TRUST_AUTHORITY_MATRIX: List[Dict[str, Any]] = [
    {
        "authority_id": "owner_primary_authority",
        "role": "owner",
        "scope": "Primary owner review, direction, packet approval, and final action intent.",
        "can_view_unredacted": True,
        "requires_step_up": True,
        "can_export": True,
        "tower_clearance_required": True,
    },
    {
        "authority_id": "tower_security_authority",
        "role": "tower",
        "scope": "Identity, permissions, clearance, step-up, export locks, redaction, audit, freeze, revoke.",
        "can_view_unredacted": True,
        "requires_step_up": False,
        "can_export": False,
        "tower_clearance_required": False,
    },
    {
        "authority_id": "trustee_limited_authority",
        "role": "trustee",
        "scope": "Trustee packet review only where owner/Tower permits and the packet requires trustee review.",
        "can_view_unredacted": False,
        "requires_step_up": True,
        "can_export": False,
        "tower_clearance_required": True,
    },
    {
        "authority_id": "legal_review_authority",
        "role": "legal",
        "scope": "Legal document review, entity/trust language review, and restricted approval comments.",
        "can_view_unredacted": False,
        "requires_step_up": True,
        "can_export": False,
        "tower_clearance_required": True,
    },
    {
        "authority_id": "financial_review_authority",
        "role": "financial",
        "scope": "Funding, bank summary, lender, mission account, and acquisition finance review.",
        "can_view_unredacted": False,
        "requires_step_up": True,
        "can_export": False,
        "tower_clearance_required": True,
    },
]

TRUST_APPROVAL_CHAIN: List[Dict[str, Any]] = [
    {
        "step_id": "trust_owner_review",
        "label": "Owner review",
        "required": True,
        "status": "template_ready",
        "receipt_type": "owner_review_receipt",
    },
    {
        "step_id": "trust_tower_clearance",
        "label": "Tower clearance",
        "required": True,
        "status": "template_ready",
        "receipt_type": "tower_clearance_receipt",
    },
    {
        "step_id": "trust_trustee_review",
        "label": "Trustee review when needed",
        "required": True,
        "status": "template_ready",
        "receipt_type": "trustee_review_receipt",
    },
    {
        "step_id": "trust_legal_review",
        "label": "Legal review when needed",
        "required": True,
        "status": "template_ready",
        "receipt_type": "legal_review_receipt",
    },
    {
        "step_id": "trust_freeze_revoke_check",
        "label": "Freeze / revoke / undo check",
        "required": True,
        "status": "template_ready",
        "receipt_type": "revocation_freeze_receipt",
    },
]

OB_PROOF_DOCUMENTS: List[Dict[str, Any]] = [
    {
        "proof_id": "ob_manual_live_alert_receipt",
        "label": "Manual Live alert receipt",
        "proof_type": "alert",
        "required": True,
        "sensitivity": "restricted",
        "status": "template_ready",
        "redaction_profile": "ob_private_proof_redaction",
        "allowed_modes": ["manual_live_level_1"],
        "blocked_fields": ["broker_credentials", "account_number", "order_submit_token"],
        "summary": "Captures OB alert timestamp, symbol, setup summary, mode state, and owner review status.",
    },
    {
        "proof_id": "ob_broker_checklist_receipt",
        "label": "Broker checklist receipt",
        "proof_type": "broker_checklist",
        "required": True,
        "sensitivity": "restricted",
        "status": "template_ready",
        "redaction_profile": "broker_secret_redaction",
        "allowed_modes": ["manual_live_level_1"],
        "blocked_fields": ["broker_credentials", "broker_session", "order_submit_token"],
        "summary": "Captures owner checklist completion without storing broker secrets or direct broker access.",
    },
    {
        "proof_id": "ob_owner_review_note",
        "label": "Owner review note",
        "proof_type": "owner_review",
        "required": True,
        "sensitivity": "high",
        "status": "template_ready",
        "redaction_profile": "owner_note_redaction",
        "allowed_modes": ["manual_live_level_1"],
        "blocked_fields": ["private_personal_notes_unredacted"],
        "summary": "Captures owner decision rationale, risk notes, next action, and final manual decision.",
    },
    {
        "proof_id": "ob_trade_tracking_snapshot",
        "label": "Trade tracking snapshot",
        "proof_type": "tracking",
        "required": True,
        "sensitivity": "restricted",
        "status": "template_ready",
        "redaction_profile": "trade_tracking_redaction",
        "allowed_modes": ["manual_live_level_1"],
        "blocked_fields": ["broker_account_number", "full_position_identifier"],
        "summary": "Captures status tracking after manual broker action without exposing broker account identifiers.",
    },
    {
        "proof_id": "ob_risk_boundary_receipt",
        "label": "Risk boundary receipt",
        "proof_type": "boundary",
        "required": True,
        "sensitivity": "restricted",
        "status": "template_ready",
        "redaction_profile": "risk_boundary_redaction",
        "allowed_modes": ["manual_live_level_1"],
        "blocked_fields": ["execution_secret", "broker_secret"],
        "summary": "Confirms no broker API read, no auto execution, no public proof, Hybrid locked, Automated locked.",
    },
    {
        "proof_id": "ob_no_auto_execution_receipt",
        "label": "No auto-execution receipt",
        "proof_type": "safety",
        "required": True,
        "sensitivity": "restricted",
        "status": "template_ready",
        "redaction_profile": "execution_boundary_redaction",
        "allowed_modes": ["manual_live_level_1"],
        "blocked_fields": ["order_submit_token", "broker_api_key", "broker_secret"],
        "summary": "Preserves the Manual Live Level 1 boundary: OB detects, owner reviews, owner manually acts at broker.",
    },
]

OB_MODE_BOUNDARIES: List[Dict[str, Any]] = [
    {"boundary_id": "no_broker_api_read", "label": "No broker API read", "enforced": True},
    {"boundary_id": "no_broker_order_submit", "label": "No broker order submit", "enforced": True},
    {"boundary_id": "no_auto_execution", "label": "No auto execution", "enforced": True},
    {"boundary_id": "no_public_proof", "label": "No public proof", "enforced": True},
    {"boundary_id": "hybrid_locked", "label": "Hybrid locked", "enforced": True},
    {"boundary_id": "automated_locked", "label": "Automated locked", "enforced": True},
    {"boundary_id": "live_auto_locked", "label": "Live Auto Locked", "enforced": True},
]

OB_APPROVAL_CHAIN: List[Dict[str, Any]] = [
    {
        "step_id": "ob_alert_generated",
        "label": "OB alert generated",
        "required": True,
        "status": "template_ready",
        "receipt_type": "manual_live_alert_receipt",
    },
    {
        "step_id": "ob_owner_reviewed",
        "label": "Owner reviewed alert",
        "required": True,
        "status": "template_ready",
        "receipt_type": "owner_review_receipt",
    },
    {
        "step_id": "ob_broker_checklist_completed",
        "label": "Broker checklist completed manually",
        "required": True,
        "status": "template_ready",
        "receipt_type": "broker_checklist_receipt",
    },
    {
        "step_id": "ob_risk_boundary_confirmed",
        "label": "Risk boundary confirmed",
        "required": True,
        "status": "template_ready",
        "receipt_type": "risk_boundary_receipt",
    },
    {
        "step_id": "ob_tracking_snapshot_saved",
        "label": "Tracking snapshot saved",
        "required": True,
        "status": "template_ready",
        "receipt_type": "trade_tracking_snapshot",
    },
]


def _completion(requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    required_count = sum(1 for item in requirements if item.get("required"))
    ready_count = sum(1 for item in requirements if item.get("status") in {"template_ready", "summary_only_ready", "redacted_summary_ready", "doctrine_ready", "index_ready_upload_locked"})
    return {
        "required_count": required_count,
        "ready_template_count": ready_count,
        "setup_score": 100 if required_count and ready_count == required_count else 0,
        "evidence_attached_score": 0,
        "status": "vault_ready_evidence_locked",
    }


def get_trust_entity_vault_payload() -> Dict[str, Any]:
    readiness = _completion(TRUST_ENTITY_DOCUMENTS)
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "trust_entity_vault",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "vault_id": "vault_trust_entity_packet",
        "vault_name": "Trust / Entity Packet Vault",
        "business_lane": "trust",
        "status": "ready",
        "purpose": "Preserve trust, entity, authority, bank summary, ownership, trustee, beneficiary, and mission funding sequence records with redaction and Tower control.",
        "documents": TRUST_ENTITY_DOCUMENTS,
        "authority_matrix": TRUST_AUTHORITY_MATRIX,
        "approval_chain": TRUST_APPROVAL_CHAIN,
        "readiness": readiness,
        "privacy_boundary": {
            "redaction_default": "maximum",
            "beneficiary_details_hidden": True,
            "bank_account_details_hidden": True,
            "full_legal_body_hidden": True,
            "tower_step_up_required": True,
            "direct_upload_allowed": False,
        },
        "owner_next_action": "Keep the trust/entity packet indexed and ready. Attach actual documents only after Tower storage clearance.",
    }
    return attach_tower_guard(payload, "/vault/trust-entity-vault.json")


def get_ob_manual_live_proof_vault_payload() -> Dict[str, Any]:
    readiness = _completion(OB_PROOF_DOCUMENTS)
    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "ob_manual_live_proof_vault",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "vault_id": "vault_ob_manual_live_proof",
        "vault_name": "OB Manual Live Proof Vault",
        "business_lane": "observatory",
        "status": "ready",
        "purpose": "Preserve private owner-reviewed Manual Live proof without broker secrets, direct broker access, auto execution, or public proof.",
        "proof_documents": OB_PROOF_DOCUMENTS,
        "mode_boundaries": OB_MODE_BOUNDARIES,
        "approval_chain": OB_APPROVAL_CHAIN,
        "readiness": readiness,
        "privacy_boundary": {
            "proof_is_public": False,
            "broker_secrets_allowed": False,
            "broker_api_read_allowed": False,
            "order_submit_allowed": False,
            "auto_execution_allowed": False,
            "redaction_default": "private_proof_redacted",
            "direct_upload_allowed": False,
        },
        "owner_next_action": "When Manual Live Level 1 creates real owner-reviewed records, link alert, checklist, review, boundary, and tracking receipts here.",
    }
    return attach_tower_guard(payload, "/vault/ob-manual-live-proof-vault.json")


def get_trust_ob_owner_queue_payload() -> Dict[str, Any]:
    actions = [
        {
            "action_id": "trust_packet_keep_index_ready",
            "label": "Keep trust/entity packet ready",
            "business_lane": "trust",
            "priority": "high",
            "status": "index_ready_upload_locked",
            "blocked_by": ["direct_upload_locked"],
            "linked_vault": "vault_trust_entity_packet",
            "next_step": "Use the packet as the authority map; upload actual documents only after Tower storage clearance.",
        },
        {
            "action_id": "trust_bank_summary_redaction_check",
            "label": "Confirm bank summary stays redacted",
            "business_lane": "trust",
            "priority": "critical",
            "status": "redaction_boundary_active",
            "blocked_by": ["sensitive_fields_redacted"],
            "linked_vault": "vault_trust_entity_packet",
            "next_step": "Show account purpose and lane only; never expose account numbers in normal views or Clouds.",
        },
        {
            "action_id": "trust_mission_funding_sequence_review",
            "label": "Review mission account funding sequence",
            "business_lane": "trust",
            "priority": "high",
            "status": "doctrine_ready",
            "blocked_by": ["financial_review_pending"],
            "linked_vault": "vault_trust_entity_packet",
            "next_step": "Track Trust-first funding sequence and mission account disbursement doctrine as a Vault record.",
        },
        {
            "action_id": "ob_manual_live_proof_chain_ready",
            "label": "Prepare OB Manual Live proof chain",
            "business_lane": "observatory",
            "priority": "high",
            "status": "template_ready",
            "blocked_by": [],
            "linked_vault": "vault_ob_manual_live_proof",
            "next_step": "Link alert, broker checklist, owner review, risk boundary, no-auto-execution, and tracking receipts when real Manual Live records begin.",
        },
        {
            "action_id": "ob_execution_boundary_lock",
            "label": "Keep OB execution boundary locked",
            "business_lane": "observatory",
            "priority": "critical",
            "status": "boundary_active",
            "blocked_by": ["no_auto_execution", "no_broker_order_submit", "hybrid_locked", "automated_locked"],
            "linked_vault": "vault_ob_manual_live_proof",
            "next_step": "Vault stores proof, not execution. OB Manual Live remains owner-reviewed and manually placed at broker.",
        },
        {
            "action_id": "clouds_trust_ob_summary_ready",
            "label": "Expose trust/OB summary to Clouds later",
            "business_lane": "clouds",
            "priority": "medium",
            "status": "summary_source_ready",
            "blocked_by": [],
            "linked_vault": "clouds_safe_trust_ob_source",
            "next_step": "Clouds can read readiness, blocked reasons, and owner focus without sensitive trust, bank, beneficiary, or broker fields.",
        },
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "trust_ob_owner_queue",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "action_count": len(actions),
        "critical_count": sum(1 for action in actions if action["priority"] == "critical"),
        "high_count": sum(1 for action in actions if action["priority"] == "high"),
        "actions": actions,
    }
    return attach_tower_guard(payload, "/vault/trust-ob-owner-queue.json")


def get_trust_ob_vault_payload() -> Dict[str, Any]:
    trust = get_trust_entity_vault_payload()
    ob = get_ob_manual_live_proof_vault_payload()
    queue = get_trust_ob_owner_queue_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "trust_ob_vault",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "room_label": "Trust + OB Proof Vault",
        "status": "ready",
        "vaults": [
            trust,
            ob,
        ],
        "owner_queue": queue,
        "boundary": {
            "tower_permission_required": True,
            "direct_upload_allowed": False,
            "redaction_default": True,
            "public_proof_allowed": False,
            "broker_secrets_allowed": False,
            "bank_account_details_hidden": True,
            "beneficiary_details_hidden": True,
        },
        "clouds_safe_source": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "summaries": [
                {
                    "vault_id": trust["vault_id"],
                    "vault_name": trust["vault_name"],
                    "business_lane": trust["business_lane"],
                    "status": trust["status"],
                    "setup_score": trust["readiness"]["setup_score"],
                    "document_or_proof_count": len(trust["documents"]),
                    "owner_next_action": trust["owner_next_action"],
                },
                {
                    "vault_id": ob["vault_id"],
                    "vault_name": ob["vault_name"],
                    "business_lane": ob["business_lane"],
                    "status": ob["status"],
                    "setup_score": ob["readiness"]["setup_score"],
                    "document_or_proof_count": len(ob["proof_documents"]),
                    "owner_next_action": ob["owner_next_action"],
                },
            ],
            "hidden_sensitive_fields": sorted(set(REDACTION_POLICY["sensitive_fields"] + [
                "broker_credentials",
                "broker_api_key",
                "order_submit_token",
                "beneficiary_details",
                "bank_account_numbers",
                "full_legal_document_body",
            ])),
            "blocked_reasons": sorted(set(NO_DIRECT_UPLOAD_POLICY["blocked_now"] + [
                "public_proof_blocked",
                "broker_secret_storage_blocked",
                "auto_execution_blocked",
            ])),
        },
        "next_pack_recommendation": "Vault Giant Pack 005 should build Soulaana Artist/IP Package Vault and Private Beta Onboarding Vault.",
    }
    return attach_tower_guard(payload, "/vault/trust-ob-vault.json")


def get_vault_gp004_status_payload() -> Dict[str, Any]:
    trust = get_trust_entity_vault_payload()
    ob = get_ob_manual_live_proof_vault_payload()
    combined = get_trust_ob_vault_payload()

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp004_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 004",
        "built": [
            "trust_entity_packet_vault",
            "trust_authority_matrix",
            "trust_approval_chain",
            "ob_manual_live_proof_vault",
            "ob_mode_boundaries",
            "ob_approval_chain",
            "trust_ob_owner_queue",
            "clouds_safe_trust_ob_source",
            "trust_ob_vault_ui",
        ],
        "trust_document_count": len(trust["documents"]),
        "trust_authority_role_count": len(trust["authority_matrix"]),
        "ob_proof_document_count": len(ob["proof_documents"]),
        "ob_boundary_count": len(ob["mode_boundaries"]),
        "owner_action_count": combined["owner_queue"]["action_count"],
        "trust_setup_score": trust["readiness"]["setup_score"],
        "ob_setup_score": ob["readiness"]["setup_score"],
        "direct_upload_allowed": False,
        "public_proof_allowed": False,
        "broker_secrets_allowed": False,
        "safe_to_continue_to_gp005": True,
    }
    return attach_tower_guard(payload, "/vault/gp004-status.json")
