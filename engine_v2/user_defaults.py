import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

USER_DEFAULTS_FILE = Path("/content/SimpleeMrkTrade/data_v2/user_defaults.json")

DEFAULT_PROFILE = {
    "intelligence_mode": "hybrid",
    "control_mode": "manual",
    "auto_scope": "both",
    "experience_mode": "balanced",
    "motion_profile": "full",
    "sidebar_collapsed": True,
    "preferred_dashboard": "live_command",
    "single_best_play_mode": False,
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

def _normalize_defaults(defaults: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(DEFAULT_PROFILE)
    if isinstance(defaults, dict):
        merged.update(defaults)

    intelligence_mode = str(merged.get("intelligence_mode", "hybrid")).strip().lower()
    if intelligence_mode not in {"equity", "options", "hybrid"}:
        intelligence_mode = "hybrid"

    control_mode = str(merged.get("control_mode", "manual")).strip().lower()
    if control_mode not in {"manual", "assisted", "auto"}:
        control_mode = "manual"

    auto_scope = str(merged.get("auto_scope", "both")).strip().lower()
    if auto_scope not in {"stocks", "options", "both"}:
        auto_scope = "both"

    experience_mode = str(merged.get("experience_mode", "balanced")).strip().lower()
    if experience_mode not in {"balanced", "focus", "low_stim"}:
        experience_mode = "balanced"

    motion_profile = str(merged.get("motion_profile", "full")).strip().lower()
    if motion_profile not in {"full", "reduced", "minimal"}:
        motion_profile = "full"

    merged["intelligence_mode"] = intelligence_mode
    merged["control_mode"] = control_mode
    merged["auto_scope"] = auto_scope
    merged["experience_mode"] = experience_mode
    merged["motion_profile"] = motion_profile
    merged["sidebar_collapsed"] = bool(merged.get("sidebar_collapsed", True))
    merged["single_best_play_mode"] = bool(merged.get("single_best_play_mode", False))
    merged["preferred_dashboard"] = str(merged.get("preferred_dashboard", "live_command")).strip() or "live_command"
    return merged

def load_all_user_defaults() -> Dict[str, Any]:
    payload = _load_json(USER_DEFAULTS_FILE, {})
    return payload if isinstance(payload, dict) else {}

def save_all_user_defaults(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        payload = {}
    _save_json(USER_DEFAULTS_FILE, payload)

def get_user_defaults(username: str) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    all_defaults = load_all_user_defaults()

    if username and username in all_defaults:
        row = all_defaults.get(username, {})
        if isinstance(row, dict):
            defaults = _normalize_defaults(row.get("defaults", {}))
            return {
                "username": username,
                "defaults": defaults,
                "updated_at": row.get("updated_at", ""),
            }

    return {
        "username": username,
        "defaults": dict(DEFAULT_PROFILE),
        "updated_at": "",
    }

def set_user_defaults(username: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    username = str(username or "").strip().lower()
    if not username:
        raise ValueError("username is required")

    all_defaults = load_all_user_defaults()
    normalized = _normalize_defaults(defaults)

    row = {
        "username": username,
        "defaults": normalized,
        "updated_at": datetime.now().isoformat(),
    }
    all_defaults[username] = row
    save_all_user_defaults(all_defaults)
    return row
