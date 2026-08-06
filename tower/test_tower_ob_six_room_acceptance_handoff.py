from tower.tower_ob_six_room_acceptance_handoff import (
    HANDOFF_JSON_ROUTE,
    HANDOFF_RETURN_CHECK_ROUTE,
    HANDOFF_ROUTE,
    OB_ACCEPTANCE_COMMIT,
    build_handoff_cert,
    build_handoff_payload,
    build_owner_session_preservation_receipt,
    dangerous_control_locks,
    render_handoff_surface,
    six_room_acceptance_contract,
    six_room_acceptance_package,
)


def test_contract_recognizes_ob_package_without_staging_ready():
    contract = six_room_acceptance_contract()

    assert contract["contract"] == "tower_ob_six_room_acceptance_handoff_v1"
    assert contract["route"] == HANDOFF_ROUTE
    assert contract["json_route"] == HANDOFF_JSON_ROUTE
    assert contract["return_check_route"] == HANDOFF_RETURN_CHECK_ROUTE
    assert contract["tower_integration_branch"] == "tower-ob-six-room-integration-dev"
    assert contract["ob_acceptance_commit"] == OB_ACCEPTANCE_COMMIT
    assert contract["ob_branch_clean_reported"] is True
    assert contract["ob_six_rooms_simplified"] is True
    assert contract["ob_tests_passed"] == 72
    assert contract["tower_recognizes_ob_acceptance_package"] is True
    assert contract["six_room_count"] == 6
    assert contract["tower_to_ob_launch_continuity"] is True
    assert contract["ob_to_tower_return_continuity"] is True
    assert contract["owner_session_preservation_required"] is True
    assert contract["dangerous_controls_locked"] is True
    assert contract["staging_ready"] is False
    assert contract["redeploy_authorized"] is False
    assert contract["merge_ob_to_main_authorized"] is False
    assert contract["merge_tower_integration_to_main_authorized"] is False
    assert contract["broker_submission"] is False
    assert contract["capital_movement"] is False
    assert contract["manual_live_authorized"] is False
    assert contract["live_auto_authorized"] is False


def test_six_room_acceptance_package_has_all_rooms():
    package = six_room_acceptance_package()

    assert package["commit"] == "8aefbbf48fac2e8f6a3ac7368ba17a80909b4253"
    assert package["status"] == "recognized_by_tower_not_merged"
    assert package["branch_clean_reported"] is True
    assert package["tests_passed"] == 72
    assert package["safety_locks_held"] is True
    assert package["staging_ready"] is False

    ids = {room["id"] for room in package["rooms"]}

    assert ids == {
        "dashboard",
        "market_map",
        "symbol_page",
        "trade_center",
        "review_center",
        "owner_console",
    }

    for room in package["rooms"]:
        assert room["acceptance_status"] == "accepted_by_ob_package"
        assert room["tower_walkthrough_route"].startswith(
            "/tower/observatory-walkthrough"
        )


def test_owner_session_preservation_receipt_requires_owner_session():
    receipt = build_owner_session_preservation_receipt(
        owner_session={
            "authenticated": True,
            "role": "owner",
            "owner_id": "owner_solice",
        },
        last_room="Market Map",
    )

    assert receipt["owner_authenticated"] is True
    assert receipt["role"] == "owner"
    assert receipt["owner_id_present"] is True
    assert receipt["owner_session_preserved"] is True
    assert receipt["clearance_preserved"] is True
    assert receipt["last_room"] == "Market Map"
    assert receipt["tower_launch"] == "/tower/launch/observatory"
    assert receipt["tower_return"] == "/tower/return/observatory"
    assert receipt["tower_return_destination"] == "/tower/access-home"
    assert receipt["dangerous_controls"]["broker_submission"] is False
    assert receipt["dangerous_controls"]["capital_movement"] is False
    assert receipt["receipt_hash"]


def test_dangerous_control_locks_stay_closed():
    locks = dangerous_control_locks()

    assert locks["broker_submission"] is False
    assert locks["capital_movement"] is False
    assert locks["production_deployment"] is False
    assert locks["staging_redeploy"] is False
    assert locks["manual_live_authorized"] is False
    assert locks["live_auto_authorized"] is False
    assert locks["direct_vault_write"] is False
    assert locks["destructive_action_unlocked"] is False
    assert locks["merge_ob_to_main_authorized"] is False
    assert locks["staging_ready"] is False


def test_handoff_payload_and_html_surface():
    payload = build_handoff_payload(
        owner_session={
            "authenticated": True,
            "role": "owner",
            "owner_id": "owner_solice",
        },
        step_up_active=True,
    )

    assert payload["surface"] == "tower_ob_six_room_acceptance_handoff_v1"
    assert payload["owner_authenticated"] is True
    assert payload["role"] == "owner"
    assert payload["owner_id_present"] is True
    assert payload["step_up_active"] is True
    assert payload["contract"]["six_room_count"] == 6
    assert payload["contract"]["staging_ready"] is False
    assert payload["contract"]["redeploy_authorized"] is False
    assert payload["dangerous_controls"]["broker_submission"] is False
    assert payload["dangerous_controls"]["capital_movement"] is False
    assert payload["payload_hash"]

    html = render_handoff_surface(payload)

    assert "Tower OB Six-Room Handoff" in html
    assert "Six-Room Handoff" in html
    assert "Tower → OB → Tower" in html
    assert "Accepted Six Rooms" in html
    assert "Dashboard" in html
    assert "Market Map" in html
    assert "Symbol Page" in html
    assert "Trade Center" in html
    assert "Review Center" in html
    assert "Owner Console" in html
    assert "Dangerous Controls Stay Locked" in html
    assert "Integration Evidence Drawers" in html
    assert "<details" in html


def test_handoff_cert_pack_2552_checkpoint():
    payload = build_handoff_cert(2552)

    assert payload["pack"] == "2552"
    assert payload["pack_name"] == "Tower-OB Handoff Repair Checkpoint"
    assert payload[
        "tower_ob_handoff_repair_checkpoint_ready"
    ] is True
    assert payload[
        "tower_ob_six_room_acceptance_handoff"
    ] is True
    assert payload["six_room_count"] == 6
    assert payload["tower_to_ob_launch_continuity"] is True
    assert payload["ob_to_tower_return_continuity"] is True
    assert payload["staging_ready"] is False
    assert payload["redeploy_authorized"] is False
    assert payload["merge_ob_to_main_authorized"] is False
    assert payload["broker_submission"] is False
    assert payload["capital_movement"] is False
    assert payload["manual_live_authorized"] is False
    assert payload["live_auto_authorized"] is False
