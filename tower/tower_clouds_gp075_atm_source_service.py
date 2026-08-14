"""
GP075 — Wave 2 source contract bootstrap status.
"""

from tower.tower_clouds_wave2_source_evidence import (
    WAVE2_SOURCE_EVIDENCE,
)


def get_clouds_gp075_status_payload():

    item = (
        WAVE2_SOURCE_EVIDENCE[
            "atm_operations"
        ]
    )


    safe = all(
        (
            item[
                "source_contract_bootstrap_ready"
            ]
            is True,

            item[
                "source_local_tests_passed"
            ]
            is True,

            item[
                "signed_transport_certified"
            ]
            is True,

            item[
                "clouds_adapter_certified"
            ]
            is True,

            bool(
                item[
                    "publisher_commit"
                ]
            ),

            item[
                "operational_system_verified"
            ]
            is False,

            item[
                "real_business_data_connected"
            ]
            is False,

            item[
                "source_endpoint_available"
            ]
            is False,

            item[
                "real_live_connection"
            ]
            is False,
        )
    )


    return {

        "pack":
        "GP075",

        "section":
        "ATM OPERATIONS SOURCE CONTRACT BOOTSTRAP",

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        **item,

        "certification_mode":
        "projection",

        "certification_fixture_only":
        True,

        "operational_system_verified":
        False,

        "real_business_data_connected":
        False,

        "source_endpoint_available":
        False,

        "external_transport_attempted":
        False,

        "real_live_connection_count":
        0,

        "hosted_staging_verified":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,
    }
