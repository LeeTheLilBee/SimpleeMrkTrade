
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


def run_tests():
    from tower.security_inbox_owner_queue import (
        SECURITY_INBOX_PANEL_PATH,
        SECURITY_INBOX_STATUS_PATH,
        build_security_inbox_owner_queue,
        load_security_inbox_owner_queue,
        render_security_inbox_owner_queue_section,
        reset_security_inbox_owner_queue_for_test,
        security_inbox_owner_queue_status_card,
        write_security_inbox_owner_queue_panel,
    )
    from tower.ob_object_permission_tightening import (
        check_export_permission,
        check_position_permission,
        evaluate_ob_object_permission,
        reset_ob_object_permissions_for_test,
    )
    try:
        from tower.redaction_reveal_system import reset_reveal_system_for_test as reset_redaction_reveal_system_for_test
    except Exception:
        try:
            from tower.redaction_reveal_system import reset_redaction_reveal_system_for_test
        except Exception:
            reset_redaction_reveal_system_for_test = None

    try:
        from tower.redaction_reveal_system import request_sensitive_reveal
    except Exception:
        request_sensitive_reveal = None
    try:
        from tower.secrets_vault_boundary import reset_secrets_boundary_for_test
    except Exception:
        reset_secrets_boundary_for_test = None

    try:
        from tower.secrets_vault_boundary import reject_raw_secret_value
    except Exception:
        try:
            from tower.secrets_vault_boundary import reject_raw_secret as reject_raw_secret_value
        except Exception:
            reject_raw_secret_value = None
    from tower.ob_route_coverage_report import build_ob_route_coverage_report
    from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

    reset_inbox = reset_security_inbox_owner_queue_for_test()
    reset_objects = reset_ob_object_permissions_for_test()

    show("RESET PACK 121 SECURITY INBOX", reset_inbox)
    show("RESET OBJECT PERMISSIONS", reset_objects)

    assert reset_inbox.get("ok") is True
    assert reset_objects.get("ok") is True

    # Seed representative security activity.
    position_deny = check_position_permission(
        user_id="beta_121",
        role="beta",
        position_id="pos_other_121",
        object_payload={"owner_user_id": "other_user"},
    )
    position_step = check_position_permission(
        user_id="beta_121",
        role="beta",
        position_id="pos_mine_121",
        action="close",
        object_payload={"owner_user_id": "beta_121"},
    )
    export_step = check_export_permission(
        user_id="owner_solice",
        role="owner",
        export_id="export_121",
    )
    analysis_summary = evaluate_ob_object_permission(
        user_id="beta_121",
        role="beta",
        object_type="analysis",
        object_id="analysis_121",
        action="view",
    )

    show("PACK 121 SEEDED OBJECT EVENTS", {
        "position_deny": position_deny.get("decision"),
        "position_step": position_step.get("decision"),
        "export_step": export_step.get("decision"),
        "analysis_summary": analysis_summary.get("decision"),
    })

    assert position_deny.get("decision") == "deny"
    assert position_step.get("decision") == "step_up_required"
    assert export_step.get("decision") == "step_up_required"
    assert analysis_summary.get("decision") == "summary_only"

    try:
        if reset_redaction_reveal_system_for_test is None or request_sensitive_reveal is None:
            raise RuntimeError("redaction_reveal_seed_helpers_unavailable")
        reset_redaction_reveal_system_for_test()
        reveal = request_sensitive_reveal(
            actor_user_id="owner_solice",
            app_id="teller",
            object_type="worker_profile",
            object_id="worker_121",
            action="reveal_payroll_detail",
            route_path="/tower/security-command",
            has_base_clearance=False,
            has_object_permission=False,
            step_up_verified=False,
            payload={"email": "worker@example.com", "bank_account": "123456789", "safe": "visible"},
            requested_fields=["email"],
            reason="Pack 121 inbox seed.",
            metadata={"session_id": "sess_should_not_survive_121"},
        )
        show("PACK 121 SEEDED REVEAL EVENT", {
            "decision": reveal.get("decision"),
            "reason_code": reveal.get("reason_code"),
        })
    except Exception as exc:
        show("PACK 121 REVEAL SEED SKIPPED", {"error_type": type(exc).__name__})

    try:
        if reset_secrets_boundary_for_test is None or reject_raw_secret_value is None:
            raise RuntimeError("secrets_boundary_seed_helpers_unavailable")
        reset_secrets_boundary_for_test()
        raw_secret = reject_raw_secret_value(
            actor_user_id="owner_solice",
            app_id="tower",
            secret_type="github_token",
            alias="repo_push_token",
            raw_secret_value="ghp_should_not_survive_pack121",
            request_metadata={"pack": "121"},
        )
        show("PACK 121 SEEDED RAW SECRET REJECTION", {
            "ok": raw_secret.get("ok"),
            "decision": raw_secret.get("decision"),
            "reason_code": raw_secret.get("reason_code"),
        })
    except Exception as exc:
        show("PACK 121 SECRET SEED SKIPPED", {"error_type": type(exc).__name__})

    status = build_security_inbox_owner_queue(limit_per_source=80, write_panel=True)

    show("PACK 121 SECURITY INBOX STATUS", {
        "ok": status.get("ok"),
        "status": status.get("status"),
        "readiness_score": status.get("readiness_score"),
        "source_count": status.get("source_count"),
        "inbox_count": status.get("inbox_count"),
        "owner_review_count": status.get("owner_review_count"),
        "by_source": status.get("by_source"),
        "by_severity": status.get("by_severity"),
        "failed_checks": status.get("failed_checks"),
        "no_secret_leakage": status.get("no_secret_leakage"),
    })

    assert status.get("ok") is True
    assert status.get("status") == "passed"
    assert status.get("readiness_score") == 100
    assert status.get("source_count", 0) >= 7
    assert status.get("inbox_count", 0) >= 1
    assert status.get("owner_review_count", 0) >= 1
    assert status.get("failed_checks") == []
    assert status.get("no_secret_leakage") is True
    assert SECURITY_INBOX_STATUS_PATH.exists()
    assert SECURITY_INBOX_PANEL_PATH.exists()
    no_secret(status)

    section = render_security_inbox_owner_queue_section(status)
    show("PACK 121 SECURITY INBOX HTML CHECK", {
        "html_length": len(section),
        "has_marker": "PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION" in section,
        "has_title": "Tower Security Inbox" in section,
        "has_owner_review": "Owner Review" in section,
    })

    assert "PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION" in section
    assert "Tower Security Inbox" in section
    assert "Owner Review" in section
    assert "SHOULD_NOT_SURVIVE" not in section
    assert "tower_keycard=" not in section
    assert "ghp_should" not in section

    panel = write_security_inbox_owner_queue_panel(status)
    show("PACK 121 PANEL WRITE", panel)
    assert panel.get("ok") is True
    assert SECURITY_INBOX_PANEL_PATH.exists()

    card = security_inbox_owner_queue_status_card()
    loaded = load_security_inbox_owner_queue()

    show("PACK 121 STATUS CARD", card)
    show("PACK 121 LOADED STATUS", {
        "ok": loaded.get("ok"),
        "status": loaded.get("status"),
        "readiness_score": loaded.get("readiness_score"),
        "inbox_count": loaded.get("inbox_count"),
        "owner_review_count": loaded.get("owner_review_count"),
    })

    assert card.get("ok") is True
    assert card.get("pack") == "121"
    assert card.get("readiness_score") == 100
    assert card.get("inbox_count", 0) >= 1
    assert card.get("owner_review_count", 0) >= 1
    assert loaded.get("ok") is True
    assert loaded.get("status") == "passed"
    assert loaded.get("readiness_score") == 100
    no_secret(card)
    no_secret(loaded)

    route_report = build_ob_route_coverage_report(write_panel=True)
    checkpoint = build_object_permission_integration_checkpoint(write_panel=True)

    show("PACK 121 FINAL HEALTH", {
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "unguarded_needed_count": route_report.get("unguarded_needed_count"),
        "unguarded_high_risk_count": route_report.get("unguarded_high_risk_count"),
        "checkpoint_status": checkpoint.get("status"),
        "checkpoint_readiness": checkpoint.get("readiness_score"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
    })

    assert route_report.get("coverage_pct") == 100
    assert route_report.get("unguarded_needed_count") == 0
    assert route_report.get("unguarded_high_risk_count") == 0
    assert checkpoint.get("status") == "passed"
    assert checkpoint.get("readiness_score") == 100
    assert checkpoint.get("helper_wrapped_count") == 0

    app_text = WEB_APP.read_text(encoding="utf-8", errors="replace")
    app_checks = {
        "pack121_route_marker": "PACK121_SECURITY_INBOX_OWNER_QUEUE_ROUTE" in app_text,
        "pack121_route_path": "/tower/security-inbox.json" in app_text,
        "pack121_route_guard": "pack121_security_inbox_owner_queue_route" in app_text,
    }
    show("PACK 121 WEB APP ROUTE CHECKS", app_checks)
    assert all(app_checks.values())

    for path in [
        PROJECT_ROOT / "tower" / "security_inbox_owner_queue.py",
        PROJECT_ROOT / "tower" / "test_tower_pack_121.py",
        PROJECT_ROOT / "tower" / "security_command_owner_ui_checkpoint.py",
        PROJECT_ROOT / "tower" / "security_command_owner_quick_actions.py",
        PROJECT_ROOT / "tower" / "security_command_unified_owner_page.py",
        PROJECT_ROOT / "tower" / "security_command_preferred_destination.py",
        PROJECT_ROOT / "tower" / "security_command_navigation_links.py",
        PROJECT_ROOT / "tower" / "security_command_composition_smoke.py",
        PROJECT_ROOT / "tower" / "security_command_object_visibility_integration.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_visibility.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_tightening.py",
        PROJECT_ROOT / "tower" / "ob_object_permission_integration_checkpoint.py",
        PROJECT_ROOT / "tower" / "redaction_reveal_system.py",
        PROJECT_ROOT / "tower" / "secrets_vault_boundary.py",
        PROJECT_ROOT / "tower" / "security_command_page.py",
        PROJECT_ROOT / "tower" / "tower_status.py",
        PROJECT_ROOT / "web" / "app.py",
    ]:
        if path.exists():
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
        "pack": "121",
        "status": "passed",
        "readiness_score": status.get("readiness_score"),
        "inbox_count": status.get("inbox_count"),
        "owner_review_count": status.get("owner_review_count"),
        "route_coverage_pct": route_report.get("coverage_pct"),
        "guarded_needed_count": route_report.get("guarded_needed_count"),
        "needs_guard_count": route_report.get("needs_guard_count"),
        "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
        "human_reason": "Tower Security Inbox owner queue collects important security activity into one review queue.",
    }
    show("PACK 121 RESULT", final)
    return final


if __name__ == "__main__":
    run_tests()
