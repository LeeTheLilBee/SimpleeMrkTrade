
from tower.owner_dashboard_service import (
    build_tower_owner_dashboard,
    owner_dashboard_status_cards,
)
from tower.owner_people_registry import (
    active_people,
    owner_access_requests,
    owner_invite_drafts,
    owner_people_authority_snapshot,
    owner_people_records,
    pending_owner_review_requests,
    person_by_id,
    staged_people,
)


def test_people_authority_is_explicitly_not_configured():
    authority = owner_people_authority_snapshot()

    assert (
        authority["status"]
        == "tower_people_authority_not_configured"
    )

    assert authority["verification_state"] == "NOT_CONFIGURED"
    assert authority["authoritative_provider_configured"] is False

    assert authority["people"]["value"] is None
    assert authority["people"]["verification_state"] == "NOT_CONFIGURED"

    assert authority["invitations"]["value"] is None
    assert authority["access_control"]["value"] is None
    assert authority["app_entitlements"]["value"] is None


def test_compatibility_people_projections_fail_closed_without_records():
    assert owner_people_records() == []
    assert active_people() == []
    assert staged_people() == []
    assert owner_access_requests() == []
    assert owner_invite_drafts() == []
    assert pending_owner_review_requests() == []


def test_person_lookup_does_not_manufacture_identity():
    assert person_by_id("owner-solice") is None
    assert person_by_id("does-not-exist") is None


def test_owner_dashboard_summary_does_not_turn_missing_authority_into_zero():
    dashboard = build_tower_owner_dashboard()
    summary = dashboard["summary"]

    assert (
        summary["status"]
        == "tower_owner_dashboard_authority_not_configured"
    )

    assert summary["people_count"] is None
    assert summary["invitation_count"] is None
    assert summary["pending_access_count"] is None

    assert summary["people_authority_state"] == "NOT_CONFIGURED"
    assert summary["invitation_authority_state"] == "NOT_CONFIGURED"
    assert summary["access_authority_state"] == "NOT_CONFIGURED"
    assert summary["entitlement_authority_state"] == "NOT_CONFIGURED"

    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False
    assert summary["release_execution"] is False


def test_owner_dashboard_cards_show_unavailable_authority_and_real_locks():
    cards = owner_dashboard_status_cards()

    by_id = {
        card["card_id"]: card
        for card in cards
    }

    assert by_id["owner-card-people"]["value"] == "NOT_CONFIGURED"
    assert by_id["owner-card-invitations"]["value"] == "NOT_CONFIGURED"
    assert by_id["owner-card-access"]["value"] == "NOT_CONFIGURED"
    assert by_id["owner-card-danger-locks"]["value"] == "LOCKED"

    assert "owner-card-staged" not in by_id
    assert "owner-card-review" not in by_id
