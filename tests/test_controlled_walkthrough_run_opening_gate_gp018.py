from ob_owner_experience.controlled_walkthrough_run_opening_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_controlled_walkthrough_run_opening_gate_bundle,
    build_controlled_walkthrough_run_opening_gate_handoff,
    build_controlled_walkthrough_run_opening_gate_status,
    build_controlled_walkthrough_run_opening_requirements,
)


def test_gp018_requirements_registered():
    reqs = build_controlled_walkthrough_run_opening_requirements()
    assert len(reqs) == 6
    assert reqs[0]["key"] == "gp017_window_prepared"
    assert reqs[0]["satisfied_now"] is True
    for item in reqs[1:]:
        assert item["satisfied_now"] is False


def test_gp018_status_locked():
    status = build_controlled_walkthrough_run_opening_gate_status()
    assert status["gp017_window_prepared"] is True
    assert status["opening_gate_closed"] is True
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp018_bundle_and_handoff():
    bundle = build_controlled_walkthrough_run_opening_gate_bundle()
    assert bundle["package"] == "ob_controlled_walkthrough_run_opening_gate_gp018"
    assert bundle["opening_gate_prepared"] is True
    assert bundle["gate_state"] == "closed_pending_future_owner_authorization_and_step_up"
    assert bundle["release_boundary"]["opening_gate_open"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_controlled_walkthrough_run_opening_gate_handoff()
    assert "Do not open the opening gate." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
