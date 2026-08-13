from dataclasses import replace

import pytest

from clouds.handoff_authorization_decision_service import (
    get_clouds_gp033_status_payload,
    get_gp033_authorized_fixture,
    get_gp033_declined_fixture,
    get_handoff_authorization_surface,
    get_handoff_authorization_surface_payload,
    record_handoff_authorization_decision,
)

from clouds.owner_intent_review_service import (
    get_owner_intent_reviews,
)


def test_gp033_authorize_path():
    record = (
        get_gp033_authorized_fixture()
    )

    assert (
        record.owner_decision
        == "authorize"
    )

    assert (
        record.authorization_state
        == "authorized_for_preparation"
    )

    assert (
        record.handoff_authorized
        is True
    )


def test_gp033_decline_path():
    record = (
        get_gp033_declined_fixture()
    )

    assert (
        record.owner_decision
        == "decline"
    )

    assert (
        record.authorization_state
        == "declined"
    )

    assert (
        record.handoff_authorized
        is False
    )


def test_gp033_invalid_decision_fails_closed():
    review = (
        get_owner_intent_reviews()[0]
    )

    with pytest.raises(ValueError):
        record_handoff_authorization_decision(
            review,
            "maybe",
        )


def test_gp033_nonready_review_fails_closed():
    review = (
        get_owner_intent_reviews()[0]
    )

    bad = replace(
        review,
        review_state="blocked",
        ready_for_handoff_authorization_prep=False,
    )

    with pytest.raises(ValueError):
        record_handoff_authorization_decision(
            bad,
            "authorize",
        )


def test_gp033_authorization_preserves_source():
    review = (
        get_owner_intent_reviews()[0]
    )

    record = (
        get_gp033_authorized_fixture()
    )

    assert (
        record.source_id
        == review.source_id
    )

    assert (
        record.owning_application_id
        == review.owning_application_id
    )


def test_gp033_tower_requirement_preserved():
    review = (
        get_owner_intent_reviews()[0]
    )

    record = (
        get_gp033_authorized_fixture()
    )

    assert (
        record.requires_tower_mediation
        == review.requires_tower_mediation
    )


def test_gp033_selected_option_preserved():
    review = (
        get_owner_intent_reviews()[0]
    )

    record = (
        get_gp033_authorized_fixture()
    )

    assert (
        record.selected_option_id
        == review.selected_option_id
    )

    assert (
        record.selected_option_kind
        == review.selected_option_kind
    )


def test_gp033_authorization_does_not_deliver():
    assert (
        get_gp033_authorized_fixture()
        .handoff_delivered
        is False
    )


def test_gp033_authorization_is_not_approval():
    assert (
        get_gp033_authorized_fixture()
        .approval_performed
        is False
    )


def test_gp033_no_capital_movement():
    assert (
        get_gp033_authorized_fixture()
        .capital_movement_performed
        is False
    )


def test_gp033_no_downstream_execution():
    assert (
        get_gp033_authorized_fixture()
        .downstream_execution_performed
        is False
    )


def test_gp033_soulaana_explains_authorization():
    record = (
        get_gp033_authorized_fixture()
    )

    assert (
        record.soulaana_decision_summary
    )

    assert (
        record.soulaana_what_this_means
    )

    assert (
        record.soulaana_what_did_not_happen
    )

    assert (
        record.soulaana_next_step
    )


def test_gp033_surface_counts():
    surface = (
        get_handoff_authorization_surface()
    )

    assert surface.record_count == 1
    assert surface.authorized_count == 1
    assert surface.declined_count == 0
    assert surface.blocked_count == 0


def test_gp033_surface_not_delivered():
    surface = (
        get_handoff_authorization_surface()
    )

    assert (
        surface.handoff_authorized
        is True
    )

    assert (
        surface.handoff_delivered
        is False
    )


def test_gp033_payload_serializes():
    payload = (
        get_handoff_authorization_surface_payload()
    )

    assert (
        payload["record_count"]
        == len(payload["records"])
    )


def test_gp033_status_ready():
    status = (
        get_clouds_gp033_status_payload()
    )

    assert status["pack"] == "GP033"

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
        status[
            "owner_confirmation_recorded"
        ]
        is True
    )

    assert (
        status["authorize_path_verified"]
        is True
    )

    assert (
        status["decline_path_verified"]
        is True
    )

    assert (
        status["handoff_authorized"]
        is True
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
        "GP034 — PROTECTED HANDOFF PACKAGE / "
        "DELIVERY PREPARATION"
    )
