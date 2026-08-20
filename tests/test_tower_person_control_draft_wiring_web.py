from flask import Flask

import tower.owner_person_control_draft_wiring as wiring


def build_app(monkeypatch):
    app = Flask(__name__)
    app.secret_key = "person-control-draft-wiring-test"

    monkeypatch.setattr(
        wiring,
        "owner_session_active",
        lambda: True,
    )

    @app.route(
        "/tower/owner-dashboard/person/<person_id>"
    )
    def person_room(person_id):
        return f"""
        <!doctype html>
        <html>
          <head></head>
          <body>
            <main>
              <section data-tower-person-control-room="true">
                <div class="tower-person-control-header">
                  <h2 class="tower-person-control-title">{person_id}</h2>
                  <div class="tower-person-control-chip-row"></div>
                </div>

                <div data-tower-drawer="designation">
                  <input value="">
                  <textarea></textarea>
                </div>

                <div data-tower-drawer="responsibility">
                  <textarea></textarea>
                </div>

                <div data-tower-drawer="access">
                  <input>
                  <input>
                  <textarea></textarea>
                </div>

                <div data-tower-drawer="freeze">
                  <textarea></textarea>
                </div>

                <div data-tower-drawer="restore">
                  <textarea></textarea>
                </div>
              </section>
            </main>
          </body>
        </html>
        """

    wiring.register_tower_person_control_draft_wiring(
        app
    )

    return app


def test_person_room_html_gets_wiring(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200

    assert "tower-person-control-draft-wiring-twr051-055" in body

    assert "Submit draft for owner review" in body

    assert "/control-draft" in body

    assert "/control-room.json" in body


def test_control_room_json_returns_real_profile(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat/control-room.json"
    )

    data = response.get_json()

    assert response.status_code == 200

    assert data["profile"]["display_name"] == "Future Manager Seat"

    assert data["safety"]["real_access_granted"] is False


def test_control_room_json_404_for_unknown(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().get(
        "/tower/owner-dashboard/person/not-real/control-room.json"
    )

    assert response.status_code == 404


def test_designation_control_draft(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/control-draft",
        json={
            "action": "designation",
            "requested_designation": "Manager",
            "notes": "Owner review",
        },
    )

    data = response.get_json()

    assert response.status_code == 200

    assert data["status"] == "person_control_draft_created"

    assert data["control_action"] == "designation"

    assert data["safety"]["changes_real_permissions"] is False


def test_app_access_control_draft(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-beta-tester-seat/control-draft",
        json={
            "action": "app_access",
            "app_name": "Observatory",
            "access_level": "View Only",
        },
    )

    data = response.get_json()

    assert response.status_code == 200

    assert data["draft"]["status"] == "app_access_change_draft_created"

    assert data["safety"]["grants_real_access"] is False


def test_invalid_action_returns_400(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/control-draft",
        json={
            "action": "become_root",
        },
    )

    data = response.get_json()

    assert response.status_code == 400

    assert data["status"] == "invalid_control_action"


def test_registration_is_idempotent(monkeypatch):
    app = build_app(monkeypatch)

    wiring.register_tower_person_control_draft_wiring(
        app
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    body = response.get_data(as_text=True)

    assert body.count(
        "tower-person-control-draft-wiring-twr051-055"
    ) == 1
