from tower.tower_ir_cert_p2373 import (
    normalize_app_id,
    normalize_request_type,
    resolve_observatory_route,
)


def test_pack_2373_aliases_resolve_canonically():
    assert normalize_app_id("ob") == "the_observatory"

    assert normalize_request_type(
        "ob.protected_room.launch"
    ) == "tower.observatory.protected_room.launch"

    route = resolve_observatory_route("/ob/market-map")

    assert route["allowed"] is True
    assert route["room_id"] == "ob_room_market_map"
    assert route["canonical_path"] == "/market-map"


def test_pack_2373_unmapped_default_deny():
    route = resolve_observatory_route(
        "/made-up-ob-room"
    )

    assert route["allowed"] is False
    assert route["reason_code"] == (
        "ob_route_unmapped_default_deny"
    )


def test_pack_2373_symbol_alias_object_resolution():
    route = resolve_observatory_route(
        "/ob/symbol/amd"
    )

    assert route["allowed"] is True
    assert route["room_id"] == "ob_room_symbol_page"
    assert route["canonical_path"] == "/symbol/AMD"
    assert route["object_context"]["symbol"] == "AMD"
