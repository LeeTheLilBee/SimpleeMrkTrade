
"""
PACK 155 fast test - Policy Expiration Rules foundation.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_155_payload_ready_and_simulated_only():
    mod = importlib.import_module("tower.policy_expiration_rules")
    payload = mod.build_policy_expiration_rules_payload(force_refresh=True)

    assert payload["pack_number"] == 155
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-expiration-rules.json"
    assert payload["source_endpoint"] == "/tower/policy-receipt-vault-preview.json"

    assert payload["simulated_only"] is True
    assert payload["real_expiration_enforced"] is False
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["expiration_entry_count"] >= 9
    assert summary["owner_review_queue_count"] == summary["expiration_entry_count"]
    assert summary["expiration_rule_count"] >= 7
    assert summary["expired_count"] >= 1
    assert summary["warning_count"] >= 1
    assert summary["fresh_count"] >= 1

    checks = payload["readiness_checks"]
    assert checks["pack_154_ready"] is True
    assert checks["has_expiration_entries"] is True
    assert checks["entry_count_matches_vault_entries"] is True
    assert checks["all_simulated_only"] is True
    assert checks["no_real_expiration_enforced"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["all_expiration_ids_present"] is True
    assert checks["all_rules_present"] is True
    assert checks["all_ttl_present"] is True
    assert checks["state_index_present"] is True
    assert checks["bucket_index_present"] is True
    assert checks["rule_index_present"] is True
    assert checks["next_action_index_present"] is True
    assert checks["owner_review_queue_present"] is True
    assert checks["required_state_coverage"] is True
    assert checks["required_bucket_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_155_expiration_entries_have_required_fields():
    mod = importlib.import_module("tower.policy_expiration_rules")
    payload = mod.build_policy_expiration_rules_payload(force_refresh=True)

    required_states = {"fresh", "warning", "expired"}
    observed_states = set()

    required_buckets = {
        "blocked_decisions",
        "challenge_required",
        "privacy_redactions",
        "containment_queue",
        "critical_safety_stops",
        "monitor_only_allows",
    }
    observed_buckets = set()

    for entry in payload["expiration_entries"]:
        observed_states.add(entry["expiration_state"])
        observed_buckets.add(entry["bucket"])

        assert entry["expiration_check_id"].startswith("expiration_preview_")
        assert entry["rule_id"].startswith("expiration.")
        assert entry["bucket"]
        assert entry["decision"]
        assert entry["severity"]
        assert entry["scenario_id"]
        assert entry["matched_policy_id"]
        assert entry["vault_entry_id"].startswith("vault_preview_")
        assert entry["ledger_entry_id"].startswith("ledger_preview_")
        assert entry["receipt_preview_id"].startswith("receipt_preview_")
        assert isinstance(entry["ttl_minutes"], int)
        assert entry["ttl_minutes"] > 0
        assert isinstance(entry["simulated_age_minutes"], int)
        assert entry["expiration_state"] in {"fresh", "warning", "expired"}
        assert entry["simulated_created_at"].endswith("Z")
        assert entry["simulated_expires_at"].endswith("Z")
        assert isinstance(entry["minutes_until_expiration"], int)
        assert entry["next_action"]
        assert entry["review_action"]
        assert entry["stale_status"]
        assert entry["owner_reason"]
        assert entry["owner_message"]
        assert entry["proof_bundle_hint"]
        assert entry["soulaana_translation"]

        assert entry["simulated_only"] is True
        assert entry["real_expiration_enforced"] is False
        assert entry["real_receipt_written"] is False
        assert entry["real_audit_written"] is False
        assert entry["real_enforcement_executed"] is False
        assert entry["source_endpoint"] == "/tower/policy-receipt-vault-preview.json"

        if entry["expiration_state"] == "expired":
            assert entry["is_expired"] is True
            assert entry["next_action"] == entry["review_action"]
        elif entry["expiration_state"] == "warning":
            assert entry["is_warning"] is True
            assert entry["next_action"] == "review_soon"
        else:
            assert entry["is_fresh"] is True
            assert entry["next_action"] == "continue_monitoring"

    assert required_states.issubset(observed_states)
    assert required_buckets.issubset(observed_buckets)


def test_pack_155_indexes_and_owner_queue_are_present():
    mod = importlib.import_module("tower.policy_expiration_rules")
    payload = mod.build_policy_expiration_rules_payload(force_refresh=True)

    indexes = payload["indexes"]
    assert indexes["by_state"]
    assert indexes["by_bucket"]
    assert indexes["by_rule"]
    assert indexes["by_next_action"]

    assert {"fresh", "warning", "expired"}.issubset(set(indexes["by_state"].keys()))

    queue = payload["owner_review_queue"]
    assert len(queue) == payload["summary"]["expiration_entry_count"]

    for idx, item in enumerate(queue, start=1):
        assert item["queue_position"] == idx
        assert item["expiration_check_id"].startswith("expiration_preview_")
        assert item["vault_entry_id"].startswith("vault_preview_")
        assert item["ledger_entry_id"].startswith("ledger_preview_")
        assert item["decision"]
        assert item["severity"]
        assert item["bucket"]
        assert item["expiration_state"] in {"fresh", "warning", "expired"}
        assert item["review_action"]
        assert item["next_action"]
        assert item["scenario_id"]
        assert item["matched_policy_id"]
        assert item["owner_message"]
        assert item["simulated_only"] is True

    # Highest urgency should come first.
    assert queue[0]["expiration_state"] == "expired"


def test_pack_155_rule_registry_has_expected_buckets():
    mod = importlib.import_module("tower.policy_expiration_rules")

    expected_buckets = {
        "critical_safety_stops",
        "containment_queue",
        "blocked_decisions",
        "challenge_required",
        "privacy_redactions",
        "monitor_only_allows",
        "review_queue",
    }

    assert expected_buckets.issubset(set(mod.EXPIRATION_RULES.keys()))

    for bucket in expected_buckets:
        rule = mod.get_expiration_rule_for_bucket(bucket)
        assert rule["bucket"] == bucket
        assert rule["rule_id"].startswith("expiration.")
        assert int(rule["ttl_minutes"]) > 0
        assert rule["review_action"]
        assert rule["stale_status"]
        assert rule["owner_reason"]


def test_pack_155_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_expiration_rules")

    bridge = mod.build_policy_expiration_rules_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 155
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-expiration-rules.json"
    assert bridge["readiness_score"] == 100
    assert bridge["expiration_entry_count"] >= 9
    assert bridge["expiration_rule_count"] >= 7
    assert bridge["owner_review_queue_count"] == bridge["expiration_entry_count"]
    assert bridge["expired_count"] >= 1
    assert bridge["warning_count"] >= 1
    assert bridge["fresh_count"] >= 1
    assert bridge["simulated_only"] is True
    assert bridge["real_expiration_enforced"] is False
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True

    action = mod.build_policy_expiration_rules_quick_action()
    assert action["id"] == "policy_expiration_rules"
    assert action["href"] == "/tower/policy-expiration-rules.json"
    assert action["simulated_only"] is True

    section = mod.build_policy_expiration_rules_unified_owner_section()
    assert section["section_id"] == "policy_expiration_rules"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-expiration-rules.json"
    assert section["simulated_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_155_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_155_policy_expiration_rules_status_bridge")

    bridge = status.build_pack_155_policy_expiration_rules_status_bridge()
    assert bridge["pack_number"] == 155
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-expiration-rules.json"
    assert bridge["readiness_score"] == 100


def test_pack_155_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_155_policy_expiration_rules_quick_action")
    assert hasattr(qa, "append_pack_155_policy_expiration_rules_quick_action")

    action = qa.build_pack_155_policy_expiration_rules_quick_action()
    assert action["id"] == "policy_expiration_rules"
    assert action["href"] == "/tower/policy-expiration-rules.json"

    actions = qa.append_pack_155_policy_expiration_rules_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_expiration_rules" for item in actions)


def test_pack_155_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_155_policy_expiration_rules_unified_section")
    assert hasattr(unified, "build_pack_155_policy_expiration_rules_html_section")
    assert hasattr(unified, "append_pack_155_policy_expiration_rules_section")

    section = unified.build_pack_155_policy_expiration_rules_unified_section()
    assert section["section_id"] == "policy_expiration_rules"
    assert section["href"] == "/tower/policy-expiration-rules.json"

    sections = unified.append_pack_155_policy_expiration_rules_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_expiration_rules" for item in sections)


def test_pack_155_web_route_present_in_app_file():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-expiration-rules.json" in app_text
    assert "tower_policy_expiration_rules_json" in app_text
    assert "_pack_155_policy_expiration_rules_route_guard" in app_text


def test_pack_155_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_expiration_rules")
    payload_text = str(mod.build_policy_expiration_rules_payload(force_refresh=True)).lower()

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
