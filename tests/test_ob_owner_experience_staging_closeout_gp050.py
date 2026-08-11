from ob_owner_experience.ob_owner_experience_staging_closeout import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_ob_owner_experience_staging_closeout_bundle,
    build_ob_owner_experience_staging_closeout_handoff,
    build_ob_owner_experience_staging_closeout_record,
    build_ob_owner_experience_staging_closeout_status,
)


def test_gp050_closeout_record():
    record = build_ob_owner_experience_staging_closeout_record()
    assert record["gp049_private_beta_access_hold_ready"] is True
    assert record["staging_ready"] is True
    assert record["staging_readiness_granted"] is True
    assert record["staging_closeout_ready"] is True
    assert record["owner_walkthrough_accepted"] is True
    assert record["hosted_runtime_verified"] is True
    assert record["hosted_live_route_verified"] is True
    assert record["private_beta_access_held"] is True
    assert record["private_beta_access_opened"] is False
    assert record["tester_credentials_issued"] is False
    assert record["production_deploy_enabled"] is False
    assert record["broker_submission_enabled"] is False
    assert record["real_capital_movement_enabled"] is False
    assert record["live_auto_locked"] is True


def test_gp050_status_bundle_handoff():
    status = build_ob_owner_experience_staging_closeout_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_ob_owner_experience_staging_closeout_bundle()
    assert bundle["package"] == "ob_owner_experience_staging_closeout_gp050"
    assert bundle["staging_closeout_ready"] is True
    assert bundle["source_dependency"] == "GP049"
    assert bundle["recommendation"] == "GO_FOR_TOWER_OB_STAGING_ACCEPTANCE_HANDOFF"
    assert bundle["gate_state"] == "ob_owner_experience_staging_closeout_sealed"
    assert bundle["release_boundary"]["staging_ready"] is True
    assert bundle["release_boundary"]["production_deploy_enabled"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "PRODUCTION_READY" in bundle["must_not_claim"]

    handoff = build_ob_owner_experience_staging_closeout_handoff()
    assert "Managed staging is STAGING_READY." in handoff["next_builder_notes"]
    assert "Private beta access remains held for owner approval." in handoff["next_builder_notes"]
    assert "Live Auto remains locked." in handoff["next_builder_notes"]
