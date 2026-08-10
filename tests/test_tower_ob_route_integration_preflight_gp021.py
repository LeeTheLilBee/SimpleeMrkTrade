from ob_owner_experience.tower_ob_route_integration_preflight import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_route_integration_preflight_bundle,
    build_tower_ob_route_integration_preflight_handoff,
    build_tower_ob_route_integration_preflight_matrix,
    build_tower_ob_route_integration_preflight_status,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp021_matrix_has_all_routes_without_mutation():
    matrix = build_tower_ob_route_integration_preflight_matrix()
    assert len(matrix) == 6
    assert [item["room"] for item in matrix] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    for item in matrix:
        assert item["route_contract_ready"] is True
        assert item["tower_entry_route_hint"] == "/tower/access/observatory"
        assert item["tower_return_route_hint"] == "/tower/access-home"
        assert item["tower_route_modified"] is False
        assert item["ob_route_modified"] is False
        assert item["live_route_opened"] is False


def test_gp021_status_and_bundle_locked():
    status = build_tower_ob_route_integration_preflight_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_route_integration_preflight_bundle()
    assert bundle["package"] == "ob_tower_ob_route_integration_preflight_gp021"
    assert bundle["preflight_ready"] is True
    assert bundle["source_dependency"] == "GP020"
    assert bundle["release_boundary"]["staging_ready"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]


def test_gp021_handoff_notes():
    handoff = build_tower_ob_route_integration_preflight_handoff()
    assert handoff["preflight_ready"] is True
    assert "Do not modify Tower routes from this package." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
