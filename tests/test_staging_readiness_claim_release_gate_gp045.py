from ob_owner_experience.staging_readiness_claim_release_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_staging_readiness_claim_release_gate_bundle,
    build_staging_readiness_claim_release_gate_handoff,
    build_staging_readiness_claim_release_record,
    build_staging_readiness_claim_release_status,
)


def test_gp045_claim_release_record_ready_but_not_released():
    record = build_staging_readiness_claim_release_record()
    assert record["gp044_hosted_safety_locks_verified"] is True
    assert record["hosted_runtime_verified"] is True
    assert record["hosted_live_route_verified"] is True
    assert record["return_session_continuity_verified"] is True
    assert record["hosted_safety_locks_verified"] is True
    assert record["staging_readiness_claim_release_ready"] is True
    assert record["staging_ready_claim_released"] is False
    assert record["staging_ready"] is False
    assert record["staging_readiness_granted"] is False
    assert record["must_release_global_staging_ready_hold_next"] is True


def test_gp045_status_bundle_handoff():
    status = build_staging_readiness_claim_release_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_staging_readiness_claim_release_gate_bundle()
    assert bundle["package"] == "ob_staging_readiness_claim_release_gate_gp045"
    assert bundle["staging_readiness_claim_release_ready"] is True
    assert bundle["source_dependency"] == "GP044"
    assert bundle["recommendation"] == "GO_FOR_STAGING_READY_CLAIM_RELEASE"
    assert bundle["gate_state"] == "ready_to_release_global_staging_ready_hold"
    assert bundle["release_boundary"]["staging_readiness_claim_release_ready"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert bundle["release_boundary"]["staging_ready_claim_released"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_staging_readiness_claim_release_gate_handoff()
    assert "The global STAGING_READY hold remains until GP046." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY from this package." in handoff["next_builder_notes"]
    assert "Next build is GP046 Staging Ready Claim Release." in handoff["next_builder_notes"]
