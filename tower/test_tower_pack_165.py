
"""
PACK 165 fast test - Approval Receipt Detail Preview / Evidence Drawer.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_165_payload_ready_and_detail_preview_only():
    mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")
    payload = mod.build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=True)

    assert payload["pack_number"] == 165
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"
    assert payload["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"

    assert payload["simulated_only"] is True
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
    assert summary["detail_drawer_count"] >= 9
    assert summary["critical_drawer_count"] >= 1
    assert summary["quarantine_drawer_count"] >= 1
    assert summary["fresh_recheck_drawer_count"] >= 1
    assert summary["renewal_drawer_count"] >= 1
    assert summary["monitor_drawer_count"] >= 1
    assert summary["redacted_drawer_count"] >= 1
    assert summary["high_sensitivity_drawer_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_164_ready"] is True
    assert checks["has_detail_drawers"] is True
    assert checks["detail_count_matches_owner_review_items"] is True
    assert checks["all_simulated_only"] is True
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

    assert checks["all_detail_drawer_ids_present"] is True
    assert checks["all_owner_review_ids_present"] is True
    assert checks["all_detail_cards_present"] is True
    assert checks["all_sections_present"] is True
    assert checks["all_required_sections_present"] is True
    assert checks["all_safe_preview_mode"] is True

    assert checks["no_raw_secret_visible"] is True
    assert checks["no_raw_strategy_visible"] is True
    assert checks["no_broker_token_visible"] is True
    assert checks["no_unredacted_sensitive_value_visible"] is True

    assert checks["critical_drawers_present"] is True
    assert checks["quarantine_drawers_present"] is True
    assert checks["fresh_recheck_drawers_present"] is True
    assert checks["renewal_drawers_present"] is True
    assert checks["monitor_drawers_present"] is True
    assert checks["redacted_drawers_present"] is True
    assert checks["high_sensitivity_drawers_present"] is True
    assert checks["required_category_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_165_detail_drawers_have_required_fields():
    mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")
    payload = mod.build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=True)

    required_categories = {
        "critical_owner_recheck",
        "quarantine_owner_recheck",
        "fresh_recheck_review",
        "renewal_review",
        "monitor_acknowledgement",
    }
    observed_categories = set()

    required_sections = {
        "receipt_story",
        "source_chain",
        "risk_gate_lineage",
        "owner_action",
        "evidence_summary",
        "safety_flags",
    }

    for item in payload["detail_drawers"]:
        observed_categories.add(item["owner_review_category"])

        assert item["detail_drawer_id"].startswith("approval_receipt_detail_drawer_")
        assert item["owner_review_item_id"].startswith("approval_receipt_owner_review_preview_")
        assert item["queue_item_id"].startswith("approval_receipt_queue_preview_")
        assert item["expiration_preview_id"].startswith("approval_receipt_expiration_preview_")
        assert item["vault_preview_id"].startswith("approval_receipt_vault_preview_")
        assert item["ledger_index_id"].startswith("approval_receipt_ledger_index_")
        assert item["approval_receipt_preview_id"].startswith("approval_receipt_preview_")
        assert item["approval_gate_id"].startswith("approval_gate_preview_")
        assert item["risk_score_id"].startswith("policy_change_risk_")
        assert item["recommendation_id"].startswith("least_privilege_preview_")

        assert item["scenario_id"]
        assert item["owner_review_category"]
        assert item["owner_review_priority"] in {"critical", "high", "medium", "monitor"}
        assert item["required_owner_action"]
        assert item["owner_review_status"]
        assert item["detail_status"] == "detail_preview_ready"
        assert item["drawer_title"]
        assert item["drawer_subtitle"]

        assert isinstance(item["sections"], list)
        assert len(item["sections"]) >= 6
        assert isinstance(item["detail_cards"], list)
        assert len(item["detail_cards"]) >= 6
        assert item["section_count"] >= 6
        assert item["detail_card_count"] >= 6

        section_ids = {
            section.get("section_id")
            for section in item["sections"]
            if isinstance(section, dict)
        }
        assert required_sections.issubset(section_ids)

        assert item["receipt_story"]["section_id"] == "receipt_story"
        assert item["source_chain"]["section_id"] == "source_chain"
        assert item["risk_gate_lineage"]["section_id"] == "risk_gate_lineage"
        assert item["owner_action"]["section_id"] == "owner_action"
        assert item["evidence_summary"]["section_id"] == "evidence_summary"
        assert item["safety_flags"]["section_id"] == "safety_flags"

        assert item["receipt_story"]["safe_for_preview"] is True
        assert item["source_chain"]["safe_for_preview"] is True
        assert item["risk_gate_lineage"]["safe_for_preview"] is True
        assert item["owner_action"]["safe_for_preview"] is True
        assert item["evidence_summary"]["safe_for_preview"] is True
        assert item["safety_flags"]["safe_for_preview"] is True

        assert item["evidence_summary"]["redacted_by_default"] is True
        assert item["safety_flags"]["redacted_by_default"] is True
        assert item["redacted_section_count"] >= 1
        assert item["high_sensitivity_section_count"] >= 1

        assert item["safe_preview_mode"] is True
        assert item["raw_secret_visible"] is False
        assert item["raw_strategy_visible"] is False
        assert item["broker_token_visible"] is False
        assert item["unredacted_sensitive_value_visible"] is False

        assert item["source_endpoint"] == "/tower/policy-change-approval-receipt-owner-review-queue.json"

        assert item["simulated_only"] is True
        assert item["detail_preview_only"] is True
        assert item["evidence_drawer_preview_only"] is True
        assert item["owner_review_preview_only"] is True
        assert item["queue_preview_only"] is True
        assert item["renewal_preview_only"] is True
        assert item["recheck_preview_only"] is True
        assert item["expiration_preview_only"] is True
        assert item["vault_preview_only"] is True
        assert item["index_preview_only"] is True
        assert item["receipt_preview_only"] is True
        assert item["approval_preview_only"] is True
        assert item["evidence_preview_only"] is True

        assert item["real_approval_executed"] is False
        assert item["real_policy_change_executed"] is False
        assert item["real_permission_change_executed"] is False
        assert item["real_access_granted"] is False
        assert item["real_enforcement_executed"] is False
        assert item["real_audit_written"] is False
        assert item["real_receipt_written"] is False
        assert item["real_archive_written"] is False
        assert item["real_vault_written"] is False
        assert item["real_expiration_enforced"] is False
        assert item["real_recheck_executed"] is False
        assert item["real_renewal_executed"] is False
        assert item["real_queue_action_executed"] is False
        assert item["real_owner_review_completed"] is False
        assert item["real_owner_approval_executed"] is False
        assert item["real_owner_rejection_executed"] is False
        assert item["real_owner_acknowledgement_executed"] is False
        assert item["real_evidence_revealed"] is False

    assert required_categories.issubset(observed_categories)


def test_pack_165_section_specific_evidence_behavior():
    mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")
    payload = mod.build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=True)

    drawer = payload["detail_drawers"][0]

    receipt_story = drawer["receipt_story"]
    assert receipt_story["section_id"] == "receipt_story"
    assert receipt_story["redacted_by_default"] is False
    assert receipt_story["safe_for_preview"] is True
    assert receipt_story["story"]

    source_chain = drawer["source_chain"]
    assert source_chain["section_id"] == "source_chain"
    assert source_chain["redacted_by_default"] is False
    assert source_chain["chain_depth"] >= 8
    assert source_chain["chain"]["owner_review_item_id"].startswith("approval_receipt_owner_review_preview_")

    risk_gate_lineage = drawer["risk_gate_lineage"]
    assert risk_gate_lineage["section_id"] == "risk_gate_lineage"
    assert risk_gate_lineage["decision"]
    assert isinstance(risk_gate_lineage["risk_score"], int)
    assert risk_gate_lineage["owner_review_category"]

    owner_action = drawer["owner_action"]
    assert owner_action["section_id"] == "owner_action"
    assert owner_action["required_owner_action"]
    assert isinstance(owner_action["required_owner_review_steps"], list)
    assert owner_action["required_owner_review_steps"]

    evidence_summary = drawer["evidence_summary"]
    assert evidence_summary["section_id"] == "evidence_summary"
    assert evidence_summary["redacted_by_default"] is True
    assert evidence_summary["contains_raw_secret"] is False
    assert evidence_summary["contains_raw_strategy"] is False
    assert evidence_summary["contains_broker_token"] is False
    assert evidence_summary["contains_unredacted_sensitive_value"] is False

    safety_flags = drawer["safety_flags"]
    assert safety_flags["section_id"] == "safety_flags"
    assert safety_flags["redacted_by_default"] is True
    assert safety_flags["real_approval_executed"] is False
    assert safety_flags["real_policy_change_executed"] is False
    assert safety_flags["real_access_granted"] is False
    assert safety_flags["real_enforcement_executed"] is False
    assert safety_flags["real_evidence_revealed"] is False


def test_pack_165_indexes_and_special_lists_are_present():
    mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")
    payload = mod.build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_owner_review_category"]
    assert indexes["by_owner_review_priority"]
    assert indexes["by_required_owner_action"]
    assert indexes["by_detail_status"]
    assert indexes["by_owner_review_status"]

    assert payload["critical_drawers"]
    assert payload["quarantine_drawers"]
    assert payload["fresh_recheck_drawers"]
    assert payload["renewal_drawers"]
    assert payload["monitor_drawers"]
    assert payload["redacted_drawers"]
    assert payload["high_sensitivity_drawers"]

    for item in payload["critical_drawers"]:
        assert item["owner_review_category"] == "critical_owner_recheck"

    for item in payload["quarantine_drawers"]:
        assert item["owner_review_category"] == "quarantine_owner_recheck"

    for item in payload["fresh_recheck_drawers"]:
        assert item["owner_review_category"] == "fresh_recheck_review"

    for item in payload["renewal_drawers"]:
        assert item["owner_review_category"] == "renewal_review"

    for item in payload["monitor_drawers"]:
        assert item["owner_review_category"] == "monitor_acknowledgement"

    for item in payload["redacted_drawers"]:
        assert item["redacted_section_count"] >= 1

    for item in payload["high_sensitivity_drawers"]:
        assert item["high_sensitivity_section_count"] >= 1


def test_pack_165_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")

    bridge = mod.build_policy_change_approval_receipt_detail_evidence_drawer_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 165
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"
    assert bridge["readiness_score"] == 100
    assert bridge["detail_drawer_count"] >= 9
    assert bridge["critical_drawer_count"] >= 1
    assert bridge["quarantine_drawer_count"] >= 1
    assert bridge["fresh_recheck_drawer_count"] >= 1
    assert bridge["renewal_drawer_count"] >= 1
    assert bridge["monitor_drawer_count"] >= 1
    assert bridge["redacted_drawer_count"] >= 1
    assert bridge["high_sensitivity_drawer_count"] >= 1

    assert bridge["simulated_only"] is True
    assert bridge["detail_preview_only"] is True
    assert bridge["evidence_drawer_preview_only"] is True
    assert bridge["real_evidence_revealed"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_change_approval_receipt_detail_evidence_drawer_quick_action()
    assert action["id"] == "policy_change_approval_receipt_detail_evidence_drawer"
    assert action["href"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"
    assert action["simulated_only"] is True
    assert action["detail_preview_only"] is True

    section = mod.build_policy_change_approval_receipt_detail_evidence_drawer_unified_owner_section()
    assert section["section_id"] == "policy_change_approval_receipt_detail_evidence_drawer"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"
    assert section["simulated_only"] is True
    assert section["detail_preview_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_165_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_status_bridge")

    bridge = status.build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_status_bridge()
    assert bridge["pack_number"] == 165
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"
    assert bridge["readiness_score"] == 100


def test_pack_165_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_quick_action")
    assert hasattr(qa, "append_pack_165_policy_change_approval_receipt_detail_evidence_drawer_quick_action")

    action = qa.build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_quick_action()
    assert action["id"] == "policy_change_approval_receipt_detail_evidence_drawer"
    assert action["href"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"

    actions = qa.append_pack_165_policy_change_approval_receipt_detail_evidence_drawer_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_change_approval_receipt_detail_evidence_drawer" for item in actions)


def test_pack_165_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_unified_section")
    assert hasattr(unified, "build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_html_section")
    assert hasattr(unified, "append_pack_165_policy_change_approval_receipt_detail_evidence_drawer_section")

    section = unified.build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_unified_section()
    assert section["section_id"] == "policy_change_approval_receipt_detail_evidence_drawer"
    assert section["href"] == "/tower/policy-change-approval-receipt-detail-evidence-drawer.json"

    sections = unified.append_pack_165_policy_change_approval_receipt_detail_evidence_drawer_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_change_approval_receipt_detail_evidence_drawer" for item in sections)


def test_pack_165_web_route_present_and_route_scanner_recognizes_it():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-detail-evidence-drawer.json" in app_text
    assert "tower_policy_change_approval_receipt_detail_evidence_drawer_json" in app_text
    assert "_pack_165_policy_change_approval_receipt_detail_evidence_drawer_route_guard" in app_text

    route_text = Path("tower/ob_route_coverage_report.py").read_text(encoding="utf-8")
    assert "/tower/policy-change-approval-receipt-detail-evidence-drawer.json" in route_text
    assert "_pack_165_policy_change_approval_receipt_detail_evidence_drawer_route_guard" in route_text


def test_pack_165_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_change_approval_receipt_detail_evidence_drawer")
    payload_text = str(mod.build_policy_change_approval_receipt_detail_evidence_drawer_payload(force_refresh=True)).lower()

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
