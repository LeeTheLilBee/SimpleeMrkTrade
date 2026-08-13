from __future__ import annotations

from tower.tower_ob_real_surface_route_map import (
    dangerous_controls_locked,
    matched_route_key,
    route_map_cert,
    route_map_payload,
    route_room_label,
    tower_ob_real_surface_route_allowed,
)


def test_route_map_payload_is_safe_and_narrow():
    payload = route_map_payload()

    assert payload["version"] == "tower_ob_real_surface_route_map_v1"
    assert payload["default_deny_preserved"] is True
    assert payload["requires_owner_session"] is True
    assert payload["requires_tower_handoff"] is True
    assert payload["dangerous_controls_locked"] is True
    assert all(value is False for value in payload["dangerous_controls"].values())


def test_approved_real_ob_surface_routes_allowed():
    assert tower_ob_real_surface_route_allowed("/ob/dashboard") is True
    assert tower_ob_real_surface_route_allowed("/ob/market-map") is True
    assert tower_ob_real_surface_route_allowed("/ob/symbol/AMD") is True
    assert tower_ob_real_surface_route_allowed("/ob/trade-center") is True
    assert tower_ob_real_surface_route_allowed("/ob/review-center") is True
    assert tower_ob_real_surface_route_allowed("/ob/owner-console") is True


def test_route_keys_and_room_labels():
    assert matched_route_key("/ob/dashboard") == "dashboard"
    assert matched_route_key("/ob/market-map") == "market_map"
    assert matched_route_key("/ob/symbol/AMD") == "symbol_page"
    assert route_room_label("/ob/symbol/AMD") == "Symbol Page"
    assert route_room_label("/ob/market-map") == "Market Map"


def test_unmapped_routes_remain_denied():
    denied = [
        "/ob/not-real",
        "/ob/symbol/",
        "/ob/symbol/../../secrets",
        "/ob/admin/root",
        "/ob/random/unmapped/page",
        "/admin",
        "/tower/owner-beta",
    ]

    for path in denied:
        assert tower_ob_real_surface_route_allowed(path) is False


def test_route_map_certs_2593_to_2602():
    for pack in range(2593, 2603):
        cert = route_map_cert(pack)

        assert cert["pack"] == pack
        assert cert["status"] == "passed"
        assert cert["route_map_ready"] is True
        assert cert["market_map_allowed"] is True
        assert cert["symbol_amd_allowed"] is True
        assert cert["random_unmapped_denied"] is True
        assert cert["default_deny_preserved"] is True
        assert cert["dangerous_controls_locked"] is True
        assert all(value is False for value in cert["dangerous_controls"].values())


def test_dangerous_controls_locked():
    assert dangerous_controls_locked() is True
