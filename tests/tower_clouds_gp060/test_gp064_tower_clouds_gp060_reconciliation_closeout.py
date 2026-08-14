from tower.tower_clouds_gp060_reconciliation_closeout_service import (
    CONCLUSION,
    get_clouds_gp064_status_payload,
)


def test_gp064():

    p = (
        get_clouds_gp064_status_payload()
    )

    assert p["pack"] == "GP064"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p[
            "default_deny_preserved"
        ]
        is True
    )

    assert (
        p[
            "ready_for_protected_runtime_integration"
        ]
        is True
    )

    assert (
        p[
            "clouds_source_branch_merged"
        ]
        is False
    )

    assert (
        p[
            "real_live_feeds_connected"
        ]
        is False
    )

    assert (
        p[
            "externally_beta_ready"
        ]
        is False
    )

    assert (
        p["conclusion"]
        == CONCLUSION
    )
