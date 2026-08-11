from ob_owner_experience.integrated_controlled_route_check_execution import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_integrated_controlled_route_check_execution_bundle,
    build_integrated_controlled_route_check_execution_handoff,
    build_integrated_controlled_route_check_execution_status,
    build_integrated_controlled_route_check_results,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp029_controlled_route_results_all_six():
    results = build_integrated_controlled_route_check_results()
    assert len(results) == 6
    assert [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in results:
        assert item["route_resolved"] is True
        assert item["return_resolved"] is True
        assert item["dangerous_actions_locked"] is True
        assert item["controlled_route_check_executed"] is True
        assert item["controlled_route_check_passed"] is True
        assert item["live_route_verified"] is False
        assert item["owner_walkthrough_started"] is False


def test_gp029_status_bundle_handoff():
    status = build_integrated_controlled_route_check_execution_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_integrated_controlled_route_check_execution_bundle()
    assert bundle["package"] == "ob_integrated_controlled_route_check_execution_gp029"
    assert bundle["controlled_route_check_executed"] is True
    assert bundle["source_dependency"] == "GP028"
    assert bundle["release_boundary"]["controlled_route_check_executed"] is True
    assert bundle["release_boundary"]["owner_walkthrough_started"] is False
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_integrated_controlled_route_check_execution_handoff()
    assert "Owner walkthrough has not started." in handoff["next_builder_notes"]
