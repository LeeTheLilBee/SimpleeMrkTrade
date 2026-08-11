from ob_owner_experience.managed_staging_redeploy_authorization_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_managed_staging_redeploy_authorization_gate_bundle,
    build_managed_staging_redeploy_authorization_gate_handoff,
    build_managed_staging_redeploy_authorization_record,
    build_managed_staging_redeploy_authorization_status,
)


def test_gp038_authorization_record():
    record = build_managed_staging_redeploy_authorization_record()
    assert record["gp037_build_configuration_verified"] is True
    assert record["owner_authorization_recorded"] is True
    assert record["authorized_for_receipt_package"] is True
    assert record["external_render_api_call_allowed_in_this_package"] is False
    assert record["receipt_only_boundary_required"] is True
    assert record["hosted_runtime_verification_required_after_receipt"] is True
    assert record["production_deploy_enabled"] is False
    assert record["staging_ready"] is False


def test_gp038_status_bundle_handoff():
    status = build_managed_staging_redeploy_authorization_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_managed_staging_redeploy_authorization_gate_bundle()
    assert bundle["package"] == "ob_managed_staging_redeploy_authorization_gate_gp038"
    assert bundle["redeploy_authorization_ready"] is True
    assert bundle["source_dependency"] == "GP037"
    assert bundle["recommendation"] == "GO_FOR_MANAGED_STAGING_REDEPLOY_EXECUTION_RECEIPT"
    assert bundle["release_boundary"]["render_api_called"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_managed_staging_redeploy_authorization_gate_handoff()
    assert "This authorization is for the next receipt package only." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
