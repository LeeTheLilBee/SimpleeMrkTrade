from ob_owner_experience.tower_ob_actual_route_implementation_return_repair import (
    FALSE_FLAGS,
    TRUE_FLAGS,
    build_tower_ob_actual_route_implementation_bundle,
    build_tower_ob_actual_route_implementation_handoff,
    build_tower_ob_actual_route_implementation_status,
    build_tower_ob_return_session_continuity_repair_adapter,
    build_tower_ob_route_implementation_table,
    resolve_ob_to_tower_return,
    resolve_tower_ob_route,
)
from ob_owner_experience.six_room_real_surface_acceptance import SIX_ROOM_REAL_SURFACE_ORDER


def test_gp026_route_table_and_return_adapter():
    table = build_tower_ob_route_implementation_table()
    ret = build_tower_ob_return_session_continuity_repair_adapter()

    assert len(table) == 6
    assert len(ret) == 6
    assert [item["room"] for item in table] == list(SIX_ROOM_REAL_SURFACE_ORDER)
    assert [item["room"] for item in ret] == list(SIX_ROOM_REAL_SURFACE_ORDER)

    for item in table:
        assert item["implementation_adapter_ready"] is True
        assert item["anonymous_access_allowed"] is False
        assert item["live_route_verified"] is False
        assert item["tower_entry_route"] == "/tower/access/observatory"
        assert item["tower_return_route"] == "/tower/access-home"

    for item in ret:
        assert item["repair_adapter_ready"] is True
        assert item["return_control_destination"] == "/tower/access-home"
        assert item["actual_runtime_return_verified"] is False
        assert item["staging_ready"] is False


def test_gp026_resolvers_default_deny_then_resolve_for_owner_session():
    denied = resolve_tower_ob_route("dashboard")
    assert denied["resolved"] is False
    assert denied["reason"] == "owner_session_required"

    no_handoff = resolve_tower_ob_route("dashboard", owner_session_active=True)
    assert no_handoff["resolved"] is False
    assert no_handoff["reason"] == "tower_handoff_required"

    resolved = resolve_tower_ob_route("dashboard", True, True)
    assert resolved["resolved"] is True
    assert resolved["ob_route_hint"] == "/ob/dashboard"
    assert resolved["staging_ready"] is False

    return_denied = resolve_ob_to_tower_return("dashboard")
    assert return_denied["return_ready"] is False

    return_ready = resolve_ob_to_tower_return("dashboard", True, True)
    assert return_ready["return_ready"] is True
    assert return_ready["tower_return_route"] == "/tower/access-home"
    assert return_ready["staging_ready"] is False


def test_gp026_status_bundle_and_handoff():
    status = build_tower_ob_actual_route_implementation_status()
    for key in FALSE_FLAGS:
        assert status[key] is False
    for key in TRUE_FLAGS:
        assert status[key] is True

    bundle = build_tower_ob_actual_route_implementation_bundle()
    assert bundle["package"] == "ob_tower_ob_actual_route_implementation_return_repair_gp026"
    assert bundle["implementation_ready"] is True
    assert bundle["source_dependency"] == "GP025"
    assert bundle["release_boundary"]["staging_ready"] is False
    assert bundle["release_boundary"]["live_auto_locked"] is True
    assert "STAGING_READY" in bundle["must_not_claim"]

    handoff = build_tower_ob_actual_route_implementation_handoff()
    assert handoff["implementation_ready"] is True
    assert "Do not start the owner walkthrough from this package." in handoff["next_builder_notes"]
