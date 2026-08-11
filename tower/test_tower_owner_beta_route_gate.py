from __future__ import annotations

from web.app import app
from tower.tower_owner_beta_route_gate import (
    owner_beta_route_gate_cert,
    owner_beta_route_gate_contract,
)


def test_owner_beta_route_gate_contract():
    contract = owner_beta_route_gate_contract()

    assert contract["version"] == "tower_owner_beta_route_gate_v1"
    assert contract["requires_owner_session"] is True
    assert contract["requires_tower_boundary"] is True
    assert contract["routes"]["html"] == "/tower/owner-beta"
    assert contract["routes"]["json"] == "/tower/owner-beta.json"
    assert contract["dangerous_controls_locked"] is True
    assert all(value is False for value in contract["dangerous_controls"].values())


def test_anonymous_owner_beta_html_denied_or_redirected():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/tower/owner-beta", follow_redirects=False)

    assert response.status_code in {301, 302, 303, 401, 403}
    if response.status_code in {301, 302, 303}:
        assert "/tower/login" in response.headers.get("Location", "")


def test_anonymous_owner_beta_json_denied():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/tower/owner-beta.json")

    assert response.status_code in {401, 403}

    payload = response.get_json()
    assert payload["status"] == "denied"
    assert payload["reason"] == "owner_session_required"
    assert payload["route_gate"]["requires_owner_session"] is True
    assert payload["route_gate"]["dangerous_controls_locked"] is True


def test_owner_session_owner_beta_html_allowed():
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"

    response = client.get("/tower/owner-beta")

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Tower Owner-Beta Control Room" in text
    assert "Owner beta is ready for walkthrough" in text


def test_owner_session_owner_beta_json_allowed():
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"

    response = client.get("/tower/owner-beta.json")

    assert response.status_code == 200

    payload = response.get_json()
    assert payload["version"] == "tower_owner_beta_control_room_v1"
    assert payload["owner_beta_control_room_ready"] is True
    assert payload["staging_ready_for_owner_beta_walkthrough"] is True
    assert all(value is False for value in payload["dangerous_controls"].values())


def test_owner_beta_route_gate_certs_2563_to_2572():
    for pack in range(2563, 2573):
        cert = owner_beta_route_gate_cert(pack)

        assert cert["pack"] == pack
        assert cert["status"] == "passed"
        assert cert["requires_owner_session"] is True
        assert cert["requires_tower_boundary"] is True
        assert cert["dangerous_controls_locked"] is True
        assert cert["route"] == "/tower/owner-beta"
        assert cert["json_route"] == "/tower/owner-beta.json"
