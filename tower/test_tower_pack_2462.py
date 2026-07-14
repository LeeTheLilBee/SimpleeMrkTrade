from tower.tower_ir_cert_p2462 import (
    build_ir_cert_p2462_preview,
)


def test_pack_2462_persistence_contract():
    payload = build_ir_cert_p2462_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Persistence Readiness Checkpoint'
    assert payload["persistence_readiness_ready"] is True
    assert payload["schema_version"] == 1
    assert payload["tower_owned_storage"] is True
    assert payload["archive_vault_storage"] is False
    assert payload["public_storage"] is False
    assert payload["direct_vault_write"] is False
    assert payload["progress_persistence"] is True
    assert payload["room_receipt_persistence"] is True
    assert payload["final_receipt_persistence"] is True
    assert payload["owner_history"] is True
    assert payload["lost_session_resume"] is True
    assert payload["integrity_verification"] is True
    assert payload["owner_only"] is True
    assert payload["default_deny"] is True
    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False
    assert payload[
        "production_manual_live_authorization"
    ] is False
    assert payload["live_auto_activation"] is False
    assert payload["preview_only"] is True
    assert payload["contract_only"] is True
    assert payload[
        "safe_to_continue_to_pack_2463"
    ] is True
