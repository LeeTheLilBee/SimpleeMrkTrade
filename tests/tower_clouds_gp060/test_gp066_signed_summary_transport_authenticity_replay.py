from dataclasses import replace

from tower.tower_clouds_signed_summary_transport_service import (
    CERTIFICATION_SECRET,
    build_gp066_certification_envelope,
    get_clouds_gp066_status_payload,
    validate_signed_summary_transport,
)


def test_gp066_valid_signature():

    envelope = (
        build_gp066_certification_envelope()
    )

    receipt = (
        validate_signed_summary_transport(
            envelope,
            secret=(
                CERTIFICATION_SECRET
            ),
        )
    )

    assert (
        receipt
        .accepted_for_connection_evaluation
        is True
    )

    assert (
        receipt.signature_verified
        is True
    )

    assert (
        receipt
        .counts_as_real_live_connection
        is False
    )


def test_gp066_replay_fails_closed():

    envelope = (
        build_gp066_certification_envelope()
    )

    receipt = (
        validate_signed_summary_transport(
            envelope,
            secret=(
                CERTIFICATION_SECRET
            ),
            seen_message_ids=(
                envelope.message_id,
            ),
            seen_nonces=(
                envelope.nonce,
            ),
        )
    )

    assert (
        receipt.replay_rejected
        is True
    )

    assert (
        receipt
        .accepted_for_connection_evaluation
        is False
    )


def test_gp066_tamper_fails():

    envelope = (
        build_gp066_certification_envelope()
    )

    tampered = replace(
        envelope,
        payload={
            **envelope.payload,
            "health":
            "tampered",
        },
    )

    receipt = (
        validate_signed_summary_transport(
            tampered,
            secret=(
                CERTIFICATION_SECRET
            ),
        )
    )

    assert (
        receipt.body_integrity_verified
        is False
    )

    assert (
        receipt
        .accepted_for_connection_evaluation
        is False
    )


def test_gp066_status():

    status = (
        get_clouds_gp066_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "message_id_replay_rejection_ready"
        ]
        is True
    )

    assert (
        status[
            "nonce_replay_rejection_ready"
        ]
        is True
    )

    assert (
        status[
            "tamper_rejection_ready"
        ]
        is True
    )

    assert (
        status[
            "certification_fixture_counts_as_live"
        ]
        is False
    )
