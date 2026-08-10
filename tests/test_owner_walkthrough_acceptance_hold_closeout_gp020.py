from ob_owner_experience.owner_walkthrough_acceptance_hold_closeout import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_walkthrough_acceptance_hold,
    build_owner_walkthrough_acceptance_hold_closeout_bundle,
    build_owner_walkthrough_acceptance_hold_closeout_handoff,
    build_owner_walkthrough_acceptance_hold_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp020_acceptance_hold_records_all_six():
    hold = build_owner_walkthrough_acceptance_hold()
    assert hold["acceptance_hold_recorded"] is True
    assert hold["acceptance_allowed_now"] is False
    assert hold["owner_walkthrough_accepted"] is False
    assert hold["walkthrough_prep_lane_closed"] is True
    assert hold["integration_handoff_ready"] is True
    assert hold["room_order"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert len(hold["room_scope"]) == 6


def test_gp020_status_locked_and_ready_for_integration():
    status = build_owner_walkthrough_acceptance_hold_status()
    assert status["gp019_capture_plan_prepared"] is True
    assert status["acceptance_hold_recorded"] is True
    assert status["walkthrough_prep_lane_closed"] is True
    assert status["integration_handoff_ready"] is True
    assert status["all_six_rooms_present"] is True
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp020_bundle_and_handoff():
    bundle = build_owner_walkthrough_acceptance_hold_closeout_bundle()
    assert bundle["package"] == "ob_owner_walkthrough_acceptance_hold_closeout_gp020"
    assert bundle["closeout_ready"] is True
    assert bundle["source_dependency"] == "GP019"
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is False
    assert bundle["release_boundary"]["tower_return_repaired"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]
    assert bundle["next_build"] == "Tower OB route integration preflight / GP021"

    handoff = build_owner_walkthrough_acceptance_hold_closeout_handoff()
    assert handoff["closeout_ready"] is True
    assert "Proceed next to Tower OB route integration preflight." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
