from ob_owner_experience.controlled_walkthrough_run_window_preparation import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_controlled_walkthrough_run_window_plan,
    build_controlled_walkthrough_run_window_preparation_bundle,
    build_controlled_walkthrough_run_window_preparation_handoff,
    build_controlled_walkthrough_run_window_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp017_window_plan_prepared_not_open():
    plan = build_controlled_walkthrough_run_window_plan()
    assert plan["window_template_prepared"] is True
    assert plan["window_active"] is False
    assert plan["window_open"] is False
    assert plan["bounded_window_required"] is True
    assert plan["room_order"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert len(plan["room_scope"]) == 6


def test_gp017_status_locked():
    status = build_controlled_walkthrough_run_window_status()
    assert status["gp016_receipt_gate_prepared"] is True
    assert status["window_template_prepared"] is True
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp017_bundle_and_handoff():
    bundle = build_controlled_walkthrough_run_window_preparation_bundle()
    assert bundle["package"] == "ob_controlled_walkthrough_run_window_preparation_gp017"
    assert bundle["window_prepared"] is True
    assert bundle["source_dependency"] == "GP016"
    assert bundle["release_boundary"]["window_open"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_controlled_walkthrough_run_window_preparation_handoff()
    assert "Do not open the run window." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
