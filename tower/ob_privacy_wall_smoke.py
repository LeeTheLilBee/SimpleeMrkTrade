
from __future__ import annotations

from typing import Any, Dict


def _ok_detail(ok: bool, detail: Any = None) -> Dict[str, Any]:
    return {"ok": bool(ok), "detail": detail}


def run_ob_privacy_wall_smoke() -> Dict[str, Any]:
    from pathlib import Path

    from web.app import app
    from tower.ob_route_guard import evaluate_ob_request_guard
    from tower.ob_object_guard import evaluate_ob_object_guard
    from tower.ob_mode_clearance import evaluate_ob_mode_clearance
    from tower.ob_route_exposure_report import build_ob_route_exposure_report
    from tower.ob_object_audit_capsules import (
        summarize_ob_object_audit_capsules,
        summarize_ob_object_security_inbox,
    )
    from tower.tower_status import get_tower_status
    from tower.security_command_page import generate_security_command_dashboard

    checks = {}
    failures = []

    def check(name: str, ok: bool, detail=None):
        checks[name] = _ok_detail(ok, detail)
        if not ok:
            failures.append(name)

    client = app.test_client()

    route_owner = evaluate_ob_request_guard(path="/signals", user_id="owner_solice", role="owner")
    route_beta = evaluate_ob_request_guard(path="/signals", user_id="beta_001", role="user")
    route_unmapped = evaluate_ob_request_guard(path="/unknown-private-route", user_id="owner_solice", role="owner")

    check(
        "route_guard_allows_owner_blocks_beta_default_denies",
        route_owner.get("allowed") is True
        and route_beta.get("allowed") is False
        and route_unmapped.get("reason_code") == "ob_route_unmapped_default_deny",
        {
            "owner": route_owner.get("reason_code"),
            "beta": route_beta.get("reason_code"),
            "unmapped": route_unmapped.get("reason_code"),
        },
    )

    symbol_owner = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="symbol",
        object_id="AAPL",
        route_key="symbol_detail",
    )
    symbol_beta = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="symbol",
        object_id="AAPL",
        route_key="symbol_detail",
    )
    trade_owner = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="trade",
        object_id="trade_060",
        owner_user_id="owner_solice",
        route_key="positions",
    )
    export_beta = evaluate_ob_object_guard(
        user_id="beta_001",
        role="user",
        object_kind="export",
        object_id="export_060",
        route_key="export",
        action="download",
    )
    unmapped_object = evaluate_ob_object_guard(
        user_id="owner_solice",
        role="owner",
        object_kind="unknown_drawer_060",
        object_id="secret_060",
        route_key="",
        action="view",
    )

    check(
        "object_guard_symbols_trades_exports_unmapped",
        symbol_owner.get("allowed") is True
        and symbol_beta.get("allowed") is False
        and trade_owner.get("allowed") is True
        and export_beta.get("allowed") is False
        and unmapped_object.get("reason_code") == "ob_object_unmapped_default_deny",
        {
            "symbol_owner": symbol_owner.get("reason_code"),
            "symbol_beta": symbol_beta.get("reason_code"),
            "trade_owner": trade_owner.get("reason_code"),
            "export_beta": export_beta.get("reason_code"),
            "unmapped_object": unmapped_object.get("reason_code"),
        },
    )

    mode_survey = evaluate_ob_mode_clearance(
        user_id="beta_001",
        role="user",
        mode_name="survey",
        action="enter",
    )
    mode_paper_beta = evaluate_ob_mode_clearance(
        user_id="beta_001",
        role="user",
        mode_name="paper",
        action="enter",
    )
    mode_auto_owner = evaluate_ob_mode_clearance(
        user_id="owner_solice",
        role="owner",
        mode_name="live_automated",
        action="enter",
        broker_connected=True,
        broker_healthy=True,
        live_authorized=True,
        automation_authorized=True,
    )

    check(
        "mode_guard_survey_paper_live_auto",
        mode_survey.get("allowed") is True
        and mode_paper_beta.get("allowed") is False
        and mode_auto_owner.get("allowed") is True,
        {
            "survey": mode_survey.get("reason_code"),
            "paper_beta": mode_paper_beta.get("reason_code"),
            "auto_owner": mode_auto_owner.get("reason_code"),
        },
    )

    beta_symbol_route = client.get("/signals/AAPL?ob_user_id=beta_001&ob_role=user")
    beta_export_route = client.get("/export?export_id=export_060&ob_user_id=beta_001&ob_role=user")
    live_auto_no_auth_route = client.get(
        "/mode/live_automated?ob_user_id=owner_solice&ob_role=owner"
        "&broker_connected=true&broker_healthy=true&live_authorized=true&automation_authorized=false"
    )
    no_access = client.get("/no-access?path=/signals")
    unmapped = client.get("/random-unmapped-private-route")

    check(
        "flask_routes_lock_private_surfaces",
        beta_symbol_route.status_code == 403
        and beta_export_route.status_code == 403
        and live_auto_no_auth_route.status_code == 403
        and no_access.status_code == 403
        and unmapped.status_code == 403,
        {
            "beta_symbol": beta_symbol_route.status_code,
            "beta_export": beta_export_route.status_code,
            "live_auto_no_auth": live_auto_no_auth_route.status_code,
            "no_access": no_access.status_code,
            "unmapped": unmapped.status_code,
        },
    )

    exposure = build_ob_route_exposure_report(app=app)
    check(
        "exposure_report_loads",
        exposure.get("ok") is True and exposure.get("default_deny_active") is True,
        {
            "counts": exposure.get("counts"),
            "attention_count": exposure.get("attention_count"),
        },
    )

    object_audit = summarize_ob_object_audit_capsules(limit=8)
    object_inbox = summarize_ob_object_security_inbox(limit=8)

    check(
        "object_audit_capsules_active",
        object_audit.get("ok") is True
        and object_audit.get("total", 0) >= 1
        and object_audit.get("denied", 0) >= 1
        and isinstance(object_audit.get("by_reason"), dict),
        {
            "total": object_audit.get("total"),
            "allowed": object_audit.get("allowed"),
            "denied": object_audit.get("denied"),
            "by_reason": object_audit.get("by_reason"),
        },
    )

    check(
        "object_security_inbox_active",
        object_inbox.get("ok") is True
        and object_inbox.get("total", 0) >= 1
        and object_inbox.get("open", 0) >= 1
        and isinstance(object_inbox.get("by_object_type"), dict),
        {
            "total": object_inbox.get("total"),
            "open": object_inbox.get("open"),
            "by_object_type": object_inbox.get("by_object_type"),
            "by_severity": object_inbox.get("by_severity"),
        },
    )

    status = get_tower_status()
    check(
        "tower_status_has_object_audit_and_inbox",
        status.get("ob_object_audit_ok") is True
        and status.get("ob_object_security_inbox_ok") is True
        and status.get("ob_object_audit_total", 0) >= 1
        and status.get("ob_object_security_inbox_total", 0) >= 1,
        {
            "ob_object_audit_total": status.get("ob_object_audit_total"),
            "ob_object_security_inbox_total": status.get("ob_object_security_inbox_total"),
            "ob_object_security_inbox_open": status.get("ob_object_security_inbox_open"),
        },
    )

    dashboard = generate_security_command_dashboard()
    html_ok = False
    html_bytes = 0
    dashboard_path = dashboard.get("path") if isinstance(dashboard, dict) else ""

    try:
        html_path = Path(dashboard_path)
        html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
        html_bytes = html_path.stat().st_size if html_path.exists() else 0
        html_ok = "OB OBJECT SECURITY INBOX" in html and "Drawer Review Queue" in html
    except Exception:
        html_ok = False

    check(
        "security_command_ui_has_object_inbox_panel",
        isinstance(dashboard, dict)
        and dashboard.get("ok") is True
        and dashboard.get("ob_object_security_inbox_ok") is True
        and html_ok,
        {
            "dashboard_ok": dashboard.get("ok") if isinstance(dashboard, dict) else None,
            "object_inbox_ok": dashboard.get("ob_object_security_inbox_ok") if isinstance(dashboard, dict) else None,
            "path": dashboard_path,
            "bytes": html_bytes,
            "html_has_panel": html_ok,
        },
    )

    serialized = str([checks, failures, status, dashboard])
    check(
        "no_raw_keycard_leakage",
        "tower_keycard=" not in serialized
        and "raw_token" not in serialized
        and "SHOULD_NOT_SURVIVE" not in serialized,
        None,
    )

    return {
        "ok": not failures,
        "pack": "060",
        "checks": checks,
        "failures": failures,
        "human_reason": "OB privacy wall smoke test passed with object audit, object inbox, Tower status, and UI surfacing."
        if not failures
        else "OB privacy wall smoke test found failures.",
    }


if __name__ == "__main__":
    import json

    result = run_ob_privacy_wall_smoke()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("OB privacy wall smoke failed.")



# ================================================================================
# PACK062_OBJECT_INBOX_ACTION_WORKFLOW_SMOKE_WRAPPER
# ================================================================================
# Adds proof that object security inbox items can be noted, reviewed, resolved,
# and ignored, without rewriting the entire smoke runner.
# ================================================================================

def _pack062_prove_object_inbox_action_workflow():
    try:
        from tower.ob_object_guard import evaluate_ob_object_guard
        from tower.ob_object_audit_capsules import (
            add_note_to_ob_object_security_inbox_item,
            ignore_ob_object_security_inbox_item,
            list_open_ob_object_security_inbox,
            mark_ob_object_security_inbox_reviewing,
            resolve_ob_object_security_inbox_item,
        )

        detail = {}

        decision = evaluate_ob_object_guard(
            user_id="beta_001",
            role="user",
            object_kind="export",
            object_id="export_062_workflow",
            action="download",
            route_key="export",
            current_risk_score=5,
        )
        detail["decision_reason"] = decision.get("reason_code")

        open_items = list_open_ob_object_security_inbox(limit=80)
        target = None
        for item in reversed(open_items.get("items", [])):
            if item.get("object_id") == "export_062_workflow":
                target = item
                break

        detail["found_review_target"] = bool(target)

        if not target:
            return {"ok": False, "detail": detail, "human_reason": "No workflow target item was found."}

        target_id = target.get("inbox_item_id")
        note = add_note_to_ob_object_security_inbox_item(
            target_id,
            actor_user_id="owner_solice",
            note="Pack 062 smoke: note before review.",
        )
        reviewing = mark_ob_object_security_inbox_reviewing(
            target_id,
            actor_user_id="owner_solice",
            note="Pack 062 smoke: reviewing object inbox workflow.",
        )
        resolved = resolve_ob_object_security_inbox_item(
            target_id,
            actor_user_id="owner_solice",
            note="Pack 062 smoke: resolved object inbox workflow.",
            resolution_reason="smoke_test_expected_block",
        )

        detail.update({
            "target_id": target_id,
            "note_ok": note.get("ok"),
            "reviewing_status": reviewing.get("new_status"),
            "resolved_status": resolved.get("new_status"),
            "resolved_by": resolved.get("item", {}).get("resolved_by"),
            "history_count": len(resolved.get("item", {}).get("history", [])),
            "owner_notes_count": len(resolved.get("item", {}).get("owner_notes", [])),
        })

        decision_2 = evaluate_ob_object_guard(
            user_id="owner_solice",
            role="owner",
            object_kind="unknown_drawer_062",
            object_id="secret_062_workflow",
            action="view",
            route_key="",
            current_risk_score=5,
        )
        detail["ignore_decision_reason"] = decision_2.get("reason_code")

        open_items_2 = list_open_ob_object_security_inbox(limit=100)
        ignore_target = None
        for item in reversed(open_items_2.get("items", [])):
            if item.get("object_id") == "secret_062_workflow":
                ignore_target = item
                break

        detail["found_ignore_target"] = bool(ignore_target)

        ignored_ok = False
        if ignore_target:
            ignored = ignore_ob_object_security_inbox_item(
                ignore_target.get("inbox_item_id"),
                actor_user_id="owner_solice",
                note="Pack 062 smoke: ignored test-generated unmapped object.",
                resolution_reason="smoke_test_noise",
            )
            detail.update({
                "ignore_id": ignore_target.get("inbox_item_id"),
                "ignored_status": ignored.get("new_status"),
                "ignored_by": ignored.get("item", {}).get("ignored_by"),
            })
            ignored_ok = (
                ignored.get("new_status") == "ignored"
                and ignored.get("item", {}).get("ignored_by") == "owner_solice"
            )

        workflow_ok = (
            note.get("ok") is True
            and reviewing.get("new_status") == "reviewing"
            and resolved.get("new_status") == "resolved"
            and resolved.get("item", {}).get("resolved_by") == "owner_solice"
            and len(resolved.get("item", {}).get("history", [])) >= 2
            and ignored_ok
        )

        return {
            "ok": workflow_ok,
            "detail": detail,
            "human_reason": "Object inbox action workflow proved." if workflow_ok else "Object inbox action workflow failed.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Object inbox action workflow raised an exception.",
        }


try:
    _pack062_original_run_ob_privacy_wall_smoke
except NameError:
    _pack062_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack062_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    workflow = _pack062_prove_object_inbox_action_workflow()
    checks["object_security_inbox_action_workflow"] = {
        "ok": workflow.get("ok") is True,
        "detail": workflow.get("detail"),
    }

    if workflow.get("ok") is not True and "object_security_inbox_action_workflow" not in failures:
        failures.append("object_security_inbox_action_workflow")

    result["ok"] = not failures
    result["pack"] = "062"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with object inbox action workflow."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result



# ================================================================================
# PACK065_FINAL_SECURITY_BLOCK_SMOKE_WRAPPER
# ================================================================================
# Adds proof for:
# - Tower UI object inbox action forms
# - Archive Vault handoff queue
# - final no-secret leakage check
# ================================================================================

def _pack065_prove_ui_actions_and_archive_handoff():
    try:
        from pathlib import Path
        from tower.security_command_page import generate_security_command_dashboard
        from tower.ob_object_guard import evaluate_ob_object_guard
        from tower.ob_object_audit_capsules import (
            list_open_ob_object_security_inbox,
            queue_ob_object_security_inbox_item_for_archive,
        )
        from tower.archive_vault_handoff import summarize_archive_vault_handoffs

        detail = {}

        dashboard = generate_security_command_dashboard()
        html_path = Path(dashboard.get("path", "")) if isinstance(dashboard, dict) else Path("")
        html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""

        ui_ok = (
            isinstance(dashboard, dict)
            and dashboard.get("ok") is True
            and "OB OBJECT SECURITY INBOX" in html
            and "/tower/security-command/object-inbox/action" in html
            and 'name="action_type"' in html
            and 'value="reviewing"' in html
            and 'value="resolve"' in html
            and 'value="ignore"' in html
            and "Add Note" in html
        )

        detail.update({
            "dashboard_ok": dashboard.get("ok") if isinstance(dashboard, dict) else None,
            "dashboard_path": str(html_path),
            "html_has_object_inbox": "OB OBJECT SECURITY INBOX" in html,
            "html_has_action_endpoint": "/tower/security-command/object-inbox/action" in html,
            "html_has_reviewing": 'value="reviewing"' in html,
            "html_has_resolve": 'value="resolve"' in html,
            "html_has_ignore": 'value="ignore"' in html,
            "html_has_add_note": "Add Note" in html,
        })

        before = summarize_archive_vault_handoffs(limit=5)

        decision = evaluate_ob_object_guard(
            user_id="beta_001",
            role="user",
            object_kind="export",
            object_id="export_065",
            action="download",
            route_key="export",
            current_risk_score=5,
        )

        open_items = list_open_ob_object_security_inbox(limit=100)
        target = None
        for item in reversed(open_items.get("items", [])):
            if item.get("object_id") == "export_065":
                target = item
                break

        archive_ok = False
        archive_result = {}
        if target:
            archive_result = queue_ob_object_security_inbox_item_for_archive(
                target.get("inbox_item_id"),
                actor_user_id="owner_solice",
                owner_note="Pack 065 final checkpoint: queue object security event for Archive Vault.",
            )
            archive_ok = archive_result.get("ok") is True and bool(archive_result.get("handoff_id"))

        after = summarize_archive_vault_handoffs(limit=8)

        detail.update({
            "object_decision_reason": decision.get("reason_code"),
            "found_archive_target": bool(target),
            "archive_handoff_ok": archive_result.get("ok"),
            "archive_handoff_id": archive_result.get("handoff_id"),
            "archive_before_total": before.get("total"),
            "archive_after_total": after.get("total"),
            "archive_queued": after.get("queued"),
        })

        ok = (
            ui_ok
            and archive_ok
            and after.get("ok") is True
            and after.get("total", 0) >= before.get("total", 0) + 1
        )

        serialized = str([detail, dashboard, archive_result, after])
        no_leak = (
            "raw_token" not in serialized
            and "tower_keycard=" not in serialized
            and "SHOULD_NOT_SURVIVE" not in serialized
        )
        detail["no_secret_leakage"] = no_leak

        return {
            "ok": ok and no_leak,
            "detail": detail,
            "human_reason": "UI action forms and Archive Vault handoff proof passed." if ok and no_leak else "UI/archive proof failed.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Pack 065 UI/archive proof raised an exception.",
        }


try:
    _pack065_original_run_ob_privacy_wall_smoke
except NameError:
    _pack065_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack065_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    proof = _pack065_prove_ui_actions_and_archive_handoff()
    checks["ui_actions_and_archive_handoff_ready"] = {
        "ok": proof.get("ok") is True,
        "detail": proof.get("detail"),
    }

    if proof.get("ok") is not True and "ui_actions_and_archive_handoff_ready" not in failures:
        failures.append("ui_actions_and_archive_handoff_ready")

    result["ok"] = not failures
    result["pack"] = "065"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with UI actions and Archive Vault handoff proof."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result



# ================================================================================
# PACK069_POLISHED_LOCKED_PAGES_SMOKE_WRAPPER
# ================================================================================
# Proves Tower-branded polished locked pages render for route/object/mode/export/unmapped.
# ================================================================================

def _pack069_prove_polished_locked_pages():
    try:
        from web.app import app, _pack068_tower_locked_response

        detail = {}

        def _safe_html_check(name, html):
            checks = {
                "has_tower": "The Tower" in html,
                "has_clearance_gate": ("Clearance Gate" in html or "Clearance Required" in html),
                "has_restricted": ("Restricted Zone" in html or "restricted" in html.lower()),
                "has_soulaana": "Soulaana:" in html,
                "no_keycard_query": "tower_keycard=" not in html,
                "no_raw_token": "raw_token" not in html,
                "no_test_secret": "SHOULD_NOT_SURVIVE" not in html,
            }
            detail[name] = checks
            return all(checks.values())

        route_html, route_status = _pack068_tower_locked_response(
            lock_type="route",
            path="/signals?tower_keycard=SHOULD_NOT_SURVIVE",
            user_id="beta_001",
            reason_code="ob_clearance_level_too_low",
            human_reason="Signals needs confidential clearance.",
            required_actions=["upgrade_clearance", "owner_review"],
            soulaana_translation="Soulaana: This corridor is not public. The Tower held the line.",
        )

        object_html, object_status = _pack068_tower_locked_response(
            lock_type="object",
            path="/signals/AAPL",
            object_type="symbol",
            object_id="AAPL",
            user_id="beta_001",
            reason_code="parent_route_clearance_failed",
            human_reason="The parent route was not cleared.",
        )

        mode_html, mode_status = _pack068_tower_locked_response(
            lock_type="mode",
            mode_name="live_automated",
            user_id="owner_solice",
            reason_code="ob_mode_automation_authorization_missing",
            human_reason="Automated live mode needs explicit automation authorization.",
            required_actions=["owner_automation_authorization", "kill_switch_check"],
            soulaana_translation="Soulaana: Automated live trading is the locked vault, not the lobby.",
        )

        export_html, export_status = _pack068_tower_locked_response(
            lock_type="export",
            export_id="export_069",
            path="/export",
            user_id="beta_001",
        )

        unmapped_html, unmapped_status = _pack068_tower_locked_response(
            lock_type="unmapped",
            path="/new-secret-page",
            object_type="mystery",
            object_id="unknown_069",
            user_id="owner_solice",
            reason_code="unmapped_default_deny",
            human_reason="This protected surface is not mapped yet, so The Tower blocks it by default.",
        )

        client = app.test_client()
        preview = client.get("/tower/polished-locked-preview?path=/signals?tower_keycard=SHOULD_NOT_SURVIVE")
        preview_html = preview.get_data(as_text=True)

        status_ok = (
            route_status == 403
            and object_status == 403
            and mode_status == 403
            and export_status == 403
            and unmapped_status == 403
            and preview.status_code == 403
        )

        content_ok = (
            "Observatory Corridor Locked" in route_html
            and "Symbol Locked" in object_html
            and "AAPL" in object_html
            and "Live Automated Locked" in mode_html
            and "owner_automation_authorization" in mode_html
            and "Export Locked" in export_html
            and "export_069" in export_html
            and "Unmapped Corridor Locked" in unmapped_html
            and "unknown_069" in unmapped_html
        )

        safe_ok = (
            _safe_html_check("route", route_html)
            and _safe_html_check("object", object_html)
            and _safe_html_check("mode", mode_html)
            and _safe_html_check("export", export_html)
            and _safe_html_check("unmapped", unmapped_html)
            and _safe_html_check("preview_route", preview_html)
        )

        detail.update({
            "status_ok": status_ok,
            "content_ok": content_ok,
            "safe_ok": safe_ok,
            "preview_status": preview.status_code,
        })

        return {
            "ok": status_ok and content_ok and safe_ok,
            "detail": detail,
            "human_reason": "Polished locked pages render safely for route/object/mode/export/unmapped."
            if status_ok and content_ok and safe_ok
            else "Polished locked page proof failed.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Polished locked page proof raised an exception.",
        }


try:
    _pack069_original_run_ob_privacy_wall_smoke
except NameError:
    _pack069_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack069_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    proof = _pack069_prove_polished_locked_pages()
    checks["polished_locked_pages_ready"] = {
        "ok": proof.get("ok") is True,
        "detail": proof.get("detail"),
    }

    if proof.get("ok") is not True and "polished_locked_pages_ready" not in failures:
        failures.append("polished_locked_pages_ready")

    result["ok"] = not failures
    result["pack"] = "069"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with polished locked pages."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result



# ================================================================================
# PACK073_AUDITED_UI_ENDPOINT_WORKFLOW_SMOKE_WRAPPER
# ================================================================================
# Proves the audited object inbox UI POST endpoint works and creates receipts.
# ================================================================================

def _pack073_prove_audited_ui_endpoint_workflow():
    try:
        from web.app import app
        from tower.ob_object_guard import evaluate_ob_object_guard
        from tower.ob_object_audit_capsules import list_open_ob_object_security_inbox
        from tower.ui_action_audit import summarize_ui_action_audit_receipts

        client = app.test_client()
        endpoint = "/tower/security-command/object-inbox/action-audited"

        before = summarize_ui_action_audit_receipts(limit=5)

        decision = evaluate_ob_object_guard(
            user_id="beta_001",
            role="user",
            object_kind="export",
            object_id="export_073_endpoint",
            action="download",
            route_key="export",
            current_risk_score=5,
        )

        open_items = list_open_ob_object_security_inbox(limit=160)
        target = None
        for item in reversed(open_items.get("items", [])):
            if item.get("object_id") == "export_073_endpoint":
                target = item
                break

        detail = {
            "decision_reason": decision.get("reason_code"),
            "target_found": bool(target),
            "before_total": before.get("total"),
        }

        if not target:
            return {
                "ok": False,
                "detail": detail,
                "human_reason": "Audited UI endpoint target item was not found.",
            }

        target_id = target.get("inbox_item_id")

        note_resp = client.post(endpoint, data={
            "inbox_item_id": target_id,
            "action_type": "note",
            "note": "Pack 073 smoke: audited endpoint note.",
            "actor_user_id": "owner_solice",
        })
        note_json = note_resp.get_json() or {}

        review_resp = client.post(endpoint, data={
            "inbox_item_id": target_id,
            "action_type": "reviewing",
            "note": "Pack 073 smoke: audited endpoint reviewing.",
            "actor_user_id": "owner_solice",
        })
        review_json = review_resp.get_json() or {}

        resolve_resp = client.post(endpoint, data={
            "inbox_item_id": target_id,
            "action_type": "resolve",
            "note": "Pack 073 smoke: audited endpoint resolved.",
            "resolution_reason": "pack073_smoke_resolved",
            "actor_user_id": "owner_solice",
        })
        resolve_json = resolve_resp.get_json() or {}

        bad_resp = client.post(endpoint, data={
            "inbox_item_id": target_id,
            "action_type": "explode",
            "actor_user_id": "owner_solice",
        })
        bad_json = bad_resp.get_json() or {}

        missing_resp = client.post(endpoint, data={
            "action_type": "note",
            "note": "Pack 073 smoke: missing id.",
            "actor_user_id": "owner_solice",
        })
        missing_json = missing_resp.get_json() or {}

        after = summarize_ui_action_audit_receipts(limit=20)

        receipt_ids = [
            note_json.get("ui_action_audit_receipt_id"),
            review_json.get("ui_action_audit_receipt_id"),
            resolve_json.get("ui_action_audit_receipt_id"),
            bad_json.get("ui_action_audit_receipt_id"),
            missing_json.get("ui_action_audit_receipt_id"),
        ]

        detail.update({
            "target_id": target_id,
            "note_status": note_resp.status_code,
            "note_ok": note_json.get("ok"),
            "review_status": review_resp.status_code,
            "review_ok": review_json.get("ok"),
            "review_new_status": review_json.get("result", {}).get("new_status"),
            "resolve_status": resolve_resp.status_code,
            "resolve_ok": resolve_json.get("ok"),
            "resolve_new_status": resolve_json.get("result", {}).get("new_status"),
            "resolve_reason": resolve_json.get("result", {}).get("item", {}).get("resolution_reason"),
            "bad_status": bad_resp.status_code,
            "bad_reason": bad_json.get("reason_code"),
            "missing_status": missing_resp.status_code,
            "missing_reason": missing_json.get("reason_code"),
            "receipt_ids_present": all(bool(x) for x in receipt_ids),
            "after_total": after.get("total"),
            "after_action_ok": after.get("action_ok"),
            "after_action_failed": after.get("action_failed"),
            "after_by_action": after.get("by_action"),
            "after_by_status_code": after.get("by_status_code"),
        })

        ok = (
            note_resp.status_code == 200
            and note_json.get("ok") is True
            and review_resp.status_code == 200
            and review_json.get("ok") is True
            and review_json.get("result", {}).get("new_status") == "reviewing"
            and resolve_resp.status_code == 200
            and resolve_json.get("ok") is True
            and resolve_json.get("result", {}).get("new_status") == "resolved"
            and resolve_json.get("result", {}).get("item", {}).get("resolution_reason") == "pack073_smoke_resolved"
            and bad_resp.status_code == 400
            and bad_json.get("reason_code") == "invalid_object_inbox_action_type"
            and missing_resp.status_code == 400
            and missing_json.get("reason_code") == "object_inbox_item_id_required"
            and all(bool(x) for x in receipt_ids)
            and after.get("total", 0) >= before.get("total", 0) + 5
            and after.get("action_ok", 0) >= 3
            and after.get("action_failed", 0) >= 2
        )

        serialized = str([detail, note_json, review_json, resolve_json, bad_json, missing_json, after])
        no_leak = (
            "tower_keycard=" not in serialized
            and "SHOULD_NOT_SURVIVE" not in serialized
            and "raw_token=" not in serialized
            and '"raw_token":' not in serialized
            and "Bearer SHOULD_NOT_SURVIVE" not in serialized
        )
        detail["no_secret_leakage"] = no_leak

        return {
            "ok": ok and no_leak,
            "detail": detail,
            "human_reason": "Audited UI endpoint workflow proved." if ok and no_leak else "Audited UI endpoint workflow failed.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Audited UI endpoint workflow proof raised an exception.",
        }


try:
    _pack073_original_run_ob_privacy_wall_smoke
except NameError:
    _pack073_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack073_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    proof = _pack073_prove_audited_ui_endpoint_workflow()
    checks["audited_ui_endpoint_workflow_ready"] = {
        "ok": proof.get("ok") is True,
        "detail": proof.get("detail"),
    }

    if proof.get("ok") is not True and "audited_ui_endpoint_workflow_ready" not in failures:
        failures.append("audited_ui_endpoint_workflow_ready")

    result["ok"] = not failures
    result["pack"] = "073"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with audited UI endpoint workflow."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result



# ================================================================================
# PACK078_AUDITED_FORMS_AND_RECEIPT_PANEL_SMOKE_WRAPPER
# ================================================================================
# Proves Security Command forms point to audited endpoint and receipt panel renders.
# ================================================================================

def _pack078_prove_audited_forms_and_receipt_panel():
    try:
        from pathlib import Path
        from web.app import app
        from tower.security_command_page import generate_security_command_dashboard
        from tower.ob_object_guard import evaluate_ob_object_guard
        from tower.ob_object_audit_capsules import list_open_ob_object_security_inbox
        from tower.ui_action_audit import summarize_ui_action_audit_receipts

        client = app.test_client()
        before = summarize_ui_action_audit_receipts(limit=8)

        # Create a fresh item and push one audited action so the receipt panel has current data.
        decision = evaluate_ob_object_guard(
            user_id="beta_001",
            role="user",
            object_kind="export",
            object_id="export_078_panel",
            action="download",
            route_key="export",
            current_risk_score=5,
        )

        open_items = list_open_ob_object_security_inbox(limit=260)
        target = None
        for item in reversed(open_items.get("items", [])):
            if item.get("object_id") == "export_078_panel":
                target = item
                break

        detail = {
            "decision_reason": decision.get("reason_code"),
            "target_found": bool(target),
            "before_total": before.get("total"),
        }

        if not target:
            return {
                "ok": False,
                "detail": detail,
                "human_reason": "No object inbox target found for Pack 078 proof.",
            }

        target_id = target.get("inbox_item_id")

        note_resp = client.post("/tower/security-command/object-inbox/action-audited", data={
            "inbox_item_id": target_id,
            "action_type": "note",
            "note": "Pack 078 smoke: audited visible-form endpoint proof.",
            "actor_user_id": "owner_solice",
        })
        note_json = note_resp.get_json() or {}

        after = summarize_ui_action_audit_receipts(limit=12)
        dashboard = generate_security_command_dashboard()

        html_path = Path(dashboard.get("path", ""))
        html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""

        has_audited_form_action = (
            'action="/tower/security-command/object-inbox/action-audited"' in html
            or "action='/tower/security-command/object-inbox/action-audited'" in html
            or "/tower/security-command/object-inbox/action-audited" in html
        )
        has_old_form_action = (
            'action="/tower/security-command/object-inbox/action"' in html
            or "action='/tower/security-command/object-inbox/action'" in html
        )

        panel_ok = (
            "UI ACTION AUDIT RECEIPTS" in html
            and "Owner Button-Click Receipts" in html
            and 'data-pack="077"' in html
            and "Successful" in html
            and "Failed / Blocked" in html
            and "By Action" in html
            and "By Reason" in html
            and "By Status Code" in html
        )

        receipt_ok = (
            note_resp.status_code == 200
            and note_json.get("ok") is True
            and bool(note_json.get("ui_action_audit_receipt_id"))
            and after.get("total", 0) >= before.get("total", 0) + 1
            and after.get("by_action", {}).get("note", 0) >= 1
        )

        detail.update({
            "target_id": target_id,
            "note_status": note_resp.status_code,
            "note_ok": note_json.get("ok"),
            "receipt_id_present": bool(note_json.get("ui_action_audit_receipt_id")),
            "after_total": after.get("total"),
            "after_by_action": after.get("by_action"),
            "dashboard_ok": dashboard.get("ok"),
            "dashboard_path": str(html_path),
            "has_audited_form_action": has_audited_form_action,
            "has_old_form_action": has_old_form_action,
            "panel_ok": panel_ok,
            "receipt_ok": receipt_ok,
            "ui_action_audit_total": dashboard.get("ui_action_audit_total"),
            "ui_action_audit_ok": dashboard.get("ui_action_audit_ok"),
        })

        serialized = str([detail, note_json, after, dashboard]) + html
        no_leak = (
            "tower_keycard=" not in serialized
            and "SHOULD_NOT_SURVIVE" not in serialized
            and "raw_token=" not in serialized
            and '"raw_token":' not in serialized
            and "Bearer SHOULD_NOT_SURVIVE" not in serialized
        )
        detail["no_secret_leakage"] = no_leak

        ok = (
            dashboard.get("ok") is True
            and has_audited_form_action
            and not has_old_form_action
            and panel_ok
            and receipt_ok
            and no_leak
        )

        return {
            "ok": ok,
            "detail": detail,
            "human_reason": "Audited forms and receipt panel proved." if ok else "Audited forms/receipt panel proof failed.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Audited forms/receipt panel proof raised an exception.",
        }


try:
    _pack078_original_run_ob_privacy_wall_smoke
except NameError:
    _pack078_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack078_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    proof = _pack078_prove_audited_forms_and_receipt_panel()
    checks["audited_forms_and_receipt_panel_ready"] = {
        "ok": proof.get("ok") is True,
        "detail": proof.get("detail"),
    }

    if proof.get("ok") is not True and "audited_forms_and_receipt_panel_ready" not in failures:
        failures.append("audited_forms_and_receipt_panel_ready")

    result["ok"] = not failures
    result["pack"] = "078"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with audited forms and receipt panel."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result



# ================================================================================
# PACK083_DENY_PATH_REPLACEMENT_RECEIPTS_SMOKE_WRAPPER
# ================================================================================
# Proves polished /no-access replacement and deny-path replacement receipts.
# ================================================================================

def _pack083_prove_deny_path_replacement_receipts():
    try:
        from web.app import app
        from tower.deny_path_replacement_audit import (
            record_deny_path_replacement_receipt,
            summarize_deny_path_replacement_receipts,
        )

        client = app.test_client()
        before = summarize_deny_path_replacement_receipts(limit=8)

        resp = client.get("/no-access?path=/signals?tower_keycard=SHOULD_NOT_SURVIVE")
        html = resp.get_data(as_text=True)

        proof = {
            "ok": (
                resp.status_code == 403
                and "The Tower" in html
                and "Clearance Gate" in html
                and "Restricted Zone" in html
                and "Observatory Corridor Locked" in html
                and "Soulaana:" in html
                and "request_observatory_clearance" in html
                and "<title>Observatory Locked</title>" not in html
                and "tower_keycard=" not in html
                and "SHOULD_NOT_SURVIVE" not in html
            ),
            "status_code": resp.status_code,
            "route_path": "/no-access",
            "has_tower": "The Tower" in html,
            "has_clearance_gate": "Clearance Gate" in html,
            "has_restricted_zone": "Restricted Zone" in html,
            "has_polished_title": "Observatory Corridor Locked" in html,
            "has_soulaana": "Soulaana:" in html,
            "has_request_clearance": "request_observatory_clearance" in html,
            "old_shell_absent": "<title>Observatory Locked</title>" not in html,
            "no_keycard_query": "tower_keycard=" not in html,
            "no_test_secret": "SHOULD_NOT_SURVIVE" not in html,
        }

        receipt = record_deny_path_replacement_receipt(
            route_path="/no-access",
            replacement_type="polished_tower_locked_page",
            old_behavior="legacy_no_access_shell",
            new_behavior="tower_polished_locked_helper",
            actor_user_id="owner_solice",
            reason="Pack 083 smoke proof confirmed /no-access replacement is polished and safe.",
            proof=proof,
            metadata={
                "pack": "083",
                "audit_source": "privacy_wall_smoke",
                "raw_token": "SHOULD_NOT_SURVIVE",
                "tower_keycard": "SHOULD_NOT_SURVIVE",
            },
        )

        after = summarize_deny_path_replacement_receipts(limit=12)

        detail = {
            "before_total": before.get("total"),
            "after_total": after.get("total"),
            "verified": after.get("verified"),
            "needs_review": after.get("needs_review"),
            "by_route": after.get("by_route"),
            "by_replacement_type": after.get("by_replacement_type"),
            "receipt_id": receipt.get("receipt_id"),
            "receipt_status": receipt.get("status"),
            "route_status": resp.status_code,
            "proof": proof,
        }

        ok = (
            proof.get("ok") is True
            and receipt.get("ok") is True
            and receipt.get("status") == "verified"
            and after.get("ok") is True
            and after.get("total", 0) >= before.get("total", 0) + 1
            and after.get("verified", 0) >= 1
            and after.get("by_route", {}).get("/no-access", 0) >= 1
            and after.get("by_replacement_type", {}).get("polished_tower_locked_page", 0) >= 1
        )

        serialized = str([detail, receipt, after]) + html
        no_leak = (
            "tower_keycard=" not in serialized
            and "SHOULD_NOT_SURVIVE" not in serialized
            and "raw_token=" not in serialized
            and '"raw_token":' not in serialized
            and "Bearer SHOULD_NOT_SURVIVE" not in serialized
        )
        detail["no_secret_leakage"] = no_leak

        return {
            "ok": ok and no_leak,
            "detail": detail,
            "human_reason": "Deny-path replacement receipts proved." if ok and no_leak else "Deny-path replacement receipt proof failed.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Deny-path replacement receipt proof raised an exception.",
        }


try:
    _pack083_original_run_ob_privacy_wall_smoke
except NameError:
    _pack083_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack083_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    proof = _pack083_prove_deny_path_replacement_receipts()
    checks["deny_path_replacement_receipts_ready"] = {
        "ok": proof.get("ok") is True,
        "detail": proof.get("detail"),
    }

    if proof.get("ok") is not True and "deny_path_replacement_receipts_ready" not in failures:
        failures.append("deny_path_replacement_receipts_ready")

    result["ok"] = not failures
    result["pack"] = "083"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with deny-path replacement receipts."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result



# ================================================================================
# PACK088_REPLACEMENT_AND_EXPOSURE_UI_PANELS_SMOKE_WRAPPER
# ================================================================================
# Proves deny-path replacement receipts panel + exposure mapping panel render safely.
# ================================================================================

def _pack088_prove_replacement_and_exposure_panels():
    try:
        from pathlib import Path
        from tower.deny_path_replacement_audit import summarize_deny_path_replacement_receipts
        from tower.ob_exposure_mapping import (
            build_ob_exposure_mapping_pass,
            summarize_ob_exposure_mapping_pass,
        )
        from tower.tower_status import get_tower_status
        from tower.security_command_page import generate_security_command_dashboard

        deny_summary = summarize_deny_path_replacement_receipts(limit=10)
        mapping = build_ob_exposure_mapping_pass()
        mapping_summary = summarize_ob_exposure_mapping_pass(limit=12)
        status = get_tower_status()
        dashboard = generate_security_command_dashboard()

        html_path = Path(dashboard.get("path", ""))
        html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""

        deny_status_ok = (
            status.get("deny_path_replacement_ok") is True
            and status.get("deny_path_replacement_total", 0) >= 1
            and status.get("deny_path_replacement_verified", 0) >= 1
            and status.get("deny_path_replacement_by_route", {}).get("/no-access", 0) >= 1
        )

        exposure_status_ok = (
            status.get("ob_exposure_mapping_ok") is True
            and status.get("ob_exposure_mapping_total", 0) >= 1
            and isinstance(status.get("ob_exposure_mapping_counts"), dict)
            and status.get("ob_exposure_mapping_readiness_score") == 100
            and status.get("ob_exposure_mapping_readiness_label") == "Exposure mapping pass ready"
        )

        deny_dashboard_ok = (
            dashboard.get("deny_path_replacement_ok") is True
            and dashboard.get("deny_path_replacement_total", 0) >= 1
            and dashboard.get("deny_path_replacement_verified", 0) >= 1
            and "DENY-PATH REPLACEMENT RECEIPTS" in html
            and "Locked Door Replacement Log" in html
            and 'data-pack="086"' in html
            and "/no-access" in html
            and "polished_tower_locked_page" in html
        )

        exposure_dashboard_ok = (
            dashboard.get("ob_exposure_mapping_ok") is True
            and dashboard.get("ob_exposure_mapping_total", 0) >= 1
            and "OB EXPOSURE MAPPING PASS" in html
            and "Route Exposure Door Map" in html
            and 'data-pack="087"' in html
            and "Total Routes" in html
            and "By Category" in html
            and "Map Next" in html
            and "Retire or Redirect" in html
            and "Later Review" in html
        )

        detail = {
            "deny_summary_ok": deny_summary.get("ok"),
            "deny_summary_total": deny_summary.get("total"),
            "deny_summary_verified": deny_summary.get("verified"),
            "deny_summary_by_route": deny_summary.get("by_route"),
            "mapping_ok": mapping_summary.get("ok"),
            "mapping_total": mapping_summary.get("total"),
            "mapping_counts": mapping_summary.get("counts"),
            "mapping_readiness_score": mapping_summary.get("readiness_score"),
            "mapping_path": mapping.get("path"),
            "tower_status_deny_ok": deny_status_ok,
            "tower_status_exposure_ok": exposure_status_ok,
            "dashboard_ok": dashboard.get("ok"),
            "dashboard_path": str(html_path),
            "dashboard_deny_panel_ok": deny_dashboard_ok,
            "dashboard_exposure_panel_ok": exposure_dashboard_ok,
            "dashboard_has_deny_panel": "DENY-PATH REPLACEMENT RECEIPTS" in html,
            "dashboard_has_exposure_panel": "OB EXPOSURE MAPPING PASS" in html,
            "dashboard_has_pack086": 'data-pack="086"' in html,
            "dashboard_has_pack087": 'data-pack="087"' in html,
        }

        ok = (
            deny_summary.get("ok") is True
            and deny_summary.get("total", 0) >= 1
            and deny_summary.get("verified", 0) >= 1
            and mapping_summary.get("ok") is True
            and mapping_summary.get("total", 0) >= 1
            and deny_status_ok
            and exposure_status_ok
            and dashboard.get("ok") is True
            and deny_dashboard_ok
            and exposure_dashboard_ok
        )

        serialized = str([detail, deny_summary, mapping_summary, status, dashboard]) + html
        no_leak = (
            "tower_keycard=" not in serialized
            and "SHOULD_NOT_SURVIVE" not in serialized
            and "raw_token=" not in serialized
            and '"raw_token":' not in serialized
            and "Bearer SHOULD_NOT_SURVIVE" not in serialized
        )
        detail["no_secret_leakage"] = no_leak

        return {
            "ok": ok and no_leak,
            "detail": detail,
            "human_reason": (
                "Deny-path replacement and exposure mapping UI panels proved."
                if ok and no_leak
                else "Replacement/exposure panel proof failed."
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "detail": {"error": f"{type(exc).__name__}: {exc}"},
            "human_reason": "Replacement/exposure panel proof raised an exception.",
        }


try:
    _pack088_original_run_ob_privacy_wall_smoke
except NameError:
    _pack088_original_run_ob_privacy_wall_smoke = run_ob_privacy_wall_smoke


def run_ob_privacy_wall_smoke():
    result = _pack088_original_run_ob_privacy_wall_smoke()
    if not isinstance(result, dict):
        result = {"ok": False, "checks": {}, "failures": ["invalid_smoke_result"]}

    checks = result.setdefault("checks", {})
    failures = result.setdefault("failures", [])

    proof = _pack088_prove_replacement_and_exposure_panels()
    checks["replacement_and_exposure_panels_ready"] = {
        "ok": proof.get("ok") is True,
        "detail": proof.get("detail"),
    }

    if proof.get("ok") is not True and "replacement_and_exposure_panels_ready" not in failures:
        failures.append("replacement_and_exposure_panels_ready")

    result["ok"] = not failures
    result["pack"] = "088"
    result["human_reason"] = (
        "OB privacy wall smoke test passed with replacement and exposure panels."
        if result["ok"]
        else "OB privacy wall smoke test found failures."
    )

    return result

