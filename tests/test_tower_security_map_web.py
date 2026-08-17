from flask import Flask

import tower.security_map_web as security_map_web


def build_app(monkeypatch, *, owner_session):
    app = Flask(__name__)
    app.secret_key = "tower-security-map-web-test"

    monkeypatch.setattr(
        security_map_web,
        "owner_session_active",
        lambda: owner_session,
    )

    security_map_web.register_tower_security_map_routes(app)

    return app


def test_security_map_page_redirects_without_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/security-map",
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


def test_security_map_json_redirects_without_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/security-map.json",
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


def test_security_map_page_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/security-map",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Tower · Security Map" in body
    assert "The lock map is visible now." in body
    assert "/ob/owner-console" in body
    assert "/ob/owner-dashboard" in body
    assert "Live Auto" in body or "Danger locks" in body


def test_security_map_json_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/security-map.json",
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["summary"]["status"] == "tower_security_map_ready"
    assert payload["summary"]["live_auto"] == "LOCKED"
    assert payload["danger_locks"]["broker_execution"] is False
    assert "/ob/owner-dashboard" in payload["route_groups"]["owner_only"]


def test_register_security_map_routes_is_idempotent(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    security_map_web.register_tower_security_map_routes(app)

    response = app.test_client().get(
        "/tower/security-map.json",
        follow_redirects=False,
    )

    assert response.status_code == 200
