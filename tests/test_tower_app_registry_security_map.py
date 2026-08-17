from tower.app_registry import (
    owner_only_routes,
    protected_ob_routes,
    registered_apps,
    registered_routes,
    step_up_routes,
    temporary_placeholder_routes,
)
from tower.security_map_service import (
    build_tower_security_map,
    security_map_status_cards,
)


def test_registry_contains_current_ob_route_coverage():
    routes = protected_ob_routes()

    assert "/ob/dashboard" in routes
    assert "/ob/market-map" in routes
    assert "/ob/symbol/<symbol>" in routes
    assert "/ob/trade-center" in routes
    assert "/ob/review-center" in routes
    assert "/ob/owner-console" in routes
    assert "/ob/owner-dashboard" in routes


def test_owner_only_routes_are_declared():
    routes = owner_only_routes()

    assert "/ob/owner-console" in routes
    assert "/ob/owner-dashboard" in routes


def test_normal_ob_routes_require_step_up():
    routes = step_up_routes()

    assert "/ob/dashboard" in routes
    assert "/ob/market-map" in routes
    assert "/ob/symbol/<symbol>" in routes
    assert "/ob/trade-center" in routes
    assert "/ob/review-center" in routes

    assert "/ob/owner-console" not in routes
    assert "/ob/owner-dashboard" not in routes


def test_owner_dashboard_is_marked_temporary_placeholder():
    placeholders = temporary_placeholder_routes()

    assert placeholders == [
        "/ob/owner-dashboard",
    ]


def test_security_map_summary_exposes_locks_and_default_deny():
    security_map = build_tower_security_map()
    summary = security_map["summary"]

    assert summary["status"] == "tower_security_map_ready"
    assert summary["unknown_ob_default"] == "403_default_deny"
    assert summary["live_auto"] == "LOCKED"
    assert summary["broker_execution"] is False
    assert summary["capital_action"] is False

    assert security_map["default_deny"]["ob_unknown_route_status"] == 403
    assert security_map["danger_locks"]["live_auto"] == "LOCKED"
    assert security_map["danger_locks"]["broker_execution"] is False
    assert security_map["danger_locks"]["capital_action"] is False


def test_registered_future_apps_are_visible_but_not_opened():
    app_ids = {
        app["app_id"]
        for app in registered_apps()
    }

    assert "observatory" in app_ids
    assert "teller" in app_ids
    assert "vault" in app_ids
    assert "clouds" in app_ids
    assert "grounds" in app_ids

    future_apps = [
        app
        for app in registered_apps()
        if app["app_id"] != "observatory"
    ]

    assert future_apps

    for app in future_apps:
        assert app["app_status"] == "registered_future_room"
        assert app["requires_tower_handoff"] is True
        assert app["dangerous_actions_locked"] is True


def test_security_map_cards_exist():
    cards = security_map_status_cards()

    card_ids = {
        card["card_id"]
        for card in cards
    }

    assert "tower-card-app-registry" in card_ids
    assert "tower-card-protected-routes" in card_ids
    assert "tower-card-owner-only" in card_ids
    assert "tower-card-step-up" in card_ids
    assert "tower-card-default-deny" in card_ids
    assert "tower-card-danger-locks" in card_ids


def test_every_route_has_explanation_and_lock_state():
    for route in registered_routes():
        assert route["route"]
        assert route["label"]
        assert route["lock_state"]
        assert route["explanation"]
        assert route["requires_owner_session"] is True
        assert route["default_denied_when_unknown"] is True
