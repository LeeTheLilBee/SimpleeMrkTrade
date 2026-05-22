
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



# ================================================================================
# PACK062_OBJECT_INBOX_ACTION_WORKFLOW_CHECKPOINT_WRAPPER
# ================================================================================
# Adds object inbox action workflow proof to the checkpoint result.
# ================================================================================

try:
    _pack062_original_build_ob_privacy_wall_checkpoint
except NameError:
    _pack062_original_build_ob_privacy_wall_checkpoint = build_ob_privacy_wall_checkpoint


def build_ob_privacy_wall_checkpoint():
    checkpoint = _pack062_original_build_ob_privacy_wall_checkpoint()
    if not isinstance(checkpoint, dict):
        checkpoint = {"ok": False, "built_packs": [], "next_steps": []}

    try:
        from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
        from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox

        smoke = run_ob_privacy_wall_smoke()
        workflow = smoke.get("checks", {}).get("object_security_inbox_action_workflow", {})
        inbox = summarize_ob_object_security_inbox(limit=8)

        checkpoint["pack"] = "062"
        checkpoint["smoke_ok"] = smoke.get("ok")
        checkpoint["smoke_failures"] = smoke.get("failures")
        checkpoint["object_security_inbox_action_workflow"] = workflow
        checkpoint["object_security_inbox_summary"] = {
            "ok": inbox.get("ok"),
            "total": inbox.get("total"),
            "open": inbox.get("open"),
            "by_status": inbox.get("by_status"),
            "by_reason": inbox.get("by_reason"),
            "by_object_type": inbox.get("by_object_type"),
            "by_severity": inbox.get("by_severity"),
        }

        built_packs = checkpoint.setdefault("built_packs", [])
        built_text = str(built_packs)
        if "061" not in built_text:
            built_packs.append({
                "pack": "061",
                "name": "Object inbox actions",
                "plain": "Object security inbox items can be noted, reviewed, resolved, and ignored.",
            })
        if "062" not in built_text:
            built_packs.append({
                "pack": "062",
                "name": "Object inbox action proof",
                "plain": "Smoke and checkpoint prove object inbox owner workflow.",
            })

        checkpoint["readiness_score"] = max(int(checkpoint.get("readiness_score", 0) or 0), 100 if workflow.get("ok") else 90)
        checkpoint["readiness_label"] = (
            "Privacy wall audit and action chain active"
            if workflow.get("ok")
            else "Privacy wall workflow needs attention"
        )
        checkpoint["ok"] = smoke.get("ok") is True
        checkpoint["soulaana_translation"] = (
            "Soulaana: The Tower does not just block drawers now. It records them, queues them, reviews them, and closes the loop."
        )
        checkpoint["human_reason"] = "OB privacy wall checkpoint now includes object inbox owner action workflow proof."

        next_steps = checkpoint.setdefault("next_steps", [])
        next_text = str(next_steps)
        if "Tower UI action buttons" not in next_text:
            next_steps.insert(0, {
                "priority": 1,
                "item": "Add Tower UI action buttons/forms for object inbox items",
                "plain": "Backend actions exist; now the owner needs buttons for review, resolve, ignore, and notes.",
            })

    except Exception as exc:
        checkpoint["ok"] = False
        checkpoint["pack062_error"] = f"{type(exc).__name__}: {exc}"

    return checkpoint



# ================================================================================
# PACK065_FINAL_SECURITY_BLOCK_CHECKPOINT_WRAPPER
# ================================================================================
# Final checkpoint before polished locked-state templates.
# ================================================================================

try:
    _pack065_original_build_ob_privacy_wall_checkpoint
except NameError:
    _pack065_original_build_ob_privacy_wall_checkpoint = build_ob_privacy_wall_checkpoint


def build_ob_privacy_wall_checkpoint():
    checkpoint = _pack065_original_build_ob_privacy_wall_checkpoint()
    if not isinstance(checkpoint, dict):
        checkpoint = {"ok": False, "built_packs": [], "next_steps": []}

    try:
        from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
        from tower.archive_vault_handoff import summarize_archive_vault_handoffs
        from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox

        smoke = run_ob_privacy_wall_smoke()
        checks = smoke.get("checks", {}) if isinstance(smoke.get("checks"), dict) else {}
        ui_archive = checks.get("ui_actions_and_archive_handoff_ready", {})
        action_workflow = checks.get("object_security_inbox_action_workflow", {})

        archive_summary = summarize_archive_vault_handoffs(limit=8)
        object_inbox = summarize_ob_object_security_inbox(limit=8)

        checkpoint["pack"] = "065"
        checkpoint["ok"] = smoke.get("ok") is True
        checkpoint["smoke_ok"] = smoke.get("ok")
        checkpoint["smoke_failures"] = smoke.get("failures")
        checkpoint["ui_actions_and_archive_handoff_ready"] = ui_archive
        checkpoint["object_security_inbox_action_workflow"] = action_workflow
        checkpoint["archive_vault_handoff_summary"] = {
            "ok": archive_summary.get("ok"),
            "total": archive_summary.get("total"),
            "queued": archive_summary.get("queued"),
            "by_status": archive_summary.get("by_status"),
            "by_source_type": archive_summary.get("by_source_type"),
            "by_severity": archive_summary.get("by_severity"),
        }
        checkpoint["object_security_inbox_summary"] = {
            "ok": object_inbox.get("ok"),
            "total": object_inbox.get("total"),
            "open": object_inbox.get("open"),
            "by_status": object_inbox.get("by_status"),
            "by_reason": object_inbox.get("by_reason"),
            "by_object_type": object_inbox.get("by_object_type"),
            "by_severity": object_inbox.get("by_severity"),
        }

        built_packs = checkpoint.setdefault("built_packs", [])
        built_text = str(built_packs)
        additions = [
            {
                "pack": "063",
                "name": "Tower UI object inbox action forms",
                "plain": "Security Command UI renders note, reviewing, resolve, and ignore forms for object inbox items.",
            },
            {
                "pack": "064",
                "name": "Archive Vault handoff stub",
                "plain": "Object security events can be queued as future evidence-bundle requests.",
            },
            {
                "pack": "065",
                "name": "Final privacy wall checkpoint",
                "plain": "Smoke/checkpoint prove UI action forms and Archive Vault handoff before locked-page polish.",
            },
        ]
        for item in additions:
            if item["pack"] not in built_text:
                built_packs.append(item)

        next_steps = [
            {
                "priority": 1,
                "item": "Build polished locked-state templates",
                "plain": "Make blocked route/object/mode pages feel intentional, premium, and aligned with The Tower.",
            },
            {
                "priority": 2,
                "item": "Wire the UI action endpoint",
                "plain": "Forms render now; next the Flask POST route should call note/review/resolve/ignore backend actions.",
            },
            {
                "priority": 3,
                "item": "Surface Archive Vault handoff summary in Tower status/UI",
                "plain": "The queue exists; now The Tower should show queued evidence handoffs.",
            },
            {
                "priority": 4,
                "item": "Map or intentionally retire unmapped Observatory routes",
                "plain": "The exposure report shows default-deny routes; choose which become real corridors.",
            },
            {
                "priority": 5,
                "item": "Create action audit receipts for UI button clicks",
                "plain": "Every owner action from the UI should leave its own admin action receipt.",
            },
        ]
        checkpoint["next_steps"] = next_steps

        checkpoint["readiness_score"] = 100 if smoke.get("ok") else 90
        checkpoint["readiness_label"] = (
            "Ready for polished locked-state templates"
            if smoke.get("ok")
            else "Needs repair before locked-state polish"
        )
        checkpoint["soulaana_translation"] = (
            "Soulaana: The Tower can block, receipt, queue, review, archive-stub, and prove the chain. Now we can make the locked doors look expensive."
        )
        checkpoint["human_reason"] = "Final privacy wall checkpoint complete before polished locked-state templates."

    except Exception as exc:
        checkpoint["ok"] = False
        checkpoint["pack065_error"] = f"{type(exc).__name__}: {exc}"

    return checkpoint



# ================================================================================
# PACK069_POLISHED_LOCKED_PAGES_CHECKPOINT_WRAPPER
# ================================================================================
# Adds polished locked-page proof to checkpoint.
# ================================================================================

try:
    _pack069_original_build_ob_privacy_wall_checkpoint
except NameError:
    _pack069_original_build_ob_privacy_wall_checkpoint = build_ob_privacy_wall_checkpoint


def build_ob_privacy_wall_checkpoint():
    checkpoint = _pack069_original_build_ob_privacy_wall_checkpoint()
    if not isinstance(checkpoint, dict):
        checkpoint = {"ok": False, "built_packs": [], "next_steps": []}

    try:
        from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke

        smoke = run_ob_privacy_wall_smoke()
        checks = smoke.get("checks", {}) if isinstance(smoke.get("checks"), dict) else {}
        polished = checks.get("polished_locked_pages_ready", {})

        checkpoint["pack"] = "069"
        checkpoint["ok"] = smoke.get("ok") is True
        checkpoint["smoke_ok"] = smoke.get("ok")
        checkpoint["smoke_failures"] = smoke.get("failures")
        checkpoint["polished_locked_pages_ready"] = polished

        built_packs = checkpoint.setdefault("built_packs", [])
        built_text = str(built_packs)
        additions = [
            {
                "pack": "066",
                "name": "Polished locked-state template system",
                "plain": "Tower-branded premium locked pages render safely.",
            },
            {
                "pack": "067",
                "name": "Locked-page variants",
                "plain": "Route, object, mode, export, and unmapped lock variants exist.",
            },
            {
                "pack": "068",
                "name": "Flask locked-response helper",
                "plain": "web/app.py can render Tower-branded locked responses.",
            },
            {
                "pack": "069",
                "name": "Polished locked-page proof",
                "plain": "Smoke/checkpoint prove polished locked pages render safely.",
            },
        ]
        for item in additions:
            if item["pack"] not in built_text:
                built_packs.append(item)

        checkpoint["next_steps"] = [
            {
                "priority": 1,
                "item": "Wire polished locked pages into the actual privacy wall deny paths",
                "plain": "The helper works; now replace older deny shells route-by-route without breaking behavior.",
            },
            {
                "priority": 2,
                "item": "Wire the UI action endpoint",
                "plain": "Object inbox forms render now; next the Flask POST route should call note/review/resolve/ignore backend actions.",
            },
            {
                "priority": 3,
                "item": "Surface Archive Vault handoff summary in Tower status/UI",
                "plain": "The queue exists; now The Tower should show queued evidence handoffs.",
            },
            {
                "priority": 4,
                "item": "Map or intentionally retire unmapped Observatory routes",
                "plain": "The exposure report shows default-deny routes; choose which become real corridors.",
            },
            {
                "priority": 5,
                "item": "Create action audit receipts for UI button clicks",
                "plain": "Every owner action from the UI should leave its own admin action receipt.",
            },
        ]

        checkpoint["readiness_score"] = 100 if smoke.get("ok") else 90
        checkpoint["readiness_label"] = (
            "Ready to wire polished locked pages into deny paths"
            if smoke.get("ok")
            else "Needs repair before deny-path wiring"
        )
        checkpoint["soulaana_translation"] = (
            "Soulaana: The locked walls are no longer ugly. The Tower blocks with receipts, context, and expensive silence."
        )
        checkpoint["human_reason"] = "Privacy wall checkpoint now proves polished locked-state pages."

    except Exception as exc:
        checkpoint["ok"] = False
        checkpoint["pack069_error"] = f"{type(exc).__name__}: {exc}"

    return checkpoint

