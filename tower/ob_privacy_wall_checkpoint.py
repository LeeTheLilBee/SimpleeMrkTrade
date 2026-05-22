
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
    from tower.ob_object_audit_capsules import (
        summarize_ob_object_audit_capsules,
        summarize_ob_object_security_inbox,
    )
    from tower.tower_status import get_tower_status
    from web.app import app

    smoke = run_ob_privacy_wall_smoke()
    route_guard = get_ob_route_guard_report()
    object_guard = get_ob_object_guard_report()
    exposure = build_ob_route_exposure_report(app=app)
    object_audit = summarize_ob_object_audit_capsules(limit=8)
    object_inbox = summarize_ob_object_security_inbox(limit=8)
    tower_status = get_tower_status()

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
        {"pack": "055", "name": "Privacy wall checkpoint summary", "plain": "Checkpoint summarizes the privacy wall."},
        {"pack": "056", "name": "Object audit capsules", "plain": "Object opens and denials write drawer-level receipts."},
        {"pack": "057", "name": "Object audit in Tower status", "plain": "Tower status sees object receipt totals and recent receipts."},
        {"pack": "058", "name": "Object security inbox bridge", "plain": "Review-worthy drawer receipts become owner tasks."},
        {"pack": "059", "name": "Object security inbox surfaced", "plain": "Tower status and Security Command UI show drawer-review tasks."},
        {"pack": "060", "name": "Audit/inbox/UI proof smoke", "plain": "Smoke and checkpoint prove the full drawer-receipt chain."},
    ]

    next_steps = [
        {
            "priority": 1,
            "item": "Add owner actions for object security inbox items",
            "plain": "Allow review, resolve, ignore, annotate, and assign object inbox items.",
        },
        {
            "priority": 2,
            "item": "Add Archive Vault handoff for object security events",
            "plain": "Important drawer receipts and review tasks should become evidence bundles.",
        },
        {
            "priority": 3,
            "item": "Add polished locked-state templates",
            "plain": "Make object/route/mode lock pages feel intentional and premium.",
        },
        {
            "priority": 4,
            "item": "Map or intentionally retire unmapped Observatory routes",
            "plain": "The exposure report shows default-deny routes; choose which become real corridors.",
        },
        {
            "priority": 5,
            "item": "Add admin UI buttons for privacy wall/inbox actions",
            "plain": "The backend is ready; the Tower UI should make owner review easy.",
        },
    ]

    score = 0
    if smoke.get("ok"):
        score += 30
    if route_guard.get("ok") and route_guard.get("default_deny_unmapped"):
        score += 15
    if object_guard.get("ok"):
        score += 15
    if exposure.get("ok") and exposure.get("default_deny_active"):
        score += 10
    if object_audit.get("ok") and object_audit.get("total", 0) >= 1:
        score += 15
    if object_inbox.get("ok") and object_inbox.get("total", 0) >= 1:
        score += 15

    score = min(100, score)

    return {
        "ok": smoke.get("ok") is True,
        "pack": "060",
        "generated_at": _utc_now(),
        "tower_name": "The Tower",
        "readiness_score": score,
        "readiness_label": "Privacy wall audit chain active" if smoke.get("ok") else "Privacy wall audit chain needs attention",
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
        "object_audit_summary": {
            "ok": object_audit.get("ok"),
            "total": object_audit.get("total"),
            "allowed": object_audit.get("allowed"),
            "denied": object_audit.get("denied"),
            "by_reason": object_audit.get("by_reason"),
            "by_object_type": object_audit.get("by_object_type"),
            "by_severity": object_audit.get("by_severity"),
        },
        "object_security_inbox_summary": {
            "ok": object_inbox.get("ok"),
            "total": object_inbox.get("total"),
            "open": object_inbox.get("open"),
            "by_status": object_inbox.get("by_status"),
            "by_reason": object_inbox.get("by_reason"),
            "by_object_type": object_inbox.get("by_object_type"),
            "by_severity": object_inbox.get("by_severity"),
        },
        "tower_status_object_fields": {
            "ob_object_audit_total": tower_status.get("ob_object_audit_total"),
            "ob_object_security_inbox_total": tower_status.get("ob_object_security_inbox_total"),
            "ob_object_security_inbox_open": tower_status.get("ob_object_security_inbox_open"),
        },
        "built_packs": built_packs,
        "next_steps": next_steps,
        "soulaana_translation": "Soulaana: The public sky is locked, the private corridors are mapped, and every serious drawer touch now leaves a receipt and a review task.",
        "human_reason": "OB privacy wall checkpoint now includes object audit receipts, object security inbox, Tower status surfacing, and UI proof.",
    }


if __name__ == "__main__":
    import json

    result = build_ob_privacy_wall_checkpoint()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("OB privacy wall checkpoint failed.")
