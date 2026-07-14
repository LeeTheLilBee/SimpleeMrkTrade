from tower.tower_ir_cert_p2382 import (
    adapt_pack_101_bridge_request,
)


def test_pack_2382_pack_101_request_adapts():
    result = adapt_pack_101_bridge_request({
        "bridge_request_type": (
            "canonical_observatory_bridge_request"
        ),
        "request_id": "request_1",
        "owner_id": "owner_1",
        "session_id": "session_1",
        "app_id": "ob",
        "preferred_route": "/dashboard",
        "mode": "paper",
        "tower_role": "owner",
    })

    assert result["adapted"] is True

    canonical = result["canonical_request"]

    assert canonical["app_id"] == "the_observatory"
    assert canonical["requested_path"] == "/dashboard"


def test_pack_2382_unsupported_request_blocked():
    result = adapt_pack_101_bridge_request({
        "bridge_request_type": "made_up_request",
    })

    assert result["adapted"] is False
    assert result["default_deny"] is True
