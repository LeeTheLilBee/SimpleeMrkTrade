from tower.tower_clouds_gp071_vault_publisher_service import (
    get_clouds_gp071_status_payload,
)


def test_gp071_status():

    p = (
        get_clouds_gp071_status_payload()
    )

    assert p["pack"] == "GP071"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p[
            "source_id"
        ]
        == "archive_vault"
    )

    assert (
        p[
            "source_owned_publisher"
        ]
        is True
    )

    assert (
        p[
            "source_local_tests_passed"
        ]
        is True
    )

    assert (
        p[
            "signed_transport_certified"
        ]
        is True
    )

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
