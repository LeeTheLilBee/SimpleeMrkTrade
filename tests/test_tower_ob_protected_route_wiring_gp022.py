from ob_owner_experience.tower_ob_protected_route_wiring import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_protected_route_wiring_bundle,
    build_tower_ob_protected_route_wiring_contract,
    build_tower_ob_protected_route_wiring_handoff,
    build_tower_ob_protected_route_wiring_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp022_contract_all_rooms_default_deny():
    contract = build_tower_ob_protected_route_wiring_contract()
    assert len(contract) == 6
    assert [item["room"] for item in contract] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in contract:
        assert item["default_deny_required"] is True
        assert item["tower_handoff_required"] is True
        assert item["owner_session_required"] is True
        assert item["anonymous_access_allowed"] is False
        assert item["broker_submission_allowed"] is False
        assert item["money_movement_allowed"] is False
        assert item["live_auto_allowed"] is False
        assert item["actual_route_code_changed"] is False
        assert item["protected_route_wired_live"] is False


def test_gp022_status_bundle_handoff():
    status = build_tower_ob_protected_route_wiring_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_protected_route_wiring_bundle()
    assert bundle["package"] == "ob_tower_ob_protected_route_wiring_gp022"
    assert bundle["wiring_contract_ready"] is True
    assert bundle["source_dependency"] == "GP021"
    assert bundle["release_boundary"]["protected_route_wired_live"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_tower_ob_protected_route_wiring_handoff()
    assert "Do not mutate actual route code from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
