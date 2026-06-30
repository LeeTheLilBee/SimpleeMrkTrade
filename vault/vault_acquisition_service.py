"""Vault Giant Pack 003 acquisition packet builders.

This pack builds the aggressive money-side Vault layer:
- ATM Route Acquisition Packet Builder
- Apartment Lender / Due Diligence Packet Builder
- Owner acquisition queue
- Clouds-safe acquisition source

Important boundary:
Vault can structure packets, requirements, readiness, receipts, and redacted
summaries. Vault does not approve loans, replace legal/financial review, unlock
direct upload, or own Tower permissions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .vault_contracts import VAULT_VERSION, utc_now_iso
from .vault_security import NO_DIRECT_UPLOAD_POLICY, REDACTION_POLICY, attach_tower_guard


ATM_TARGET_INTAKE_FIELDS: List[Dict[str, Any]] = [
    {"field_id": "seller_name", "label": "Seller / broker name", "required": True, "sensitivity": "medium"},
    {"field_id": "route_location_market", "label": "Route market / city / state", "required": True, "sensitivity": "medium"},
    {"field_id": "machine_count", "label": "Machine count", "required": True, "sensitivity": "low"},
    {"field_id": "asking_price", "label": "Asking price", "required": True, "sensitivity": "high"},
    {"field_id": "monthly_gross_volume", "label": "Monthly gross withdrawal volume", "required": True, "sensitivity": "high"},
    {"field_id": "monthly_net_income", "label": "Monthly net income", "required": True, "sensitivity": "high"},
    {"field_id": "vault_cash_required", "label": "Estimated vault cash required", "required": True, "sensitivity": "high"},
    {"field_id": "site_contract_status", "label": "Site contract status", "required": True, "sensitivity": "high"},
    {"field_id": "processor_status", "label": "Processor / ISO status", "required": True, "sensitivity": "restricted"},
    {"field_id": "lender_needed", "label": "Loan or seller financing needed", "required": True, "sensitivity": "high"},
]

ATM_DOCUMENT_REQUIREMENTS: List[Dict[str, Any]] = [
    {
        "requirement_id": "atm_seller_summary",
        "label": "Seller summary",
        "category": "seller",
        "required": True,
        "readiness_weight": 8,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "target_not_selected",
        "notes": "Seller identity, sale reason, included assets, and contact channel.",
    },
    {
        "requirement_id": "atm_route_machine_list",
        "label": "Route machine list",
        "category": "asset",
        "required": True,
        "readiness_weight": 10,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "target_not_selected",
        "notes": "Machine count, model, age, condition, location, ownership, and replacement risk.",
    },
    {
        "requirement_id": "atm_site_contracts",
        "label": "Site contracts / placement agreements",
        "category": "legal",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "direct_upload_locked",
        "notes": "Placement terms, revocation risk, owner contact, split terms, and expiration.",
    },
    {
        "requirement_id": "atm_cashflow_statement",
        "label": "Cashflow statement",
        "category": "financial",
        "required": True,
        "readiness_weight": 14,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "target_not_selected",
        "notes": "Revenue, surcharge split, processing fees, rent/share, service cost, net cashflow.",
    },
    {
        "requirement_id": "atm_processor_statement",
        "label": "Processor statements",
        "category": "processor",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "direct_upload_locked",
        "notes": "Processor proof, transaction volume, uptime, dispute issues, and settlement timing.",
    },
    {
        "requirement_id": "atm_vault_cash_plan",
        "label": "Vault cash plan",
        "category": "funding",
        "required": True,
        "readiness_weight": 14,
        "evidence_attached": False,
        "status": "template_ready",
        "blocked_reason": "funding_source_pending",
        "notes": "Loan should account for vault cash need, working capital, and replenishment schedule.",
    },
    {
        "requirement_id": "atm_loan_preapproval",
        "label": "Loan / funding preapproval",
        "category": "funding",
        "required": True,
        "readiness_weight": 10,
        "evidence_attached": False,
        "status": "awaiting_lender",
        "blocked_reason": "lender_not_selected",
        "notes": "Packet should show route economics, vault cash, owner equity, and repayment plan.",
    },
    {
        "requirement_id": "atm_owner_approval_receipt",
        "label": "Owner approval receipt",
        "category": "approval",
        "required": True,
        "readiness_weight": 10,
        "evidence_attached": False,
        "status": "template_ready",
        "blocked_reason": "owner_review_not_started",
        "notes": "Owner decision, review timestamp, freeze/undo path, and linked Tower clearance.",
    },
    {
        "requirement_id": "atm_tower_clearance_receipt",
        "label": "Tower clearance receipt",
        "category": "security",
        "required": True,
        "readiness_weight": 10,
        "evidence_attached": False,
        "status": "template_ready",
        "blocked_reason": "tower_step_up_needed",
        "notes": "Tower clearance for sensitive deal room, exports, and lender packet viewing.",
    },
]

PROPERTY_TARGET_INTAKE_FIELDS: List[Dict[str, Any]] = [
    {"field_id": "property_name", "label": "Property / package name", "required": True, "sensitivity": "medium"},
    {"field_id": "market", "label": "Market / city / state", "required": True, "sensitivity": "medium"},
    {"field_id": "building_count", "label": "Building count", "required": True, "sensitivity": "low"},
    {"field_id": "unit_count", "label": "Unit count", "required": True, "sensitivity": "low"},
    {"field_id": "asking_price", "label": "Asking price", "required": True, "sensitivity": "high"},
    {"field_id": "occupancy", "label": "Occupancy", "required": True, "sensitivity": "high"},
    {"field_id": "monthly_gross_rent", "label": "Monthly gross rent", "required": True, "sensitivity": "high"},
    {"field_id": "monthly_operating_expenses", "label": "Monthly operating expenses", "required": True, "sensitivity": "high"},
    {"field_id": "loan_type", "label": "Loan type / lender path", "required": True, "sensitivity": "high"},
    {"field_id": "property_manager_status", "label": "Property manager status", "required": False, "sensitivity": "medium"},
]

PROPERTY_DOCUMENT_REQUIREMENTS: List[Dict[str, Any]] = [
    {
        "requirement_id": "property_rent_roll",
        "label": "Rent roll",
        "category": "income",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "target_not_selected",
        "notes": "Unit, tenant, rent, lease date, deposit, delinquency, vacancy, and concessions.",
    },
    {
        "requirement_id": "property_t12_financials",
        "label": "Trailing 12 financials",
        "category": "financial",
        "required": True,
        "readiness_weight": 14,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "target_not_selected",
        "notes": "Income, expenses, repairs, utilities, taxes, insurance, payroll, management, NOI.",
    },
    {
        "requirement_id": "property_photos",
        "label": "Property photos / condition evidence",
        "category": "condition",
        "required": True,
        "readiness_weight": 8,
        "evidence_attached": False,
        "status": "awaiting_target",
        "blocked_reason": "direct_upload_locked",
        "notes": "Exterior, units, systems, roof, parking, common areas, deferred maintenance.",
    },
    {
        "requirement_id": "property_inspection_summary",
        "label": "Inspection summary",
        "category": "condition",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "awaiting_inspection",
        "blocked_reason": "inspection_not_ordered",
        "notes": "Inspection findings, repairs, severity, budget, safety, lender-required fixes.",
    },
    {
        "requirement_id": "property_insurance_quote",
        "label": "Insurance quote",
        "category": "risk",
        "required": True,
        "readiness_weight": 8,
        "evidence_attached": False,
        "status": "awaiting_quote",
        "blocked_reason": "insurance_quote_missing",
        "notes": "Coverage, premium, deductible, exclusions, replacement cost, lender requirements.",
    },
    {
        "requirement_id": "property_loan_terms",
        "label": "Loan terms / lender worksheet",
        "category": "funding",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "awaiting_lender",
        "blocked_reason": "lender_not_selected",
        "notes": "Loan amount, down payment, rate, amortization, term, reserves, covenants.",
    },
    {
        "requirement_id": "property_entity_ownership_summary",
        "label": "Entity ownership summary",
        "category": "ownership",
        "required": True,
        "readiness_weight": 10,
        "evidence_attached": False,
        "status": "template_ready",
        "blocked_reason": "direct_upload_locked",
        "notes": "Trust/entity ownership, authority, signing authority, and lender-facing summary.",
    },
    {
        "requirement_id": "property_owner_approval_receipt",
        "label": "Owner approval receipt",
        "category": "approval",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "template_ready",
        "blocked_reason": "owner_review_not_started",
        "notes": "Owner decision, review timestamp, risk notes, freeze/undo path, linked Tower clearance.",
    },
    {
        "requirement_id": "property_tower_clearance_receipt",
        "label": "Tower clearance receipt",
        "category": "security",
        "required": True,
        "readiness_weight": 12,
        "evidence_attached": False,
        "status": "template_ready",
        "blocked_reason": "tower_step_up_needed",
        "notes": "Tower clearance for lender packet exports, sensitive data visibility, and redacted views.",
    },
]

ATM_RISK_FLAGS: List[Dict[str, Any]] = [
    {"flag_id": "atm_site_contract_expiration", "label": "Site contract near expiration", "severity": "high"},
    {"flag_id": "atm_machine_age_unknown", "label": "Machine age or ownership unclear", "severity": "medium"},
    {"flag_id": "atm_processor_dependency", "label": "Processor/ISO dependency unclear", "severity": "high"},
    {"flag_id": "atm_vault_cash_underestimated", "label": "Vault cash requirement underestimated", "severity": "critical"},
    {"flag_id": "atm_volume_unverified", "label": "Withdrawal volume not independently verified", "severity": "high"},
    {"flag_id": "atm_repair_cost_unknown", "label": "Repair/replacement cost unknown", "severity": "medium"},
]

PROPERTY_RISK_FLAGS: List[Dict[str, Any]] = [
    {"flag_id": "property_occupancy_unverified", "label": "Occupancy not verified", "severity": "high"},
    {"flag_id": "property_t12_missing", "label": "T12 missing or incomplete", "severity": "critical"},
    {"flag_id": "property_deferred_maintenance", "label": "Deferred maintenance unclear", "severity": "high"},
    {"flag_id": "property_insurance_unknown", "label": "Insurance quote missing", "severity": "high"},
    {"flag_id": "property_lender_reserves", "label": "Lender reserves not confirmed", "severity": "medium"},
    {"flag_id": "property_management_gap", "label": "Property manager not identified", "severity": "medium"},
]


def _requirement_summary(requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_weight = sum(item["readiness_weight"] for item in requirements)
    attached_weight = sum(item["readiness_weight"] for item in requirements if item["evidence_attached"])
    required_count = sum(1 for item in requirements if item["required"])
    attached_count = sum(1 for item in requirements if item["evidence_attached"])

    return {
        "required_document_count": required_count,
        "evidence_attached_count": attached_count,
        "total_weight": total_weight,
        "attached_weight": attached_weight,
        "packet_completion_score": int(round((attached_weight / total_weight) * 100)) if total_weight else 0,
        "builder_setup_score": 100,
        "status": "builder_ready_packet_empty" if attached_count == 0 else "packet_in_progress",
    }


def _safe_clouds_summary(builder: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "builder_id": builder["builder_id"],
        "builder_name": builder["builder_name"],
        "business_lane": builder["business_lane"],
        "status": builder["status"],
        "builder_setup_score": builder["readiness"]["builder_setup_score"],
        "packet_completion_score": builder["readiness"]["packet_completion_score"],
        "required_document_count": builder["readiness"]["required_document_count"],
        "risk_flag_count": len(builder["risk_flags"]),
        "next_owner_action": builder["owner_next_action"],
    }


def get_atm_route_builder_payload() -> Dict[str, Any]:
    readiness = _requirement_summary(ATM_DOCUMENT_REQUIREMENTS)
    builder = {
        "builder_id": "builder_atm_route_acquisition",
        "builder_name": "ATM Route Acquisition Packet Builder",
        "business_lane": "atm",
        "packet_id": "packet_atm_route_acquisition",
        "status": readiness["status"],
        "purpose": "Build a lender/owner-ready packet for buying ATM routes, including route economics, site contracts, machines, processor proof, vault cash, and approval receipts.",
        "target_intake_fields": ATM_TARGET_INTAKE_FIELDS,
        "required_documents": ATM_DOCUMENT_REQUIREMENTS,
        "risk_flags": ATM_RISK_FLAGS,
        "readiness": readiness,
        "approval_chain": ["owner", "tower", "trustee", "financial", "legal"],
        "vault_cash_plan_fields": [
            "starting_vault_cash_needed",
            "cash_replenishment_frequency",
            "cash_source",
            "cash_transport_method",
            "insurance_or_risk_control",
            "emergency_cash_buffer",
        ],
        "route_economics_fields": [
            "asking_price",
            "monthly_gross_volume",
            "monthly_surcharge_income",
            "processor_fees",
            "site_commissions",
            "service_costs",
            "estimated_monthly_net",
            "estimated_payback_period",
        ],
        "owner_questions": [
            "Does this route create enough net cashflow after vault cash, service, processor, and site split costs?",
            "Are site contracts transferable and long enough to protect the purchase?",
            "Are machine condition, processor relationship, and cash replenishment logistics verified?",
            "Can loan structure include vault cash and working capital without choking the business?",
        ],
        "owner_next_action": "When first route targets are chosen, enter target facts and attach approved records after Tower storage clearance.",
        "direct_upload_allowed": False,
        "redacted_view_default": True,
        "storage_provider": "not_connected",
    }

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "atm_route_builder",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "builder": builder,
    }
    return attach_tower_guard(payload, "/vault/atm-route-builder.json")


def get_apartment_lender_builder_payload() -> Dict[str, Any]:
    readiness = _requirement_summary(PROPERTY_DOCUMENT_REQUIREMENTS)
    builder = {
        "builder_id": "builder_apartment_lender_due_diligence",
        "builder_name": "Apartment Lender / Due Diligence Packet Builder",
        "business_lane": "property",
        "packet_id": "packet_apartment_lender_due_diligence",
        "status": readiness["status"],
        "purpose": "Build lender and owner due-diligence packets for 4-5 building apartment acquisition targets.",
        "target_intake_fields": PROPERTY_TARGET_INTAKE_FIELDS,
        "required_documents": PROPERTY_DOCUMENT_REQUIREMENTS,
        "risk_flags": PROPERTY_RISK_FLAGS,
        "readiness": readiness,
        "approval_chain": ["owner", "tower", "trustee", "financial", "legal"],
        "lender_packet_fields": [
            "borrower_or_entity_summary",
            "property_summary",
            "purchase_price",
            "down_payment_source",
            "loan_request",
            "rent_roll_summary",
            "t12_summary",
            "insurance_quote",
            "inspection_summary",
            "management_plan",
            "reserve_plan",
        ],
        "due_diligence_fields": [
            "rent_roll_validation",
            "expense_validation",
            "maintenance_risk",
            "lease_audit",
            "insurance_review",
            "tax_review",
            "capex_budget",
            "property_management_plan",
        ],
        "owner_questions": [
            "Does the property support the loan after expenses, reserves, insurance, repairs, and management?",
            "Is the rent roll verified against deposits, leases, and occupancy?",
            "Are repairs and deferred maintenance priced before lender review?",
            "Does the trust/entity ownership packet clearly support signing authority and lender paperwork?",
        ],
        "owner_next_action": "Use this builder during parallel apartment search and attach target records only after Tower storage clearance.",
        "direct_upload_allowed": False,
        "redacted_view_default": True,
        "storage_provider": "not_connected",
    }

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "apartment_lender_builder",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "builder": builder,
    }
    return attach_tower_guard(payload, "/vault/apartment-lender-builder.json")


def get_acquisition_owner_queue_payload() -> Dict[str, Any]:
    atm = get_atm_route_builder_payload()["builder"]
    property_builder = get_apartment_lender_builder_payload()["builder"]

    actions = [
        {
            "action_id": "acq_owner_choose_first_atm_targets",
            "label": "Choose first ATM route targets",
            "business_lane": "atm",
            "priority": "high",
            "status": "ready_for_owner_research",
            "linked_builder": atm["builder_id"],
            "blocked_by": [],
            "next_step": "Collect seller summary, route machine list, monthly volume, site terms, and vault cash estimate.",
        },
        {
            "action_id": "acq_owner_confirm_atm_vault_cash_path",
            "label": "Confirm ATM vault cash funding path",
            "business_lane": "atm",
            "priority": "critical",
            "status": "needs_financial_review",
            "linked_builder": atm["builder_id"],
            "blocked_by": ["funding_source_pending"],
            "next_step": "Keep vault cash plan visible in the packet so loan/funding conversations include working cash needs.",
        },
        {
            "action_id": "acq_owner_start_apartment_target_watch",
            "label": "Start apartment target watch list",
            "business_lane": "property",
            "priority": "high",
            "status": "ready_for_owner_research",
            "linked_builder": property_builder["builder_id"],
            "blocked_by": [],
            "next_step": "Track 4-5 building opportunities and require rent roll, T12, insurance, inspection, and lender terms.",
        },
        {
            "action_id": "acq_owner_prepare_lender_packet_shell",
            "label": "Prepare apartment lender packet shell",
            "business_lane": "property",
            "priority": "high",
            "status": "template_ready",
            "linked_builder": property_builder["builder_id"],
            "blocked_by": ["target_not_selected"],
            "next_step": "Use this shell once a specific property target is selected.",
        },
        {
            "action_id": "acq_owner_keep_upload_locked",
            "label": "Keep acquisition uploads locked until Tower storage clearance",
            "business_lane": "vault",
            "priority": "critical",
            "status": "locked_boundary_active",
            "linked_builder": "vault_storage_clearance",
            "blocked_by": ["direct_upload_locked", "upload_provider_not_approved"],
            "next_step": "Do not unlock raw file upload until storage, scanning, retention, redaction, and permissions are approved.",
        },
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "acquisition_owner_queue",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "action_count": len(actions),
        "critical_count": sum(1 for action in actions if action["priority"] == "critical"),
        "high_count": sum(1 for action in actions if action["priority"] == "high"),
        "actions": actions,
    }
    return attach_tower_guard(payload, "/vault/acquisition-owner-queue.json")


def get_acquisition_builders_payload() -> Dict[str, Any]:
    atm_payload = get_atm_route_builder_payload()
    property_payload = get_apartment_lender_builder_payload()
    queue = get_acquisition_owner_queue_payload()

    builders = [
        atm_payload["builder"],
        property_payload["builder"],
    ]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "acquisition_builders",
        "generated_at": utc_now_iso(),
        "public_access": False,
        "room_label": "Acquisition Builders",
        "status": "ready",
        "builder_count": len(builders),
        "builders": builders,
        "owner_queue": queue,
        "boundary": {
            "direct_upload_allowed": False,
            "storage_provider": "not_connected",
            "redacted_view_default": True,
            "tower_permission_required": True,
            "not_financial_or_legal_approval": True,
        },
        "clouds_safe_source": {
            "safe_for_clouds": True,
            "view": "summary_only_redacted",
            "builder_summaries": [_safe_clouds_summary(builder) for builder in builders],
            "hidden_sensitive_fields": REDACTION_POLICY["sensitive_fields"],
            "blocked_reasons": NO_DIRECT_UPLOAD_POLICY["blocked_now"],
        },
        "next_pack_recommendation": "Vault Giant Pack 004 should build Trust/Entity packet vault and OB Manual Live proof vault.",
    }
    return attach_tower_guard(payload, "/vault/acquisition-builders.json")


def get_vault_gp003_status_payload() -> Dict[str, Any]:
    builders = get_acquisition_builders_payload()
    atm = get_atm_route_builder_payload()["builder"]
    property_builder = get_apartment_lender_builder_payload()["builder"]

    payload = {
        "app_id": "archive_vault",
        "version": VAULT_VERSION,
        "payload_type": "vault_gp003_status",
        "generated_at": utc_now_iso(),
        "status": "ready",
        "pack": "Vault Giant Pack 003",
        "built": [
            "atm_route_acquisition_packet_builder",
            "apartment_lender_due_diligence_builder",
            "acquisition_owner_queue",
            "clouds_safe_acquisition_source",
            "acquisition_builder_ui",
            "tower_guarded_builder_routes",
        ],
        "builder_count": builders["builder_count"],
        "atm_required_document_count": atm["readiness"]["required_document_count"],
        "apartment_required_document_count": property_builder["readiness"]["required_document_count"],
        "atm_builder_setup_score": atm["readiness"]["builder_setup_score"],
        "apartment_builder_setup_score": property_builder["readiness"]["builder_setup_score"],
        "packet_completion_score_note": "0 means target evidence has not been attached yet; builder setup is ready.",
        "direct_upload_allowed": False,
        "safe_to_continue_to_gp004": True,
    }
    return attach_tower_guard(payload, "/vault/gp003-status.json")
