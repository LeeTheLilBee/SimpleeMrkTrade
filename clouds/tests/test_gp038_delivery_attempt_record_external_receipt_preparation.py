from dataclasses import replace

import pytest

from clouds.protected_handoff_delivery_attempt_service import (
    build_delivery_attempt_record,
    get_clouds_gp038_status_payload,
    get_gp038_delivery_attempt_record,
)

from clouds.protected_handoff_release_execution_service import (
    get_gp037_release_execution,
)


def test_gp038_attempt_record_ready():
    record = (
        get_gp038_delivery_attempt_record()
    )

    assert (
        record.attempt_state
        == "awaiting_external_transport"
    )

    assert (
        record.delivery_attempt_record_prepared
        is True
    )


def test_gp038_external_transport_not_invoked():
    record = (
        get_gp038_delivery_attempt_record()
    )

    assert (
        record.external_transport_invoked
        is False
    )

    assert (
        record.tower_contacted
        is False
    )


def test_gp038_receipt_still_required():
    record = (
        get_gp038_delivery_attempt_record()
    )

    assert (
        record.external_receipt_required
        is True
    )

    assert (
        record.external_receipt_present
        is False
    )

    assert (
        record.external_acceptance_verified
        is False
    )


def test_gp038_nonreleased_execution_fails_closed():
    execution = (
        get_gp037_release_execution()
    )

    bad = replace(
        execution,
        released_to_delivery_boundary=False,
    )

    with pytest.raises(ValueError):
        build_delivery_attempt_record(
            bad
        )


def test_gp038_status_ready():
    status = (
        get_clouds_gp038_status_payload()
    )

    assert status["pack"] == "GP038"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert (
        status["external_transport_invoked"]
        is False
    )

    assert (
        status["external_receipt_present"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )
