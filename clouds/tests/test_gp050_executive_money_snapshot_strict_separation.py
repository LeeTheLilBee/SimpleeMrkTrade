from clouds.executive_money_snapshot_service import (
    get_clouds_gp050_status_payload,
    get_gp050_certification_money_snapshot,
)


def test_gp050_simulation_not_spendable():
    snapshot = (
        get_gp050_certification_money_snapshot()
    )

    assert (
        snapshot.simulated_cents
        > 0
    )

    assert (
        snapshot
        .verified_real_spendable_cents
        == 0
    )

    assert (
        snapshot
        .simulation_excluded_from_spendable
        is True
    )


def test_gp050_projection_not_spendable():
    snapshot = (
        get_gp050_certification_money_snapshot()
    )

    assert snapshot.projected_cents > 0

    assert (
        snapshot
        .projection_excluded_from_spendable
        is True
    )


def test_gp050_status():
    status = (
        get_clouds_gp050_status_payload()
    )

    assert status["status"] == "ready"

    assert (
        status[
            "verified_real_spendable_cents"
        ]
        == 0
    )

    assert (
        status["real_money_claimed"]
        is False
    )
