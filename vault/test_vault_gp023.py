"""
Tests for VAULT GIANT PACK 023 — Packet Action Plan
"""

from pathlib import Path

import pytest

from vault.packet_action_plan_service import (
    get_gp023_status,
    get_packet_action_plan_blocked,
    get_packet_action_plan_board,
    get_packet_action_plan_dependencies,
    get_packet_action_plan_home,
    get_packet_action_plan_owner_queue,
    get_packet_action_plan_priority,
    get_packet_action_plan_steps,
    render_packet_action_plan_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp023_status_ready_safe_to_continue_and_not_done():
    status = get_gp023_status()

    assert status["pack"]["id"] == "VAULT_GP023"
    assert status["gp023_status"]["ready"] is True
    assert status["gp023_status"]["gp022_packet_gap_detail_connected"] is True
    assert status["gp023_status"]["packet_action_plan_ready"] is True
    assert status["gp023_status"]["safe_to_continue_to_gp024"] is True
    assert status["gp023_status"]["vault_done"] is False
    assert status["gp023_status"]["metadata_only_action_plan"] is True
    assert status["gp023_status"]["direct_upload_still_locked"] is True
    assert status["gp023_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp023_status"]["external_access_still_locked"] is True
    assert status["gp023_status"]["unredacted_export_still_locked"] is True
    assert status["gp023_status"]["raw_export_still_locked"] is True
    assert status["gp023_status"]["public_proof_still_locked"] is True
    assert status["gp023_status"]["portal_access_still_locked"] is True
    assert status["gp023_status"]["financing_decision_not_claimed"] is True
    assert status["gp023_status"]["legal_advice_not_claimed"] is True
    assert status["gp023_status"]["raw_verification_not_claimed"] is True
    assert status["gp023_status"]["auto_action_execution_disabled"] is True
    assert status["gp023_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp023"


def test_gp023_action_truth_keeps_all_restricted_paths_locked():
    status = get_gp023_status()
    truth = status["action_truth"]

    assert truth["packet_action_plan_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["external_access_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["auto_packet_approval_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp023_tower_authority_and_vault_boundaries():
    status = get_gp023_status()
    tower = status["tower_authority"]
    vault = status["vault_boundary"]

    assert tower["tower_owns_identity"] is True
    assert tower["tower_owns_permissions"] is True
    assert tower["tower_owns_clearance"] is True
    assert tower["tower_owns_step_up"] is True
    assert tower["tower_owns_export_locks"] is True
    assert tower["tower_owns_freeze_revoke"] is True
    assert tower["tower_owns_external_access"] is True
    assert tower["tower_owns_portal_unlocks"] is True
    assert tower["tower_owns_sensitive_visibility"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp023_action_plan_board_has_all_packet_plans():
    board = get_packet_action_plan_board()["action_plan_board"]

    assert board["action_plan_count"] >= 6
    assert board["high_priority_plan_count"] >= 3
    assert board["ready_for_owner_action_count"] == board["action_plan_count"]
    assert board["auto_execute_allowed_count"] == 0
    assert board["clouds_status"] == "parked_do_not_continue_from_vault_gp023"

    packet_ids = {plan["packet_id"] for plan in board["action_plans"]}
    assert "owner_review_atm_route_acquisition" in packet_ids
    assert "owner_review_apartment_lender" in packet_ids
    assert "owner_review_trust_entity_authority" in packet_ids
    assert "owner_review_ob_manual_live_private_proof" in packet_ids
    assert "owner_review_soulaana_artist_ip" in packet_ids
    assert "owner_review_private_beta_onboarding" in packet_ids

    for plan in board["action_plans"]:
        assert plan["plan_id"].startswith("VAP-")
        assert plan["plan_status"] == "READY_FOR_OWNER_ACTION_REVIEW"
        assert plan["gap_count"] >= 1
        assert plan["action_step_count"] >= plan["gap_count"]
        assert plan["owner_required_step_count"] >= 1
        assert plan["tower_owned_step_count"] >= 1
        assert plan["auto_execute_allowed_count"] == 0
        assert plan["plan_truth"]["metadata_only"] is True
        assert plan["plan_truth"]["raw_body_available"] is False
        assert plan["plan_truth"]["external_share_allowed"] is False
        assert plan["plan_truth"]["auto_execute_allowed"] is False
        assert plan["plan_truth"]["financing_decision_allowed"] is False
        assert plan["plan_truth"]["legal_advice_allowed"] is False
        assert plan["plan_truth"]["raw_verification_claim_allowed"] is False


def test_gp023_action_steps_are_safe_and_do_not_auto_execute():
    steps = get_packet_action_plan_steps()

    assert steps["action_step_count"] >= 40

    action_types = {step["action_type"] for step in steps["action_steps"]}
    assert "review_metadata_gap" in action_types
    assert "request_missing_detail" in action_types
    assert "hold_raw_support" in action_types
    assert "hold_external_share" in action_types
    assert "owner_confirm_next_step" in action_types

    for step in steps["action_steps"]:
        assert step["step_id"].startswith("VAS-")
        assert step["plan_packet_id"].startswith("owner_review_")
        assert step["status"] == "READY_FOR_OWNER_ACTION_REVIEW"
        assert step["can_auto_execute"] is False
        assert step["raw_body_available"] is False
        assert step["external_share_allowed"] is False
        assert "RAW_FILE_BODY_LOCKED" in step["blocked_codes"]
        assert "DIRECT_UPLOAD_LOCKED" in step["blocked_codes"]
        assert "NO_AUTO_ACTION_EXECUTION" in step["blocked_codes"]
        assert "CLOUDS_PARKED" in step["blocked_codes"]


def test_gp023_dependency_lanes_keep_restricted_dependencies_locked():
    deps = get_packet_action_plan_dependencies()["dependency_lanes"]

    assert deps["lane_count"] >= 4
    assert deps["blocked_lane_count"] >= 1
    assert deps["tower_owned_lane_count"] >= 1
    assert deps["all_restricted_dependencies_locked"] is True

    lane_ids = {lane["lane_id"] for lane in deps["lanes"]}
    assert "dependency_owner_review" in lane_ids
    assert "dependency_tower_clearance" in lane_ids
    assert "dependency_storage_provider" in lane_ids
    assert "dependency_external_share" in lane_ids

    for lane in deps["lanes"]:
        assert lane["step_count"] >= 0
        if lane["lane_id"] != "dependency_owner_review":
            assert lane["blocked"] is True
            assert lane["tower_owned"] is True


def test_gp023_priority_queue_orders_high_priority_first():
    priority = get_packet_action_plan_priority()["priority_queue"]

    assert priority["priority_item_count"] >= 6
    assert priority["first_priority_packet_id"] == "owner_review_atm_route_acquisition"
    assert priority["owner_review_required"] is True
    assert priority["auto_execute_allowed"] is False

    ranks = [item["priority_rank"] for item in priority["priority_items"]]
    assert ranks == sorted(ranks)

    for item in priority["priority_items"]:
        assert item["priority_id"].startswith("VAPQ-")
        assert item["plan_id"].startswith("VAP-")
        assert item["packet_id"].startswith("owner_review_")
        assert item["owner_review_required"] is True
        assert item["auto_execute_allowed"] is False


def test_gp023_blocked_actions_keep_restricted_paths_locked():
    blocked = get_packet_action_plan_blocked()["blocked_actions"]

    assert blocked["blocked_action_count"] >= 10
    assert blocked["all_blocked_actions_safe"] is True
    assert blocked["auto_override_allowed"] is False
    assert blocked["all_restricted_paths_locked"] is True

    codes = {item["code"] for item in blocked["blocked_actions"]}
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "PERMANENT_STORAGE_NOT_CONFIGURED" in codes
    assert "EXTERNAL_ACCESS_DENIED" in codes
    assert "UNREDACTED_EXPORT_LOCKED" in codes
    assert "RAW_EXPORT_LOCKED" in codes
    assert "PUBLIC_PROOF_LOCKED" in codes
    assert "TOWER_CLEARANCE_REQUIRED" in codes
    assert "OWNER_CONFIRMATION_REQUIRED" in codes
    assert "NO_AUTO_ACTION_EXECUTION" in codes
    assert "CLOUDS_PARKED" in codes

    for blocker in blocked["blocked_actions"]:
        assert blocker["safe_to_override_inside_vault"] is False
        assert blocker["affected_step_count"] >= 1
        assert blocker["vault_response"]


def test_gp023_owner_queue_says_continue_vault_not_clouds():
    queue = get_packet_action_plan_owner_queue()["owner_review_state"]

    assert queue["review_room"] == "Vault Packet Action Plan"
    assert queue["action_count"] >= 5
    assert queue["action_plan_count"] >= 6
    assert queue["priority_item_count"] >= 6
    assert queue["blocked_action_count"] >= 10
    assert queue["owner_review_needed_count"] >= 1
    assert queue["tower_owned_action_count"] >= 1
    assert queue["auto_complete_allowed"] is False

    joined = " ".join(queue["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp024" in joined


def test_gp023_home_routes_declared():
    home = get_packet_action_plan_home()
    summary = home["action_summary"]

    assert summary["route"] == "/vault/packet-action-plan"
    assert summary["json_route"] == "/vault/packet-action-plan.json"
    assert summary["board_route"] == "/vault/packet-action-plan-board.json"
    assert summary["steps_route"] == "/vault/packet-action-plan-steps.json"
    assert summary["dependencies_route"] == "/vault/packet-action-plan-dependencies.json"
    assert summary["priority_route"] == "/vault/packet-action-plan-priority.json"
    assert summary["blocked_route"] == "/vault/packet-action-plan-blocked.json"
    assert summary["owner_queue_route"] == "/vault/packet-action-plan-owner-queue.json"
    assert summary["gp023_status_route"] == "/vault/gp023-status.json"
    assert summary["metadata_only"] is True

    assert home["gp022_connection"]["gp022_ready"] is True
    assert home["gp022_connection"]["gp022_safe_to_continue"] is True
    assert home["gp022_connection"]["gp022_vault_done"] is False


def test_gp023_html_is_dark_and_has_no_white_background_tokens():
    html = render_packet_action_plan_page()
    lowered = html.lower()

    assert "Vault Packet Action Plan" in html
    assert "Archive Vault" in html
    assert "/vault/packet-action-plan.json" in html
    assert "/vault/gp023-status.json" in html
    assert "Clouds parked" in html

    forbidden = [
        "background: #fff",
        "background:#fff",
        "background-color: #fff",
        "background-color:#fff",
        "background: white",
        "background:white",
    ]

    for token in forbidden:
        assert token not in lowered


def test_gp023_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/packet-action-plan",
        "/vault/packet-action-plan.json",
        "/vault/packet-action-plan-board.json",
        "/vault/packet-action-plan-steps.json",
        "/vault/packet-action-plan-dependencies.json",
        "/vault/packet-action-plan-priority.json",
        "/vault/packet-action-plan-blocked.json",
        "/vault/packet-action-plan-owner-queue.json",
        "/vault/gp023-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp023_flask_routes_when_app_importable_accepts_tower_guard():
    """
    In the full app, private Vault paths may return 403 because Tower/guard layers
    protect /vault routes. That is correct.

    Accept:
    - 200 direct local route response
    - 403 protected private route response

    Do not accept 404.
    """
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/packet-action-plan",
        "/vault/packet-action-plan.json",
        "/vault/packet-action-plan-board.json",
        "/vault/packet-action-plan-steps.json",
        "/vault/packet-action-plan-dependencies.json",
        "/vault/packet-action-plan-priority.json",
        "/vault/packet-action-plan-blocked.json",
        "/vault/packet-action-plan-owner-queue.json",
        "/vault/gp023-status.json",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code in (200, 403), (
            f"{route} returned unexpected status {response.status_code}. "
            "Expected 200 direct route or 403 Tower/private guard."
        )

        if response.status_code == 200:
            if route.endswith(".json"):
                assert response.get_json() is not None
            else:
                assert b"Vault Packet Action Plan" in response.data
