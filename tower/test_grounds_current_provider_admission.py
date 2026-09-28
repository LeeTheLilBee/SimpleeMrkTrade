"""No proposed role/grant or stale source may mint a Grounds runtime admission."""
from copy import deepcopy

import pytest

from tower.grounds_current_provider_admission import (
    GroundsCurrentProviderUnavailable, inspect_current_ground_grants,
)

NOW = 1800000000


def fixtures(role="resident"):
    tower = {
        "verification_state": "VERIFIED",
        "evidence_id": "tower-current-identity-receipt",
        "subject_ref": "person-01",
        "session_ref": "tower-session-01",
        "role": role,
        "revoked": False,
        "expires_at_epoch": NOW + 45,
    }
    membership = {
        "verification_state": "VERIFIED",
        "evidence_id": "grounds-current-lease-receipt",
        "subject_ref": "person-01",
        "role": role,
        "revoked": False,
        "expires_at_epoch": NOW + 25,
        "property_refs": ["property-01", "property-02"],
        "unit_property_pairs": [["property-01", "unit-01"]],
        "assigned_work_refs": [] if role == "resident" else ["work-01"],
        "lease_state": "ACTIVE" if role == "resident" else "NOT_APPLICABLE",
    }
    calls = []
    def tower_provider(session):
        calls.append(("tower", session))
        return deepcopy(tower)
    def grounds_provider(subject, current_role):
        calls.append(("grounds", subject, current_role))
        return deepcopy(membership)
    return tower, membership, calls, tower_provider, grounds_provider


def inspect(tower_provider, grounds_provider):
    return inspect_current_ground_grants(
        "tower-session-01",
        current_tower_session=tower_provider,
        current_grounds_membership=grounds_provider,
        now_epoch=NOW,
    )


def test_independent_server_providers_are_required():
    with pytest.raises(GroundsCurrentProviderUnavailable, match="independent_providers_required"):
        inspect_current_ground_grants(
            "tower-session-01", now_epoch=NOW,
            current_tower_session=lambda _: {}, current_grounds_membership=None,
        )


def test_requeries_both_live_sources_and_preserves_exact_property_unit_pair():
    tower, membership, calls, tower_provider, grounds_provider = fixtures()
    result = inspect(tower_provider, grounds_provider)
    assert calls == [
        ("tower", "tower-session-01"),
        ("grounds", "person-01", "resident"),
    ]
    assert result["unit_property_pairs"] == [["property-01", "unit-01"]]
    assert result["candidate_until_epoch"] == NOW + 25
    assert result["state"] == "SOURCE_RECONCILED_EXTERNAL_CERTIFICATION_REQUIRED"
    for permission in ("certified_issuer", "certified_receiver", "operational_release_verified",
                       "signed_handoff_issued", "tenant_or_staff_session_created",
                       "can_issue_live_handoff", "money_authorized", "physical_entry_authorized"):
        assert result[permission] is False
    assert tower["subject_ref"] == membership["subject_ref"]


@pytest.mark.parametrize("owner", ["tower", "membership"])
def test_revocation_between_successive_requests_denies(owner):
    tower, membership, calls, tower_provider, grounds_provider = fixtures()
    assert inspect(tower_provider, grounds_provider)["current_sources_requeried"] is True
    (tower if owner == "tower" else membership)["revoked"] = True
    with pytest.raises(GroundsCurrentProviderUnavailable):
        inspect(tower_provider, grounds_provider)
    assert len(calls) >= 3


@pytest.mark.parametrize("key,value", [
    ("lease_state", "ENDED"),
    ("unit_property_pairs", []),
    ("unit_property_pairs", [["property-03", "unit-01"]]),
    ("unit_property_pairs", [["property-01", "unit-01"], ["property-01", "unit-01"]]),
    ("subject_ref", "person-other"),
    ("role", "owner"),
    ("expires_at_epoch", NOW - 1),
    ("verification_state", "UNKNOWN"),
])
def test_stale_cross_person_or_invalid_resident_membership_is_denied(key, value):
    _, membership, _, tower_provider, grounds_provider = fixtures()
    membership[key] = value
    with pytest.raises(GroundsCurrentProviderUnavailable):
        inspect(tower_provider, grounds_provider)


@pytest.mark.parametrize("key,value", [
    ("role", "unknown-role"),
    ("subject_ref", "other-person"),
    ("session_ref", "other-session"),
    ("expires_at_epoch", NOW),
    ("verification_state", "UNKNOWN"),
])
def test_tower_session_mismatch_and_unverified_identity_denied_before_membership(key, value):
    tower, _, calls, tower_provider, grounds_provider = fixtures()
    tower[key] = value
    with pytest.raises(GroundsCurrentProviderUnavailable):
        inspect(tower_provider, grounds_provider)
    if key == "subject_ref":
        # Tower determines the subject; its current answer is rechecked at
        # Grounds, which must independently reject an unrelated membership.
        assert ("grounds", "other-person", "resident") in calls
    else:
        assert not any(c[0] == "grounds" for c in calls)


def test_staff_requires_current_job_and_cannot_inherit_resident_lease():
    _, membership, _, tower_provider, grounds_provider = fixtures("maintenance_technician")
    assert inspect(tower_provider, grounds_provider)["assigned_work_refs"] == ["work-01"]
    membership["assigned_work_refs"] = []
    with pytest.raises(GroundsCurrentProviderUnavailable, match="current_job_assignment_required"):
        inspect(tower_provider, grounds_provider)
    membership["assigned_work_refs"] = ["work-01"]
    membership["lease_state"] = "ACTIVE"
    with pytest.raises(GroundsCurrentProviderUnavailable, match="resident_lease_not_a_staff_grant"):
        inspect(tower_provider, grounds_provider)


def test_provider_failure_never_surfaces_private_error():
    _, _, _, tower_provider, grounds_provider = fixtures()
    def broken_provider(*_):
        raise RuntimeError("private resident record and secret")
    with pytest.raises(GroundsCurrentProviderUnavailable) as caught:
        inspect(tower_provider, broken_provider)
    assert "private resident record" not in str(caught.value)
    assert caught.value.__cause__ is None


def test_claimed_browser_fields_do_not_enter_the_api():
    _, _, _, tower_provider, grounds_provider = fixtures()
    with pytest.raises(TypeError):
        inspect_current_ground_grants(
            "tower-session-01", now_epoch=NOW,
            current_tower_session=tower_provider,
            current_grounds_membership=grounds_provider,
            claimed_browser_role="owner",
        )
