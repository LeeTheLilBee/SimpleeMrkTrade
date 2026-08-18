from flask import Flask

from tower.owner_people_combined_rooms import register_tower_people_combined_rooms


def build_app():
    app = Flask(__name__)
    app.secret_key = "tower-combine-people-rooms-test"

    @app.route("/tower/owner-dashboard")
    def owner_dashboard():
        return """
        <!doctype html>
        <html>
          <head><title>People + Access Desk</title></head>
          <body>
            <nav id="tower-owner-back-nav">Back to Access Home</nav>

            <section id="bottom-people-seats">
              <h2>People + seats</h2>
              <input type="search" placeholder="Search people + seats">
              <article>
                <a class="tower-people-name-room-link" href="/tower/owner-dashboard/person/future-manager-seat">
                  Future Manager Seat
                </a>
                <a class="tower-people-open-room-chip" href="/tower/owner-dashboard/person/future-manager-seat">
                  Open room
                </a>
              </article>
            </section>

            <section id="separate-people-rooms">
              <h2>People Rooms</h2>
              <p>Separate room dock should be hidden by the combined rule.</p>
            </section>

            <section id="tower-people-change-queue-controls">
              <strong>Draft queue</strong>
            </section>
          </body>
        </html>
        """

    @app.route("/tower/security-map")
    def security_map():
        return "<html><body>Security Map</body></html>"

    @app.route("/other")
    def other():
        return "<html><body>Other</body></html>"

    register_tower_people_combined_rooms(app)

    return app


def test_owner_dashboard_gets_combined_people_rooms_script_and_style():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-combine-people-seats-rooms-twr036-040" in body
    assert "tower-combine-people-seats-rooms-style-twr036-040" in body
    assert "people-seats-roster-is-room-hub" in body
    assert "tower-inline-room-panel" in body
    assert "Room details" in body


def test_owner_dashboard_preserves_search_links_and_draft_queue():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert "input type=\"search\"" in body
    assert "tower-people-name-room-link" in body
    assert "tower-people-open-room-chip" in body
    assert "/tower/owner-dashboard/person/future-manager-seat" in body
    assert "tower-people-change-queue-controls" in body


def test_owner_dashboard_has_hide_rule_for_separate_people_rooms():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert "data-tower-hidden-separate-people-rooms" in body
    assert "hideSeparatePeopleRoomsBlocks" in body


def test_security_map_is_not_modified():
    app = build_app()

    response = app.test_client().get("/tower/security-map", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-combine-people-seats-rooms-twr036-040" not in body


def test_other_route_is_not_modified():
    app = build_app()

    response = app.test_client().get("/other", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-combine-people-seats-rooms-twr036-040" not in body


def test_registration_is_idempotent():
    app = build_app()

    register_tower_people_combined_rooms(app)

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert body.count("tower-combine-people-seats-rooms-twr036-040") == 1
