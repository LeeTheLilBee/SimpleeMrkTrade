import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

BEHAVIOR_STATE_FILE = Path("/content/SimpleeMrkTrade/data_v2/behavior_state.json")

DEFAULT_BEHAVIOR_STATE = {
    "page_switch_count_30s": 0,
    "symbol_open_count_30s": 0,
    "rapid_jump_score": 0,
    "dwell_score": 100,
    "overload_risk": "low",          # low | medium | high
    "suggest_low_stim": False,
    "suggest_focus_mode": False,
    "last_intervention_at": "",
    "last_page": "",
    "last_symbol": "",
    "last_event_at": "",
}


def _load_json(path: Path, default: Any):
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _normalize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(DEFAULT_BEHAVIOR_STATE)
    if isinstance(state, dict):
        merged.update(state)

    overload_risk = str(merged.get("overload_risk", "low")).strip().lower()
    if overload_risk not in {"low", "medium", "high"}:
        overload_risk = "low"

    merged["page_switch_count_30s"] = int(merged.get("page_switch_count_30s", 0) or 0)
    merged["symbol_open_count_30s"] = int(merged.get("symbol_open_count_30s", 0) or 0)
    merged["rapid_jump_score"] = int(merged.get("rapid_jump_score", 0) or 0)
    merged["dwell_score"] = int(merged.get("dwell_score", 100) or 100)
    merged["overload_risk"] = overload_risk
    merged["suggest_low_stim"] = bool(merged.get("suggest_low_stim", False))
    merged["suggest_focus_mode"] = bool(merged.get("suggest_focus_mode", False))
    merged["last_intervention_at"] = str(merged.get("last_intervention_at", "") or "")
    merged["last_page"] = str(merged.get("last_page", "") or "")
    merged["last_symbol"] = str(merged.get("last_symbol", "") or "")
    merged["last_event_at"] = str(merged.get("last_event_at", "") or "")
    return merged


def load_all_behavior_states() -> Dict[str, Any]:
    payload = _load_json(BEHAVIOR_STATE_FILE, {})
    return payload if isinstance(payload, dict) else {}


def save_all_behavior_states(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        payload = {}
    _save_json(BEHAVIOR_STATE_FILE, payload)


def get_behavior_state(username: str) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    all_states = load_all_behavior_states()

    if username and username in all_states:
        row = _safe_dict(all_states.get(username))
        state = _normalize_state(_safe_dict(row.get("state")))
        return {
            "username": username,
            "state": state,
            "updated_at": row.get("updated_at", ""),
        }

    return {
        "username": username,
        "state": dict(DEFAULT_BEHAVIOR_STATE),
        "updated_at": "",
    }


def set_behavior_state(username: str, state: Dict[str, Any]) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    if not username:
        raise ValueError("username is required")

    all_states = load_all_behavior_states()
    normalized = _normalize_state(state)

    row = {
        "username": username,
        "state": normalized,
        "updated_at": datetime.now().isoformat(),
    }
    all_states[username] = row
    save_all_behavior_states(all_states)
    return row


def update_behavior_state(username: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    current = get_behavior_state(username)
    merged = dict(current.get("state", {}))
    if isinstance(patch, dict):
        merged.update(patch)
    return set_behavior_state(username, merged)


def reset_behavior_state(username: str) -> Dict[str, Any]:
    return set_behavior_state(username, dict(DEFAULT_BEHAVIOR_STATE))
