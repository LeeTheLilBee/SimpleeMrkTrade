from tower.owner_person_control_room import (
    OBSERVATORY_ACCESS_AREAS,
    PERSON_CONTROL_ROOM_MARKER,
    PERSON_ROOM_SECTIONS,
    TOWER_ACCESS_AREAS,
    inject_person_control_room,
    is_person_room_path,
    person_control_room_summary,
)


def test_person_control_room_summary_is_safe():
    summary = person_control_room_summary()

    assert summary["status"] == "tower_person_control_room_ready"
    assert summary["product_rule"] == "person_room_is_owner_control_surface"

    assert summary["designation_change"] == "draft_only"
    assert summary["responsibility_change"] == "draft_only"
    assert summary["access_change"] == "draft_only"
    assert summary["status_change"] == "draft_only"
    assert summary["freeze_change"] == "draft_only"
    assert summary["restore_change"] == "draft_only"

    assert summary["paperwork_review"] == "owner_review_only"
    assert summary["activity_history"] is True

    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_access_revoked"] is False
    assert summary["real_person_suspended"] is False
    assert summary["real_permission_changes"] is False

    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_person_room_sections_are_deep_enough():
    expected = {
        "Identity",
        "Designation",
        "Responsibilities",
        "Companies",
        "Access",
        "Paperwork",
        "Activity",
        "Notes",
        "Change Queue",
    }

    assert expected.issubset(
        set(PERSON_ROOM_SECTIONS)
    )


def test_access_areas_cover_tower_and_ob():
    assert "People + seats" in TOWER_ACCESS_AREAS
    assert "Security Map" in TOWER_ACCESS_AREAS
    assert "The Teller" in TOWER_ACCESS_AREAS
    assert "The Vault" in TOWER_ACCESS_AREAS

    assert "Dashboard" in OBSERVATORY_ACCESS_AREAS
    assert "Market Map" in OBSERVATORY_ACCESS_AREAS
    assert "Trade Center" in OBSERVATORY_ACCESS_AREAS
    assert "Review Center" in OBSERVATORY_ACCESS_AREAS
    assert "Owner Console" in OBSERVATORY_ACCESS_AREAS


def test_person_room_path_detection():
    assert is_person_room_path(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    assert is_person_room_path(
        "/tower/owner-dashboard/person/solice-bowdre"
    )

    assert not is_person_room_path(
        "/tower/owner-dashboard"
    )

    assert not is_person_room_path(
        "/tower/owner-dashboard/person/future-manager-seat.json"
    )

    assert not is_person_room_path(
        "/tower/owner-dashboard/person/future-manager-seat/designation-draft"
    )


def test_injection_adds_control_room_source():
    html = """
    <html>
      <head></head>
      <body>
        <main>
          <h1>Future Manager Seat</h1>
        </main>
      </body>
    </html>
    """

    injected = inject_person_control_room(
        html
    )

    assert PERSON_CONTROL_ROOM_MARKER in injected
    assert "tower-person-control-room-style-twr046-050" in injected
    assert "Person Control Room" in injected
    assert "Change designation" in injected
    assert "Change access draft" in injected
    assert "Responsibilities" in injected
    assert "Suspend / freeze draft" in injected
    assert "Restore draft" in injected
    assert "Owner review chain" in injected


def test_injection_is_idempotent():
    html = "<html><head></head><body></body></html>"

    once = inject_person_control_room(
        html
    )

    twice = inject_person_control_room(
        once
    )

    assert once == twice

    assert once.count(
        PERSON_CONTROL_ROOM_MARKER
    ) == 1


def test_source_keeps_real_actions_locked():
    html = "<html><head></head><body></body></html>"

    injected = inject_person_control_room(
        html
    )

    assert "Draft only" in injected
    assert "does not change the live designation" in injected
    assert "No permission is granted or revoked" in injected
    assert "does not disable a real account" in injected
    assert "does not restore or change live permissions" in injected
    assert "Nothing in TWR046–TWR050 applies real access or identity changes" in injected
