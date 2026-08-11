from ob_owner_experience.tower_ob_hosted_route_verification import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_hosted_route_verification_bundle,
    build_tower_ob_hosted_route_verification_handoff,
    build_tower_ob_hosted_route_verification_results,
    build_tower_ob_hosted_route_verification_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp042_route_results_all_six():
    results = build_tower_ob_hosted_route_verification_results()
    assert len(results) == 6
    assert [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in results:
        assert item["tower_handoff_required"] is True
        assert item["owner_session_required"] is True
        assert item["hosted_route_check_executed"] is True
        assert item["hosted_route_check_passed"] is True
        assert item["hosted_live_route_verified"] is True
        assert item["dangerous_actions_locked"] is True
        assert item["staging_ready_claim_allowed_now"] is False


def test_gp042_status_bundle_handoff():
    status = build_tower_ob_hosted_route_verification_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_hosted_route_verification_bundle()
    assert bundle["package"] == "ob_tower_ob_hosted_route_verification_gp042"
    assert bundle["hosted_route_verification_ready"] is True
    assert bundle["source_dependency"] == "GP041"
    assert bundle["release_boundary"]["hosted_live_route_verified"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_tower_ob_hosted_route_verification_handoff()
    assert "All six OB hosted routes are verified in the controlled evidence lane." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
