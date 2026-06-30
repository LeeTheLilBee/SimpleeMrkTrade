"""
Tests for VAULT GIANT PACK 035 — Packet Review Decision Prep
"""

from pathlib import Path

import pytest

from vault.packet_review_decision_prep_service import (
    get_gp035_status,
    get_packet_review_decision_prep_blocker_limits,
    get_packet_review_decision_prep_carry_forward,
    get_packet_review_decision_prep_home,
    get_packet_review_decision_prep_next_decisions,
    get_packet_review_decision_prep_options,
    get_packet_review_decision_prep_paths,
    get_packet_review_decision_prep_prompts,
    get_packet_review_decision_prep_readiness,
    get_packet_review_decision_prep_records,
    get_packet_review_decision_prep_tower_requirements,
    render_packet_review_decision_prep_page,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_gp035_status_ready_and_safe_to_continue():
    status = get_gp035_status()

    assert status["pack"]["id"] == "VAULT_GP035"
    assert status["pack"]["section"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["pack"]["section_range"] == "GP031-GP040"
    assert status["gp035_status"]["ready"] is True
    assert status["gp035_status"]["section_id"] == "ARCHIVE_VAULT_CONTROLLED_PACKET_ASSEMBLY_LAYER"
    assert status["gp035_status"]["gp034_priority_connected"] is True
    assert status["gp035_status"]["packet_review_decision_prep_ready"] is True
    assert status["gp035_status"]["safe_to_continue_to_gp036"] is True
    assert status["gp035_status"]["vault_done"] is False
    assert status["gp035_status"]["metadata_only_decision_prep"] is True
    assert status["gp035_status"]["private_decision_prep_only"] is True
    assert status["gp035_status"]["owner_review_required"] is True
    assert status["gp035_status"]["owner_confirmation_required"] is True
    assert status["gp035_status"]["owner_confirmed_count"] == 0
    assert status["gp035_status"]["completed_count"] == 0
    assert status["gp035_status"]["auto_completion_disabled"] is True
    assert status["gp035_status"]["auto_confirmation_disabled"] is True
    assert status["gp035_status"]["execution_engine_disabled"] is True
    assert status["gp035_status"]["auto_action_execution_disabled"] is True
    assert status["gp035_status"]["direct_upload_still_locked"] is True
    assert status["gp035_status"]["raw_file_body_storage_still_locked"] is True
    assert status["gp035_status"]["external_delivery_still_locked"] is True
    assert status["gp035_status"]["external_access_still_locked"] is True
    assert status["gp035_status"]["packet_export_still_locked"] is True
    assert status["gp035_status"]["unredacted_export_still_locked"] is True
    assert status["gp035_status"]["raw_export_still_locked"] is True
    assert status["gp035_status"]["public_proof_still_locked"] is True
    assert status["gp035_status"]["public_packet_proof_disabled"] is True
    assert status["gp035_status"]["portal_access_still_locked"] is True
    assert status["gp035_status"]["financing_decision_not_claimed"] is True
    assert status["gp035_status"]["legal_advice_not_claimed"] is True
    assert status["gp035_status"]["raw_verification_not_claimed"] is True
    assert status["gp035_status"]["clouds_status"] == "parked_do_not_continue_from_vault_gp035"


def test_gp035_truth_keeps_restricted_paths_locked():
    status = get_gp035_status()
    truth = status["decision_truth"]

    assert truth["packet_review_decision_prep_enabled"] is True
    assert truth["metadata_only"] is True
    assert truth["private_decision_prep_only"] is True
    assert truth["decision_prep_means_owner_review_not_approval"] is True
    assert truth["safe_decision_options_enabled"] is True
    assert truth["unsafe_decision_paths_locked"] is True
    assert truth["readiness_labels_enabled"] is True
    assert truth["owner_decision_prompts_enabled"] is True
    assert truth["tower_gate_requirements_enabled"] is True
    assert truth["blocker_based_limits_enabled"] is True
    assert truth["next_decision_sorting_enabled"] is True
    assert truth["raw_file_body_storage_enabled"] is False
    assert truth["direct_upload_unlocked"] is False
    assert truth["provider_configured"] is False
    assert truth["external_packet_delivery_enabled"] is False
    assert truth["external_access_enabled"] is False
    assert truth["packet_export_enabled"] is False
    assert truth["unredacted_export_enabled"] is False
    assert truth["raw_export_enabled"] is False
    assert truth["public_packet_proof_enabled"] is False
    assert truth["public_proof_enabled"] is False
    assert truth["portal_access_enabled"] is False
    assert truth["owner_confirmed_count"] == 0
    assert truth["completed_count"] == 0
    assert truth["auto_completion_enabled"] is False
    assert truth["auto_confirmation_enabled"] is False
    assert truth["execution_engine_enabled"] is False
    assert truth["auto_action_execution_enabled"] is False
    assert truth["financing_decision_enabled"] is False
    assert truth["legal_advice_enabled"] is False
    assert truth["raw_document_verification_claimed"] is False
    assert truth["auto_packet_approval_enabled"] is False
    assert truth["clouds_should_continue"] is False


def test_gp035_tower_authority_and_vault_boundaries():
    status = get_gp035_status()
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
    assert tower["tower_owns_action_authority_gates"] is True
    assert tower["vault_owns_tower_permissions"] is False

    assert vault["no_public_vault"] is True
    assert vault["direct_raw_upload_unlocked"] is False
    assert vault["permanent_file_body_storage_enabled"] is False
    assert vault["external_access_default"] == "denied"
    assert vault["external_packet_delivery_allowed"] is False
    assert vault["packet_export_allowed"] is False
    assert vault["unredacted_export_allowed"] is False
    assert vault["raw_export_allowed"] is False
    assert vault["redacted_owner_preview_allowed"] is True
    assert vault["sensitive_body_display_in_summary_views"] is False
    assert vault["beneficiary_details_in_summary_views"] is False
    assert vault["broker_secret_storage_allowed"] is False
    assert vault["public_ob_proof_allowed"] is False
    assert vault["public_packet_proof_allowed"] is False
    assert vault["ai_generated_soulaana_or_black_woman_character_art_allowed"] is False


def test_gp035_decision_records_cover_priority_packets():
    records = get_packet_review_decision_prep_records()

    assert records["decision_record_count"] == 7

    ordered_packet_ids = [record["packet_id"] for record in records["decision_records"]]
    assert ordered_packet_ids == [
        "ATM_ROUTE_ACQUISITION_PACKET",
        "APARTMENT_LENDER_DUE_DILIGENCE_PACKET",
        "TRUST_ENTITY_AUTHORITY_PACKET",
        "OB_MANUAL_LIVE_PROOF_PACKET",
        "SOULAANA_ARTIST_IP_PACKET",
        "PRIVATE_BETA_ONBOARDING_PACKET",
        "OWNER_ACTION_RECEIPT_PACKET",
    ]

    for record in records["decision_records"]:
        assert record["decision_prep_id"].startswith("VDR-")
        assert record["priority_id"].startswith("VPR-")
        assert record["review_group_id"].startswith("VPG-")
        assert record["assembly_id"].startswith("VPA-")
        assert record["decision_prep_status"] == "READY_FOR_OWNER_DECISION_PREP_NO_EXECUTION"
        assert len(record["safe_decision_options"]) == 4
        assert len(record["unsafe_decision_options"]) == 16
        assert record["recommended_safe_option"] in {
            "OWNER_REVIEW_NOW",
            "HOLD_FOR_TOWER_GATE",
            "HOLD_FOR_BLOCKER_RESOLUTION",
            "CARRY_FORWARD_TO_GP036",
        }
        assert record["metadata_only"] is True
        assert record["private_decision_prep_only"] is True
        assert record["owner_review_required"] is True
        assert record["owner_reviewed"] is False
        assert record["owner_confirmation_required"] is True
        assert record["owner_confirmed"] is False
        assert record["decision_selected"] is False
        assert record["selected_decision_code"] is None
        assert record["completed"] is False
        assert record["auto_complete_allowed"] is False
        assert record["auto_confirm_allowed"] is False
        assert record["approval_allowed"] is False
        assert record["can_execute_from_vault"] is False
        assert record["execution_engine_enabled"] is False
        assert record["raw_body_available_count"] == 0
        assert record["raw_file_body_storage_enabled"] is False
        assert record["direct_upload_unlocked"] is False
        assert record["external_delivery_allowed"] is False
        assert record["external_access_allowed"] is False
        assert record["packet_export_allowed"] is False
        assert record["raw_export_allowed"] is False
        assert record["unredacted_export_allowed"] is False
        assert record["public_packet_proof_allowed"] is False
        assert record["portal_access_allowed"] is False
        assert record["tower_clearance_required"] is True
        assert record["tower_step_up_required"] is True
        assert record["vault_can_override_tower"] is False
        assert record["safe_to_review_privately"] is True
        assert record["safe_to_deliver_externally"] is False
        assert record["safe_to_export"] is False
        assert record["safe_to_carry_to_gp036"] is True
        assert "PACKET_REVIEW_DECISION_PREP_PRIVATE_ONLY" in record["blocked_codes"]
        assert "NO_EXTERNAL_PACKET_DELIVERY" in record["blocked_codes"]
        assert "NO_PACKET_EXPORT" in record["blocked_codes"]
        assert "CLOUDS_PARKED" in record["blocked_codes"]


def test_gp035_decision_options_split_safe_and_unsafe():
    options = get_packet_review_decision_prep_options()["decision_options"]

    assert options["safe_option_count"] == 28
    assert options["unsafe_option_count"] == 112
    assert options["decision_record_count"] == 7
    assert options["safe_option_per_packet_count"] == 4
    assert options["unsafe_option_per_packet_count"] == 16
    assert options["external_delivery_allowed_count"] == 0
    assert options["packet_export_allowed_count"] == 0
    assert options["executes_action_count"] == 0
    assert options["unsafe_locked_count"] == 112
    assert options["safe_to_continue_decision_options"] is True

    safe_codes = {item["option_code"] for item in options["safe_decision_options"]}
    assert safe_codes == {
        "OWNER_REVIEW_NOW",
        "HOLD_FOR_TOWER_GATE",
        "HOLD_FOR_BLOCKER_RESOLUTION",
        "CARRY_FORWARD_TO_GP036",
    }

    unsafe_codes = {item["option_code"] for item in options["unsafe_decision_options"]}
    assert "EXPORT_PACKET" in unsafe_codes
    assert "UNLOCK_DIRECT_UPLOAD" in unsafe_codes
    assert "EXECUTE_ACTION_FROM_VAULT" in unsafe_codes
    assert "CONTINUE_CLOUDS_FROM_VAULT" in unsafe_codes

    for item in options["safe_decision_options"]:
        assert item["decision_option_id"].startswith("VDO-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["safe_option"] is True
        assert item["metadata_only"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["owner_review_required"] is True
        assert item["safe_to_carry_to_gp036"] is True

    for item in options["unsafe_decision_options"]:
        assert item["unsafe_option_id"].startswith("VUDO-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["safe_option"] is False
        assert item["locked"] is True
        assert item["metadata_only"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["owner_review_required"] is True
        assert item["safe_to_override_inside_vault"] is False


def test_gp035_readiness_labels_are_private_review_only():
    readiness = get_packet_review_decision_prep_readiness()["readiness_labels"]

    assert readiness["readiness_label_count"] == 7
    assert readiness["owner_review_required_count"] == 7
    assert readiness["owner_confirmed_count"] == 0
    assert readiness["completed_count"] == 0
    assert readiness["external_delivery_allowed_count"] == 0
    assert readiness["packet_export_allowed_count"] == 0
    assert readiness["safe_to_continue_readiness_labels"] is True

    labels = {item["readiness_label"] for item in readiness["readiness_items"]}
    assert "OWNER_FOCUS_READY_CRITICAL_BLOCKERS_TOWER_LOCKED" in labels
    assert "OWNER_FOCUS_READY_AUTHORITY_BLOCKERS_TOWER_LOCKED" in labels
    assert "PRIVATE_REVIEW_READY_HIGH_BLOCKERS" in labels
    assert "PRIVATE_REVIEW_READY_MEDIUM_BLOCKERS" in labels

    for item in readiness["readiness_items"]:
        assert item["readiness_id"].startswith("VDRL-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp036"] is True


def test_gp035_owner_prompts_do_not_execute_or_confirm():
    prompts = get_packet_review_decision_prep_prompts()["owner_prompts"]

    assert prompts["owner_prompt_count"] == 7
    assert prompts["auto_confirm_allowed_count"] == 0
    assert prompts["executes_action_count"] == 0
    assert prompts["external_delivery_allowed_count"] == 0
    assert prompts["packet_export_allowed_count"] == 0
    assert prompts["safe_to_continue_owner_prompts"] is True

    for item in prompts["owner_prompt_items"]:
        assert item["owner_prompt_id"].startswith("VDP-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert "Do not export" in item["prompt"]
        assert item["prompt_status"] == "READY_FOR_OWNER_REVIEW_NO_AUTO_CONFIRM"
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["executes_action"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["safe_to_carry_to_gp036"] is True


def test_gp035_tower_requirements_preserve_tower_control():
    tower = get_packet_review_decision_prep_tower_requirements()["tower_requirements"]

    assert tower["tower_requirement_count"] == 7
    assert tower["tower_clearance_required_count"] == 7
    assert tower["tower_step_up_required_count"] == 7
    assert tower["tower_export_lock_required_count"] == 7
    assert tower["vault_override_allowed_count"] == 0
    assert tower["external_delivery_allowed_count"] == 0
    assert tower["packet_export_allowed_count"] == 0
    assert tower["portal_access_allowed_count"] == 0
    assert tower["all_tower_requirements_preserved"] is True

    for item in tower["tower_requirement_items"]:
        assert item["tower_requirement_id"].startswith("VDTR-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["tower_clearance_required"] is True
        assert item["tower_step_up_required"] is True
        assert item["tower_export_lock_required"] is True
        assert item["tower_external_access_required"] is True
        assert item["tower_portal_unlock_required"] is True
        assert item["tower_sensitive_visibility_required"] is True
        assert item["vault_can_override_tower"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["safe_to_carry_to_gp036"] is True


def test_gp035_blocker_limits_keep_all_restricted_paths_locked():
    limits = get_packet_review_decision_prep_blocker_limits()["blocker_limits"]

    assert limits["blocker_limit_count"] == 7
    assert limits["active_block_code_count"] >= 20
    assert limits["critical_limit_count"] == 2
    assert limits["high_limit_count"] == 3
    assert limits["medium_limit_count"] == 2
    assert limits["all_restricted_paths_locked"] is True
    assert limits["safe_to_override_inside_vault_count"] == 0
    assert limits["external_delivery_allowed_count"] == 0
    assert limits["packet_export_allowed_count"] == 0
    assert limits["public_packet_proof_allowed_count"] == 0
    assert limits["execution_allowed_count"] == 0
    assert limits["safe_to_continue_blocker_limits"] is True

    codes = set(limits["active_block_codes"])
    assert "RAW_FILE_BODY_LOCKED" in codes
    assert "DIRECT_UPLOAD_LOCKED" in codes
    assert "NO_EXTERNAL_PACKET_DELIVERY" in codes
    assert "NO_PACKET_EXPORT" in codes
    assert "NO_ACTION_EXECUTION_FROM_VAULT" in codes
    assert "PACKET_REVIEW_DECISION_PREP_PRIVATE_ONLY" in codes
    assert "CLOUDS_PARKED" in codes

    for item in limits["blocker_limit_items"]:
        assert item["blocker_limit_id"].startswith("VDBL-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["decision_limit_status"] == "LIMITED_TO_PRIVATE_OWNER_REVIEW"
        assert item["all_restricted_paths_locked"] is True
        assert item["safe_to_override_inside_vault"] is False
        assert item["raw_storage_allowed"] is False
        assert item["direct_upload_allowed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["portal_access_allowed"] is False
        assert item["execution_allowed"] is False
        assert item["safe_to_carry_to_gp036"] is True


def test_gp035_decision_paths_split_safe_and_locked_unsafe():
    paths = get_packet_review_decision_prep_paths()["decision_paths"]

    assert paths["safe_path_count"] == 21
    assert paths["unsafe_path_count"] == 21
    assert paths["decision_path_count"] == 42
    assert paths["locked_unsafe_path_count"] == 21
    assert paths["external_delivery_allowed_count"] == 0
    assert paths["packet_export_allowed_count"] == 0
    assert paths["executes_action_count"] == 0
    assert paths["safe_to_continue_decision_paths"] is True

    for item in paths["safe_decision_paths"]:
        assert item["path_id"].startswith("VDSP-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["safe_path"] is True
        assert item["metadata_only"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["safe_to_carry_to_gp036"] is True

    for item in paths["unsafe_decision_paths"]:
        assert item["path_id"].startswith("VDUP-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["safe_path"] is False
        assert item["locked"] is True
        assert item["metadata_only"] is True
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["executes_action"] is False
        assert item["safe_to_override_inside_vault"] is False


def test_gp035_next_decisions_sorted_and_continue_vault_not_clouds():
    decisions = get_packet_review_decision_prep_next_decisions()["next_decisions"]

    assert decisions["next_decision_count"] == 9
    assert decisions["packet_decision_count"] == 7
    assert decisions["boundary_decision_count"] == 1
    assert decisions["next_build_decision_count"] == 1
    assert decisions["owner_review_required_count"] == 9
    assert decisions["decision_selected_count"] == 0
    assert decisions["completed_count"] == 0
    assert decisions["owner_confirmed_count"] == 0
    assert decisions["external_delivery_allowed_count"] == 0
    assert decisions["packet_export_allowed_count"] == 0
    assert decisions["public_packet_proof_allowed_count"] == 0
    assert decisions["safe_to_continue_next_decisions"] is True

    ranks = [item["priority_rank"] for item in decisions["next_decision_items"]]
    assert ranks == sorted(ranks)

    assert decisions["next_decision_items"][0]["packet_id"] == "ATM_ROUTE_ACQUISITION_PACKET"
    assert decisions["next_decision_items"][1]["packet_id"] == "APARTMENT_LENDER_DUE_DILIGENCE_PACKET"
    assert decisions["next_decision_items"][-1]["packet_id"] == "NEXT_VAULT_PACK"

    joined = " ".join(decisions["next_owner_actions"]).lower()
    assert "do not switch to clouds" in joined
    assert "continue vault" in joined
    assert "gp036" in joined

    for item in decisions["next_decision_items"]:
        assert item["next_decision_id"].startswith("VDN-")
        assert item["metadata_only"] is True
        assert item["owner_review_required"] is True
        assert item["owner_confirmed"] is False
        assert item["decision_selected"] is False
        assert item["completed"] is False
        assert item["auto_complete_allowed"] is False
        assert item["auto_confirm_allowed"] is False
        assert item["approval_allowed"] is False
        assert item["can_execute_from_vault"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp036"] is True


def test_gp035_carry_forward_prepares_gp036():
    carry = get_packet_review_decision_prep_carry_forward()["carry_forward"]

    assert carry["carry_forward_count"] == 7
    assert carry["ready_for_gp036_count"] == 7
    assert carry["owner_reviewed_count"] == 0
    assert carry["owner_confirmed_count"] == 0
    assert carry["decision_selected_count"] == 0
    assert carry["completed_count"] == 0
    assert carry["external_delivery_allowed_count"] == 0
    assert carry["packet_export_allowed_count"] == 0
    assert carry["public_packet_proof_allowed_count"] == 0
    assert carry["safe_to_carry_to_gp036"] is True
    assert carry["next_decision_count"] == 9

    for item in carry["carry_forward_items"]:
        assert item["carry_forward_id"].startswith("VDR-CF-")
        assert item["decision_prep_id"].startswith("VDR-")
        assert item["priority_id"].startswith("VPR-")
        assert item["review_group_id"].startswith("VPG-")
        assert item["carry_forward_status"] == "READY_FOR_GP036_OWNER_DECISION_REVIEW"
        assert item["owner_reviewed"] is False
        assert item["owner_confirmed"] is False
        assert item["decision_selected"] is False
        assert item["completed"] is False
        assert item["external_delivery_allowed"] is False
        assert item["packet_export_allowed"] is False
        assert item["public_packet_proof_allowed"] is False
        assert item["safe_to_carry_to_gp036"] is True


def test_gp035_home_routes_declared():
    home = get_packet_review_decision_prep_home()
    summary = home["decision_summary"]

    assert summary["section_header"] == "Archive Vault — Controlled Packet Assembly Layer"
    assert summary["section_range"] == "GP031-GP040"
    assert summary["route"] == "/vault/packet-review-decision-prep"
    assert summary["json_route"] == "/vault/packet-review-decision-prep.json"
    assert summary["records_route"] == "/vault/packet-review-decision-prep-records.json"
    assert summary["options_route"] == "/vault/packet-review-decision-prep-options.json"
    assert summary["readiness_route"] == "/vault/packet-review-decision-prep-readiness.json"
    assert summary["prompts_route"] == "/vault/packet-review-decision-prep-prompts.json"
    assert summary["tower_requirements_route"] == "/vault/packet-review-decision-prep-tower-requirements.json"
    assert summary["blocker_limits_route"] == "/vault/packet-review-decision-prep-blocker-limits.json"
    assert summary["paths_route"] == "/vault/packet-review-decision-prep-paths.json"
    assert summary["next_decisions_route"] == "/vault/packet-review-decision-prep-next-decisions.json"
    assert summary["carry_forward_route"] == "/vault/packet-review-decision-prep-carry-forward.json"
    assert summary["gp035_status_route"] == "/vault/gp035-status.json"
    assert summary["decision_record_count"] == 7
    assert summary["safe_option_count"] == 28
    assert summary["unsafe_option_count"] == 112
    assert summary["metadata_only"] is True

    assert home["gp034_connection"]["gp034_ready"] is True
    assert home["gp034_connection"]["gp034_safe_to_continue"] is True
    assert home["gp034_connection"]["gp034_vault_done"] is False
    assert home["gp034_connection"]["gp034_priority_record_count"] == 7
    assert home["gp034_connection"]["gp034_next_action_count"] == 9
    assert home["gp034_connection"]["gp034_priority_reason_count"] == 28


def test_gp035_html_is_dark_and_has_no_white_background_tokens():
    html = render_packet_review_decision_prep_page()
    lowered = html.lower()

    assert "Vault Packet Review Decision Prep" in html
    assert "Archive Vault" in html
    assert "/vault/packet-review-decision-prep.json" in html
    assert "/vault/gp035-status.json" in html
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


def test_gp035_routes_registered_in_web_app_text():
    web_app = PROJECT_ROOT / "web" / "app.py"
    text = web_app.read_text(encoding="utf-8", errors="ignore")

    required_routes = [
        "/vault/packet-review-decision-prep",
        "/vault/packet-review-decision-prep.json",
        "/vault/packet-review-decision-prep-records.json",
        "/vault/packet-review-decision-prep-options.json",
        "/vault/packet-review-decision-prep-readiness.json",
        "/vault/packet-review-decision-prep-prompts.json",
        "/vault/packet-review-decision-prep-tower-requirements.json",
        "/vault/packet-review-decision-prep-blocker-limits.json",
        "/vault/packet-review-decision-prep-paths.json",
        "/vault/packet-review-decision-prep-next-decisions.json",
        "/vault/packet-review-decision-prep-carry-forward.json",
        "/vault/gp035-status.json",
    ]

    for route in required_routes:
        assert route in text


def test_gp035_flask_routes_when_app_importable_accepts_tower_guard():
    try:
        from web.app import app
    except Exception as exc:
        pytest.skip(f"web.app import skipped in this environment: {exc}")

    client = app.test_client()

    routes = [
        "/vault/packet-review-decision-prep",
        "/vault/packet-review-decision-prep.json",
        "/vault/packet-review-decision-prep-records.json",
        "/vault/packet-review-decision-prep-options.json",
        "/vault/packet-review-decision-prep-readiness.json",
        "/vault/packet-review-decision-prep-prompts.json",
        "/vault/packet-review-decision-prep-tower-requirements.json",
        "/vault/packet-review-decision-prep-blocker-limits.json",
        "/vault/packet-review-decision-prep-paths.json",
        "/vault/packet-review-decision-prep-next-decisions.json",
        "/vault/packet-review-decision-prep-carry-forward.json",
        "/vault/gp035-status.json",
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
                assert b"Vault Packet Review Decision Prep" in response.data
