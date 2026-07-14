from tower.tower_ir_cert_p2486 import (
    build_ir_cert_p2486_preview,
)


def test_pack_2486_deployment_boundary():
    payload = build_ir_cert_p2486_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Backup Cadence Enforcement Preview'
    assert payload["backup_enforcement_preview_ready"] is True
    assert payload["deployment_manifest"] is True
    assert payload["environment_binding_receipts"] is True
    assert payload["startup_gate_receipts"] is True
    assert payload["backup_enforcement_preview"] is True
    assert payload["restore_drill_evidence"] is True
    assert payload["retention_owner_decisions"] is True
    assert payload["incident_review_queue"] is True
    assert payload["release_evidence_packet"] is True
    assert payload["activation_recommendation"] is True
    assert payload["owner_approval_required"] is True
    assert payload["activation_performed"] is False
    assert payload["deployment_command_executed"] is False
    assert payload["production_database_replaced"] is False
    assert payload["automatic_restore"] is False
    assert payload["automatic_cleanup"] is False
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
        "safe_to_continue_to_pack_2487"
    ] is True
