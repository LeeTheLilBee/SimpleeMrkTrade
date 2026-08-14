from clouds.feed_resilience_service import (
    get_clouds_gp057_status_payload,
    get_gp057_certification_scenarios,
)


def test_gp057_projection_is_not_live_truth():

    surface = (
        get_gp057_certification_scenarios()[
            "projection"
        ]
    )

    assert (
        surface.projection_only_count
        == 6
    )

    assert (
        surface.healthy_live_count
        == 0
    )

    assert (
        surface.trusted_current_source_count
        == 0
    )


def test_gp057_missing_source_detected():

    surface = (
        get_gp057_certification_scenarios()[
            "missing"
        ]
    )

    assert (
        surface.missing_count
        == 1
    )

    assert (
        surface.business_risk_inference_count
        == 0
    )

    assert (
        surface.false_urgency_count
        == 0
    )


def test_gp057_stale_source_detected():

    surface = (
        get_gp057_certification_scenarios()[
            "stale"
        ]
    )

    assert (
        surface.stale_count
        == 1
    )

    assert (
        surface.business_attention_escalation_count
        == 0
    )


def test_gp057_conflict_source_detected():

    surface = (
        get_gp057_certification_scenarios()[
            "conflict"
        ]
    )

    assert (
        surface.conflict_count
        == 1
    )

    assert (
        surface.trusted_current_source_count
        == 0
    )


def test_gp057_status():

    status = (
        get_clouds_gp057_status_payload()
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status[
            "missing_detection_ready"
        ]
        is True
    )

    assert (
        status[
            "stale_detection_ready"
        ]
        is True
    )

    assert (
        status[
            "conflict_detection_ready"
        ]
        is True
    )

    assert (
        status[
            "data_degradation_is_business_risk"
        ]
        is False
    )

    assert (
        status[
            "false_urgency_count"
        ]
        == 0
    )
