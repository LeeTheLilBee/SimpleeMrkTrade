from tower.tower_ir_cert_p2375 import (
    evaluate_room_access,
)


def test_pack_2375_dashboard_owner_clearance_passes():
    decision = evaluate_room_access(
        room_id="ob_room_dashboard",
        tower_role="owner",
        canonical_clearance_value="ob_owner_command",
        canonical_clearance_rank=900,
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode="paper",
        step_up_reference=None,
        step_up_valid=False,
        object_context={},
    )

    assert decision["allowed"] is True
    assert decision["reason_code"] == (
        "ob_room_contract_allow"
    )


def test_pack_2375_owner_string_clearance_does_not_pass():
    decision = evaluate_room_access(
        room_id="ob_room_dashboard",
        tower_role="owner",
        canonical_clearance_value="owner",
        canonical_clearance_rank=0,
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode="paper",
        step_up_reference=None,
        step_up_valid=False,
        object_context={},
    )

    assert decision["allowed"] is False
    assert decision["reason_code"] == (
        "ob_clearance_level_too_low"
    )


def test_pack_2375_sensitive_room_requires_step_up():
    decision = evaluate_room_access(
        room_id="ob_room_owner_console",
        tower_role="owner",
        canonical_clearance_value="ob_owner_command",
        canonical_clearance_rank=900,
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode="paper",
        step_up_reference=None,
        step_up_valid=False,
        object_context={
            "mission_account_id": "proof_demo",
        },
    )

    assert decision["allowed"] is False
    assert decision["reason_code"] == (
        "ob_step_up_required"
    )
