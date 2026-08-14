"""
GP041 — Tower + Observatory Real Summary Feed Adapter Contracts.

Contract-ready only.

No real Tower or Observatory feed is claimed connected here.
"""

from __future__ import annotations

try:
    from .protected_handoff_corridor_closeout_service import (
        get_clouds_gp040_status_payload,
    )

    from .real_summary_feed_adapter_service import (
        adapt_external_summary,
        build_adapter_spec,
        build_certification_result,
    )

except ImportError:
    from protected_handoff_corridor_closeout_service import (
        get_clouds_gp040_status_payload,
    )

    from real_summary_feed_adapter_service import (
        adapt_external_summary,
        build_adapter_spec,
        build_certification_result,
    )


TOWER_SUMMARY_ADAPTER = (
    build_adapter_spec(
        adapter_id=(
            "clouds-adapter-tower-v1"
        ),

        source_id="tower",

        source_contract_version=(
            "tower-clouds-summary-v1"
        ),
    )
)


OBSERVATORY_SUMMARY_ADAPTER = (
    build_adapter_spec(
        adapter_id=(
            "clouds-adapter-observatory-v1"
        ),

        source_id="observatory",

        source_contract_version=(
            "observatory-clouds-summary-v1"
        ),
    )
)


def get_gp041_adapter_specs():
    return (
        TOWER_SUMMARY_ADAPTER,
        OBSERVATORY_SUMMARY_ADAPTER,
    )


def get_gp041_certification_results():
    return (
        build_certification_result(
            TOWER_SUMMARY_ADAPTER,
            sequence=4101,
        ),

        build_certification_result(
            OBSERVATORY_SUMMARY_ADAPTER,
            sequence=4102,
        ),
    )


def adapt_tower_summary(
    payload,
    *,
    external_source_connected=False,
    external_connection_verified=False,
    certification_fixture_only=False,
    prior_feed_id=None,
    prior_sequence=None,
):
    return adapt_external_summary(
        TOWER_SUMMARY_ADAPTER,
        payload,

        external_source_connected=(
            external_source_connected
        ),

        external_connection_verified=(
            external_connection_verified
        ),

        certification_fixture_only=(
            certification_fixture_only
        ),

        prior_feed_id=prior_feed_id,
        prior_sequence=prior_sequence,
    )


def adapt_observatory_summary(
    payload,
    *,
    external_source_connected=False,
    external_connection_verified=False,
    certification_fixture_only=False,
    prior_feed_id=None,
    prior_sequence=None,
):
    return adapt_external_summary(
        OBSERVATORY_SUMMARY_ADAPTER,
        payload,

        external_source_connected=(
            external_source_connected
        ),

        external_connection_verified=(
            external_connection_verified
        ),

        certification_fixture_only=(
            certification_fixture_only
        ),

        prior_feed_id=prior_feed_id,
        prior_sequence=prior_sequence,
    )


def get_clouds_gp041_status_payload():
    gp040 = (
        get_clouds_gp040_status_payload()
    )

    specs = (
        get_gp041_adapter_specs()
    )

    results = (
        get_gp041_certification_results()
    )


    safe = (
        gp040["status"] == "ready"

        and gp040[
            "safe_to_continue"
        ]
        is True

        and len(specs) == 2

        and {
            item.source_id
            for item in specs
        }
        == {
            "tower",
            "observatory",
        }

        and all(
            item
            .accepted_for_clouds_interpretation
            is True
            for item in results
        )

        and all(
            item.certification_fixture_only
            is True
            for item in results
        )

        and all(
            item.external_source_connected
            is False
            for item in results
        )

        and all(
            item.external_connection_verified
            is False
            for item in results
        )

        and all(
            item
            .counts_as_real_live_connection
            is False
            for item in results
        )

        and all(
            item.cross_app_imports_used
            is False
            for item in results
        )
    )


    return {
        "pack": "GP041",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "TOWER + OBSERVATORY REAL "
            "SUMMARY FEED ADAPTER CONTRACTS"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "adapter_count": 2,

        "accepted_certification_count": (
            sum(
                item
                .accepted_for_clouds_interpretation
                is True
                for item in results
            )
        ),

        "tower_adapter_ready": True,

        "observatory_adapter_ready": True,

        "tower_external_source_connected": False,

        "observatory_external_source_connected": False,

        "real_live_connection_count": 0,

        "real_live_feed_connected": False,

        "live_feed_claimed": False,

        "certification_fixtures_live": False,

        "gp025_schema_reused": True,

        "gp025_validator_reused": True,

        "raw_source_access_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP042 — ATM OPERATIONS + ARCHIVE VAULT "
            "REAL SUMMARY FEED ADAPTER CONTRACTS"
        ),
    }
