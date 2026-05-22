
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
