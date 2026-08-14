from clouds.phase_ii_owner_walkthrough_service import (
    get_clouds_gp059_status_payload,
    get_phase_ii_owner_walkthrough_surface,
)


def test_gp059_all_steps_pass():

    surface = (
        get_phase_ii_owner_walkthrough_surface()
    )

    assert (
        surface.step_count
        == 12
    )

    assert (
        surface.pass_count
        == 12
    )

    assert (
        surface.walkthrough_ready
        is True
    )


def test_gp059_external_states_remain_false():

    surface = (
        get_phase_ii_owner_walkthrough_surface()
    )

    assert (
        surface.external_claim_count
        == 0
    )

    assert (
        surface.execution_count
        == 0
    )

    assert (
        surface.real_live_feed_connected
        is False
    )

    assert (
        surface.hosted_tower_integration_verified
        is False
    )

    assert (
        surface.hosted_staging_verified
        is False
    )

    assert (
        surface.external_beta_acceptance_recorded
        is False
    )


def test_gp059_status():

    status = (
        get_clouds_gp059_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "walkthrough_pass_count"
        ]
        == 12
    )

    assert (
        status[
            "no_false_urgency_walkthrough_ready"
        ]
        is True
    )

    assert (
        status[
            "tower_boundary_preserved"
        ]
        is True
    )
