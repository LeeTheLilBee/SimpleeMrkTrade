from tower.tower_clouds_gp078_mixed_source_rehearsal_service import (
    get_clouds_gp078_status_payload,
)


def test_gp078_mixed_source_counts():

    p = (
        get_clouds_gp078_status_payload()
    )

    assert p["status"] == "ready"

    assert (
        p[
            "canonical_source_count"
        ]
        == 6
    )

    assert (
        p[
            "projection_only_count"
        ]
        == 3
    )

    assert (
        p[
            "missing_count"
        ]
        == 3
    )

    assert (
        p[
            "healthy_live_count"
        ]
        == 0
    )


def test_gp078_no_false_urgency():

    p = (
        get_clouds_gp078_status_payload()
    )

    assert (
        p[
            "business_risk_inference_count"
        ]
        == 0
    )

    assert (
        p[
            "business_attention_escalation_count"
        ]
        == 0
    )

    assert (
        p[
            "false_urgency_count"
        ]
        == 0
    )


def test_gp078_safe_fallback():

    p = (
        get_clouds_gp078_status_payload()
    )

    assert (
        p[
            "withheld_current_state_count"
        ]
        == 3
    )

    assert (
        p[
            "projection_reference_count"
        ]
        == 3
    )

    assert (
        p[
            "last_known_falsely_current_count"
        ]
        == 0
    )

    assert (
        p[
            "all_degraded_sources_fail_safe"
        ]
        is True
    )
