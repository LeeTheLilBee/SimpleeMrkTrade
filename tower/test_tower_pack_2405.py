from tower.tower_ir_cert_p2405 import (
    detect_route_contract_drift,
)


def test_pack_2405_stable_route():
    result = detect_route_contract_drift(
        room_id="ob_room_dashboard",
        expected_canonical_path="/dashboard",
        observed_path="/ob/dashboard",
    )

    assert result["drift_detected"] is False
    assert result["resolved_path"] == "/dashboard"


def test_pack_2405_unmapped_route_drift():
    result = detect_route_contract_drift(
        room_id="ob_room_dashboard",
        expected_canonical_path="/dashboard",
        observed_path="/fake-room",
    )

    assert result["drift_detected"] is True
    assert result["reason_code"] == (
        "ob_route_unmapped_default_deny"
    )
