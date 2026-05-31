
"""
PACK 158 fast test - Policy Change Risk Score foundation.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_158_payload_ready_and_scoring_only():
    mod = importlib.import_module("tower.policy_change_risk_score")
    payload = mod.build_policy_change_risk_score_payload(force_refresh=True)

    assert payload["pack_number"] == 158
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-risk-score.json"
    assert payload["source_endpoint"] == "/tower/least-privilege-recommendations.json"

    assert payload["simulated_only"] is True
    assert payload["scoring_only"] is True
    assert payload["recommendation_only"] is True
    assert payload["real_policy_change_executed"] is False
    assert payload["real_permission_change_executed"] is False
    assert payload["real_access_granted"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["risk_item_count"] >= 9
    assert summary["critical_count"] >= 1
    assert summary["high_count"] >= 1
    assert summary["medium_count"] >= 1
    assert summary["low_count"] >= 1
    assert summary["monitor_count"] >= 1
    assert summary["owner_review_required_count"] >= 1
    assert summary["blocked_from_auto_change_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_157_ready"] is True
    assert checks["has_risk_items"] is True
    assert checks["risk_count_matches_recommendations"] is True
    assert checks["all_simulated_only"] is True
    assert checks["all_scoring_only"] is True
    assert checks["all_recommendation_only"] is True
    assert checks["no_real_policy_change"] is True
    assert checks["no_real_permission_change"] is True
    assert checks["no_real_access_granted"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["all_risk_ids_present"] is True
    assert checks["all_scores_present"] is True
    assert checks["all_bands_present"] is True
    assert checks["all_factors_present"] is True
    assert checks["critical_items_present"] is True
    assert checks["high_items_present"] is True
    assert checks["medium_items_present"] is True
    assert checks["low_items_present"] is True
    assert checks["monitor_items_present"] is True
    assert checks["owner_review_required_present"] is True
    assert checks["blocked_from_auto_change_present"] is True
    assert checks["required_band_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_158_risk_items_have_required_fields():
    mod = importlib.import_module("tower.policy_change_risk_score")
    payload = mod.build_policy_change_risk_score_payload(force_refresh=True)

    observed_bands = set()

    for item in payload["risk_items"]:
        observed_bands.add(item["risk_band"])

        assert item["risk_score_id"].startswith("policy_change_risk_")
        assert item["recommendation_id"].startswith("least_privilege_preview_")
        assert item["recheck_item_id"].startswith("recheck_preview_")
        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["receipt_preview_id"].startswith("receipt_preview_")
        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["decision"]
        assert item["recommended_access_level"]
        assert item["recommended_action"]
        assert item["recommendation_family"]

        assert isinstance(item["risk_score"], int)
        assert 0 <= item["risk_score"] <= 100
        assert item["risk_band"] in {"critical", "high", "medium", "low", "monitor"}
        assert isinstance(item["risk_factors"], list)
        assert len(item["risk_factors"]) >= 1
        assert isinstance(item["factor_count"], int)
        assert item["factor_count"] == len(item["risk_factors"])

        assert isinstance(item["requires_owner_review"], bool)
        assert isinstance(item["step_up_required"], bool)
        assert isinstance(item["fresh_recheck_required"], bool)
        assert isinstance(item["would_reduce_access"], bool)
        assert item["would_grant_new_access"] is False
        assert item["would_mutate_permissions"] is False
        assert item["would_execute_action"] is False

        assert item["least_privilege_reason"]
        assert item["owner_prompt"]
        assert item["soulaana_risk_translation"]
        assert item["source_endpoint"] == "/tower/least-privilege-recommendations.json"

        assert item["simulated_only"] is True
        assert item["scoring_only"] is True
        assert item["recommendation_only"] is True
        assert item["real_policy_change_executed"] is False
        assert item["real_permission_change_executed"] is False
        assert item["real_access_granted"] is False
        assert item["real_enforcement_executed"] is False
        assert item["real_audit_written"] is False
        assert item["real_receipt_written"] is False

    assert {"critical", "high", "medium", "low", "monitor"}.issubset(observed_bands)


def test_pack_158_decision_specific_risk_bands():
    mod = importlib.import_module("tower.policy_change_risk_score")
    payload = mod.build_policy_change_risk_score_payload(force_refresh=True)

    by_decision = payload["indexes"]["by_decision"]

    fail_closed = by_decision["fail_closed"][0]
    assert fail_closed["risk_band"] == "critical"
    assert fail_closed["risk_score"] >= 85

    quarantine = by_decision["quarantine"][0]
    assert quarantine["risk_band"] == "high"
    assert 65 <= quarantine["risk_score"] <= 84

    allow = by_decision["allow"][0]
    assert allow["risk_band"] == "monitor"
    assert allow["risk_score"] <= 14

    deny_items = by_decision["deny"]
    assert any(item["risk_band"] == "low" for item in deny_items)
    assert any(item["risk_band"] == "medium" for item in deny_items)

    redact = by_decision["redact"][0]
    assert redact["risk_band"] == "medium"

    step_up = by_decision["step_up"][0]
    assert step_up["risk_band"] == "medium"


def test_pack_158_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_risk_score")
    payload = mod.build_policy_change_risk_score_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_band"]
    assert indexes["by_decision"]
    assert indexes["by_access_level"]
    assert indexes["by_family"]

    assert payload["critical_items"]
    assert payload["high_items"]
    assert payload["medium_items"]
    assert payload["low_items"]
    assert payload["monitor_items"]
    assert payload["owner_review_required"]
    assert payload["blocked_from_auto_change"]

    for item in payload["critical_items"]:
        assert item["risk_band"] == "critical"

    for item in payload["high_items"]:
        assert item["risk_band"] == "high"

    for item in payload["medium_items"]:
        assert item["risk_band"] == "medium"

    for item in payload["low_items"]:
        assert item["risk_band"] == "low"

    for item in payload["monitor_items"]:
        assert item["risk_band"] == "monitor"

    for item in payload["owner_review_required"]:
        assert item["requires_owner_review"] is True

    for item in payload["blocked_from_auto_change"]:
        assert item["risk_band"] in {"critical", "high"}


def test_pack_158_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_risk_score")

    bridge = mod.build_policy_change_risk_score_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 158
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-risk-score.json"
    assert bridge["readiness_score"] == 100
    assert bridge["risk_item_count"] >= 9
    assert bridge["critical_count"] >= 1
    assert bridge["high_count"] >= 1
    assert bridge["medium_count"] >= 1
    assert bridge["low_count"] >= 1
    assert bridge["monitor_count"] >= 1
    assert bridge["simulated_only"] is True
    assert bridge["scoring_only"] is True
    assert bridge["recommendation_only"] is True
    assert bridge["real_policy_change_executed"] is False
    assert bridge["real_permission_change_executed"] is False
    assert bridge["real_access_granted"] is False
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_risk_score_quick_action()
    assert action["id"] == "policy_change_risk_score"
    assert action["href"] == "/tower/policy-change-risk-score.json"
    assert action["simulated_only"] is True
    assert action["scoring_only"] is True

    section = mod.build_policy_change_risk_score_unified_owner_section()
    assert section["section_id"] == "policy_change_risk_score"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-risk-score.json"
    assert section["simulated_only"] is True
    assert section["scoring_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_158_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_158_policy_change_risk_score_status_bridge")

    bridge = status.build_pack_158_policy_change_risk_score_status_bridge()
    assert bridge["pack_number"] == 158
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-risk-score.json"
    assert bridge["readiness_score"] == 100


def test_pack_158_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_158_policy_change_risk_score_quick_action")
    assert hasattr(qa, "append_pack_158_policy_change_risk_score_quick_action")

    action = qa.build_pack_158_policy_change_risk_score_quick_action()
    assert action["id"] == "policy_change_risk_score"
    assert action["href"] == "/tower/policy-change-risk-score.json"

    actions = qa.append_pack_158_policy_change_risk_score_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_risk_score" for item in actions)


def test_pack_158_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_158_policy_change_risk_score_unified_section")
    assert hasattr(unified, "build_pack_158_policy_change_risk_score_html_section")
    assert hasattr(unified, "append_pack_158_policy_change_risk_score_section")

    section = unified.build_pack_158_policy_change_risk_score_unified_section()
    assert section["section_id"] == "policy_change_risk_score"
    assert section["href"] == "/tower/policy-change-risk-score.json"

    sections = unified.append_pack_158_policy_change_risk_score_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_risk_score" for item in sections)


def test_pack_158_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-risk-score.json" in app_text
    assert "tower_policy_change_risk_score_json" in app_text
    assert "_pack_158_policy_change_risk_score_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-risk-score.json" in route_text
    assert "_pack_158_policy_change_risk_score_route_guard" in route_text


def test_pack_158_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_risk_score")
    payload_text = str(mod.build_policy_change_risk_score_payload(force_refresh=True)).lower()

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
