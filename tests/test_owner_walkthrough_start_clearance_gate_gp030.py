from ob_owner_experience.owner_walkthrough_start_clearance_gate import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_owner_walkthrough_start_clearance_gate_bundle,
    build_owner_walkthrough_start_clearance_gate_handoff,
    build_owner_walkthrough_start_clearance_record,
    build_owner_walkthrough_start_clearance_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp030_clearance_record_go_but_not_started():
    record = build_owner_walkthrough_start_clearance_record()
    assert record["recommendation"] == "GO_FOR_CONTROLLED_OWNER_WALKTHROUGH_START"
    assert record["gp029_controlled_route_check_executed"] is True
    assert record["rooms_cleared"] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert record["walkthrough_start_clearance_ready"] is True
    assert record["owner_action_required_to_start"] is True
    assert record["owner_walkthrough_started"] is False
    assert record["owner_walkthrough_accepted"] is False
    assert record["staging_ready"] is False


def test_gp030_status_locked_until_owner_start():
    status = build_owner_walkthrough_start_clearance_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True


def test_gp030_bundle_and_handoff():
    bundle = build_owner_walkthrough_start_clearance_gate_bundle()
    assert bundle["package"] == "ob_owner_walkthrough_start_clearance_gate_gp030"
    assert bundle["walkthrough_start_clearance_ready"] is True
    assert bundle["recommendation"] == "GO_FOR_CONTROLLED_OWNER_WALKTHROUGH_START"
    assert bundle["gate_state"] == "ready_for_explicit_owner_controlled_walkthrough_start"
    assert bundle["release_boundary"]["owner_walkthrough_started"] is False
    assert bundle["release_boundary"]["owner_walkthrough_accepted"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_owner_walkthrough_start_clearance_gate_handoff()
    assert handoff["walkthrough_start_clearance_ready"] is True
    assert "Owner action is required to start the walkthrough." in handoff["next_builder_notes"]
    assert "This package does not start the walkthrough." in handoff["next_builder_notes"]
    assert "Next build is GP031 Owner Walkthrough Controlled Start." in handoff["next_builder_notes"]
