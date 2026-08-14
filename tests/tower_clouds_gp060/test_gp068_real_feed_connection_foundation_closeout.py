from tower.tower_clouds_feed_connection_foundation_closeout_service import (
    CONCLUSION,
    SOURCE_WAVE_1,
    build_feed_connection_foundation_closeout,
    get_clouds_gp068_status_payload,
)


def test_gp068_wave_1_ready():

    closeout = (
        build_feed_connection_foundation_closeout()
    )

    assert (
        closeout
        .ready_for_source_connection_wave_1
        is True
    )

    assert (
        closeout.wave_1_source_ids
        == SOURCE_WAVE_1
    )


def test_gp068_no_real_connection_invented():

    closeout = (
        build_feed_connection_foundation_closeout()
    )

    assert (
        closeout.real_live_connection_count
        == 0
    )

    assert (
        closeout.real_live_feeds_connected
        is False
    )

    assert (
        closeout.source_endpoints_contacted
        is False
    )

    assert (
        closeout.external_transport_attempted
        is False
    )

    assert (
        closeout.hosted_tower_integration_verified
        is False
    )

    assert (
        closeout.hosted_staging_verified
        is False
    )

    assert (
        closeout.external_beta_acceptance_recorded
        is False
    )

    assert (
        closeout.externally_beta_ready
        is False
    )


def test_gp068_no_secret_or_execution():

    closeout = (
        build_feed_connection_foundation_closeout()
    )

    assert (
        closeout.secret_material_persisted
        is False
    )

    assert (
        closeout.capital_movement_performed
        is False
    )

    assert (
        closeout.downstream_execution_performed
        is False
    )


def test_gp068_status():

    status = (
        get_clouds_gp068_status_payload()
    )

    assert (
        status["pack"]
        == "GP068"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "ready_for_source_connection_wave_1"
        ]
        is True
    )

    assert (
        status[
            "wave_1_source_ids"
        ]
        == [
            "tower",
            "observatory",
            "archive_vault",
        ]
    )

    assert (
        status["conclusion"]
        == CONCLUSION
    )
