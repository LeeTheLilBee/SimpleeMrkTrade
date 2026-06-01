
"""
PACK 166 fast test - Approval Receipt Evidence Drawer UI Index / Detail Lookup.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_166_payload_ready_and_lookup_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
    payload = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=True)

    assert payload["pack_number"] == 166
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"

    assert payload["simulated_only"] is True
    assert payload["lookup_preview_only"] is True
    assert payload["detail_preview_only"] is True
    assert payload["evidence_drawer_preview_only"] is True
    assert payload["owner_review_preview_only"] is True
    assert payload["queue_preview_only"] is True
    assert payload["renewal_preview_only"] is True
    assert payload["recheck_preview_only"] is True
    assert payload["expiration_preview_only"] is True
    assert payload["vault_preview_only"] is True
    assert payload["index_preview_only"] is True
    assert payload["receipt_preview_only"] is True
    assert payload["approval_preview_only"] is True
    assert payload["evidence_preview_only"] is True

    assert payload["real_approval_executed"] is False
    assert payload["real_policy_change_executed"] is False
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["real_archive_written"] is False
    assert payload["real_vault_written"] is False
    assert payload["real_expiration_enforced"] is False
    assert payload["real_recheck_executed"] is False
    assert payload["real_renewal_executed"] is False
    assert payload["real_queue_action_executed"] is False
    assert payload["real_owner_review_completed"] is False
    assert payload["real_owner_approval_executed"] is False
    assert payload["real_owner_rejection_executed"] is False
    assert payload["real_owner_acknowledgement_executed"] is False
    assert payload["real_evidence_revealed"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["lookup_record_count"] >= 9
    assert summary["detail_drawer_count"] >= 9
    assert summary["lookup_key_count"] >= 9

    assert summary["unique_index_counts"]["by_detail_drawer_id"] == summary["lookup_record_count"]
    assert summary["unique_index_counts"]["by_owner_review_item_id"] == summary["lookup_record_count"]
    assert summary["unique_index_counts"]["by_queue_item_id"] == summary["lookup_record_count"]

    assert summary["group_index_counts"]["by_scenario_id"] >= 1
    assert summary["group_index_counts"]["by_owner_review_category"] >= 5
    assert summary["group_index_counts"]["by_required_owner_action"] >= 5
    assert summary["group_index_counts"]["by_owner_review_priority"] >= 4
    assert summary["group_index_counts"]["by_detail_status"] >= 1
    assert summary["group_index_counts"]["by_risk_lane"] >= 5

    checks = payload["readiness_checks"]
    assert checks["pack_165_ready"] is True
    assert checks["has_lookup_records"] is True
    assert checks["lookup_count_matches_detail_drawers"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_lookup_preview_only"] is True
    assert checks["all_detail_preview_only"] is True
    assert checks["all_evidence_drawer_preview_only"] is True
    assert checks["all_owner_review_preview_only"] is True
    assert checks["all_queue_preview_only"] is True
    assert checks["all_renewal_preview_only"] is True
    assert checks["all_recheck_preview_only"] is True
    assert checks["all_expiration_preview_only"] is True
    assert checks["all_vault_preview_only"] is True
    assert checks["all_index_preview_only"] is True
    assert checks["all_receipt_preview_only"] is True
    assert checks["all_approval_preview_only"] is True
    assert checks["all_evidence_preview_only"] is True

    assert checks["no_real_approval_executed"] is True
    assert checks["no_real_policy_change"] is True
    assert checks["no_real_permission_change"] is True
    assert checks["no_real_access_granted"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["no_real_archive_written"] is True
    assert checks["no_real_vault_written"] is True
    assert checks["no_real_expiration_enforced"] is True
    assert checks["no_real_recheck_executed"] is True
    assert checks["no_real_renewal_executed"] is True
    assert checks["no_real_queue_action_executed"] is True
    assert checks["no_real_owner_review_completed"] is True
    assert checks["no_real_owner_approval_executed"] is True
    assert checks["no_real_owner_rejection_executed"] is True
    assert checks["no_real_owner_acknowledgement_executed"] is True
    assert checks["no_real_evidence_revealed"] is True

    assert checks["no_raw_secret_visible"] is True
    assert checks["no_raw_strategy_visible"] is True
    assert checks["no_broker_token_visible"] is True
    assert checks["no_unredacted_sensitive_value_visible"] is True

    assert checks["all_lookup_record_ids_present"] is True
    assert checks["all_detail_drawer_ids_present"] is True
    assert checks["all_owner_review_item_ids_present"] is True
    assert checks["all_queue_item_ids_present"] is True
    assert checks["all_risk_lanes_present"] is True
    assert checks["all_lookup_result_type_present"] is True
    assert checks["all_detail_lookup_allowed"] is True
    assert checks["all_raw_evidence_lookup_blocked"] is True

    assert checks["all_unique_indexes_present"] is True
    assert checks["all_group_indexes_present"] is True
    assert checks["unique_detail_drawer_index_complete"] is True
    assert checks["unique_owner_review_index_complete"] is True
    assert checks["unique_queue_item_index_complete"] is True
    assert checks["risk_lane_coverage"] is True
    assert checks["lookup_preview_checks_pass"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_166_lookup_records_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
    payload = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=True)

    expected_risk_lanes = {
        "critical_evidence_lane",
        "quarantine_evidence_lane",
        "fresh_recheck_evidence_lane",
        "renewal_evidence_lane",
        "monitor_evidence_lane",
    }
    observed_risk_lanes = set()

    for record in payload["lookup_records"]:
        observed_risk_lanes.add(record["risk_lane"])

        assert record["lookup_record_id"].startswith("evidence_drawer_lookup_record_")
        assert record["detail_drawer_id"].startswith("approval_receipt_detail_drawer_")
        assert record["owner_review_item_id"].startswith("approval_receipt_owner_review_preview_")
        assert record["queue_item_id"].startswith("approval_receipt_queue_preview_")
        assert record["expiration_preview_id"].startswith("approval_receipt_expiration_preview_")
        assert record["vault_preview_id"].startswith("approval_receipt_vault_preview_")
        assert record["ledger_index_id"].startswith("approval_receipt_ledger_index_")
        assert record["approval_receipt_preview_id"].startswith("approval_receipt_preview_")
        assert record["approval_gate_id"].startswith("approval_gate_preview_")
        assert record["risk_score_id"].startswith("policy_change_risk_")
        assert record["recommendation_id"].startswith("least_privilege_preview_")

        assert record["scenario_id"]
        assert record["owner_review_category"]
        assert record["owner_review_priority"] in {"critical", "high", "medium", "monitor"}
        assert record["required_owner_action"]
        assert record["owner_review_status"]
        assert record["detail_status"] == "detail_preview_ready"
        assert record["risk_lane"]
        assert record["drawer_title"]
        assert record["drawer_subtitle"]

        assert isinstance(record["section_count"], int)
        assert record["section_count"] >= 6
        assert isinstance(record["detail_card_count"], int)
        assert record["detail_card_count"] >= 6
        assert isinstance(record["redacted_section_count"], int)
        assert record["redacted_section_count"] >= 1
        assert isinstance(record["high_sensitivity_section_count"], int)
        assert record["high_sensitivity_section_count"] >= 1

        assert record["safe_preview_mode"] is True
        assert record["raw_secret_visible"] is False
        assert record["raw_strategy_visible"] is False
        assert record["broker_token_visible"] is False
        assert record["unredacted_sensitive_value_visible"] is False

        assert record["lookup_result_type"] == "detail_drawer_preview"
        assert record["detail_lookup_allowed"] is True
        assert record["raw_evidence_lookup_allowed"] is False
        assert record["source_endpoint"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"

        assert record["simulated_only"] is True
        assert record["lookup_preview_only"] is True
        assert record["detail_preview_only"] is True
        assert record["evidence_drawer_preview_only"] is True
        assert record["owner_review_preview_only"] is True
        assert record["queue_preview_only"] is True
        assert record["renewal_preview_only"] is True
        assert record["recheck_preview_only"] is True
        assert record["expiration_preview_only"] is True
        assert record["vault_preview_only"] is True
        assert record["index_preview_only"] is True
        assert record["receipt_preview_only"] is True
        assert record["approval_preview_only"] is True
        assert record["evidence_preview_only"] is True

        assert record["real_approval_executed"] is False
        assert record["real_policy_change_executed"] is False
        assert record["real_permission_change_executed"] is False
        assert record["real_access_granted"] is False
        assert record["real_enforcement_executed"] is False
        assert record["real_audit_written"] is False
        assert record["real_receipt_written"] is False
        assert record["real_archive_written"] is False
        assert record["real_vault_written"] is False
        assert record["real_expiration_enforced"] is False
        assert record["real_recheck_executed"] is False
        assert record["real_renewal_executed"] is False
        assert record["real_queue_action_executed"] is False
        assert record["real_owner_review_completed"] is False
        assert record["real_owner_approval_executed"] is False
        assert record["real_owner_rejection_executed"] is False
        assert record["real_owner_acknowledgement_executed"] is False
        assert record["real_evidence_revealed"] is False

    assert expected_risk_lanes.issubset(observed_risk_lanes)


def test_pack_166_indexes_lookup_records_correctly():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
    payload = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=True)

    records = payload["lookup_records"]
    indexes = payload["indexes"]
    first = records[0]

    assert indexes["by_detail_drawer_id"][first["detail_drawer_id"]]["lookup_record_id"] == first["lookup_record_id"]
    assert indexes["by_owner_review_item_id"][first["owner_review_item_id"]]["lookup_record_id"] == first["lookup_record_id"]
    assert indexes["by_queue_item_id"][first["queue_item_id"]]["lookup_record_id"] == first["lookup_record_id"]

    assert any(
        row["lookup_record_id"] == first["lookup_record_id"]
        for row in indexes["by_scenario_id"][first["scenario_id"]]
    )
    assert any(
        row["lookup_record_id"] == first["lookup_record_id"]
        for row in indexes["by_owner_review_category"][first["owner_review_category"]]
    )
    assert any(
        row["lookup_record_id"] == first["lookup_record_id"]
        for row in indexes["by_required_owner_action"][first["required_owner_action"]]
    )
    assert any(
        row["lookup_record_id"] == first["lookup_record_id"]
        for row in indexes["by_owner_review_priority"][first["owner_review_priority"]]
    )
    assert any(
        row["lookup_record_id"] == first["lookup_record_id"]
        for row in indexes["by_detail_status"][first["detail_status"]]
    )
    assert any(
        row["lookup_record_id"] == first["lookup_record_id"]
        for row in indexes["by_risk_lane"][first["risk_lane"]]
    )


def test_pack_166_lookup_preview_examples_return_expected_shapes():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
    payload = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=True)

    examples = payload["lookup_query_examples"]
    preview = payload["lookup_preview"]
    checks = payload["lookup_preview_checks"]

    assert examples["detail_drawer_id"]
    assert examples["owner_review_item_id"]
    assert examples["queue_item_id"]
    assert examples["scenario_id"]
    assert examples["owner_review_category"]
    assert examples["required_owner_action"]
    assert examples["owner_review_priority"]
    assert examples["detail_status"]
    assert examples["risk_lane"]

    assert isinstance(preview["by_detail_drawer_id"], dict)
    assert isinstance(preview["by_owner_review_item_id"], dict)
    assert isinstance(preview["by_queue_item_id"], dict)
    assert isinstance(preview["by_scenario_id"], list)
    assert isinstance(preview["by_owner_review_category"], list)
    assert isinstance(preview["by_required_owner_action"], list)
    assert isinstance(preview["by_owner_review_priority"], list)
    assert isinstance(preview["by_detail_status"], list)
    assert isinstance(preview["by_risk_lane"], list)

    assert all(checks.values())


def test_pack_166_lookup_keys_are_documented():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
    payload = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=True)

    lookup_keys = payload["lookup_keys"]

    required_keys = {
        "by_detail_drawer_id",
        "by_owner_review_item_id",
        "by_queue_item_id",
        "by_scenario_id",
        "by_owner_review_category",
        "by_required_owner_action",
        "by_owner_review_priority",
        "by_detail_status",
        "by_risk_lane",
    }

    assert required_keys.issubset(set(lookup_keys.keys()))

    for key, meta in lookup_keys.items():
        assert meta["label"]
        assert meta["description"]
        assert isinstance(meta["unique"], bool)


def test_pack_166_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")

    bridge = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 166
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"
    assert bridge["readiness_score"] == 100
    assert bridge["lookup_record_count"] >= 9
    assert bridge["detail_drawer_count"] >= 9
    assert bridge["lookup_key_count"] >= 9

    assert bridge["simulated_only"] is True
    assert bridge["lookup_preview_only"] is True
    assert bridge["detail_preview_only"] is True
    assert bridge["evidence_drawer_preview_only"] is True
    assert bridge["real_evidence_revealed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_quick_action()
    assert action["id"] == "policy_change_approval_receipt_evidence_drawer_lookup"
    assert action["href"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"
    assert action["simulated_only"] is True
    assert action["lookup_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_evidence_drawer_lookup_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_evidence_drawer_lookup"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"
    assert section["simulated_only"] is True
    assert section["lookup_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_166_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge")

    bridge = status.build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_status_bridge()
    assert bridge["pack_number"] == 166
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"
    assert bridge["readiness_score"] == 100


def test_pack_166_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_quick_action")
    assert hasattr(qa, "append_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_quick_action")

    action = qa.build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_quick_action()
    assert action["id"] == "policy_change_approval_receipt_evidence_drawer_lookup"
    assert action["href"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"

    actions = qa.append_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_evidence_drawer_lookup" for item in actions)


def test_pack_166_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_unified_section")
    assert hasattr(unified, "build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_html_section")
    assert hasattr(unified, "append_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_section")

    section = unified.build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_evidence_drawer_lookup"
    assert section["href"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"

    sections = unified.append_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_evidence_drawer_lookup" for item in sections)


def test_pack_166_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json" in app_text
    assert "tower_policy_change_approval_receipt_evidence_drawer_lookup_json" in app_text
    assert "_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json" in route_text
    assert "_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_route_guard" in route_text


def test_pack_166_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_evidence_drawer_lookup")
    payload_text = str(mod.build_policy_change_approval_receipt_evidence_drawer_lookup_payload(force_refresh=True)).lower()

    forbidden_fragments = [
        "sk_live_",
        "sk_test_",
        "github_pat_",
        "ghp_",
        "xoxb-",
        "aws_secret_access_key",
        "private_key-----",
        "broker_token_value",
        "api_secret_value",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in payload_text
