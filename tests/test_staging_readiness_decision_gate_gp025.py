from ob_owner_experience.staging_readiness_decision_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_staging_readiness_decision_gate_bundle,
    build_staging_readiness_decision_gate_handoff,
    build_staging_readiness_decision_gate_status,
    build_staging_readiness_decision_record,
)


def test_gp025_decision_record_is_no_go_hold():
    record = build_staging_readiness_decision_record()
    assert record["recommendation"] == "NO_GO_HOLD"
    assert record["staging_ready"] is False
    assert record["staging_readiness_granted"] is False
    assert record["actual_tower_route_work_required"] is True
    assert record["render_redeploy_required_later"] is True
    assert record["owner_controlled_walkthrough_required_later"] is True


def test_gp025_status_safety_locked():
    status = build_staging_readiness_decision_gate_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp025_bundle_and_handoff():
    bundle = build_staging_readiness_decision_gate_bundle()
    assert bundle["package"] == "ob_staging_readiness_decision_gate_gp025"
    assert bundle["decision"] == "NO_GO_HOLD_STAGING_READY_NOT_CLAIMED_PENDING_ACTUAL_TOWER_ROUTE_WORK"
    assert bundle["decision_gate_ready"] is True
    assert bundle["recommendation"] == "NO_GO_HOLD"
    assert bundle["gate_state"] == "closed_pending_actual_tower_route_work"
    assert bundle["release_boundary"]["staging_ready"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_staging_readiness_decision_gate_handoff()
    assert "Decision is NO_GO_HOLD for staging readiness." in handoff["next_builder_notes"]
    assert "Proceed next to actual Tower OB route implementation and return repair." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
