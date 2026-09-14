from tower.app_registry import (
    registered_apps,
    route_by_path,
)


def test_twr186_teller_owner_corridor_is_now_activated_by_twr190():
    route = route_by_path(
        "/tower/launch/teller"
    )

    assert route is not None
    assert route["route_id"] == "teller_owner_launch"
    assert route["app_id"] == "teller"
    assert route["owner_only"] is True
    assert route["requires_owner_session"] is True
    assert route["requires_step_up"] is True
    assert route["default_denied_when_unknown"] is True
    assert route["temporary_placeholder"] is False
    assert route["lock_state"] == "protected_owner_handoff"


def test_twr186_security_invariants_survive_activation():
    teller = next(
        item
        for item in registered_apps()
        if item["app_id"] == "teller"
    )

    assert teller["app_status"] == "protected_hosted"
    assert teller["tower_launch_route"] == "/tower/launch/teller"
    assert teller["primary_room_route"] == "/teller"

    # Teller stays multi-role as a product.
    assert teller["owner_only"] is False

    assert teller["requires_tower_handoff"] is True
    assert teller["dangerous_actions_locked"] is True
    assert teller["live_auto_locked"] is True
    assert teller["broker_execution_enabled"] is False
    assert teller["capital_action_enabled"] is False
