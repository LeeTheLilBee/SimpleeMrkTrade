from ob_owner_experience.private_beta_access_hold_boundary import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_private_beta_access_hold_boundary_bundle,
    build_private_beta_access_hold_boundary_handoff,
    build_private_beta_access_hold_record,
    build_private_beta_access_hold_status,
)


def test_gp049_access_hold_record():
    record = build_private_beta_access_hold_record()
    assert record["gp048_owner_beta_readiness_ready"] is True
    assert record["staging_ready"] is True
    assert record["private_beta_access_hold_ready"] is True
    assert record["owner_approval_required_to_open_beta"] is True
    assert record["tester_survey_paper_only_boundary_ready"] is True
    assert record["manual_live_owner_only"] is True
    assert record["private_beta_access_opened"] is False
    assert record["public_beta_open"] is False
    assert record["tester_credentials_issued"] is False
    assert record["live_auto_locked"] is True


def test_gp049_status_bundle_handoff():
    status = build_private_beta_access_hold_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_private_beta_access_hold_boundary_bundle()
    assert bundle["package"] == "ob_private_beta_access_hold_boundary_gp049"
    assert bundle["private_beta_access_hold_ready"] is True
    assert bundle["source_dependency"] == "GP048"
    assert bundle["gate_state"] == "private_beta_ready_but_access_held_for_owner_approval"
    assert bundle["release_boundary"]["private_beta_access_opened"] is False
    assert bundle["release_boundary"]["staging_ready"] is True
    assert "TESTER_ACCESS_OPEN" in bundle["must_not_claim"]

    handoff = build_private_beta_access_hold_boundary_handoff()
    assert "Tester access is not open." in handoff["next_builder_notes"]
    assert "Live Auto remains locked." in handoff["next_builder_notes"]
