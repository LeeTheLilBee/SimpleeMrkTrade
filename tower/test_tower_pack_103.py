
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path("/content/SimpleeMrkTrade_REAL_CLONE")
os.chdir(PROJECT_ROOT)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

for name in list(sys.modules.keys()):
    if name == "tower" or name.startswith("tower.") or name == "web.app":
        sys.modules.pop(name, None)

from tower.emergency_lockdown import reset_emergency_lockdown_for_test
from tower.quarantine_mode import activate_quarantine, reset_quarantine_for_test
from tower.ob_tower_bridge_adapter import reset_ob_tower_bridge_for_test
from tower.ob_tower_route_guard import reset_ob_route_guard_for_test
from tower.ob_flask_guard_hook import (
    OB_FLASK_GUARD_PANEL_PATH,
    extract_flask_guard_context,
    guard_current_ob_flask_route,
    guard_then_call,
    infer_user_role,
    render_locked_response_from_hook,
    reset_ob_flask_guard_hook_for_test,
    summarize_ob_flask_guard_hook,
)


@dataclass
class FakeUser:
    id: str
    role: str = ""


@dataclass
class FakeRequest:
    path: str
    method: str = "GET"
    remote_addr: str = "127.0.0.1"
    headers: dict = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


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
    reset_all = {
        "lockdown": reset_emergency_lockdown_for_test(),
        "quarantine": reset_quarantine_for_test(),
        "bridge": reset_ob_tower_bridge_for_test(),
        "route_guard": reset_ob_route_guard_for_test(),
        "flask_hook": reset_ob_flask_guard_hook_for_test(),
    }
    _print("RESET OB FLASK GUARD DEPENDENCIES", reset_all)
    assert all(item.get("ok") for item in reset_all.values())

    owner = infer_user_role(user=FakeUser(id="bowdre.solice@gmail.com"))
    beta = infer_user_role(user=FakeUser(id="beta_user_103", role="pro"))
    public = infer_user_role(user=None, session_data={})
    admin = infer_user_role(user=FakeUser(id="manager_103", role="admin"))

    _print("INFER OWNER", owner)
    _print("INFER BETA", beta)
    _print("INFER PUBLIC", public)
    _print("INFER ADMIN", admin)

    assert owner.get("user_id") == "owner_solice"
    assert owner.get("role") == "owner"
    assert beta.get("role") == "beta"
    assert public.get("role") == "public"
    assert admin.get("role") == "admin"

    context = extract_flask_guard_context(
        request_obj=FakeRequest(
            path="/paper",
            method="GET",
            remote_addr="10.0.0.1",
            headers={
                "X-Forwarded-For": "203.0.113.10, 10.0.0.1",
                "X-Session-ID": "sess_103",
                "X-Device-ID": "device_103",
                "Authorization": "Bearer SHOULD_NOT_SURVIVE",
            },
        ),
        user=FakeUser(id="beta_user_103", role="starter"),
        metadata={
            "raw_token": "SHOULD_NOT_SURVIVE",
            "safe": "ok",
        },
    )
    _print("EXTRACT FLASK GUARD CONTEXT", context)

    assert context.get("user_id") == "beta_user_103"
    assert context.get("role") == "beta"
    assert context.get("route_path") == "/paper"
    assert context.get("method") == "GET"
    assert context.get("ip_address") == "203.0.113.10"
    assert context.get("session_id") == "sess_103"
    assert context.get("device_id") == "device_103"
    _assert_no_secret_leakage(context)

    public_hook = guard_current_ob_flask_route(
        request_obj=FakeRequest(path="/signals-spotlight"),
        user=None,
        session_data={},
        metadata={"api_key": "SHOULD_NOT_SURVIVE"},
    )
    _print("PUBLIC FLASK HOOK", public_hook)

    assert public_hook.get("decision") == "allow"
    assert public_hook.get("allowed") is True
    assert public_hook.get("should_render_route") is True
    _assert_no_secret_leakage(public_hook)

    owner_hook = guard_current_ob_flask_route(
        request_obj=FakeRequest(path="/observatory-private"),
        user=FakeUser(id="owner_solice", role="owner"),
        session_data={},
    )
    _print("OWNER OB ENTRY FLASK HOOK", owner_hook)

    assert owner_hook.get("decision") == "allow"
    assert owner_hook.get("allowed") is True
    _assert_no_secret_leakage(owner_hook)

    beta_paper_hook = guard_current_ob_flask_route(
        request_obj=FakeRequest(path="/paper"),
        user=FakeUser(id="beta_user_103", role="free"),
        session_data={},
    )
    _print("BETA PAPER FLASK HOOK", beta_paper_hook)

    assert beta_paper_hook.get("decision") == "allow"
    assert beta_paper_hook.get("allowed") is True
    _assert_no_secret_leakage(beta_paper_hook)

    export_hook = guard_current_ob_flask_route(
        request_obj=FakeRequest(path="/export/report"),
        user=FakeUser(id="owner_solice", role="owner"),
        session_data={},
    )
    _print("EXPORT FLASK HOOK STEP-UP", export_hook)

    assert export_hook.get("decision") == "step_up_required"
    assert export_hook.get("allowed") is False
    assert export_hook.get("locked_page_kind") == "step_up"
    _assert_no_secret_leakage(export_hook)

    html, status_code = render_locked_response_from_hook(export_hook)
    _print("EXPORT LOCKED RESPONSE", {"status_code": status_code, "html_length": len(html)})
    assert status_code == 428
    assert "Tower Step-Up Required" in html
    assert "SHOULD_NOT_SURVIVE" not in html

    live_hook = guard_current_ob_flask_route(
        request_obj=FakeRequest(path="/live/manual"),
        user=FakeUser(id="owner_solice", role="owner"),
        session_data={},
    )
    _print("LIVE FLASK HOOK DENIED", live_hook)

    assert live_hook.get("decision") == "deny"
    assert live_hook.get("allowed") is False
    assert live_hook.get("locked_page_kind") == "denied"
    _assert_no_secret_leakage(live_hook)

    rendered = guard_then_call(
        view_func=lambda: "PAPER_VIEW_RENDERED",
        route_path="/paper",
        user=FakeUser(id="beta_user_103", role="starter"),
        session_data={},
    )
    _print("GUARD THEN CALL ALLOWED", rendered)

    assert rendered.get("decision") == "route_rendered"
    assert rendered.get("view_result") == "PAPER_VIEW_RENDERED"
    _assert_no_secret_leakage(rendered)

    locked = guard_then_call(
        view_func=lambda: "SHOULD_NOT_RENDER",
        route_path="/export/report",
        user=FakeUser(id="owner_solice", role="owner"),
        session_data={},
    )
    _print("GUARD THEN CALL LOCKED", {"decision": locked.get("decision"), "status_code": locked.get("status_code"), "html_len": len(locked.get("html", ""))})

    assert locked.get("decision") == "locked_response_returned"
    assert locked.get("status_code") == 428
    assert "SHOULD_NOT_RENDER" not in locked.get("html", "")
    _assert_no_secret_leakage(locked)

    quarantine_case = activate_quarantine(
        actor_user_id="owner_solice",
        scope="user",
        target={"user_id": "quarantined_flask_user_103"},
        reason_code="pack103_flask_hook_test",
        human_reason="Pack 103 Flask hook quarantine test.",
        severity="restricted",
    )
    _print("ACTIVATE QUARANTINE FOR FLASK HOOK", quarantine_case)
    assert quarantine_case.get("ok") is True

    quarantine_hook = guard_current_ob_flask_route(
        request_obj=FakeRequest(path="/observatory-private"),
        user=FakeUser(id="quarantined_flask_user_103", role="beta"),
        session_data={},
    )
    _print("QUARANTINE FLASK HOOK", quarantine_hook)

    assert quarantine_hook.get("decision") == "quarantine"
    assert quarantine_hook.get("allowed") is False
    assert quarantine_hook.get("locked_page_kind") == "quarantine"
    _assert_no_secret_leakage(quarantine_hook)

    summary = summarize_ob_flask_guard_hook(limit=100)
    _print("OB FLASK GUARD HOOK SUMMARY", summary)

    assert summary.get("ok") is True
    assert summary.get("readiness_score") == 100
    assert summary.get("readiness_label") == "OB Flask guard hook ready"
    assert summary.get("event_count", 0) >= 8
    assert summary.get("by_decision", {}).get("allow", 0) >= 4
    assert summary.get("by_decision", {}).get("step_up_required", 0) >= 2
    assert summary.get("by_decision", {}).get("deny", 0) >= 1
    assert summary.get("by_decision", {}).get("quarantine", 0) >= 1
    assert summary.get("no_secret_leakage") is True
    assert OB_FLASK_GUARD_PANEL_PATH.exists()
    _assert_no_secret_leakage(summary)

    html = OB_FLASK_GUARD_PANEL_PATH.read_text(encoding="utf-8")
    assert "The Tower · OB Flask Guard Hook" in html
    assert "SHOULD_NOT_SURVIVE" not in html
    assert "tower_keycard=" not in html

    final = {
        "pack": "103",
        "status": "passed",
        "human_reason": "OB Flask guard hook provides clean route-context extraction, guard execution, locked response rendering, and guard-then-call helper without leaking secrets.",
    }
    _print("PACK 103 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
