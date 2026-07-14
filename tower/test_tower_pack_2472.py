from tower.tower_ir_cert_p2472 import (
    build_ir_cert_p2472_preview,
)


def test_pack_2472_operations_contract():
    payload = build_ir_cert_p2472_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Hosted Persistence Operations Readiness'
    assert payload["operations_readiness_ready"] is True
    assert payload["schema_version_gate"] is True
    assert payload["startup_health_check"] is True
    assert payload["backup_snapshot"] is True
    assert payload["backup_verification"] is True
    assert payload["restore_preview"] is True
    assert payload["explicit_restore_confirmation"] is True
    assert payload["retention_preview"] is True
    assert payload["automatic_cleanup"] is False
    assert payload["owner_export_preview"] is True
    assert payload["corruption_assessment"] is True
    assert payload["automatic_restore"] is False
    assert payload["tower_owned_storage"] is True
    assert payload["direct_vault_write"] is False
    assert payload["public_links"] is False
    assert payload["owner_only"] is True
    assert payload["default_deny"] is True
    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False
    assert payload[
        "production_manual_live_authorization"
    ] is False
    assert payload["live_auto_activation"] is False
    assert payload["preview_only"] is True
    assert payload[
        "safe_to_continue_to_pack_2473"
    ] is True
