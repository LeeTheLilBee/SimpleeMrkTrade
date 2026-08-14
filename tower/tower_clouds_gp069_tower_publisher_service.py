"""
GP069 — Tower source-owned Clouds publisher certification.
"""

from tower.tower_clouds_wave1_source_evidence import (
    WAVE1_SOURCE_EVIDENCE,
)


def get_clouds_gp069_status_payload():

    item = (
        WAVE1_SOURCE_EVIDENCE[
            "tower"
        ]
    )

    safe = all(
        (
            item[
                "source_owned_publisher"
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

            item[
                "external_source_connected"
            ]
            is False,

            item[
                "external_connection_verified"
            ]
            is False,

            item[
                "counts_as_real_live_connection"
            ]
            is False,
        )
    )

    return {

        "pack":
        "GP069",

        "source_id":
        "tower",

        "section":
        "TOWER SOURCE-OWNED CLOUDS SUMMARY PUBLISHER",

        "status":
        "ready" if safe else "blocked",

        "safe_to_continue":
        safe,

        **item,

        "certification_mode":
        "projection",

        "certification_connection_state":
        "certification_verified",

        "real_live_connection_count":
        0,

        "source_endpoint_contacted":
        False,

        "external_transport_attempted":
        False,

        "secret_material_persisted":
        False,

        "downstream_execution_performed":
        False,
    }
