from tower.tower_clouds_gp060_contract_service import (
    get_clouds_gp061_status_payload,
)


def test_gp061():

    p = (
        get_clouds_gp061_status_payload()
    )

    assert p["pack"] == "GP061"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p["phase_pack_end"]
        == "GP060"
    )

    assert (
        p["ready_for_tower_integration"]
        is True
    )

    assert (
        p["ready_for_real_feed_connection"]
        is True
    )

    assert (
        p["real_live_feeds_connected"]
        is False
    )

    assert (
        p["externally_beta_ready"]
        is False
    )
