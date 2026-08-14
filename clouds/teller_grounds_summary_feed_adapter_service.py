"""
GP043 — Teller + Grounds Real Summary Feed Adapters.

Contract-ready only.
"""

from __future__ import annotations

try:
    from .atm_vault_summary_feed_adapter_service import (
        get_clouds_gp042_status_payload,
    )

    from .real_summary_feed_adapter_service import (
        adapt_external_summary,
        build_adapter_spec,
        build_certification_result,
    )

except ImportError:
    from atm_vault_summary_feed_adapter_service import (
        get_clouds_gp042_status_payload,
    )

    from real_summary_feed_adapter_service import (
        adapt_external_summary,
        build_adapter_spec,
        build_certification_result,
    )


TELLER_SUMMARY_ADAPTER = (
    build_adapter_spec(
        adapter_id=(
            "clouds-adapter-teller-v1"
        ),

        source_id="teller",

        source_contract_version=(
            "teller-clouds-summary-v1"
        ),
    )
)


GROUNDS_SUMMARY_ADAPTER = (
    build_adapter_spec(
        adapter_id=(
            "clouds-adapter-grounds-v1"
        ),

        source_id="grounds",

        source_contract_version=(
            "grounds-clouds-summary-v1"
        ),
    )
)


def get_gp043_adapter_specs():
    return (
        TELLER_SUMMARY_ADAPTER,
        GROUNDS_SUMMARY_ADAPTER,
    )


def get_gp043_certification_results():
    return (
        build_certification_result(
            TELLER_SUMMARY_ADAPTER,
            sequence=4301,
        ),

        build_certification_result(
            GROUNDS_SUMMARY_ADAPTER,
            sequence=4302,
        ),
    )


def adapt_teller_summary(
    payload,
    **kwargs,
):
    return adapt_external_summary(
        TELLER_SUMMARY_ADAPTER,
        payload,
        **kwargs,
    )


def adapt_grounds_summary(
    payload,
    **kwargs,
):
    return adapt_external_summary(
        GROUNDS_SUMMARY_ADAPTER,
        payload,
        **kwargs,
    )


def get_clouds_gp043_status_payload():
    gp042 = (
        get_clouds_gp042_status_payload()
    )

    specs = (
        get_gp043_adapter_specs()
    )

    results = (
        get_gp043_certification_results()
    )


    safe = (
        gp042["status"] == "ready"

        and gp042[
            "safe_to_continue"
        ]
        is True

        and len(specs) == 2

        and {
            item.source_id
            for item in specs
        }
        == {
            "teller",
            "grounds",
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
            item
            .counts_as_real_live_connection
            is False
            for item in results
        )
    )


    return {
        "pack": "GP043",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "TELLER + GROUNDS REAL "
            "SUMMARY FEED ADAPTER CONTRACTS"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "adapter_count": 2,

        "accepted_certification_count": 2,

        "teller_adapter_ready": True,

        "grounds_adapter_ready": True,

        "teller_external_source_connected": False,

        "grounds_external_source_connected": False,

        "real_live_connection_count": 0,

        "real_live_feed_connected": False,

        "live_feed_claimed": False,

        "raw_source_access_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP044 — SIX-SOURCE REAL FEED ADAPTER "
            "REGISTRY / LIVE CONNECTION READINESS GATE"
        ),
    }
