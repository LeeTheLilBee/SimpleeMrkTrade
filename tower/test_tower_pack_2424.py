from tower.tower_ir_cert_p2424 import (
    build_ir_cert_p2424_preview,
)


def test_pack_2424_walkthrough_contract():
    payload = build_ir_cert_p2424_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == "Owner Access and Session Guard"
    assert payload["owner_session_guard_ready"] is True
    assert payload["official_room_count"] == 6

    assert payload["walkthrough_route"] == (
        "/tower/observatory-walkthrough"
    )

    assert payload["owner_only"] is True

    assert payload["tower_clearance_value"] == (
        "ob_owner_command"
    )

    assert payload["tower_clearance_rank"] == 900
    assert payload["default_deny"] is True

    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False

    assert payload[
        "production_manual_live_authorization"
    ] is False

    assert payload["live_auto_activation"] is False
    assert payload["direct_vault_upload"] is False
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True

    assert payload[
        "safe_to_continue_to_pack_2425"
    ] is True
