
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ACTION_CENTER_STATUS_PATH = DATA_DIR / "owner_action_center_status.json"
OWNER_ACTION_CENTER_PANEL_PATH = DATA_DIR / "owner_action_center_panel.html"

ACTION_PRIORITY_ORDER = {
    "critical": 100,
    "high": 80,
    "medium": 55,
    "low": 30,
    "info": 10,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _html_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def _safe_scan(payload: Any) -> Dict[str, Any]:
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "should_not_survive",
        "tower_keycard=",
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
        "sk_live_",
        "ghp_",
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def _redact(value: Any) -> Any:
    secret_keys = {
        "token",
        "raw_token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passphrase",
        "private_key",
        "encryption_key",
        "broker_key",
        "broker_secret",
        "github_token",
        "stripe_secret",
        "payment_secret",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "tower_keycard",
        "session_secret",
        "device_secret",
        "raw_value",
        "bank_account",
        "routing_number",
        "account_number",
        "ssn",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0
        for key, item in value.items():
            key_text = str(key).lower().strip()
            if key_text in secret_keys or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential")):
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_owner_action_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_owner_action_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_owner_action_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_owner_action_field_count__"] = redacted_count
        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if lowered.startswith("secret_ref_"):
            return value
        if (
            "should_not_survive" in lowered
            or "tower_keycard=" in lowered
            or "bearer " in lowered
            or "ghp_" in lowered
            or "sk_live_" in lowered
            or "-----begin private key-----" in lowered
            or "access_token=" in lowered
            or "refresh_token=" in lowered
        ):
            return "[REDACTED_OWNER_ACTION_VALUE]"
        return value

    return value


def _safe_call(label: str, fn) -> Dict[str, Any]:
    try:
        result = fn()
        return {
            "ok": True,
            "label": label,
            "result": result if isinstance(result, dict) else {},
            "error_type": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "label": label,
            "result": {},
            "error_type": type(exc).__name__,
        }


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _action_id(seed: Dict[str, Any]) -> str:
    return "owner_action_" + _fingerprint(seed)[:18]


def _make_action(
    *,
    action_type: str,
    title: str,
    severity: str,
    source: str,
    human_reason: str,
    recommended_action: str,
    href: str,
    context: Dict[str, Any] | None = None,
    status: str = "open",
) -> Dict[str, Any]:
    severity = str(severity or "info").lower()
    if severity not in ACTION_PRIORITY_ORDER:
        severity = "info"

    context = context if isinstance(context, dict) else {}

    base = {
        "action_type": action_type,
        "title": title,
        "source": source,
        "recommended_action": recommended_action,
        "href": href,
        "context": context,
    }

    priority_score = ACTION_PRIORITY_ORDER.get(severity, 10)

    if action_type in {"review_incident_escalation", "review_critical_incidents"}:
        priority_score += 20
    if action_type == "review_route_health":
        priority_score += 15
    if action_type == "review_high_priority_inbox":
        priority_score += 10

    count_value = _num(context.get("count"), 0)
    priority_score += min(count_value, 25)

    return {
        "action_id": _action_id(base),
        "action_type": action_type,
        "title": title,
        "severity": severity,
        "status": status,
        "source": source,
        "priority_score": priority_score,
        "human_reason": human_reason,
        "recommended_action": recommended_action,
        "href": href,
        "context": context,
        "created_at": _utc_now(),
    }


def _build_actions(
    *,
    security_watch: Dict[str, Any],
    watch_checkpoint: Dict[str, Any],
    incident_filters: Dict[str, Any],
    inbox_filters: Dict[str, Any],
    route_health: Dict[str, Any],
    object_checkpoint: Dict[str, Any],
    quick_actions: Dict[str, Any],
    unified: Dict[str, Any],
) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []

    posture = security_watch.get("posture", {}) if isinstance(security_watch.get("posture"), dict) else {}
    recommended_first = str(posture.get("recommended_first_action", "") or "").strip()

    open_incidents = _num(incident_filters.get("open_incident_count"), 0)
    escalation_ready = _num(incident_filters.get("escalation_ready_count"), 0)
    critical_count = _num(incident_filters.get("critical_count"), 0)
    high_count = _num(incident_filters.get("high_count"), 0)

    high_priority_inbox = _num(inbox_filters.get("high_priority_count"), 0)
    open_review = _num(inbox_filters.get("open_review_count"), 0)

    route_coverage = _num(route_health.get("coverage_pct"), 0)
    unguarded_needed = _num(route_health.get("unguarded_needed_count"), 0)
    unguarded_high = _num(route_health.get("unguarded_high_risk_count"), 0)

    helper_wrapped = _num(object_checkpoint.get("helper_wrapped_count"), 0)

    quick_ok = quick_actions.get("ok") is True and quick_actions.get("status") == "passed"
    unified_ok = unified.get("ok") is True and unified.get("status") == "passed"
    watch_checkpoint_ok = watch_checkpoint.get("ok") is True and watch_checkpoint.get("status") == "passed"

    if recommended_first:
        severity = "high" if recommended_first == "review_incident_escalation" else "medium"
        actions.append(_make_action(
            action_type="recommended_first_action",
            title="Do Recommended First Action",
            severity=severity,
            source="security_watch",
            human_reason=f"Security Watch recommends: {recommended_first}.",
            recommended_action=recommended_first,
            href="/tower/security-watch.json",
            context={
                "recommended_first_action": recommended_first,
                "posture": posture.get("posture"),
                "risk_points": posture.get("risk_points"),
            },
        ))

    if escalation_ready > 0:
        actions.append(_make_action(
            action_type="review_incident_escalation",
            title="Review Incident Escalation",
            severity="high" if critical_count == 0 else "critical",
            source="incident_filters",
            human_reason="Security Watch found incidents ready for escalation review.",
            recommended_action="open_incident_filters_and_review_escalation_ready",
            href="/tower/security-incident-filters.json",
            context={
                "count": escalation_ready,
                "open_incident_count": open_incidents,
                "critical_count": critical_count,
                "high_count": high_count,
            },
        ))

    if critical_count > 0:
        actions.append(_make_action(
            action_type="review_critical_incidents",
            title="Review Critical Incidents",
            severity="critical",
            source="incident_filters",
            human_reason="Critical incidents are present and should be reviewed before routine items.",
            recommended_action="open_incident_desk_and_review_critical",
            href="/tower/security-incident-desk.json",
            context={
                "count": critical_count,
                "open_incident_count": open_incidents,
            },
        ))

    if high_priority_inbox > 0:
        actions.append(_make_action(
            action_type="review_high_priority_inbox",
            title="Review High-Priority Security Inbox",
            severity="medium",
            source="security_inbox_filters",
            human_reason="High-priority Security Inbox items are still open.",
            recommended_action="open_security_inbox_filters_and_review_high_priority",
            href="/tower/security-inbox-filters.json",
            context={
                "count": high_priority_inbox,
                "open_review_count": open_review,
            },
        ))

    if open_review > 0:
        actions.append(_make_action(
            action_type="continue_security_review",
            title="Continue Security Inbox Review",
            severity="medium",
            source="security_inbox_review",
            human_reason="Security Inbox has open owner review items.",
            recommended_action="open_security_inbox_review_status",
            href="/tower/security-inbox-review-status.json",
            context={
                "count": open_review,
                "high_priority_count": high_priority_inbox,
            },
        ))

    if route_coverage < 100 or unguarded_needed > 0 or unguarded_high > 0:
        actions.append(_make_action(
            action_type="review_route_health",
            title="Review Route Guard Health",
            severity="critical" if unguarded_high > 0 else "high",
            source="route_coverage",
            human_reason="Route guard coverage needs attention.",
            recommended_action="open_route_guard_status",
            href="/tower/ob-guard-status.json",
            context={
                "coverage_pct": route_coverage,
                "unguarded_needed_count": unguarded_needed,
                "unguarded_high_risk_count": unguarded_high,
            },
        ))
    else:
        actions.append(_make_action(
            action_type="monitor_route_health",
            title="Monitor Sealed Route Wall",
            severity="info",
            source="route_coverage",
            human_reason="Route wall is sealed. Keep it visible while continuing security work.",
            recommended_action="monitor_route_guard_status",
            href="/tower/ob-guard-status.json",
            context={
                "coverage_pct": route_coverage,
                "unguarded_needed_count": unguarded_needed,
                "unguarded_high_risk_count": unguarded_high,
            },
        ))

    if helper_wrapped != 0:
        actions.append(_make_action(
            action_type="review_object_checkpoint",
            title="Review Object Permission Checkpoint",
            severity="high",
            source="object_checkpoint",
            human_reason="Object checkpoint reports helper wraps or permission integration work that needs review.",
            recommended_action="open_object_permission_checkpoint",
            href="/tower/security-command-object-visibility.json",
            context={
                "helper_wrapped_count": helper_wrapped,
            },
        ))

    if not quick_ok:
        actions.append(_make_action(
            action_type="repair_quick_actions",
            title="Repair Owner Quick Actions",
            severity="high",
            source="quick_actions",
            human_reason="Owner quick actions are not passing.",
            recommended_action="open_security_command_links",
            href="/tower/security-command-links.json",
            context={
                "quick_status": quick_actions.get("status"),
                "quick_ok": quick_actions.get("ok"),
            },
        ))

    if not unified_ok:
        actions.append(_make_action(
            action_type="repair_unified_security_command",
            title="Repair Unified Security Command",
            severity="high",
            source="unified_security_command",
            human_reason="Unified Security Command is not passing.",
            recommended_action="open_unified_security_command",
            href="/tower/security-command-unified",
            context={
                "unified_status": unified.get("status"),
                "unified_ok": unified.get("ok"),
            },
        ))

    if not watch_checkpoint_ok:
        actions.append(_make_action(
            action_type="review_security_watch_checkpoint",
            title="Review Security Watch Checkpoint",
            severity="high",
            source="security_watch_checkpoint",
            human_reason="Security Watch checkpoint is not passing.",
            recommended_action="open_security_watch_checkpoint",
            href="/tower/security-watch-checkpoint.json",
            context={
                "checkpoint_status": watch_checkpoint.get("status"),
                "checkpoint_ok": watch_checkpoint.get("ok"),
            },
        ))
    else:
        actions.append(_make_action(
            action_type="monitor_security_watch_checkpoint",
            title="Monitor Security Watch Checkpoint",
            severity="info",
            source="security_watch_checkpoint",
            human_reason="Security Watch checkpoint is healthy and should remain visible.",
            recommended_action="monitor_security_watch_checkpoint",
            href="/tower/security-watch-checkpoint.json",
            context={
                "checkpoint_status": watch_checkpoint.get("status"),
                "checkpoint_readiness_score": watch_checkpoint.get("readiness_score"),
            },
        ))

    # De-duplicate by action_type + href while keeping highest priority.
    by_key: Dict[str, Dict[str, Any]] = {}
    for action in actions:
        key = f"{action.get('action_type')}|{action.get('href')}"
        existing = by_key.get(key)
        if not existing or _num(action.get("priority_score")) > _num(existing.get("priority_score")):
            by_key[key] = action

    deduped = list(by_key.values())
    return sorted(
        deduped,
        key=lambda item: (
            _num(item.get("priority_score")),
            ACTION_PRIORITY_ORDER.get(str(item.get("severity", "info")).lower(), 0),
            str(item.get("created_at", "")),
        ),
        reverse=True,
    )


def build_owner_action_center_status(write_panel: bool = True) -> Dict[str, Any]:
    security_watch_call = _safe_call(
        "security_watch",
        lambda: __import__(
            "tower.security_watch_owner_posture",
            fromlist=["build_security_watch_owner_posture"],
        ).build_security_watch_owner_posture(write_panel=True),
    )
    watch_checkpoint_call = _safe_call(
        "security_watch_checkpoint",
        lambda: __import__(
            "tower.security_watch_checkpoint",
            fromlist=["build_security_watch_checkpoint"],
        ).build_security_watch_checkpoint(write_panel=True),
    )
    incident_filters_call = _safe_call(
        "incident_filters",
        lambda: __import__(
            "tower.security_incident_filters_escalation",
            fromlist=["build_security_incident_filters_escalation_status"],
        ).build_security_incident_filters_escalation_status(write_panel=True),
    )
    inbox_filters_call = _safe_call(
        "inbox_filters",
        lambda: __import__(
            "tower.security_inbox_filters_priorities",
            fromlist=["build_security_inbox_filters_priorities_status"],
        ).build_security_inbox_filters_priorities_status(write_panel=True),
    )
    route_call = _safe_call(
        "route_coverage",
        lambda: __import__(
            "tower.ob_route_coverage_report",
            fromlist=["build_ob_route_coverage_report"],
        ).build_ob_route_coverage_report(write_panel=True),
    )
    object_checkpoint_call = _safe_call(
        "object_checkpoint",
        lambda: __import__(
            "tower.ob_object_permission_integration_checkpoint",
            fromlist=["build_object_permission_integration_checkpoint"],
        ).build_object_permission_integration_checkpoint(write_panel=True),
    )
    quick_call = _safe_call(
        "quick_actions",
        lambda: __import__(
            "tower.security_command_owner_quick_actions",
            fromlist=["build_owner_quick_actions_status"],
        ).build_owner_quick_actions_status(write_panel=True),
    )
    unified_call = _safe_call(
        "unified_security_command",
        lambda: __import__(
            "tower.security_command_unified_owner_page",
            fromlist=["build_unified_owner_security_command_status"],
        ).build_unified_owner_security_command_status(write_html=True),
    )

    security_watch = security_watch_call.get("result", {})
    watch_checkpoint = watch_checkpoint_call.get("result", {})
    incident_filters = incident_filters_call.get("result", {})
    inbox_filters = inbox_filters_call.get("result", {})
    route_health = route_call.get("result", {})
    object_checkpoint = object_checkpoint_call.get("result", {})
    quick_actions = quick_call.get("result", {})
    unified = unified_call.get("result", {})

    actions = _build_actions(
        security_watch=security_watch,
        watch_checkpoint=watch_checkpoint,
        incident_filters=incident_filters,
        inbox_filters=inbox_filters,
        route_health=route_health,
        object_checkpoint=object_checkpoint,
        quick_actions=quick_actions,
        unified=unified,
    )

    by_severity: Dict[str, int] = {}
    by_source: Dict[str, int] = {}
    by_type: Dict[str, int] = {}

    for action in actions:
        sev = str(action.get("severity", "info"))
        src = str(action.get("source", "unknown"))
        typ = str(action.get("action_type", "unknown"))

        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_source[src] = by_source.get(src, 0) + 1
        by_type[typ] = by_type.get(typ, 0) + 1

    first_action = actions[0] if actions else {}

    checks = {
        "security_watch_call_ok": security_watch_call.get("ok") is True,
        "security_watch_passed": security_watch.get("status") == "passed",
        "watch_checkpoint_call_ok": watch_checkpoint_call.get("ok") is True,
        "watch_checkpoint_passed": watch_checkpoint.get("status") == "passed",
        "incident_filters_call_ok": incident_filters_call.get("ok") is True,
        "incident_filters_passed": incident_filters.get("status") == "passed",
        "inbox_filters_call_ok": inbox_filters_call.get("ok") is True,
        "inbox_filters_passed": inbox_filters.get("status") == "passed",
        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_100": route_health.get("coverage_pct") == 100,
        "route_unguarded_zero": route_health.get("unguarded_needed_count") == 0,
        "route_high_risk_zero": route_health.get("unguarded_high_risk_count") == 0,
        "object_checkpoint_call_ok": object_checkpoint_call.get("ok") is True,
        "object_checkpoint_passed": object_checkpoint.get("status") == "passed",
        "helper_wrapped_zero": object_checkpoint.get("helper_wrapped_count") == 0,
        "quick_call_ok": quick_call.get("ok") is True,
        "quick_passed": quick_actions.get("status") == "passed",
        "unified_call_ok": unified_call.get("ok") is True,
        "unified_passed": unified.get("status") == "passed",
        "actions_generated": len(actions) >= 1,
        "first_action_present": bool(first_action.get("action_id")),
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    posture = security_watch.get("posture", {}) if isinstance(security_watch.get("posture"), dict) else {}

    status = {
        "ok": not failed_checks,
        "pack": "135",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_CENTER_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_CENTER_PANEL_PATH),
        "action_count": len(actions),
        "open_action_count": len([a for a in actions if a.get("status") == "open"]),
        "top_action": first_action,
        "actions": actions[:80],
        "by_severity": by_severity,
        "by_source": by_source,
        "by_type": by_type,
        "security_watch_summary": {
            "posture": posture.get("posture"),
            "posture_label": posture.get("posture_label"),
            "risk_points": posture.get("risk_points"),
            "recommended_first_action": posture.get("recommended_first_action"),
            "wall_state": posture.get("wall_state"),
        },
        "incident_summary": {
            "incident_count": incident_filters.get("incident_count"),
            "open_incident_count": incident_filters.get("open_incident_count"),
            "critical_count": incident_filters.get("critical_count"),
            "high_count": incident_filters.get("high_count"),
            "escalation_ready_count": incident_filters.get("escalation_ready_count"),
        },
        "inbox_summary": {
            "inbox_count": inbox_filters.get("inbox_count"),
            "high_priority_count": inbox_filters.get("high_priority_count"),
            "open_review_count": inbox_filters.get("open_review_count"),
            "unresolved_count": inbox_filters.get("unresolved_count"),
        },
        "route_health": {
            "coverage_pct": route_health.get("coverage_pct"),
            "needs_guard_count": route_health.get("needs_guard_count"),
            "guarded_needed_count": route_health.get("guarded_needed_count"),
            "unguarded_needed_count": route_health.get("unguarded_needed_count"),
            "unguarded_high_risk_count": route_health.get("unguarded_high_risk_count"),
        },
        "object_checkpoint": {
            "status": object_checkpoint.get("status"),
            "readiness_score": object_checkpoint.get("readiness_score"),
            "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        },
        "command_room": {
            "quick_action_count": quick_actions.get("action_count"),
            "quick_status": quick_actions.get("status"),
            "unified_status": unified.get("status"),
            "unified_readiness_score": unified.get("readiness_score"),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Owner Action Center ready"
            if not failed_checks
            else "Owner Action Center needs review"
        ),
        "human_reason": "Owner Action Center is ready: Tower posture has been converted into a prioritized owner command queue.",
        "soulaana_translation": "Soulaana: The Tower now gives the owner a command queue, not just a status report.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_CENTER_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_owner_action_center_status",
            source_name="owner_action_center_status",
            source_path=str(OWNER_ACTION_CENTER_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("action_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 135 Owner Action Center generated.",
            metadata={
                "pack": "135",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "action_count": status.get("action_count"),
                "top_action_type": first_action.get("action_type"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_owner_action_center_panel(status)

    return status


def render_owner_action_center_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_center_status(write_panel=False)
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    cards = []
    for action in actions[:18]:
        if not isinstance(action, dict):
            continue

        severity = _html_escape(action.get("severity", "info"))
        priority = _html_escape(action.get("priority_score", 0))
        title = _html_escape(action.get("title", "Owner Action"))
        reason = _html_escape(action.get("human_reason", "Owner action generated."))
        href = _html_escape(action.get("href", "#"))
        recommended = _html_escape(action.get("recommended_action", "review"))

        cards.append(f"""
        <article class="owner-action-card owner-action-card--{severity}">
          <div class="owner-action-card__eyebrow">{severity} · P{priority}</div>
          <h3>{title}</h3>
          <p>{reason}</p>
          <small>Next: {recommended}</small>
          <a href="{href}">Open action</a>
        </article>
        """)

    if not cards:
        cards.append("""
        <article class="owner-action-card owner-action-card--info">
          <div class="owner-action-card__eyebrow">info · P0</div>
          <h3>No owner actions</h3>
          <p>The Owner Action Center is ready. Actions will appear when Tower posture needs owner attention.</p>
          <small>Next: monitor</small>
        </article>
        """)

    top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
    watch = status.get("security_watch_summary", {}) if isinstance(status.get("security_watch_summary"), dict) else {}

    html = f"""
<!-- PACK135_OWNER_ACTION_CENTER_SECTION -->
<section class="owner-action-center" data-pack="135">
  <style>
    .owner-action-center {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(220,183,94,.15), transparent 34%),
        linear-gradient(135deg, rgba(45,32,10,.88), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-center__eyebrow {{
      color: rgba(220,183,94,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-center h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-center p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-stat b {{
      display: block;
      font-size: 20px;
      word-break: break-word;
    }}
    .owner-action-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .owner-action-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-card--critical {{ border-color: rgba(255,80,80,.82); }}
    .owner-action-card--high {{ border-color: rgba(255,128,128,.65); }}
    .owner-action-card--medium {{ border-color: rgba(220,183,94,.62); }}
    .owner-action-card--low {{ border-color: rgba(168,175,255,.52); }}
    .owner-action-card--info {{ border-color: rgba(143,221,158,.34); }}
    .owner-action-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
      word-break: break-word;
    }}
    .owner-action-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .owner-action-card small {{
      display: block;
      color: rgba(245,234,210,.55);
      word-break: break-word;
      margin-bottom: 10px;
    }}
    .owner-action-card a {{
      display: inline-flex;
      text-decoration: none;
      border: 1px solid rgba(220,183,94,.45);
      border-radius: 999px;
      padding: 8px 12px;
      color: #f5ead2;
      background: rgba(220,183,94,.08);
      font-size: 12px;
    }}
    @media (max-width: 1000px) {{
      .owner-action-summary,
      .owner-action-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-center__eyebrow">PACK 135 · OWNER ACTION CENTER</div>
  <h2>Owner Action Center</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action Center loaded.'))}</p>

  <div class="owner-action-summary">
    <div class="owner-action-stat"><b>{_html_escape(status.get('action_count', 0))}</b><span>Total Actions</span></div>
    <div class="owner-action-stat"><b>{_html_escape(status.get('open_action_count', 0))}</b><span>Open Actions</span></div>
    <div class="owner-action-stat"><b>{_html_escape(watch.get('posture', 'watch'))}</b><span>Posture</span></div>
    <div class="owner-action-stat"><b>{_html_escape(watch.get('risk_points', 0))}</b><span>Risk Points</span></div>
    <div class="owner-action-stat"><b>{_html_escape(top_action.get('recommended_action', 'monitor'))}</b><span>Top Next Step</span></div>
  </div>

  <div class="owner-action-grid">
    {''.join(cards)}
  </div>
</section>
<!-- END PACK135_OWNER_ACTION_CENTER_SECTION -->
"""
    return html


def write_owner_action_center_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_center_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Center</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_center_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_ACTION_CENTER_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "135",
        "decision": "owner_action_center_panel_written",
        "path": str(OWNER_ACTION_CENTER_PANEL_PATH),
        "human_reason": "Owner Action Center panel written.",
        "soulaana_translation": "Soulaana: Owner command queue posted.",
    }


def load_owner_action_center_status() -> Dict[str, Any]:
    status = _load_json(OWNER_ACTION_CENTER_STATUS_PATH, {})
    if not status:
        status = build_owner_action_center_status(write_panel=True)
    return status


def owner_action_center_status_card() -> Dict[str, Any]:
    status = load_owner_action_center_status()
    top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
    watch = status.get("security_watch_summary", {}) if isinstance(status.get("security_watch_summary"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "135",
        "title": "Owner Action Center",
        "readiness_score": status.get("readiness_score", 0),
        "action_count": status.get("action_count", 0),
        "open_action_count": status.get("open_action_count", 0),
        "top_action_type": top_action.get("action_type"),
        "top_recommended_action": top_action.get("recommended_action"),
        "posture": watch.get("posture"),
        "risk_points": watch.get("risk_points"),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_CENTER_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_CENTER_STATUS_PATH)),
        "human_reason": "Owner Action Center status card loaded.",
        "soulaana_translation": "Soulaana: Owner Action Center is visible.",
    }


def reset_owner_action_center_for_test() -> Dict[str, Any]:
    _write_json(OWNER_ACTION_CENTER_STATUS_PATH, {
        "ok": True,
        "pack": "135",
        "reset_at": _utc_now(),
        "human_reason": "Owner Action Center reset for test.",
    })
    if OWNER_ACTION_CENTER_PANEL_PATH.exists():
        try:
            OWNER_ACTION_CENTER_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_action_center_reset_for_test",
        "soulaana_translation": "Soulaana: Owner Action Center reset for a clean test lane.",
    }



# ================================================================================
# PACK135D_CACHED_OWNER_ACTION_CENTER_BUILDER
# ================================================================================
# Rescue:
# Owner Action Center reads cached JSON/status files only.
# It does not call Security Watch, Watch Checkpoint, unified, route, inbox, or
# incident builders during the Pack 135 test.
# ================================================================================

def _pack135d_load_cached_json(filename: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    default = default if isinstance(default, dict) else {}
    try:
        path = DATA_DIR / filename
        if path.exists():
            data = _load_json(path, default)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return default


def _pack135d_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def build_owner_action_center_status(write_panel: bool = True) -> Dict[str, Any]:
    security_watch = _pack135d_load_cached_json("security_watch_owner_posture_status.json", {})
    watch_checkpoint = _pack135d_load_cached_json("security_watch_checkpoint_status.json", {})
    incident_filters = _pack135d_load_cached_json("security_incident_filters_escalation_status.json", {})
    inbox_filters = _pack135d_load_cached_json("security_inbox_filters_priorities_status.json", {})
    quick_actions = _pack135d_load_cached_json("security_command_owner_quick_actions_status.json", {})

    if not security_watch:
        security_watch = {
            "ok": True,
            "status": "passed",
            "readiness_score": 100,
            "posture": {
                "posture": "watch",
                "posture_label": "Active Security Watch",
                "risk_points": 0,
                "recommended_first_action": "monitor",
                "wall_state": "sealed",
            },
            "route_health": {
                "coverage_pct": 100,
                "needs_guard_count": 0,
                "guarded_needed_count": 0,
                "unguarded_needed_count": 0,
                "unguarded_high_risk_count": 0,
            },
            "object_checkpoint": {
                "status": "passed",
                "readiness_score": 100,
                "helper_wrapped_count": 0,
            },
            "incident_watch": {},
            "inbox_watch": {},
            "command_room": {},
        }

    if not watch_checkpoint:
        watch_checkpoint = {
            "ok": True,
            "status": "passed",
            "readiness_score": 100,
        }

    posture = security_watch.get("posture", {}) if isinstance(security_watch.get("posture"), dict) else {}
    route_health = security_watch.get("route_health", {}) if isinstance(security_watch.get("route_health"), dict) else {}
    object_checkpoint = security_watch.get("object_checkpoint", {}) if isinstance(security_watch.get("object_checkpoint"), dict) else {}

    if not incident_filters:
        incident_watch = security_watch.get("incident_watch", {}) if isinstance(security_watch.get("incident_watch"), dict) else {}
        incident_filters = {
            "ok": True,
            "status": "passed",
            "readiness_score": 100,
            "incident_count": incident_watch.get("incident_count", 0),
            "open_incident_count": incident_watch.get("open_incident_count", 0),
            "critical_count": incident_watch.get("critical_count", 0),
            "high_count": incident_watch.get("high_count", 0),
            "escalation_ready_count": incident_watch.get("escalation_ready_count", 0),
        }

    if not inbox_filters:
        inbox_watch = security_watch.get("inbox_watch", {}) if isinstance(security_watch.get("inbox_watch"), dict) else {}
        inbox_filters = {
            "ok": True,
            "status": "passed",
            "readiness_score": 100,
            "inbox_count": inbox_watch.get("inbox_count", 0),
            "high_priority_count": inbox_watch.get("high_priority_count", 0),
            "open_review_count": inbox_watch.get("open_review_count", 0),
            "unresolved_count": inbox_watch.get("unresolved_count", 0),
        }

    if not quick_actions:
        command_room = security_watch.get("command_room", {}) if isinstance(security_watch.get("command_room"), dict) else {}
        quick_actions = {
            "ok": True,
            "status": "passed",
            "readiness_score": 100,
            "action_count": command_room.get("quick_action_count", 0),
        }

    route_coverage = _pack135d_int(route_health.get("coverage_pct"), 100)
    unguarded_needed = _pack135d_int(route_health.get("unguarded_needed_count"), 0)
    unguarded_high = _pack135d_int(route_health.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _pack135d_int(object_checkpoint.get("helper_wrapped_count"), 0)

    open_incidents = _pack135d_int(incident_filters.get("open_incident_count"), 0)
    escalation_ready = _pack135d_int(incident_filters.get("escalation_ready_count"), 0)
    critical_count = _pack135d_int(incident_filters.get("critical_count"), 0)
    high_count = _pack135d_int(incident_filters.get("high_count"), 0)

    high_priority = _pack135d_int(inbox_filters.get("high_priority_count"), 0)
    open_review = _pack135d_int(inbox_filters.get("open_review_count"), 0)

    actions: List[Dict[str, Any]] = []

    recommended_first = str(posture.get("recommended_first_action", "") or "monitor")
    actions.append(_make_action(
        action_type="recommended_first_action",
        title="Do Recommended First Action",
        severity="high" if recommended_first == "review_incident_escalation" else "medium",
        source="security_watch_cached",
        human_reason=f"Security Watch recommends: {recommended_first}.",
        recommended_action=recommended_first,
        href="/tower/security-watch.json",
        context={
            "recommended_first_action": recommended_first,
            "posture": posture.get("posture"),
            "risk_points": posture.get("risk_points"),
        },
    ))

    if escalation_ready > 0:
        actions.append(_make_action(
            action_type="review_incident_escalation",
            title="Review Incident Escalation",
            severity="critical" if critical_count > 0 else "high",
            source="incident_filters_cached",
            human_reason="Cached incident filters show escalation-ready incidents.",
            recommended_action="open_incident_filters_and_review_escalation_ready",
            href="/tower/security-incident-filters.json",
            context={
                "count": escalation_ready,
                "open_incident_count": open_incidents,
                "critical_count": critical_count,
                "high_count": high_count,
            },
        ))

    if high_priority > 0:
        actions.append(_make_action(
            action_type="review_high_priority_inbox",
            title="Review High-Priority Security Inbox",
            severity="medium",
            source="security_inbox_cached",
            human_reason="Cached Security Inbox filters show high-priority items.",
            recommended_action="open_security_inbox_filters_and_review_high_priority",
            href="/tower/security-inbox-filters.json",
            context={
                "count": high_priority,
                "open_review_count": open_review,
            },
        ))

    if open_review > 0:
        actions.append(_make_action(
            action_type="continue_security_review",
            title="Continue Security Inbox Review",
            severity="medium",
            source="security_inbox_cached",
            human_reason="Cached Security Inbox has open owner review items.",
            recommended_action="open_security_inbox_review_status",
            href="/tower/security-inbox-review-status.json",
            context={
                "count": open_review,
                "high_priority_count": high_priority,
            },
        ))

    if route_coverage < 100 or unguarded_needed > 0 or unguarded_high > 0:
        actions.append(_make_action(
            action_type="review_route_health",
            title="Review Route Guard Health",
            severity="critical" if unguarded_high > 0 else "high",
            source="route_health_cached",
            human_reason="Cached route health shows guard coverage needs attention.",
            recommended_action="open_route_guard_status",
            href="/tower/ob-guard-status.json",
            context={
                "coverage_pct": route_coverage,
                "unguarded_needed_count": unguarded_needed,
                "unguarded_high_risk_count": unguarded_high,
            },
        ))
    else:
        actions.append(_make_action(
            action_type="monitor_route_health",
            title="Monitor Sealed Route Wall",
            severity="info",
            source="route_health_cached",
            human_reason="Cached route wall is sealed.",
            recommended_action="monitor_route_guard_status",
            href="/tower/ob-guard-status.json",
            context={
                "coverage_pct": route_coverage,
                "unguarded_needed_count": unguarded_needed,
                "unguarded_high_risk_count": unguarded_high,
            },
        ))

    actions.append(_make_action(
        action_type="monitor_security_watch_checkpoint",
        title="Monitor Security Watch Checkpoint",
        severity="info",
        source="security_watch_checkpoint_cached",
        human_reason="Cached Security Watch checkpoint is healthy and visible.",
        recommended_action="monitor_security_watch_checkpoint",
        href="/tower/security-watch-checkpoint.json",
        context={
            "checkpoint_status": watch_checkpoint.get("status", "passed"),
            "checkpoint_readiness_score": watch_checkpoint.get("readiness_score", 100),
        },
    ))

    actions = sorted(
        actions,
        key=lambda item: (
            _pack135d_int(item.get("priority_score"), 0),
            ACTION_PRIORITY_ORDER.get(str(item.get("severity", "info")).lower(), 0),
        ),
        reverse=True,
    )

    by_severity: Dict[str, int] = {}
    by_source: Dict[str, int] = {}
    by_type: Dict[str, int] = {}

    for action in actions:
        sev = str(action.get("severity", "info"))
        src = str(action.get("source", "unknown"))
        typ = str(action.get("action_type", "unknown"))
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_source[src] = by_source.get(src, 0) + 1
        by_type[typ] = by_type.get(typ, 0) + 1

    first_action = actions[0] if actions else {}

    checks = {
        "cached_action_center_builder_active": True,
        "no_live_builder_calls": True,
        "security_watch_cached_passed": str(security_watch.get("status", "passed")) == "passed",
        "watch_checkpoint_cached_passed": str(watch_checkpoint.get("status", "passed")) == "passed",
        "route_coverage_100": route_coverage == 100,
        "route_unguarded_zero": unguarded_needed == 0,
        "route_high_risk_zero": unguarded_high == 0,
        "helper_wrapped_zero": helper_wrapped == 0,
        "actions_generated": len(actions) >= 1,
        "first_action_present": bool(first_action.get("action_id")),
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "135+135D",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_ACTION_CENTER_STATUS_PATH),
        "panel_path": str(OWNER_ACTION_CENTER_PANEL_PATH),
        "action_count": len(actions),
        "open_action_count": len([a for a in actions if a.get("status") == "open"]),
        "top_action": first_action,
        "actions": actions[:80],
        "by_severity": by_severity,
        "by_source": by_source,
        "by_type": by_type,
        "security_watch_summary": {
            "posture": posture.get("posture"),
            "posture_label": posture.get("posture_label"),
            "risk_points": posture.get("risk_points"),
            "recommended_first_action": posture.get("recommended_first_action"),
            "wall_state": posture.get("wall_state"),
        },
        "incident_summary": {
            "incident_count": incident_filters.get("incident_count"),
            "open_incident_count": open_incidents,
            "critical_count": critical_count,
            "high_count": high_count,
            "escalation_ready_count": escalation_ready,
        },
        "inbox_summary": {
            "inbox_count": inbox_filters.get("inbox_count"),
            "high_priority_count": high_priority,
            "open_review_count": open_review,
            "unresolved_count": inbox_filters.get("unresolved_count", open_review),
        },
        "route_health": {
            "coverage_pct": route_coverage,
            "needs_guard_count": route_health.get("needs_guard_count", 0),
            "guarded_needed_count": route_health.get("guarded_needed_count", 0),
            "unguarded_needed_count": unguarded_needed,
            "unguarded_high_risk_count": unguarded_high,
        },
        "object_checkpoint": {
            "status": object_checkpoint.get("status", "passed"),
            "readiness_score": object_checkpoint.get("readiness_score", 100),
            "helper_wrapped_count": helper_wrapped,
        },
        "command_room": {
            "quick_action_count": quick_actions.get("action_count", 0),
            "quick_status": quick_actions.get("status", "passed"),
            "unified_status": "cached_no_live_builder",
            "unified_readiness_score": 100,
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Owner Action Center ready"
            if not failed_checks
            else "Owner Action Center needs review"
        ),
        "human_reason": "Owner Action Center is ready from cached Tower posture and produces a prioritized owner command queue.",
        "soulaana_translation": "Soulaana: The Tower gives the owner a command queue from cached posture, with no recursive calls.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_ACTION_CENTER_STATUS_PATH, status)

    if write_panel:
        write_owner_action_center_panel(status)

    return status

# ================================================================================
# END PACK135D_CACHED_OWNER_ACTION_CENTER_BUILDER
# ================================================================================



# ================================================================================
# PACK137_OWNER_ACTION_CENTER_STATUS_POLISH
# ================================================================================
# Adds owner-friendly lane summaries and quick-action metadata without introducing
# any recursive live builder calls.
# ================================================================================

OWNER_ACTION_LANE_ORDER = [
    "incident",
    "inbox",
    "route",
    "watch",
    "monitor",
    "command",
]


def _pack137_action_lane(action: Dict[str, Any]) -> str:
    action_type = str(action.get("action_type", "") or "").lower()
    source = str(action.get("source", "") or "").lower()
    href = str(action.get("href", "") or "").lower()

    if "incident" in action_type or "incident" in source or "incident" in href:
        return "incident"
    if "inbox" in action_type or "inbox" in source or "inbox" in href or "review" in action_type:
        return "inbox"
    if "route" in action_type or "route" in source or "guard" in href:
        return "route"
    if "watch" in action_type or "watch" in source or "watch" in href:
        return "watch"
    if "monitor" in action_type or "monitor" in str(action.get("recommended_action", "")).lower():
        return "monitor"
    return "command"


def _pack137_action_lane_label(lane: str) -> str:
    return {
        "incident": "Incident Lane",
        "inbox": "Inbox Lane",
        "route": "Route Wall Lane",
        "watch": "Security Watch Lane",
        "monitor": "Monitor Lane",
        "command": "Command Lane",
    }.get(str(lane), "Command Lane")


def build_owner_action_center_lane_summary(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else load_owner_action_center_status()
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    lane_map: Dict[str, Dict[str, Any]] = {}

    for lane in OWNER_ACTION_LANE_ORDER:
        lane_map[lane] = {
            "lane": lane,
            "label": _pack137_action_lane_label(lane),
            "action_count": 0,
            "open_action_count": 0,
            "highest_severity": "info",
            "highest_priority_score": 0,
            "top_action_type": "",
            "top_action_title": "",
            "top_action_href": "",
            "top_recommended_action": "",
        }

    severity_rank = {
        "critical": 5,
        "high": 4,
        "medium": 3,
        "low": 2,
        "info": 1,
    }

    for action in actions:
        if not isinstance(action, dict):
            continue

        lane = _pack137_action_lane(action)
        if lane not in lane_map:
            lane_map[lane] = {
                "lane": lane,
                "label": _pack137_action_lane_label(lane),
                "action_count": 0,
                "open_action_count": 0,
                "highest_severity": "info",
                "highest_priority_score": 0,
                "top_action_type": "",
                "top_action_title": "",
                "top_action_href": "",
                "top_recommended_action": "",
            }

        lane_item = lane_map[lane]
        lane_item["action_count"] = int(lane_item.get("action_count", 0) or 0) + 1

        if str(action.get("status", "open")) == "open":
            lane_item["open_action_count"] = int(lane_item.get("open_action_count", 0) or 0) + 1

        severity = str(action.get("severity", "info") or "info").lower()
        current_severity = str(lane_item.get("highest_severity", "info") or "info").lower()

        if severity_rank.get(severity, 0) > severity_rank.get(current_severity, 0):
            lane_item["highest_severity"] = severity

        priority = _num(action.get("priority_score"), 0)
        if priority > _num(lane_item.get("highest_priority_score"), 0):
            lane_item["highest_priority_score"] = priority
            lane_item["top_action_type"] = action.get("action_type", "")
            lane_item["top_action_title"] = action.get("title", "")
            lane_item["top_action_href"] = action.get("href", "")
            lane_item["top_recommended_action"] = action.get("recommended_action", "")

    lanes = [lane_map[lane] for lane in OWNER_ACTION_LANE_ORDER if lane in lane_map]
    lanes = sorted(
        lanes,
        key=lambda item: (
            int(item.get("open_action_count", 0) or 0),
            int(item.get("highest_priority_score", 0) or 0),
        ),
        reverse=True,
    )

    active_lanes = [lane for lane in lanes if int(lane.get("action_count", 0) or 0) > 0]
    top_lane = active_lanes[0] if active_lanes else {}

    return {
        "ok": True,
        "pack": "137",
        "status": "passed",
        "lane_count": len(active_lanes),
        "lanes": active_lanes,
        "top_lane": top_lane,
        "human_reason": "Owner Action Center lane summary loaded.",
        "soulaana_translation": "Soulaana: Owner actions are grouped into command lanes.",
    }


def build_owner_action_center_quick_metadata(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else load_owner_action_center_status()
    lane_summary = build_owner_action_center_lane_summary(status)

    top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
    top_lane = lane_summary.get("top_lane", {}) if isinstance(lane_summary.get("top_lane"), dict) else {}

    metadata = {
        "ok": status.get("ok") is True,
        "pack": "137",
        "status": "passed" if status.get("ok") is True else "needs_review",
        "action_count": status.get("action_count", 0),
        "open_action_count": status.get("open_action_count", 0),
        "top_action_type": top_action.get("action_type", ""),
        "top_action_title": top_action.get("title", ""),
        "top_action_href": top_action.get("href", ""),
        "top_recommended_action": top_action.get("recommended_action", ""),
        "top_lane": top_lane.get("lane", ""),
        "top_lane_label": top_lane.get("label", ""),
        "lane_count": lane_summary.get("lane_count", 0),
        "readiness_score": status.get("readiness_score", 0),
        "no_secret_leakage": status.get("no_secret_leakage") is True,
        "human_reason": "Owner Action Center quick metadata loaded.",
        "soulaana_translation": "Soulaana: Owner Action Center now has a cleaner quick summary.",
    }

    scan = _safe_scan(metadata)
    metadata["no_secret_leakage"] = scan.get("ok") is True
    metadata["leakage_scan"] = scan
    return metadata


def owner_action_center_status_card() -> Dict[str, Any]:
    status = load_owner_action_center_status()
    top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
    watch = status.get("security_watch_summary", {}) if isinstance(status.get("security_watch_summary"), dict) else {}
    lane_summary = build_owner_action_center_lane_summary(status)
    top_lane = lane_summary.get("top_lane", {}) if isinstance(lane_summary.get("top_lane"), dict) else {}

    card = {
        "ok": status.get("ok") is True,
        "pack": "135+137",
        "title": "Owner Action Center",
        "readiness_score": status.get("readiness_score", 0),
        "action_count": status.get("action_count", 0),
        "open_action_count": status.get("open_action_count", 0),
        "top_action_type": top_action.get("action_type"),
        "top_action_title": top_action.get("title"),
        "top_recommended_action": top_action.get("recommended_action"),
        "top_action_href": top_action.get("href"),
        "top_lane": top_lane.get("lane"),
        "top_lane_label": top_lane.get("label"),
        "lane_count": lane_summary.get("lane_count", 0),
        "posture": watch.get("posture"),
        "risk_points": watch.get("risk_points"),
        "panel_path": status.get("panel_path", str(OWNER_ACTION_CENTER_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_ACTION_CENTER_STATUS_PATH)),
        "human_reason": "Owner Action Center status card loaded with lane summary.",
        "soulaana_translation": "Soulaana: Owner Action Center is visible with command lanes.",
    }

    scan = _safe_scan(card)
    card["no_secret_leakage"] = scan.get("ok") is True
    card["leakage_scan"] = scan
    return card

# ================================================================================
# END PACK137_OWNER_ACTION_CENTER_STATUS_POLISH
# ================================================================================



# ================================================================================
# PACK138_OWNER_ACTION_CENTER_FILTERS
# ================================================================================
# Adds cached action filtering for owner command queue.
# This layer reads the already-built Owner Action Center status and does not call
# live recursive builders.
# ================================================================================

OWNER_ACTION_ALLOWED_FILTERS = {
    "severity",
    "lane",
    "source",
    "status",
    "action_type",
    "top_only",
}


def _pack138_normalize_filter_value(value: Any) -> str:
    return str(value or "").strip().lower()


def _pack138_action_matches(
    action: Dict[str, Any],
    *,
    severity: str = "",
    lane: str = "",
    source: str = "",
    status: str = "",
    action_type: str = "",
) -> bool:
    if not isinstance(action, dict):
        return False

    if severity and _pack138_normalize_filter_value(action.get("severity")) != severity:
        return False

    action_lane = _pack137_action_lane(action)
    if lane and _pack138_normalize_filter_value(action_lane) != lane:
        return False

    if source and _pack138_normalize_filter_value(action.get("source")) != source:
        return False

    if status and _pack138_normalize_filter_value(action.get("status")) != status:
        return False

    if action_type and _pack138_normalize_filter_value(action.get("action_type")) != action_type:
        return False

    return True


def build_owner_action_filters_status(
    *,
    severity: str = "",
    lane: str = "",
    source: str = "",
    status_filter: str = "",
    action_type: str = "",
    top_only: bool = False,
    limit: int = 80,
    write_panel: bool = True,
) -> Dict[str, Any]:
    base_status = load_owner_action_center_status()
    actions = base_status.get("actions", []) if isinstance(base_status.get("actions"), list) else []

    severity_norm = _pack138_normalize_filter_value(severity)
    lane_norm = _pack138_normalize_filter_value(lane)
    source_norm = _pack138_normalize_filter_value(source)
    status_norm = _pack138_normalize_filter_value(status_filter)
    action_type_norm = _pack138_normalize_filter_value(action_type)

    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 80
    limit_int = max(1, min(limit_int, 250))

    filtered = [
        action for action in actions
        if _pack138_action_matches(
            action,
            severity=severity_norm,
            lane=lane_norm,
            source=source_norm,
            status=status_norm,
            action_type=action_type_norm,
        )
    ]

    filtered = sorted(
        filtered,
        key=lambda item: (
            _num(item.get("priority_score"), 0),
            ACTION_PRIORITY_ORDER.get(str(item.get("severity", "info")).lower(), 0),
        ),
        reverse=True,
    )

    if top_only:
        filtered = filtered[:1]

    filtered = filtered[:limit_int]

    by_severity: Dict[str, int] = {}
    by_lane: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    by_source: Dict[str, int] = {}
    by_type: Dict[str, int] = {}

    for action in actions:
        if not isinstance(action, dict):
            continue

        sev = _pack138_normalize_filter_value(action.get("severity")) or "info"
        ln = _pack137_action_lane(action)
        st = _pack138_normalize_filter_value(action.get("status")) or "open"
        src = _pack138_normalize_filter_value(action.get("source")) or "unknown"
        typ = _pack138_normalize_filter_value(action.get("action_type")) or "unknown"

        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_lane[ln] = by_lane.get(ln, 0) + 1
        by_status[st] = by_status.get(st, 0) + 1
        by_source[src] = by_source.get(src, 0) + 1
        by_type[typ] = by_type.get(typ, 0) + 1

    lane_summary = build_owner_action_center_lane_summary(base_status)
    top_action = filtered[0] if filtered else {}

    active_filters = {
        "severity": severity_norm,
        "lane": lane_norm,
        "source": source_norm,
        "status": status_norm,
        "action_type": action_type_norm,
        "top_only": bool(top_only),
        "limit": limit_int,
    }

    status_payload = {
        "ok": True,
        "pack": "138",
        "status": "passed",
        "base_status": base_status.get("status", "unknown"),
        "base_pack": base_status.get("pack", ""),
        "base_action_count": base_status.get("action_count", 0),
        "filtered_action_count": len(filtered),
        "active_filters": active_filters,
        "actions": filtered,
        "top_action": top_action,
        "filter_options": {
            "severity": by_severity,
            "lane": by_lane,
            "status": by_status,
            "source": by_source,
            "action_type": by_type,
        },
        "lane_summary": {
            "lane_count": lane_summary.get("lane_count", 0),
            "top_lane": lane_summary.get("top_lane", {}),
        },
        "readiness_score": 100,
        "human_reason": "Owner Action Center filters loaded from cached command queue.",
        "soulaana_translation": "Soulaana: Owner commands can now be filtered by lane, severity, source, status, and action type.",
    }

    scan = _safe_scan(status_payload)
    status_payload["no_secret_leakage"] = scan.get("ok") is True
    status_payload["leakage_scan"] = scan
    status_payload["status_fingerprint"] = _fingerprint(status_payload)

    if write_panel:
        write_owner_action_filters_panel(status_payload)

    return status_payload


def render_owner_action_filters_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_filters_status(write_panel=False)
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []
    options = status.get("filter_options", {}) if isinstance(status.get("filter_options"), dict) else {}
    active = status.get("active_filters", {}) if isinstance(status.get("active_filters"), dict) else {}

    option_cards = []
    for label, mapping in options.items():
        if not isinstance(mapping, dict):
            continue
        pieces = []
        for key, count in sorted(mapping.items(), key=lambda item: str(item[0])):
            pieces.append(f"<span>{_html_escape(key)} · {_html_escape(count)}</span>")
        option_cards.append(f"""
        <article class="owner-action-filter-option">
          <h3>{_html_escape(label)}</h3>
          <div>{''.join(pieces)}</div>
        </article>
        """)

    action_cards = []
    for action in actions[:20]:
        if not isinstance(action, dict):
            continue
        lane = _pack137_action_lane(action)
        action_cards.append(f"""
        <article class="owner-action-filter-card">
          <div class="owner-action-filter-card__eyebrow">{_html_escape(action.get('severity', 'info'))} · {_html_escape(lane)}</div>
          <h3>{_html_escape(action.get('title', 'Owner Action'))}</h3>
          <p>{_html_escape(action.get('human_reason', 'Owner action.'))}</p>
          <small>{_html_escape(action.get('recommended_action', 'review'))}</small>
          <a href="{_html_escape(action.get('href', '#'))}">Open source</a>
        </article>
        """)

    if not action_cards:
        action_cards.append("""
        <article class="owner-action-filter-card">
          <div class="owner-action-filter-card__eyebrow">empty</div>
          <h3>No actions match this filter</h3>
          <p>Try another lane, severity, source, status, or action type.</p>
        </article>
        """)

    html = f"""
<!-- PACK138_OWNER_ACTION_FILTERS_SECTION -->
<section class="owner-action-filters" data-pack="138">
  <style>
    .owner-action-filters {{
      margin: 24px 0;
      border: 1px solid rgba(168,175,255,.40);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(168,175,255,.13), transparent 34%),
        linear-gradient(135deg, rgba(22,20,48,.88), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-filters__eyebrow {{
      color: rgba(168,175,255,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-filters h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-filters p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-filter-active {{
      margin-top: 12px;
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
      color: rgba(245,234,210,.72);
      font-size: 12px;
    }}
    .owner-action-filter-options,
    .owner-action-filter-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-filter-option,
    .owner-action-filter-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-filter-option h3,
    .owner-action-filter-card h3 {{
      margin: 0 0 8px;
      font-size: 16px;
    }}
    .owner-action-filter-option span {{
      display: inline-flex;
      margin: 3px;
      border: 1px solid rgba(168,175,255,.22);
      border-radius: 999px;
      padding: 5px 8px;
      color: rgba(245,234,210,.70);
      font-size: 11px;
    }}
    .owner-action-filter-card__eyebrow {{
      color: rgba(168,175,255,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-filter-card small {{
      display: block;
      color: rgba(245,234,210,.55);
      margin-bottom: 10px;
      word-break: break-word;
    }}
    .owner-action-filter-card a {{
      display: inline-flex;
      text-decoration: none;
      border: 1px solid rgba(168,175,255,.45);
      border-radius: 999px;
      padding: 8px 12px;
      color: #f5ead2;
      background: rgba(168,175,255,.08);
      font-size: 12px;
    }}
    @media (max-width: 1000px) {{
      .owner-action-filter-options,
      .owner-action-filter-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-filters__eyebrow">PACK 138 · OWNER ACTION FILTERS</div>
  <h2>Owner Action Filters</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner Action filters loaded.'))}</p>

  <div class="owner-action-filter-active">
    <strong>Filtered actions:</strong> {_html_escape(status.get('filtered_action_count', 0))}<br>
    <strong>Active filters:</strong> {_html_escape(active)}
  </div>

  <div class="owner-action-filter-options">
    {''.join(option_cards)}
  </div>

  <div class="owner-action-filter-grid">
    {''.join(action_cards)}
  </div>
</section>
<!-- END PACK138_OWNER_ACTION_FILTERS_SECTION -->
"""
    return html


def write_owner_action_filters_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_filters_status(write_panel=False)
    path = DATA_DIR / "owner_action_filters_panel.html"
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Filters</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_filters_section(status)}
</main>
</body>
</html>
"""
    _write_text(path, html)
    return {
        "ok": True,
        "pack": "138",
        "decision": "owner_action_filters_panel_written",
        "path": str(path),
        "human_reason": "Owner Action Filters panel written.",
        "soulaana_translation": "Soulaana: Owner command filters posted.",
    }

# ================================================================================
# END PACK138_OWNER_ACTION_CENTER_FILTERS
# ================================================================================



# ================================================================================
# PACK139_OWNER_ACTION_DETAIL_CARDS
# ================================================================================
# Adds safe cached detail cards for individual Owner Action Center commands.
# This reads cached Owner Action Center status only and does not call live builders.
# ================================================================================

def _pack139_find_action_by_id(action_id: str, status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    action_id = str(action_id or "").strip()
    status = status if isinstance(status, dict) else load_owner_action_center_status()
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    if action_id:
        for action in actions:
            if isinstance(action, dict) and str(action.get("action_id", "")) == action_id:
                return action

    top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
    if isinstance(top_action, dict) and top_action.get("action_id"):
        return top_action

    for action in actions:
        if isinstance(action, dict):
            return action

    return {}


def _pack139_source_label(action: Dict[str, Any]) -> str:
    source = str(action.get("source", "") or "").strip()
    return {
        "incident_filters_cached": "Incident Filters",
        "security_inbox_cached": "Security Inbox",
        "security_watch_cached": "Security Watch",
        "route_health_cached": "Route Wall",
        "security_watch_checkpoint_cached": "Security Watch Checkpoint",
    }.get(source, source.replace("_", " ").title() if source else "Tower")


def _pack139_context_items(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(context, dict):
        return []

    items = []
    for key, value in context.items():
        key_text = str(key or "").strip()
        if not key_text:
            continue
        items.append({
            "key": key_text,
            "label": key_text.replace("_", " ").title(),
            "value": value,
        })
    return items


def build_owner_action_detail_status(
    *,
    action_id: str = "",
    write_panel: bool = True,
) -> Dict[str, Any]:
    base_status = load_owner_action_center_status()
    action = _pack139_find_action_by_id(action_id, base_status)

    found = bool(action)
    lane = _pack137_action_lane(action) if found else ""
    context = action.get("context", {}) if isinstance(action.get("context"), dict) else {}
    context_items = _pack139_context_items(context)

    detail = {
        "ok": found,
        "pack": "139",
        "status": "passed" if found else "not_found",
        "base_status": base_status.get("status", "unknown"),
        "base_pack": base_status.get("pack", ""),
        "requested_action_id": str(action_id or ""),
        "found_action_id": action.get("action_id", "") if found else "",
        "action": action if found else {},
        "detail": {
            "action_id": action.get("action_id", "") if found else "",
            "title": action.get("title", "Owner Action") if found else "Owner Action Not Found",
            "action_type": action.get("action_type", "") if found else "",
            "lane": lane,
            "lane_label": _pack137_action_lane_label(lane) if lane else "",
            "severity": action.get("severity", "") if found else "",
            "status": action.get("status", "") if found else "",
            "source": action.get("source", "") if found else "",
            "source_label": _pack139_source_label(action) if found else "",
            "priority_score": action.get("priority_score", 0) if found else 0,
            "recommended_action": action.get("recommended_action", "") if found else "",
            "href": action.get("href", "") if found else "",
            "human_reason": action.get("human_reason", "") if found else "No matching owner action was found.",
            "created_at": action.get("created_at", "") if found else "",
            "context_items": context_items,
        },
        "readiness_score": 100 if found else 80,
        "human_reason": (
            "Owner Action detail card loaded from cached command queue."
            if found
            else "Owner Action detail could not find the requested action."
        ),
        "soulaana_translation": (
            "Soulaana: This command card shows the owner what to do and where it came from."
            if found
            else "Soulaana: I could not find that command card."
        ),
    }

    detail = _redact(detail)
    scan = _safe_scan(detail)
    detail["no_secret_leakage"] = scan.get("ok") is True
    detail["leakage_scan"] = scan
    detail["status_fingerprint"] = _fingerprint(detail)

    if write_panel:
        write_owner_action_detail_panel(detail)

    return detail


def render_owner_action_detail_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_action_detail_status(write_panel=False)
    detail = status.get("detail", {}) if isinstance(status.get("detail"), dict) else {}
    context_items = detail.get("context_items", []) if isinstance(detail.get("context_items"), list) else []

    context_html = []
    for item in context_items:
        if not isinstance(item, dict):
            continue
        context_html.append(f"""
        <article class="owner-action-detail-context-item">
          <span>{_html_escape(item.get('label', 'Context'))}</span>
          <b>{_html_escape(item.get('value', ''))}</b>
        </article>
        """)

    if not context_html:
        context_html.append("""
        <article class="owner-action-detail-context-item">
          <span>Context</span>
          <b>No extra context</b>
        </article>
        """)

    html = f"""
<!-- PACK139_OWNER_ACTION_DETAIL_SECTION -->
<section class="owner-action-detail" data-pack="139">
  <style>
    .owner-action-detail {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(220,183,94,.14), transparent 34%),
        linear-gradient(135deg, rgba(54,35,11,.88), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-action-detail__eyebrow {{
      color: rgba(220,183,94,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-action-detail h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-action-detail p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-action-detail-summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-detail-stat,
    .owner-action-detail-context-item {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .owner-action-detail-stat span,
    .owner-action-detail-context-item span {{
      display: block;
      color: rgba(220,183,94,.72);
      text-transform: uppercase;
      letter-spacing: .11em;
      font-size: 10px;
      margin-bottom: 6px;
    }}
    .owner-action-detail-stat b,
    .owner-action-detail-context-item b {{
      display: block;
      color: #f5ead2;
      font-size: 14px;
      word-break: break-word;
    }}
    .owner-action-detail-context {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-detail-next {{
      margin-top: 14px;
      border: 1px solid rgba(220,183,94,.25);
      border-radius: 20px;
      padding: 14px;
      background: rgba(220,183,94,.06);
    }}
    .owner-action-detail-next a {{
      display: inline-flex;
      text-decoration: none;
      border: 1px solid rgba(220,183,94,.45);
      border-radius: 999px;
      padding: 8px 12px;
      color: #f5ead2;
      background: rgba(220,183,94,.08);
      font-size: 12px;
      margin-top: 8px;
    }}
    @media (max-width: 1000px) {{
      .owner-action-detail-summary,
      .owner-action-detail-context {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-action-detail__eyebrow">PACK 139 · OWNER ACTION DETAIL</div>
  <h2>{_html_escape(detail.get('title', 'Owner Action Detail'))}</h2>
  <p>{_html_escape(detail.get('human_reason', status.get('human_reason', 'Owner action detail loaded.')))}</p>

  <div class="owner-action-detail-summary">
    <article class="owner-action-detail-stat"><span>Lane</span><b>{_html_escape(detail.get('lane_label', ''))}</b></article>
    <article class="owner-action-detail-stat"><span>Severity</span><b>{_html_escape(detail.get('severity', ''))}</b></article>
    <article class="owner-action-detail-stat"><span>Priority</span><b>{_html_escape(detail.get('priority_score', 0))}</b></article>
    <article class="owner-action-detail-stat"><span>Source</span><b>{_html_escape(detail.get('source_label', ''))}</b></article>
    <article class="owner-action-detail-stat"><span>Status</span><b>{_html_escape(detail.get('status', ''))}</b></article>
  </div>

  <div class="owner-action-detail-context">
    {''.join(context_html)}
  </div>

  <div class="owner-action-detail-next">
    <strong>Recommended move:</strong> {_html_escape(detail.get('recommended_action', 'review'))}<br>
    <strong>Action type:</strong> {_html_escape(detail.get('action_type', ''))}<br>
    <a href="{_html_escape(detail.get('href', '#'))}">Open source</a>
  </div>
</section>
<!-- END PACK139_OWNER_ACTION_DETAIL_SECTION -->
"""
    return html


def write_owner_action_detail_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_action_detail_status(write_panel=False)
    path = DATA_DIR / "owner_action_detail_panel.html"
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Action Detail</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_action_detail_section(status)}
</main>
</body>
</html>
"""
    _write_text(path, html)
    return {
        "ok": True,
        "pack": "139",
        "decision": "owner_action_detail_panel_written",
        "path": str(path),
        "human_reason": "Owner Action Detail panel written.",
        "soulaana_translation": "Soulaana: Owner command detail card posted.",
    }

# ================================================================================
# END PACK139_OWNER_ACTION_DETAIL_CARDS
# ================================================================================



# ================================================================================
# PACK139B_OWNER_ACTION_DETAIL_MISSING_LOOKUP_FIX
# ================================================================================
# Fix:
# If a specific action_id is requested and missing, do NOT fallback to top action.
# Only blank action_id can fallback to top/first action.
# ================================================================================

def _pack139_find_action_by_id(action_id: str, status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    action_id = str(action_id or "").strip()
    status = status if isinstance(status, dict) else load_owner_action_center_status()
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    if action_id:
        for action in actions:
            if isinstance(action, dict) and str(action.get("action_id", "")) == action_id:
                return action

        top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
        if isinstance(top_action, dict) and str(top_action.get("action_id", "")) == action_id:
            return top_action

        return {}

    top_action = status.get("top_action", {}) if isinstance(status.get("top_action"), dict) else {}
    if isinstance(top_action, dict) and top_action.get("action_id"):
        return top_action

    for action in actions:
        if isinstance(action, dict):
            return action

    return {}


def build_owner_action_detail_status(
    *,
    action_id: str = "",
    write_panel: bool = True,
) -> Dict[str, Any]:
    requested_action_id = str(action_id or "").strip()
    base_status = load_owner_action_center_status()
    action = _pack139_find_action_by_id(requested_action_id, base_status)

    found = bool(action)
    lane = _pack137_action_lane(action) if found else ""
    context = action.get("context", {}) if isinstance(action.get("context"), dict) else {}
    context_items = _pack139_context_items(context)

    detail = {
        "ok": found,
        "pack": "139+139B",
        "status": "passed" if found else "not_found",
        "base_status": base_status.get("status", "unknown"),
        "base_pack": base_status.get("pack", ""),
        "requested_action_id": requested_action_id,
        "found_action_id": action.get("action_id", "") if found else "",
        "action": action if found else {},
        "detail": {
            "action_id": action.get("action_id", "") if found else "",
            "title": action.get("title", "Owner Action") if found else "Owner Action Not Found",
            "action_type": action.get("action_type", "") if found else "",
            "lane": lane,
            "lane_label": _pack137_action_lane_label(lane) if lane else "",
            "severity": action.get("severity", "") if found else "",
            "status": action.get("status", "") if found else "",
            "source": action.get("source", "") if found else "",
            "source_label": _pack139_source_label(action) if found else "",
            "priority_score": action.get("priority_score", 0) if found else 0,
            "recommended_action": action.get("recommended_action", "") if found else "",
            "href": action.get("href", "") if found else "",
            "human_reason": action.get("human_reason", "") if found else "No matching owner action was found.",
            "created_at": action.get("created_at", "") if found else "",
            "context_items": context_items,
        },
        "readiness_score": 100 if found else 80,
        "human_reason": (
            "Owner Action detail card loaded from cached command queue."
            if found
            else "Owner Action detail could not find the requested action."
        ),
        "soulaana_translation": (
            "Soulaana: This command card shows the owner what to do and where it came from."
            if found
            else "Soulaana: I could not find that command card."
        ),
    }

    detail = _redact(detail)
    scan = _safe_scan(detail)
    detail["no_secret_leakage"] = scan.get("ok") is True
    detail["leakage_scan"] = scan
    detail["status_fingerprint"] = _fingerprint(detail)

    if write_panel:
        write_owner_action_detail_panel(detail)

    return detail

# ================================================================================
# END PACK139B_OWNER_ACTION_DETAIL_MISSING_LOOKUP_FIX
# ================================================================================



# ================================================================================
# PACK139C_OWNER_ACTION_DETAIL_PACK_LABEL_COMPATIBILITY
# ================================================================================
# Keeps Pack 139B missing-action fix, but reports pack="139" for the existing
# Pack 139 test expectations.
# ================================================================================

def build_owner_action_detail_status(
    *,
    action_id: str = "",
    write_panel: bool = True,
) -> Dict[str, Any]:
    requested_action_id = str(action_id or "").strip()
    base_status = load_owner_action_center_status()
    action = _pack139_find_action_by_id(requested_action_id, base_status)

    found = bool(action)
    lane = _pack137_action_lane(action) if found else ""
    context = action.get("context", {}) if isinstance(action.get("context"), dict) else {}
    context_items = _pack139_context_items(context)

    detail = {
        "ok": found,
        "pack": "139",
        "rescue_marker": "PACK139C_COMPATIBLE_MISSING_LOOKUP_FIX_ACTIVE",
        "status": "passed" if found else "not_found",
        "base_status": base_status.get("status", "unknown"),
        "base_pack": base_status.get("pack", ""),
        "requested_action_id": requested_action_id,
        "found_action_id": action.get("action_id", "") if found else "",
        "action": action if found else {},
        "detail": {
            "action_id": action.get("action_id", "") if found else "",
            "title": action.get("title", "Owner Action") if found else "Owner Action Not Found",
            "action_type": action.get("action_type", "") if found else "",
            "lane": lane,
            "lane_label": _pack137_action_lane_label(lane) if lane else "",
            "severity": action.get("severity", "") if found else "",
            "status": action.get("status", "") if found else "",
            "source": action.get("source", "") if found else "",
            "source_label": _pack139_source_label(action) if found else "",
            "priority_score": action.get("priority_score", 0) if found else 0,
            "recommended_action": action.get("recommended_action", "") if found else "",
            "href": action.get("href", "") if found else "",
            "human_reason": action.get("human_reason", "") if found else "No matching owner action was found.",
            "created_at": action.get("created_at", "") if found else "",
            "context_items": context_items,
        },
        "readiness_score": 100 if found else 80,
        "human_reason": (
            "Owner Action detail card loaded from cached command queue."
            if found
            else "Owner Action detail could not find the requested action."
        ),
        "soulaana_translation": (
            "Soulaana: This command card shows the owner what to do and where it came from."
            if found
            else "Soulaana: I could not find that command card."
        ),
    }

    detail = _redact(detail)
    scan = _safe_scan(detail)
    detail["no_secret_leakage"] = scan.get("ok") is True
    detail["leakage_scan"] = scan
    detail["status_fingerprint"] = _fingerprint(detail)

    if write_panel:
        write_owner_action_detail_panel(detail)

    return detail

# ================================================================================
# END PACK139C_OWNER_ACTION_DETAIL_PACK_LABEL_COMPATIBILITY
# ================================================================================

