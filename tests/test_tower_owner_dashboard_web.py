from flask import Flask

import tower.owner_dashboard_web as owner_dashboard_web


def build_app(monkeypatch, *, owner_session):
    app = Flask(__name__)
    app.secret_key = "tower-owner-dashboard-web-test"

    monkeypatch.setattr(
        owner_dashboard_web,
        "owner_session_active",
        lambda: owner_session,
    )

    owner_dashboard_web.register_tower_owner_dashboard_routes(app)

    return app


def test_owner_dashboard_page_redirects_without_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert response.headers["Location"].endswith(
        "/tower/login"
    )


def test_owner_dashboard_json_redirects_without_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard.json",
        follow_redirects=False,
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert response.headers["Location"].endswith(
        "/tower/login"
    )


def test_owner_dashboard_page_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Tower · Owner Dashboard" in body
    assert "The owner desk is coming online." in body
    assert "People + seats" in body
    assert "Invite drafts" in body
    assert "Access requests" in body
    assert "Future Manager Seat" in body
    assert "Future Family / Friend Seat" in body
    assert "cannot create real accounts" in body


def test_owner_dashboard_json_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard.json",
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["summary"]["status"] == "tower_owner_dashboard_ready"
    assert payload["summary"]["real_account_creation"] is False
    assert payload["summary"]["real_invites_sent"] is False
    assert payload["summary"]["real_access_granted"] is False
    assert payload["danger_locks"]["broker_execution"] is False
    assert payload["danger_locks"]["capital_action"] is False


def test_register_owner_dashboard_routes_is_idempotent(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    owner_dashboard_web.register_tower_owner_dashboard_routes(app)

    response = app.test_client().get(
        "/tower/owner-dashboard.json",
        follow_redirects=False,
    )

    assert response.status_code == 200
