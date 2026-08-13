from dataclasses import replace

import pytest

from clouds.owner_decision_choice_service import (
    get_gp031_fixture_choice_record,
)

from clouds.owner_intent_review_service import (
    build_owner_intent_review,
    get_clouds_gp032_status_payload,
    get_owner_intent_review_surface,
    get_owner_intent_review_surface_payload,
    get_owner_intent_reviews,
)


def test_gp032_single_fixture_review():
    reviews = (
        get_owner_intent_reviews()
    )

    assert len(reviews) == 1


def test_gp032_review_is_ready():
    review = (
        get_owner_intent_reviews()[0]
    )

    assert (
        review.review_state
        == "ready_for_handoff_authorization_prep"
    )

    assert (
        review
        .ready_for_handoff_authorization_prep
        is True
    )


def test_gp032_ten_green_checks():
    review = (
        get_owner_intent_reviews()[0]
    )

    assert (
        review.check_count
        == 10
    )

    assert (
        review.passed_check_count
        == 10
    )

    assert (
        review.failed_check_count
        == 0
    )


def test_gp032_soulaana_explains_review():
    review = (
        get_owner_intent_reviews()[0]
    )

    assert (
        review.soulaana_review_summary
    )

    assert (
        review.soulaana_why_it_matters
    )

    assert (
        review.soulaana_blocker_summary
    )

    assert (
        review.soulaana_next_step
    )


def test_gp032_unrecorded_choice_fails_closed():
    choice = (
        get_gp031_fixture_choice_record()
    )

    bad = replace(
        choice,
        choice_state="pending",
        owner_choice_recorded=False,
    )

    with pytest.raises(ValueError):
        build_owner_intent_review(
            bad
        )


def test_gp032_tower_flag_preserved():
    choice = (
        get_gp031_fixture_choice_record()
    )

    review = (
        build_owner_intent_review(
            choice
        )
    )

    assert (
        review.requires_tower_mediation
        == choice.requires_tower_mediation
    )


def test_gp032_selected_option_preserved():
    choice = (
        get_gp031_fixture_choice_record()
    )

    review = (
        build_owner_intent_review(
            choice
        )
    )

    assert (
        review.selected_option_id
        == choice.selected_option_id
    )

    assert (
        review.selected_option_kind
        == choice.selected_option_kind
    )


def test_gp032_no_handoff_authorization():
    review = (
        get_owner_intent_reviews()[0]
    )

    assert (
        review.handoff_authorized
        is False
    )


def test_gp032_no_handoff_delivery():
    review = (
        get_owner_intent_reviews()[0]
    )

    assert (
        review.handoff_delivered
        is False
    )


def test_gp032_no_approval():
    assert (
        get_owner_intent_reviews()[0]
        .approval_performed
        is False
    )


def test_gp032_no_capital_movement():
    assert (
        get_owner_intent_reviews()[0]
        .capital_movement_performed
        is False
    )


def test_gp032_no_downstream_execution():
    assert (
        get_owner_intent_reviews()[0]
        .downstream_execution_performed
        is False
    )


def test_gp032_surface_counts():
    surface = (
        get_owner_intent_review_surface()
    )

    assert surface.review_count == 1
    assert surface.ready_count == 1
    assert surface.blocked_count == 0


def test_gp032_surface_authorizes_nothing():
    surface = (
        get_owner_intent_review_surface()
    )

    assert (
        surface.handoff_authorized
        is False
    )

    assert (
        surface.handoff_delivered
        is False
    )

    assert (
        surface.approval_performed
        is False
    )

    assert (
        surface
        .capital_movement_performed
        is False
    )

    assert (
        surface
        .downstream_execution_performed
        is False
    )


def test_gp032_payload_serializes():
    payload = (
        get_owner_intent_review_surface_payload()
    )

    assert (
        payload["review_count"]
        == len(payload["reviews"])
    )


def test_gp032_status_ready():
    status = (
        get_clouds_gp032_status_payload()
    )

    assert status["pack"] == "GP032"

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["review_count"]
        == 1
    )

    assert (
        status["ready_count"]
        == 1
    )

    assert (
        status["blocked_count"]
        == 0
    )

    assert (
        status["checks_per_review"]
        == 10
    )

    assert (
        status[
            "recorded_intent_validated"
        ]
        is True
    )

    assert (
        status[
            "selected_option_still_valid"
        ]
        is True
    )

    assert (
        status[
            "tower_mediation_preserved"
        ]
        is True
    )

    assert (
        status[
            "ready_for_handoff_authorization_prep"
        ]
        is True
    )

    assert (
        status["handoff_authorized"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )

    assert (
        status["approval_performed"]
        is False
    )

    assert (
        status[
            "capital_movement_performed"
        ]
        is False
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )

    assert status["next_pack"] == (
        "GP033 — HANDOFF AUTHORIZATION DECISION / "
        "OWNER CONFIRMATION BOUNDARY"
    )
