from tower.tower_clouds_gp076_source_wave2_closeout_service import (
    CONCLUSION,
    get_clouds_gp076_status_payload,
)


def test_gp076_contract_layer_ready():

    p = (
        get_clouds_gp076_status_payload()
    )

    assert p["pack"] == "GP076"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p[
            "source_ids"
        ]
        == [
            "teller",
            "grounds",
            "atm_operations",
        ]
    )

    assert (
        p[
            "source_contract_bootstrap_count"
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


def test_gp076_operational_truth_locked():

    p = (
        get_clouds_gp076_status_payload()
    )

    assert (
        p[
            "operational_source_system_verified_count"
        ]
        == 0
    )

    assert (
        p[
            "real_business_data_connection_count"
        ]
        == 0
    )

    assert (
        p[
            "source_endpoint_available_count"
        ]
        == 0
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


def test_gp076_gp077_staging_remains_closed():

    p = (
        get_clouds_gp076_status_payload()
    )

    assert (
        p[
            "real_source_implementation_required"
        ]
        is True
    )

    assert (
        p[
            "operational_source_systems_missing_or_unverified"
        ]
        is True
    )

    assert (
        p[
            "ready_for_gp077_hosted_end_to_end_staging"
        ]
        is False
    )

    assert (
        p[
            "hosted_end_to_end_staging_authorized"
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
            "externally_beta_ready"
        ]
        is False
    )


def test_gp076_no_execution():

    p = (
        get_clouds_gp076_status_payload()
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


def test_gp076_conclusion():

    p = (
        get_clouds_gp076_status_payload()
    )

    assert (
        p[
            "conclusion"
        ]
        == CONCLUSION
    )
