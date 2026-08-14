import json
import pytest

from atm_operations.clouds_summary_publisher import (
    build_certification_summary,
    build_clouds_summary,
    get_publisher_contract,
    sign_clouds_summary,
)


CERT_SECRET = (
    b"wave2-certification-only"
)


def test_contract_identity():

    contract = (
        get_publisher_contract()
    )

    assert (
        contract[
            "source_id"
        ]
        == "atm_operations"
    )

    assert (
        contract[
            "source_contract_version"
        ]
        == "atm-operations-clouds-summary-v1"
    )

    assert (
        contract[
            "source_owned_contract_bootstrap"
        ]
        is True
    )


def test_operational_truth_locked():

    contract = (
        get_publisher_contract()
    )

    assert (
        contract[
            "operational_system_verified"
        ]
        is False
    )

    assert (
        contract[
            "real_business_data_connected"
        ]
        is False
    )

    assert (
        contract[
            "source_endpoint_available"
        ]
        is False
    )


def test_certification_projection_only():

    payload = (
        build_certification_summary(

            source_sequence=1,

            observed_at=(
                "2026-08-14T23:00:00Z"
            ),
        )
    )

    assert (
        payload[
            "mode"
        ]
        == "projection"
    )

    assert (
        payload[
            "source_claims_live"
        ]
        is False
    )

    assert (
        payload[
            "health"
        ]
        == "unknown"
    )

    assert (
        payload[
            "readiness"
        ]
        == "planning"
    )


def test_projection_live_claim_rejected():

    with pytest.raises(
        ValueError
    ):

        build_clouds_summary(

            source_sequence=2,

            observed_at=(
                "2026-08-14T23:00:00Z"
            ),

            health="unknown",

            readiness="planning",

            attention="informational",

            headline="test",

            explanation="test",

            owner_message="test",

            mode="projection",

            source_claims_live=True,
        )


def test_secret_not_serialized():

    payload = (
        build_certification_summary(

            source_sequence=3,

            observed_at=(
                "2026-08-14T23:00:00Z"
            ),
        )
    )

    signed = (
        sign_clouds_summary(

            payload,

            secret=CERT_SECRET,

            message_id="message-3",

            nonce="nonce-3",

            sent_at=(
                "2026-08-14T23:00:00Z"
            ),

            certification_fixture_only=True,
        )
    )

    encoded = (
        json.dumps(
            signed,
            sort_keys=True,
        )
    )

    assert (
        "wave2-certification-only"
        not in encoded
    )

    assert (
        signed[
            "certification_fixture_only"
        ]
        is True
    )
