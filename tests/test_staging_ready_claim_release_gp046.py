from ob_owner_experience.staging_ready_claim_release import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_staging_ready_claim_release_bundle,
    build_staging_ready_claim_release_handoff,
    build_staging_ready_claim_release_record,
    build_staging_ready_claim_release_status,
)


def test_gp046_release_record():
    record = build_staging_ready_claim_release_record()
    assert record["gp045_release_gate_ready"] is True
    assert record["hosted_runtime_verified"] is True
    assert record["hosted_live_route_verified"] is True
    assert record["return_session_continuity_verified"] is True
    assert record["hosted_safety_locks_verified"] is True
    assert record["staging_ready_claim_released"] is True
    assert record["staging_ready"] is True
    assert record["staging_readiness_granted"] is True
    assert record["production_deploy_enabled"] is False
    assert record["broker_submission_enabled"] is False
    assert record["real_capital_movement_enabled"] is False
    assert record["live_auto_locked"] is True


def test_gp046_status_bundle_handoff():
    status = build_staging_ready_claim_release_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_staging_ready_claim_release_bundle()
    assert bundle["package"] == "ob_staging_ready_claim_release_gp046"
    assert bundle["staging_ready_claim_released"] is True
    assert bundle["source_dependency"] == "GP045"
    assert bundle["release_boundary"]["staging_ready"] is True
    assert bundle["release_boundary"]["production_deploy_enabled"] is False
    assert "STAGING_READY" not in bundle["must_not_claim"]
    assert "production deployment" in bundle["not_authorized"]

    handoff = build_staging_ready_claim_release_handoff()
    assert "STAGING_READY is released for managed staging only." in handoff["next_builder_notes"]
    assert "Live Auto remains locked." in handoff["next_builder_notes"]
