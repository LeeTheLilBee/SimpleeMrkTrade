
# =============================================================================
# The Tower — Security Command View Model
# Pack 019
#
# Purpose:
#   Turns the raw Security Command Dashboard JSON into a clean UI/API shape.
#
# This keeps the future admin dashboard simple:
#   - header status
#   - summary metric cards
#   - urgent lanes
#   - owner focus tasks
#   - recommended actions
#   - clean labels/tone/status language
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


TOWER_DIR = Path(__file__).resolve().parent
DATA_DIR = TOWER_DIR / "data"

DASHBOARD_PATH = DATA_DIR / "security_command_dashboard.json"
VIEW_PATH = DATA_DIR / "security_command_dashboard_view.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _tone_rank(tone: str) -> int:
    tone = _as_text(tone).lower().strip()
    ranks = {
        "critical": 5,
        "danger": 5,
        "high": 4,
        "urgent": 4,
        "watch": 3,
        "medium": 2,
        "info": 1,
        "low": 1,
        "clear": 0,
    }
    return ranks.get(tone, 1)


def _priority_rank(priority: str) -> int:
    priority = _as_text(priority).lower().strip()
    ranks = {
        "urgent": 5,
        "critical": 5,
        "high": 4,
        "watch": 3,
        "medium": 2,
        "low": 1,
        "clear": 0,
    }
    return ranks.get(priority, 1)


def _status_label_from_health(health: Dict[str, Any]) -> Dict[str, Any]:
    state = _as_text(health.get("state"), "unknown").strip() or "unknown"
    reason = _as_text(health.get("human_reason"), "Tower health needs review.")

    if state == "clear":
        label = "Clear"
        tone = "clear"
        headline = "The Tower is calm."
    elif state == "attention_required":
        label = "Attention Required"
        tone = "critical"
        headline = "The Tower needs owner review."
    elif state in {"watch", "warning"}:
        label = "Watch"
        tone = "watch"
        headline = "The Tower is watching elevated activity."
    else:
        label = state.replace("_", " ").title()
        tone = "watch"
        headline = "The Tower needs review."

    return {
        "state": state,
        "label": label,
        "tone": tone,
        "headline": headline,
        "human_reason": reason,
    }


def _normalize_summary_card(card: Dict[str, Any]) -> Dict[str, Any]:
    name = _as_text(card.get("card"), "Metric")
    value = _as_int(card.get("value"), 0)
    tone = _as_text(card.get("tone"), "info").lower().strip() or "info"
    human_reason = _as_text(card.get("human_reason"), "")

    return {
        "label": name,
        "value": value,
        "tone": tone,
        "tone_rank": _tone_rank(tone),
        "human_reason": human_reason,
        "display_value": f"{value:,}",
    }


def _make_action_hints(reason_code: str, source_type: str, priority: str) -> List[Dict[str, str]]:
    reason_code = _as_text(reason_code).lower().strip()
    source_type = _as_text(source_type).lower().strip()
    priority = _as_text(priority).lower().strip()

    actions: List[Dict[str, str]] = []

    if "live_automated" in reason_code or "automated_mode" in reason_code:
        actions.extend([
            {
                "action": "keep_locked",
                "label": "Keep Locked",
                "tone": "critical",
                "human_reason": "Do not unlock Live Automated for public/beta users without legal, owner, and Control Tower clearance.",
            },
            {
                "action": "review_evidence",
                "label": "Review Evidence",
                "tone": "high",
                "human_reason": "Open the related audit trail before deciding anything.",
            },
        ])
    elif "session_risk_quarantine" in reason_code:
        actions.extend([
            {
                "action": "quarantine_user",
                "label": "Quarantine User",
                "tone": "critical",
                "human_reason": "Pause access until the risky session is reviewed.",
            },
            {
                "action": "require_step_up",
                "label": "Require Step-Up",
                "tone": "high",
                "human_reason": "Force fresh authorization before the user continues.",
            },
        ])
    elif "session_risk_high" in reason_code:
        actions.extend([
            {
                "action": "require_step_up",
                "label": "Require Step-Up",
                "tone": "high",
                "human_reason": "The session is not fully trusted.",
            },
            {
                "action": "monitor",
                "label": "Monitor",
                "tone": "watch",
                "human_reason": "Keep watching before escalating further.",
            },
        ])
    elif "admin_role_required" in reason_code:
        actions.extend([
            {
                "action": "confirm_block",
                "label": "Confirm Block",
                "tone": "high",
                "human_reason": "Verify the non-admin was blocked correctly.",
            },
            {
                "action": "resolve_or_keep_evidence",
                "label": "Resolve or Keep Evidence",
                "tone": "watch",
                "human_reason": "Keep as proof or resolve if it was only a test.",
            },
        ])
    elif "export_step_up" in reason_code:
        actions.extend([
            {
                "action": "review_export",
                "label": "Review Export",
                "tone": "high",
                "human_reason": "Check the export request and redaction behavior.",
            },
            {
                "action": "expire_stale_stepups",
                "label": "Expire Stale Step-Ups",
                "tone": "watch",
                "human_reason": "Clean old pending challenges if they are stale.",
            },
        ])
    elif "global_lockdown" in reason_code:
        actions.extend([
            {
                "action": "confirm_lockdown_state",
                "label": "Confirm Lockdown State",
                "tone": "critical",
                "human_reason": "Decide whether this is test noise or a real emergency state.",
            },
            {
                "action": "review_security_state",
                "label": "Review Security State",
                "tone": "high",
                "human_reason": "Check The Tower security-state record before clearing anything.",
            },
        ])

    if not actions:
        if priority in {"urgent", "critical"}:
            actions.append({
                "action": "owner_review",
                "label": "Owner Review",
                "tone": "critical",
                "human_reason": "This item needs owner attention.",
            })
        elif source_type == "evidence_capsule":
            actions.append({
                "action": "review_evidence",
                "label": "Review Evidence",
                "tone": "watch",
                "human_reason": "Open the evidence capsule and decide whether it should remain open.",
            })
        else:
            actions.append({
                "action": "review",
                "label": "Review",
                "tone": "watch",
                "human_reason": "Review and decide whether to resolve, dismiss, or escalate.",
            })

    return actions


def _normalize_group(group: Dict[str, Any], include_items: bool = False) -> Dict[str, Any]:
    reason_code = _as_text(group.get("reason_code"), "unknown")
    source_type = _as_text(group.get("source_type"), "unknown")
    app_name = _as_text(group.get("app_name"), "unknown")
    priority = _as_text(group.get("priority"), "watch")
    open_count = _as_int(group.get("open_count"), 0)
    priority_score = _as_int(group.get("priority_score"), 0)
    summary = _as_text(group.get("summary"), "Needs review.")
    group_key = _as_text(group.get("group_key"), "")

    normalized = {
        "group_key": group_key,
        "app_name": app_name,
        "source_type": source_type,
        "reason_code": reason_code,
        "priority": priority,
        "priority_rank": _priority_rank(priority),
        "priority_score": priority_score,
        "open_count": open_count,
        "summary": summary,
        "sample_item_ids": group.get("sample_item_ids", []) if isinstance(group.get("sample_item_ids"), list) else [],
        "action_hints": _make_action_hints(reason_code, source_type, priority),
    }

    if include_items:
        items = group.get("items", [])
        normalized["items"] = items if isinstance(items, list) else []

    return normalized


def _normalize_owner_focus(task: Dict[str, Any]) -> Dict[str, Any]:
    reason_code = _as_text(task.get("reason_code"), "unknown")
    priority = _as_text(task.get("priority"), "watch")
    app_name = _as_text(task.get("app_name"), "unknown")
    human_task = _as_text(task.get("human_task"), "Review this issue.")
    open_count = _as_int(task.get("open_count"), 0)
    group_key = _as_text(task.get("group_key"), "")

    return {
        "group_key": group_key,
        "app_name": app_name,
        "reason_code": reason_code,
        "priority": priority,
        "priority_rank": _priority_rank(priority),
        "open_count": open_count,
        "human_task": human_task,
        "action_hints": _make_action_hints(reason_code, "owner_focus", priority),
    }


def _build_lanes(groups: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    lanes = {
        "urgent": [],
        "high": [],
        "watch": [],
        "other": [],
    }

    for group in groups:
        priority = _as_text(group.get("priority"), "other").lower().strip()
        if priority in {"urgent", "critical"}:
            lanes["urgent"].append(group)
        elif priority == "high":
            lanes["high"].append(group)
        elif priority in {"watch", "medium"}:
            lanes["watch"].append(group)
        else:
            lanes["other"].append(group)

    for key in lanes:
        lanes[key] = sorted(
            lanes[key],
            key=lambda g: (_as_int(g.get("priority_score"), 0), _as_int(g.get("open_count"), 0)),
            reverse=True,
        )

    return lanes


def build_security_command_view(
    dashboard: Optional[Dict[str, Any]] = None,
    include_raw_groups: bool = False,
) -> Dict[str, Any]:
    if dashboard is None:
        dashboard = _safe_read_json(DASHBOARD_PATH, {})

    if not isinstance(dashboard, dict):
        dashboard = {}

    health = dashboard.get("health", {})
    if not isinstance(health, dict):
        health = {}

    summary_cards_raw = dashboard.get("summary_cards", [])
    if not isinstance(summary_cards_raw, list):
        summary_cards_raw = []

    top_groups_raw = dashboard.get("top_review_groups", [])
    if not isinstance(top_groups_raw, list):
        top_groups_raw = []

    owner_focus_raw = dashboard.get("recommended_owner_focus", [])
    if not isinstance(owner_focus_raw, list):
        owner_focus_raw = []

    summary_cards = [_normalize_summary_card(card) for card in summary_cards_raw if isinstance(card, dict)]
    top_groups = [_normalize_group(group, include_items=include_raw_groups) for group in top_groups_raw if isinstance(group, dict)]
    owner_focus = [_normalize_owner_focus(task) for task in owner_focus_raw if isinstance(task, dict)]

    top_groups = sorted(
        top_groups,
        key=lambda g: (_as_int(g.get("priority_score"), 0), _as_int(g.get("open_count"), 0)),
        reverse=True,
    )

    owner_focus = sorted(
        owner_focus,
        key=lambda g: (g.get("priority_rank", 0), g.get("open_count", 0)),
        reverse=True,
    )

    status = _status_label_from_health(health)
    lanes = _build_lanes(top_groups)

    open_inbox = 0
    critical_alerts = 0
    high_alerts = 0
    evidence_open = 0
    step_up_pending = 0
    review_groups = 0

    for card in summary_cards:
        label = _as_text(card.get("label")).lower()
        value = _as_int(card.get("value"), 0)
        if "open inbox" in label:
            open_inbox = value
        elif "critical" in label:
            critical_alerts = value
        elif "high" in label:
            high_alerts = value
        elif "evidence" in label:
            evidence_open = value
        elif "step" in label:
            step_up_pending = value
        elif "review" in label:
            review_groups = value

    view = {
        "view_name": "The Tower Security Command View",
        "dashboard_name": _as_text(dashboard.get("dashboard_name"), "The Tower Security Command Dashboard"),
        "generated_at": _utc_now(),
        "source_generated_at": dashboard.get("generated_at"),
        "status": status,
        "hero": {
            "title": "The Tower",
            "subtitle": "Security Command Dashboard",
            "state_label": status["label"],
            "headline": status["headline"],
            "human_reason": status["human_reason"],
            "tone": status["tone"],
        },
        "metrics": {
            "open_inbox": open_inbox,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
            "evidence_open": evidence_open,
            "step_up_pending": step_up_pending,
            "review_groups": review_groups,
        },
        "summary_cards": summary_cards,
        "lanes": lanes,
        "top_review_groups": top_groups,
        "recommended_owner_focus": owner_focus,
        "primary_owner_tasks": owner_focus[:5],
        "api_shape_version": "security_command_view_v0.1.0",
    }

    return view


def save_security_command_view(
    dashboard: Optional[Dict[str, Any]] = None,
    path: Optional[Path] = None,
    include_raw_groups: bool = False,
) -> Dict[str, Any]:
    view = build_security_command_view(dashboard=dashboard, include_raw_groups=include_raw_groups)
    output_path = path or VIEW_PATH
    _safe_write_json(output_path, view)

    return {
        "ok": True,
        "status": "saved",
        "path": str(output_path),
        "view_name": view.get("view_name"),
        "state": view.get("status", {}).get("state"),
        "open_inbox": view.get("metrics", {}).get("open_inbox"),
        "critical_alerts": view.get("metrics", {}).get("critical_alerts"),
        "primary_owner_tasks": len(view.get("primary_owner_tasks", [])),
    }


def load_security_command_view() -> Dict[str, Any]:
    return _safe_read_json(VIEW_PATH, {})


def get_security_command_cards_api() -> Dict[str, Any]:
    view = load_security_command_view()
    if not view:
        view = build_security_command_view()
    return {
        "view_name": view.get("view_name"),
        "generated_at": view.get("generated_at"),
        "hero": view.get("hero", {}),
        "metrics": view.get("metrics", {}),
        "summary_cards": view.get("summary_cards", []),
        "primary_owner_tasks": view.get("primary_owner_tasks", []),
        "lanes": view.get("lanes", {}),
        "api_shape_version": view.get("api_shape_version"),
    }
