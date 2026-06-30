"""Archive Vault default registry and packet templates."""

from __future__ import annotations

from typing import Dict, List

from .vault_contracts import (
    VAULT_VERSION,
    VaultDocumentRecord,
    VaultPacketTemplate,
    VaultReceiptRecord,
    VaultUniversalId,
)


APP_ID = "archive_vault"
ENTITY_ID = "simplee_world"
ACCOUNT_ID = "owner_control"


DOCUMENT_TYPES: List[Dict[str, object]] = [
    {
        "document_type": "trust_entity_document",
        "label": "Trust / Entity Document",
        "sensitivity": "high",
        "default_lane": "trust",
        "freshness_days": 365,
        "redaction_required": True,
    },
    {
        "document_type": "atm_route_acquisition_document",
        "label": "ATM Route Acquisition Document",
        "sensitivity": "high",
        "default_lane": "atm",
        "freshness_days": 30,
        "redaction_required": True,
    },
    {
        "document_type": "apartment_due_diligence_document",
        "label": "Apartment Due Diligence Document",
        "sensitivity": "high",
        "default_lane": "property",
        "freshness_days": 30,
        "redaction_required": True,
    },
    {
        "document_type": "ob_manual_live_proof_document",
        "label": "OB Manual Live Proof Document",
        "sensitivity": "restricted",
        "default_lane": "observatory",
        "freshness_days": 7,
        "redaction_required": True,
    },
    {
        "document_type": "soulaana_artist_package_document",
        "label": "Soulaana Artist Package Document",
        "sensitivity": "restricted",
        "default_lane": "soulaana",
        "freshness_days": 180,
        "redaction_required": True,
    },
    {
        "document_type": "beta_onboarding_document",
        "label": "Beta Onboarding Document",
        "sensitivity": "medium",
        "default_lane": "beta",
        "freshness_days": 60,
        "redaction_required": True,
    },
]


PACKET_TEMPLATES: List[VaultPacketTemplate] = [
    VaultPacketTemplate(
        packet_id="packet_atm_route_acquisition",
        packet_name="ATM Route Acquisition Packet",
        business_lane="atm",
        owning_app=APP_ID,
        purpose="Collect acquisition, seller, machine, vault cash, site, contract, lender, and owner approval proof for ATM route deals.",
        required_document_types=[
            "seller_summary",
            "route_machine_list",
            "site_contracts",
            "cashflow_statement",
            "vault_cash_plan",
            "loan_preapproval",
            "owner_approval_receipt",
        ],
        required_receipt_types=["owner_review", "tower_clearance", "deal_freeze_check", "funding_decision"],
        approval_chain=["owner", "tower", "trustee", "financial", "legal"],
        readiness_weight=20,
        redaction_profile="deal_room_high_redaction",
    ),
    VaultPacketTemplate(
        packet_id="packet_apartment_lender_due_diligence",
        packet_name="Apartment Lender / Due Diligence Packet",
        business_lane="property",
        owning_app=APP_ID,
        purpose="Collect lender and acquisition diligence for 4-5 building apartment targets.",
        required_document_types=[
            "rent_roll",
            "trailing_12_financials",
            "property_photos",
            "inspection_summary",
            "insurance_quote",
            "loan_terms",
            "entity_ownership_summary",
            "owner_approval_receipt",
        ],
        required_receipt_types=["owner_review", "tower_clearance", "lender_packet_check", "risk_review"],
        approval_chain=["owner", "tower", "trustee", "financial", "legal"],
        readiness_weight=20,
        redaction_profile="property_high_redaction",
    ),
    VaultPacketTemplate(
        packet_id="packet_trust_entity",
        packet_name="Trust / Entity Packet",
        business_lane="trust",
        owning_app=APP_ID,
        purpose="Preserve trust, entity, ownership, operating agreement, and approval proof records.",
        required_document_types=[
            "trust_instrument",
            "llc_operating_agreement",
            "ein_letter",
            "bank_account_summary",
            "trustee_authority_record",
            "beneficiary_summary_redacted",
        ],
        required_receipt_types=["owner_review", "trustee_review", "tower_clearance", "revocation_check"],
        approval_chain=["owner", "tower", "trustee", "legal"],
        readiness_weight=20,
        redaction_profile="trust_max_redaction",
    ),
    VaultPacketTemplate(
        packet_id="packet_ob_manual_live_proof",
        packet_name="OB Manual Live Proof Packet",
        business_lane="observatory",
        owning_app=APP_ID,
        purpose="Preserve Manual Live Level 1 proof without exposing broker credentials, direct broker access, or public proof.",
        required_document_types=[
            "manual_live_alert_receipt",
            "broker_checklist_receipt",
            "owner_review_note",
            "trade_tracking_snapshot",
            "risk_boundary_receipt",
        ],
        required_receipt_types=["owner_review", "tower_mode_gate", "manual_live_boundary", "no_auto_execution_check"],
        approval_chain=["owner", "tower", "compliance"],
        readiness_weight=15,
        redaction_profile="ob_private_proof_redaction",
    ),
    VaultPacketTemplate(
        packet_id="packet_soulaana_artist_package",
        packet_name="Soulaana Artist Package",
        business_lane="soulaana",
        owning_app=APP_ID,
        purpose="Protect Soulaana artist instructions, reserved art slots, IP proof, payment proof, and delivery receipts.",
        required_document_types=[
            "artist_scope",
            "reserved_art_slot_manifest",
            "ip_ownership_terms",
            "payment_receipt",
            "delivery_receipt",
        ],
        required_receipt_types=["owner_review", "ip_boundary_check", "artist_delivery_check"],
        approval_chain=["owner", "tower", "legal"],
        readiness_weight=10,
        redaction_profile="artist_package_redaction",
    ),
    VaultPacketTemplate(
        packet_id="packet_beta_onboarding",
        packet_name="Private Beta Onboarding Packet",
        business_lane="beta",
        owning_app=APP_ID,
        purpose="Collect NDA, invite, Tower clearance, access scope, feedback consent, and tester receipts for private beta.",
        required_document_types=[
            "nda_acknowledgment",
            "invite_receipt",
            "tower_clearance_snapshot",
            "access_scope_record",
            "feedback_consent",
        ],
        required_receipt_types=["tower_clearance", "owner_invite", "access_scope_review", "revocation_check"],
        approval_chain=["owner", "tower"],
        readiness_weight=15,
        redaction_profile="beta_medium_redaction",
    ),
]


SAMPLE_DOCUMENT_RECORDS: List[VaultDocumentRecord] = [
    VaultDocumentRecord(
        document_id="doc_trust_core_placeholder",
        title="Trust Core Document Index",
        document_type="trust_entity_document",
        business_lane="trust",
        owning_app=APP_ID,
        sensitivity="high",
        status="index_ready_upload_locked",
        required_for=["packet_trust_entity", "clouds_owner_snapshot"],
        universal_id=VaultUniversalId(APP_ID, ENTITY_ID, "trust", ACCOUNT_ID, document_id="doc_trust_core_placeholder"),
        allowed_viewers=["owner", "tower", "trustee"],
        linked_receipt_ids=["receipt_vault_gp001_trust_index"],
        summary="Trust and entity document index is ready, but direct file upload remains locked until Tower approves storage.",
        next_action="Attach approved storage provider only after Tower storage clearance exists.",
    ),
    VaultDocumentRecord(
        document_id="doc_ob_manual_live_proof_index",
        title="OB Manual Live Proof Index",
        document_type="ob_manual_live_proof_document",
        business_lane="observatory",
        owning_app=APP_ID,
        sensitivity="restricted",
        status="index_ready_upload_locked",
        required_for=["packet_ob_manual_live_proof", "clouds_owner_snapshot"],
        universal_id=VaultUniversalId(APP_ID, ENTITY_ID, "observatory", ACCOUNT_ID, document_id="doc_ob_manual_live_proof_index"),
        allowed_viewers=["owner", "tower", "compliance"],
        linked_receipt_ids=["receipt_vault_gp001_ob_index"],
        freshness_days=7,
        summary="Manual Live proof index is ready for private receipts without broker secrets or auto-execution exposure.",
        next_action="Link OB receipts once Manual Live Level 1 begins producing live owner-reviewed records.",
    ),
    VaultDocumentRecord(
        document_id="doc_atm_acquisition_index",
        title="ATM Acquisition Index",
        document_type="atm_route_acquisition_document",
        business_lane="atm",
        owning_app=APP_ID,
        sensitivity="high",
        status="index_ready_upload_locked",
        required_for=["packet_atm_route_acquisition", "clouds_owner_snapshot"],
        universal_id=VaultUniversalId(APP_ID, ENTITY_ID, "atm", ACCOUNT_ID, document_id="doc_atm_acquisition_index"),
        allowed_viewers=["owner", "tower", "financial", "legal"],
        linked_receipt_ids=["receipt_vault_gp001_atm_index"],
        summary="ATM acquisition index is ready for route, seller, machine, lender, and vault cash document tracking.",
        next_action="Use this packet when the first two ATM route targets are evaluated.",
    ),
    VaultDocumentRecord(
        document_id="doc_property_acquisition_index",
        title="Apartment Acquisition Index",
        document_type="apartment_due_diligence_document",
        business_lane="property",
        owning_app=APP_ID,
        sensitivity="high",
        status="index_ready_upload_locked",
        required_for=["packet_apartment_lender_due_diligence", "clouds_owner_snapshot"],
        universal_id=VaultUniversalId(APP_ID, ENTITY_ID, "property", ACCOUNT_ID, document_id="doc_property_acquisition_index"),
        allowed_viewers=["owner", "tower", "financial", "legal"],
        linked_receipt_ids=["receipt_vault_gp001_property_index"],
        summary="Apartment acquisition index is ready for lender and due-diligence packet assembly.",
        next_action="Use this packet during parallel apartment search in Manual Live Phase 1.",
    ),
]


SAMPLE_RECEIPTS: List[VaultReceiptRecord] = [
    VaultReceiptRecord(
        receipt_id="receipt_vault_gp001_build",
        receipt_type="build_receipt",
        business_lane="vault",
        owning_app=APP_ID,
        linked_document_ids=[record.document_id for record in SAMPLE_DOCUMENT_RECORDS],
        linked_packet_id="vault_giant_pack_001",
        linked_decision_id="decision_start_vault_before_clouds",
        status="ready",
        actor="owner_build_session",
        summary="Vault Giant Pack 001 created the protected Archive Vault foundation and Clouds source contract.",
    ),
    VaultReceiptRecord(
        receipt_id="receipt_vault_gp001_no_direct_upload",
        receipt_type="security_boundary_receipt",
        business_lane="vault",
        owning_app=APP_ID,
        linked_document_ids=[],
        linked_packet_id="vault_giant_pack_001",
        linked_decision_id="decision_keep_uploads_locked_until_storage_clearance",
        status="active",
        actor="tower_boundary_contract",
        summary="Direct uploads remain blocked until approved storage and Tower permission are connected.",
    ),
]


OPEN_APP_HANDOFFS = [
    {"target_app": "tower", "target_route": "/tower", "purpose": "permission, clearance, role, and mode-gate authority"},
    {"target_app": "observatory", "target_route": "/ob/dashboard", "purpose": "Manual Live proof source and owner review receipts"},
    {"target_app": "clouds", "target_route": "/clouds", "purpose": "owner command dashboard snapshot once Clouds is built"},
    {"target_app": "teller", "target_route": "/teller", "purpose": "future people, payroll, payment, and onboarding packet references"},
]


GLOBAL_SEARCH_SCOPE = [
    "document_id",
    "title",
    "document_type",
    "business_lane",
    "owning_app",
    "status",
    "required_for",
    "linked_asset",
    "linked_contact",
    "linked_decision",
    "linked_receipt_ids",
    "summary",
    "next_action",
]


def get_registry_snapshot() -> Dict[str, object]:
    return {
        "vault_version": VAULT_VERSION,
        "app_id": APP_ID,
        "entity_id": ENTITY_ID,
        "account_id": ACCOUNT_ID,
        "document_types": DOCUMENT_TYPES,
        "packet_templates": [template.to_dict() for template in PACKET_TEMPLATES],
        "sample_document_records": [record.to_dict() for record in SAMPLE_DOCUMENT_RECORDS],
        "sample_receipts": [receipt.to_dict() for receipt in SAMPLE_RECEIPTS],
        "open_app_handoffs": OPEN_APP_HANDOFFS,
        "global_search_scope": GLOBAL_SEARCH_SCOPE,
    }
