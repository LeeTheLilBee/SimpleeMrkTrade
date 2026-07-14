from tower.tower_ir_cert_p2476 import (
    build_ir_cert_p2476_preview,
)


def test_pack_2476_hosted_assurance_contract():
    payload = build_ir_cert_p2476_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Backup Rotation Inventory'
    assert payload["backup_rotation_inventory_ready"] is True
    assert payload["runtime_gate"] is True
    assert payload["startup_fail_closed"] is True
    assert payload["backup_cadence_readiness"] is True
    assert payload["backup_rotation_inventory"] is True
    assert payload["restore_drill"] is True
    assert payload[
        "production_database_replaced_in_drill"
    ] is False
    assert payload["retention_approval_queue"] is True
    assert payload["automatic_cleanup"] is False
    assert payload["export_evidence_review"] is True
    assert payload["storage_incident_receipts"] is True
    assert payload["operations_readiness_board"] is True
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
        "safe_to_continue_to_pack_2477"
    ] is True
