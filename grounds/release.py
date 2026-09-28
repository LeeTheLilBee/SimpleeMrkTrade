"""GRD077 — source-vs-live release status: descriptive, never an unlock switch.

Actual release may only occur after the owner reviews independently verified,
current Tower/Teller/Vault/storage/notification/privacy evidence outside this
package. Supplying booleans, a green unit test, a preview screenshot or a
locally simulated ticket cannot authorize live traffic or create entitlements.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from .contract import foundation_status

RELEASE_REQUIREMENTS={
    "tower_identity_and_scopes":"Tower-certified signed resident/staff/owner handoff and per-resource revocation",
    "private_storage_and_recovery":"Hosted private tenant store, safe migrations, backup and restore evidence",
    "teller_billing_checkout":"Fresh authenticated invoices, Tower-mediated checkout, webhook reconciliation and failures",
    "vault_sealed_documents":"Certified, private file/document intake and proof verification with revocation and retention",
    "staff_dispatch_and_notifications":"Actual after-hours urgency escalation, acknowledgment, provider delivery and safe failure path",
    "housing_privacy_accessibility":"Jurisdiction-specific entry/notice/lease review, privacy, fair access and accessibility acceptance",
    "soulaana_source_runtime":"Read-only authorized source adapter with current revision, freshness and privacy checks",
    "owner_release_acceptance":"Explicit owner decision based on the compiled certification packet",
}

def source_completion_status()->dict:
    foundation=foundation_status()
    return {
        "mode":"source_only","review_label":"REAL_DATA_WEB_SOURCE_AVAILABLE_EXTERNAL_RELEASE_GATES_LOCKED",
        "role_contract_count":foundation["roles_defined"],
        "fictional_browser_preview":foundation["local_preview_available"],
        "real_data_web_source_available":foundation["real_data_browser_ui_source_available"],
        "tower_guarded_wsgi_source_available":foundation["server_injected_tower_wsgi_api_source_available"],
        "postgres_schema_and_adapter_source_available":(
            foundation["postgresql_baseline_schema_source_available"]
            and foundation["postgresql_transaction_adapter_source_available"]
        ),
        "real_postgres_ci_workflow_available":True,
        "real_postgres_ci_result_must_be_checked_externally":True,
        "retry_safe_work_and_appointment_source_available":True,
        "authenticated_staff_safety_desk_source_available":True,
        "privacy_minimized_leasing_read_desk_source_available":True,
        "role_scoped_physical_workboard_source_available":True,
        "verified_post_close_property_receiver_source_available":True,
        "verified_delivery_receipt_ledger_source_available":True,
        "certified_external_post_close_or_delivery_provider_connected":False,
        "actual_dispatch_inspection_signoff_vault_and_entry_certified":False,
        "independent_operational_runtime_release_gate_source_available":True,
        "combined_real_postgres_operational_and_tower_gate_regression_source_available":True,
        "role_specific_my_home_daily_and_portfolio_source_available":True,
        "current_lease_scoped_private_maintenance_conversation_source_available":True,
        "resident_self_reported_move_concierge_source_available":True,
        "historical_delivery_exception_desk_source_available":True,
        "resident_minimal_record_access_history_source_available":True,
        "current_lease_resident_completion_confirmation_source_available":True,
        "real_privacy_retention_and_security_audit_certified":False,
        "source_level_accessibility_regression_available":True,
        "actual_provider_retry_and_human_accessibility_certified":False,
        "externally_verified_move_completion_and_deposit_authority":False,
        "external_maintenance_message_transport_connected":False,
        "externally_certified_money_and_private_document_actions":False,
        "external_owner_walkthrough_signed_off":False,
        "certified_tower_operational_release_issuer_and_guard_connected":False,
        "real_applicant_intake_and_decisions_certified":False,
        "human_on_call_escalation_or_provider_delivery_certified":False,
        "tower_staff_directory_and_assignment_receiver_certified":False,
        "developer_demo_command":"python -m grounds.dev_demo --fictional-only",
        "domain_tests_required":True,"latest_github_ci_must_be_confirmed_externally":True,
        "demo_result_is_not_production_evidence":True,
        "actual_resident_sessions_enabled":False,
        "tower_receiver_certified":False,"checkout_enabled":False,
        "vault_file_upload_enabled":False,"notifications_delivered":False,
        "paid_infrastructure_provisioned":False,
        "live_tenant_release_authorized":False,
    }

def review_live_requirements(evidence:Mapping[str,bool]|None=None)->dict:
    """A self-reported checklist is not verified acceptance or authorization."""
    supplied=evidence if isinstance(evidence,Mapping) else {}
    marked=sorted(key for key in RELEASE_REQUIREMENTS if supplied.get(key) is True)
    absent=sorted(set(RELEASE_REQUIREMENTS)-set(marked))
    return deepcopy({
        "stage":"not_live","mode":"advisory_only",
        "requirement_details":RELEASE_REQUIREMENTS,
        "self_reported_items":marked,
        "missing_or_unverified":absent,
        "review_state":"EXTERNAL_CERTIFICATION_AND_OWNER_ACCEPTANCE_REQUIRED",
        "trusts_self_reported_evidence":False,
        "runtime_unlocked":False,"tenant_session_accepted":False,
        "real_money_movement_enabled":False,"live_release_authorized":False,
        "provider_resources_created":False,
    })
