
"""
PACK 152 fast test - Policy Simulation Mode foundation.
"""

from __future__ import annotations

import importlib


def test_pack_152_payload_is_ready_and_simulated_only():
    mod = importlib.import_module("tower.policy_simulation_mode")
    payload = mod.build_policy_simulation_mode_payload(force_refresh=True)

    assert payload["pack_number"] == 152
    assert payload["status"] == "ready"
    assert payload["endpoint"] == "/tower/policy-simulation-mode.json"
    assert payload["simulated_only"] is True
    assert payload["real_enforcement_executed"] is False
    assert payload["cached_non_recursive"] is True

    summary = payload["summary"]
    assert summary["scenario_count"] >= 8
    assert summary["readiness_score"] == 100

    checks = payload["readiness_checks"]
    assert checks["simulated_only"] is True
    assert checks["no_real_enforcement"] is True
    assert checks["has_allow"] is True
    assert checks["has_deny"] is True
    assert checks["has_step_up"] is True
    assert checks["has_redact"] is True
    assert checks["has_quarantine"] is True
    assert checks["has_fail_closed"] is True
    assert checks["expected_policy_coverage"] is True
    assert checks["pack_151_registry_loaded_or_fallback"] is True
    assert checks["cached_non_recursive"] is True


def test_pack_152_scenario_decisions_cover_required_cases():
    mod = importlib.import_module("tower.policy_simulation_mode")
    payload = mod.build_policy_simulation_mode_payload(force_refresh=True)

    by_id = {row["scenario_id"]: row for row in payload["scenarios"]}

    expected = {
        "no_tower_clearance_open_ob": ("deny", "tower.no_clearance_no_ob"),
        "public_user_live_automated": ("deny", "live.public_automated_locked"),
        "sensitive_export_step_up": ("step_up", "export.sensitive_step_up"),
        "raw_secret_request_denied": ("deny", "secrets.vault_boundary"),
        "unknown_route_quarantined": ("quarantine", "route.unknown_route_quarantine"),
        "object_without_permission_denied": ("deny", "object.least_privilege"),
        "dependency_failure_fail_closed": ("fail_closed", "dependency.fail_closed"),
        "normal_allowed_monitor_only": ("allow", "simulation.explicit_allow_monitor"),
    }

    for scenario_id, (decision, policy_id) in expected.items():
        assert scenario_id in by_id
        row = by_id[scenario_id]
        assert row["decision"] == decision
        assert row["matched_policy_id"] == policy_id
        assert row["simulated_only"] is True
        assert row["real_enforcement_executed"] is False
        assert row["effect"] in {"allow", "deny", "step_up", "redact", "quarantine", "fail_closed"}
        assert row["enforcement_mode"] == "simulation_only"
        assert row["receipt_type"]
        assert row["owner_reason"]
        assert row["soulaana_translation"]


def test_pack_152_status_bridge_quick_action_and_unified_section():
    sim = importlib.import_module("tower.policy_simulation_mode")

    bridge = sim.build_policy_simulation_mode_status_bridge(force_refresh=True)
    assert bridge["pack_number"] == 152
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["simulated_only"] is True
    assert bridge["real_enforcement_executed"] is False
    assert bridge["cached_non_recursive"] is True

    quick_action = sim.build_policy_simulation_quick_action()
    assert quick_action["id"] == "policy_simulation_mode"
    assert quick_action["href"] == "/tower/policy-simulation-mode.json"
    assert quick_action["simulated_only"] is True

    section = sim.build_policy_simulation_unified_owner_section()
    assert section["section_id"] == "policy_simulation_mode"
    assert section["status"] == "ready"
    assert section["href"] == "/tower/policy-simulation-mode.json"
    assert section["simulated_only"] is True
    assert section["cached_non_recursive"] is True
    assert len(section["cards"]) >= 6


def test_pack_152_tower_status_bridge_available():
    status = importlib.import_module("tower.tower_status")
    assert hasattr(status, "build_pack_152_policy_simulation_status_bridge")

    bridge = status.build_pack_152_policy_simulation_status_bridge()
    assert bridge["pack_number"] == 152
    assert bridge["status"] == "ready"
    assert bridge["readiness_score"] == 100
    assert bridge["endpoint"] == "/tower/policy-simulation-mode.json"


def test_pack_152_quick_action_helper_available():
    qa = importlib.import_module("tower.security_command_owner_quick_actions")
    assert hasattr(qa, "build_pack_152_policy_simulation_quick_action")
    assert hasattr(qa, "append_pack_152_policy_simulation_quick_action")

    action = qa.build_pack_152_policy_simulation_quick_action()
    assert action["id"] == "policy_simulation_mode"
    assert action["href"] == "/tower/policy-simulation-mode.json"

    actions = qa.append_pack_152_policy_simulation_quick_action([])
    assert isinstance(actions, list)
    assert any(item.get("id") == "policy_simulation_mode" for item in actions)


def test_pack_152_unified_section_helper_available():
    unified = importlib.import_module("tower.security_command_unified_owner_page")
    assert hasattr(unified, "build_pack_152_policy_simulation_unified_section")
    assert hasattr(unified, "build_pack_152_policy_simulation_html_section")
    assert hasattr(unified, "append_pack_152_policy_simulation_section")

    section = unified.build_pack_152_policy_simulation_unified_section()
    assert section["section_id"] == "policy_simulation_mode"
    assert section["href"] == "/tower/policy-simulation-mode.json"

    sections = unified.append_pack_152_policy_simulation_section([])
    assert isinstance(sections, list)
    assert any(item.get("section_id") == "policy_simulation_mode" for item in sections)


def test_pack_152_web_route_present_in_app_file():
    from pathlib import Path

    app_text = Path("web/app.py").read_text(encoding="utf-8")
    assert "/tower/policy-simulation-mode.json" in app_text
    assert "tower_policy_simulation_mode_json" in app_text
    assert "_pack_152_policy_simulation_route_guard" in app_text


def test_pack_152_no_secret_leakage_in_new_policy_payload():
    mod = importlib.import_module("tower.policy_simulation_mode")
    payload_text = str(mod.build_policy_simulation_mode_payload(force_refresh=True)).lower()

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
