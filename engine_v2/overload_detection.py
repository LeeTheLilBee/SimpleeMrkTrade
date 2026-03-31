from datetime import datetime
from typing import Dict, Any

from engine_v2.behavior_state import get_behavior_state, update_behavior_state
from engine_v2.intervention_queue import add_intervention_item, active_interventions


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _score_overload(page_switch_count_30s: int, symbol_open_count_30s: int, dwell_score: int) -> Dict[str, Any]:
    page_switch_count_30s = _safe_int(page_switch_count_30s, 0)
    symbol_open_count_30s = _safe_int(symbol_open_count_30s, 0)
    dwell_score = _safe_int(dwell_score, 100)

    rapid_jump_score = (page_switch_count_30s * 9) + (symbol_open_count_30s * 7)

    if dwell_score <= 20:
        rapid_jump_score += 25
    elif dwell_score <= 40:
        rapid_jump_score += 15
    elif dwell_score <= 60:
        rapid_jump_score += 8

    rapid_jump_score = max(0, min(100, rapid_jump_score))

    if rapid_jump_score >= 70:
        overload_risk = "high"
    elif rapid_jump_score >= 40:
        overload_risk = "medium"
    else:
        overload_risk = "low"

    suggest_focus_mode = overload_risk in {"medium", "high"}
    suggest_low_stim = overload_risk == "high"

    return {
        "rapid_jump_score": rapid_jump_score,
        "overload_risk": overload_risk,
        "suggest_focus_mode": suggest_focus_mode,
        "suggest_low_stim": suggest_low_stim,
    }


def evaluate_overload(username: str) -> Dict[str, Any]:
    current = get_behavior_state(username)
    state = current.get("state", {}) or {}

    result = _score_overload(
        page_switch_count_30s=state.get("page_switch_count_30s", 0),
        symbol_open_count_30s=state.get("symbol_open_count_30s", 0),
        dwell_score=state.get("dwell_score", 100),
    )

    update_behavior_state(username, {
        "rapid_jump_score": result["rapid_jump_score"],
        "overload_risk": result["overload_risk"],
        "suggest_focus_mode": result["suggest_focus_mode"],
        "suggest_low_stim": result["suggest_low_stim"],
        "last_event_at": datetime.now().isoformat(),
    })

    return result


def queue_overload_interventions(username: str) -> Dict[str, Any]:
    result = evaluate_overload(username)
    existing = active_interventions(username)
    existing_types = {str(item.get("type", "")).strip() for item in existing}

    queued = []

    if result["suggest_low_stim"] and "low_stim_suggestion" not in existing_types:
        queued.append(add_intervention_item(username, {
            "type": "low_stim_suggestion",
            "headline": "Want to simplify the view for a second?",
            "body": "You’ve been moving quickly across the system. Low Stim Mode can soften visuals and reduce motion.",
            "actions": [
                {"id": "enter_low_stim_mode", "label": "Enter Low Stim Mode"},
                {"id": "enter_focus_mode", "label": "Enter Focus Mode"},
                {"id": "keep_exploring", "label": "Keep Exploring"},
            ],
            "priority": "high",
            "created_at": datetime.now().isoformat(),
        }))

    elif result["suggest_focus_mode"] and "focus_mode_suggestion" not in existing_types:
        queued.append(add_intervention_item(username, {
            "type": "focus_mode_suggestion",
            "headline": "Want a cleaner view?",
            "body": "Focus Mode can dim the noise and highlight the strongest opportunities.",
            "actions": [
                {"id": "enter_focus_mode", "label": "Enter Focus Mode"},
                {"id": "keep_balanced_mode", "label": "Stay in Current Mode"},
            ],
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
        }))

    return {
        "evaluation": result,
        "queued_count": len(queued),
        "active_types": [str(item.get("type", "")).strip() for item in active_interventions(username)],
    }


def record_navigation_activity(
    username: str,
    page_switch_increment: int = 0,
    symbol_open_increment: int = 0,
    dwell_score: int | None = None,
    last_page: str = "",
    last_symbol: str = "",
) -> Dict[str, Any]:
    current = get_behavior_state(username)
    state = current.get("state", {}) or {}

    new_page_switch_count = _safe_int(state.get("page_switch_count_30s", 0), 0) + _safe_int(page_switch_increment, 0)
    new_symbol_open_count = _safe_int(state.get("symbol_open_count_30s", 0), 0) + _safe_int(symbol_open_increment, 0)

    patch = {
        "page_switch_count_30s": new_page_switch_count,
        "symbol_open_count_30s": new_symbol_open_count,
        "last_event_at": datetime.now().isoformat(),
    }

    if dwell_score is not None:
        patch["dwell_score"] = _safe_int(dwell_score, 100)
    if last_page:
        patch["last_page"] = str(last_page)
    if last_symbol:
        patch["last_symbol"] = str(last_symbol)

    update_behavior_state(username, patch)
    return queue_overload_interventions(username)
