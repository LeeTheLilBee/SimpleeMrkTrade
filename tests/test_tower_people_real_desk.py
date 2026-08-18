from tower.owner_people_real_desk import (
    PERSON_CATEGORIES,
    REAL_DESK_MARKER,
    inject_people_real_desk,
    people_real_desk_summary,
)


def test_people_real_desk_summary_is_safe():
    summary = people_real_desk_summary()

    assert summary["status"] == "tower_people_seats_real_desk_ready"
    assert summary["product_rule"] == "people_seats_is_the_single_people_desk"
    assert summary["better_cards_added"] is True
    assert summary["add_person_workspace_added"] is True
    assert summary["category_filters_added"] is True
    assert summary["inline_room_details_polished"] is True
    assert summary["draft_queue_polished"] is True
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_person_categories_include_needed_groups():
    assert "Family/Friends" in PERSON_CATEGORIES
    assert "Managers" in PERSON_CATEGORIES
    assert "Employees" in PERSON_CATEGORIES
    assert "Vendors" in PERSON_CATEGORIES
    assert "Advisors" in PERSON_CATEGORIES
    assert "Trustees/Admin" in PERSON_CATEGORIES
    assert "Beta testers" in PERSON_CATEGORIES
    assert "Future seats" in PERSON_CATEGORIES


def test_inject_people_real_desk_adds_style_and_script():
    html = """
    <html>
      <head></head>
      <body>
        <section data-tower-keep-bottom-people-seats="true">
          <h2>People + seats</h2>
          <article>
            <a href="/tower/owner-dashboard/person/future-manager-seat">Future Manager Seat</a>
          </article>
        </section>
      </body>
    </html>
    """

    injected = inject_people_real_desk(html)

    assert REAL_DESK_MARKER in injected
    assert "tower-people-seats-real-desk-style-twr041-045" in injected
    assert "people-seats-real-desk-ready" in injected
    assert "Add person draft" in injected
    assert "tower-real-filter-chip" in injected
    assert "tower-real-person-chip" in injected


def test_inject_people_real_desk_is_idempotent():
    html = "<html><head></head><body><main>Owner Dashboard</main></body></html>"

    once = inject_people_real_desk(html)
    twice = inject_people_real_desk(once)

    assert once == twice
    assert once.count(REAL_DESK_MARKER) == 1


def test_script_keeps_draft_only_safety_language():
    html = "<html><head></head><body></body></html>"
    injected = inject_people_real_desk(html)

    assert "Draft only" in injected
    assert "does not create an account" in injected
    assert "send an invite" in injected
    assert "grant access" in injected
    assert "change permissions" in injected
    assert "Nothing here changes live permissions" in injected


def test_script_supports_filters_and_queue_polish():
    html = "<html><head></head><body></body></html>"
    injected = inject_people_real_desk(html)

    assert "wireFilters" in injected
    assert "data-tower-real-filter" in injected
    assert "data-tower-real-filter-hidden" in injected
    assert "polishDraftQueue" in injected
    assert "Owner review required" in injected
