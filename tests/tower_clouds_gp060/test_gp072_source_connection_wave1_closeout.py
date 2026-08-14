from tower.tower_clouds_gp072_source_wave1_closeout_service import (
    CONCLUSION,
    get_clouds_gp072_status_payload,
)


def test_gp072_wave1_ready():

    p = (
        get_clouds_gp072_status_payload()
    )

    assert p["pack"] == "GP072"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p[
            "source_ids"
        ]
        == [
            "tower",
            "observatory",
            "archive_vault",
        ]
    )

    assert (
        p[
            "source_owned_publisher_count"
        ]
        == 3
    )

    assert (
        p[
            "signed_transport_certification_count"
        ]
        == 3
    )

    assert (
        p[
            "clouds_adapter_certification_count"
        ]
        == 3
    )

    assert (
        p[
            "certification_verified_connection_state_count"
        ]
        == 3
    )


def test_gp072_no_fake_live():

    p = (
        get_clouds_gp072_status_payload()
    )

    assert (
        p[
            "real_live_connection_count"
        ]
        == 0
    )

    assert (
        p[
            "real_live_feeds_connected"
        ]
        is False
    )

    assert (
        p[
            "source_endpoints_contacted"
        ]
        is False
    )

    assert (
        p[
            "external_transport_attempted"
        ]
        is False
    )

    assert (
        p[
            "hosted_tower_integration_verified"
        ]
        is False
    )

    assert (
        p[
            "hosted_staging_verified"
        ]
        is False
    )

    assert (
        p[
            "external_beta_acceptance_recorded"
        ]
        is False
    )

    assert (
        p[
            "externally_beta_ready"
        ]
        is False
    )


def test_gp072_no_secret_execution_or_capital():

    p = (
        get_clouds_gp072_status_payload()
    )

    assert (
        p[
            "secret_material_persistence_count"
        ]
        == 0
    )

    assert (
        p[
            "capital_movement_performed"
        ]
        is False
    )

    assert (
        p[
            "downstream_execution_count"
        ]
        == 0
    )

    assert (
        p[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp072_conclusion():

    p = (
        get_clouds_gp072_status_payload()
    )

    assert (
        p["conclusion"]
        == CONCLUSION
    )
