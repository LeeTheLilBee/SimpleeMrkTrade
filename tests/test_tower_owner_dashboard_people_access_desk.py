from tower.owner_dashboard_service import (
    build_tower_owner_dashboard,
    owner_dashboard_status_cards,
)
from tower.owner_people_registry import (
    active_people,
    owner_access_requests,
    owner_invite_drafts,
    owner_people_records,
    pending_owner_review_requests,
    person_by_id,
    staged_people,
)


def test_owner_people_registry_contains_owner_and_staged_seats():
    people = owner_people_records()
    person_ids = {
        person["person_id"]
        for person in people
    }

    assert "owner-solice" in person_ids
    assert "future-manager-seat" in person_ids
    assert "future-family-seat" in person_ids


def test_owner_is_active_and_future_seats_are_staged():
    active = active_people()
    staged = staged_people()

    assert [
        person["person_id"]
        for person in active
    ] == [
        "owner-solice",
    ]

    staged_ids = {
        person["person_id"]
        for person in staged
    }

    assert "future-manager-seat" in staged_ids
    assert "future-family-seat" in staged_ids


def test_invites_are_drafts_not_sent():
    invites = owner_invite_drafts()

    assert invites

    for invite in invites:
        assert invite["status"] == "draft_not_sent"
        assert invite["owner_decision_required"] is True


def test_access_requests_are_pending_and_not_auto_granted():
    requests = owner_access_requests()

    assert requests

    for request in requests:
        assert request["status"] == "pending_owner_review"
        assert request["can_auto_grant"] is False


def test_pending_owner_review_requests_visible():
    pending = pending_owner_review_requests()

    assert len(pending) == 2


def test_person_lookup():
    person = person_by_id("owner-solice")

    assert person is not None
    assert person["display_name"] == "Solice Bowdre"

    assert person_by_id("does-not-exist") is None


def test_owner_dashboard_summary_exposes_safety_boundaries():
    dashboard = build_tower_owner_dashboard()
    summary = dashboard["summary"]

    assert summary["status"] == "tower_owner_dashboard_ready"
    assert summary["real_account_creation"] is False
    assert summary["real_invites_sent"] is False
    assert summary["real_access_granted"] is False
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False

    locks = dashboard["danger_locks"]

    assert locks["real_account_creation"] is False
    assert locks["real_invites_sent"] is False
    assert locks["real_access_granted"] is False
    assert locks["live_auto"] == "LOCKED"
    assert locks["broker_execution"] is False
    assert locks["capital_action"] is False


def test_owner_dashboard_cards_exist():
    cards = owner_dashboard_status_cards()

    card_ids = {
        card["card_id"]
        for card in cards
    }

    assert "owner-card-people" in card_ids
    assert "owner-card-staged" in card_ids
    assert "owner-card-invites" in card_ids
    assert "owner-card-review" in card_ids
    assert "owner-card-access-grants" in card_ids
    assert "owner-card-danger-locks" in card_ids
