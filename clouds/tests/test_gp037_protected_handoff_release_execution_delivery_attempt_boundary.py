from dataclasses import replace

import pytest

from clouds.protected_handoff_release_execution_service import (
    execute_protected_handoff_release,
    get_clouds_gp037_status_payload,
    get_gp037_release_execution,
)

from clouds.protected_handoff_release_record_service import (
    get_gp036_delivery_envelope,
)


def test_gp037_release_executes_to_boundary():
    record = get_gp037_release_execution()

    assert (
        record.release_execution_state
        == "released_to_external_boundary"
    )

    assert (
        record.delivery_release_executed
        is True
    )

    assert (
        record.released_to_delivery_boundary
        is True
    )


def test_gp037_does_not_contact_tower():
    record = get_gp037_release_execution()

    assert record.tower_contacted is False

    assert (
        record.external_transport_invoked
        is False
    )


def test_gp037_does_not_claim_delivery():
    record = get_gp037_release_execution()

    assert (
        record.external_delivery_attempted
        is False
    )

    assert (
        record.external_receipt_present
        is False
    )

    assert (
        record.handoff_delivered
        is False
    )


def test_gp037_tampered_envelope_fails_closed():
    envelope = get_gp036_delivery_envelope()

    bad = replace(
        envelope,
        delivery_target_id="tampered",
    )

    with pytest.raises(ValueError):
        execute_protected_handoff_release(
            bad
        )


def test_gp037_already_released_fails_closed():
    envelope = get_gp036_delivery_envelope()

    bad = replace(
        envelope,
        delivery_released=True,
    )

    with pytest.raises(ValueError):
        execute_protected_handoff_release(
            bad
        )


def test_gp037_status_ready():
    status = (
        get_clouds_gp037_status_payload()
    )

    assert status["pack"] == "GP037"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert (
        status["delivery_release_executed"]
        is True
    )

    assert (
        status["tower_contacted"]
        is False
    )

    assert (
        status["external_delivery_attempted"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )
