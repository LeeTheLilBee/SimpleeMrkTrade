from tower.tower_clouds_feed_source_trust_service import (
    CANONICAL_CONNECTION_SOURCE_IDS,
    get_clouds_feed_source_trust_registry,
    get_clouds_gp065_status_payload,
)


def test_gp065_six_sources_exact():

    registry = (
        get_clouds_feed_source_trust_registry()
    )

    assert (
        tuple(
            item.source_id
            for item
            in registry.sources
        )
        == CANONICAL_CONNECTION_SOURCE_IDS
    )

    assert (
        registry.source_count
        == 6
    )


def test_gp065_no_secret_material_stored():

    registry = (
        get_clouds_feed_source_trust_registry()
    )

    assert (
        registry.secret_material_count
        == 0
    )

    assert all(
        item.credential_reference_only
        is True

        for item
        in registry.sources
    )


def test_gp065_status():

    status = (
        get_clouds_gp065_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "canonical_source_count"
        ]
        == 6
    )

    assert (
        status[
            "real_live_connection_count"
        ]
        == 0
    )

    assert (
        status[
            "external_transport_attempted"
        ]
        is False
    )
