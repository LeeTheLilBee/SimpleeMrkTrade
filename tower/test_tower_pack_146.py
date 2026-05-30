
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


def run_fast(label: str, code: str, timeout: int = 15):
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
    from tower.owner_action_review_checkpoint import (
        build_owner_action_review_checkpoint,
        owner_action_review_checkpoint_status_card,
    )
    from tower.security_command_owner_quick_actions import build_owner_quick_actions_status
    from tower.security_command_unified_owner_page import (
        render_unified_owner_security_command_html,
        write_unified_owner_security_command_html,
    )
    from tower.tower_status import pack146_owner_action_review_checkpoint_status_bridge
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    run_fast(
        "FAST PACK 146 QUICK ACTIONS",
        "from tower.security_command_owner_quick_actions import build_owner_quick_actions_status; "
        "s=build_owner_quick_actions_status(write_panel=False); "
        "print(s.get('status'), s.get('action_count'), s.get('pack146_owner_action_review_checkpoint_link_present'))",
        timeout=15,
    )

    run_fast(
        "FAST PACK 146 UNIFIED HTML",
        "from tower.security_command_unified_owner_page import render_unified_owner_security_command_html; "
        "h=render_unified_owner_security_command_html(); "
        "print(len(h), 'PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT' in h, 'PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION' in h)",
        timeout=20,
    )

    checkpoint = build_owner_action_review_checkpoint(write_panel=True)
    card = owner_action_review_checkpoint_status_card()
    bridge = pack146_owner_action_review_checkpoint_status_bridge()
    quick = build_owner_quick_actions_status(write_panel=True)
    html = render_unified_owner_security_command_html()
    write_result = write_unified_owner_security_command_html()

    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    action_ids = {
        action.get("action_id")
        for action in actions
        if isinstance(action, dict)
    }
    hrefs = {
        action.get("href")
        for action in actions
        if isinstance(action, dict)
    }

    show("PACK 146 CHECKPOINT", {
        "ok": checkpoint.get("ok"),
        "pack": checkpoint.get("pack"),
        "status": checkpoint.get("status"),
        "readiness_score": checkpoint.get("readiness_score"),
        "review_depth": checkpoint.get("review_depth"),
        "no_secret_leakage": checkpoint.get("no_secret_leakage"),
    })

    show("PACK 146 STATUS CARD", card)
    show("PACK 146 TOWER STATUS BRIDGE", bridge)

    show("PACK 146 QUICK ACTIONS", {
        "ok": quick.get("ok"),
        "status": quick.get("status"),
        "readiness_score": quick.get("readiness_score"),
        "action_count": quick.get("action_count"),
        "has_pack146_marker": quick.get("pack146_marker") == "PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_QUICK_ACTIONS",
        "has_review_action_id": "review_owner_action_review_checkpoint" in action_ids,
        "has_review_href": "/tower/owner-action-review-checkpoint.json" in hrefs,
        "no_secret_leakage": quick.get("no_secret_leakage"),
    })

    show("PACK 146 UNIFIED HTML CHECK", {
        "html_length": len(html),
        "has_pack146_marker": "PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT" in html,
        "has_pack145_section": "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in html,
        "has_title": "Owner Action Review-State Checkpoint" in html,
    })

    show("PACK 146 WRITE UNIFIED HTML", write_result)

    assert checkpoint.get("ok") is True
    assert checkpoint.get("pack") == "145"
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("review_depth", {}).get("score") == 100
    assert checkpoint.get("no_secret_leakage") is True

    assert card.get("ok") is True
    assert card.get("pack") == "145"
    assert card.get("readiness_score") == 100
    assert card.get("review_depth_score") == 100

    assert bridge.get("ok") is True
    assert bridge.get("pack") == "145"
    assert bridge.get("readiness_score") == 100
    assert bridge.get("review_depth_score") == 100

    assert quick.get("ok") is True
    assert quick.get("status") == "passed"
    assert quick.get("pack146_owner_action_review_checkpoint_link_present") is True
    assert quick.get("pack146_marker") == "PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_QUICK_ACTIONS"
    assert "review_owner_action_review_checkpoint" in action_ids
    assert "/tower/owner-action-review-checkpoint.json" in hrefs
    assert quick.get("action_count", 0) >= 1
    assert quick.get("no_secret_leakage") is True

    assert "PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT" in html
    assert "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in html
    assert "Owner Action Review-State Checkpoint" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    assert write_result.get("ok") is True
    assert write_result.get("pack") == "146"
    assert write_result.get("html_length", 0) > 1000

    no_secret(checkpoint)
    no_secret(card)
    no_secret(bridge)
    no_secret(quick)

    route_report = build_ob_route_coverage_report(write_panel=True)
    object_checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 146 FINAL HEALTH", {
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
        "pack146_route_marker": "PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_CARD_ROUTE" in app_text,
        "pack146_route_path": "/tower/owner-action-review-checkpoint-card.json" in app_text,
        "pack146_route_guard": "pack146_owner_action_review_checkpoint_card_route" in app_text,
        "pack145_route_still_present": "/tower/owner-action-review-checkpoint.json" in app_text,
    }
    show("PACK 146 WEB APP ROUTE CHECKS", route_checks)
    assert all(route_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "tower" / "owner_action_review_checkpoint.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_146.py",
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
        "pack": "146",
        "status": "passed",
        "readiness_score": 100,
        "quick_action_count": quick.get("action_count"),
        "review_checkpoint_link_present": True,
        "unified_has_review_checkpoint": True,
        "bridge_readiness_score": bridge.get("readiness_score"),
        "review_depth_score": checkpoint.get("review_depth", {}).get("score"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        "human_reason": "Owner Action Review Checkpoint is integrated into quick actions and unified UI.",
    }
    show("PACK 146 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
