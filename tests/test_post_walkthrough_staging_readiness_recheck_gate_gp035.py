from ob_owner_experience.post_walkthrough_staging_readiness_recheck_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_post_walkthrough_staging_readiness_record,
    build_post_walkthrough_staging_readiness_recheck_bundle,
    build_post_walkthrough_staging_readiness_recheck_handoff,
    build_post_walkthrough_staging_readiness_status,
)


def test_gp035_readiness_record():
    record = build_post_walkthrough_staging_readiness_record()
    assert record["recommendation"] == "GO_FOR_MANAGED_STAGING_REDEPLOY_PREP"
    assert record["owner_walkthrough_started"] is True
    assert record["owner_walkthrough_accepted"] is True
    assert record["managed_staging_redeploy_prep_required"] is True
    assert record["hosted_runtime_verification_required_after_redeploy"] is True
    assert record["staging_ready"] is False
    assert record["staging_readiness_granted"] is False


def test_gp035_status_bundle_handoff():
    status = build_post_walkthrough_staging_readiness_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_post_walkthrough_staging_readiness_recheck_bundle()
    assert bundle["package"] == "ob_post_walkthrough_staging_readiness_recheck_gate_gp035"
    assert bundle["readiness_recheck_ready"] is True
    assert bundle["source_dependency"] == "GP034"
    assert bundle["recommendation"] == "GO_FOR_MANAGED_STAGING_REDEPLOY_PREP"
    assert bundle["gate_state"] == "ready_for_managed_staging_redeploy_preparation"
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_post_walkthrough_staging_readiness_recheck_handoff()
    assert "Owner walkthrough is accepted." in handoff["next_builder_notes"]
    assert "Staging readiness is still false." in handoff["next_builder_notes"]
    assert "Next build is GP036 Managed Staging Redeploy Preparation." in handoff["next_builder_notes"]
