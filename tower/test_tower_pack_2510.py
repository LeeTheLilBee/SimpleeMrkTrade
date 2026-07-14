from tower.tower_ir_cert_p2510 import (
    build_ir_cert_p2510_preview,
)


def test_pack_2510_human_login_ob_contract():
    payload = build_ir_cert_p2510_preview()

    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload["pack_name"] == 'Protected Tower-to-OB Handoff'
    assert payload["protected_ob_handoff_ready"] is True
    assert payload["human_login_form"] is True
    assert payload[
        "owner_credential_verification"
    ] is True
    assert payload[
        "owner_session_establishment"
    ] is True
    assert payload["tower_access_home"] is True
    assert payload[
        "observatory_launch_card"
    ] is True
    assert payload["owner_permission_gate"] is True
    assert payload["owner_step_up_gate"] is True
    assert payload["protected_ob_handoff"] is True
    assert payload["launch_receipt"] is True
    assert payload["logout_session_clear"] is True
    assert payload["credentials_committed"] is False
    assert payload[
        "test_session_injection_required"
    ] is False
    assert payload["default_deny"] is True
    assert payload["broker_order_submission"] is False
    assert payload["real_capital_movement"] is False
    assert payload[
        "production_manual_live_authorization"
    ] is False
    assert payload["live_auto_activation"] is False
    assert payload["direct_vault_write"] is False
    assert payload["public_links"] is False
    assert payload[
        "safe_to_continue_to_pack_2511"
    ] is True
