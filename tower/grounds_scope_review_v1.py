"""TWR-GRD007–011: untrusted Grounds role/scope review, never an access grant.

Inputs are proposed claims from the documented Grounds normal form. This module
does not authenticate an issuer, user, lease, assignment, role or session; it
does not issue a token, activate a route, accept an appointment as entry consent,
count in-app notice-reading as legal service, or perform any external call.
A future live adapter must derive/revalidate authority independently in Tower
AND Grounds. Even a perfect proposed packet always yields launch_authorized=False.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from tower.grounds_handoff_requirements_v1 import (
    ALLOWED_CLAIM_FIELDS,
    ROOM_ROLES,
)

CONTRACT_ID = "tower.grounds.scope.review.v1"
MAX_CLAIM_LIFETIME_SECONDS = 300
MAX_REFS = 500
_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
REQUEST_FIELDS = frozenset({
    "property_ref", "unit_ref", "assigned_work_ref", "operation",
})
OPERATIONS = frozenset({
    "READ", "NOTICE_READ", "NOTICE_DELIVERY", "APPOINTMENT_REQUEST",
    "ENTRY", "WORK_START", "INSPECT", "URGENT_REPORT", "URGENT_TRIAGE",
    "RENT_STATUS", "RENT_CHECKOUT",
})
JOB_SCOPED_ROLES = frozenset({
    "maintenance_technician", "inspector", "turnover_crew",
    "grounds_janitorial", "vendor",
})
RESIDENT_PHYSICAL_OPERATIONS = frozenset({
    "NOTICE_DELIVERY", "ENTRY", "WORK_START", "INSPECT", "URGENT_TRIAGE",
})
PHYSICAL_OPERATIONS = frozenset({"ENTRY", "WORK_START", "INSPECT"})
ROLE_GROUPS = {
    "resident": "resident",
    "owner": "owner",
    **{role: "staff" for role in ROOM_ROLES if role not in {"resident", "owner"}},
}


class GroundsScopeReviewError(ValueError):
    """Safe source-level rejection; never include tenant or session references."""


def _ref(value: Any) -> bool:
    return isinstance(value, str) and _REF.fullmatch(value) is not None


def _refs(value: Any, field: str) -> frozenset[str]:
    if not isinstance(value, list) or len(value) > MAX_REFS:
        raise GroundsScopeReviewError(field + "_INVALID")
    if any(not _ref(item) for item in value) or len(set(value)) != len(value):
        raise GroundsScopeReviewError(field + "_INVALID")
    return frozenset(value)


def _target_ref(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not _ref(value):
        raise GroundsScopeReviewError(field + "_INVALID")
    return value


def review_untrusted_grounds_scope(
    claims: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    now_epoch: int,
) -> dict[str, Any]:
    """Compare two proposed shapes without accepting either as authority.

    A matching property/unit/job in claimed arrays is NOT a current Tower
    grant, active Grounds household/lease membership, work assignment,
    signed/replay-safe token, physical-entry consent or verified delivery.
    """
    if (
        not isinstance(claims, Mapping)
        or set(claims) != ALLOWED_CLAIM_FIELDS
        or not isinstance(target, Mapping)
        or set(target) != REQUEST_FIELDS
    ):
        raise GroundsScopeReviewError("EXACT_FIELDS_REQUIRED")
    if claims["issuer"] != "tower" or claims["audience"] != "grounds":
        raise GroundsScopeReviewError("ROUTING_INVALID")
    if not _ref(claims["subject_ref"]) or not _ref(claims["session_ref"]):
        raise GroundsScopeReviewError("IDENTITY_REFERENCE_INVALID")
    role = claims["role"]
    if not isinstance(role, str) or role not in ROOM_ROLES:
        raise GroundsScopeReviewError("ROLE_UNKNOWN")

    issued = claims["issued_at"]
    expires = claims["expires_at"]
    if any(type(value) is not int for value in (issued, expires, now_epoch)):
        raise GroundsScopeReviewError("TIME_TYPE_INVALID")
    if (
        issued > now_epoch + 5
        or expires <= now_epoch
        or not 0 < expires - issued <= MAX_CLAIM_LIFETIME_SECONDS
    ):
        raise GroundsScopeReviewError("TIME_WINDOW_INVALID")

    properties = _refs(claims["property_refs"], "PROPERTY_REFS")
    units = _refs(claims["unit_refs"], "UNIT_REFS")
    assigned_work = _refs(claims["assigned_work_refs"], "WORK_REFS")
    if not properties:
        raise GroundsScopeReviewError("PROPERTY_SCOPE_REQUIRED")
    if role == "resident" and not units:
        raise GroundsScopeReviewError("RESIDENT_UNIT_SCOPE_REQUIRED")
    if role in JOB_SCOPED_ROLES and not assigned_work:
        raise GroundsScopeReviewError("JOB_ASSIGNMENT_SCOPE_REQUIRED")

    property_ref = _target_ref(target["property_ref"], "TARGET_PROPERTY")
    unit_ref = _target_ref(target["unit_ref"], "TARGET_UNIT")
    work_ref = _target_ref(target["assigned_work_ref"], "TARGET_WORK")
    operation = target["operation"]
    if property_ref is None or not isinstance(operation, str) or operation not in OPERATIONS:
        raise GroundsScopeReviewError("TARGET_OPERATION_OR_PROPERTY_INVALID")

    reasons = [
        "REAL_TOWER_IDENTITY_SESSION_STEP_UP_AND_REVOCATION_UNVERIFIED",
        "SIGNED_AUDIENCE_BOUND_NONREPLAYABLE_RECEIVER_UNVERIFIED",
        "CURRENT_GROUNDS_LEASE_MEMBERSHIP_OR_STAFF_ASSIGNMENT_UNVERIFIED",
        "PRIVATE_HOSTING_AND_RESTORE_UNVERIFIED",
    ]
    candidate_match = property_ref in properties
    if unit_ref is not None:
        candidate_match = candidate_match and unit_ref in units
    if work_ref is not None:
        candidate_match = candidate_match and work_ref in assigned_work
    if role == "resident" and unit_ref is None:
        candidate_match = False
    if role in JOB_SCOPED_ROLES and operation in PHYSICAL_OPERATIONS and work_ref is None:
        candidate_match = False
    if role == "resident" and operation in RESIDENT_PHYSICAL_OPERATIONS:
        candidate_match = False
    if role == "owner" and operation in PHYSICAL_OPERATIONS:
        candidate_match = False
    if not candidate_match:
        reasons.append("PROPOSED_SCOPE_OR_ROLE_MISMATCH")

    operation_blockers = {
        "NOTICE_DELIVERY": "ACTUAL_DELIVERY_OR_LEGAL_SERVICE_RECEIPT_UNVERIFIED",
        "APPOINTMENT_REQUEST": "APPOINTMENT_IS_NOT_PHYSICAL_ENTRY_CONSENT",
        "ENTRY": "SPECIFIC_ENTRY_CONSENT_NOTICE_AND_HUMAN_AUTHORITY_UNVERIFIED",
        "WORK_START": "CURRENT_WORK_ASSIGNMENT_AND_ENTRY_PERMISSION_UNVERIFIED",
        "INSPECT": "CURRENT_INSPECTOR_ASSIGNMENT_AND_ENTRY_PERMISSION_UNVERIFIED",
        "URGENT_REPORT": "URGENT_REPORT_REQUIRES_HUMAN_TRIAGE_AND_DELIVERY_CONFIRMATION",
        "URGENT_TRIAGE": "CURRENT_ON_CALL_HUMAN_ACKNOWLEDGMENT_UNVERIFIED",
        "RENT_STATUS": "TELLER_ISSUED_STATUS_UNVERIFIED",
        "RENT_CHECKOUT": "TELLER_ISSUED_INVOICE_AND_CHECKOUT_UNVERIFIED",
    }
    if operation in operation_blockers:
        reasons.append(operation_blockers[operation])

    return {
        "contract_id": CONTRACT_ID,
        "state": "UNTRUSTED_SOURCE_REVIEW",
        "role_context": ROLE_GROUPS[role],
        "candidate_scope_match": bool(candidate_match),
        "reason_codes": reasons,
        "tower_identity_verified": False,
        "grounds_current_membership_verified": False,
        "receiver_certified": False,
        "launch_authorized": False,
        "session_created": False,
        "entry_authorized": False,
        "notice_delivered": False,
        "urgent_dispatch_sent": False,
        "teller_payment_authorized": False,
        "vault_proof_accepted": False,
        "paid_resources_provisioned": False,
    }
