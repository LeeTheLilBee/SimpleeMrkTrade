from ob_owner_experience.tower_ob_return_session_runtime_verification import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_return_session_runtime_results,
    build_tower_ob_return_session_runtime_verification_bundle,
    build_tower_ob_return_session_runtime_verification_handoff,
    build_tower_ob_return_session_runtime_verification_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp028_return_results_all_six():
    results = build_tower_ob_return_session_runtime_results()
    assert len(results) == 6
    assert [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in results:
        assert item["default_deny_passed"] is True
        assert item["session_reference_required_passed"] is True
        assert item["authorized_return_passed"] is True
        assert item["return_session_verified"] is True
        assert item["live_route_verified"] is False
        assert item["staging_ready"] is False


def test_gp028_status_bundle_handoff():
    status = build_tower_ob_return_session_runtime_verification_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_return_session_runtime_verification_bundle()
    assert bundle["package"] == "ob_tower_ob_return_session_runtime_verification_gp028"
    assert bundle["return_session_verified"] is True
    assert bundle["source_dependency"] == "GP027"
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_tower_ob_return_session_runtime_verification_handoff()
    assert "Do not start the owner walkthrough." in handoff["next_builder_notes"]
