from dataclasses import replace

import pytest

from clouds.owner_decision_packet_service import (
    get_owner_decision_packets,
)

from clouds.owner_decision_review_service import (
    build_owner_decision_review,
    get_clouds_gp030_status_payload,
    get_owner_decision_review,
    get_owner_decision_review_by_packet,
    get_owner_decision_review_surface,
    get_owner_decision_review_surface_payload,
    get_owner_decision_reviews,
)


def test_gp030_one_review_per_packet():
    packets = (
        get_owner_decision_packets()
    )

    reviews = (
        get_owner_decision_reviews()
    )

    assert (
        len(reviews)
        == len(packets)
    )


def test_gp030_all_reviews_ready():
    reviews = (
        get_owner_decision_reviews()
    )

    assert reviews

    assert all(
        review.review_state
        == "ready_for_owner_choice"
        for review in reviews
    )


def test_gp030_ten_checks_per_review():
    for review in (
        get_owner_decision_reviews()
    ):
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


def test_gp030_owner_ready_to_choose():
    assert all(
        review.owner_ready_to_choose
        is True
        for review
        in get_owner_decision_reviews()
    )


def test_gp030_soulaana_explains_readiness():
    for review in (
        get_owner_decision_reviews()
    ):
        assert (
            review
            .soulaana_readiness_summary
        )

        assert (
            review
            .soulaana_blocker_summary
        )

        assert (
            review.soulaana_next_step
        )


def test_gp030_no_review_records_choice():
    for review in (
        get_owner_decision_reviews()
    ):
        assert (
            review.owner_choice_recorded
            is False
        )


def test_gp030_no_decision_or_approval():
    for review in (
        get_owner_decision_reviews()
    ):
        assert (
            review
            .automatic_decision_performed
            is False
        )

        assert (
            review.approval_performed
            is False
        )


def test_gp030_no_capital_movement():
    assert all(
        review
        .capital_movement_performed
        is False
        for review
        in get_owner_decision_reviews()
    )


def test_gp030_no_execution():
    assert all(
        review
        .downstream_execution_performed
        is False
        for review
        in get_owner_decision_reviews()
    )


def test_gp030_unknown_packet_fails_closed():
    with pytest.raises(KeyError):
        build_owner_decision_review(
            "missing-packet"
        )


def test_gp030_unknown_review_fails_closed():
    with pytest.raises(KeyError):
        get_owner_decision_review(
            "missing-review"
        )


def test_gp030_packet_lookup():
    review = (
        get_owner_decision_reviews()[0]
    )

    assert (
        get_owner_decision_review_by_packet(
            review.packet_id
        )
        == review
    )


def test_gp030_surface_counts():
    surface = (
        get_owner_decision_review_surface()
    )

    assert (
        surface.review_count
        == surface.ready_review_count
    )

    assert (
        surface.blocked_review_count
        == 0
    )


def test_gp030_surface_executes_nothing():
    surface = (
        get_owner_decision_review_surface()
    )

    assert (
        surface
        .automatic_decision_performed
        is False
    )

    assert (
        surface.approval_performed
        is False
    )

    assert (
        surface.owner_choice_recorded
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


def test_gp030_payload_serializes():
    payload = (
        get_owner_decision_review_surface_payload()
    )

    assert (
        payload["review_count"]
        == len(payload["reviews"])
    )


def test_gp030_status_ready():
    status = (
        get_clouds_gp030_status_payload()
    )

    assert status["pack"] == "GP030"

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
        == status["ready_review_count"]
    )

    assert (
        status["blocked_review_count"]
        == 0
    )

    assert (
        status["checks_per_review"]
        == 10
    )

    assert (
        status["owner_ready_to_choose"]
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
            "automatic_decision_performed"
        ]
        is False
    )

    assert (
        status["approval_performed"]
        is False
    )

    assert (
        status["owner_choice_recorded"]
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
        "GP031 — OWNER DECISION CHOICE / "
        "INTENT RECORDING BOUNDARY"
    )
