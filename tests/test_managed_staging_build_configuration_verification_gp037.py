from ob_owner_experience.managed_staging_build_configuration_verification import (
    FALSE_FLAGS,
    REQUIRED_SECRET_ALIASES,
    TRUE_FLAGS,
    build_managed_staging_build_configuration_record,
    build_managed_staging_build_configuration_status,
    build_managed_staging_build_configuration_verification_bundle,
    build_managed_staging_build_configuration_verification_handoff,
)


def test_gp037_configuration_record():
    record = build_managed_staging_build_configuration_record()
    assert record["build_configuration_verified"] is True
    assert record["entrypoint_verified"] is True
    assert record["branch_verified"] is True
    assert record["secret_aliases_verified"] is True
    assert record["secret_aliases"] == list(REQUIRED_SECRET_ALIASES)
    assert record["secret_values_present"] is False
    assert record["render_api_called"] is False
    assert record["render_redeployed"] is False
    assert record["staging_ready"] is False


def test_gp037_status_bundle_handoff():
    status = build_managed_staging_build_configuration_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_managed_staging_build_configuration_verification_bundle()
    assert bundle["package"] == "ob_managed_staging_build_configuration_verification_gp037"
    assert bundle["build_configuration_verified"] is True
    assert bundle["source_dependency"] == "GP036"
    assert bundle["recommendation"] == "GO_FOR_MANAGED_STAGING_REDEPLOY_AUTHORIZATION_GATE"
    assert bundle["release_boundary"]["secret_values_present"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_managed_staging_build_configuration_verification_handoff()
    assert "Only secret aliases are present." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
