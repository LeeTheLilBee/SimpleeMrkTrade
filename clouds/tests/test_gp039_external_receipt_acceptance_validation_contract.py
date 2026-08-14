from dataclasses import replace

from clouds.external_handoff_receipt_service import (
    build_gp039_certification_fixture,
    get_clouds_gp039_status_payload,
    get_gp039_fixture_validation,
    validate_external_handoff_receipt,
)


def test_gp039_fixture_validates_structure():
    result = (
        get_gp039_fixture_validation()
    )

    assert (
        result.validation_state
        == "valid"
    )

    assert (
        result.attempt_binding_verified
        is True
    )

    assert (
        result.envelope_binding_verified
        is True
    )


def test_gp039_fixture_never_counts_as_real_receipt():
    result = (
        get_gp039_fixture_validation()
    )

    assert result.fixture_only is True

    assert (
        result.counts_as_real_external_receipt
        is False
    )

    assert (
        result.handoff_delivered_verified
        is False
    )


def test_gp039_tampered_receipt_rejected():
    receipt = (
        build_gp039_certification_fixture()
    )

    bad = replace(
        receipt,
        delivery_target_id="tampered",
    )

    result = (
        validate_external_handoff_receipt(
            bad
        )
    )

    assert (
        result.validation_state
        == "rejected"
    )

    assert (
        result.counts_as_real_external_receipt
        is False
    )


def test_gp039_status_does_not_claim_live_receipt():
    status = (
        get_clouds_gp039_status_payload()
    )

    assert status["pack"] == "GP039"
    assert status["status"] == "ready"

    assert (
        status["receipt_validator_ready"]
        is True
    )

    assert (
        status["external_receipt_connected"]
        is False
    )

    assert (
        status["external_receipt_verified"]
        is False
    )

    assert (
        status["tower_receipt_verified"]
        is False
    )

    assert (
        status["handoff_delivered"]
        is False
    )
