"""GRD001–GRD003: recovered Grounds scope and non-live room contracts.

This is product/domain specification expressed as code, not an authorization,
identity, billing, checkout, persistence, or tenant-facing runtime implementation.
A real Tower-verified receiver and property-scoped grants remain prerequisites.
"""
from __future__ import annotations

from copy import deepcopy

CONTRACT_VERSION = "grounds.foundation.v1"
SOURCE_ONLY = True

ROOMS = {
    "resident": ("home", "rent_display", "lease", "maintenance", "notices", "appointments"),
    "maintenance_technician": ("assigned_work", "schedule", "asset_history", "completion"),
    "maintenance_supervisor": ("triage", "dispatch", "work_orders", "parts_labor", "escalations"),
    "leasing_agent": ("availability", "prospects", "tours", "applications", "move_ins", "renewals"),
    "property_manager": ("property_pulse", "residents", "maintenance", "leasing", "vendors", "inspections", "compliance"),
    "regional_manager": ("portfolio_operations", "property_reviews", "manager_tasks"),
    "inspector": ("assigned_inspections", "condition_records"),
    "turnover_crew": ("make_ready", "assigned_turns"),
    "grounds_janitorial": ("assigned_grounds_tasks", "checklists"),
    "renovation_coordinator": ("projects", "milestones", "contractor_tasks"),
    "compliance": ("deadlines", "notices", "review_cases"),
    "vendor": ("temporarily_assigned_jobs", "job_updates"),
    "owner": ("portfolio", "properties", "occupancy", "work_order_pulse", "decision_packets"),
}

SYSTEM_BOUNDARIES = {
    "grounds": "property, building, unit, resident/lease context, maintenance, inspections, occupancy, physical asset history",
    "tower": "identity, tenant/unit and staff/property access, role grants, step-up, cross-system handoff, audit",
    "teller": "rent invoices and financial status, ACH/card checkout, autopay, failures, refunds, receipts and reconciliation",
    "vault": "Tower-mediated sealed leases, authorization, inspection and work-order evidence, notices and receipt proof",
    "clouds": "permission-safe owner-wide status summaries, not property workflow execution",
    "buybox": "pre-close acquisition intelligence; ownership handoff only on verified close",
    "observatory": "capital intelligence under its own policies; no direct tenant or Grounds money execution",
}

ORIGINAL_SCOPE_GROUPS = (
    "portfolio_foundation",
    "acquisition_and_close_handoff",
    "property_intelligence_and_planning",
    "resident_and_lease_operations",
    "maintenance_and_asset_history",
    "staff_and_vendor_workspaces",
    "inspections_and_turnover",
    "utilities_infrastructure_and_sustainability",
    "tax_intelligence_and_compliance",
    "renovation_and_capex",
)

def foundation_status() -> dict:
    """Publish explicit truth rather than imply a live operating system."""
    return {
        "contract_version": CONTRACT_VERSION,
        "mode": "source_only",
        "roles_defined": len(ROOMS),
        "scope_groups": list(ORIGINAL_SCOPE_GROUPS),
        "real_tenant_data_connected": False,
        "tower_receiver_certified": False,
        "tenant_login_enabled": False,
        "resident_rent_checkout_enabled": False,
        "teller_connected": False,
        "work_order_persistence_enabled": False,
        "local_development_sqlite_available": True,
        "local_preview_available": True,
        "resident_household_local_model_available": True,
        "local_in_app_notice_reads_available": True,
        "local_appointment_negotiation_available": True,
        "human_urgency_review_local_model_available": True,
        "notification_intent_outbox_available": True,
        "notification_delivery_enabled": False,
        "emergency_dispatch_connected": False,
        "legal_entry_notice_or_consent_certified": False,
        "soulaana_read_only_source_explanations_available": True,
        "live_soulaana_ai_connected": False,
        "vault_connected": False,
        "clouds_operational_publisher_enabled": False,
        "paid_infrastructure_provisioned": False,
    }

def room_contract(role: str) -> dict:
    """Descriptive workspace manifest; never an entitlement or authorization."""
    if role not in ROOMS:
        raise ValueError("unknown Grounds role")
    return {
        "contract_version": CONTRACT_VERSION,
        "role": role,
        "rooms": list(ROOMS[role]),
        "permission_grant": False,
        "tower_authorization_required": True,
        "source_only": SOURCE_ONLY,
    }

def resident_home_contract() -> dict:
    """Resident-facing experience; amount/payment truth must be Teller-sourced."""
    return deepcopy({
        "contract_version": CONTRACT_VERSION,
        "entry": "Tower-verified resident/property/unit entitlement required",
        "sections": [
            "home", "lease_and_unit", "rent_display", "pay_rent_handoff",
            "autopay_status", "payment_history", "maintenance", "notices",
            "appointments",
        ],
        "lease_and_unit_source": "grounds",
        "amount_due_and_invoice_source": "teller",
        "checkout_owner": "teller",
        "receipt_owner": "teller",
        "evidence": "Tower-mediated Vault references only",
        "checkout_url": None,
        "payment_token": None,
        "actual_amount_due": None,
        "payment_execution_enabled": False,
        "source_only": True,
    })
