"""
GP076 — Source Connection Wave 2 truth-state closeout.

Wave 2 summary contracts are now source-owned and certified.

However, the underlying Teller / Grounds / ATM operational systems
have NOT been proven connected.

Therefore hosted end-to-end staging remains CLOSED.
"""

from tower.tower_clouds_gp073_teller_source_service import (
    get_clouds_gp073_status_payload,
)

from tower.tower_clouds_gp074_grounds_source_service import (
    get_clouds_gp074_status_payload,
)

from tower.tower_clouds_gp075_atm_source_service import (
    get_clouds_gp075_status_payload,
)


SOURCE_IDS = (
    "teller",
    "grounds",
    "atm_operations",
)


CONCLUSION = (
    "TOWER_CLOUDS_SOURCE_WAVE_2_CONTRACT_BOOTSTRAP_READY_"
    "REAL_SOURCE_IMPLEMENTATION_REQUIRED"
)


def get_clouds_gp076_status_payload():

    statuses = (

        get_clouds_gp073_status_payload(),

        get_clouds_gp074_status_payload(),

        get_clouds_gp075_status_payload(),
    )


    source_ids = tuple(
        item[
            "source_id"
        ]
        for item
        in statuses
    )


    contract_ready_count = sum(
        item[
            "source_contract_bootstrap_ready"
        ]
        is True

        for item
        in statuses
    )


    signed_count = sum(
        item[
            "signed_transport_certified"
        ]
        is True

        for item
        in statuses
    )


    adapter_count = sum(
        item[
            "clouds_adapter_certified"
        ]
        is True

        for item
        in statuses
    )


    operational_count = sum(
        item[
            "operational_system_verified"
        ]
        is True

        for item
        in statuses
    )


    data_connection_count = sum(
        item[
            "real_business_data_connected"
        ]
        is True

        for item
        in statuses
    )


    endpoint_count = sum(
        item[
            "source_endpoint_available"
        ]
        is True

        for item
        in statuses
    )


    live_count = sum(
        item[
            "real_live_connection"
        ]
        is True

        for item
        in statuses
    )


    execution_count = sum(
        item[
            "downstream_execution_performed"
        ]
        is True

        for item
        in statuses
    )


    contract_layer_safe = (

        len(
            statuses
        )
        == 3

        and source_ids
        == SOURCE_IDS

        and contract_ready_count
        == 3

        and signed_count
        == 3

        and adapter_count
        == 3

        and all(
            item[
                "status"
            ]
            == "ready"

            and item[
                "safe_to_continue"
            ]
            is True

            for item
            in statuses
        )

        and operational_count
        == 0

        and data_connection_count
        == 0

        and endpoint_count
        == 0

        and live_count
        == 0

        and execution_count
        == 0
    )


    # This is deliberately FALSE.
    #
    # We are not allowed to enter hosted end-to-end source-data
    # staging while all three operational source systems remain
    # unverified.
    ready_for_gp077_hosted_e2e = False


    return {

        "pack":
        "GP076",

        "section":
        (
            "SOURCE CONNECTION WAVE 2 / "
            "TRUTH-STATE CLOSEOUT"
        ),

        "status":
        (
            "ready"
            if contract_layer_safe
            else "blocked"
        ),

        "safe_to_continue":
        contract_layer_safe,

        "source_ids":
        list(
            source_ids
        ),

        "source_contract_bootstrap_count":
        contract_ready_count,

        "signed_transport_certification_count":
        signed_count,

        "clouds_adapter_certification_count":
        adapter_count,

        "operational_source_system_verified_count":
        operational_count,

        "real_business_data_connection_count":
        data_connection_count,

        "source_endpoint_available_count":
        endpoint_count,

        "real_live_connection_count":
        live_count,

        "source_contract_layer_ready":
        contract_layer_safe,

        "all_six_clouds_adapter_contracts_have_source_owned_seams":
        (
            contract_layer_safe
        ),

        "real_source_implementation_required":
        True,

        "operational_source_systems_missing_or_unverified":
        True,

        "ready_for_gp077_hosted_end_to_end_staging":
        ready_for_gp077_hosted_e2e,

        "hosted_end_to_end_staging_authorized":
        False,

        "real_live_feeds_connected":
        False,

        "source_endpoints_contacted":
        False,

        "external_business_data_transport_attempted":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "externally_beta_ready":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_count":
        execution_count,

        "downstream_execution_performed":
        False,

        "conclusion":
        (
            CONCLUSION

            if contract_layer_safe

            else
            "TOWER_CLOUDS_SOURCE_WAVE_2_BLOCKED"
        ),

        "next_required_work":
        (
            "SOURCE-SIDE OPERATIONAL IMPLEMENTATION / "
            "CONNECTION GAP REPAIR BEFORE GP077"
        ),
    }
