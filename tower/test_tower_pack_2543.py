from tower.tower_ir_cert_p2543 import (
    build_ir_cert_p2543_preview,
)


def test_pack_2543_tower_ob_handoff_contract():
    payload = build_ir_cert_p2543_preview()

    assert payload["pack"] == "2543"
    assert payload["pack_name"] == 'Tower Integration Branch Wake'
    assert payload["status"] == "ready"
    assert payload["readiness"] == 100
    assert payload[
        "tower_ob_six_room_acceptance_handoff"
    ] is True
    assert payload[
        "tower_return_session_continuity_repair"
    ] is True
    assert payload["tower_integration_branch_wake_ready"] is True
    assert payload[
        "tower_integration_branch"
    ] == "tower-ob-six-room-integration-dev"
    assert payload[
        "ob_acceptance_commit"
    ] == "8aefbbf48fac2e8f6a3ac7368ba17a80909b4253"
    assert payload["ob_six_rooms_simplified"] is True
    assert payload["ob_tests_passed"] == 72
    assert payload["six_room_count"] == 6
    assert payload["dashboard_accepted"] is True
    assert payload["market_map_accepted"] is True
    assert payload["symbol_page_accepted"] is True
    assert payload["trade_center_accepted"] is True
    assert payload["review_center_accepted"] is True
    assert payload["owner_console_accepted"] is True
    assert payload[
        "tower_recognizes_ob_acceptance_package"
    ] is True
    assert payload["tower_to_ob_launch_continuity"] is True
    assert payload["ob_to_tower_return_continuity"] is True
    assert payload[
        "owner_session_preservation_required"
    ] is True
    assert payload[
        "owner_walkthrough_integration_surface"
    ] is True
    assert payload["integration_evidence_drawers"] is True
    assert payload["cert_routes_registered"] is True
    assert payload["staging_ready"] is False
    assert payload["redeploy_authorized"] is False
    assert payload["merge_ob_to_main_authorized"] is False
    assert payload[
        "merge_tower_integration_to_main_authorized"
    ] is False
    assert payload["broker_submission"] is False
    assert payload["capital_movement"] is False
    assert payload["production_deployment"] is False
    assert payload["staging_redeploy"] is False
    assert payload["manual_live_authorized"] is False
    assert payload["live_auto_authorized"] is False
    assert payload["direct_vault_write"] is False
    assert payload["destructive_action_unlocked"] is False
    assert payload[
        "safe_to_continue_to_pack_2544"
    ] is True
    assert payload["cert_hash"]
