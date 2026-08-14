"""
GP072 — Source Connection Wave 1 closeout.

Wave 1 source-owned publisher seams are certified.

This is NOT yet a claim that real network/runtime connections
are active.
"""

from tower.tower_clouds_gp069_tower_publisher_service import (
    get_clouds_gp069_status_payload,
)

from tower.tower_clouds_gp070_observatory_publisher_service import (
    get_clouds_gp070_status_payload,
)

from tower.tower_clouds_gp071_vault_publisher_service import (
    get_clouds_gp071_status_payload,
)


CONCLUSION = (
    "TOWER_CLOUDS_SOURCE_WAVE_1_PUBLISHERS_"
    "READY_FOR_EXTERNAL_CONNECTION_CERTIFICATION"
)


WAVE1_SOURCE_IDS = (
    "tower",
    "observatory",
    "archive_vault",
)


def get_clouds_gp072_status_payload():

    statuses = (

        get_clouds_gp069_status_payload(),

        get_clouds_gp070_status_payload(),

        get_clouds_gp071_status_payload(),
    )


    publisher_count = len(
        statuses
    )


    ready_count = sum(
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


    certification_state_count = sum(
        item[
            "certification_connection_state"
        ]
        == "certification_verified"

        for item
        in statuses
    )


    real_live_count = sum(
        item[
            "counts_as_real_live_connection"
        ]
        is True

        for item
        in statuses
    )


    endpoint_count = sum(
        item[
            "source_endpoint_contacted"
        ]
        is True

        for item
        in statuses
    )


    external_transport_count = sum(
        item[
            "external_transport_attempted"
        ]
        is True

        for item
        in statuses
    )


    secret_persistence_count = sum(
        item[
            "secret_material_persisted"
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


    source_ids = tuple(
        item[
            "source_id"
        ]
        for item
        in statuses
    )


    safe = (
        publisher_count
        == 3

        and ready_count
        == 3

        and source_ids
        == WAVE1_SOURCE_IDS

        and signed_count
        == 3

        and adapter_count
        == 3

        and certification_state_count
        == 3

        and real_live_count
        == 0

        and endpoint_count
        == 0

        and external_transport_count
        == 0

        and secret_persistence_count
        == 0

        and execution_count
        == 0
    )


    return {

        "pack":
        "GP072",

        "section":
        (
            "SOURCE CONNECTION WAVE 1 / "
            "CROSS-CONTRACT CERTIFICATION CLOSEOUT"
        ),

        "status":
        "ready" if safe else "blocked",

        "safe_to_continue":
        safe,

        "source_ids":
        list(
            source_ids
        ),

        "source_owned_publisher_count":
        publisher_count,

        "ready_publisher_count":
        ready_count,

        "signed_transport_certification_count":
        signed_count,

        "clouds_adapter_certification_count":
        adapter_count,

        "certification_verified_connection_state_count":
        certification_state_count,

        "source_branch_commit_evidence_ready":
        True,

        "ready_for_external_connection_certification":
        safe,

        "real_live_connection_count":
        real_live_count,

        "real_live_feeds_connected":
        False,

        "source_endpoint_contact_count":
        endpoint_count,

        "source_endpoints_contacted":
        False,

        "external_transport_attempt_count":
        external_transport_count,

        "external_transport_attempted":
        False,

        "hosted_tower_integration_verified":
        False,

        "hosted_staging_verified":
        False,

        "external_beta_acceptance_recorded":
        False,

        "externally_beta_ready":
        False,

        "secret_material_persistence_count":
        secret_persistence_count,

        "capital_movement_performed":
        False,

        "downstream_execution_count":
        execution_count,

        "downstream_execution_performed":
        False,

        "conclusion":
        (
            CONCLUSION
            if safe
            else
            "TOWER_CLOUDS_SOURCE_WAVE_1_BLOCKED"
        ),

        "next_pack":
        (
            "GP073 — SOURCE CONNECTION WAVE 2 / "
            "TELLER SOURCE PUBLISHER"
        ),
    }
