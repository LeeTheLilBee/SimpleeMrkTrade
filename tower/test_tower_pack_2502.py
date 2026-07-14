from tower.tower_ir_cert_p2502 import (
    build_ir_cert_p2502_preview,
)


def test_pack_2502_activation_approval_contract():
    payload = build_ir_cert_p2502_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Owner Approval Readiness Checkpoint'
    assert payload["owner_approval_checkpoint_ready"] is True
    assert payload["approval_request"] is True
    assert payload["owner_step_up_required"] is True
    assert payload["credential_material_stored"] is False
    assert payload["scope_freeze"] is True
    assert payload["activation_window_preview"] is True
    assert payload["rollback_readiness"] is True
    assert payload["deployment_command_dry_run"] is True
    assert payload["shell_invoked"] is False
    assert payload["owner_decision_receipt"] is True
    assert payload["execution_hold"] is True
    assert payload["owner_approval_required"] is True
    assert payload["activation_performed"] is False
    assert payload["deployment_command_executed"] is False
    assert payload["production_database_replaced"] is False
    assert payload["automatic_restore"] is False
    assert payload["automatic_cleanup"] is False
    assert payload["direct_vault_write"] is False
    assert payload["public_links"] is False
    assert payload["default_deny"] is True
    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False
    assert payload[
        "production_manual_live_authorization"
    ] is False
    assert payload["live_auto_activation"] is False
    assert payload["preview_only"] is True
    assert payload[
        "safe_to_continue_to_pack_2503"
    ] is True
