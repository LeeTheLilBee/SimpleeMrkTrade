"""
GP042 — ATM Operations + Archive Vault Real Summary Feed Adapters.

Contract-ready only.
"""

from __future__ import annotations

try:
    from .tower_ob_summary_feed_adapter_service import (
        get_clouds_gp041_status_payload,
    )

    from .real_summary_feed_adapter_service import (
        adapt_external_summary,
        build_adapter_spec,
        build_certification_result,
    )

except ImportError:
    from tower_ob_summary_feed_adapter_service import (
        get_clouds_gp041_status_payload,
    )

    from real_summary_feed_adapter_service import (
        adapt_external_summary,
        build_adapter_spec,
        build_certification_result,
    )


ATM_OPERATIONS_SUMMARY_ADAPTER = (
    build_adapter_spec(
        adapter_id=(
            "clouds-adapter-atm-operations-v1"
        ),

        source_id="atm_operations",

        source_contract_version=(
            "atm-operations-clouds-summary-v1"
        ),
    )
)


ARCHIVE_VAULT_SUMMARY_ADAPTER = (
    build_adapter_spec(
        adapter_id=(
            "clouds-adapter-archive-vault-v1"
        ),

        source_id="archive_vault",

        source_contract_version=(
            "archive-vault-clouds-summary-v1"
        ),
    )
)


def get_gp042_adapter_specs():
    return (
        ATM_OPERATIONS_SUMMARY_ADAPTER,
        ARCHIVE_VAULT_SUMMARY_ADAPTER,
    )


def get_gp042_certification_results():
    return (
        build_certification_result(
            ATM_OPERATIONS_SUMMARY_ADAPTER,
            sequence=4201,
        ),

        build_certification_result(
            ARCHIVE_VAULT_SUMMARY_ADAPTER,
            sequence=4202,
        ),
    )


def adapt_atm_operations_summary(
    payload,
    **kwargs,
):
    return adapt_external_summary(
        ATM_OPERATIONS_SUMMARY_ADAPTER,
        payload,
        **kwargs,
    )


def adapt_archive_vault_summary(
    payload,
    **kwargs,
):
    return adapt_external_summary(
        ARCHIVE_VAULT_SUMMARY_ADAPTER,
        payload,
        **kwargs,
    )


def get_clouds_gp042_status_payload():
    gp041 = (
        get_clouds_gp041_status_payload()
    )

    specs = (
        get_gp042_adapter_specs()
    )

    results = (
        get_gp042_certification_results()
    )


    safe = (
        gp041["status"] == "ready"

        and gp041[
            "safe_to_continue"
        ]
        is True

        and len(specs) == 2

        and {
            item.source_id
            for item in specs
        }
        == {
            "atm_operations",
            "archive_vault",
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
        "pack": "GP042",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "ATM OPERATIONS + ARCHIVE VAULT "
            "REAL SUMMARY FEED ADAPTER CONTRACTS"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "adapter_count": 2,

        "accepted_certification_count": 2,

        "atm_operations_adapter_ready": True,

        "archive_vault_adapter_ready": True,

        "atm_operations_external_source_connected": False,

        "archive_vault_external_source_connected": False,

        "real_live_connection_count": 0,

        "real_live_feed_connected": False,

        "live_feed_claimed": False,

        "raw_source_access_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP043 — TELLER + GROUNDS REAL "
            "SUMMARY FEED ADAPTER CONTRACTS"
        ),
    }
