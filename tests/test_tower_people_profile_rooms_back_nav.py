from tower.owner_people_profile_rooms import (
    APP_ACCESS_OPTIONS,
    APP_MATRIX,
    DESIGNATION_OPTIONS,
    build_app_access_change_draft,
    build_designation_change_draft,
    build_person_freeze_draft,
    inject_back_nav,
    inject_people_room_dock,
    people_profile_by_id,
    people_profile_rooms,
    people_profile_summary,
)


def test_people_profile_rooms_exist_and_are_clickable_units():
    people = people_profile_rooms()

    assert len(people) >= 4

    ids = {
        person["person_id"]
        for person in people
    }

    assert "future-manager-seat" in ids
    assert "future-family-friend-seat" in ids

    for person in people:
        assert person["display_name"]
        assert person["designation"]
        assert person["access_summary"]


def test_people_profile_summary_keeps_home_calm_and_danger_off():
    summary = people_profile_summary()

    assert summary["status"] == "tower_people_profile_rooms_ready"
    assert summary["homepage_clutter_policy"] == "calm_home_power_behind_names"
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_people_profile_lookup():
    profile = people_profile_by_id("future-manager-seat")

    assert profile is not None
    assert profile["display_name"] == "Future Manager Seat"

    assert people_profile_by_id("missing") is None


def test_designation_change_draft_is_safe():
    draft = build_designation_change_draft(
        "future-manager-seat",
        "Manager",
        "Make them a manager later.",
    )

    assert draft["status"] == "designation_change_draft_created"
    assert draft["requested_designation"] == "Manager"
    assert draft["requires_owner_review"] is True
    assert draft["creates_real_account"] is False
    assert draft["sends_real_invite"] is False
    assert draft["grants_real_access"] is False
    assert draft["changes_real_permissions"] is False


def test_designation_change_rejects_invalid_designation():
    draft = build_designation_change_draft(
        "future-manager-seat",
        "Supreme Admin",
    )

    assert draft["status"] == "invalid_designation"
    assert "Supreme Admin" not in DESIGNATION_OPTIONS
    assert draft["real_permission_changes"] is False


def test_app_access_change_draft_is_safe():
    draft = build_app_access_change_draft(
        "future-beta-tester-seat",
        "Observatory",
        "Owner Review Required",
        "Beta only later.",
    )

    assert draft["status"] == "app_access_change_draft_created"
    assert draft["app_name"] == "Observatory"
    assert draft["requested_access_level"] == "Owner Review Required"
    assert draft["requires_owner_review"] is True
    assert draft["grants_real_access"] is False
    assert draft["changes_real_permissions"] is False


def test_app_access_change_rejects_invalid_app_or_level():
    invalid_app = build_app_access_change_draft(
        "future-beta-tester-seat",
        "Unknown App",
        "Blocked",
    )

    assert invalid_app["status"] == "invalid_app"
    assert "Unknown App" not in APP_MATRIX

    invalid_level = build_app_access_change_draft(
        "future-beta-tester-seat",
        "Tower",
        "God Mode",
    )

    assert invalid_level["status"] == "invalid_access_level"
    assert "God Mode" not in APP_ACCESS_OPTIONS


def test_person_freeze_draft_is_safe():
    draft = build_person_freeze_draft(
        "future-family-friend-seat",
        "Pause until paperwork exists.",
    )

    assert draft["status"] == "person_freeze_draft_created"
    assert draft["requires_owner_review"] is True
    assert draft["freezes_real_access"] is False
    assert draft["grants_real_access"] is False
    assert draft["changes_real_permissions"] is False


def test_back_nav_injection_is_idempotent():
    html = "<html><body><main>Room</main></body></html>"

    once = inject_back_nav(
        html,
        active="owner",
    )
    twice = inject_back_nav(
        once,
        active="owner",
    )

    assert once == twice
    assert "tower-owner-back-nav" in twice
    assert "/tower/access-home" in twice
    assert "/tower/security-map" in twice


def test_people_room_dock_injection_is_idempotent_and_has_person_links():
    html = "<html><body><main>Owner Dashboard</main></body></html>"

    once = inject_people_room_dock(html)
    twice = inject_people_room_dock(once)

    assert once == twice
    assert "tower-people-room-dock" in twice
    assert "/tower/owner-dashboard/person/future-manager-seat" in twice
    assert "/tower/owner-dashboard/person/future-family-friend-seat" in twice
