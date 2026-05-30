
"""
PACK 153 fast test - Policy Decision Trace / Receipt Preview layer.
"""

from __future__ import annotations

import importlib
from pathlib import Path


def test_pack_153_payload_ready_and_preview_only():
    mod = importlib.import_module("tower.policy_decision_trace_receipt_preview")
    payload = mod.build_policy_decision_trace_preview_payload(force_refresh=True)

    assert payload["pack_number"] == 153
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-decision-trace-preview.json"
    assert payload["source_endpoint"] == "/tower/policy-simulation-mode.json"

    assert payload["simulated_only"] is True
    assert payload["real_enforcement_executed"] is False
    assert payload["real_audit_written"] is False
    assert payload["real_receipt_written"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["readiness_score"] == 100
    assert summary["trace_count"] >= 9
    assert summary["receipt_preview_count"] == summary["trace_count"]

    checks = payload["readiness_checks"]
    assert checks["pack_152_ready"] is True
    assert checks["has_traces"] is True
    assert checks["trace_count_matches_scenarios"] is True
    assert checks["all_simulated_only"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["no_real_audit_written"] is True
    assert checks["no_real_receipt_written"] is True
    assert checks["all_receipt_previews_present"] is True
    assert checks["all_trace_ids_present"] is True
    assert checks["required_decision_coverage"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_153_traces_have_required_receipt_preview_fields():
    mod = importlib.import_module("tower.policy_decision_trace_receipt_preview")
    payload = mod.build_policy_decision_trace_preview_payload(force_refresh=True)

    required_decisions = {"allow", "deny", "step_up", "redact", "quarantine", "fail_closed"}
    observed = set()

    for trace in payload["traces"]:
        observed.add(trace["decision"])

        assert trace["trace_id"].startswith("trace_preview_")
        assert trace["scenario_id"]
        assert trace["scenario_label"]
        assert trace["decision"]
        assert trace["matched_policy_id"]
        assert trace["effect"]
        assert trace["enforcement_mode"] == "simulation_only"
        assert trace["simulated_only"] is True
        assert trace["real_enforcement_executed"] is False
        assert trace["real_audit_written"] is False
        assert trace["real_receipt_written"] is False
        assert trace["trace_steps"]
        assert len(trace["trace_steps"]) >= 5
        assert trace["plain_language_trace"]
        assert trace["owner_reason_prompt"]
        assert trace["soulaana_translation"]

        receipt = trace["receipt_preview"]
        assert receipt["receipt_preview_id"].startswith("receipt_preview_")
        assert receipt["receipt_type"]
        assert receipt["would_write_receipt"] is True
        assert receipt["real_receipt_written"] is False
        assert receipt["simulated_only"] is True
        assert receipt["receipt_action"]
        assert receipt["receipt_status"] == "preview_only"

        required_fields = receipt["required_fields_preview"]
        assert required_fields["scenario_id"] == trace["scenario_id"]
        assert required_fields["decision"] == trace["decision"]
        assert required_fields["matched_policy_id"] == trace["matched_policy_id"]
        assert required_fields["enforcement_mode"] == "simulation_only"
        assert required_fields["owner_reason_prompt"]

    assert required_decisions.issubset(observed)


def test_pack_153_status_bridge_quick_action_and_unified_section():
    mod = importlib.import_module("tower.policy_decision_trace_receipt_preview")

    bridge = mod.build_policy_decision_trace_preview_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 153
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["simulated_only"] is True
    assert bridge["real_enforcement_executed"] is False
    assert bridge["real_audit_written"] is False
    assert bridge["real_receipt_written"] is False
    assert bridge["cached_non_recursive"] is True
    assert bridge["trace_count"] >= 9
    assert bridge["receipt_preview_count"] == bridge["trace_count"]

    action = mod.build_policy_decision_trace_preview_quick_action()
    assert action["id"] == "policy_decision_trace_preview"
    assert action["href"] == "/tower/policy-decision-trace-preview.json"
    assert action["simulated_only"] is True

    section = mod.build_policy_decision_trace_preview_unified_owner_section()
    assert section["section_id"] == "policy_decision_trace_preview"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-decision-trace-preview.json"
    assert section["simulated_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_153_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_153_policy_decision_trace_preview_status_bridge")

    bridge = status.build_pack_153_policy_decision_trace_preview_status_bridge()
    assert bridge["pack_number"] == 153
    assert bridge["status"] == "ready"
    assert bridge["endpoint"] == "/tower/policy-decision-trace-preview.json"
    assert bridge["readiness_score"] == 100


def test_pack_153_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_153_policy_decision_trace_preview_quick_action")
    assert hasattr(qa, "append_pack_153_policy_decision_trace_preview_quick_action")

    action = qa.build_pack_153_policy_decision_trace_preview_quick_action()
    assert action["id"] == "policy_decision_trace_preview"
    assert action["href"] == "/tower/policy-decision-trace-preview.json"

    actions = qa.append_pack_153_policy_decision_trace_preview_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_decision_trace_preview" for item in actions)


def test_pack_153_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_153_policy_decision_trace_preview_unified_section")
    assert hasattr(unified, "build_pack_153_policy_decision_trace_preview_html_section")
    assert hasattr(unified, "append_pack_153_policy_decision_trace_preview_section")

    section = unified.build_pack_153_policy_decision_trace_preview_unified_section()
    assert section["section_id"] == "policy_decision_trace_preview"
    assert section["href"] == "/tower/policy-decision-trace-preview.json"

    sections = unified.append_pack_153_policy_decision_trace_preview_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_decision_trace_preview" for item in sections)


def test_pack_153_web_route_present_in_app_file():
    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-decision-trace-preview.json" in app_text
    assert "tower_policy_decision_trace_preview_json" in app_text
    assert "_pack_153_policy_decision_trace_preview_route_guard" in app_text


def test_pack_153_no_secret_leakage_in_payload():
    mod = importlib.import_module("tower.policy_decision_trace_receipt_preview")
    payload_text = str(mod.build_policy_decision_trace_preview_payload(force_refresh=True)).lower()

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
