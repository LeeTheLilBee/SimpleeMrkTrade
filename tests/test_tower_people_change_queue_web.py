from flask import Flask

import tower.owner_people_change_queue as change_queue


def build_app(monkeypatch, *, owner_session):
    app = Flask(__name__)
    app.secret_key = "tower-change-queue-test"

    monkeypatch.setattr(
        change_queue,
        "owner_session_active",
        lambda: owner_session,
    )

    @app.route("/tower/owner-dashboard")
    def fake_owner_dashboard():
        return """
        <!doctype html>
        <html>
          <body>
            <div id="tower-people-search-note">
              People + seats stays search-first.
            </div>
          </body>
        </html>
        """

    @app.route("/other")
    def other():
        return "<html><body>Other</body></html>"

    change_queue.register_tower_people_change_queue(app)

    return app


def test_owner_dashboard_gets_small_change_queue_controls(monkeypatch):
    app = build_app(monkeypatch, owner_session=True)

    response = app.test_client().get("/tower/owner-dashboard")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-change-queue-controls" in body
    assert "/tower/owner-dashboard/person-drafts.json" in body
    assert "/tower/owner-dashboard/change-queue.json" in body


def test_other_route_not_modified(monkeypatch):
    app = build_app(monkeypatch, owner_session=True)

    response = app.test_client().get("/other")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-change-queue-controls" not in body


def test_person_drafts_json_requires_owner(monkeypatch):
    app = build_app(monkeypatch, owner_session=False)

    response = app.test_client().get("/tower/owner-dashboard/person-drafts.json")

    assert response.status_code in {301, 302, 303, 307, 308}
    assert response.headers["Location"].endswith("/tower/login")


def test_change_queue_json_requires_owner(monkeypatch):
    app = build_app(monkeypatch, owner_session=False)

    response = app.test_client().get("/tower/owner-dashboard/change-queue.json")

    assert response.status_code in {301, 302, 303, 307, 308}
    assert response.headers["Location"].endswith("/tower/login")


def test_person_drafts_json_for_owner(monkeypatch):
    app = build_app(monkeypatch, owner_session=True)

    response = app.test_client().get("/tower/owner-dashboard/person-drafts.json")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["summary"]["status"] == "tower_people_change_queue_ready"
    assert payload["safety"]["real_account_creation"] is False
    assert len(payload["drafts"]) >= 2


def test_change_queue_json_for_owner(monkeypatch):
    app = build_app(monkeypatch, owner_session=True)

    response = app.test_client().get("/tower/owner-dashboard/change-queue.json")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["summary"]["status"] == "tower_people_change_queue_ready"
    assert payload["safety"]["real_permission_changes"] is False
    assert len(payload["queue"]) >= 2


def test_create_person_draft_endpoint_is_safe(monkeypatch):
    app = build_app(monkeypatch, owner_session=True)

    response = app.test_client().post(
        "/tower/owner-dashboard/person-draft",
        json={
            "display_name": "Azzarah Williams",
            "relationship": "Family",
            "requested_designation": "Family",
        },
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "add_person_draft_created"
    assert payload["creates_real_account"] is False
    assert payload["grants_real_access"] is False


def test_create_change_queue_endpoint_is_safe(monkeypatch):
    app = build_app(monkeypatch, owner_session=True)

    response = app.test_client().post(
        "/tower/owner-dashboard/change-queue",
        json={
            "person_id": "future-manager-seat",
            "display_name": "Future Manager Seat",
            "change_type": "designation",
            "requested_change": "Review Manager designation",
        },
    )

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["status"] == "change_queue_item_created"
    assert payload["grants_real_access"] is False
    assert payload["changes_real_permissions"] is False
