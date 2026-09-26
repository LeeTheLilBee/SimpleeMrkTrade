"""Tower-to-Grounds handoff requirements, source-only review artifact.

This module deliberately neither issues/verifies tokens nor registers routes.
It describes the resident/staff/owner security contract Tower must certify
before a real Grounds service can accept user sessions. A green checklist is
never permission to launch. Existing Observatory and Teller routes unchanged.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Mapping

CONTRACT_ID = "tower.grounds.handoff.requirements.v1"

ROOM_ROLES = (
    "resident", "maintenance_technician", "maintenance_supervisor",
    "leasing_agent", "property_manager", "regional_manager", "inspector",
    "turnover_crew", "grounds_janitorial", "renovation_coordinator",
    "compliance", "vendor", "owner",
)

DECISION_REQUIRED = (
    "real_separate_resident_identity", "real_separate_staff_identity",
    "attested_ground_audience_and_issuer", "host_and_receiver_proof",
    "audience_bound_nonreplayable_handoff", "revocation_and_logout",
    "property_and_unit_membership_verification", "staff_property_assignment",
    "technician_and_vendor_job_assignment", "purpose_bound_permissions",
    "tenant_data_privacy_review", "audit_and_incident_response",
    "return_route_and_expiry_tests", "storage_and_backup_restore_proof",
)

ALLOWED_CLAIM_FIELDS = frozenset((
    "issuer", "audience", "subject_ref", "session_ref", "role",
    "property_refs", "unit_refs", "assigned_work_refs",
    "issued_at", "expires_at",
))

def get_grounds_requirements() -> dict:
    """Copy-safe checklist. Never a token schema or effective entitlement."""
    return deepcopy({
        "contract_id": CONTRACT_ID,
        "mode": "source_only",
        "tower_role": "authenticate, scope, step-up and audit",
        "grounds_role": "verify certified handoff, recheck property/unit/job on reads and writes",
        "teller_role": "own rent invoice, payment status and checkout",
        "vault_role": "sealed lease and work proof via Tower-mediated references",
        "buybox_role": "verified-close source, no implicit owned property on listing",
        "clouds_role": "permission-safe summaries, not resident transactions",
        "roles": list(ROOM_ROLES),
        "separate_identity_contexts": ["resident", "staff", "owner"],
        "required_review_evidence": list(DECISION_REQUIRED),
        "proposed_claim_fields_for_reconciliation": sorted(ALLOWED_CLAIM_FIELDS),
        "wire_protocol_authorized": False,
        "signed_token_issuer_implemented": False,
        "receiver_certified": False,
        "route_registered": False,
        "tenant_session_enabled": False,
        "staff_session_enabled": False,
        "entitlement_granted": False,
        "payment_action_enabled": False,
        "lease_mutation_enabled": False,
        "capital_movement_enabled": False,
        "render_resources_provisioned": False,
    })

def grounds_readiness_review(evidence: Mapping[str, bool] | None = None) -> dict:
    """Advisory checklist. Even every item marked True requires human Tower acceptance."""
    supplied = evidence if isinstance(evidence, Mapping) else {}
    covered = sorted(k for k in DECISION_REQUIRED if supplied.get(k) is True)
    missing = sorted(set(DECISION_REQUIRED) - set(covered))
    return {
        "contract_id": CONTRACT_ID,
        "reviewed_items": covered,
        "missing_or_unverified": missing,
        "status": "BLOCKED" if missing else "OWNER_SECURITY_REVIEW_REQUIRED",
        "launch_authorized": False,
        "entitlement_granted": False,
        "token_issued": False,
        "tenant_or_staff_traffic_accepted": False,
        "note": "Self-reported checklist entries are not security evidence; source-only handoff.",
    }
