from tower.tower_clouds_gp079_soulaana_mixed_source_service import (
    build_soulaana_mixed_source_brief,
    get_clouds_gp079_status_payload,
)


def test_gp079_soulaana_first():

    brief = (
        build_soulaana_mixed_source_brief()
    )

    assert (
        brief[
            "soulaana_explanation_first"
        ]
        is True
    )

    assert (
        brief[
            "raw_evidence_first"
        ]
        is False
    )


def test_gp079_exact_source_split():

    brief = (
        build_soulaana_mixed_source_brief()
    )

    assert (
        brief[
            "projection_source_ids"
        ]
        == [
            "observatory",
            "tower",
            "archive_vault",
        ]
    )

    assert (
        brief[
            "unavailable_source_ids"
        ]
        == [
            "teller",
            "grounds",
            "atm_operations",
        ]
    )


def test_gp079_no_fake_business_danger():

    p = (
        get_clouds_gp079_status_payload()
    )

    assert p["status"] == "ready"

    assert (
        p[
            "business_danger_invented"
        ]
        is False
    )

    assert (
        p[
            "false_all_clear_given"
        ]
        is False
    )

    assert (
        p[
            "automatic_business_decision_performed"
        ]
        is False
    )
