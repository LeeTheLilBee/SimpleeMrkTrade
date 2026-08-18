from flask import Flask

from tower.owner_people_real_desk import register_tower_people_real_desk


def build_app():
    app = Flask(__name__)
    app.secret_key = "tower-real-people-desk-test"

    @app.route("/tower/owner-dashboard")
    def owner_dashboard():
        return """
        <!doctype html>
        <html>
          <head><title>People + Access Desk</title></head>
          <body>
            <nav id="tower-owner-back-nav">Back to Access Home</nav>

            <section data-tower-keep-bottom-people-seats="true" id="bottom-people-seats">
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
              <article>
                <a class="tower-people-name-room-link" href="/tower/owner-dashboard/person/future-family-friend-seat">
                  Future Family / Friend Seat
                </a>
                <a class="tower-people-open-room-chip" href="/tower/owner-dashboard/person/future-family-friend-seat">
                  Open room
                </a>
              </article>
            </section>

            <section id="tower-people-change-queue-controls">
              <strong>Draft Queue</strong>
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

    register_tower_people_real_desk(app)

    return app


def test_owner_dashboard_gets_real_desk_script_and_style():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-seats-real-desk-twr041-045" in body
    assert "tower-people-seats-real-desk-style-twr041-045" in body
    assert "people-seats-real-desk-ready" in body
    assert "data-tower-real-people-toolbar" in body
    assert "Add person draft" in body


def test_owner_dashboard_preserves_search_people_links_and_queue():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert "input type=\"search\"" in body
    assert "tower-people-name-room-link" in body
    assert "tower-people-open-room-chip" in body
    assert "/tower/owner-dashboard/person/future-manager-seat" in body
    assert "/tower/owner-dashboard/person/future-family-friend-seat" in body
    assert "tower-people-change-queue-controls" in body


def test_owner_dashboard_has_filters_categories_and_safety():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert "Family/Friends" in body
    assert "Managers" in body
    assert "Employees" in body
    assert "Vendors" in body
    assert "Advisors" in body
    assert "Trustees/Admin" in body
    assert "Beta testers" in body
    assert "Future seats" in body
    assert "Draft only" in body
    assert "does not create an account" in body


def test_security_map_is_not_modified():
    app = build_app()

    response = app.test_client().get("/tower/security-map", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-seats-real-desk-twr041-045" not in body


def test_other_route_is_not_modified():
    app = build_app()

    response = app.test_client().get("/other", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-seats-real-desk-twr041-045" not in body


def test_registration_is_idempotent():
    app = build_app()

    register_tower_people_real_desk(app)

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert body.count("tower-people-seats-real-desk-twr041-045") == 1
