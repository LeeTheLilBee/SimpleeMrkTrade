from __future__ import annotations

import pytest
import time
from flask import Flask

from tower.ecosystem_direct_route_guard import (
    ACCESS_RECEIPT_KEYS, build_ecosystem_access_receipt,
    register_ecosystem_direct_route_guard,
)
from tower.ecosystem_return_routes import register_ecosystem_return_routes
from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH, LOGIN_PATH, register_tower_human_login,
)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    monkeypatch.setenv("TOWER_OWNER_USERNAME", "fixture-owner")
    monkeypatch.setenv("TOWER_LOCAL_OWNER_PASSWORD", "fixture-password")
    monkeypatch.setenv("TOWER_SESSION_SECRET", "fixture-session-secret-value-long-enough")
    monkeypatch.setenv("TOWER_OWNER_ID", "tower_owner_fixture_000000000001")

    app = Flask(__name__)
    app.config.update(TESTING=True)
    register_tower_human_login(app)
    register_ecosystem_direct_route_guard(app)
    register_ecosystem_return_routes(app)

    @app.get("/vault")
    def vault():
        return "VAULT SHOULD REQUIRE TOWER RECEIPT"

    @app.get("/clouds/status.json")
    def clouds_status():
        return {"ok": True}

    @app.get("/grounds")
    def grounds():
        return "GROUNDS"

    @app.get("/buybox")
    def buybox():
        return "BUYBOX"

    @app.get("/tower/archive-vault/acceptance-records.json")
    def tower_internal_vault_route():
        return {"tower_internal": True}

    return app.test_client()


def login(client):
    response = client.post(
        LOGIN_PATH,
        data={"username": "fixture-owner", "password": "fixture-password"},
        follow_redirects=False,
    )
    assert response.status_code == 302


@pytest.mark.parametrize("path", ["/vault", "/clouds/status.json", "/grounds", "/buybox"])
def test_future_product_direct_routes_require_tower_session_first(client, path):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert "/tower/login" in response.location


@pytest.mark.parametrize("path", ["/vault", "/clouds/status.json", "/grounds", "/buybox"])
def test_authenticated_owner_still_cannot_bypass_launch_receipt(client, path):
    login(client)
    response = client.get(path)
    assert response.status_code == 503
    if path.endswith(".json"):
        assert response.get_json()["direct_route_authorized"] is False
    else:
        assert "not open through Tower yet" in response.get_data(as_text=True)


def test_invalid_access_receipt_is_removed_and_denied(client):
    login(client)
    with client.session_transaction() as session:
        session[ACCESS_RECEIPT_KEYS["vault"]] = {
            "app_id": "vault",
            "allowed": True,
            "owner_session_preserved": False,
        }
    response = client.get("/vault")
    assert response.status_code == 503
    with client.session_transaction() as session:
        assert ACCESS_RECEIPT_KEYS["vault"] not in session


def test_server_issued_shape_can_open_only_its_exact_app_path(client):
    login(client)
    with client.session_transaction() as session:
        now = int(time.time())
        session[ACCESS_RECEIPT_KEYS["vault"]] = {
            "schema_version": "tower.ecosystem.access-receipt.v1",
            "app_id": "vault",
            "allowed": True,
            "owner_id": session["owner_id"],
            "tower_session_id": session["tower_session_id"],
            "issued_at_epoch": now,
            "expires_at_epoch": now + 300,
            "owner_session_preserved": True,
            "new_entitlement_granted": False,
            "dangerous_action_unlocked": False,
        }
    assert client.get("/vault").status_code == 200
    assert client.get("/grounds").status_code == 503


def test_tower_internal_archive_vault_route_is_not_caught_by_product_guard(client):
    login(client)
    response = client.get("/tower/archive-vault/acceptance-records.json")
    assert response.status_code == 200
    assert response.get_json() == {"tower_internal": True}


@pytest.mark.parametrize("app_id,last_room", [
    ("teller", "Payroll"),
    ("grounds", "My Home"),
    ("buybox", "Decision Desk"),
    ("vault", "Command Center"),
    ("clouds", "Owner Focus"),
])
def test_reciprocal_return_preserves_existing_owner_only(client, app_id, last_room):
    login(client)
    response = client.get(
        f"/tower/return/{app_id}",
        query_string={"last_room": last_room},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.location.endswith(ACCESS_HOME_PATH)
    with client.session_transaction() as session:
        receipt = session[f"tower_{app_id}_return_receipt"]
        assert receipt["app_id"] == app_id
        assert receipt["last_room"] == last_room
        assert receipt["owner_session_preserved"] is True
        assert receipt["new_entitlement_granted"] is False
        assert receipt["capital_movement"] is False
        assert receipt["tenant_access_granted"] is False
        assert f"tower_{app_id}_access_receipt" not in session


def test_return_route_rejects_untrusted_room_hint_into_unknown(client):
    login(client)
    client.get("/tower/return/buybox", query_string={
        "last_room": "<script>not-a-room</script>",
    })
    with client.session_transaction() as session:
        assert session["tower_buybox_return_receipt"]["last_room"] == "unknown"


def test_return_json_requires_owner_and_never_grants_app_access(client):
    anonymous = client.get("/tower/return/teller.json", follow_redirects=False)
    assert anonymous.status_code == 302
    login(client)
    response = client.get(
        "/tower/return/teller.json",
        query_string={"last_room": "Owner Money Workspace"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["allowed"] is True
    assert payload["owner_session_preserved"] is True
    assert payload["new_entitlement_granted"] is False
    with client.session_transaction() as session:
        assert "tower_teller_access_receipt" not in session


def test_access_receipt_helper_binds_current_owner_session_and_expires(client):
    login(client)
    with client.application.test_request_context("/"):
        # Move the real browser session into this context only through a request;
        # helper must never accept an anonymous context.
        with pytest.raises(ValueError):
            build_ecosystem_access_receipt("vault", now_epoch=1_800_000_000)

    # A stale receipt copied from another session must fail even when its app id
    # and booleans look right.
    with client.session_transaction() as session:
        now = int(time.time())
        session[ACCESS_RECEIPT_KEYS["clouds"]] = {
            "schema_version": "tower.ecosystem.access-receipt.v1",
            "app_id": "clouds",
            "allowed": True,
            "owner_id": session["owner_id"],
            "tower_session_id": "tower_session_from_some_other_browser",
            "issued_at_epoch": now,
            "expires_at_epoch": now + 300,
            "owner_session_preserved": True,
            "new_entitlement_granted": False,
            "dangerous_action_unlocked": False,
        }
    assert client.get("/clouds/status.json").status_code == 503
