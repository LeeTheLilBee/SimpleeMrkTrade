from flask import Flask

from tower.owner_person_control_room import (
    register_tower_person_control_room,
)


def build_app():
    app = Flask(__name__)

    app.secret_key = "tower-person-control-room-test"

    @app.route(
        "/tower/owner-dashboard/person/<person_id>"
    )
    def person_room(person_id):
        return f"""
        <!doctype html>
        <html>
          <head>
            <title>{person_id}</title>
          </head>
          <body>
            <main>
              <a href="/tower/owner-dashboard">
                Back to People + seats
              </a>

              <h1>
                Future Manager Seat
              </h1>

              <p>
                Existing person profile room.
              </p>
            </main>
          </body>
        </html>
        """

    @app.route(
        "/tower/owner-dashboard/person/<person_id>.json"
    )
    def person_json(person_id):
        return {
            "person_id": person_id,
        }

    @app.route(
        "/tower/owner-dashboard/person/<person_id>/designation-draft",
        methods=["POST"],
    )
    def designation_draft(person_id):
        return {
            "person_id": person_id,
            "draft": True,
        }

    @app.route(
        "/tower/security-map"
    )
    def security_map():
        return """
        <html>
          <body>
            Security Map
          </body>
        </html>
        """

    register_tower_person_control_room(
        app
    )

    return app


def test_person_html_room_gets_control_room():
    app = build_app()

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat",
        follow_redirects=False,
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert "tower-person-control-room-twr046-050" in body
    assert "tower-person-control-room-style-twr046-050" in body

    assert "Person Control Room" in body
    assert "Identity + designation" in body
    assert "Access" in body
    assert "Paperwork + notes" in body
    assert "Activity + history" in body
    assert "Owner actions" in body
    assert "Owner review chain" in body


def test_person_room_preserves_existing_back_link():
    app = build_app()

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat",
        follow_redirects=False,
    )

    body = response.get_data(
        as_text=True
    )

    assert "Back to People + seats" in body


def test_person_json_is_not_modified():
    app = build_app()

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat.json",
        follow_redirects=False,
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "tower-person-control-room-twr046-050" not in body


def test_designation_post_route_is_not_modified():
    app = build_app()

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/designation-draft",
        follow_redirects=False,
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "tower-person-control-room-twr046-050" not in body


def test_security_map_is_not_modified():
    app = build_app()

    response = app.test_client().get(
        "/tower/security-map",
        follow_redirects=False,
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert "tower-person-control-room-twr046-050" not in body


def test_registration_is_idempotent():
    app = build_app()

    register_tower_person_control_room(
        app
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat",
        follow_redirects=False,
    )

    body = response.get_data(
        as_text=True
    )

    assert body.count(
        "tower-person-control-room-twr046-050"
    ) == 1
