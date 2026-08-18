from flask import Flask

import tower.access_home_owner_launches as owner_launches


def build_app(monkeypatch, *, owner_session):
    app = Flask(__name__)
    app.secret_key = "tower-access-home-owner-launches-test"

    monkeypatch.setattr(
        owner_launches,
        "owner_session_active",
        lambda: owner_session,
    )

    @app.route("/tower/access-home")
    def fake_access_home():
        return """
        <!doctype html>
        <html>
          <body>
            <main>
              <h1>Existing Access Home</h1>
            </main>
          </body>
        </html>
        """

    @app.route("/not-access-home")
    def not_access_home():
        return """
        <!doctype html>
        <html>
          <body>
            <main>
              <h1>Different Page</h1>
            </main>
          </body>
        </html>
        """

    owner_launches.register_tower_access_home_owner_launches(app)

    return app


def test_access_home_injects_owner_dashboard_and_security_map_cards(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/access-home",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Existing Access Home" in body
    assert "tower-owner-launch-dock" in body
    assert "Owner Dashboard" in body
    assert "People + Access Desk" in body
    assert "/tower/owner-dashboard" in body
    assert "Security Map" in body
    assert "/tower/security-map" in body
    assert "no real accounts, invites, or access grants" in body


def test_injector_does_not_touch_other_pages(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/not-access-home",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Different Page" in body
    assert "tower-owner-launch-dock" not in body


def test_access_home_launches_json_redirects_without_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/access-home-launches.json",
        follow_redirects=False,
    )

    assert response.status_code in {
        301,
        302,
        303,
        307,
        308,
    }

    assert response.headers["Location"].endswith("/tower/login")


def test_access_home_launches_json_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/access-home-launches.json",
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["summary"]["status"] == "tower_access_home_owner_launches_ready"
    assert payload["summary"]["real_account_creation"] is False
    assert payload["summary"]["real_invites_sent"] is False
    assert payload["summary"]["real_access_granted"] is False

    routes = {
        launch["href"]
        for launch in payload["launches"]
    }

    assert "/tower/owner-dashboard" in routes
    assert "/tower/security-map" in routes


def test_register_access_home_owner_launches_is_idempotent(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    owner_launches.register_tower_access_home_owner_launches(app)

    response = app.test_client().get(
        "/tower/access-home-launches.json",
        follow_redirects=False,
    )

    assert response.status_code == 200
