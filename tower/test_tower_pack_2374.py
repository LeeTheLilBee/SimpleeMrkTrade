from tower.tower_ir_cert_p2374 import (
    build_ir_cert_p2374_preview,
    translate_tower_clearance,
)


def test_pack_2374_owner_translation():
    decision = translate_tower_clearance(
        subject_id="owner_1",
        tower_role="owner",
        identity_verified=True,
        account_active=True,
        risk_state="acceptable",
        lockdown_state="tower_guarded_default_deny",
    )

    assert decision["allowed"] is True
    assert decision["canonical_clearance_value"] == (
        "ob_owner_command"
    )
    assert decision["canonical_clearance_rank"] == 900
    assert decision["tower_role"] == "owner"


def test_pack_2374_raw_owner_is_not_ob_clearance():
    payload = build_ir_cert_p2374_preview()

    assert payload[
        "raw_owner_string_is_ob_clearance"
    ] is False

    assert payload["owner_role_policy_lowered"] is False
    assert payload["ob_translation_enabled"] is False
