from tower.tower_clouds_gp069_tower_publisher_service import (
    get_clouds_gp069_status_payload,
)

from tower.tower_clouds_summary_publisher import (
    build_certification_summary,
    get_publisher_contract,
)


def test_gp069_tower_contract():

    contract = (
        get_publisher_contract()
    )

    assert (
        contract[
            "source_id"
        ]
        == "tower"
    )

    assert (
        contract[
            "source_contract_version"
        ]
        == "tower-clouds-summary-v1"
    )

    assert (
        contract[
            "source_owned_publisher"
        ]
        is True
    )


def test_gp069_fixture_not_live():

    payload = (
        build_certification_summary(

            source_sequence=6901,

            observed_at=(
                "2026-08-14T22:30:00Z"
            ),
        )
    )

    assert (
        payload["mode"]
        == "projection"
    )

    assert (
        payload[
            "source_claims_live"
        ]
        is False
    )


def test_gp069_status():

    p = (
        get_clouds_gp069_status_payload()
    )

    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p[
            "clouds_adapter_certified"
        ]
        is True
    )

    assert (
        p[
            "counts_as_real_live_connection"
        ]
        is False
    )

    assert (
        p[
            "external_transport_attempted"
        ]
        is False
    )
