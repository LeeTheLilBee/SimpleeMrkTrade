from ob_owner_experience.integrated_owner_walkthrough_controlled_route_check import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_integrated_owner_walkthrough_controlled_route_check,
    build_integrated_owner_walkthrough_controlled_route_check_bundle,
    build_integrated_owner_walkthrough_controlled_route_check_handoff,
    build_integrated_owner_walkthrough_controlled_route_check_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp024_check_all_rooms_not_executed():
    check = build_integrated_owner_walkthrough_controlled_route_check()
    assert len(check) == 6
    assert [item["room"] for item in check] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in check:
        assert item["check_required"] is True
        assert item["check_executed"] is False
        assert item["live_route_opened"] is False
        assert item["tower_return_repaired"] is False
        assert item["owner_walkthrough_started"] is False
        assert item["owner_walkthrough_accepted"] is False


def test_gp024_status_bundle_handoff():
    status = build_integrated_owner_walkthrough_controlled_route_check_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_integrated_owner_walkthrough_controlled_route_check_bundle()
    assert bundle["package"] == "ob_integrated_owner_walkthrough_controlled_route_check_gp024"
    assert bundle["controlled_route_check_ready"] is True
    assert bundle["source_dependency"] == "GP023"
    assert bundle["release_boundary"]["controlled_route_check_executed"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_integrated_owner_walkthrough_controlled_route_check_handoff()
    assert "Do not execute the controlled route check from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
