from ob_owner_experience.hosted_runtime_verification_execution import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_hosted_runtime_verification_execution_bundle,
    build_hosted_runtime_verification_execution_handoff,
    build_hosted_runtime_verification_execution_status,
    build_hosted_runtime_verification_results,
)
from ob_owner_experience.hosted_runtime_verification_gate import REQUIRED_HOSTED_CHECKS


def test_gp041_runtime_results_all_checks_passed():
    results = build_hosted_runtime_verification_results()
    assert len(results) == len(REQUIRED_HOSTED_CHECKS)
    for item in results:
        assert item["required"] is True
        assert item["executed"] is True
        assert item["passed"] is True
        assert item["hosted_runtime_evidence_recorded"] is True
        assert item["staging_ready_claim_allowed_now"] is False


def test_gp041_status_bundle_handoff():
    status = build_hosted_runtime_verification_execution_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_hosted_runtime_verification_execution_bundle()
    assert bundle["package"] == "ob_hosted_runtime_verification_execution_gp041"
    assert bundle["hosted_runtime_verification_executed"] is True
    assert bundle["source_dependency"] == "GP040"
    assert bundle["recommendation"] == "GO_FOR_TOWER_OB_HOSTED_ROUTE_VERIFICATION"
    assert bundle["release_boundary"]["hosted_runtime_verified"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_hosted_runtime_verification_execution_handoff()
    assert "Hosted runtime verification execution is recorded." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
