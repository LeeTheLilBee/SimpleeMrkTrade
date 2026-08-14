from tower.tower_clouds_feed_connection_lifecycle import (
    FeedConnectionState,
)

from tower.tower_clouds_feed_connection_lifecycle_service import (
    get_clouds_gp067_status_payload,
    get_default_disconnected_connection_receipts,
    get_gp067_certification_scenarios,
)


def test_gp067_defaults_are_disconnected():

    receipts = (
        get_default_disconnected_connection_receipts()
    )

    assert len(receipts) == 6

    assert all(
        item.connection_state
        == FeedConnectionState
        .DISCONNECTED.value

        for item
        in receipts
    )

    assert all(
        item.counts_as_real_live_connection
        is False

        for item
        in receipts
    )


def test_gp067_cert_fixture_not_real_live():

    receipt = (
        get_gp067_certification_scenarios()[
            "certification_verified"
        ]
    )

    assert (
        receipt.connection_state
        == FeedConnectionState
        .CERTIFICATION_VERIFIED.value
    )

    assert (
        receipt.authenticated_message
        is True
    )

    assert (
        receipt.fresh_message
        is True
    )

    assert (
        receipt.counts_as_real_live_connection
        is False
    )


def test_gp067_stale_and_replay_degrade():

    scenarios = (
        get_gp067_certification_scenarios()
    )

    assert (
        scenarios[
            "stale_degraded"
        ].connection_state
        == FeedConnectionState
        .DEGRADED.value
    )

    assert (
        scenarios[
            "replay_degraded"
        ].connection_state
        == FeedConnectionState
        .DEGRADED.value
    )


def test_gp067_revoke_fails_closed():

    receipt = (
        get_gp067_certification_scenarios()[
            "revoked"
        ]
    )

    assert (
        receipt.connection_state
        == FeedConnectionState
        .REVOKED.value
    )

    assert receipt.revoked is True

    assert (
        receipt.counts_as_real_live_connection
        is False
    )


def test_gp067_status():

    status = (
        get_clouds_gp067_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "freshness_gate_ready"
        ]
        is True
    )

    assert (
        status[
            "disconnect_fail_closed"
        ]
        is True
    )

    assert (
        status[
            "real_live_connection_count"
        ]
        == 0
    )
