from clouds.atm_vault_summary_feed_adapter_service import (
    get_clouds_gp042_status_payload,
    get_gp042_certification_results,
)


def test_gp042_sources():
    results = (
        get_gp042_certification_results()
    )

    assert {
        item.source_id
        for item in results
    } == {
        "atm_operations",
        "archive_vault",
    }


def test_gp042_certifications_accepted():
    for item in (
        get_gp042_certification_results()
    ):
        assert (
            item.validation_state
            == "accepted"
        )

        assert (
            item
            .accepted_for_clouds_interpretation
            is True
        )


def test_gp042_not_live():
    for item in (
        get_gp042_certification_results()
    ):
        assert (
            item.certification_fixture_only
            is True
        )

        assert (
            item.external_source_connected
            is False
        )

        assert (
            item.counts_as_real_live_connection
            is False
        )


def test_gp042_status_ready():
    status = (
        get_clouds_gp042_status_payload()
    )

    assert status["pack"] == "GP042"
    assert status["status"] == "ready"

    assert (
        status[
            "atm_operations_adapter_ready"
        ]
        is True
    )

    assert (
        status[
            "archive_vault_adapter_ready"
        ]
        is True
    )

    assert (
        status["real_live_connection_count"]
        == 0
    )
