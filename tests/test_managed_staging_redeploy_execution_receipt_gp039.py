from ob_owner_experience.managed_staging_redeploy_execution_receipt import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_managed_staging_redeploy_execution_receipt,
    build_managed_staging_redeploy_execution_receipt_bundle,
    build_managed_staging_redeploy_execution_receipt_handoff,
    build_managed_staging_redeploy_execution_receipt_status,
)


def test_gp039_execution_receipt_recorded_not_staging_ready():
    receipt = build_managed_staging_redeploy_execution_receipt()
    assert receipt["gp038_redeploy_authorization_ready"] is True
    assert receipt["redeploy_execution_receipt_recorded"] is True
    assert receipt["receipt_append_only"] is True
    assert receipt["external_render_api_called"] is False
    assert receipt["render_redeploy_receipt_recorded"] is True
    assert receipt["hosted_runtime_verification_required"] is True
    assert receipt["hosted_runtime_verified"] is False
    assert receipt["hosted_live_route_verified"] is False
    assert receipt["production_deploy_enabled"] is False
    assert receipt["staging_ready"] is False


def test_gp039_status_bundle_handoff():
    status = build_managed_staging_redeploy_execution_receipt_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_managed_staging_redeploy_execution_receipt_bundle()
    assert bundle["package"] == "ob_managed_staging_redeploy_execution_receipt_gp039"
    assert bundle["redeploy_execution_receipt_recorded"] is True
    assert bundle["source_dependency"] == "GP038"
    assert bundle["recommendation"] == "GO_FOR_HOSTED_RUNTIME_VERIFICATION_GATE"
    assert bundle["release_boundary"]["hosted_runtime_verified"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_managed_staging_redeploy_execution_receipt_handoff()
    assert "Hosted runtime verification is still required." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
