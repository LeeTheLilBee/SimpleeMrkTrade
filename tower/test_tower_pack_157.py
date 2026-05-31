
"""
PACK 157 fast test - Least-Privilege Recommendation Engine foundation.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_157_payload_ready_and_recommendation_only():
    mod = importlib.import_module("tower.least_privilege_recommendation_engine")
    payload = mod.build_least_privilege_recommendation_payload(force_refresh=True)

    assert payload["pack_number"] == 157
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/least-privilege-recommendations.json"
    assert payload["source_endpoint"] == "/tower/policy-renewal-recheck-queue.json"

    assert payload["simulated_only"] is True
    assert payload["recommendation_only"] is True
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_renewal_executed"] is False
    assert payload["real_recheck_executed"] is False
    assert payload["real_expiration_enforced"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["recommendation_count"] >= 9
    assert summary["owner_review_recommendation_count"] >= 1
    assert summary["step_up_recommendation_count"] >= 1
    assert summary["no_access_recommendation_count"] >= 1
    assert summary["redaction_recommendation_count"] >= 1
    assert summary["monitor_recommendation_count"] >= 1
    assert summary["access_level_count"] >= 6
    assert summary["family_count"] >= 6

    checks = payload["readiness_checks"]
    assert checks["pack_156_ready"] is True
    assert checks["has_recommendations"] is True
    assert checks["recommendation_count_matches_queue"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_recommendation_only"] is True
    assert checks["no_real_permission_change"] is True
    assert checks["no_real_access_granted"] is True
    assert checks["no_real_renewal_executed"] is True
    assert checks["no_real_recheck_executed"] is True
    assert checks["no_real_expiration_enforced"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["all_recommendation_ids_present"] is True
    assert checks["all_access_levels_present"] is True
    assert checks["all_actions_present"] is True
    assert checks["all_reasons_present"] is True
    assert checks["all_reduce_or_safe_monitor"] is True
    assert checks["no_new_access_grants"] is True
    assert checks["no_permission_mutations"] is True
    assert checks["owner_review_recommendations_present"] is True
    assert checks["step_up_recommendations_present"] is True
    assert checks["no_access_recommendations_present"] is True
    assert checks["redaction_recommendations_present"] is True
    assert checks["monitor_recommendations_present"] is True
    assert checks["required_access_level_coverage"] is True
    assert checks["required_family_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_157_recommendations_have_required_fields():
    mod = importlib.import_module("tower.least_privilege_recommendation_engine")
    payload = mod.build_least_privilege_recommendation_payload(force_refresh=True)

    required_access_levels = {
        "none",
        "deny_only",
        "containment_only",
        "redacted_summary_only",
        "step_up_challenge_only",
        "monitor_read_only",
    }
    observed_access_levels = set()

    required_families = {
        "critical_stop",
        "containment",
        "deny",
        "privacy",
        "step_up",
        "monitor",
    }
    observed_families = set()

    for item in payload["recommendations"]:
        observed_access_levels.add(item["recommended_access_level"])
        observed_families.add(item["recommendation_family"])

        assert item["recommendation_id"].startswith("least_privilege_preview_")
        assert item["recheck_item_id"].startswith("recheck_preview_")
        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["receipt_preview_id"].startswith("receipt_preview_")
        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert item["severity"]
        assert item["bucket"]
        assert item["lane"]
        assert item["expiration_state"] in {"fresh", "warning", "expired"}
        assert item["priority"]
        assert isinstance(item["priority_rank"], int)
        assert item["risk_label"]
        assert item["recommended_access_level"]
        assert isinstance(item["recommended_access_rank"], int)
        assert item["recommended_action"]
        assert item["recommendation_family"]
        assert isinstance(item["safe_capability_scope"], list)
        assert isinstance(item["blocked_capabilities"], list)
        assert item["owner_gate"]
        assert isinstance(item["step_up_required"], bool)
        assert isinstance(item["fresh_recheck_required"], bool)
        assert isinstance(item["renewal_allowed"], bool)
        assert isinstance(item["requires_owner_review"], bool)
        assert item["would_reduce_access"] is True
        assert item["would_grant_new_access"] is False
        assert item["would_mutate_permissions"] is False
        assert item["would_execute_action"] is False
        assert item["least_privilege_reason"]
        assert item["owner_prompt"]
        assert item["soulaana_recommendation_translation"]
        assert item["source_endpoint"] == "/tower/policy-renewal-recheck-queue.json"

        assert item["simulated_only"] is True
        assert item["recommendation_only"] is True
        assert item["real_permission_change_executed"] is False
        assert item["real_access_granted"] is False
        assert item["real_renewal_executed"] is False
        assert item["real_recheck_executed"] is False
        assert item["real_expiration_enforced"] is False
        assert item["real_enforcement_executed"] is False
        assert item["real_audit_written"] is False
        assert item["real_receipt_written"] is False

    assert required_access_levels.issubset(observed_access_levels)
    assert required_families.issubset(observed_families)


def test_pack_157_decision_specific_recommendations_are_least_privilege():
    mod = importlib.import_module("tower.least_privilege_recommendation_engine")
    payload = mod.build_least_privilege_recommendation_payload(force_refresh=True)

    by_decision = payload["indexes"]["by_decision"]

    fail_closed = by_decision["fail_closed"][0]
    assert fail_closed["recommended_access_level"] == "none"
    assert fail_closed["recommended_action"] == "owner_recheck_no_access"
    assert fail_closed["step_up_required"] is True
    assert fail_closed["fresh_recheck_required"] is True

    quarantine = by_decision["quarantine"][0]
    assert quarantine["recommended_access_level"] == "containment_only"
    assert quarantine["recommended_action"] == "keep_quarantined_until_rechecked"

    step_up = by_decision["step_up"][0]
    assert step_up["recommended_access_level"] == "step_up_challenge_only"
    assert step_up["recommended_action"] == "issue_fresh_step_up_challenge_preview"

    redact = by_decision["redact"][0]
    assert redact["recommended_access_level"] == "redacted_summary_only"
    assert redact["recommended_action"] == "keep_redacted_prepare_privacy_review"

    allow = by_decision["allow"][0]
    assert allow["recommended_access_level"] == "monitor_read_only"
    assert allow["recommended_action"] == "continue_monitor_only_read_only"

    for deny in by_decision["deny"]:
        assert deny["recommended_access_level"] == "deny_only"
        assert deny["recommended_action"] == "maintain_deny_prepare_limited_renewal_review"


def test_pack_157_indexes_and_specialized_lists_are_present():
    mod = importlib.import_module("tower.least_privilege_recommendation_engine")
    payload = mod.build_least_privilege_recommendation_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_access_level"]
    assert indexes["by_action"]
    assert indexes["by_family"]
    assert indexes["by_risk"]
    assert indexes["by_decision"]

    assert payload["owner_review_recommendations"]
    assert payload["step_up_recommendations"]
    assert payload["no_access_recommendations"]
    assert payload["redaction_recommendations"]
    assert payload["monitor_recommendations"]

    for item in payload["owner_review_recommendations"]:
        assert item["requires_owner_review"] is True

    for item in payload["step_up_recommendations"]:
        assert item["step_up_required"] is True

    for item in payload["no_access_recommendations"]:
        assert item["recommended_access_level"] in {"none", "deny_only", "containment_only"}

    for item in payload["redaction_recommendations"]:
        assert item["recommended_access_level"] == "redacted_summary_only"

    for item in payload["monitor_recommendations"]:
        assert item["recommended_access_level"] == "monitor_read_only"

    top = payload["recommendations"][0]
    assert top["priority"] == "critical"
    assert top["recommended_access_level"] == "none"


def test_pack_157_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.least_privilege_recommendation_engine")

    bridge = mod.build_least_privilege_recommendation_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 157
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/least-privilege-recommendations.json"
    assert bridge["readiness_score"] == 100
    assert bridge["recommendation_count"] >= 9
    assert bridge["owner_review_recommendation_count"] >= 1
    assert bridge["step_up_recommendation_count"] >= 1
    assert bridge["no_access_recommendation_count"] >= 1
    assert bridge["redaction_recommendation_count"] >= 1
    assert bridge["monitor_recommendation_count"] >= 1
    assert bridge["simulated_only"] is True
    assert bridge["recommendation_only"] is True
    assert bridge["real_permission_change_executed"] is False
    assert bridge["real_access_granted"] is False
    assert bridge["real_renewal_executed"] is False
    assert bridge["real_recheck_executed"] is False
    assert bridge["real_expiration_enforced"] is False
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_least_privilege_recommendation_quick_action()
    assert action["id"] == "least_privilege_recommendations"
    assert action["href"] == "/tower/least-privilege-recommendations.json"
    assert action["simulated_only"] is True
    assert action["recommendation_only"] is True

    section = mod.build_least_privilege_recommendation_unified_owner_section()
    assert section["section_id"] == "least_privilege_recommendations"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/least-privilege-recommendations.json"
    assert section["simulated_only"] is True
    assert section["recommendation_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_157_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_157_least_privilege_recommendation_status_bridge")

    bridge = status.build_pack_157_least_privilege_recommendation_status_bridge()
    assert bridge["pack_number"] == 157
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/least-privilege-recommendations.json"
    assert bridge["readiness_score"] == 100


def test_pack_157_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_157_least_privilege_recommendation_quick_action")
    assert hasattr(qa, "append_pack_157_least_privilege_recommendation_quick_action")

    action = qa.build_pack_157_least_privilege_recommendation_quick_action()
    assert action["id"] == "least_privilege_recommendations"
    assert action["href"] == "/tower/least-privilege-recommendations.json"

    actions = qa.append_pack_157_least_privilege_recommendation_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "least_privilege_recommendations" for item in actions)


def test_pack_157_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_157_least_privilege_recommendation_unified_section")
    assert hasattr(unified, "build_pack_157_least_privilege_recommendation_html_section")
    assert hasattr(unified, "append_pack_157_least_privilege_recommendation_section")

    section = unified.build_pack_157_least_privilege_recommendation_unified_section()
    assert section["section_id"] == "least_privilege_recommendations"
    assert section["href"] == "/tower/least-privilege-recommendations.json"

    sections = unified.append_pack_157_least_privilege_recommendation_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "least_privilege_recommendations" for item in sections)


def test_pack_157_web_route_present_in_app_file_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/least-privilege-recommendations.json" in app_text
    assert "tower_least_privilege_recommendations_json" in app_text
    assert "_pack_157_least_privilege_recommendation_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "_pack_157_least_privilege_recommendation_route_guard" in route_text
    assert "/tower/least-privilege-recommendations.json" in route_text


def test_pack_157_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.least_privilege_recommendation_engine")
    payload_text = str(mod.build_least_privilege_recommendation_payload(force_refresh=True)).lower()

    forbidden_fragments = [
        "sk-",
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
