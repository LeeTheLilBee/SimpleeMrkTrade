from tower.tower_ir_cert_p2381 import (
    build_protected_bridge_request,
)


def test_pack_2381_valid_bridge_request():
    request = build_protected_bridge_request(
        request_id="request_1",
        requester_id="owner_1",
        session_id="session_1",
        app_id="ob",
        request_type="ob.protected_room.launch",
        requested_path="/dashboard",
        requested_mode="paper",
        tower_role="owner",
    )

    assert request["valid"] is True
    assert request["app_id"] == "the_observatory"
    assert request["request_type"] == (
        "tower.observatory.protected_room.launch"
    )


def test_pack_2381_invalid_app_default_denied():
    request = build_protected_bridge_request(
        request_id="request_1",
        requester_id="owner_1",
        session_id="session_1",
        app_id="unknown",
        request_type="ob.protected_room.launch",
        requested_path="/dashboard",
        requested_mode="paper",
        tower_role="owner",
    )

    assert request["valid"] is False
    assert request["reason_code"] == (
        "ob_app_id_not_supported"
    )
