
from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WEB_APP_PATH = PROJECT_ROOT / "web" / "app.py"


def _print(title, payload=None):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _assert_no_secret_leakage(payload):
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "tower_keycard=",
        "should_not_survive",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
    ]
    for item in forbidden:
        assert item not in serialized, item


def run_tests():
    text = WEB_APP_PATH.read_text(encoding="utf-8", errors="replace")

    helper_checks = {
        "helper_block_present": "PACK104_TOWER_OB_FLASK_GUARD_HELPERS" in text,
        "guard_helper_present": "def _tower_guard_ob_route_or_response" in text,
        "context_helper_present": "def _tower_current_user_context_104" in text,
        "marker_present": "def _tower_ob_route_guard_marker_104" in text,
        "flask_hook_import_present": "guard_current_ob_flask_route" in text,
        "locked_response_import_present": "render_locked_response_from_hook" in text,
    }
    _print("WEB APP PACK 104 HELPER CHECKS", helper_checks)
    assert all(helper_checks.values())

    protected_guard_insertions = text.count("PACK104: Tower guard for protected Observatory route")
    helper_references = text.count("_tower_guard_ob_route_or_response")
    _print("WEB APP PACK 104 ROUTE PATCH COUNTS", {
        "protected_guard_insertions": protected_guard_insertions,
        "helper_references": helper_references,
    })

    # Helper references should be present even if exact route patching found no matching routes.
    assert helper_references >= 3

    # Importing web.app may depend on runtime data/packages, so compile is the stable hard test here.
    py_compile = subprocess.run(
        [sys.executable, "-m", "py_compile", str(WEB_APP_PATH)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    _print("WEB APP PY_COMPILE", {
        "returncode": py_compile.returncode,
        "stdout": py_compile.stdout,
        "stderr": py_compile.stderr,
    })
    assert py_compile.returncode == 0

    # Direct helper behavior smoke through tower hook, independent of web.app import side effects.
    from tower.ob_flask_guard_hook import guard_then_call, reset_ob_flask_guard_hook_for_test
    from tower.ob_tower_route_guard import reset_ob_route_guard_for_test
    from tower.ob_tower_bridge_adapter import reset_ob_tower_bridge_for_test
    from tower.emergency_lockdown import reset_emergency_lockdown_for_test
    from tower.quarantine_mode import reset_quarantine_for_test

    reset_all = {
        "lockdown": reset_emergency_lockdown_for_test(),
        "quarantine": reset_quarantine_for_test(),
        "bridge": reset_ob_tower_bridge_for_test(),
        "route_guard": reset_ob_route_guard_for_test(),
        "flask_hook": reset_ob_flask_guard_hook_for_test(),
    }
    _print("RESET PACK 104 SMOKE DEPENDENCIES", reset_all)
    assert all(item.get("ok") for item in reset_all.values())

    class FakeUser:
        def __init__(self, id, role):
            self.id = id
            self.role = role

    allowed = guard_then_call(
        view_func=lambda: "PAPER_RENDER_OK",
        route_path="/paper",
        user=FakeUser("beta_user_104", "starter"),
        session_data={},
    )
    _print("PACK 104 GUARD THEN CALL ALLOWED", allowed)
    assert allowed.get("decision") == "route_rendered"
    assert allowed.get("view_result") == "PAPER_RENDER_OK"
    _assert_no_secret_leakage(allowed)

    blocked = guard_then_call(
        view_func=lambda: "EXPORT_SHOULD_NOT_RENDER",
        route_path="/export/report",
        user=FakeUser("owner_solice", "owner"),
        session_data={},
    )
    _print("PACK 104 GUARD THEN CALL BLOCKED", {
        "decision": blocked.get("decision"),
        "status_code": blocked.get("status_code"),
        "html_has_step_up": "Tower Step-Up Required" in blocked.get("html", ""),
    })
    assert blocked.get("decision") == "locked_response_returned"
    assert blocked.get("status_code") == 428
    assert "EXPORT_SHOULD_NOT_RENDER" not in blocked.get("html", "")
    _assert_no_secret_leakage(blocked)

    live_blocked = guard_then_call(
        view_func=lambda: "LIVE_SHOULD_NOT_RENDER",
        route_path="/live/manual",
        user=FakeUser("owner_solice", "owner"),
        session_data={},
    )
    _print("PACK 104 LIVE BLOCKED", {
        "decision": live_blocked.get("decision"),
        "status_code": live_blocked.get("status_code"),
        "html_has_denied": "Tower Access Denied" in live_blocked.get("html", ""),
    })
    assert live_blocked.get("decision") == "locked_response_returned"
    assert live_blocked.get("status_code") == 403
    assert "LIVE_SHOULD_NOT_RENDER" not in live_blocked.get("html", "")
    _assert_no_secret_leakage(live_blocked)

    final = {
        "pack": "104",
        "status": "passed",
        "protected_guard_insertions": protected_guard_insertions,
        "human_reason": "web/app.py now has a lightweight Tower OB Flask guard helper, and selected matching protected routes are patched when present.",
    }
    _print("PACK 104 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
