
"""
PACK 154 fast test - Policy Receipt Vault Preview / Simulated Ledger Index.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_154_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.policy_receipt_vault_preview")
    payload = mod.build_policy_receipt_vault_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 154
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-receipt-vault-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-decision-trace-preview.json"

    assert payload["simulated_only"] is True
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["vault_entry_count"] >= 9
    assert summary["ledger_entry_count"] == summary["vault_entry_count"]
    assert summary["receipt_preview_count"] == summary["vault_entry_count"]
    assert summary["owner_review_queue_count"] == summary["vault_entry_count"]
    assert summary["bucket_count"] >= 6

    checks = payload["readiness_checks"]
    assert checks["pack_153_ready"] is True
    assert checks["has_entries"] is True
    assert checks["entry_count_matches_traces"] is True
    assert checks["all_simulated_only"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["all_vault_ids_present"] is True
    assert checks["all_ledger_ids_present"] is True
    assert checks["all_receipt_preview_ids_present"] is True
    assert checks["bucket_index_present"] is True
    assert checks["decision_index_present"] is True
    assert checks["severity_index_present"] is True
    assert checks["policy_index_present"] is True
    assert checks["owner_review_queue_present"] is True
    assert checks["required_decision_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_154_vault_entries_have_required_fields():
    mod = importlib.import_module("tower.policy_receipt_vault_preview")
    payload = mod.build_policy_receipt_vault_preview_payload(force_refresh=True)

    required_decisions = {"allow", "deny", "step_up", "redact", "quarantine", "fail_closed"}
    observed = set()

    for entry in payload["vault_entries"]:
        observed.add(entry["decision"])

        assert entry["vault_entry_id"].startswith("vault_preview_")
        assert entry["ledger_entry_id"].startswith("ledger_preview_")
        assert entry["bucket"]
        assert entry["ledger_status"]
        assert entry["decision"]
        assert entry["severity"]
        assert isinstance(entry["severity_rank"], int)
        assert entry["scenario_id"]
        assert entry["matched_policy_id"]
        assert entry["trace_id"].startswith("trace_preview_")
        assert entry["receipt_preview_id"].startswith("receipt_preview_")
        assert entry["receipt_type"]
        assert entry["receipt_status"] == "preview_only"
        assert entry["receipt_action"]
        assert entry["owner_reason_prompt"]
        assert entry["soulaana_translation"]
        assert entry["plain_language_trace"]
        assert entry["proof_bundle_hint"]

        assert entry["simulated_only"] is True
        assert entry["real_receipt_written"] is False
        assert entry["real_audit_written"] is False
        assert entry["real_enforcement_executed"] is False
        assert entry["source_endpoint"] == "/tower/policy-decision-trace-preview.json"

    assert required_decisions.issubset(observed)


def test_pack_154_indexes_and_owner_review_queue_are_present():
    mod = importlib.import_module("tower.policy_receipt_vault_preview")
    payload = mod.build_policy_receipt_vault_preview_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_bucket"]
    assert indexes["by_decision"]
    assert indexes["by_severity"]
    assert indexes["by_policy"]

    expected_buckets = {
        "blocked_decisions",
        "challenge_required",
        "privacy_redactions",
        "containment_queue",
        "critical_safety_stops",
        "monitor_only_allows",
    }
    assert expected_buckets.issubset(set(indexes["by_bucket"].keys()))

    queue = payload["owner_review_queue"]
    assert len(queue) == payload["summary"]["vault_entry_count"]

    for idx, item in enumerate(queue, start=1):
        assert item["queue_position"] == idx
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["decision"]
        assert item["severity"]
        assert item["bucket"]
        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["owner_reason_prompt"]
        assert item["simulated_only"] is True


def test_pack_154_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_receipt_vault_preview")

    bridge = mod.build_policy_receipt_vault_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 154
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-receipt-vault-preview.json"
    assert bridge["readiness_score"] == 100
    assert bridge["vault_entry_count"] >= 9
    assert bridge["ledger_entry_count"] == bridge["vault_entry_count"]
    assert bridge["receipt_preview_count"] == bridge["vault_entry_count"]
    assert bridge["owner_review_queue_count"] == bridge["vault_entry_count"]
    assert bridge["simulated_only"] is True
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_receipt_vault_preview_quick_action()
    assert action["id"] == "policy_receipt_vault_preview"
    assert action["href"] == "/tower/policy-receipt-vault-preview.json"
    assert action["simulated_only"] is True

    section = mod.build_policy_receipt_vault_preview_unified_owner_section()
    assert section["section_id"] == "policy_receipt_vault_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-receipt-vault-preview.json"
    assert section["simulated_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_154_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_154_policy_receipt_vault_preview_status_bridge")

    bridge = status.build_pack_154_policy_receipt_vault_preview_status_bridge()
    assert bridge["pack_number"] == 154
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-receipt-vault-preview.json"
    assert bridge["readiness_score"] == 100


def test_pack_154_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_154_policy_receipt_vault_preview_quick_action")
    assert hasattr(qa, "append_pack_154_policy_receipt_vault_preview_quick_action")

    action = qa.build_pack_154_policy_receipt_vault_preview_quick_action()
    assert action["id"] == "policy_receipt_vault_preview"
    assert action["href"] == "/tower/policy-receipt-vault-preview.json"

    actions = qa.append_pack_154_policy_receipt_vault_preview_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_receipt_vault_preview" for item in actions)


def test_pack_154_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_154_policy_receipt_vault_preview_unified_section")
    assert hasattr(unified, "build_pack_154_policy_receipt_vault_preview_html_section")
    assert hasattr(unified, "append_pack_154_policy_receipt_vault_preview_section")

    section = unified.build_pack_154_policy_receipt_vault_preview_unified_section()
    assert section["section_id"] == "policy_receipt_vault_preview"
    assert section["href"] == "/tower/policy-receipt-vault-preview.json"

    sections = unified.append_pack_154_policy_receipt_vault_preview_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_receipt_vault_preview" for item in sections)


def test_pack_154_web_route_present_in_app_file():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-receipt-vault-preview.json" in app_text
    assert "tower_policy_receipt_vault_preview_json" in app_text
    assert "_pack_154_policy_receipt_vault_preview_route_guard" in app_text


def test_pack_154_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_receipt_vault_preview")
    payload_text = str(mod.build_policy_receipt_vault_preview_payload(force_refresh=True)).lower()

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
