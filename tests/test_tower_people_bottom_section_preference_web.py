from flask import Flask

from tower.owner_people_bottom_section_preference import (
    register_tower_bottom_people_seats_preference,
)


def build_app():
    app = Flask(__name__)
    app.secret_key = "tower-bottom-people-section-test"

    @app.route("/tower/owner-dashboard")
    def owner_dashboard():
        return """
        <!doctype html>
        <html>
          <head><title>People + Access Desk</title></head>
          <body>
            <nav id="tower-owner-back-nav">Back to Access Home</nav>

            <section id="top-people-seats">
              <h2>People + seats</h2>
              <p>Old top block that Solice does not want.</p>
            </section>

            <section id="tower-people-change-queue-controls">
              <strong>Draft queue</strong>
            </section>

            <section id="bottom-people-seats">
              <h2>People + seats</h2>
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
          </body>
        </html>
        """

    @app.route("/tower/security-map")
    def security_map():
        return "<html><body>Security Map</body></html>"

    @app.route("/other")
    def other():
        return "<html><body>Other</body></html>"

    register_tower_bottom_people_seats_preference(app)

    return app


def test_owner_dashboard_gets_bottom_preference_script_and_style():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-keep-bottom-people-seats-search-twr031-035" in body
    assert "tower-bottom-people-seats-search-style-twr031-035" in body
    assert "var keptSection = candidates[candidates.length - 1]" in body
    assert "ensureSearchBar(keptSection)" in body
    assert "Search people + seats" in body
    assert "top-hidden-bottom-kept-search-ready" in body


def test_owner_dashboard_preserves_person_links_and_draft_queue_markup():
    app = build_app()

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert "tower-people-change-queue-controls" in body
    assert "tower-people-name-room-link" in body
    assert "tower-people-open-room-chip" in body
    assert "/tower/owner-dashboard/person/future-manager-seat" in body
    assert "/tower/owner-dashboard/person/future-family-friend-seat" in body


def test_security_map_is_not_modified():
    app = build_app()

    response = app.test_client().get("/tower/security-map", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-keep-bottom-people-seats-search-twr031-035" not in body
    assert "tower-bottom-people-seats-search-style-twr031-035" not in body


def test_other_route_is_not_modified():
    app = build_app()

    response = app.test_client().get("/other", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-keep-bottom-people-seats-search-twr031-035" not in body
    assert "tower-bottom-people-seats-search-style-twr031-035" not in body


def test_registration_is_idempotent():
    app = build_app()

    register_tower_bottom_people_seats_preference(app)

    response = app.test_client().get("/tower/owner-dashboard", follow_redirects=False)
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert body.count("tower-keep-bottom-people-seats-search-twr031-035") == 1
