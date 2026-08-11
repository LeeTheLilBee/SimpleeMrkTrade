from ob_owner_experience.tower_ob_staging_acceptance_handoff import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_staging_acceptance_handoff_bundle,
    build_tower_ob_staging_acceptance_handoff_handoff,
    build_tower_ob_staging_acceptance_handoff_packet,
    build_tower_ob_staging_acceptance_handoff_status,
)


def test_gp051_handoff_packet():
    packet = build_tower_ob_staging_acceptance_handoff_packet()
    assert packet["gp050_staging_closeout_ready"] is True
    assert packet["staging_ready"] is True
    assert packet["staging_acceptance_handoff_ready"] is True
    assert packet["tower_acceptance_required"] is True
    assert packet["evidence_packet_required"] is True
    assert len(packet["handoff_evidence_refs"]) == 5
    assert packet["private_beta_access_opened"] is False
    assert packet["tester_credentials_issued"] is False
    assert packet["production_deploy_enabled"] is False


def test_gp051_status_bundle_handoff():
    status = build_tower_ob_staging_acceptance_handoff_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_staging_acceptance_handoff_bundle()
    assert bundle["package"] == "ob_tower_ob_staging_acceptance_handoff_gp051"
    assert bundle["staging_acceptance_handoff_ready"] is True
    assert bundle["source_dependency"] == "GP050"
    assert bundle["recommendation"] == "GO_FOR_TOWER_OB_STAGING_ACCEPTANCE_REVIEW_PACKET"
    assert bundle["release_boundary"]["staging_ready"] is True
    assert bundle["release_boundary"]["private_beta_access_opened"] is False
    assert bundle["release_boundary"]["tester_credentials_issued"] is False

    handoff = build_tower_ob_staging_acceptance_handoff_handoff()
    assert "Private beta access is not opened." in handoff["next_builder_notes"]
    assert "Tester credentials are not issued." in handoff["next_builder_notes"]
