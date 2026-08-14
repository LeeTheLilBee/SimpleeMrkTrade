from dataclasses import replace

import pytest

from clouds.real_summary_feed_adapter_service import (
    adapt_external_summary,
    build_certification_payload,
)

from clouds.tower_ob_summary_feed_adapter_service import (
    OBSERVATORY_SUMMARY_ADAPTER,
    TOWER_SUMMARY_ADAPTER,
    get_clouds_gp041_status_payload,
    get_gp041_certification_results,
)


def test_gp041_two_specs_certify():
    results = (
        get_gp041_certification_results()
    )

    assert len(results) == 2

    assert {
        item.source_id
        for item in results
    } == {
        "tower",
        "observatory",
    }


def test_gp041_certification_is_not_live():
    for result in (
        get_gp041_certification_results()
    ):
        assert (
            result.certification_fixture_only
            is True
        )

        assert (
            result.external_source_connected
            is False
        )

        assert (
            result.counts_as_real_live_connection
            is False
        )


def test_gp041_uses_gp025_validator():
    for result in (
        get_gp041_certification_results()
    ):
        assert (
            result.validation_state
            == "accepted"
        )

        assert (
            result.source_integrity_verified
            is True
        )

        assert (
            result
            .accepted_for_clouds_interpretation
            is True
        )


def test_gp041_source_mismatch_fails_closed():
    payload = (
        build_certification_payload(
            OBSERVATORY_SUMMARY_ADAPTER,
            sequence=4199,
        )
    )

    bad = replace(
        payload,
        source_id="tower",
    )

    with pytest.raises(ValueError):
        adapt_external_summary(
            OBSERVATORY_SUMMARY_ADAPTER,
            bad,

            certification_fixture_only=True,
        )


def test_gp041_fake_live_without_connection_fails_closed():
    payload = (
        build_certification_payload(
            TOWER_SUMMARY_ADAPTER,
            sequence=4198,
        )
    )

    bad = replace(
        payload,
        mode="live",
        source_claims_live=True,
        observed_at=(
            "2099-01-01T00:00:00Z"
        ),
    )

    with pytest.raises(ValueError):
        adapt_external_summary(
            TOWER_SUMMARY_ADAPTER,
            bad,

            external_source_connected=False,
            external_connection_verified=False,
            certification_fixture_only=False,
        )


def test_gp041_fixture_cannot_masquerade_live():
    payload = (
        build_certification_payload(
            TOWER_SUMMARY_ADAPTER,
            sequence=4197,
        )
    )

    bad = replace(
        payload,
        mode="live",
        source_claims_live=True,
        observed_at=(
            "2099-01-01T00:00:00Z"
        ),
    )

    with pytest.raises(ValueError):
        adapt_external_summary(
            TOWER_SUMMARY_ADAPTER,
            bad,

            external_source_connected=True,
            external_connection_verified=True,
            certification_fixture_only=True,
        )


def test_gp041_status_ready():
    status = (
        get_clouds_gp041_status_payload()
    )

    assert status["pack"] == "GP041"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True

    assert (
        status["adapter_count"]
        == 2
    )

    assert (
        status["tower_adapter_ready"]
        is True
    )

    assert (
        status[
            "observatory_adapter_ready"
        ]
        is True
    )

    assert (
        status[
            "real_live_connection_count"
        ]
        == 0
    )

    assert (
        status[
            "real_live_feed_connected"
        ]
        is False
    )
