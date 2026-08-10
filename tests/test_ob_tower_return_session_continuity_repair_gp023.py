from ob_owner_experience.ob_tower_return_session_continuity_repair import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_ob_tower_return_session_continuity_contract,
    build_ob_tower_return_session_continuity_repair_bundle,
    build_ob_tower_return_session_continuity_repair_handoff,
    build_ob_tower_return_session_continuity_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp023_contract_all_rooms_return_required_not_repaired_live():
    contract = build_ob_tower_return_session_continuity_contract()
    assert len(contract) == 6
    assert [item["room"] for item in contract] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in contract:
        assert item["return_control_required"] is True
        assert item["tower_session_reference_required"] is True
        assert item["session_continuity_check_required"] is True
        assert item["owner_session_required"] is True
        assert item["actual_tower_return_code_changed"] is False
        assert item["tower_return_repaired"] is False
        assert item["session_continuity_repaired_live"] is False


def test_gp023_status_bundle_handoff():
    status = build_ob_tower_return_session_continuity_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_ob_tower_return_session_continuity_repair_bundle()
    assert bundle["package"] == "ob_tower_return_session_continuity_repair_gp023"
    assert bundle["return_repair_contract_ready"] is True
    assert bundle["source_dependency"] == "GP022"
    assert bundle["release_boundary"]["tower_return_repaired"] is False
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_ob_tower_return_session_continuity_repair_handoff()
    assert "Do not claim actual Tower return repaired from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
