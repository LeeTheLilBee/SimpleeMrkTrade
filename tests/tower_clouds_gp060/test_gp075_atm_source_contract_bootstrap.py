from tower.tower_clouds_gp075_atm_source_service import (
    get_clouds_gp075_status_payload,
)


def test_gp075_ready_but_not_operational():

    p = (
        get_clouds_gp075_status_payload()
    )

    assert p["pack"] == "GP075"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p["source_id"]
        == "atm_operations"
    )

    assert (
        p[
            "source_contract_bootstrap_ready"
        ]
        is True
    )

    assert (
        p[
            "clouds_adapter_certified"
        ]
        is True
    )

    assert (
        p[
            "operational_system_verified"
        ]
        is False
    )

    assert (
        p[
            "real_business_data_connected"
        ]
        is False
    )

    assert (
        p[
            "real_live_connection_count"
        ]
        == 0
    )
