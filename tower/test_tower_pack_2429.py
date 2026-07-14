from tower.tower_ir_cert_p2429 import (
    build_ir_cert_p2429_preview,
)


def test_pack_2429_walkthrough_contract():
    payload = build_ir_cert_p2429_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == "Guided Close and Lockback"
    assert payload["guided_lockback_ready"] is True
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
        "safe_to_continue_to_pack_2430"
    ] is True
