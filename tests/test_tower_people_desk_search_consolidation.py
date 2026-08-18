from tower.owner_people_search_consolidation import (
    add_people_search_note,
    enhance_preferred_people_search_section,
    people_search_consolidation_summary,
    preferred_people_room_links,
    remove_duplicate_people_rooms_dock,
)


def test_people_search_consolidation_summary_is_safe():
    summary = people_search_consolidation_summary()

    assert summary["status"] == "tower_people_desk_search_consolidation_ready"
    assert summary["homepage_policy"] == "one_people_section_search_first"
    assert summary["preferred_home_surface"] == "existing_people_and_seats_search_section"
    assert summary["duplicate_people_rooms_dock_removed"] is True
    assert summary["person_names_clickable"] is True
    assert summary["open_room_chips_added"] is True
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_preferred_people_room_links_include_current_staged_people():
    links = preferred_people_room_links()

    labels = {
        link["label"]
        for link in links
    }

    assert "Future Manager Seat" in labels
    assert "Future Family / Friend Seat" in labels
    assert "Future Trustee / Advisor Seat" in labels
    assert "Future Beta Tester Seat" in labels

    for link in links:
        assert link["route"].startswith("/tower/owner-dashboard/person/")
        assert link["person_id"]


def test_remove_duplicate_people_rooms_dock_removes_section():
    html = """
    <html>
      <body>
        <section id="tower-people-room-dock">
          <h2>Click a name to control the room behind it.</h2>
        </section>
        <section id="preferred-people-seats">People + seats</section>
      </body>
    </html>
    """

    cleaned = remove_duplicate_people_rooms_dock(html)

    assert "tower-people-room-dock" not in cleaned
    assert "Click a name to control the room behind it." not in cleaned
    assert "preferred-people-seats" in cleaned


def test_remove_duplicate_people_rooms_dock_is_noop_when_absent():
    html = "<html><body><section>People + seats</section></body></html>"

    assert remove_duplicate_people_rooms_dock(html) == html


def test_enhance_preferred_people_search_section_adds_links_and_chips():
    html = """
    <html>
      <head></head>
      <body>
        <section>
          <input placeholder="Search people">
          <div>Future Manager Seat</div>
          <div>Future Family / Friend Seat</div>
        </section>
      </body>
    </html>
    """

    enhanced = enhance_preferred_people_search_section(html)

    assert "tower-people-search-consolidation-style" in enhanced
    assert "tower-people-search-note" in enhanced
    assert "tower-people-name-room-link" in enhanced
    assert "tower-people-open-room-chip" in enhanced
    assert "/tower/owner-dashboard/person/future-manager-seat" in enhanced
    assert "/tower/owner-dashboard/person/future-family-friend-seat" in enhanced


def test_enhance_preferred_people_search_section_removes_duplicate_and_keeps_search():
    html = """
    <html>
      <head></head>
      <body>
        <section id="tower-people-room-dock">
          <h2>Click a name to control the room behind it.</h2>
          <div>Future Manager Seat</div>
        </section>

        <section id="preferred">
          <input placeholder="Search people">
          <div>Future Manager Seat</div>
        </section>
      </body>
    </html>
    """

    enhanced = enhance_preferred_people_search_section(html)

    assert "tower-people-room-dock" not in enhanced
    assert "Search people" in enhanced
    assert "/tower/owner-dashboard/person/future-manager-seat" in enhanced
    assert enhanced.count("/tower/owner-dashboard/person/future-manager-seat") >= 1


def test_add_people_search_note_is_idempotent():
    html = "<html><body><main>Owner Dashboard</main></body></html>"

    once = add_people_search_note(html)
    twice = add_people_search_note(once)

    assert once == twice
    assert "tower-people-search-note" in once
