from clouds.feed_degradation_service import (
    get_clouds_gp058_status_payload,
    get_gp058_certification_surfaces,
)


def test_gp058_missing_withholds_current_claim():

    surface = (
        get_gp058_certification_surfaces()[
            "missing"
        ]
    )

    assert (
        surface.degraded_source_count
        == 1
    )

    assert (
        surface.withheld_current_state_count
        == 1
    )

    assert (
        surface.last_known_falsely_current_count
        == 0
    )


def test_gp058_stale_does_not_override_business_health():

    surface = (
        get_gp058_certification_surfaces()[
            "stale"
        ]
    )

    assert (
        surface.business_health_override_count
        == 0
    )

    assert (
        surface.business_attention_escalation_count
        == 0
    )


def test_gp058_conflict_fails_safe():

    surface = (
        get_gp058_certification_surfaces()[
            "conflict"
        ]
    )

    assert (
        surface.all_degraded_sources_fail_safe
        is True
    )

    assert (
        surface.false_urgency_count
        == 0
    )


def test_gp058_status():

    status = (
        get_clouds_gp058_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "current_claim_withheld_when_degraded"
        ]
        is True
    )

    assert (
        status[
            "reference_data_label_required"
        ]
        is True
    )

    assert (
        status[
            "system_review_is_business_danger"
        ]
        is False
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )
