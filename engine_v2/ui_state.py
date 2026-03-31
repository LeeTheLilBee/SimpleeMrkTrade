import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

from engine_v2.user_defaults import get_user_defaults

UI_STATE_FILE = Path("/content/SimpleeMrkTrade/data_v2/ui_state.json")

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

def load_ui_state() -> Dict[str, Any]:
    payload = _load_json(UI_STATE_FILE, {})
    return payload if isinstance(payload, dict) else {}

def save_ui_state(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        payload = {}
    _save_json(UI_STATE_FILE, payload)

def get_ui_state(username: str) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    payload = load_ui_state()
    users = payload.get("users", {})
    if isinstance(users, dict) and username in users and isinstance(users[username], dict):
        return users[username]

    defaults = get_user_defaults(username).get("defaults", {})
    return {
        "username": username,
        "current": {
            "intelligence_mode": defaults.get("intelligence_mode", "hybrid"),
            "control_mode": defaults.get("control_mode", "manual"),
            "auto_scope": defaults.get("auto_scope", "both"),
            "experience_mode": defaults.get("experience_mode", "balanced"),
            "motion_profile": defaults.get("motion_profile", "full"),
            "sidebar_expanded": not bool(defaults.get("sidebar_collapsed", True)),
            "focus_symbol": None,
            "map_layer": "pressure",
        },
        "updated_at": "",
    }

def set_ui_state(username: str, current: Dict[str, Any]) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    if not username:
        raise ValueError("username is required")

    payload = load_ui_state()
    users = payload.get("users", {})
    if not isinstance(users, dict):
        users = {}

    row = {
        "username": username,
        "current": current if isinstance(current, dict) else {},
        "updated_at": datetime.now().isoformat(),
    }
    users[username] = row
    payload["users"] = users
    save_ui_state(payload)
    return row

def update_ui_state(username: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    current_row = get_ui_state(username)
    current = dict(current_row.get("current", {}))
    if isinstance(patch, dict):
        current.update(patch)
    return set_ui_state(username, current)
