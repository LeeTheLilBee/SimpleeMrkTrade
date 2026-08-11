from ob_owner_experience.hosted_runtime_verification_gate import (
    FALSE_FLAGS,
    REQUIRED_HOSTED_CHECKS,
    TRUE_FLAGS,
    build_hosted_runtime_verification_gate_bundle,
    build_hosted_runtime_verification_gate_handoff,
    build_hosted_runtime_verification_gate_status,
    build_hosted_runtime_verification_plan,
)


def test_gp040_verification_plan_ready_not_verified():
    plan = build_hosted_runtime_verification_plan()
    assert plan["gp039_redeploy_execution_receipt_recorded"] is True
    assert plan["hosted_runtime_verification_gate_ready"] is True
    assert plan["required_hosted_checks"] == list(REQUIRED_HOSTED_CHECKS)
    assert plan["hosted_runtime_checks_declared"] is True
    assert plan["hosted_runtime_verified"] is False
    assert plan["hosted_live_route_verified"] is False
    assert plan["staging_ready"] is False
    assert plan["staging_readiness_granted"] is False


def test_gp040_status_bundle_handoff():
    status = build_hosted_runtime_verification_gate_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_hosted_runtime_verification_gate_bundle()
    assert bundle["package"] == "ob_hosted_runtime_verification_gate_gp040"
    assert bundle["hosted_runtime_verification_gate_ready"] is True
    assert bundle["source_dependency"] == "GP039"
    assert bundle["recommendation"] == "GO_FOR_HOSTED_RUNTIME_VERIFICATION_EXECUTION"
    assert bundle["release_boundary"]["hosted_runtime_verified"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_hosted_runtime_verification_gate_handoff()
    assert "Hosted runtime verification gate is ready." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
