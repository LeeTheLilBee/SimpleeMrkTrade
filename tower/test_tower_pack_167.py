
"""
PACK 167 fast test - Evidence Drawer Filter Lanes / Search Facets.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_167_payload_ready_and_filter_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")
    payload = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=True)

    assert payload["pack_number"] == 167
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"

    assert payload["simulated_only"] is True
    assert payload["filter_preview_only"] is True
    assert payload["search_facet_preview_only"] is True
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
    assert summary["filter_record_count"] >= 9
    assert summary["lookup_record_count"] >= 9
    assert summary["filter_lane_count"] >= 8
    assert summary["facet_count"] >= 8
    assert len(summary["risk_lane_counts"]) >= 5
    assert "safe_preview_only" in summary["safety_visibility_counts"]

    checks = payload["readiness_checks"]
    assert checks["pack_166_ready"] is True
    assert checks["has_filter_records"] is True
    assert checks["filter_count_matches_lookup_records"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_filter_preview_only"] is True
    assert checks["all_search_facet_preview_only"] is True
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
    assert checks["all_raw_evidence_lookup_blocked"] is True
    assert checks["all_raw_evidence_reveal_blocked"] is True

    assert checks["all_filter_record_ids_present"] is True
    assert checks["all_lookup_record_ids_present"] is True
    assert checks["all_detail_drawer_ids_present"] is True
    assert checks["all_facet_results_allowed"] is True
    assert checks["all_filter_result_type_present"] is True
    assert checks["all_filter_lanes_present"] is True
    assert checks["all_facets_have_options"] is True
    assert checks["all_facet_options_safe"] is True
    assert checks["risk_lane_coverage"] is True
    assert checks["sensitivity_redaction_present"] is True
    assert checks["safety_visibility_present"] is True
    assert checks["facet_preview_checks_pass"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_167_filter_records_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")
    payload = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=True)

    expected_risk_lanes = {
        "critical_evidence_lane",
        "quarantine_evidence_lane",
        "fresh_recheck_evidence_lane",
        "renewal_evidence_lane",
        "monitor_evidence_lane",
    }
    observed_risk_lanes = set()

    for record in payload["filter_records"]:
        observed_risk_lanes.add(record["risk_lane"])

        assert record["filter_record_id"].startswith("evidence_drawer_filter_record_")
        assert record["lookup_record_id"].startswith("evidence_drawer_lookup_record_")
        assert record["detail_drawer_id"].startswith("approval_receipt_detail_drawer_")
        assert record["owner_review_item_id"].startswith("approval_receipt_owner_review_preview_")
        assert record["queue_item_id"].startswith("approval_receipt_queue_preview_")

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

        assert record["sensitivity_redaction"]
        assert record["safety_visibility"] == "safe_preview_only"

        assert record["safe_preview_mode"] is True
        assert record["raw_secret_visible"] is False
        assert record["raw_strategy_visible"] is False
        assert record["broker_token_visible"] is False
        assert record["unredacted_sensitive_value_visible"] is False
        assert record["raw_evidence_lookup_allowed"] is False

        assert record["filter_result_type"] == "evidence_drawer_filter_preview"
        assert record["facet_result_allowed"] is True
        assert record["raw_evidence_reveal_allowed"] is False
        assert record["source_endpoint"] == "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json"

        assert record["simulated_only"] is True
        assert record["filter_preview_only"] is True
        assert record["search_facet_preview_only"] is True
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


def test_pack_167_facets_and_filter_indexes_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")
    payload = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=True)

    expected_lanes = {
        "owner_review_category",
        "required_owner_action",
        "owner_review_priority",
        "risk_lane",
        "detail_status",
        "scenario_id",
        "sensitivity_redaction",
        "safety_visibility",
    }

    assert expected_lanes.issubset(set(payload["facets"].keys()))

    for lane_id, facet in payload["facets"].items():
        assert facet["lane_id"] == lane_id
        assert facet["lane_label"]
        assert facet["lane_description"]
        assert facet["lane_type"]
        assert facet["source_field"]
        assert facet["option_count"] >= 1
        assert facet["record_count"] >= 1
        assert facet["safe_for_preview"] is True
        assert facet["raw_evidence_reveal_allowed"] is False
        assert facet["simulated_only"] is True
        assert facet["filter_preview_only"] is True
        assert facet["search_facet_preview_only"] is True

        for option in facet["options"]:
            assert option["facet_option_id"].startswith("evidence_drawer_facet_")
            assert option["lane_id"] == lane_id
            assert option["value"]
            assert option["label"]
            assert option["count"] >= 1
            assert option["filter_record_ids"]
            assert option["detail_drawer_ids"]
            assert option["safe_for_preview"] is True
            assert option["raw_evidence_reveal_allowed"] is False

    indexes = payload["filter_indexes"]
    assert "by_owner_review_category" in indexes
    assert "by_required_owner_action" in indexes
    assert "by_owner_review_priority" in indexes
    assert "by_risk_lane" in indexes
    assert "by_detail_status" in indexes
    assert "by_scenario_id" in indexes
    assert "by_sensitivity_redaction" in indexes
    assert "by_safety_visibility" in indexes


def test_pack_167_filter_preview_has_one_option_per_lane():
    mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")
    payload = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=True)

    preview = payload["filter_preview"]
    expected_lanes = set(payload["filter_lanes"].keys())

    assert expected_lanes.issubset(set(preview.keys()))

    for lane_id in expected_lanes:
        option = preview[lane_id]
        assert isinstance(option, dict)
        assert option["lane_id"] == lane_id
        assert option["count"] >= 1
        assert option["safe_for_preview"] is True
        assert option["raw_evidence_reveal_allowed"] is False


def test_pack_167_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")

    bridge = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 167
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"
    assert bridge["readiness_score"] == 100
    assert bridge["filter_record_count"] >= 9
    assert bridge["lookup_record_count"] >= 9
    assert bridge["filter_lane_count"] >= 8
    assert bridge["facet_count"] >= 8

    assert bridge["simulated_only"] is True
    assert bridge["filter_preview_only"] is True
    assert bridge["search_facet_preview_only"] is True
    assert bridge["lookup_preview_only"] is True
    assert bridge["real_evidence_revealed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_quick_action()
    assert action["id"] == "policy_change_approval_receipt_filter_lanes_search_facets"
    assert action["href"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"
    assert action["simulated_only"] is True
    assert action["filter_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_filter_lanes_search_facets_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_filter_lanes_search_facets"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"
    assert section["simulated_only"] is True
    assert section["filter_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_167_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge")

    bridge = status.build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_status_bridge()
    assert bridge["pack_number"] == 167
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"
    assert bridge["readiness_score"] == 100


def test_pack_167_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_quick_action")
    assert hasattr(qa, "append_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_quick_action")

    action = qa.build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_quick_action()
    assert action["id"] == "policy_change_approval_receipt_filter_lanes_search_facets"
    assert action["href"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"

    actions = qa.append_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_filter_lanes_search_facets" for item in actions)


def test_pack_167_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_unified_section")
    assert hasattr(unified, "build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_html_section")
    assert hasattr(unified, "append_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_section")

    section = unified.build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_filter_lanes_search_facets"
    assert section["href"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"

    sections = unified.append_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_filter_lanes_search_facets" for item in sections)


def test_pack_167_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json" in app_text
    assert "tower_policy_change_approval_receipt_filter_lanes_search_facets_json" in app_text
    assert "_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json" in route_text
    assert "_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_route_guard" in route_text


def test_pack_167_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_filter_lanes_search_facets")
    payload_text = str(mod.build_policy_change_approval_receipt_filter_lanes_search_facets_payload(force_refresh=True)).lower()

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
