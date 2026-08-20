from tower.owner_person_control_draft_wiring import (
    CONTROL_ACTIONS,
    STATUS_OPTIONS,
    build_person_control_draft,
    person_control_draft_wiring_summary,
    person_control_room_payload,
    person_queue_projection,
)


def test_summary_is_fail_closed():
    summary = person_control_draft_wiring_summary()

    assert summary["draft_submission_enabled"] is True
    assert summary["durable_persistence_enabled"] is False
    assert summary["draft_receipts_enabled"] is True

    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_access_revoked"] is False
    assert summary["real_person_frozen"] is False
    assert summary["real_person_restored"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"


def test_control_actions_are_expected():
    assert set(CONTROL_ACTIONS) == {
        "designation",
        "app_access",
        "responsibility",
        "status",
        "freeze",
        "restore",
        "paperwork_note",
    }


def test_person_control_payload_uses_real_profile():
    payload = person_control_room_payload(
        "future-manager-seat"
    )

    assert payload["status"] == "tower_person_control_room_payload_ready"

    assert payload["profile"]["person_id"] == "future-manager-seat"
    assert payload["profile"]["display_name"] == "Future Manager Seat"

    assert "Manager" in payload["allowed"]["designations"]
    assert "Tower" in payload["allowed"]["apps"]

    assert payload["safety"]["durable_persistence_enabled"] is False
    assert payload["safety"]["real_access_granted"] is False


def test_unknown_person_is_not_found():
    payload = person_control_room_payload(
        "not-real"
    )

    assert payload["status"] == "not_found"


def test_existing_person_queue_projection():
    queue = person_queue_projection(
        "future-manager-seat"
    )

    assert isinstance(queue, list)

    assert any(
        item["person_id"] == "future-manager-seat"
        for item in queue
    )


def test_designation_draft_builds_existing_draft_and_queue_packet():
    result = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "designation",
            "requested_designation": "Manager",
            "notes": "Owner review",
        },
    )

    assert result["status"] == "person_control_draft_created"
    assert result["control_action"] == "designation"

    assert result["draft"]["status"] == "designation_change_draft_created"

    assert result["queue_item"]["status"] == "change_queue_item_created"

    assert result["receipt"]["durable_persistence"] is False

    assert result["safety"]["changes_real_permissions"] is False


def test_app_access_draft_uses_existing_contract():
    result = build_person_control_draft(
        "future-beta-tester-seat",
        {
            "action": "app_access",
            "app_name": "Observatory",
            "access_level": "View Only",
            "notes": "Survey/Paper review only",
        },
    )

    assert result["status"] == "person_control_draft_created"

    assert result["draft"]["status"] == "app_access_change_draft_created"

    assert result["draft"]["app_name"] == "Observatory"

    assert result["draft"]["requested_access_level"] == "View Only"

    assert result["safety"]["grants_real_access"] is False


def test_freeze_draft_does_not_freeze_real_access():
    result = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "freeze",
            "reason": "Owner wants access review",
        },
    )

    assert result["status"] == "person_control_draft_created"

    assert result["draft"]["status"] == "person_freeze_draft_created"

    assert result["draft"]["freezes_real_access"] is False

    assert result["safety"]["freezes_real_access"] is False


def test_restore_draft_does_not_restore_live_permissions():
    result = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "restore",
            "reason": "Review restore later",
        },
    )

    assert result["status"] == "person_control_draft_created"

    assert result["draft"]["status"] == "person_restore_draft_created"

    assert result["draft"]["restores_real_access"] is False


def test_responsibility_requires_content():
    result = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "responsibility",
        },
    )

    assert result["status"] == "invalid_responsibility_draft"


def test_status_validation():
    valid = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "status",
            "requested_status": "Owner Review Required",
        },
    )

    assert valid["status"] == "person_control_draft_created"

    invalid = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "status",
            "requested_status": "SUPER ADMIN NOW",
        },
    )

    assert invalid["status"] == "invalid_status_draft"

    assert set(invalid["allowed_statuses"]) == set(STATUS_OPTIONS)


def test_invalid_action_fails_closed():
    result = build_person_control_draft(
        "future-manager-seat",
        {
            "action": "grant_everything",
        },
    )

    assert result["status"] == "invalid_control_action"
    assert result["real_permission_changes"] is False
    assert result["real_access_granted"] is False
