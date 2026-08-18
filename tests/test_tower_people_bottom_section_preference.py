from tower.owner_people_bottom_section_preference import (
    BOTTOM_SECTION_PREFERENCE_MARKER,
    bottom_section_preference_summary,
    inject_bottom_people_seats_preference,
)


def test_bottom_section_preference_summary_is_safe():
    summary = bottom_section_preference_summary()

    assert summary["status"] == "tower_bottom_people_seats_search_ready"
    assert summary["visual_rule"] == "remove_top_people_seats_keep_bottom_people_seats"
    assert summary["top_people_seats_removed"] is True
    assert summary["bottom_people_seats_preserved"] is True
    assert summary["bottom_people_seats_search_required"] is True
    assert summary["person_room_links_preserved"] is True
    assert summary["open_room_chips_preserved"] is True
    assert summary["draft_queue_preserved"] is True
    assert summary["back_buttons_preserved"] is True
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_inject_bottom_people_seats_preference_adds_script_and_style():
    html = """
    <!doctype html>
    <html>
      <head></head>
      <body>
        <section><h2>People + seats</h2></section>
        <section><h2>People + seats</h2></section>
      </body>
    </html>
    """

    injected = inject_bottom_people_seats_preference(html)

    assert BOTTOM_SECTION_PREFERENCE_MARKER in injected
    assert "tower-bottom-people-seats-search-style-twr031-035" in injected
    assert "top-hidden-bottom-kept-search-ready" in injected
    assert "single-bottom-search-ready" in injected
    assert "data-tower-removed-top-people-seats" in injected
    assert "data-tower-keep-bottom-people-seats" in injected


def test_inject_bottom_people_seats_preference_is_idempotent():
    html = "<html><head></head><body><main>Owner Dashboard</main></body></html>"

    once = inject_bottom_people_seats_preference(html)
    twice = inject_bottom_people_seats_preference(once)

    assert once == twice
    assert once.count(BOTTOM_SECTION_PREFERENCE_MARKER) == 1


def test_script_keeps_bottom_and_removes_top_candidates():
    html = "<html><head></head><body></body></html>"
    injected = inject_bottom_people_seats_preference(html)

    assert "var keptSection = candidates[candidates.length - 1]" in injected
    assert "candidates.slice(0, -1).forEach" in injected
    assert "node.style.display = \"none\"" in injected
    assert "top-hidden-bottom-kept-search-ready" in injected


def test_script_requires_search_on_kept_bottom_section():
    html = "<html><head></head><body></body></html>"
    injected = inject_bottom_people_seats_preference(html)

    assert "ensureSearchBar(keptSection)" in injected
    assert "Search people + seats" in injected
    assert "Search people, seats, roles, access notes..." in injected
    assert "data-tower-people-search" in injected


def test_script_preserves_existing_search_if_present():
    html = "<html><head></head><body></body></html>"
    injected = inject_bottom_people_seats_preference(html)

    assert "existing-search-kept" in injected
    assert "input[type='search']" in injected
    assert "input[placeholder*='Search']" in injected


def test_script_keeps_safety_controls_protected():
    html = "<html><head></head><body></body></html>"
    injected = inject_bottom_people_seats_preference(html)

    assert "#tower-owner-back-nav" in injected
    assert "#tower-people-change-queue-controls" in injected
    assert "#tower-people-search-note" in injected
