from tower.owner_people_combined_rooms import (
    COMBINED_PEOPLE_ROOMS_MARKER,
    combined_people_rooms_summary,
    inject_combined_people_rooms,
)


def test_combined_people_rooms_summary_is_safe():
    summary = combined_people_rooms_summary()

    assert summary["status"] == "tower_people_seats_rooms_combined_ready"
    assert summary["product_rule"] == "people_seats_is_the_roster_and_room_hub"
    assert summary["people_rooms_separate_homepage_block_removed"] is True
    assert summary["people_seats_roster_preserved"] is True
    assert summary["inline_room_controls_added"] is True
    assert summary["full_person_room_routes_preserved"] is True
    assert summary["search_preserved"] is True
    assert summary["draft_queue_preserved"] is True
    assert summary["back_buttons_preserved"] is True
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_inject_combined_people_rooms_adds_script_and_style():
    html = """
    <!doctype html>
    <html>
      <head></head>
      <body>
        <section>
          <h2>People + seats</h2>
          <article>
            <a class="tower-people-name-room-link" href="/tower/owner-dashboard/person/future-manager-seat">
              Future Manager Seat
            </a>
          </article>
        </section>
      </body>
    </html>
    """

    injected = inject_combined_people_rooms(html)

    assert COMBINED_PEOPLE_ROOMS_MARKER in injected
    assert "tower-combine-people-seats-rooms-style-twr036-040" in injected
    assert "people-seats-roster-is-room-hub" in injected
    assert "data-tower-inline-room-panel" in injected
    assert "Room details" in injected


def test_inject_combined_people_rooms_is_idempotent():
    html = "<html><head></head><body><main>Owner Dashboard</main></body></html>"

    once = inject_combined_people_rooms(html)
    twice = inject_combined_people_rooms(once)

    assert once == twice
    assert once.count(COMBINED_PEOPLE_ROOMS_MARKER) == 1


def test_script_preserves_full_person_room_routes():
    html = "<html><head></head><body></body></html>"
    injected = inject_combined_people_rooms(html)

    assert "/tower/owner-dashboard/person/" in injected
    assert "Open full room" in injected
    assert "slugFromHref" in injected


def test_script_hides_separate_people_rooms_blocks():
    html = "<html><head></head><body></body></html>"
    injected = inject_combined_people_rooms(html)

    assert "hideSeparatePeopleRoomsBlocks" in injected
    assert "data-tower-hidden-separate-people-rooms" in injected
    assert "people rooms" in injected
    assert "person rooms" in injected
    assert "room dock" in injected


def test_script_keeps_safety_language():
    html = "<html><head></head><body></body></html>"
    injected = inject_combined_people_rooms(html)

    assert "Nothing here creates accounts" in injected
    assert "sends invites" in injected
    assert "grants access" in injected
    assert "changes real permissions" in injected
