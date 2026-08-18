from flask import Flask

import tower.owner_people_profile_rooms as profile_rooms


def build_app(monkeypatch, *, owner_session):
    app = Flask(__name__)
    app.secret_key = "tower-people-profile-rooms-test"

    monkeypatch.setattr(
        profile_rooms,
        "owner_session_active",
        lambda: owner_session,
    )

    @app.route("/tower/owner-dashboard")
    def fake_owner_dashboard():
        return """
        <!doctype html>
        <html>
          <body>
            <main>
              <h1>Tower Owner Dashboard</h1>
            </main>
          </body>
        </html>
        """

    @app.route("/tower/security-map")
    def fake_security_map():
        return """
        <!doctype html>
        <html>
          <body>
            <main>
              <h1>Tower Security Map</h1>
            </main>
          </body>
        </html>
        """

    @app.route("/other")
    def other():
        return "<html><body>Other</body></html>"

    profile_rooms.register_tower_people_profile_rooms(app)

    return app


def test_owner_dashboard_gets_back_nav_and_people_room_dock(monkeypatch):
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
    assert "tower-owner-back-nav" in body
    assert "tower-people-room-dock" in body
    assert "Click a name to control the room behind it." in body
    assert "/tower/access-home" in body
    assert "/tower/security-map" in body
    assert "/tower/owner-dashboard/person/future-manager-seat" in body


def test_security_map_gets_back_nav_only(monkeypatch):
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
    assert "tower-owner-back-nav" in body
    assert "/tower/access-home" in body
    assert "/tower/owner-dashboard" in body
    assert "tower-people-room-dock" not in body


def test_other_pages_are_not_injected(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/other",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-owner-back-nav" not in body
    assert "tower-people-room-dock" not in body


def test_people_json_requires_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/people.json",
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


def test_people_json_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/people.json",
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["summary"]["status"] == "tower_people_profile_rooms_ready"
    assert payload["summary"]["real_access_granted"] is False
    assert len(payload["people"]) >= 4


def test_person_room_requires_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=False,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat",
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


def test_person_room_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Future Manager Seat" in body
    assert "Designation controls" in body
    assert "App access matrix" in body
    assert "Danger locks" in body
    assert "draft-only controls" in body
    assert "/tower/owner-dashboard/person/future-manager-seat.json" in body


def test_person_json_renders_for_owner_session(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat.json",
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "person_profile_room_ready"
    assert payload["profile"]["display_name"] == "Future Manager Seat"
    assert payload["safety"]["real_access_granted"] is False
    assert payload["safety"]["real_permission_changes"] is False


def test_designation_draft_endpoint_is_safe(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/designation-draft",
        json={
            "designation": "Manager",
            "notes": "Later manager role.",
        },
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "designation_change_draft_created"
    assert payload["requested_designation"] == "Manager"
    assert payload["grants_real_access"] is False
    assert payload["changes_real_permissions"] is False


def test_app_access_draft_endpoint_is_safe(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-beta-tester-seat/app-access-draft",
        json={
            "app_name": "Observatory",
            "access_level": "Owner Review Required",
            "notes": "Beta only later.",
        },
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "app_access_change_draft_created"
    assert payload["app_name"] == "Observatory"
    assert payload["requested_access_level"] == "Owner Review Required"
    assert payload["grants_real_access"] is False
    assert payload["changes_real_permissions"] is False


def test_freeze_draft_endpoint_is_safe(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-family-friend-seat/freeze-draft",
        json={
            "reason": "Pause until paperwork exists.",
        },
        follow_redirects=False,
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "person_freeze_draft_created"
    assert payload["freezes_real_access"] is False
    assert payload["grants_real_access"] is False
    assert payload["changes_real_permissions"] is False


def test_register_people_profile_rooms_is_idempotent(monkeypatch):
    app = build_app(
        monkeypatch,
        owner_session=True,
    )

    profile_rooms.register_tower_people_profile_rooms(app)

    response = app.test_client().get(
        "/tower/owner-dashboard/people.json",
        follow_redirects=False,
    )

    assert response.status_code == 200
