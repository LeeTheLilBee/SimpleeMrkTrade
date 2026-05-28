
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"
VISIBILITY_POLICY_CHECKPOINT_PATH = DATA_DIR / "visibility_policy_transition_checkpoint.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def build_visibility_policy_transition_checkpoint() -> Dict[str, Any]:
    from tower.ob_privacy_wall_smoke import run_ob_privacy_wall_smoke
    from tower.ob_privacy_wall_checkpoint import build_ob_privacy_wall_checkpoint
    from tower.deny_path_replacement_audit import summarize_deny_path_replacement_receipts
    from tower.ob_exposure_mapping import (
        build_ob_exposure_mapping_pass,
        summarize_ob_exposure_mapping_pass,
    )
    from tower.route_replacement_policy import (
        build_route_replacement_policy_list,
        get_policy_for_route,
        summarize_route_replacement_policy_list,
    )
    from tower.tower_status import get_tower_status
    from tower.security_command_page import generate_security_command_dashboard

    smoke = run_ob_privacy_wall_smoke()
    privacy_checkpoint = build_ob_privacy_wall_checkpoint()
    deny_summary = summarize_deny_path_replacement_receipts(limit=10)
    exposure = build_ob_exposure_mapping_pass()
    exposure_summary = summarize_ob_exposure_mapping_pass(limit=12)
    policy = build_route_replacement_policy_list()
    policy_summary = summarize_route_replacement_policy_list(limit=12)
    status = get_tower_status()
    dashboard = generate_security_command_dashboard()

    html_path = Path(dashboard.get("path", ""))
    dashboard_html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""

    policy_lookups = {
        "no_access": get_policy_for_route("/no-access"),
        "observatory_private": get_policy_for_route("/observatory-private"),
        "admin": get_policy_for_route("/admin"),
        "signals": get_policy_for_route("/signals"),
        "signals_symbol": get_policy_for_route("/signals/AAPL"),
        "unknown": get_policy_for_route("/brand-new-secret-door"),
    }

    smoke_checks = smoke.get("checks", {}) if isinstance(smoke.get("checks"), dict) else {}
    panel_proof = smoke_checks.get("replacement_and_exposure_panels_ready", {})

    proof = {
        "smoke_ok": smoke.get("ok") is True,
        "privacy_checkpoint_ok": privacy_checkpoint.get("ok") is True,
        "replacement_and_exposure_panels_ready": panel_proof.get("ok") is True,
        "deny_summary_ok": deny_summary.get("ok") is True,
        "deny_summary_has_no_access": deny_summary.get("by_route", {}).get("/no-access", 0) >= 1,
        "exposure_summary_ok": exposure_summary.get("ok") is True,
        "exposure_total_present": exposure_summary.get("total", 0) >= 1,
        "exposure_readiness_ready": exposure_summary.get("readiness_score") == 100,
        "policy_ok": policy.get("ok") is True,
        "policy_total_matches_exposure": policy.get("total") == exposure_summary.get("total"),
        "policy_summary_ok": policy_summary.get("ok") is True,
        "policy_has_approved_to_replace": policy_summary.get("counts", {}).get("approved_to_replace", 0) >= 1,
        "policy_has_needs_owner_review": policy_summary.get("counts", {}).get("needs_owner_review", 0) >= 1,
        "policy_has_retire_or_redirect": policy_summary.get("counts", {}).get("retire_or_redirect", 0) >= 1,
        "policy_has_tower_only": policy_summary.get("counts", {}).get("Tower_only", 0) >= 1,
        "policy_has_ob_protected": policy_summary.get("counts", {}).get("OB_protected", 0) >= 1,
        "tower_status_has_deny": status.get("deny_path_replacement_ok") is True,
        "tower_status_has_exposure": status.get("ob_exposure_mapping_ok") is True,
        "dashboard_ok": dashboard.get("ok") is True,
        "dashboard_has_deny_panel": "DENY-PATH REPLACEMENT RECEIPTS" in dashboard_html,
        "dashboard_has_exposure_panel": "OB EXPOSURE MAPPING PASS" in dashboard_html,
        "policy_lookup_no_access_approved": policy_lookups["no_access"].get("policy_decision") == "approved_to_replace",
        "policy_lookup_ob_private_approved": policy_lookups["observatory_private"].get("policy_decision") == "approved_to_replace",
        "policy_lookup_admin_retire": policy_lookups["admin"].get("policy_decision") == "retire_or_redirect",
        "policy_lookup_signals_ob": policy_lookups["signals"].get("policy_decision") == "OB_protected",
        "policy_lookup_dynamic_symbol_review": policy_lookups["signals_symbol"].get("policy_decision") == "needs_owner_review",
        "policy_lookup_unknown_review": policy_lookups["unknown"].get("policy_decision") == "needs_owner_review",
    }

    built_packs = [
        {
            "pack": "086",
            "name": "Surface deny-path replacement receipts",
            "plain": "Deny-path replacement receipt summary appears in Tower status and Security Command UI.",
        },
        {
            "pack": "087",
            "name": "Surface exposure mapping pass",
            "plain": "OB route exposure mapping appears in Tower status and Security Command UI.",
        },
        {
            "pack": "088",
            "name": "Prove replacement and exposure panels",
            "plain": "Privacy wall smoke/checkpoint prove both visibility panels render safely.",
        },
        {
            "pack": "089",
            "name": "Route replacement policy list",
            "plain": "Routes now have policy categories controlling replacement, review, protection, retirement, and ownership.",
        },
        {
            "pack": "090",
            "name": "Visibility and policy transition checkpoint",
            "plain": "Closes the visibility/policy block and prepares the audit-chain block.",
        },
    ]

    next_block = [
        {
            "pack": "091",
            "item": "Tamper-evident audit chain",
            "plain": "Create chain hashes for critical receipts so silent edits are detectable.",
        },
        {
            "pack": "092",
            "item": "Step-up authentication framework",
            "plain": "Sensitive exports, policy changes, owner actions, live/automated mode, and lockdown disable require step-up.",
        },
        {
            "pack": "093",
            "item": "Emergency lockdown system",
            "plain": "Freeze sensitive app access/actions while keeping owner recovery path.",
        },
        {
            "pack": "094",
            "item": "Quarantine mode",
            "plain": "Suspicious sessions enter a restricted holding state without full ecosystem freeze.",
        },
        {
            "pack": "095",
            "item": "Session/device/IP risk scoring foundation",
            "plain": "Risk score requests and decide allow, step_up, throttle, quarantine, lockdown, or deny.",
        },
    ]

    current_boundary = {
        "done": [
            "Deny-path replacement receipts are visible in Tower status and Security Command UI.",
            "Exposure mapping is visible in Tower status and Security Command UI.",
            "Smoke/checkpoint prove both visibility panels.",
            "Route replacement policy list exists and is generated from exposure mapping.",
            "Known locked-shell routes can be approved_to_replace.",
            "Core OB routes are OB_protected.",
            "Tower routes are Tower_only.",
            "Admin/debug/test routes are retire_or_redirect.",
            "Dynamic object routes default to needs_owner_review until object-level mapping is explicit.",
            "Unknown routes default to needs_owner_review.",
        ],
        "not_done_yet": [
            "Route policy decisions do not yet have owner action buttons in Security Command.",
            "Policy changes are not yet chained with tamper-evident hashes.",
            "Step-up authentication is not active yet.",
            "Emergency lockdown and quarantine are upcoming.",
            "Session/device/IP risk scoring is upcoming.",
        ],
        "why": "The Tower now has visibility and a route policy sheet before deeper escalation controls are added.",
    }

    serialized = json.dumps(
        [
            smoke,
            privacy_checkpoint,
            deny_summary,
            exposure,
            exposure_summary,
            policy,
            policy_summary,
            status,
            dashboard,
            policy_lookups,
            proof,
        ],
        sort_keys=True,
        default=str,
    ) + dashboard_html

    no_secret_leakage = (
        "tower_keycard=" not in serialized
        and "SHOULD_NOT_SURVIVE" not in serialized
        and "raw_token=" not in serialized
        and '"raw_token":' not in serialized
        and "Bearer SHOULD_NOT_SURVIVE" not in serialized
    )

    proof["no_secret_leakage"] = no_secret_leakage

    ok = all(proof.values())

    payload = {
        "ok": bool(ok),
        "pack": "090",
        "generated_at": _utc_now(),
        "path": str(VISIBILITY_POLICY_CHECKPOINT_PATH),
        "readiness_score": 100 if ok else 90,
        "readiness_label": (
            "Ready for tamper-evident audit chain"
            if ok
            else "Needs repair before tamper-evident audit chain"
        ),
        "proof": proof,
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
            "ok": exposure_summary.get("ok"),
            "total": exposure_summary.get("total"),
            "counts": exposure_summary.get("counts"),
            "reason_counts": exposure_summary.get("reason_counts"),
            "priority_counts": exposure_summary.get("priority_counts"),
            "readiness_label": exposure_summary.get("readiness_label"),
            "readiness_score": exposure_summary.get("readiness_score"),
        },
        "route_replacement_policy_summary": {
            "ok": policy_summary.get("ok"),
            "total": policy_summary.get("total"),
            "counts": policy_summary.get("counts"),
            "clearance_counts": policy_summary.get("clearance_counts"),
            "replacement_allowed_count": policy_summary.get("replacement_allowed_count"),
            "owner_review_count": policy_summary.get("owner_review_count"),
            "public_allowed_count": policy_summary.get("public_allowed_count"),
            "archive_handoff_count": policy_summary.get("archive_handoff_count"),
            "step_up_count": policy_summary.get("step_up_count"),
            "readiness_label": policy_summary.get("readiness_label"),
            "readiness_score": policy_summary.get("readiness_score"),
        },
        "policy_lookup_proof": policy_lookups,
        "built_packs": built_packs,
        "next_block": next_block,
        "current_boundary": current_boundary,
        "soulaana_translation": "Soulaana: The Tower can now see the changed doors, see the route map, and read the policy sheet. Next we make the receipts harder to tamper with.",
        "human_reason": "Visibility and route replacement policy block is checkpointed.",
    }

    _write_json(VISIBILITY_POLICY_CHECKPOINT_PATH, payload)
    return payload


def load_visibility_policy_transition_checkpoint() -> Dict[str, Any]:
    try:
        if not VISIBILITY_POLICY_CHECKPOINT_PATH.exists():
            return {
                "ok": False,
                "human_reason": "No visibility/policy transition checkpoint saved yet.",
                "path": str(VISIBILITY_POLICY_CHECKPOINT_PATH),
            }
        return json.loads(VISIBILITY_POLICY_CHECKPOINT_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "human_reason": "Visibility/policy checkpoint could not be loaded.",
            "error": f"{type(exc).__name__}: {exc}",
            "path": str(VISIBILITY_POLICY_CHECKPOINT_PATH),
        }


if __name__ == "__main__":
    result = build_visibility_policy_transition_checkpoint()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if not result.get("ok"):
        raise SystemExit("Visibility/policy transition checkpoint failed.")
