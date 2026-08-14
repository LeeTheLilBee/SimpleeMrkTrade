import pytest

from clouds.ecosystem_feed_adapter_registry_service import (
    adapt_registered_external_summary,
    get_clouds_gp044_status_payload,
    get_ecosystem_feed_adapter_registry_surface,
    get_ecosystem_feed_adapter_registry_surface_payload,
    get_real_summary_feed_adapter_spec,
    get_registered_adapter_specs,
    get_registered_certification_results,
)

from clouds.operating_feed_ingestion import (
    CANONICAL_OPERATING_SOURCE_IDS,
)


def test_gp044_exact_six_sources():
    specs = (
        get_registered_adapter_specs()
    )

    assert (
        tuple(
            item.source_id
            for item in specs
        )
        == tuple(
            CANONICAL_OPERATING_SOURCE_IDS
        )
    )


def test_gp044_six_certification_results():
    results = (
        get_registered_certification_results()
    )

    assert len(results) == 6

    assert all(
        item.validation_state
        == "accepted"
        for item in results
    )


def test_gp044_every_fixture_non_live():
    results = (
        get_registered_certification_results()
    )

    assert all(
        item.certification_fixture_only
        is True
        for item in results
    )

    assert all(
        item.external_source_connected
        is False
        for item in results
    )

    assert all(
        item.external_connection_verified
        is False
        for item in results
    )

    assert all(
        item.counts_as_real_live_connection
        is False
        for item in results
    )


def test_gp044_unknown_source_fails_closed():
    with pytest.raises(KeyError):
        get_real_summary_feed_adapter_spec(
            "not-a-source"
        )


def test_gp044_surface_ready_for_connection_not_connected():
    surface = (
        get_ecosystem_feed_adapter_registry_surface()
    )

    assert surface.source_count == 6

    assert (
        surface.adapter_contract_ready_count
        == 6
    )

    assert (
        surface.accepted_certification_count
        == 6
    )

    assert (
        surface.external_source_connected_count
        == 0
    )

    assert (
        surface.verified_external_connection_count
        == 0
    )

    assert (
        surface.real_live_connection_count
        == 0
    )

    assert (
        surface
        .ready_for_external_feed_connection
        is True
    )

    assert (
        surface.real_live_feed_connected
        is False
    )


def test_gp044_no_cross_app_imports():
    surface = (
        get_ecosystem_feed_adapter_registry_surface()
    )

    assert (
        surface.cross_app_imports_used
        is False
    )

    assert (
        surface.raw_source_access_performed
        is False
    )

    assert (
        surface.downstream_execution_performed
        is False
    )


def test_gp044_payload_serializes():
    payload = (
        get_ecosystem_feed_adapter_registry_surface_payload()
    )

    assert (
        payload["source_count"]
        == len(
            payload["specs"]
        )
    )

    assert (
        payload[
            "accepted_certification_count"
        ]
        == 6
    )


def test_gp044_status_ready():
    status = (
        get_clouds_gp044_status_payload()
    )

    assert status["pack"] == "GP044"

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["canonical_source_count"]
        == 6
    )

    assert (
        status[
            "registered_adapter_count"
        ]
        == 6
    )

    assert (
        status[
            "adapter_contract_ready_count"
        ]
        == 6
    )

    assert (
        status[
            "accepted_certification_count"
        ]
        == 6
    )

    assert (
        status[
            "external_source_connected_count"
        ]
        == 0
    )

    assert (
        status[
            "real_live_connection_count"
        ]
        == 0
    )

    assert (
        status[
            "ready_for_external_feed_connection"
        ]
        is True
    )

    assert (
        status[
            "real_live_feed_connected"
        ]
        is False
    )

    assert (
        status[
            "live_feed_claimed"
        ]
        is False
    )

    assert (
        status[
            "live_requires_verified_external_connection"
        ]
        is True
    )

    assert (
        status[
            "fixture_live_claim_prohibited"
        ]
        is True
    )

    assert status["next_pack"] == (
        "GP045 — OWNER MEMORY / "
        "PERSISTENT ATTENTION STATE FOUNDATION"
    )
