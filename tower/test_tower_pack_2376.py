from tower.tower_ir_cert_p2376 import (
    build_protected_room_manifest,
)


def test_pack_2376_owner_manifest_contains_six_rooms():
    manifest = build_protected_room_manifest(
        tower_role="owner",
        canonical_clearance_value="ob_owner_command",
        canonical_clearance_rank=900,
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode="paper",
        step_up_reference="stepup_1",
        step_up_valid=True,
        object_context_by_room={
            "ob_room_symbol_page": {"symbol": "AMD"},
            "ob_room_trade_center": {
                "mission_account_id": "proof_demo"
            },
            "ob_room_review_center": {
                "mission_account_id": "proof_demo"
            },
            "ob_room_owner_console": {
                "mission_account_id": "proof_demo"
            },
        },
    )

    assert manifest["available_room_count"] == 6
    assert manifest["denied_room_count"] == 0


def test_pack_2376_manifest_filters_denied_rooms():
    manifest = build_protected_room_manifest(
        tower_role="authorized_observer",
        canonical_clearance_value="ob_protected_read",
        canonical_clearance_rank=300,
        identity_verified=True,
        risk_state="acceptable",
        lockdown_active=False,
        mode="paper",
        step_up_reference=None,
        step_up_valid=False,
        object_context_by_room={
            "ob_room_symbol_page": {"symbol": "AMD"},
        },
    )

    available = {
        room["room_id"]
        for room in manifest["available_rooms"]
    }

    assert "ob_room_owner_console" not in available
    assert manifest["denied_room_count"] >= 1
