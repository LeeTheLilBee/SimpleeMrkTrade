from tower.tower_ir_cert_p2415 import (
    create_safety_boundary_attestation,
)


def test_pack_2415_safety_attestation():
    attestation = create_safety_boundary_attestation()

    assert attestation[
        "all_required_boundaries_present"
    ] is True

    assert attestation[
        "all_prohibited_capabilities_disabled"
    ] is True

    boundaries = attestation["boundaries"]

    assert boundaries["default_deny"] is True
    assert boundaries["unmapped_routes_blocked"] is True
    assert boundaries["ob_self_authorization"] is False
    assert boundaries["broker_order_submission"] is False
    assert boundaries["real_capital_movement"] is False
    assert boundaries["live_auto_activation"] is False
