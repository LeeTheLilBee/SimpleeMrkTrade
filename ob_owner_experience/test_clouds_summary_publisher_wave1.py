import json
import pytest

from ob_owner_experience.clouds_summary_publisher import (
    build_certification_summary,
    get_publisher_contract,
    sign_clouds_summary,
)


CERT_SECRET = (
    b"wave1-certification-only"
)


def test_publisher_contract():

    contract = (
        get_publisher_contract()
    )

    assert (
        contract[
            "source_id"
        ]
        == "observatory"
    )

    assert (
        contract[
            "source_contract_version"
        ]
        == "observatory-clouds-summary-v1"
    )

    assert (
        contract[
            "source_owned_publisher"
        ]
        is True
    )

    assert (
        contract[
            "secret_material_persisted"
        ]
        is False
    )

    assert (
        contract[
            "external_transport_performed"
        ]
        is False
    )


def test_certification_is_projection_only():

    payload = (
        build_certification_summary(

            source_sequence=1,

            observed_at=(
                "2026-08-14T22:30:00Z"
            ),
        )
    )

    assert (
        payload["mode"]
        == "projection"
    )

    assert (
        payload[
            "source_claims_live"
        ]
        is False
    )


def test_signing_does_not_serialize_secret():

    payload = (
        build_certification_summary(

            source_sequence=2,

            observed_at=(
                "2026-08-14T22:30:00Z"
            ),
        )
    )

    envelope = (
        sign_clouds_summary(

            payload,

            secret=CERT_SECRET,

            message_id=(
                "message-2"
            ),

            nonce=(
                "nonce-2"
            ),

            sent_at=(
                "2026-08-14T22:30:00Z"
            ),

            certification_fixture_only=True,
        )
    )

    encoded = (
        json.dumps(
            envelope,
            sort_keys=True,
        )
    )

    assert (
        "wave1-certification-only"
        not in encoded
    )

    assert (
        envelope[
            "certification_fixture_only"
        ]
        is True
    )


def test_projection_cannot_claim_live():

    with pytest.raises(
        ValueError
    ):

        from ob_owner_experience.clouds_summary_publisher import (
            build_clouds_summary,
        )

        build_clouds_summary(

            source_sequence=3,

            observed_at=(
                "2026-08-14T22:30:00Z"
            ),

            health="healthy",

            readiness="ready",

            attention="none",

            headline="test",

            explanation="test",

            owner_message="test",

            mode="projection",

            source_claims_live=True,
        )
