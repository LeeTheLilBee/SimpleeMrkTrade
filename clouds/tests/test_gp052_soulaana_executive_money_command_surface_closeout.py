from clouds.executive_money_command_surface_service import (
    get_clouds_gp052_status_payload,
    get_executive_money_command_surface,
)


def test_gp052_strict_money_separation():
    surface = (
        get_executive_money_command_surface()
    )

    assert (
        surface
        .strict_money_separation_verified
        is True
    )

    assert (
        surface
        .verified_real_spendable_cents
        == 0
    )

    assert (
        surface.simulated_cents
        > 0
    )

    assert (
        surface
        .simulated_money_in_spendable_total
        is False
    )

    assert (
        surface
        .projected_money_in_spendable_total
        is False
    )


def test_gp052_soulaana_explains_money_picture():
    surface = (
        get_executive_money_command_surface()
    )

    assert surface.soulaana_owner_brief
    assert surface.soulaana_why_it_matters
    assert surface.soulaana_what_needs_attention
    assert surface.soulaana_what_can_wait
    assert surface.soulaana_next_step


def test_gp052_status():
    status = (
        get_clouds_gp052_status_payload()
    )

    assert status["pack"] == "GP052"

    assert status["status"] == "ready"

    assert (
        status[
            "strict_money_separation_verified"
        ]
        is True
    )

    assert (
        status[
            "real_money_claimed"
        ]
        is False
    )

    assert (
        status["conclusion"]
        == (
            "CLOUDS_PHASE_II_EXECUTIVE_"
            "MONEY_PICTURE_LAYER_READY"
        )
    )
