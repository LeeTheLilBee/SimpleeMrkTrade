from tower.tower_clouds_gp077_source_availability_service import (
    CANONICAL_SOURCE_IDS,
    build_source_availability_matrix,
    get_clouds_gp077_status_payload,
)


def test_gp077_exact_six_sources():

    rows = (
        build_source_availability_matrix()
    )

    assert len(rows) == 6

    assert (
        tuple(
            item[
                "source_id"
            ]
            for item
            in rows
        )
        == CANONICAL_SOURCE_IDS
    )


def test_gp077_no_live_invented():

    rows = (
        build_source_availability_matrix()
    )

    assert all(
        item[
            "counts_as_real_live_connection"
        ]
        is False

        for item
        in rows
    )

    assert all(
        item[
            "business_risk_inferred_from_missing_data"
        ]
        is False

        for item
        in rows
    )


def test_gp077_status():

    p = (
        get_clouds_gp077_status_payload()
    )

    assert p["status"] == "ready"

    assert (
        p[
            "contract_ready_count"
        ]
        == 6
    )

    assert (
        p[
            "wave1_publisher_certified_count"
        ]
        == 3
    )

    assert (
        p[
            "wave2_contract_bootstrap_count"
        ]
        == 3
    )

    assert (
        p[
            "real_live_connection_count"
        ]
        == 0
    )
