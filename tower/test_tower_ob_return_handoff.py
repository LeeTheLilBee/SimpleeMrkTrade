"""Return navigation uses an existing verified owner session, never a new grant."""
from __future__ import annotations

from flask import Flask
import pytest

from tower.tower_access_home_ui_v2 import verify_return_receipt
from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH, LOGIN_PATH, LOGOUT_PATH, register_tower_human_login,
)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    monkeypatch.setenv("TOWER_OWNER_USERNAME", "fixture-owner")
    monkeypatch.setenv("TOWER_LOCAL_OWNER_PASSWORD", "fixture-password")
    monkeypatch.setenv("TOWER_SESSION_SECRET", "test-only-owner-session-secret")
    monkeypatch.setenv("TOWER_OWNER_ID", "fictional-owner-id")
    app = Flask(__name__)
    app.config.update(TESTING=True)
    register_tower_human_login(app)
    return app.test_client()


def login(client):
    response = client.post(
        LOGIN_PATH,
        data={"username": "fixture-owner", "password": "fixture-password"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.location.endswith(ACCESS_HOME_PATH)


def test_anonymous_cannot_record_return_receipt(client):
    response = client.get(
        "/tower/return/observatory?last_room=Trade%20Center",
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/tower/login" in response.location
    with client.session_transaction() as session:
        assert "tower_ob_return_receipt" not in session


@pytest.mark.parametrize("room", [
    "Dashboard", "Market Map", "Trade Center", "Review Center",
    "Owner Console", "Owner Dashboard", "Symbol Page",
])
def test_owner_return_preserves_session_with_bounded_receipt(client, room):
    from urllib.parse import urlencode
    login(client)
    response = client.get(
        "/tower/return/observatory?" + urlencode({"last_room": room}),
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.location.endswith(ACCESS_HOME_PATH)
    with client.session_transaction() as session:
        receipt = session["tower_ob_return_receipt"]
        assert receipt["last_room"] == room
        assert receipt["owner_session_preserved"] is True
        assert receipt["clearance_preserved"] is True
        assert receipt["destination"] == ACCESS_HOME_PATH
        assert verify_return_receipt(receipt) is True
        assert receipt["broker_submission"] is False
        assert receipt["capital_movement"] is False
        assert receipt["manual_live_authorized"] is False
        assert receipt["live_auto_authorized"] is False
        assert session["tower_authenticated"] is True
    home = client.get(ACCESS_HOME_PATH)
    assert home.status_code == 200
    assert "Verified return receipt" in home.get_data(as_text=True)


@pytest.mark.parametrize("unsafe", [
    "<script>alert(1)</script>", "X" * 5000, "/ob/trade-center", "", "unknown",
])
def test_untrusted_last_room_is_only_a_navigation_hint(client, unsafe):
    login(client)
    response = client.get(
        "/tower/return/observatory",
        query_string={"last_room": unsafe},
        follow_redirects=False,
    )
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["tower_ob_return_receipt"]["last_room"] == "unknown"
    home = client.get(ACCESS_HOME_PATH)
    if unsafe not in ("", "unknown"):
        assert unsafe not in home.get_data(as_text=True)


def test_return_json_cannot_be_used_anonymously_and_never_authorizes_actions(client):
    unauth = client.get("/tower/return/observatory.json?last_room=Review%20Center")
    assert unauth.status_code == 302
    login(client)
    response = client.get("/tower/return/observatory.json?last_room=Review%20Center")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["return_receipt"]["last_room"] == "Review Center"
    for key in ("dangerous_action_unlocked", "broker_submission",
                "capital_movement", "manual_live_authorized", "live_auto_authorized"):
        assert payload[key] is False


def test_logout_revokes_owner_session_and_return_route_requires_new_login(client):
    login(client)
    client.get("/tower/return/observatory?last_room=Dashboard")
    client.get(LOGOUT_PATH)
    response = client.get("/tower/return/observatory?last_room=Dashboard")
    assert response.status_code == 302
    assert "/tower/login" in response.location
    with client.session_transaction() as session:
        assert "tower_ob_return_receipt" not in session
