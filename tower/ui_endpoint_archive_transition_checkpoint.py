
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_ui_endpoint_archive_transition_checkpoint() -> Dict[str, Any]:
    from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
    from tower.ob_privacy_wall_checkpoint import build_ob_privacy_wall_checkpoint
    from tower.ui_action_audit import summarize_ui_action_audit_receipts
    from tower.archive_vault_handoff import summarize_archive_vault_handoffs
    from tower.ob_object_audit_capsules import summarize_ob_object_security_inbox
    from tower.tower_status import get_tower_status
    from tower.security_command_page import generate_security_command_dashboard

    smoke = run_ob_privacy_wall_smoke()
    privacy_checkpoint = build_ob_privacy_wall_checkpoint()
    ui_audit = summarize_ui_action_audit_receipts(limit=10)
    archive = summarize_archive_vault_handoffs(limit=10)
    object_inbox = summarize_ob_object_security_inbox(limit=10)
    tower_status = get_tower_status()
    dashboard = generate_security_command_dashboard()

    html_ok = False
    html_has_object_forms = False
    html_has_archive_panel = False
    html_has_audited_endpoint = False
    html_path_text = dashboard.get("path", "") if isinstance(dashboard, dict) else ""

    try:
        html_path = Path(html_path_text)
        html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""
        html_has_object_forms = "/tower/security-command/object-inbox/action" in html
        html_has_archive_panel = "ARCHIVE VAULT HANDOFFS" in html and "Evidence Bundle Queue" in html
        html_has_audited_endpoint = "/tower/security-command/object-inbox/action-audited" in html
        # action-audited may not be wired into forms yet; action endpoint forms are still acceptable.
        html_ok = "OB OBJECT SECURITY INBOX" in html and html_has_object_forms and html_has_archive_panel
    except Exception:
        html_ok = False

    smoke_checks = smoke.get("checks", {}) if isinstance(smoke.get("checks"), dict) else {}

    built_packs = [
        {
            "pack": "071",
            "name": "Object inbox UI POST endpoint",
            "plain": "Security Command object inbox forms can submit owner actions through Flask.",
        },
        {
            "pack": "072",
            "name": "UI action audit receipts",
            "plain": "Successful and failed owner UI actions leave audit receipts.",
        },
        {
            "pack": "073",
            "name": "Audited UI endpoint workflow proof",
            "plain": "Smoke/checkpoint prove audited endpoint note/review/resolve/failure paths.",
        },
        {
            "pack": "074",
            "name": "Archive Vault handoff status/UI surfacing",
            "plain": "Archive handoff queue is visible in Tower status and Security Command UI.",
        },
        {
            "pack": "075",
            "name": "UI endpoint/archive transition checkpoint",
            "plain": "Close this block before the next security build section.",
        },
    ]

    proof = {
        "smoke_ok": smoke.get("ok") is True,
        "privacy_checkpoint_ok": privacy_checkpoint.get("ok") is True,
        "audited_ui_endpoint_workflow_ready": smoke_checks.get("audited_ui_endpoint_workflow_ready", {}).get("ok") is True,
        "ui_action_audit_ok": ui_audit.get("ok") is True,
        "ui_action_audit_total_present": ui_audit.get("total", 0) >= 1,
        "ui_action_successes_present": ui_audit.get("action_ok", 0) >= 1,
        "ui_action_failures_present": ui_audit.get("action_failed", 0) >= 1,
        "archive_handoff_ok": archive.get("ok") is True,
        "archive_handoff_total_present": archive.get("total", 0) >= 1,
        "archive_handoff_queued_present": archive.get("queued", 0) >= 1,
        "object_inbox_ok": object_inbox.get("ok") is True,
        "tower_status_has_archive": tower_status.get("archive_vault_handoff_ok") is True,
        "tower_status_has_archive_total": tower_status.get("archive_vault_handoff_total", 0) >= 1,
        "dashboard_ok": dashboard.get("ok") is True if isinstance(dashboard, dict) else False,
        "dashboard_has_object_forms": html_has_object_forms,
        "dashboard_has_archive_panel": html_has_archive_panel,
        "dashboard_html_ok": html_ok,
        "dashboard_has_audited_endpoint": html_has_audited_endpoint,
    }

    ok = all(
        value for key, value in proof.items()
        if key != "dashboard_has_audited_endpoint"
    )

    next_block = [
        {
            "pack": "076",
            "item": "Wire audited endpoint into Security Command forms",
            "plain": "Update object inbox form actions from /action to /action-audited so UI clicks create receipts by default.",
        },
        {
            "pack": "077",
            "item": "Add UI action receipt summary panel",
            "plain": "Show owner button-click audit receipts inside Security Command.",
        },
        {
            "pack": "078",
            "item": "Update smoke/checkpoint for audited forms + receipt panel",
            "plain": "Prove the visible forms use the audited endpoint and the receipt panel renders.",
        },
        {
            "pack": "079",
            "item": "Begin controlled deny-path replacement",
            "plain": "Start replacing older locked shells with the polished Tower locked helper route-by-route.",
        },
        {
            "pack": "080",
            "item": "Save/transition checkpoint",
            "plain": "Close the audited UI forms/receipt visibility block cleanly.",
        },
    ]

    current_boundary = {
        "done": [
            "Object inbox owner action backend exists.",
            "Object inbox UI POST endpoint works.",
            "Audited endpoint creates receipts for success and failure paths.",
            "Smoke/checkpoint prove audited UI endpoint workflow.",
            "Archive Vault handoff queue exists.",
            "Tower status surfaces Archive Vault handoff summary.",
            "Security Command UI surfaces Archive Vault Evidence Bundle Queue.",
        ],
        "not_done_yet": [
            "Security Command forms still point at the original /action endpoint unless explicitly updated later.",
            "UI action receipt summary is not yet shown as its own dashboard panel.",
            "Older privacy-wall deny paths have not all been replaced with polished locked pages.",
        ],
        "why": "We are keeping each security layer small and provable instead of changing UI forms, receipts, archive surfacing, and deny-path behavior all at once.",
    }

    serialized = str([smoke, privacy_checkpoint, ui_audit, archive, object_inbox, tower_status, dashboard, proof])
    no_secret_leakage = (
        "tower_keycard=" not in serialized
        and "SHOULD_NOT_SURVIVE" not in serialized
        and "raw_token=" not in serialized
        and '"raw_token":' not in serialized
        and "Bearer SHOULD_NOT_SURVIVE" not in serialized
    )

    return {
        "ok": bool(ok and no_secret_leakage),
        "pack": "075",
        "generated_at": _utc_now(),
        "readiness_score": 100 if ok and no_secret_leakage else 90,
        "readiness_label": "Ready for audited form wiring and receipt dashboard"
        if ok and no_secret_leakage
        else "Needs repair before audited form wiring",
        "proof": proof,
        "no_secret_leakage": no_secret_leakage,
        "ui_action_audit_summary": {
            "ok": ui_audit.get("ok"),
            "total": ui_audit.get("total"),
            "action_ok": ui_audit.get("action_ok"),
            "action_failed": ui_audit.get("action_failed"),
            "by_action": ui_audit.get("by_action"),
            "by_reason": ui_audit.get("by_reason"),
            "by_severity": ui_audit.get("by_severity"),
            "by_status_code": ui_audit.get("by_status_code"),
        },
        "archive_vault_handoff_summary": {
            "ok": archive.get("ok"),
            "total": archive.get("total"),
            "queued": archive.get("queued"),
            "by_status": archive.get("by_status"),
            "by_source_type": archive.get("by_source_type"),
            "by_severity": archive.get("by_severity"),
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
        "tower_status_archive_fields": {
            "archive_vault_handoff_ok": tower_status.get("archive_vault_handoff_ok"),
            "archive_vault_handoff_total": tower_status.get("archive_vault_handoff_total"),
            "archive_vault_handoff_queued": tower_status.get("archive_vault_handoff_queued"),
            "archive_vault_handoff_by_status": tower_status.get("archive_vault_handoff_by_status"),
            "archive_vault_handoff_by_source_type": tower_status.get("archive_vault_handoff_by_source_type"),
        },
        "dashboard_summary": {
            "ok": dashboard.get("ok") if isinstance(dashboard, dict) else False,
            "path": html_path_text,
            "has_object_forms": html_has_object_forms,
            "has_archive_panel": html_has_archive_panel,
            "has_audited_endpoint": html_has_audited_endpoint,
        },
        "built_packs": built_packs,
        "next_block": next_block,
        "current_boundary": current_boundary,
        "soulaana_translation": "Soulaana: Owner actions move the review queue, receipts prove the clicks, and evidence handoffs are visible. Next we make the visible forms use the audited path by default.",
        "human_reason": "UI endpoint and Archive Vault surfacing transition checkpoint is ready.",
    }


if __name__ == "__main__":
    import json

    result = build_ui_endpoint_archive_transition_checkpoint()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("UI endpoint/archive transition checkpoint failed.")
