from tower.owner_people_change_queue import (
    APP_MATRIX,
    build_add_person_draft,
    build_change_queue_item,
    inject_change_queue_controls,
    people_change_queue_summary,
    staged_change_queue,
    staged_person_drafts,
)


def test_people_change_queue_summary_is_safe():
    summary = people_change_queue_summary()

    assert summary["status"] == "tower_people_change_queue_ready"
    assert summary["homepage_policy"] == "calm_search_first_with_small_actions"
    assert summary["add_person_draft_available"] is True
    assert summary["change_queue_available"] is True
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["real_permission_changes"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False


def test_staged_drafts_and_queue_exist():
    drafts = staged_person_drafts()
    queue = staged_change_queue()

    assert len(drafts) >= 2
    assert len(queue) >= 2
    assert drafts[0]["status"] == "draft_only_owner_review_required"
    assert queue[0]["status"] == "queued_for_owner_review"


def test_build_add_person_draft_valid_packet():
    draft = build_add_person_draft(
        {
            "display_name": "Azzarah Williams",
            "relationship": "Family",
            "requested_designation": "Family",
            "requested_scope": "No app access by default",
            "paperwork_needed": "Privacy terms",
            "owner_notes": "Invite later.",
        }
    )

    assert draft["status"] == "add_person_draft_created"
    assert draft["display_name"] == "Azzarah Williams"
    assert draft["requested_designation"] == "Family"
    assert draft["requires_owner_review"] is True
    assert draft["creates_real_account"] is False
    assert draft["sends_real_invite"] is False
    assert draft["grants_real_access"] is False
    assert draft["changes_real_permissions"] is False


def test_build_add_person_draft_rejects_missing_name():
    draft = build_add_person_draft(
        {
            "requested_designation": "Family",
        }
    )

    assert draft["status"] == "invalid_person_draft"
    assert draft["reason"] == "display_name_required"
    assert draft["creates_real_account"] is False


def test_build_add_person_draft_rejects_invalid_designation():
    draft = build_add_person_draft(
        {
            "display_name": "Test Person",
            "requested_designation": "Supreme Admin",
        }
    )

    assert draft["status"] == "invalid_person_draft"
    assert draft["reason"] == "invalid_requested_designation"


def test_build_change_queue_item_valid_packet():
    item = build_change_queue_item(
        {
            "person_id": "future-manager-seat",
            "display_name": "Future Manager Seat",
            "change_type": "designation",
            "requested_change": "Review Manager designation",
            "risk_note": "Keep money movement blocked.",
        }
    )

    assert item["status"] == "change_queue_item_created"
    assert item["requires_owner_review"] is True
    assert item["grants_real_access"] is False
    assert item["changes_real_permissions"] is False


def test_build_change_queue_item_rejects_missing_fields():
    item = build_change_queue_item(
        {
            "person_id": "future-manager-seat",
        }
    )

    assert item["status"] == "invalid_change_queue_item"
    assert item["grants_real_access"] is False
    assert item["changes_real_permissions"] is False


def test_inject_change_queue_controls_is_idempotent():
    html = "<html><body><main>People Desk</main></body></html>"

    once = inject_change_queue_controls(html)
    twice = inject_change_queue_controls(once)

    assert once == twice
    assert "tower-people-change-queue-controls" in once
    assert "/tower/owner-dashboard/person-drafts.json" in once
    assert "/tower/owner-dashboard/change-queue.json" in once


def test_app_matrix_retains_safe_apps():
    assert "Tower" in APP_MATRIX
    assert "Observatory" in APP_MATRIX
    assert "Teller" in APP_MATRIX
    assert "Vault" in APP_MATRIX
