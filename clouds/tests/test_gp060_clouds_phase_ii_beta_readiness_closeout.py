from clouds.phase_ii_beta_closeout_service import (
    get_clouds_gp060_status_payload,
    get_clouds_phase_ii_closeout_surface,
)


def test_gp060_clouds_side_phase_ii_ready():

    surface = (
        get_clouds_phase_ii_closeout_surface()
    )

    closeout = (
        surface.closeout
    )

    assert (
        closeout.clouds_phase_ii_software_ready
        is True
    )

    assert (
        closeout.ready_for_tower_integration
        is True
    )

    assert (
        closeout.ready_for_real_feed_connection
        is True
    )


def test_gp060_external_beta_readiness_not_invented():

    closeout = (
        get_clouds_phase_ii_closeout_surface()
        .closeout
    )

    assert (
        closeout.real_live_feeds_connected
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


def test_gp060_no_execution_or_capital_authority():

    closeout = (
        get_clouds_phase_ii_closeout_surface()
        .closeout
    )

    assert (
        closeout
        .automatic_business_decision_performed
        is False
    )

    assert (
        closeout.allocation_performed
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


def test_gp060_status():

    status = (
        get_clouds_gp060_status_payload()
    )

    assert (
        status["pack"]
        == "GP060"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "clouds_phase_ii_software_ready"
        ]
        is True
    )

    assert (
        status[
            "externally_beta_ready"
        ]
        is False
    )

    assert (
        status["conclusion"]
        == (
            "CLOUDS_PHASE_II_READY_FOR_"
            "TOWER_INTEGRATION_AND_REAL_FEED_CONNECTION"
        )
    )
