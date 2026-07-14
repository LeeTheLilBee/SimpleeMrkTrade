from tower.tower_ir_cert_p2403 import (
    evaluate_runtime_interrupt,
)


def test_pack_2403_clear_runtime():
    result = evaluate_runtime_interrupt(
        original_risk_state="acceptable",
        current_risk_state="acceptable",
        original_lockdown_state="normal",
        current_lockdown_state="normal",
        account_active=True,
        identity_still_verified=True,
    )

    assert result["allowed"] is True
    assert result["interrupted"] is False


def test_pack_2403_lockdown_interrupt():
    result = evaluate_runtime_interrupt(
        original_risk_state="acceptable",
        current_risk_state="acceptable",
        original_lockdown_state="normal",
        current_lockdown_state="active",
        account_active=True,
        identity_still_verified=True,
    )

    assert result["allowed"] is False
    assert result["interrupted"] is True
    assert result["required_action"] == "emergency_lockback"
