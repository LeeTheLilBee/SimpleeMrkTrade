"""TWR-GRD007–011: no self-asserted Grounds claim grants a session or entry."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from tower.app_registry import route_by_path
from tower.app_truth_projection import app_truth_by_id
from tower.grounds_handoff_requirements_v1 import ROOM_ROLES
from tower.grounds_scope_review_v1 import (
    CONTRACT_ID, JOB_SCOPED_ROLES, ROLE_GROUPS,
    GroundsScopeReviewError, review_untrusted_grounds_scope,
)

NOW = 2_000_000_000


def proposed(role="resident", **changes):
    item = {
        "issuer": "tower", "audience": "grounds",
        "subject_ref": "person-A", "session_ref": "session-A",
        "role": role,
        "property_refs": ["property-A"],
        "unit_refs": ["unit-A"] if role == "resident" else [],
        "assigned_work_refs": ["work-A"] if role in JOB_SCOPED_ROLES else [],
        "issued_at": NOW, "expires_at": NOW + 300,
    }
    item.update(changes)
    return item


def target(**changes):
    item = {
        "property_ref": "property-A", "unit_ref": "unit-A",
        "assigned_work_ref": None, "operation": "READ",
    }
    item.update(changes)
    return item


@pytest.mark.parametrize("role", ROOM_ROLES)
def test_exact_roles_are_review_only_even_with_matching_claimed_property(role):
    scope = proposed(role)
    item = target(unit_ref="unit-A" if role == "resident" else None)
    result = review_untrusted_grounds_scope(scope, item, now_epoch=NOW)
    assert result["contract_id"] == CONTRACT_ID
    assert result["role_context"] == ROLE_GROUPS[role]
    assert result["candidate_scope_match"] is True
    assert result["state"] == "UNTRUSTED_SOURCE_REVIEW"
    for field in (
        "tower_identity_verified", "grounds_current_membership_verified",
        "receiver_certified", "launch_authorized", "session_created",
        "entry_authorized", "notice_delivered", "urgent_dispatch_sent",
        "teller_payment_authorized", "vault_proof_accepted",
        "paid_resources_provisioned",
    ):
        assert result[field] is False


def test_roles_match_independently_pinned_grounds_domain_source():
    path = Path(__file__).resolve().parents[1] / "grounds-source" / "grounds" / "contract.py"
    assert path.is_file(), "The exact Grounds source checkout must be pinned by CI"
    spec = importlib.util.spec_from_file_location("sealed_grounds_roles", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert set(module.ROOMS) == set(ROOM_ROLES)
    assert len(ROOM_ROLES) == 13


@pytest.mark.parametrize("extra", [
    {"step_up_active": True}, {"approved": True},
    {"teller_payment_authorized": True}, {"lease_membership_current": True},
    {"entry_permission": True}, {"signed_by_tower": True},
])
def test_self_asserted_authorization_fields_are_rejected(extra):
    with pytest.raises(GroundsScopeReviewError, match="EXACT_FIELDS_REQUIRED"):
        review_untrusted_grounds_scope(proposed(**extra), target(), now_epoch=NOW)


@pytest.mark.parametrize("change", [
    {"issuer": "buybox"}, {"audience": "vault"},
    {"role": "unknown"}, {"subject_ref": ""}, {"session_ref": "../unsafe"},
    {"property_refs": []}, {"property_refs": ["property-A", "property-A"]},
    {"unit_refs": ["unit-A", "unit-A"]}, {"assigned_work_refs": 1},
    {"issued_at": True}, {"expires_at": NOW},
    {"issued_at": NOW + 6, "expires_at": NOW + 30},
    {"expires_at": NOW + 301},
])
def test_bad_claim_shapes_fail_closed(change):
    with pytest.raises(GroundsScopeReviewError):
        review_untrusted_grounds_scope(proposed(**change), target(), now_epoch=NOW)


def test_resident_requires_a_unit_and_job_worker_requires_assignment():
    with pytest.raises(GroundsScopeReviewError, match="RESIDENT_UNIT_SCOPE_REQUIRED"):
        review_untrusted_grounds_scope(
            proposed(unit_refs=[]), target(), now_epoch=NOW
        )
    with pytest.raises(GroundsScopeReviewError, match="JOB_ASSIGNMENT_SCOPE_REQUIRED"):
        review_untrusted_grounds_scope(
            proposed("vendor", assigned_work_refs=[]),
            target(unit_ref=None), now_epoch=NOW,
        )


@pytest.mark.parametrize("changed_target", [
    {"property_ref": "property-B"},
    {"unit_ref": "unit-B"},
    {"unit_ref": None},
    {"assigned_work_ref": "job-not-assigned"},
])
def test_resident_cannot_browse_other_properties_or_units(changed_target):
    response = review_untrusted_grounds_scope(
        proposed(), target(**changed_target), now_epoch=NOW
    )
    assert response["candidate_scope_match"] is False
    assert "PROPOSED_SCOPE_OR_ROLE_MISMATCH" in response["reason_codes"]
    assert response["launch_authorized"] is False


def test_vendor_job_scope_does_not_extend_to_unassigned_work():
    response = review_untrusted_grounds_scope(
        proposed("vendor"),
        target(unit_ref=None, assigned_work_ref="work-B", operation="WORK_START"),
        now_epoch=NOW,
    )
    assert response["candidate_scope_match"] is False
    assert response["entry_authorized"] is False


def test_resident_cannot_claim_physical_work_or_dispatch():
    for operation in ("ENTRY", "WORK_START", "INSPECT", "NOTICE_DELIVERY", "URGENT_TRIAGE"):
        response = review_untrusted_grounds_scope(
            proposed(), target(operation=operation), now_epoch=NOW,
        )
        assert response["candidate_scope_match"] is False
        assert response["launch_authorized"] is False


@pytest.mark.parametrize("operation,reason", [
    ("NOTICE_DELIVERY", "ACTUAL_DELIVERY_OR_LEGAL_SERVICE_RECEIPT_UNVERIFIED"),
    ("APPOINTMENT_REQUEST", "APPOINTMENT_IS_NOT_PHYSICAL_ENTRY_CONSENT"),
    ("ENTRY", "SPECIFIC_ENTRY_CONSENT_NOTICE_AND_HUMAN_AUTHORITY_UNVERIFIED"),
    ("WORK_START", "CURRENT_WORK_ASSIGNMENT_AND_ENTRY_PERMISSION_UNVERIFIED"),
    ("INSPECT", "CURRENT_INSPECTOR_ASSIGNMENT_AND_ENTRY_PERMISSION_UNVERIFIED"),
    ("URGENT_REPORT", "URGENT_REPORT_REQUIRES_HUMAN_TRIAGE_AND_DELIVERY_CONFIRMATION"),
    ("URGENT_TRIAGE", "CURRENT_ON_CALL_HUMAN_ACKNOWLEDGMENT_UNVERIFIED"),
    ("RENT_STATUS", "TELLER_ISSUED_STATUS_UNVERIFIED"),
    ("RENT_CHECKOUT", "TELLER_ISSUED_INVOICE_AND_CHECKOUT_UNVERIFIED"),
])
def test_source_operations_cannot_be_misrepresented_as_live_receipts(operation, reason):
    response = review_untrusted_grounds_scope(
        proposed(), target(operation=operation), now_epoch=NOW,
    )
    assert reason in response["reason_codes"]
    assert response["entry_authorized"] is False
    assert response["notice_delivered"] is False
    assert response["urgent_dispatch_sent"] is False
    assert response["teller_payment_authorized"] is False


@pytest.mark.parametrize("data", [
    {"operation": "AUTO_UNLOCK"}, {"property_ref": None},
    {"property_ref": "../other"}, {"unit_ref": True}, {"assigned_work_ref": ["work-A"]},
    {"extra_access": True},
])
def test_invalid_target_does_not_create_access(data):
    with pytest.raises(GroundsScopeReviewError):
        review_untrusted_grounds_scope(
            proposed(), target(**data), now_epoch=NOW,
        )


def test_owner_role_is_not_permission_for_physical_entry():
    response = review_untrusted_grounds_scope(
        proposed("owner"), target(unit_ref=None, operation="ENTRY"), now_epoch=NOW,
    )
    assert response["candidate_scope_match"] is False
    assert response["entry_authorized"] is False


def test_fail_closed_grounds_launch_gate_is_not_product_entry():
    launch = route_by_path("/tower/launch/grounds")
    assert launch is not None
    assert launch["owner_only"] is True
    assert launch["requires_owner_session"] is True
    assert launch["requires_step_up"] is True
    assert launch["lock_state"] == "protected_fail_closed_launch_gate"
    assert route_by_path("/grounds") is None
    truth = app_truth_by_id("grounds")
    assert truth is not None
    assert truth["launchable"] is False
    import tower.grounds_scope_review_v1 as module
    source = Path(module.__file__).read_text(encoding="utf-8")
    for forbidden in ("@app.route(", "requests.post(", "from grounds.", "from vault.", "from observatory."):
        assert forbidden not in source
