import pytest

from clouds.owner_decision_choice_service import (
    get_clouds_gp031_status_payload,
    get_gp031_fixture_choice_record,
    get_owner_choice_surface,
    get_owner_choice_surface_payload,
    get_pending_owner_choice_records,
    record_owner_choice,
)

from clouds.owner_decision_packet_service import (
    get_owner_decision_packet,
)

from clouds.owner_decision_review_service import (
    get_owner_decision_reviews,
)


def test_gp031_pending_record_per_review():
    pending = (
        get_pending_owner_choice_records()
    )

    reviews = (
        get_owner_decision_reviews()
    )

    assert (
        len(pending)
        == len(reviews)
    )


def test_gp031_pending_records_have_no_choice():
    for record in (
        get_pending_owner_choice_records()
    ):
        assert (
            record.choice_state
            == "pending"
        )

        assert (
            record.owner_choice_recorded
            is False
        )

        assert (
            record.selected_option_id
            is None
        )


def test_gp031_fixture_records_review_now():
    record = (
        get_gp031_fixture_choice_record()
    )

    assert (
        record.choice_state
        == "recorded"
    )

    assert (
        record.owner_choice_recorded
        is True
    )

    assert (
        record.selected_option_kind
        == "review_now"
    )


def test_gp031_recorded_choice_is_not_approval():
    record = (
        get_gp031_fixture_choice_record()
    )

    assert (
        record.approval_performed
        is False
    )

    assert (
        record.automatic_decision_performed
        is False
    )


def test_gp031_recorded_choice_does_not_move_capital():
    assert (
        get_gp031_fixture_choice_record()
        .capital_movement_performed
        is False
    )


def test_gp031_recorded_choice_does_not_execute():
    assert (
        get_gp031_fixture_choice_record()
        .downstream_execution_performed
        is False
    )


def test_gp031_invalid_option_fails_closed():
    review = (
        get_owner_decision_reviews()[0]
    )

    with pytest.raises(ValueError):
        record_owner_choice(
            review.review_id,
            "missing-option",
        )


def test_gp031_unknown_review_fails_closed():
    with pytest.raises(KeyError):
        record_owner_choice(
            "missing-review",
            "anything",
        )


def test_gp031_valid_option_can_be_recorded():
    review = (
        get_owner_decision_reviews()[0]
    )

    packet = (
        get_owner_decision_packet(
            review.packet_id
        )
    )

    option = packet.options[0]

    record = record_owner_choice(
        review.review_id,
        option.option_id,
    )

    assert (
        record.selected_option_id
        == option.option_id
    )

    assert (
        record.selected_option_kind
        == option.kind
    )

    assert (
        record.owner_choice_recorded
        is True
    )


def test_gp031_preserves_tower_mediation_flag():
    record = (
        get_gp031_fixture_choice_record()
    )

    packet = (
        get_owner_decision_packet(
            record.packet_id
        )
    )

    assert (
        record.requires_tower_mediation
        == packet.requires_tower_mediation
    )


def test_gp031_soulaana_explains_recorded_choice():
    record = (
        get_gp031_fixture_choice_record()
    )

    assert (
        record.soulaana_choice_summary
    )

    assert (
        record.soulaana_what_this_means
    )

    assert (
        record
        .soulaana_what_did_not_happen
    )

    assert (
        record.soulaana_next_step
    )


def test_gp031_surface_has_one_fixture_recorded():
    surface = (
        get_owner_choice_surface()
    )

    assert (
        surface.recorded_count
        == 1
    )

    assert (
        surface.pending_count
        == surface.record_count - 1
    )

    assert (
        surface.blocked_count
        == 0
    )


def test_gp031_surface_executes_nothing():
    surface = (
        get_owner_choice_surface()
    )

    assert (
        surface.approval_performed
        is False
    )

    assert (
        surface
        .automatic_decision_performed
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


def test_gp031_payload_serializes():
    payload = (
        get_owner_choice_surface_payload()
    )

    assert (
        payload["record_count"]
        == len(payload["records"])
    )


def test_gp031_status_ready():
    status = (
        get_clouds_gp031_status_payload()
    )

    assert status["pack"] == "GP031"

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
        status["recorded_count"]
        == 1
    )

    assert (
        status["blocked_count"]
        == 0
    )

    assert (
        status["fixture_choice_kind"]
        == "review_now"
    )

    assert (
        status[
            "explicit_owner_intent_required"
        ]
        is True
    )

    assert (
        status["owner_choice_recorded"]
        is True
    )

    assert (
        status["approval_performed"]
        is False
    )

    assert (
        status[
            "automatic_decision_performed"
        ]
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
            "tower_authority_changed"
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
        "GP032 — OWNER INTENT REVIEW / "
        "HANDOFF AUTHORIZATION PREPARATION"
    )
