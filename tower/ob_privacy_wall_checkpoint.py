
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_ob_privacy_wall_checkpoint() -> Dict[str, Any]:
    from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
    from tower.ob_route_guard import get_ob_route_guard_report
    from tower.ob_object_guard import get_ob_object_guard_report
    from tower.ob_route_exposure_report import build_ob_route_exposure_report
    from web.app import app

    smoke = run_ob_privacy_wall_smoke()
    route_guard = get_ob_route_guard_report()
    object_guard = get_ob_object_guard_report()
    exposure = build_ob_route_exposure_report(app=app)

    built_packs = [
        {"pack": "045", "name": "OB route guard foundation", "plain": "Mapped public-safe, protected, dynamic, and default-deny routes."},
        {"pack": "046", "name": "Flask privacy wall wiring", "plain": "Flask requests ask the OB route guard before protected pages show."},
        {"pack": "047", "name": "Route exposure report", "plain": "Flask routes are categorized into public-safe, guarded, Tower-owned, static, or default-deny."},
        {"pack": "048", "name": "Private outer shell", "plain": "No-access public shell is harmless and real Observatory stays private."},
        {"pack": "049", "name": "OB object guard foundation", "plain": "Specific symbols, trades, accounts, exports, modes, records, and controls get drawer-level checks."},
        {"pack": "050", "name": "Symbol object guard wiring", "plain": "Symbol-detail routes require exact symbol clearance."},
        {"pack": "051", "name": "Trade/position object guard wiring", "plain": "Trade and position detail routes require exact object clearance."},
        {"pack": "052", "name": "Export/download object guard wiring", "plain": "Export and download requests require critical object clearance."},
        {"pack": "053", "name": "Mode switcher guard wiring", "plain": "Mode requests ask the Tower mode bridge first."},
        {"pack": "054", "name": "Privacy wall smoke runner", "plain": "One smoke test validates the full route/object/mode privacy wall."},
    ]

    next_steps = [
        {"priority": 1, "item": "Wire real app templates to show clean locked/upgrade states", "plain": "The backend guard works; user-facing cards should feel intentional and premium."},
        {"priority": 2, "item": "Add object guard audit receipts", "plain": "Object denies/allows should create reviewable receipts like door swipes."},
        {"priority": 3, "item": "Add Tower UI panels for privacy wall status", "plain": "The Tower dashboard should show protected routes, object guard health, and default-deny exposure."},
        {"priority": 4, "item": "Add Archive Vault handoff for privacy/security events", "plain": "Important locked/denied/revealed events should become evidence capsules."},
        {"priority": 5, "item": "Begin cleanup pass on duplicated legacy routes", "plain": "Now that default-deny exists, old public-ish routes can be intentionally mapped or removed."},
    ]

    score = 0
    if smoke.get("ok"):
        score += 35
    if route_guard.get("ok") and route_guard.get("default_deny_unmapped"):
        score += 20
    if object_guard.get("ok"):
        score += 20
    if exposure.get("ok") and exposure.get("default_deny_active"):
        score += 15
    if exposure.get("counts", {}).get("unmapped_default_deny", 0) >= 0:
        score += 10

    score = min(100, score)

    return {
        "ok": smoke.get("ok") is True,
        "pack": "055",
        "generated_at": _utc_now(),
        "tower_name": "The Tower",
        "readiness_score": score,
        "readiness_label": "Privacy wall active" if smoke.get("ok") else "Privacy wall needs attention",
        "smoke_ok": smoke.get("ok"),
        "smoke_failures": smoke.get("failures"),
        "route_guard_summary": {
            "guarded_count": route_guard.get("guarded_count"),
            "public_safe_count": route_guard.get("public_safe_count"),
            "default_deny_unmapped": route_guard.get("default_deny_unmapped"),
        },
        "object_guard_summary": {
            "object_guard_count": object_guard.get("object_guard_count"),
            "default_object_policy": object_guard.get("default_object_policy"),
        },
        "exposure_summary": {
            "counts": exposure.get("counts"),
            "attention_count": exposure.get("attention_count"),
        },
        "built_packs": built_packs,
        "next_steps": next_steps,
        "soulaana_translation": "Soulaana: The public sky is locked, the private corridors are mapped, and the drawers now ask for keys.",
        "human_reason": "OB privacy wall checkpoint summarizes route, object, mode, exposure, and smoke-test readiness.",
    }


if __name__ == "__main__":
    import json
    result = build_ob_privacy_wall_checkpoint()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("OB privacy wall checkpoint failed.")
