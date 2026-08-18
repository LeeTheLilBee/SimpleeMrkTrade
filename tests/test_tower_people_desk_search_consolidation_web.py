from flask import Flask

from tower.owner_people_search_consolidation import register_tower_people_search_consolidation


def build_app():
    app = Flask(__name__)
    app.secret_key = "tower-people-search-consolidation-test"

    @app.route("/tower/owner-dashboard")
    def fake_owner_dashboard():
        return """
        <!doctype html>
        <html>
          <head><title>People + Access Desk</title></head>
          <body>
            <nav id="tower-owner-back-nav">Back to Access Home</nav>

            <section id="existing-people-seats">
              <label>Search people</label>
              <input placeholder="Search people">
              <article>Future Manager Seat</article>
              <article>Future Family / Friend Seat</article>
              <article>Future Trustee / Advisor Seat</article>
              <article>Future Beta Tester Seat</article>
            </section>

            <section id="tower-people-room-dock">
              <h2>Click a name to control the room behind it.</h2>
              <a href="/tower/owner-dashboard/person/future-manager-seat">
                Future Manager Seat
              </a>
            </section>
          </body>
        </html>
        """

    @app.route("/tower/security-map")
    def fake_security_map():
        return "<html><body>Security Map</body></html>"

    @app.route("/other")
    def other():
        return "<html><body>Other</body></html>"

    register_tower_people_search_consolidation(app)

    return app


def test_owner_dashboard_consolidates_people_sections():
    app = build_app()

    response = app.test_client().get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Search people" in body
    assert "tower-people-room-dock" not in body
    assert "tower-people-search-note" in body
    assert "tower-people-name-room-link" in body
    assert "tower-people-open-room-chip" in body
    assert "/tower/owner-dashboard/person/future-manager-seat" in body
    assert "/tower/owner-dashboard/person/future-family-friend-seat" in body
    assert "/tower/owner-dashboard/person/future-trustee-advisor-seat" in body
    assert "/tower/owner-dashboard/person/future-beta-tester-seat" in body


def test_owner_dashboard_enhancement_is_idempotent():
    app = build_app()
    client = app.test_client()

    first = client.get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    ).get_data(as_text=True)

    second = client.get(
        "/tower/owner-dashboard",
        follow_redirects=False,
    ).get_data(as_text=True)

    assert first == second
    assert first.count("tower-people-search-consolidation-style") == 1
    assert first.count("tower-people-search-note") == 2


def test_security_map_not_modified():
    app = build_app()

    response = app.test_client().get(
        "/tower/security-map",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-search-note" not in body
    assert "tower-people-open-room-chip" not in body


def test_other_routes_not_modified():
    app = build_app()

    response = app.test_client().get(
        "/other",
        follow_redirects=False,
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-people-search-note" not in body
    assert "tower-people-open-room-chip" not in body
