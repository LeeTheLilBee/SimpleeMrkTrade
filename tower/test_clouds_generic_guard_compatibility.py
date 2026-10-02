from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

from tower.ecosystem_direct_route_guard import register_ecosystem_direct_route_guard
from tower.ecosystem_return_routes import register_ecosystem_return_routes
from tower.tower_clouds_native_launch import (
    CLOUDS_ACCESS_PATH,
    CLOUDS_HOME_PATH,
    CLOUDS_RETURN_PATH,
    SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF,
    register_tower_clouds_native_launch,
)
from tower.tower_human_login_ob_launch import (
    LOGIN_PATH, register_tower_human_login,
)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "true")
    monkeypatch.setenv("TOWER_OWNER_USERNAME", "fixture-owner")
    monkeypatch.setenv("TOWER_LOCAL_OWNER_PASSWORD", "fixture-password")
    monkeypatch.setenv("TOWER_SESSION_SECRET", "fixture-clouds-session-secret-long-enough")
    monkeypatch.setenv("TOWER_OWNER_ID", "tower_owner_clouds_fixture_000001")

    app = Flask(__name__)
    app.config.update(TESTING=True)
    register_tower_human_login(app)
    register_tower_clouds_native_launch(app)
    register_ecosystem_direct_route_guard(app)
    register_ecosystem_return_routes(app)

    @app.get("/vault")
    def vault_fixture():
        return "must remain blocked"

    return app.test_client()


def login(client):
    response = client.post(
        LOGIN_PATH,
        data={"username": "fixture-owner", "password": "fixture-password"},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_generic_guard_does_not_break_existing_clouds_tower_launch(client):
    login(client)

    # No browser can open Clouds solely from source registration.
    direct = client.get(CLOUDS_HOME_PATH, follow_redirects=False)
    assert direct.status_code in {403, 503}

    with client.session_transaction() as session:
        session["tower_step_up_until"] = (
            datetime.now(timezone.utc) + timedelta(minutes=10)
        ).isoformat()

    launch = client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)
    assert launch.status_code == 302
    assert launch.location.endswith(CLOUDS_HOME_PATH)

    with client.session_transaction() as session:
        assert SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF in session
        # Existing Clouds contract is authoritative; generic receipt is absent.
        assert "tower_clouds_access_receipt" not in session

    opened = client.get(CLOUDS_HOME_PATH)
    assert opened.status_code == 200
    assert opened.headers["x-tower-clouds-pack1"] == "canonical-owner-command"
    assert "The Clouds" in opened.get_data(as_text=True)


def test_existing_clouds_return_route_is_not_duplicated(client):
    rules = [
        rule for rule in client.application.url_map.iter_rules()
        if rule.rule == CLOUDS_RETURN_PATH
    ]
    assert len(rules) == 1

    login(client)
    with client.session_transaction() as session:
        session["tower_step_up_until"] = (
            datetime.now(timezone.utc) + timedelta(minutes=10)
        ).isoformat()
    client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)

    returned = client.get(CLOUDS_RETURN_PATH, follow_redirects=False)
    assert returned.status_code == 302
    assert returned.location.endswith("/tower/access-home")
    with client.session_transaction() as session:
        receipt = session["tower_clouds_return_receipt"]
        assert receipt["receipt_type"] == "tower_clouds_return_receipt"
        assert receipt["tower_session_preserved"] is True
        assert receipt["downstream_execution_performed"] is False


def test_other_future_app_remains_blocked_after_clouds_handoff(client):
    login(client)
    with client.session_transaction() as session:
        session["tower_step_up_until"] = (
            datetime.now(timezone.utc) + timedelta(minutes=10)
        ).isoformat()
    client.get(CLOUDS_ACCESS_PATH, follow_redirects=False)
    assert client.get("/vault").status_code == 503
