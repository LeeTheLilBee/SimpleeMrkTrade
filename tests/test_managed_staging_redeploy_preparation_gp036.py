from ob_owner_experience.managed_staging_redeploy_preparation import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    STAGING_BRANCH,
    STAGING_ENTRYPOINT,
    STAGING_REGION,
    STAGING_SERVICE,
    build_managed_staging_redeploy_plan,
    build_managed_staging_redeploy_preparation_bundle,
    build_managed_staging_redeploy_preparation_handoff,
    build_managed_staging_redeploy_preparation_status,
)


def test_gp036_redeploy_plan_declared_not_executed():
    plan = build_managed_staging_redeploy_plan()
    assert plan["service"] == STAGING_SERVICE
    assert plan["region"] == STAGING_REGION
    assert plan["entrypoint"] == STAGING_ENTRYPOINT
    assert plan["branch"] == STAGING_BRANCH
    assert plan["owner_walkthrough_accepted"] is True
    assert plan["redeploy_preparation_ready"] is True
    assert plan["commit_pin_required"] is True
    assert plan["secret_alias_only_required"] is True
    assert plan["render_api_call_allowed_now"] is False
    assert plan["render_redeployed"] is False
    assert plan["staging_ready"] is False


def test_gp036_status_bundle_handoff():
    status = build_managed_staging_redeploy_preparation_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_managed_staging_redeploy_preparation_bundle()
    assert bundle["package"] == "ob_managed_staging_redeploy_preparation_gp036"
    assert bundle["redeploy_preparation_ready"] is True
    assert bundle["source_dependency"] == "GP035"
    assert bundle["recommendation"] == "GO_FOR_BUILD_CONFIGURATION_VERIFICATION"
    assert bundle["release_boundary"]["render_redeployed"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_managed_staging_redeploy_preparation_handoff()
    assert "Do not call Render API from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
