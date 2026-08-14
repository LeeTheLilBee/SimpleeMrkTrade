from tower.tower_clouds_gp080_prehosted_staging_readiness_service import (
    CONCLUSION,
    get_clouds_gp080_status_payload,
)


def test_gp080_ready_to_enter_staging():

    p = (
        get_clouds_gp080_status_payload()
    )

    assert p["pack"] == "GP080"
    assert p["status"] == "ready"
    assert p["safe_to_continue"] is True

    assert (
        p[
            "ready_for_hosted_staging_rehearsal"
        ]
        is True
    )

    assert (
        p[
            "hosted_staging_rehearsal_authorized"
        ]
        is True
    )


def test_gp080_tower_protection_preserved():

    p = (
        get_clouds_gp080_status_payload()
    )

    assert (
        p[
            "tower_owner_session_required"
        ]
        is True
    )

    assert (
        p[
            "tower_owner_permission_required"
        ]
        is True
    )

    assert (
        p[
            "tower_step_up_required"
        ]
        is True
    )

    assert (
        p[
            "tower_default_deny_preserved"
        ]
        is True
    )


def test_gp080_does_not_claim_staging_happened():

    p = (
        get_clouds_gp080_status_payload()
    )

    assert (
        p[
            "hosted_tower_integration_verified"
        ]
        is False
    )

    assert (
        p[
            "hosted_staging_verified"
        ]
        is False
    )

    assert (
        p[
            "verified_live_source_count"
        ]
        == 0
    )

    assert (
        p[
            "real_live_feeds_connected"
        ]
        is False
    )

    assert (
        p[
            "external_beta_acceptance_recorded"
        ]
        is False
    )

    assert (
        p[
            "externally_beta_ready"
        ]
        is False
    )


def test_gp080_no_execution():

    p = (
        get_clouds_gp080_status_payload()
    )

    assert (
        p[
            "capital_movement_performed"
        ]
        is False
    )

    assert (
        p[
            "automatic_business_decision_performed"
        ]
        is False
    )

    assert (
        p[
            "downstream_execution_performed"
        ]
        is False
    )


def test_gp080_conclusion():

    p = (
        get_clouds_gp080_status_payload()
    )

    assert (
        p["conclusion"]
        == CONCLUSION
    )
