
"""
PACK 168 fast test - Evidence Drawer Saved Views / Filter Presets.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_168_payload_ready_and_saved_view_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")
    payload = mod.build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=True)

    assert payload["pack_number"] == 168
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json"

    assert payload["simulated_only"] is True
    assert payload["saved_view_preview_only"] is True
    assert payload["filter_preset_preview_only"] is True
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
    assert payload["real_saved_view_written"] is False
    assert payload["real_user_preference_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["saved_view_count"] >= 8
    assert summary["filter_record_count"] >= 9
    assert summary["non_empty_view_count"] >= 1
    assert "all_evidence_drawers" in summary["observed_saved_views"]
    assert "critical_owner_review" in summary["observed_saved_views"]
    assert "quarantine_review" in summary["observed_saved_views"]
    assert "fresh_recheck" in summary["observed_saved_views"]
    assert "renewal_review" in summary["observed_saved_views"]
    assert "monitor_only" in summary["observed_saved_views"]
    assert "high_sensitivity_redacted" in summary["observed_saved_views"]
    assert "safe_preview_only" in summary["observed_saved_views"]

    checks = payload["readiness_checks"]
    assert checks["pack_167_ready"] is True
    assert checks["has_saved_views"] is True
    assert checks["all_expected_saved_views_present"] is True
    assert checks["saved_view_count_matches_blueprints"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_saved_view_preview_only"] is True
    assert checks["all_filter_preset_preview_only"] is True
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
    assert checks["no_real_saved_view_written"] is True
    assert checks["no_real_user_preference_written"] is True

    assert checks["all_save_actions_blocked"] is True
    assert checks["all_set_default_actions_blocked"] is True
    assert checks["all_share_actions_blocked"] is True
    assert checks["all_raw_evidence_reveal_blocked"] is True
    assert checks["all_raw_evidence_lookup_blocked"] is True

    assert checks["all_saved_view_ids_present"] is True
    assert checks["all_saved_view_preview_ids_present"] is True
    assert checks["all_view_result_type_present"] is True
    assert checks["all_views_have_status"] is True
    assert checks["non_empty_views_present"] is True
    assert checks["all_evidence_drawers_view_present"] is True
    assert checks["critical_owner_review_view_present"] is True
    assert checks["quarantine_review_view_present"] is True
    assert checks["fresh_recheck_view_present"] is True
    assert checks["renewal_review_view_present"] is True
    assert checks["monitor_only_view_present"] is True
    assert checks["high_sensitivity_view_present"] is True
    assert checks["safe_preview_view_present"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_168_saved_views_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")
    payload = mod.build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=True)

    expected_views = {
        "all_evidence_drawers",
        "critical_owner_review",
        "quarantine_review",
        "fresh_recheck",
        "renewal_review",
        "monitor_only",
        "high_sensitivity_redacted",
        "safe_preview_only",
    }
    observed_views = set()

    for view in payload["saved_views"]:
        observed_views.add(view["saved_view_id"])

        assert view["saved_view_preview_id"].startswith("evidence_drawer_saved_view_")
        assert view["saved_view_id"]
        assert view["label"]
        assert view["description"]
        assert view["view_priority"] in {"critical", "high", "medium", "standard", "monitor"}
        assert isinstance(view["requires_owner_review"], bool)
        assert isinstance(view["filters"], dict)
        assert isinstance(view["matched_record_count"], int)
        assert isinstance(view["filter_record_ids"], list)
        assert isinstance(view["detail_drawer_ids"], list)
        assert isinstance(view["risk_lane_counts"], dict)
        assert isinstance(view["owner_review_category_counts"], dict)
        assert isinstance(view["owner_review_priority_counts"], dict)
        assert isinstance(view["sensitivity_redaction_counts"], dict)
        assert isinstance(view["empty_view"], bool)
        assert view["view_status"] == "saved_view_preview_ready"
        assert view["view_result_type"] == "evidence_drawer_saved_view_preview"

        assert view["save_action_allowed_now"] is False
        assert view["set_default_allowed_now"] is False
        assert view["share_view_allowed_now"] is False
        assert view["raw_evidence_reveal_allowed"] is False
        assert view["raw_evidence_lookup_allowed"] is False

        assert view["simulated_only"] is True
        assert view["saved_view_preview_only"] is True
        assert view["filter_preset_preview_only"] is True
        assert view["filter_preview_only"] is True
        assert view["search_facet_preview_only"] is True
        assert view["lookup_preview_only"] is True
        assert view["detail_preview_only"] is True
        assert view["evidence_drawer_preview_only"] is True
        assert view["owner_review_preview_only"] is True
        assert view["queue_preview_only"] is True
        assert view["renewal_preview_only"] is True
        assert view["recheck_preview_only"] is True
        assert view["expiration_preview_only"] is True
        assert view["vault_preview_only"] is True
        assert view["index_preview_only"] is True
        assert view["receipt_preview_only"] is True
        assert view["approval_preview_only"] is True
        assert view["evidence_preview_only"] is True

        assert view["real_approval_executed"] is False
        assert view["real_policy_change_executed"] is False
        assert view["real_permission_change_executed"] is False
        assert view["real_access_granted"] is False
        assert view["real_enforcement_executed"] is False
        assert view["real_audit_written"] is False
        assert view["real_receipt_written"] is False
        assert view["real_archive_written"] is False
        assert view["real_vault_written"] is False
        assert view["real_expiration_enforced"] is False
        assert view["real_recheck_executed"] is False
        assert view["real_renewal_executed"] is False
        assert view["real_queue_action_executed"] is False
        assert view["real_owner_review_completed"] is False
        assert view["real_owner_approval_executed"] is False
        assert view["real_owner_rejection_executed"] is False
        assert view["real_owner_acknowledgement_executed"] is False
        assert view["real_evidence_revealed"] is False
        assert view["real_saved_view_written"] is False
        assert view["real_user_preference_written"] is False

    assert expected_views.issubset(observed_views)


def test_pack_168_specific_saved_view_filters_match_expected_records():
    mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")
    payload = mod.build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=True)

    views = payload["saved_view_preview"]

    all_view = views["all_evidence_drawers"]
    assert all_view["filters"] == {}
    assert all_view["matched_record_count"] == payload["summary"]["filter_record_count"]

    critical = views["critical_owner_review"]
    assert critical["filters"] == {"owner_review_category": ["critical_owner_recheck"]}
    assert "critical_owner_recheck" in critical["owner_review_category_counts"]

    quarantine = views["quarantine_review"]
    assert quarantine["filters"] == {"owner_review_category": ["quarantine_owner_recheck"]}
    assert "quarantine_owner_recheck" in quarantine["owner_review_category_counts"]

    fresh = views["fresh_recheck"]
    assert fresh["filters"] == {"owner_review_category": ["fresh_recheck_review"]}
    assert "fresh_recheck_review" in fresh["owner_review_category_counts"]

    renewal = views["renewal_review"]
    assert renewal["filters"] == {"owner_review_category": ["renewal_review"]}
    assert "renewal_review" in renewal["owner_review_category_counts"]

    monitor = views["monitor_only"]
    assert monitor["filters"] == {"owner_review_category": ["monitor_acknowledgement"]}
    assert "monitor_acknowledgement" in monitor["owner_review_category_counts"]

    redacted = views["high_sensitivity_redacted"]
    assert redacted["filters"] == {"sensitivity_redaction": ["redacted_high_sensitivity"]}

    safe_only = views["safe_preview_only"]
    assert safe_only["filters"] == {"safety_visibility": ["safe_preview_only"]}
    assert safe_only["matched_record_count"] == payload["summary"]["filter_record_count"]


def test_pack_168_preset_indexes_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")
    payload = mod.build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=True)

    indexes = payload["preset_indexes"]
    assert indexes["by_saved_view_id"]
    assert indexes["by_view_priority"]
    assert indexes["by_requires_owner_review"]
    assert indexes["by_view_status"]

    assert "all_evidence_drawers" in indexes["by_saved_view_id"]
    assert "critical_owner_review" in indexes["by_saved_view_id"]
    assert "saved_view_preview_ready" in indexes["by_view_status"]
    assert "owner_review_required" in indexes["by_requires_owner_review"]
    assert "owner_review_not_required" in indexes["by_requires_owner_review"]


def test_pack_168_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")

    bridge = mod.build_policy_change_approval_receipt_saved_views_filter_presets_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 168
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"
    assert bridge["readiness_score"] == 100
    assert bridge["saved_view_count"] >= 8
    assert bridge["filter_record_count"] >= 9

    assert bridge["simulated_only"] is True
    assert bridge["saved_view_preview_only"] is True
    assert bridge["filter_preset_preview_only"] is True
    assert bridge["filter_preview_only"] is True
    assert bridge["real_saved_view_written"] is False
    assert bridge["real_user_preference_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_saved_views_filter_presets_quick_action()
    assert action["id"] == "policy_change_approval_receipt_saved_views_filter_presets"
    assert action["href"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"
    assert action["simulated_only"] is True
    assert action["saved_view_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_saved_views_filter_presets_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_saved_views_filter_presets"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"
    assert section["simulated_only"] is True
    assert section["saved_view_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_168_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_status_bridge")

    bridge = status.build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_status_bridge()
    assert bridge["pack_number"] == 168
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"
    assert bridge["readiness_score"] == 100


def test_pack_168_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_quick_action")
    assert hasattr(qa, "append_pack_168_policy_change_approval_receipt_saved_views_filter_presets_quick_action")

    action = qa.build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_quick_action()
    assert action["id"] == "policy_change_approval_receipt_saved_views_filter_presets"
    assert action["href"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"

    actions = qa.append_pack_168_policy_change_approval_receipt_saved_views_filter_presets_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_saved_views_filter_presets" for item in actions)


def test_pack_168_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_unified_section")
    assert hasattr(unified, "build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_html_section")
    assert hasattr(unified, "append_pack_168_policy_change_approval_receipt_saved_views_filter_presets_section")

    section = unified.build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_saved_views_filter_presets"
    assert section["href"] == "/tower/policy-change-approval-receipt-saved-views-filter-presets.json"

    sections = unified.append_pack_168_policy_change_approval_receipt_saved_views_filter_presets_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_saved_views_filter_presets" for item in sections)


def test_pack_168_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-saved-views-filter-presets.json" in app_text
    assert "tower_policy_change_approval_receipt_saved_views_filter_presets_json" in app_text
    assert "_pack_168_policy_change_approval_receipt_saved_views_filter_presets_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-saved-views-filter-presets.json" in route_text
    assert "_pack_168_policy_change_approval_receipt_saved_views_filter_presets_route_guard" in route_text


def test_pack_168_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_saved_views_filter_presets")
    payload_text = str(mod.build_policy_change_approval_receipt_saved_views_filter_presets_payload(force_refresh=True)).lower()

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
