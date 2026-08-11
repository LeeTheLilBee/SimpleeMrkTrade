from ob_owner_experience.owner_beta_readiness_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_beta_readiness_gate_bundle,
    build_owner_beta_readiness_gate_handoff,
    build_owner_beta_readiness_record,
    build_owner_beta_readiness_status,
)


def test_gp048_beta_readiness_record():
    record = build_owner_beta_readiness_record()
    assert record["gp047_staging_ready_evidence_sealed"] is True
    assert record["staging_ready"] is True
    assert record["owner_beta_readiness_ready"] is True
    assert record["survey_mode_allowed"] is True
    assert record["paper_mode_allowed"] is True
    assert record["manual_live_owner_only"] is True
    assert record["private_beta_access_opened"] is False
    assert record["public_beta_open"] is False
    assert record["broker_submission_enabled"] is False
    assert record["real_capital_movement_enabled"] is False
    assert record["live_auto_locked"] is True


def test_gp048_status_bundle_handoff():
    status = build_owner_beta_readiness_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_owner_beta_readiness_gate_bundle()
    assert bundle["package"] == "ob_owner_beta_readiness_gate_gp048"
    assert bundle["owner_beta_readiness_ready"] is True
    assert bundle["source_dependency"] == "GP047"
    assert bundle["gate_state"] == "owner_beta_ready_access_still_closed"
    assert bundle["release_boundary"]["private_beta_access_opened"] is False
    assert bundle["release_boundary"]["staging_ready"] is True
    assert "PUBLIC_BETA_OPEN" in bundle["must_not_claim"]

    handoff = build_owner_beta_readiness_gate_handoff()
    assert "Private beta access is still closed." in handoff["next_builder_notes"]
    assert "Live Auto remains locked." in handoff["next_builder_notes"]
