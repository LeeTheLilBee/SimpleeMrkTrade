"""Only independently verified hosted truth may appear as a Tower launch action."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from flask import Flask

from tower.ecosystem_integration_desk import (
    INTEGRATION_DESK_PATH, INTEGRATION_DESK_JSON_PATH,
    integration_desk_snapshot, register_tower_integration_desk,
)
from tower.tower_human_login_ob_launch import register_tower_human_login


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    monkeypatch.setenv("TOWER_OWNER_USERNAME", "fictional-owner")
    monkeypatch.setenv("TOWER_LOCAL_OWNER_PASSWORD", "synthetic-not-production")
    monkeypatch.setenv("TOWER_SESSION_SECRET", "test-only-session-secret")
    monkeypatch.setenv("TOWER_OWNER_ID", "fictional-owner-id")
    app = Flask(__name__)
    app.config.update(TESTING=True)
    register_tower_human_login(app)
    register_tower_integration_desk(app)
    return app.test_client()


def _login(client):
    assert client.post("/tower/login", data={
        "username": "fictional-owner",
        "password": "synthetic-not-production",
    }).status_code == 302


@pytest.mark.parametrize("path", [INTEGRATION_DESK_PATH, INTEGRATION_DESK_JSON_PATH])
def test_anonymous_desk_denied_before_truth_invocation(client, path):
    with patch("tower.ecosystem_integration_desk.app_truth_by_id") as truth:
        response = client.get(path)
    assert response.status_code == 302
    assert "/tower/login" in response.location
    truth.assert_not_called()


def test_authenticated_runtime_truth_is_not_a_false_future_launch(client):
    _login(client)
    with patch("tower.ecosystem_integration_desk.app_truth_by_id", return_value={"launchable": True}):
        result = client.get(INTEGRATION_DESK_JSON_PATH)
    assert result.status_code == 200
    assert result.headers["Cache-Control"].startswith("no-store")
    data = result.get_json()
    apps = {a["app_id"]: a for a in data["systems"]}
    assert set(apps) >= {"observatory", "teller", "grounds", "buybox", "vault", "clouds"}
    for name in ("grounds", "buybox", "vault", "clouds"):
        assert apps[name]["launchable"] is False
        assert apps[name]["state"] == "BLOCKED_EXTERNAL_INTEGRATION"
        assert apps[name]["tower_launch_route"] is None
        assert apps[name]["owner_acceptance_verified"] is False
        assert apps[name]["separate_product_runtime_activated"] is False
    for name in ("observatory", "teller"):
        assert apps[name]["launchable"] is True
        assert apps[name]["tower_launch_route"].startswith("/tower/launch/")
        assert apps[name]["owner_acceptance_verified"] is False
    assert data["grants_issued"] is False
    assert data["external_calls_made"] is False


def test_provider_error_degrades_to_blocked_without_secret_error_or_launch(client):
    _login(client)
    with patch("tower.ecosystem_integration_desk.app_truth_by_id", side_effect=RuntimeError("do-not-show-private-provider-secret")):
        html = client.get(INTEGRATION_DESK_PATH)
        json_response = client.get(INTEGRATION_DESK_JSON_PATH)
    assert html.status_code == json_response.status_code == 200
    assert "do-not-show-private-provider-secret" not in html.get_data(as_text=True)
    assert "do-not-show-private-provider-secret" not in json_response.get_data(as_text=True)
    assert "Grounds" in html.get_data(as_text=True)
    assert "BuyBox" in html.get_data(as_text=True)
    assert "/tower/access-home" in html.get_data(as_text=True)
    assert all(x["launchable"] is False for x in json_response.get_json()["systems"])


def test_owner_access_home_offers_desk_but_no_grounds_or_buybox_launch(client):
    _login(client)
    html = client.get("/tower/access-home").get_data(as_text=True)
    assert 'href="/tower/integrations"' in html
    assert 'href="/tower/launch/grounds"' not in html
    assert 'href="/tower/launch/buybox"' not in html
