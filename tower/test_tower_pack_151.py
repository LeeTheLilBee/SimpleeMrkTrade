
from __future__ import annotations

import json
import os
import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WEB_APP = PROJECT_ROOT / "web" / "app.py"


def show(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def no_secret(payload):
    s = json.dumps(payload, sort_keys=True, default=str).lower()
    bad = [
        "should_not_survive",
        "tower_keycard=",
        '"raw_token":',
        '"api_key":',
        '"password":',
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
        "sk_live_should",
        "ghp_should",
    ]
    for item in bad:
        assert item not in s, item


def run_fast(label: str, code: str, timeout: int = 20):
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = round(time.time() - start, 2)
    show(label, {
        "elapsed": elapsed,
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    })
    assert result.returncode == 0
    assert elapsed < timeout


def run_tests():
    from tower.policy_as_code_engine import (
        POLICY_AS_CODE_PANEL_PATH,
        POLICY_AS_CODE_REGISTRY_PATH,
        POLICY_AS_CODE_STATUS_PATH,
        build_policy_as_code_engine_status,
        load_policy_as_code_engine_status,
        policy_as_code_engine_status_card,
        render_policy_as_code_engine_section,
        reset_policy_as_code_engine_for_test,
        write_policy_as_code_engine_panel,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.tower_status import pack151_policy_as_code_engine_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset = reset_policy_as_code_engine_for_test()
    show("RESET PACK 151 POLICY ENGINE", reset)
    assert reset.get("ok") is True

    run_fast(
        "FAST PACK 151 POLICY ENGINE",
        "from tower.policy_as_code_engine import build_policy_as_code_engine_status; "
        "s=build_policy_as_code_engine_status(write_panel=False); "
        "print(s.get('status'), s.get('pack'), s.get('policy_count'), s.get('readiness_score'))",
        timeout=20,
    )

    run_fast(
        "FAST PACK 151 QUICK ACTIONS",
        "from tower.security_command_owner_quick_actions import build_owner_quick_actions_status; "
        "s=build_owner_quick_actions_status(write_panel=False); "
        "print(s.get('status'), s.get('action_count'), s.get('pack151_policy_link_present'))",
        timeout=20,
    )

    run_fast(
        "FAST PACK 151 UNIFIED HTML",
        "from tower.security_command_unified_owner_page import render_unified_owner_security_command_html; "
        "h=render_unified_owner_security_command_html(); "
        "print(len(h), 'PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE' in h, 'PACK151_POLICY_AS_CODE_ENGINE_SECTION' in h)",
        timeout=35,
    )

    status = build_policy_as_code_engine_status(write_panel=True)
    card = policy_as_code_engine_status_card()
    bridge = pack151_policy_as_code_engine_status_bridge()
    loaded = load_policy_as_code_engine_status()
    section = render_policy_as_code_engine_section(status)
    panel = write_policy_as_code_engine_panel(status)

    quick = build_owner_quick_actions_status(write_panel=True)
    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    action_ids = {action.get("action_id") for action in actions if isinstance(action, dict)}
    hrefs = {action.get("href") for action in actions if isinstance(action, dict)}

    unified_html = render_unified_owner_security_command_html()
    unified_write = write_unified_owner_security_command_html()

    show("PACK 151 POLICY STATUS", {
        "ok": status.get("ok"),
        "pack": status.get("pack"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "readiness_label": status.get("readiness_label"),
        "policy_count": status.get("policy_count"),
        "enabled_policy_count": status.get("enabled_policy_count"),
        "failed_enabled_validation_count": status.get("failed_enabled_validation_count"),
        "by_domain": status.get("by_domain"),
        "by_effect": status.get("by_effect"),
        "failed_checks": status.get("failed_checks"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    show("PACK 151 STATUS CARD", card)
    show("PACK 151 TOWER STATUS BRIDGE", bridge)

    show("PACK 151 QUICK ACTIONS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "action_count": quick.get("action_count"),
        "has_policy_action": "review_policy_as_code_engine" in action_ids,
        "has_policy_href": "/tower/policy-as-code-engine.json" in hrefs,
        "pack151_marker": quick.get("pack151_marker"),
        "no_secret_leakage": quick.get("no_secret_leakage"),
    })

    show("PACK 151 SECTION CHECK", {
        "html_length": len(section),
        "has_marker": "PACK151_POLICY_AS_CODE_ENGINE_SECTION" in section,
        "has_title": "Policy-as-Code" in section,
        "has_default_deny": "tower.default_deny" in section,
        "has_live_lock": "live.public_automated_locked" in section,
    })

    show("PACK 151 PANEL WRITE", panel)

    show("PACK 151 UNIFIED HTML CHECK", {
        "html_length": len(unified_html),
        "has_pack151_marker": "PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE" in unified_html,
        "has_pack151_section": "PACK151_POLICY_AS_CODE_ENGINE_SECTION" in unified_html,
        "has_pack150_section": "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in unified_html,
    })

    show("PACK 151 WRITE UNIFIED HTML", unified_write)

    assert status.get("ok") is True
    assert status.get("pack") == "151"
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("readiness_label") == "Policy-as-Code foundation ready"
    assert status.get("policy_count", 0) >= 10
    assert status.get("enabled_policy_count", 0) >= 10
    assert status.get("failed_enabled_validation_count") == 0
    assert status.get("failed_checks") == []
    assert status.get("no_secret_leakage") is True

    checks = status.get("checks", {})
    assert checks.get("default_deny_present") is True
    assert checks.get("no_clearance_no_ob_present") is True
    assert checks.get("public_live_automated_locked_present") is True
    assert checks.get("secrets_vault_boundary_present") is True
    assert checks.get("export_step_up_present") is True
    assert checks.get("redact_by_default_present") is True
    assert checks.get("object_least_privilege_present") is True
    assert checks.get("dependency_fail_closed_present") is True
    assert checks.get("all_required_policies_present") is True
    assert checks.get("no_duplicate_policy_ids") is True
    assert checks.get("all_enabled_policies_valid") is True

    assert POLICY_AS_CODE_REGISTRY_PATH.exists()
    assert POLICY_AS_CODE_STATUS_PATH.exists()
    assert POLICY_AS_CODE_PANEL_PATH.exists()

    assert card.get("ok") is True
    assert card.get("pack") == "151"
    assert card.get("readiness_score") == 100
    assert card.get("policy_count", 0) >= 10
    assert card.get("default_deny_present") is True
    assert card.get("no_clearance_no_ob_present") is True
    assert card.get("public_live_automated_locked_present") is True

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "151"
    assert bridge.get("readiness_score") == 100

    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("pack151_policy_link_present") is True
    assert quick.get("pack151_marker") == "PACK151_POLICY_AS_CODE_QUICK_LINK"
    assert "review_policy_as_code_engine" in action_ids
    assert "/tower/policy-as-code-engine.json" in hrefs
    assert quick.get("no_secret_leakage") is True

    assert "PACK151_POLICY_AS_CODE_ENGINE_SECTION" in section
    assert "tower.default_deny" in section
    assert "live.public_automated_locked" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section

    assert panel.get("ok") is True
    assert panel.get("pack") == "151"

    assert "PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE" in unified_html
    assert "PACK151_POLICY_AS_CODE_ENGINE_SECTION" in unified_html
    assert "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in unified_html
    assert "SHOULD_NOT_SURVIVE" not in unified_html
    assert "tower_keycard=" not in unified_html

    assert unified_write.get("ok") is True
    assert unified_write.get("pack") == "151"
    assert unified_write.get("html_length", 0) > 1000

    no_secret(status)
    no_secret(card)
    no_secret(bridge)
    no_secret(loaded)
    no_secret(quick)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 151 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": object_checkpoint.get("status"),
        "checkpoint_readiness": object_checkpoint.get("readiness_score"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert object_checkpoint.get("status") == "passed"
    assert object_checkpoint.get("readiness_score") == 100
    assert object_checkpoint.get("helper_wrapped_count") == 0

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    route_checks = {
        "pack151_route_marker": "PACK151_POLICY_AS_CODE_ENGINE_ROUTE" in app_text,
        "pack151_route_path": "/tower/policy-as-code-engine.json" in app_text,
        "pack151_route_guard": "pack151_policy_as_code_engine_route" in app_text,
        "pack150_route_still_present": "/tower/owner-action-review-readiness-checkpoint.json" in app_text,
    }
    show("PACK 151 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "policy_as_code_engine.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_151.py",
        PROJECT_ROOT / "web" / "app.py",
    ]:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        show("PY_COMPILE " + str(path), {
            "returncode": result.returncode,
            "stderr": result.stderr,
        })
        assert result.returncode == 0

    final = {
        "pack": "151",
        "status": "passed",
        "readiness_score": 100,
        "policy_count": status.get("policy_count"),
        "enabled_policy_count": status.get("enabled_policy_count"),
        "failed_enabled_validation_count": status.get("failed_enabled_validation_count"),
        "default_deny_present": checks.get("default_deny_present"),
        "no_clearance_no_ob_present": checks.get("no_clearance_no_ob_present"),
        "public_live_automated_locked_present": checks.get("public_live_automated_locked_present"),
        "secrets_vault_boundary_present": checks.get("secrets_vault_boundary_present"),
        "quick_action_count": quick.get("action_count"),
        "policy_link_present": True,
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Policy-as-Code Engine foundation is working.",
    }
    show("PACK 151 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
