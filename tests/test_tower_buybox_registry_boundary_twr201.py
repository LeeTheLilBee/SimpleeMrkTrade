"""TWR201 — BuyBox registration is descriptive, not access authorization."""

from tower.app_registry import (
    app_ids,
    registered_apps,
    registered_routes,
    route_by_path,
)
from tower.app_truth_projection import (
    app_truth_by_id,
    verified_launchable_app_ids,
)


def test_buybox_registered_once_without_hosted_access():
    registered = [entry for entry in registered_apps() if entry["app_id"] == "buybox"]
    assert len(registered) == 1
    app = registered[0]
    assert app["app_status"] == "registered_future_room"
    assert app["tower_launch_route"] == "/tower/app-registry"
    assert app["primary_room_route"] == "/buybox"
    assert app["owner_only"] is True
    assert app["requires_tower_handoff"] is True
    assert app["dangerous_actions_locked"] is True
    assert app["broker_execution_enabled"] is False
    assert app["capital_action_enabled"] is False
    assert app_ids().count("buybox") == 1


def test_buybox_registry_does_not_mint_launch_route_or_entitlement():
    assert route_by_path("/tower/launch/buybox") is None
    assert route_by_path("/buybox") is None
    assert not any(route["app_id"] == "buybox" for route in registered_routes())
    truth = app_truth_by_id("buybox")
    assert truth is not None
    assert truth["registry_status"] == "registered_future_room"
    assert truth["launchable"] is False
    assert truth["request_authorization_required"] is True
    assert truth["owner_session_gate_bypassed"] is False
    assert truth["step_up_gate_bypassed"] is False
    assert "buybox" not in verified_launchable_app_ids()


def test_existing_apps_and_owner_only_future_rooms_unchanged():
    registered = {entry["app_id"]: entry for entry in registered_apps()}
    assert {"observatory", "teller", "vault", "clouds", "grounds", "buybox"} <= set(registered)
    assert registered["observatory"]["tower_launch_route"] == "/tower/launch/observatory"
    assert registered["teller"]["tower_launch_route"] == "/tower/launch/teller"
    for name in ("vault", "clouds", "grounds", "buybox"):
        assert registered[name]["app_status"] == "registered_future_room"
