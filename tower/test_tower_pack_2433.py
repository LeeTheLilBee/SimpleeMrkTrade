from tower.tower_ir_cert_p2433 import (
    REAL_ROOM_REGISTRY,
    build_ir_cert_p2433_preview,
    real_room_by_id,
)


def test_pack_2433_real_room_registry():
    payload = build_ir_cert_p2433_preview()

    assert payload["status"] == "ready"
    assert payload["room_count"] == 6
    assert payload["unresolved_rooms"] == []

    assert [
        room["real_route"]
        for room in REAL_ROOM_REGISTRY
    ] == [
        "/dashboard",
        "/market-map",
        "/ob/symbol/AMD",
        "/ob/trade-center",
        "/ob/review-center",
        "/ob/owner-console",
    ]

    symbol = real_room_by_id(
        "ob_room_symbol_page"
    )

    assert symbol is not None

    assert symbol["route_pattern"] == (
        "/ob/symbol/<symbol>"
    )


def test_pack_2433_safety():
    payload = build_ir_cert_p2433_preview()

    assert payload["default_deny"] is True
    assert payload["preview_only"] is True
    assert payload["writes_state"] is False
