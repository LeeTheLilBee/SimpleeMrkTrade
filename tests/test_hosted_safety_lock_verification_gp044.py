from ob_owner_experience.hosted_safety_lock_verification import (
    FALSE_FLAGS,
    SAFETY_LOCKS,
    TRUE_FLAGS,
    build_hosted_safety_lock_verification_bundle,
    build_hosted_safety_lock_verification_handoff,
    build_hosted_safety_lock_verification_results,
    build_hosted_safety_lock_verification_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp044_safety_results_all_six():
    results = build_hosted_safety_lock_verification_results()
    assert len(results) == 6
    assert [item["room"] for item in results] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in results:
        assert item["locks_checked"] == list(SAFETY_LOCKS)
        assert item["broker_submission_enabled"] is False
        assert item["real_capital_movement_enabled"] is False
        assert item["direct_execution_enabled"] is False
        assert item["automated_execution_enabled"] is False
        assert item["permission_mutation_enabled"] is False
        assert item["secret_reveal_enabled"] is False
        assert item["live_auto_locked"] is True
        assert item["hosted_safety_locks_verified"] is True
        assert item["staging_ready_claim_allowed_now"] is False


def test_gp044_status_bundle_handoff():
    status = build_hosted_safety_lock_verification_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_hosted_safety_lock_verification_bundle()
    assert bundle["package"] == "ob_hosted_safety_lock_verification_gp044"
    assert bundle["hosted_safety_locks_verified"] is True
    assert bundle["source_dependency"] == "GP043"
    assert bundle["release_boundary"]["hosted_safety_locks_verified"] is True
    assert bundle["release_boundary"]["staging_ready"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_hosted_safety_lock_verification_handoff()
    assert "Hosted safety locks are verified in the controlled evidence lane." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
