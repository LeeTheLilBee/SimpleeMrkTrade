"""
GP077 — Six-source availability / truth-state matrix.

This separates:
- publisher/contract readiness
- operational source readiness
- real-live connection readiness

Those are NOT interchangeable.
"""

from tower.tower_clouds_gp072_source_wave1_closeout_service import (
    get_clouds_gp072_status_payload,
)

from tower.tower_clouds_gp076_source_wave2_closeout_service import (
    get_clouds_gp076_status_payload,
)


CANONICAL_SOURCE_IDS = (
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
    "atm_operations",
)


WAVE1_SOURCE_IDS = (
    "tower",
    "observatory",
    "archive_vault",
)


WAVE2_SOURCE_IDS = (
    "teller",
    "grounds",
    "atm_operations",
)


def build_source_availability_matrix():

    gp072 = (
        get_clouds_gp072_status_payload()
    )

    gp076 = (
        get_clouds_gp076_status_payload()
    )


    rows = []


    for source_id in (
        CANONICAL_SOURCE_IDS
    ):

        if source_id in WAVE1_SOURCE_IDS:

            state = (
                "publisher_certified_"
                "not_real_live"
            )

            contract_ready = True

            publisher_ready = True

            operational_verified = False

            current_live_available = False

            safe_fallback = (
                "projection_reference_only"
            )

            soulaana = (
                "I have a certified source-owned "
                "publisher contract here, but I am "
                "not calling it current live truth yet."
            )

        else:

            state = (
                "contract_bootstrap_"
                "operational_source_unverified"
            )

            contract_ready = True

            publisher_ready = True

            operational_verified = False

            current_live_available = False

            safe_fallback = (
                "withhold_current_claim"
            )

            soulaana = (
                "I know how this source will speak "
                "to Clouds, but its real operational "
                "system is not connected yet, so I "
                "will not invent a current state."
            )


        rows.append({

            "source_id":
            source_id,

            "availability_state":
            state,

            "contract_ready":
            contract_ready,

            "source_owned_seam_ready":
            publisher_ready,

            "operational_system_verified":
            operational_verified,

            "current_live_available":
            current_live_available,

            "safe_fallback":
            safe_fallback,

            "soulaana_explanation":
            soulaana,

            "business_risk_inferred_from_missing_data":
            False,

            "business_attention_escalated_from_missing_data":
            False,

            "counts_as_real_live_connection":
            False,

            "downstream_execution_performed":
            False,
        })


    return tuple(
        rows
    )


def get_clouds_gp077_status_payload():

    gp072 = (
        get_clouds_gp072_status_payload()
    )

    gp076 = (
        get_clouds_gp076_status_payload()
    )

    rows = (
        build_source_availability_matrix()
    )


    contract_ready_count = sum(
        item[
            "contract_ready"
        ]
        is True

        for item
        in rows
    )


    live_count = sum(
        item[
            "counts_as_real_live_connection"
        ]
        is True

        for item
        in rows
    )


    risk_inference_count = sum(
        item[
            "business_risk_inferred_from_missing_data"
        ]
        is True

        for item
        in rows
    )


    safe = (
        gp072["status"]
        == "ready"

        and gp076["status"]
        == "ready"

        and len(
            rows
        )
        == 6

        and tuple(
            item[
                "source_id"
            ]
            for item
            in rows
        )
        == CANONICAL_SOURCE_IDS

        and contract_ready_count
        == 6

        and live_count
        == 0

        and risk_inference_count
        == 0

        and all(
            item[
                "downstream_execution_performed"
            ]
            is False

            for item
            in rows
        )
    )


    return {

        "pack":
        "GP077",

        "section":
        (
            "SIX-SOURCE AVAILABILITY / "
            "TRUTH-STATE MATRIX"
        ),

        "status":
        (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue":
        safe,

        "source_count":
        len(
            rows
        ),

        "contract_ready_count":
        contract_ready_count,

        "wave1_publisher_certified_count":
        3,

        "wave2_contract_bootstrap_count":
        3,

        "operational_system_verified_count":
        0,

        "real_live_connection_count":
        live_count,

        "business_risk_inference_from_missing_data_count":
        risk_inference_count,

        "source_states":
        list(
            rows
        ),

        "real_live_feeds_connected":
        False,

        "hosted_staging_verified":
        False,

        "externally_beta_ready":
        False,

        "capital_movement_performed":
        False,

        "downstream_execution_performed":
        False,

        "next_pack":
        (
            "GP078 — MIXED-SOURCE "
            "SAFE-DEGRADATION REHEARSAL"
        ),
    }
