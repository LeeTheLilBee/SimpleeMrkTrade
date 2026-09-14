
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

    owner_dashboard_web.register_tower_owner_dashboard_routes(
        app
    )

    return app


def test_owner_dashboard_page_redirects_without_owner_session(
    monkeypatch,
):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    )

    assert response.status_code in {
        301, 302, 303, 307, 308,
    }

    assert response.headers["Location"].endswith(
        "/tower/login"
    )


def test_owner_dashboard_json_redirects_without_owner_session(
    monkeypatch,
):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard.json",
        follow_redirects=False,
    )

    assert response.status_code in {
        301, 302, 303, 307, 308,
    }

    assert response.headers["Location"].endswith(
        "/tower/login"
    )


def test_owner_dashboard_page_renders_truthful_owner_headquarters(
    monkeypatch,
):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200
    assert "Tower · Owner Dashboard" in body
    assert "Owner Headquarters" in body
    assert "People &amp; access" in body or "People & access" in body
    assert "NOT_CONFIGURED" in body
    assert "Open release review" in body

    assert "Future Manager Seat" not in body
    assert "Future Family / Friend Seat" not in body
    assert "Invite drafts" not in body
    assert "/tower/owner/release-review/walkthrough" not in body


def test_owner_dashboard_json_reports_unknown_counts_not_fake_zero(
    monkeypatch,
):
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

    summary = payload["summary"]

    assert (
        summary["status"]
        == "tower_owner_dashboard_authority_not_configured"
    )

    assert summary["people_count"] is None
    assert summary["invitation_count"] is None
    assert summary["pending_access_count"] is None

    assert summary["people_authority_state"] == "NOT_CONFIGURED"
    assert summary["invitation_authority_state"] == "NOT_CONFIGURED"
    assert summary["access_authority_state"] == "NOT_CONFIGURED"

    assert payload["people"] == []
    assert payload["access_requests"] == []

    assert payload["danger_locks"]["live_auto"] == "LOCKED"
    assert payload["danger_locks"]["broker_execution"] is False
    assert payload["danger_locks"]["capital_action"] is False
    assert payload["danger_locks"]["release_execution"] is False


def test_register_owner_dashboard_routes_is_idempotent(
    monkeypatch,
):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    owner_dashboard_web.register_tower_owner_dashboard_routes(
        app
    )

    response = app.test_client().get(
        "/tower/owner-dashboard.json",
        follow_redirects=False,
    )

    assert response.status_code == 200
