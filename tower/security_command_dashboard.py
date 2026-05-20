
# =============================================================================
# THE TOWER - SECURITY COMMAND DASHBOARD
# Pack 018
# =============================================================================

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


TOWER_DIR = Path(__file__).resolve().parent
DATA_DIR = TOWER_DIR / "data"


SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
    "urgent": 4,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return default


def _safe_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def _as_list(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        for key in ("items", "events", "records", "capsules", "exports", "actions", "users", "challenges"):
            value = data.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def _load_possible_json(names: List[str], default: Any) -> Any:
    for name in names:
        path = DATA_DIR / name
        if path.exists():
            return _safe_read_json(path, default)
    return default


def _count_by(items: List[Dict[str, Any]], key: str, fallback: str = "unknown") -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in items:
        value = item.get(key, fallback)
        if value is None or value == "":
            value = fallback
        value = str(value)
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def _severity_of(item: Dict[str, Any]) -> str:
    severity = item.get("severity")
    if not severity and isinstance(item.get("decision"), dict):
        severity = item["decision"].get("risk_state")
    if not severity:
        severity = item.get("risk_state")
    severity = str(severity or "medium").lower()
    if severity in ("locked", "restricted", "quarantined", "critical_admin_action"):
        return "critical"
    if severity in ("step_up_required", "sensitive_admin_action", "watch"):
        return "high"
    if severity not in SEVERITY_RANK:
        return "medium"
    return severity


def _status_of(item: Dict[str, Any]) -> str:
    return str(item.get("status") or "open").lower()


def _priority_score(item: Dict[str, Any]) -> int:
    severity = _severity_of(item)
    base = SEVERITY_RANK.get(severity, 2) * 100

    reason = str(item.get("reason_code") or item.get("event_type") or "").lower()
    recommended = str(item.get("recommended_action") or "").lower()
    source_type = str(item.get("source_type") or "").lower()

    bonus = 0
    if "quarantine" in reason or "quarantine" in recommended:
        bonus += 35
    if "live_automated" in reason or "automated" in reason:
        bonus += 30
    if "lockdown" in reason:
        bonus += 30
    if "admin_role_required" in reason:
        bonus += 25
    if "step_up" in reason or "step_up" in recommended:
        bonus += 20
    if source_type == "evidence_capsule":
        bonus += 10
    if source_type == "admin_action":
        bonus += 10

    status = _status_of(item)
    if status in ("resolved", "dismissed", "closed"):
        bonus -= 200

    return max(0, base + bonus)


def load_inbox_items() -> List[Dict[str, Any]]:
    data = _load_possible_json(
        [
            "security_inbox.json",
            "security_inbox_items.json",
            "inbox.json",
        ],
        [],
    )
    return _as_list(data)


def load_security_events() -> List[Dict[str, Any]]:
    data = _load_possible_json(
        [
            "security_events.json",
            "events.json",
            "security_event_log.json",
        ],
        [],
    )
    return _as_list(data)


def load_evidence_capsules() -> List[Dict[str, Any]]:
    data = _load_possible_json(
        [
            "evidence_capsules.json",
            "capsules.json",
        ],
        [],
    )
    return _as_list(data)


def load_step_up_challenges() -> List[Dict[str, Any]]:
    data = _load_possible_json(
        [
            "step_up_challenges.json",
            "step_up.json",
            "challenges.json",
        ],
        [],
    )
    return _as_list(data)


def load_admin_actions() -> List[Dict[str, Any]]:
    data = _load_possible_json(
        [
            "admin_actions.json",
            "admin_action_log.json",
        ],
        [],
    )
    return _as_list(data)


def _group_inbox(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[str, Dict[str, Any]] = {}

    for item in items:
        status = _status_of(item)
        if status in ("resolved", "dismissed", "closed"):
            continue

        source_type = str(item.get("source_type") or "unknown")
        app_name = str(item.get("app_name") or item.get("source_app") or "unknown")
        user_id = str(item.get("user_id") or "unknown")
        reason_code = str(item.get("reason_code") or item.get("event_type") or "unknown")

        group_key = item.get("group_key") or f"{source_type}:{app_name}:{user_id}:{reason_code}"

        severity = _severity_of(item)
        rank = SEVERITY_RANK.get(severity, 2)
        priority_score = _priority_score(item)

        if group_key not in groups:
            groups[group_key] = {
                "group_key": group_key,
                "source_type": source_type,
                "app_name": app_name,
                "user_id": user_id,
                "reason_code": reason_code,
                "title": item.get("title") or f"{source_type}: {reason_code}",
                "summary": item.get("summary") or item.get("description") or reason_code,
                "recommended_action": item.get("recommended_action"),
                "highest_severity": severity,
                "highest_severity_rank": rank,
                "priority_score": priority_score,
                "open_count": 0,
                "items": [],
                "sample_item_ids": [],
                "first_seen_at": item.get("created_at") or item.get("timestamp"),
                "last_seen_at": item.get("updated_at") or item.get("created_at") or item.get("timestamp"),
            }

        group = groups[group_key]
        group["open_count"] += 1
        group["items"].append(item)

        item_id = item.get("inbox_item_id") or item.get("id") or item.get("source_id")
        if item_id and len(group["sample_item_ids"]) < 5:
            group["sample_item_ids"].append(item_id)

        if rank > group["highest_severity_rank"]:
            group["highest_severity"] = severity
            group["highest_severity_rank"] = rank

        if priority_score > group["priority_score"]:
            group["priority_score"] = priority_score

        seen = item.get("updated_at") or item.get("created_at") or item.get("timestamp")
        if seen:
            group["last_seen_at"] = seen

    out = list(groups.values())

    for group in out:
        score = int(group.get("priority_score", 0))
        if score >= 400:
            group["priority"] = "urgent"
        elif score >= 300:
            group["priority"] = "high"
        elif score >= 200:
            group["priority"] = "medium"
        else:
            group["priority"] = "low"

        # Keep dashboard payload light.
        group["items"] = group["items"][:3]

    return sorted(out, key=lambda g: (-int(g.get("priority_score", 0)), -int(g.get("open_count", 0)), str(g.get("group_key"))))


def build_security_command_dashboard(limit_groups: int = 12) -> Dict[str, Any]:
    inbox_items = load_inbox_items()
    security_events = load_security_events()
    evidence_capsules = load_evidence_capsules()
    step_up_challenges = load_step_up_challenges()
    admin_actions = load_admin_actions()

    open_inbox = [x for x in inbox_items if _status_of(x) not in ("resolved", "dismissed", "closed")]
    resolved_inbox = [x for x in inbox_items if _status_of(x) == "resolved"]
    dismissed_inbox = [x for x in inbox_items if _status_of(x) == "dismissed"]

    groups = _group_inbox(inbox_items)

    critical_open = [x for x in open_inbox if _severity_of(x) == "critical"]
    high_open = [x for x in open_inbox if _severity_of(x) == "high"]

    pending_stepups = [x for x in step_up_challenges if _status_of(x) == "pending"]
    open_capsules = [x for x in evidence_capsules if _status_of(x) == "open"]

    dashboard = {
        "dashboard_name": "The Tower Security Command Dashboard",
        "control_identity": "control_tower_security_command_center",
        "generated_at": _now_iso(),
        "health": {
            "state": "clear" if not critical_open else "attention_required",
            "human_reason": (
                "No critical open inbox items detected."
                if not critical_open
                else "Critical open inbox items require owner review."
            ),
        },
        "summary_cards": [
            {
                "card": "Open Inbox",
                "value": len(open_inbox),
                "tone": "critical" if critical_open else "watch",
                "human_reason": "Open Tower review items waiting for action.",
            },
            {
                "card": "Critical Alerts",
                "value": len(critical_open),
                "tone": "critical" if critical_open else "clear",
                "human_reason": "Items that may involve lockdowns, quarantine, live automation, or restricted access.",
            },
            {
                "card": "High Alerts",
                "value": len(high_open),
                "tone": "high" if high_open else "clear",
                "human_reason": "Items that likely need owner/admin review soon.",
            },
            {
                "card": "Evidence Capsules",
                "value": len(open_capsules),
                "tone": "watch" if open_capsules else "clear",
                "human_reason": "Open evidence records for review or audit trail.",
            },
            {
                "card": "Pending Step-Ups",
                "value": len(pending_stepups),
                "tone": "high" if pending_stepups else "clear",
                "human_reason": "Authorization challenges waiting to be completed, used, expired, or cleaned up.",
            },
            {
                "card": "Review Groups",
                "value": len(groups),
                "tone": "watch" if groups else "clear",
                "human_reason": "Grouped issues so admin screens do not drown in duplicate events.",
            },
        ],
        "inbox": {
            "total": len(inbox_items),
            "open": len(open_inbox),
            "resolved": len(resolved_inbox),
            "dismissed": len(dismissed_inbox),
            "by_status": _count_by(inbox_items, "status", "open"),
            "by_app": _count_by(inbox_items, "app_name", "unknown"),
            "by_source_type": _count_by(inbox_items, "source_type", "unknown"),
            "by_reason_code": _count_by(inbox_items, "reason_code", "unknown"),
        },
        "security_events": {
            "total": len(security_events),
            "open": len([x for x in security_events if _status_of(x) == "open"]),
            "by_app": _count_by(security_events, "source_app", "unknown"),
            "by_event_type": _count_by(security_events, "event_type", "unknown"),
            "by_severity": _count_by(security_events, "severity", "medium"),
        },
        "evidence_capsules": {
            "total": len(evidence_capsules),
            "open": len(open_capsules),
            "by_status": _count_by(evidence_capsules, "status", "open"),
            "by_trigger": _count_by(evidence_capsules, "trigger", "unknown"),
        },
        "step_up": {
            "total": len(step_up_challenges),
            "pending": len(pending_stepups),
            "by_status": _count_by(step_up_challenges, "status", "unknown"),
            "by_action": _count_by(step_up_challenges, "action", "unknown"),
        },
        "admin_actions": {
            "total": len(admin_actions),
            "by_status": _count_by(admin_actions, "status", "unknown"),
            "by_action": _count_by(admin_actions, "admin_action", "unknown"),
            "by_actor": _count_by(admin_actions, "actor_user_id", "unknown"),
        },
        "top_review_groups": groups[:limit_groups],
        "recommended_owner_focus": _build_owner_focus(groups),
    }

    return dashboard


def _build_owner_focus(groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    focus = []

    for group in groups[:8]:
        reason = str(group.get("reason_code") or "")
        priority = group.get("priority")
        action = group.get("recommended_action") or "review_required"

        focus.append(
            {
                "priority": priority,
                "reason_code": reason,
                "app_name": group.get("app_name"),
                "open_count": group.get("open_count"),
                "human_task": _human_task_for_reason(reason, action),
                "group_key": group.get("group_key"),
            }
        )

    return focus


def _human_task_for_reason(reason_code: str, recommended_action: str) -> str:
    reason = reason_code.lower()

    if "quarantine" in reason:
        return "Review risky session, decide whether to quarantine user/session, and require fresh step-up."
    if "live_automated" in reason or "automated" in reason:
        return "Keep Live Automated locked unless this is an internal owner/trust-approved account with legal/compliance clearance."
    if "global_lockdown" in reason:
        return "Confirm whether global lockdown is test noise or a real emergency state."
    if "lockdown" in reason:
        return "Review lock state and decide whether to keep lock, unlock, or archive test noise."
    if "admin_role_required" in reason:
        return "Confirm non-admin was blocked correctly; keep as evidence or dismiss as completed test proof."
    if "step_up" in reason:
        return "Review pending step-up, approve only if actor and action are valid."
    if "export" in reason:
        return "Review export request and require step-up before allowing sensitive data movement."

    return recommended_action or "Review item and choose resolve, dismiss, escalate, or require step-up."


def save_security_command_dashboard(path: Optional[str] = None, limit_groups: int = 12) -> Dict[str, Any]:
    dashboard = build_security_command_dashboard(limit_groups=limit_groups)
    output_path = Path(path) if path else DATA_DIR / "security_command_dashboard.json"
    _safe_write_json(output_path, dashboard)
    return {
        "ok": True,
        "status": "saved",
        "path": str(output_path),
        "dashboard": dashboard,
    }


def get_security_command_cards(limit_groups: int = 8) -> Dict[str, Any]:
    dashboard = build_security_command_dashboard(limit_groups=limit_groups)
    return {
        "dashboard_name": dashboard["dashboard_name"],
        "generated_at": dashboard["generated_at"],
        "health": dashboard["health"],
        "summary_cards": dashboard["summary_cards"],
        "recommended_owner_focus": dashboard["recommended_owner_focus"],
        "top_review_groups": dashboard["top_review_groups"][:limit_groups],
    }


if __name__ == "__main__":
    result = save_security_command_dashboard()
    print(json.dumps(result, indent=2, sort_keys=True))
