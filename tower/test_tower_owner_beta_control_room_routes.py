from __future__ import annotations

from web.app import app


def test_owner_beta_control_room_routes_registered():
    rules = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/tower/owner-beta" in rules
    assert "/tower/owner-beta.json" in rules


def test_owner_beta_control_room_json_route_requires_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/tower/owner-beta.json")

    assert response.status_code in {401, 403}

    payload = response.get_json()

    assert payload["status"] == "denied"
    assert payload["reason"] == "owner_session_required"


def test_owner_beta_control_room_json_route_payload_with_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"

    response = client.get("/tower/owner-beta.json")

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["version"] == "tower_owner_beta_control_room_v1"
    assert payload["staging_ready_for_owner_beta_walkthrough"] is True
    assert payload["owner_beta_control_room_ready"] is True
    assert all(value is False for value in payload["dangerous_controls"].values())


def test_owner_beta_control_room_html_route_requires_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    anon = client.get("/tower/owner-beta", follow_redirects=False)
    assert anon.status_code in {301, 302, 303, 401, 403}

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"

    response = client.get("/tower/owner-beta")

    assert response.status_code == 200
    text = response.get_data(as_text=True)

    assert "Tower Owner-Beta Control Room" in text
    assert "Owner beta is ready for walkthrough" in text
    assert "Manual Live locked" in text
