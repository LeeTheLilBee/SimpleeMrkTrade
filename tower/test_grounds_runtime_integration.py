from __future__ import annotations

import sys
import time
import types
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

import tower.grounds_runtime_receiver as runtime
import tower.grounds_operational_release as release


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv(runtime.PROVIDER_ENV, raising=False)
    monkeypatch.delenv(release.PROVIDER_ENV, raising=False)


def install_runtime_provider(monkeypatch, name="simplee_integrations.fake_grounds"):
    now = int(time.time())
    provider = types.ModuleType(name)
    provider.provider_attestation = lambda: {
        "schema_version": runtime.ATTESTATION_SCHEMA,
        "issuer": "tower",
        "audience": "grounds",
        "provider_id": "tower_grounds_provider_fixture_001",
        "status": "VERIFIED",
        "issued_at_epoch": now - 5,
        "expires_at_epoch": now + 60,
        "revocation_checked": True,
        "session_binding_checked": True,
        "resource_grants_checked": True,
    }
    provider.health_check = lambda: True
    provider.verify_grounds_request = lambda ticket: ticket["claims"]
    provider.list_ground_technicians = lambda **kwargs: [
        {"staff_ref": "tower_staff_technician_fixture_001", "label": "Technician A"}
    ]
    provider.verify_ground_technician_assignment = lambda **kwargs: {
        "claims": {
            "issuer": "tower",
            "audience": "grounds",
            "subject_ref": kwargs["technician_ref"],
            "session_ref": "tower_session_technician_fixture_001",
            "role": "maintenance_technician",
            "property_refs": [kwargs["property_ref"]],
            "unit_refs": [],
            "assigned_work_refs": [kwargs["work_ref"]],
            "issued_at": now - 5,
            "expires_at": now + 60,
        }
    }
    monkeypatch.setitem(sys.modules, name, provider)
    monkeypatch.setenv(runtime.PROVIDER_ENV, name)
    return provider


def install_fake_grounds_access(monkeypatch):
    access = types.ModuleType("grounds.access")

    @dataclass(frozen=True)
    class TowerScope:
        subject_ref: str
        role: str
        property_refs: frozenset[str]
        unit_refs: frozenset[str]
        assigned_work_refs: frozenset[str]
        expires_at: int
        session_ref: str

    def verified_scope(ticket, *, verifier):
        claims = verifier(ticket)
        return TowerScope(
            claims["subject_ref"], claims["role"],
            frozenset(claims["property_refs"]), frozenset(claims["unit_refs"]),
            frozenset(claims["assigned_work_refs"]), claims["expires_at"],
            claims["session_ref"],
        )

    package = types.ModuleType("grounds")
    package.__path__ = []
    access.TowerScope = TowerScope
    access.verified_scope = verified_scope
    monkeypatch.setitem(sys.modules, "grounds", package)
    monkeypatch.setitem(sys.modules, "grounds.access", access)
    return TowerScope


def install_release_provider(monkeypatch, name="simplee_integrations.fake_grounds_release"):
    now = int(time.time())
    provider = types.ModuleType(name)
    provider.health_check = lambda: True
    provider.current_release_decision = lambda: {
        "schema_version": release.SCHEMA,
        "issuer": "tower",
        "audience": "grounds",
        "status": "APPROVED",
        "environment_id": "grounds_environment_fixture_001",
        "revision_id": "grounds_revision_fixture_001",
        "owner_acceptance_ref": "owner_acceptance_fixture_001",
        "storage_restore_ref": "storage_restore_fixture_001",
        "privacy_housing_review_ref": "privacy_review_fixture_001",
        "operations_coverage_ref": "operations_coverage_fixture_001",
        "issued_at_epoch": now - 5,
        "expires_at_epoch": now + 60,
        "revocation_checked": True,
    }
    monkeypatch.setitem(sys.modules, name, provider)
    monkeypatch.setenv(release.PROVIDER_ENV, name)
    return provider


def test_missing_ground_providers_fail_closed():
    with pytest.raises(runtime.GroundsRuntimeReceiverUnavailable):
        runtime.create_certified_grounds_receiver()
    with pytest.raises(release.GroundsOperationalReleaseAuthorityUnavailable):
        release.create_certified_grounds_operational_release_guard()


def test_runtime_receiver_only_normalizes_provider_verified_scope(monkeypatch):
    install_fake_grounds_access(monkeypatch)
    install_runtime_provider(monkeypatch)
    receiver = runtime.create_certified_grounds_receiver()
    now = int(time.time())
    ticket = {"claims": {
        "issuer": "tower", "audience": "grounds",
        "subject_ref": "tower_owner_subject_fixture_001",
        "session_ref": "tower_session_owner_fixture_001",
        "role": "owner",
        "property_refs": ["grounds_property_fixture_001"],
        "unit_refs": [], "assigned_work_refs": [],
        "issued_at": now - 5, "expires_at": now + 60,
    }}
    scope = receiver(ticket)
    assert scope.role == "owner"
    assert "grounds_property_fixture_001" in scope.property_refs
    assert receiver.health_check() is True


def test_staff_directory_and_resolver_recheck_actor_and_exact_assignment(monkeypatch):
    TowerScope = install_fake_grounds_access(monkeypatch)
    install_runtime_provider(monkeypatch)
    actor = TowerScope(
        "tower_owner_subject_fixture_001", "owner",
        frozenset({"grounds_property_fixture_001"}), frozenset(), frozenset(),
        int(time.time()) + 60, "tower_session_owner_fixture_001",
    )
    directory = runtime.create_certified_grounds_staff_directory()
    resolver = runtime.create_certified_grounds_staff_resolver()
    rows = directory(actor, "grounds_property_fixture_001")
    assert rows == [{"staff_ref": "tower_staff_technician_fixture_001", "label": "Technician A"}]
    tech = resolver(
        actor, "grounds_property_fixture_001",
        "grounds_work_fixture_001", "tower_staff_technician_fixture_001",
    )
    assert tech.role == "maintenance_technician"
    assert "grounds_work_fixture_001" in tech.assigned_work_refs


def test_runtime_attestation_revocation_or_staleness_closes_health(monkeypatch):
    install_fake_grounds_access(monkeypatch)
    provider = install_runtime_provider(monkeypatch)
    receiver = runtime.create_certified_grounds_receiver()
    original = provider.provider_attestation
    stale = original()
    stale["expires_at_epoch"] = int(time.time()) - 1
    provider.provider_attestation = lambda: stale
    assert receiver.health_check() is False


def test_release_guard_requires_current_independent_decision(monkeypatch):
    provider = install_release_provider(monkeypatch)
    guard = release.create_certified_grounds_operational_release_guard()
    assert guard({"PATH_INFO": "/grounds", "REQUEST_METHOD": "GET"}) is True
    assert guard.health_check() is True
    decision = provider.current_release_decision()
    decision["status"] = "REVOKED"
    provider.current_release_decision = lambda: decision
    assert guard.health_check() is False
    assert guard({"PATH_INFO": "/grounds", "REQUEST_METHOD": "GET"}) is False


def test_provider_cannot_be_selected_from_tower_or_grounds_package(monkeypatch):
    monkeypatch.setenv(runtime.PROVIDER_ENV, "tower.some_test_provider")
    with pytest.raises(runtime.GroundsRuntimeReceiverUnavailable):
        runtime.create_certified_grounds_receiver()
    monkeypatch.setenv(release.PROVIDER_ENV, "grounds.fake_release")
    with pytest.raises(release.GroundsOperationalReleaseAuthorityUnavailable):
        release.create_certified_grounds_operational_release_guard()
