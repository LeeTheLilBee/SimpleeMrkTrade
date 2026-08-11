from __future__ import annotations

from web.app import app


def test_owner_beta_control_room_routes_registered():
    rules = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/tower/owner-beta" in rules
    assert "/tower/owner-beta.json" in rules


def test_owner_beta_control_room_json_route_payload():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/tower/owner-beta.json")

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["version"] == "tower_owner_beta_control_room_v1"
    assert payload["staging_ready_for_owner_beta_walkthrough"] is True
    assert payload["owner_beta_control_room_ready"] is True
    assert all(value is False for value in payload["dangerous_controls"].values())


def test_owner_beta_control_room_html_route():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/tower/owner-beta")

    assert response.status_code == 200
    text = response.get_data(as_text=True)

    assert "Tower Owner-Beta Control Room" in text
    assert "Owner beta is ready for walkthrough" in text
    assert "Manual Live locked" in text
