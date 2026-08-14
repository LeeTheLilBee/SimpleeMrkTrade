from clouds.capital_competition_service import (
    get_capital_competition_surface,
    get_clouds_gp051_status_payload,
)


def test_gp051_competition_is_review_order_not_allocation():
    surface = (
        get_capital_competition_surface()
    )

    assert surface.need_count == 2

    assert (
        surface
        .capital_competition_present
        is True
    )

    assert (
        surface.allocation_performed
        is False
    )

    assert (
        surface
        .capital_movement_performed
        is False
    )


def test_gp051_no_verified_capital_means_no_coverage_claim():
    surface = (
        get_capital_competition_surface()
    )

    assert (
        surface
        .verified_real_spendable_cents
        == 0
    )

    assert (
        surface
        .fully_covered_by_verified_real_capital
        is False
    )


def test_gp051_status():
    status = (
        get_clouds_gp051_status_payload()
    )

    assert status["status"] == "ready"

    assert (
        status[
            "review_order_is_allocation"
        ]
        is False
    )

    assert (
        status[
            "capital_movement_performed"
        ]
        is False
    )
