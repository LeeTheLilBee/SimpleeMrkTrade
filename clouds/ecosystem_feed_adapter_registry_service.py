"""
GP044 — Six-Source Real Feed Adapter Registry /
Live Connection Readiness Gate.

PERFORMANCE REPAIR
------------------

GP044 is the registry closeout itself.

It must validate the actual six registered adapter contracts
and actual six certification results directly.

It must NOT recursively invoke GP041, GP042, and GP043 status
payloads and then rebuild those same certification artifacts
again.

Immutable registry/spec/certification objects are cached inside
this process so repeated status/surface reads do not repeatedly
reconstruct the same projection certification chain.

Safety semantics are unchanged.
"""

from __future__ import annotations

from functools import lru_cache

try:
    from .atm_vault_summary_feed_adapter_service import (
        get_gp042_adapter_specs,
        get_gp042_certification_results,
    )

    from .ecosystem_feed_adapter_registry import (
        EcosystemFeedAdapterRegistrySurface,
    )

    from .operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
    )

    from .real_summary_feed_adapter_service import (
        adapt_external_summary,
    )

    from .teller_grounds_summary_feed_adapter_service import (
        get_gp043_adapter_specs,
        get_gp043_certification_results,
    )

    from .tower_ob_summary_feed_adapter_service import (
        get_gp041_adapter_specs,
        get_gp041_certification_results,
    )

except ImportError:
    from atm_vault_summary_feed_adapter_service import (
        get_gp042_adapter_specs,
        get_gp042_certification_results,
    )

    from ecosystem_feed_adapter_registry import (
        EcosystemFeedAdapterRegistrySurface,
    )

    from operating_feed_ingestion import (
        CANONICAL_OPERATING_SOURCE_IDS,
    )

    from real_summary_feed_adapter_service import (
        adapt_external_summary,
    )

    from teller_grounds_summary_feed_adapter_service import (
        get_gp043_adapter_specs,
        get_gp043_certification_results,
    )

    from tower_ob_summary_feed_adapter_service import (
        get_gp041_adapter_specs,
        get_gp041_certification_results,
    )


@lru_cache(maxsize=1)
def _all_specs_unsorted():
    return (
        get_gp041_adapter_specs()
        + get_gp042_adapter_specs()
        + get_gp043_adapter_specs()
    )


@lru_cache(maxsize=1)
def _all_results_unsorted():
    return (
        get_gp041_certification_results()
        + get_gp042_certification_results()
        + get_gp043_certification_results()
    )


@lru_cache(maxsize=1)
def get_registered_adapter_specs():

    all_specs = (
        _all_specs_unsorted()
    )

    by_source = {
        item.source_id: item
        for item in all_specs
    }


    if (
        len(by_source)
        != len(all_specs)
    ):
        raise RuntimeError(
            "Duplicate source adapter registration detected."
        )


    canonical = tuple(
        CANONICAL_OPERATING_SOURCE_IDS
    )


    if (
        set(by_source)
        != set(canonical)
    ):
        raise RuntimeError(
            "Adapter registry does not match canonical GP025 sources."
        )


    return tuple(
        by_source[
            source_id
        ]
        for source_id
        in canonical
    )


@lru_cache(maxsize=1)
def get_registered_certification_results():

    all_results = (
        _all_results_unsorted()
    )


    by_source = {
        item.source_id: item
        for item in all_results
    }


    canonical = tuple(
        CANONICAL_OPERATING_SOURCE_IDS
    )


    if (
        len(by_source)
        != len(all_results)
    ):
        raise RuntimeError(
            "Duplicate certification source detected."
        )


    if (
        set(by_source)
        != set(canonical)
    ):
        raise RuntimeError(
            "Certification results do not cover canonical sources."
        )


    return tuple(
        by_source[
            source_id
        ]
        for source_id
        in canonical
    )


def get_real_summary_feed_adapter_spec(
    source_id,
):

    for spec in (
        get_registered_adapter_specs()
    ):

        if (
            spec.source_id
            == source_id
        ):
            return spec


    raise KeyError(
        "Unknown registered feed source: "
        f"{source_id}"
    )


def adapt_registered_external_summary(
    payload,
    *,
    external_source_connected=False,
    external_connection_verified=False,
    certification_fixture_only=False,
    prior_feed_id=None,
    prior_sequence=None,
):
    """
    Canonical external summary adapter entrypoint.
    """

    spec = (
        get_real_summary_feed_adapter_spec(
            payload.source_id
        )
    )


    return adapt_external_summary(
        spec,
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

        prior_feed_id=(
            prior_feed_id
        ),

        prior_sequence=(
            prior_sequence
        ),
    )


@lru_cache(maxsize=1)
def get_ecosystem_feed_adapter_registry_surface():

    specs = (
        get_registered_adapter_specs()
    )

    results = (
        get_registered_certification_results()
    )


    contract_ready_count = sum(
        item.adapter_contract_ready
        is True
        for item in results
    )


    accepted_count = sum(
        item
        .accepted_for_clouds_interpretation
        is True
        for item in results
    )


    connected_count = sum(
        item.external_source_connected
        is True
        for item in results
    )


    verified_count = sum(
        item.external_connection_verified
        is True
        for item in results
    )


    live_count = sum(
        item
        .counts_as_real_live_connection
        is True
        for item in results
    )


    fixture_count = sum(
        item.certification_fixture_only
        is True
        for item in results
    )


    integrity_verified_count = sum(
        item.source_integrity_verified
        is True
        for item in results
    )


    no_raw_access = all(
        item.raw_source_access_performed
        is False
        for item in results
    )


    no_execution = all(
        item.downstream_execution_performed
        is False
        for item in results
    )


    no_cross_imports = all(
        item.cross_app_imports_used
        is False
        for item in results
    )


    canonical_sources = tuple(
        CANONICAL_OPERATING_SOURCE_IDS
    )


    exact_sources = (
        tuple(
            item.source_id
            for item in specs
        )
        == canonical_sources
    )


    ready_for_connection = (
        len(specs) == 6

        and len(results) == 6

        and exact_sources

        and contract_ready_count == 6

        and accepted_count == 6

        and fixture_count == 6

        and integrity_verified_count == 6

        and connected_count == 0

        and verified_count == 0

        and live_count == 0

        and no_raw_access

        and no_execution

        and no_cross_imports
    )


    return (
        EcosystemFeedAdapterRegistrySurface(
            title=(
                "Simplee World Real Summary "
                "Feed Adapter Registry"
            ),

            source_ids=tuple(
                item.source_id
                for item in specs
            ),

            specs=(
                specs
            ),

            certification_results=(
                results
            ),

            source_count=(
                len(specs)
            ),

            adapter_contract_ready_count=(
                contract_ready_count
            ),

            accepted_certification_count=(
                accepted_count
            ),

            external_source_connected_count=(
                connected_count
            ),

            verified_external_connection_count=(
                verified_count
            ),

            real_live_connection_count=(
                live_count
            ),

            ready_for_external_feed_connection=(
                ready_for_connection
            ),

            real_live_feed_connected=False,

            live_feed_claimed=False,

            raw_source_access_performed=False,

            downstream_execution_performed=False,

            cross_app_imports_used=False,

            boundary_notice=(
                "All six canonical source adapter contracts "
                "are ready and certified against GP025. "
                "Certification fixtures remain non-live. "
                "No source is called connected until a real "
                "external integration verifies that connection "
                "and supplies a valid live envelope."
            ),
        )
    )


def get_ecosystem_feed_adapter_registry_surface_payload():

    return (
        get_ecosystem_feed_adapter_registry_surface()
        .to_dict()
    )


def get_clouds_gp044_status_payload():

    # ONE registry construction.
    #
    # The registry directly contains and validates all six
    # GP041–GP043 adapter specifications and certification
    # results.
    surface = (
        get_ecosystem_feed_adapter_registry_surface()
    )


    specs = (
        get_registered_adapter_specs()
    )

    results = (
        get_registered_certification_results()
    )


    canonical_sources = tuple(
        CANONICAL_OPERATING_SOURCE_IDS
    )


    exact_source_order = (
        surface.source_ids
        == canonical_sources
    )


    every_result_safe = all(

        item.adapter_contract_ready
        is True

        and item.certification_fixture_only
        is True

        and item.external_source_connected
        is False

        and item.external_connection_verified
        is False

        and item.envelope_mode
        == "projection"

        and item
        .accepted_for_clouds_interpretation
        is True

        and item.validation_state
        == "accepted"

        and item.source_integrity_verified
        is True

        and item
        .counts_as_real_live_connection
        is False

        and item.raw_source_access_performed
        is False

        and item.downstream_execution_performed
        is False

        and item.cross_app_imports_used
        is False

        for item in results
    )


    every_spec_safe = all(

        item.supports_projection
        is True

        and item.supports_live
        is True

        and item
        .external_connection_verification_required
        is True

        and item.raw_source_access_allowed
        is False

        and item.downstream_execution_allowed
        is False

        and item.cross_app_import_allowed
        is False

        for item in specs
    )


    safe = (
        surface.source_count == 6

        and len(specs) == 6

        and len(results) == 6

        and exact_source_order

        and every_spec_safe

        and every_result_safe

        and surface
        .adapter_contract_ready_count
        == 6

        and surface
        .accepted_certification_count
        == 6

        and surface
        .external_source_connected_count
        == 0

        and surface
        .verified_external_connection_count
        == 0

        and surface
        .real_live_connection_count
        == 0

        and surface
        .ready_for_external_feed_connection
        is True

        and surface
        .real_live_feed_connected
        is False

        and surface
        .live_feed_claimed
        is False

        and surface
        .raw_source_access_performed
        is False

        and surface
        .downstream_execution_performed
        is False

        and surface
        .cross_app_imports_used
        is False
    )


    return {
        "pack": "GP044",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "SIX-SOURCE REAL FEED ADAPTER "
            "REGISTRY / LIVE CONNECTION READINESS GATE"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": (
            safe
        ),

        "canonical_source_count": 6,

        "registered_adapter_count": (
            surface.source_count
        ),

        "adapter_contract_ready_count": (
            surface
            .adapter_contract_ready_count
        ),

        "accepted_certification_count": (
            surface
            .accepted_certification_count
        ),

        "source_ids": list(
            surface.source_ids
        ),

        "tower_adapter_ready": (
            "tower"
            in surface.source_ids
        ),

        "observatory_adapter_ready": (
            "observatory"
            in surface.source_ids
        ),

        "atm_operations_adapter_ready": (
            "atm_operations"
            in surface.source_ids
        ),

        "archive_vault_adapter_ready": (
            "archive_vault"
            in surface.source_ids
        ),

        "teller_adapter_ready": (
            "teller"
            in surface.source_ids
        ),

        "grounds_adapter_ready": (
            "grounds"
            in surface.source_ids
        ),

        "external_source_connected_count": (
            surface
            .external_source_connected_count
        ),

        "verified_external_connection_count": (
            surface
            .verified_external_connection_count
        ),

        "real_live_connection_count": (
            surface
            .real_live_connection_count
        ),

        "ready_for_external_feed_connection": (
            surface
            .ready_for_external_feed_connection
        ),

        "real_live_feed_connected": False,

        "live_feed_claimed": False,

        "certification_fixtures_live": False,

        "gp025_schema_reused": True,

        "gp025_validator_reused": True,

        "live_requires_verified_external_connection": True,

        "fixture_live_claim_prohibited": True,

        "raw_source_access_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "upstream_status_recalculation_removed": True,

        "registry_objects_cached": True,

        "next_pack": (
            "GP045 — OWNER MEMORY / "
            "PERSISTENT ATTENTION STATE FOUNDATION"
        ),
    }
