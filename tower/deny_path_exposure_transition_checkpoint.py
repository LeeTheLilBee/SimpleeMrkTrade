
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_deny_path_exposure_transition_checkpoint() -> Dict[str, Any]:
    from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
    from tower.ob_privacy_wall_checkpoint import build_ob_privacy_wall_checkpoint
    from tower.deny_path_replacement_audit import summarize_deny_path_replacement_receipts
    from tower.ob_exposure_mapping import build_ob_exposure_mapping_pass, summarize_ob_exposure_mapping_pass
    from tower.ui_action_audit import summarize_ui_action_audit_receipts
    from tower.archive_vault_handoff import summarize_archive_vault_handoffs
    from tower.tower_status import get_tower_status
    from tower.security_command_page import generate_security_command_dashboard
    from web.app import app

    smoke = run_ob_privacy_wall_smoke()
    privacy_checkpoint = build_ob_privacy_wall_checkpoint()
    deny_summary = summarize_deny_path_replacement_receipts(limit=12)
    mapping = build_ob_exposure_mapping_pass()
    mapping_summary = summarize_ob_exposure_mapping_pass(limit=12)
    ui_audit = summarize_ui_action_audit_receipts(limit=8)
    archive = summarize_archive_vault_handoffs(limit=8)
    tower_status = get_tower_status()
    dashboard = generate_security_command_dashboard()

    client = app.test_client()

    no_access_resp = client.get("/no-access?path=/signals?tower_keycard=SHOULD_NOT_SURVIVE")
    no_access_html = no_access_resp.get_data(as_text=True)

    observatory_private_resp = client.get("/observatory-private?tower_keycard=SHOULD_NOT_SURVIVE")
    observatory_private_html = observatory_private_resp.get_data(as_text=True)

    no_access_proof = {
        "status_code": no_access_resp.status_code,
        "has_tower": "The Tower" in no_access_html,
        "has_clearance_gate": "Clearance Gate" in no_access_html,
        "has_restricted_zone": "Restricted Zone" in no_access_html,
        "has_polished_title": "Observatory Corridor Locked" in no_access_html,
        "has_soulaana": "Soulaana:" in no_access_html,
        "old_shell_absent": "<title>Observatory Locked</title>" not in no_access_html,
        "no_keycard_query": "tower_keycard=" not in no_access_html,
        "no_test_secret": "SHOULD_NOT_SURVIVE" not in no_access_html,
    }

    observatory_private_proof = {
        "status_code": observatory_private_resp.status_code,
        "has_tower": "The Tower" in observatory_private_html,
        "has_clearance_gate": "Clearance Gate" in observatory_private_html,
        "has_restricted_zone": "Restricted Zone" in observatory_private_html,
        "has_polished_title": "Observatory Corridor Locked" in observatory_private_html,
        "has_soulaana": "Soulaana:" in observatory_private_html,
        "old_shell_absent": "<title>Observatory Locked</title>" not in observatory_private_html,
        "no_keycard_query": "tower_keycard=" not in observatory_private_html,
        "no_test_secret": "SHOULD_NOT_SURVIVE" not in observatory_private_html,
    }

    smoke_checks = smoke.get("checks", {}) if isinstance(smoke.get("checks"), dict) else {}

    proof = {
        "smoke_ok": smoke.get("ok") is True,
        "privacy_checkpoint_ok": privacy_checkpoint.get("ok") is True,
        "deny_path_replacement_receipts_ready": smoke_checks.get("deny_path_replacement_receipts_ready", {}).get("ok") is True,
        "deny_summary_ok": deny_summary.get("ok") is True,
        "deny_summary_verified_present": deny_summary.get("verified", 0) >= 1,
        "deny_summary_no_access_present": deny_summary.get("by_route", {}).get("/no-access", 0) >= 1,
        "mapping_ok": mapping.get("ok") is True,
        "mapping_total_present": mapping.get("total", 0) >= 1,
        "mapping_summary_ok": mapping_summary.get("ok") is True,
        "mapping_counts_present": bool(mapping_summary.get("counts")),
        "ui_action_audit_ok": ui_audit.get("ok") is True,
        "archive_handoff_ok": archive.get("ok") is True,
        "tower_status_archive_ok": tower_status.get("archive_vault_handoff_ok") is True,
        "tower_status_ui_audit_ok": tower_status.get("ui_action_audit_ok") is True,
        "dashboard_ok": dashboard.get("ok") is True if isinstance(dashboard, dict) else False,
        "no_access_status_403": no_access_resp.status_code == 403,
        "no_access_polished": all(no_access_proof.values()),
        "observatory_private_status_403": observatory_private_resp.status_code == 403,
        "observatory_private_polished": all(observatory_private_proof.values()),
    }

    built_packs = [
        {
            "pack": "081",
            "name": "Deny-path replacement audit receipts",
            "plain": "Replacement events can be recorded with route, behavior, proof, and status.",
        },
        {
            "pack": "082",
            "name": "Legacy no-access shell replacement",
            "plain": "/no-access now uses the polished Tower locked helper.",
        },
        {
            "pack": "083",
            "name": "Deny-path replacement smoke/checkpoint proof",
            "plain": "Smoke/checkpoint prove /no-access replacement and receipt summary.",
        },
        {
            "pack": "084",
            "name": "Exposure report mapping pass",
            "plain": "Routes are categorized into keep, map-next, retire/redirect, or later review.",
        },
        {
            "pack": "085",
            "name": "Deny-path/exposure transition checkpoint",
            "plain": "Close this block before saving and moving to the next security section.",
        },
    ]

    next_block = [
        {
            "pack": "086",
            "item": "Surface deny-path replacement receipts in Tower status/UI",
            "plain": "Show replacement receipts in Security Command like the other audit panels.",
        },
        {
            "pack": "087",
            "item": "Surface exposure mapping pass in Tower status/UI",
            "plain": "Show keep/map-next/retire/later-review route categories in Security Command.",
        },
        {
            "pack": "088",
            "item": "Smoke/checkpoint proves replacement + exposure panels",
            "plain": "Prove deny-path receipts and exposure mapping panels render safely.",
        },
        {
            "pack": "089",
            "item": "Route replacement policy list",
            "plain": "Create a controlled list of routes approved for replacement and routes that must stay untouched.",
        },
        {
            "pack": "090",
            "item": "Save/transition checkpoint",
            "plain": "Close the replacement visibility and policy-list block cleanly.",
        },
    ]

    current_boundary = {
        "done": [
            "Deny-path replacement receipts exist.",
            "Verified and needs-review replacement receipt states exist.",
            "Legacy /no-access shell is replaced by polished Tower lock.",
            "/observatory-private controlled polished deny path is still holding.",
            "Smoke/checkpoint prove deny-path replacement receipts.",
            "Exposure mapping pass categorizes current routes.",
        ],
        "not_done_yet": [
            "Deny-path replacement receipts are not yet surfaced in Security Command UI.",
            "Exposure mapping categories are not yet surfaced in Security Command UI.",
            "A formal route replacement policy list is not built yet.",
            "Most older deny paths are still intentionally untouched.",
        ],
        "why": "The privacy wall is being upgraded in small verified pieces. This keeps the fortress strict while preventing accidental route exposure.",
    }

    serialized = str([
        smoke,
        privacy_checkpoint,
        deny_summary,
        mapping,
        mapping_summary,
        ui_audit,
        archive,
        tower_status,
        dashboard,
        proof,
        no_access_proof,
        observatory_private_proof,
    ])

    no_secret_leakage = (
        "tower_keycard=" not in serialized
        and "SHOULD_NOT_SURVIVE" not in serialized
        and "raw_token=" not in serialized
        and '"raw_token":' not in serialized
        and "Bearer SHOULD_NOT_SURVIVE" not in serialized
    )

    ok = all(proof.values()) and no_secret_leakage

    return {
        "ok": bool(ok),
        "pack": "085",
        "generated_at": _utc_now(),
        "readiness_score": 100 if ok else 90,
        "readiness_label": "Ready to surface deny-path and exposure mapping panels"
        if ok
        else "Needs repair before replacement/exposure visibility",
        "proof": proof,
        "no_access_proof": no_access_proof,
        "observatory_private_proof": observatory_private_proof,
        "no_secret_leakage": no_secret_leakage,
        "deny_path_replacement_summary": {
            "ok": deny_summary.get("ok"),
            "total": deny_summary.get("total"),
            "verified": deny_summary.get("verified"),
            "needs_review": deny_summary.get("needs_review"),
            "by_status": deny_summary.get("by_status"),
            "by_route": deny_summary.get("by_route"),
            "by_replacement_type": deny_summary.get("by_replacement_type"),
            "by_severity": deny_summary.get("by_severity"),
        },
        "exposure_mapping_summary": {
            "ok": mapping_summary.get("ok"),
            "total": mapping_summary.get("total"),
            "counts": mapping_summary.get("counts"),
            "reason_counts": mapping_summary.get("reason_counts"),
            "priority_counts": mapping_summary.get("priority_counts"),
            "top_next": mapping_summary.get("top_next"),
            "retire_or_redirect": mapping_summary.get("retire_or_redirect"),
            "later_review": mapping_summary.get("later_review"),
        },
        "built_packs": built_packs,
        "next_block": next_block,
        "current_boundary": current_boundary,
        "soulaana_translation": "Soulaana: The replacement receipts are filed, the old no-access shell is retired, and the door map is sorted. Next we put those maps on the Tower wall.",
        "human_reason": "Deny-path replacement and exposure mapping transition checkpoint is ready.",
    }


if __name__ == "__main__":
    import json

    result = build_deny_path_exposure_transition_checkpoint()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("Deny-path/exposure transition checkpoint failed.")
