
from __future__ import annotations

from typing import Any, Dict


def _ok_detail(ok: bool, detail: Any = None) -> Dict[str, Any]:
    return {"ok": bool(ok), "detail": detail}


def run_ob_privacy_wall_smoke() -> Dict[str, Any]:
    from web.app import app
    from tower.ob_route_guard import evaluate_ob_request_guard
    from tower.ob_object_guard import evaluate_ob_object_guard
    from tower.ob_mode_clearance import evaluate_ob_mode_clearance
    from tower.ob_route_exposure_report import build_ob_route_exposure_report

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
    check("route_guard_allows_owner_blocks_beta_default_denies", route_owner.get("allowed") is True and route_beta.get("allowed") is False and route_unmapped.get("reason_code") == "ob_route_unmapped_default_deny", {
        "owner": route_owner.get("reason_code"),
        "beta": route_beta.get("reason_code"),
        "unmapped": route_unmapped.get("reason_code"),
    })

    symbol_owner = evaluate_ob_object_guard(user_id="owner_solice", role="owner", object_kind="symbol", object_id="AAPL", route_key="symbol_detail")
    symbol_beta = evaluate_ob_object_guard(user_id="beta_001", role="user", object_kind="symbol", object_id="AAPL", route_key="symbol_detail")
    trade_owner = evaluate_ob_object_guard(user_id="owner_solice", role="owner", object_kind="trade", object_id="trade_054", owner_user_id="owner_solice", route_key="positions")
    export_beta = evaluate_ob_object_guard(user_id="beta_001", role="user", object_kind="export", object_id="export_054", route_key="export", action="download")
    check("object_guard_symbols_trades_exports", symbol_owner.get("allowed") is True and symbol_beta.get("allowed") is False and trade_owner.get("allowed") is True and export_beta.get("allowed") is False, {
        "symbol_owner": symbol_owner.get("reason_code"),
        "symbol_beta": symbol_beta.get("reason_code"),
        "trade_owner": trade_owner.get("reason_code"),
        "export_beta": export_beta.get("reason_code"),
    })

    mode_survey = evaluate_ob_mode_clearance(user_id="beta_001", role="user", mode_name="survey", action="enter")
    mode_paper_beta = evaluate_ob_mode_clearance(user_id="beta_001", role="user", mode_name="paper", action="enter")
    mode_auto_owner = evaluate_ob_mode_clearance(user_id="owner_solice", role="owner", mode_name="live_automated", action="enter", broker_connected=True, broker_healthy=True, live_authorized=True, automation_authorized=True)
    check("mode_guard_survey_paper_live_auto", mode_survey.get("allowed") is True and mode_paper_beta.get("allowed") is False and mode_auto_owner.get("allowed") is True, {
        "survey": mode_survey.get("reason_code"),
        "paper_beta": mode_paper_beta.get("reason_code"),
        "auto_owner": mode_auto_owner.get("reason_code"),
    })

    beta_symbol_route = client.get("/signals/AAPL?ob_user_id=beta_001&ob_role=user")
    no_access = client.get("/no-access?path=/signals")
    unmapped = client.get("/random-unmapped-private-route")
    check("flask_routes_lock_private_surfaces", beta_symbol_route.status_code == 403 and no_access.status_code == 403 and unmapped.status_code == 403, {
        "beta_symbol": beta_symbol_route.status_code,
        "no_access": no_access.status_code,
        "unmapped": unmapped.status_code,
    })

    exposure = build_ob_route_exposure_report(app=app)
    check("exposure_report_loads", exposure.get("ok") is True and exposure.get("default_deny_active") is True, {
        "counts": exposure.get("counts"),
        "attention_count": exposure.get("attention_count"),
    })

    serialized = str([checks, failures])
    check("no_raw_keycard_leakage", "tower_keycard=" not in serialized and "raw_token" not in serialized, None)

    return {
        "ok": not failures,
        "pack": "054",
        "checks": checks,
        "failures": failures,
        "human_reason": "OB privacy wall smoke test passed." if not failures else "OB privacy wall smoke test found failures.",
    }


if __name__ == "__main__":
    import json
    result = run_ob_privacy_wall_smoke()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("OB privacy wall smoke failed.")
