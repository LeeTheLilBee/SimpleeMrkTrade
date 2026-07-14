from tower.tower_ir_cert_p2448 import (
    build_ir_cert_p2448_preview,
)


def test_pack_2448_guided_run_contract():
    payload = build_ir_cert_p2448_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Guided Next-Room Handoff'
    assert payload["guided_next_room_handoff_ready"] is True
    assert payload["room_count"] == 6
    assert len(payload["room_order"]) == 6
    assert payload["ordered_progression"] is True
    assert payload["resume_supported"] is True
    assert payload["per_room_receipts"] is True
    assert payload["final_receipt"] is True
    assert payload["tower_progress_badge"] is True
    assert payload["owner_only"] is True
    assert payload["existing_room_guards_preserved"] is True
    assert payload["existing_templates_preserved"] is True
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
    assert payload["writes_state"] is False
    assert payload[
        "safe_to_continue_to_pack_2449"
    ] is True
