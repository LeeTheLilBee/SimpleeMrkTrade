from ob_owner_experience.hosted_return_session_continuity_verification import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_hosted_return_session_continuity_results,
    build_hosted_return_session_continuity_verification_bundle,
    build_hosted_return_session_continuity_verification_handoff,
    build_hosted_return_session_continuity_verification_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp043_return_results_all_six():
    results = build_hosted_return_session_continuity_results()
    assert len(results) == 6
    assert [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in results:
        assert item["tower_return_route"] == "/tower/access-home"
        assert item["return_control_visible"] is True
        assert item["owner_session_reference_present"] is True
        assert item["session_continuity_preserved"] is True
        assert item["hosted_return_check_executed"] is True
        assert item["hosted_return_check_passed"] is True
        assert item["staging_ready_claim_allowed_now"] is False


def test_gp043_status_bundle_handoff():
    status = build_hosted_return_session_continuity_verification_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_hosted_return_session_continuity_verification_bundle()
    assert bundle["package"] == "ob_hosted_return_session_continuity_verification_gp043"
    assert bundle["return_session_continuity_verified"] is True
    assert bundle["source_dependency"] == "GP042"
    assert bundle["release_boundary"]["return_session_continuity_verified"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_hosted_return_session_continuity_verification_handoff()
    assert "Hosted return session continuity is verified in the controlled evidence lane." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
