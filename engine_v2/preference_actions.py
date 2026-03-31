from typing import Dict, Any

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.experience_presets import get_experience_preset
from engine_v2.user_defaults import get_user_defaults, set_user_defaults
from engine_v2.ui_state import get_ui_state, set_ui_state
from engine_v2.behavior_state import update_behavior_state

PREFERENCE_ACTION_LOG = "/content/SimpleeMrkTrade/data_v2/preference_action_log.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _load_action_log() -> Dict[str, Any]:
    payload = _load_json(PREFERENCE_ACTION_LOG, {})
    return payload if isinstance(payload, dict) else {}


def _save_action_log(payload: Dict[str, Any]) -> None:
    _save_json(PREFERENCE_ACTION_LOG, payload)


def _append_action_log(username: str, action_type: str, payload: Dict[str, Any]) -> None:
    username = str(username or "").strip().lower()
    log = _load_action_log()

    items = log.get("items", [])
    if not isinstance(items, list):
        items = []

    items.append({
        "username": username,
        "action_type": action_type,
        "payload": payload,
        "timestamp": now_iso(),
    })

    log["items"] = items[-200:]
    log["meta"] = {
        "updated_at": now_iso(),
        "count": len(log["items"]),
    }
    _save_action_log(log)


def apply_experience_preset(username: str, preset_key: str) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    preset = get_experience_preset(preset_key)
    settings = _safe_dict(preset.get("settings"))

    if not username:
        raise ValueError("username is required")

    current_defaults = get_user_defaults(username)
    defaults = _safe_dict(current_defaults.get("defaults"))

    defaults_patch = {
        "experience_mode": settings.get("experience_mode", defaults.get("experience_mode", "balanced")),
        "motion_profile": settings.get("motion_profile", defaults.get("motion_profile", "full")),
        "sidebar_collapsed": settings.get("sidebar_collapsed", defaults.get("sidebar_collapsed", True)),
    }

    updated_defaults = dict(defaults)
    updated_defaults.update(defaults_patch)
    set_user_defaults(username, updated_defaults)

    current_ui = get_ui_state(username)
    ui_current = _safe_dict(current_ui.get("current"))

    ui_patch = {
        "experience_mode": settings.get("experience_mode", ui_current.get("experience_mode", "balanced")),
        "motion_profile": settings.get("motion_profile", ui_current.get("motion_profile", "full")),
        "sidebar_expanded": not bool(settings.get("sidebar_collapsed", False)),
        "map_layer": "pressure",
    }

    updated_ui = dict(ui_current)
    updated_ui.update(ui_patch)
    set_ui_state(username, updated_ui)

    update_behavior_state(username, {
        "last_intervention_at": now_iso(),
    })

    result = {
        "username": username,
        "applied_preset": preset.get("key", preset_key),
        "label": preset.get("label", preset_key),
        "defaults_patch": defaults_patch,
        "ui_patch": ui_patch,
        "timestamp": now_iso(),
    }

    _append_action_log(username, "apply_experience_preset", result)
    return result


def apply_intervention_action(username: str, action_id: str) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    action_id = str(action_id or "").strip().lower()

    if action_id == "enter_low_stim_mode":
        result = apply_experience_preset(username, "low_stim")
    elif action_id == "enter_focus_mode":
        result = apply_experience_preset(username, "focus")
    elif action_id in {"keep_balanced_mode", "keep_exploring"}:
        result = apply_experience_preset(username, "balanced")
    else:
        result = {
            "username": username,
            "applied_preset": None,
            "label": "No change",
            "timestamp": now_iso(),
            "note": f"Unknown action_id: {action_id}",
        }

    _append_action_log(username, "apply_intervention_action", {
        "action_id": action_id,
        "result": result,
    })
    return result


def load_preference_action_log() -> Dict[str, Any]:
    return _load_action_log()
