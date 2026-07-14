from tower.tower_ir_cert_p2372 import (
    build_ir_cert_p2372_preview,
    get_room_by_id,
)


def test_pack_2372_six_room_registry():
    payload = build_ir_cert_p2372_preview()

    assert payload["pack"] == "2372"
    assert payload["app_id"] == "the_observatory"
    assert payload["room_count"] == 6
    assert payload["default_deny"] is True
    assert payload["unmapped_routes_blocked"] is True

    names = {
        room["display_name"]
        for room in payload["rooms"]
    }

    assert names == {
        "Dashboard",
        "Market Map",
        "Symbol Page",
        "Trade Center",
        "Review Center",
        "Owner Console",
    }


def test_pack_2372_owner_console_contract():
    room = get_room_by_id("ob_room_owner_console")

    assert room["canonical_route"] == "/owner-console"
    assert room["required_role"] == "owner"
    assert room["required_clearance_value"] == (
        "ob_owner_command"
    )
    assert room["required_clearance_rank"] == 900
    assert room["step_up_required"] is True
    assert room["owner_only"] is True
