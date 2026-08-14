from clouds.teller_grounds_summary_feed_adapter_service import (
    get_clouds_gp043_status_payload,
    get_gp043_certification_results,
)


def test_gp043_sources():
    results = (
        get_gp043_certification_results()
    )

    assert {
        item.source_id
        for item in results
    } == {
        "teller",
        "grounds",
    }


def test_gp043_certifications_accepted():
    for item in (
        get_gp043_certification_results()
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


def test_gp043_not_live():
    for item in (
        get_gp043_certification_results()
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


def test_gp043_status_ready():
    status = (
        get_clouds_gp043_status_payload()
    )

    assert status["pack"] == "GP043"
    assert status["status"] == "ready"

    assert (
        status["teller_adapter_ready"]
        is True
    )

    assert (
        status["grounds_adapter_ready"]
        is True
    )

    assert (
        status["real_live_connection_count"]
        == 0
    )
