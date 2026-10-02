from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

from flask import Flask, session

import simplee_integrations.grounds_owner_runtime_provider as provider
from tower.ecosystem_direct_route_guard import (
    ACCESS_RECEIPT_KEYS, build_ecosystem_access_receipt,
)
from tower.tower_human_login_ob_launch import (
    SESSION_AUTHENTICATED, SESSION_ID, SESSION_OWNER_ID, SESSION_ROLE,
    SESSION_STEP_UP_UNTIL, SESSION_USERNAME, utc_now,
)


def owner_session():
    session[SESSION_AUTHENTICATED]=True
    session[SESSION_ROLE]="owner"
    session[SESSION_OWNER_ID]="owner_runtime_fixture_000001"
    session[SESSION_USERNAME]="owner"
    session[SESSION_ID]="tower_session_owner_runtime_fixture_000001"
    session[SESSION_STEP_UP_UNTIL]=(utc_now()+timedelta(minutes=10)).isoformat()


def identity():
    return {
        "verification_state":"VERIFIED",
        "record":{
            "person_id":"owner_runtime_fixture_000001",
            "role":"owner",
            "session_subject_alignment":"VERIFIED",
        },
        "app_entitlements":[{
            "app_id":"grounds","access_policy":"GRANTED",
            "verification_state":"VERIFIED",
        }],
    }


def app():
    a=Flask(__name__)
    a.config.update(TESTING=True,SECRET_KEY="provider-fixture-secret")
    return a


def test_attestation_requires_real_identity_and_current_property_source(monkeypatch):
    monkeypatch.setattr(provider,"hosted_owner_identity_authority",identity)
    monkeypatch.setattr(provider,"_property_refs",lambda:["property_runtime_fixture_000001"])
    record=provider.provider_attestation()
    assert record["status"]=="VERIFIED"
    assert record["audience"]=="grounds"
    assert record["resource_grants_checked"] is True
    assert provider.health_check() is True


def test_owner_request_uses_signed_session_current_receipt_and_server_property_grants(monkeypatch):
    monkeypatch.setattr(provider,"hosted_owner_identity_authority",identity)
    monkeypatch.setattr(provider,"_property_refs",lambda:["property_runtime_fixture_000001"])
    a=app()
    with a.test_request_context("/grounds/api/me"):
        owner_session()
        session[ACCESS_RECEIPT_KEYS["grounds"]]=build_ecosystem_access_receipt("grounds")
        claims=provider.verify_grounds_request(request_environ:=dict(
            __import__("flask").request.environ
        ))
        assert claims["subject_ref"]=="owner_runtime_fixture_000001"
        assert claims["role"]=="owner"
        assert claims["property_refs"]==["property_runtime_fixture_000001"]
        assert claims["unit_refs"]==[]
        assert claims["assigned_work_refs"]==[]
        assert claims["expires_at"]<=session[ACCESS_RECEIPT_KEYS["grounds"]]["expires_at_epoch"]


def test_browser_or_missing_receipt_cannot_choose_owner_or_property(monkeypatch):
    monkeypatch.setattr(provider,"hosted_owner_identity_authority",identity)
    monkeypatch.setattr(provider,"_property_refs",lambda:["property_runtime_fixture_000001"])
    a=app()
    with a.test_request_context(
        "/grounds/api/me",
        headers={"X-Role":"owner","X-Property-Refs":"invented-property"},
    ):
        owner_session()
        try:
            provider.verify_grounds_request(dict(__import__("flask").request.environ))
        except provider.GroundsOwnerRuntimeProviderUnavailable:
            pass
        else:
            raise AssertionError("missing server-created Grounds receipt unexpectedly authorized")
        session[ACCESS_RECEIPT_KEYS["grounds"]]=build_ecosystem_access_receipt("grounds")
        claims=provider.verify_grounds_request(dict(__import__("flask").request.environ))
        assert claims["property_refs"]==["property_runtime_fixture_000001"]
        assert "invented-property" not in claims["property_refs"]


def test_current_provider_has_no_fake_staff_directory_or_assignment(monkeypatch):
    monkeypatch.setattr(provider,"hosted_owner_identity_authority",identity)
    monkeypatch.setattr(provider,"_property_refs",lambda:["property_runtime_fixture_000001"])
    a=app()
    with a.test_request_context("/grounds/api/staff-directory"):
        owner_session()
        session[ACCESS_RECEIPT_KEYS["grounds"]]=build_ecosystem_access_receipt("grounds")
        assert provider.list_ground_technicians(
            actor_subject_ref="owner_runtime_fixture_000001",
            actor_session_ref="tower_session_owner_runtime_fixture_000001",
            property_ref="property_runtime_fixture_000001",
        )==[]
        try:
            provider.verify_ground_technician_assignment(
                actor_subject_ref="owner_runtime_fixture_000001",
                actor_session_ref="tower_session_owner_runtime_fixture_000001",
                property_ref="property_runtime_fixture_000001",
                work_ref="work_runtime_fixture_000001",
                technician_ref="tech_runtime_fixture_000001",
            )
        except provider.GroundsOwnerRuntimeProviderUnavailable:
            pass
        else:
            raise AssertionError("staff assignment must remain unavailable")
