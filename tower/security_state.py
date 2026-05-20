# =============================================================================
# THE TOWER — SECURITY STATE STORE
# FILE: tower/security_state.py
# =============================================================================

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from tower.audit import write_audit_event
from tower.security_events import create_security_event


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
SECURITY_STATE_PATH = TOWER_DATA_DIR / "security_state.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


DEFAULT_SECURITY_STATE = {
    "global_lockdown": False,
    "global_lockdown_reason": None,

    "locked_apps": {},
    "locked_modes": {},
    "locked_actions": {},

    "export_lockdown": False,
    "live_mode_lockdown": True,
    "automated_mode_lockdown": True,
    "broker_bridge_lockdown": True,

    "step_up_required_actions": {
        "export": True,
        "enter_admin": False,
        "change_permissions": True,
        "live_mode_entry": True,
        "broker_connect": True,
        "kill_switch_change": True,
    },

    "updated_at": None,
    "updated_by": None,
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _load_state() -> Dict[str, Any]:
    if not SECURITY_STATE_PATH.exists():
        state = dict(DEFAULT_SECURITY_STATE)
        state["updated_at"] = _now()
        state["updated_by"] = "system"
        _save_state(state)
        return state

    try:
        with SECURITY_STATE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return dict(DEFAULT_SECURITY_STATE)

        merged = dict(DEFAULT_SECURITY_STATE)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_SECURITY_STATE)


def _save_state(state: Dict[str, Any]) -> Dict[str, Any]:
    TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    tmp_path = SECURITY_STATE_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(SECURITY_STATE_PATH)
    return state


def get_security_state() -> Dict[str, Any]:
    """
    Reads The Tower's current security switches.

    Baby version:
    This checks which doors are locked.
    """

    return _load_state()


def update_security_state(
    updates: Dict[str, Any],
    actor_user_id: str = "system",
    reason: str = "security_state_update",
) -> Dict[str, Any]:
    """
    Updates security switches.

    Baby version:
    This flips Tower switches and writes a receipt.
    """

    state = _load_state()
    before = dict(state)

    state.update(updates)
    state["updated_at"] = _now()
    state["updated_by"] = actor_user_id

    saved = _save_state(state)

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=None,
        action="update_security_state",
        app_name="tower_admin",
        object_type="security_state",
        object_id="global",
        result="allow",
        reason_code=reason,
        human_reason="Tower security state was updated.",
        risk_score=80,
        risk_state="restricted",
        metadata={
            "updates": updates,
            "before": before,
            "after": saved,
        },
    )

    create_security_event(
        user_id=actor_user_id,
        event_type="security_state_updated",
        severity="high",
        source_app="tower_admin",
        description="Tower security state was updated.",
        recommended_action="review_security_state_change",
        metadata={
            "reason": reason,
            "updates": updates,
        },
    )

    return saved


def set_global_lockdown(
    enabled: bool,
    actor_user_id: str = "system",
    reason: str = "global_lockdown_update",
) -> Dict[str, Any]:
    return update_security_state(
        updates={
            "global_lockdown": bool(enabled),
            "global_lockdown_reason": reason if enabled else None,
        },
        actor_user_id=actor_user_id,
        reason=reason,
    )


def set_app_lockdown(
    app_name: str,
    enabled: bool,
    actor_user_id: str = "system",
    reason: str = "app_lockdown_update",
) -> Dict[str, Any]:
    state = _load_state()
    locked_apps = dict(state.get("locked_apps") or {})

    if enabled:
        locked_apps[app_name] = {
            "locked": True,
            "reason": reason,
            "updated_at": _now(),
            "updated_by": actor_user_id,
        }
    else:
        locked_apps.pop(app_name, None)

    return update_security_state(
        updates={"locked_apps": locked_apps},
        actor_user_id=actor_user_id,
        reason=reason,
    )


def set_mode_lockdown(
    mode_name: str,
    enabled: bool,
    actor_user_id: str = "system",
    reason: str = "mode_lockdown_update",
) -> Dict[str, Any]:
    state = _load_state()
    locked_modes = dict(state.get("locked_modes") or {})

    if enabled:
        locked_modes[mode_name] = {
            "locked": True,
            "reason": reason,
            "updated_at": _now(),
            "updated_by": actor_user_id,
        }
    else:
        locked_modes.pop(mode_name, None)

    return update_security_state(
        updates={"locked_modes": locked_modes},
        actor_user_id=actor_user_id,
        reason=reason,
    )


def set_action_lockdown(
    action: str,
    enabled: bool,
    actor_user_id: str = "system",
    reason: str = "action_lockdown_update",
) -> Dict[str, Any]:
    state = _load_state()
    locked_actions = dict(state.get("locked_actions") or {})

    if enabled:
        locked_actions[action] = {
            "locked": True,
            "reason": reason,
            "updated_at": _now(),
            "updated_by": actor_user_id,
        }
    else:
        locked_actions.pop(action, None)

    return update_security_state(
        updates={"locked_actions": locked_actions},
        actor_user_id=actor_user_id,
        reason=reason,
    )


def is_app_locked(app_name: str) -> Optional[Dict[str, Any]]:
    state = _load_state()

    if state.get("global_lockdown"):
        return {
            "locked": True,
            "reason_code": "global_lockdown_active",
            "human_reason": "Global Tower lockdown is active.",
            "risk_score": 100,
        }

    locked_apps = state.get("locked_apps") or {}
    lock = locked_apps.get(app_name)

    if lock and lock.get("locked"):
        return {
            "locked": True,
            "reason_code": "app_lockdown_active",
            "human_reason": f"{app_name} is currently locked by The Tower.",
            "risk_score": 95,
            "lock": lock,
        }

    return None


def is_mode_locked(mode_name: Optional[str]) -> Optional[Dict[str, Any]]:
    if not mode_name:
        return None

    state = _load_state()

    locked_modes = state.get("locked_modes") or {}
    lock = locked_modes.get(mode_name)

    if lock and lock.get("locked"):
        return {
            "locked": True,
            "reason_code": "mode_lockdown_active",
            "human_reason": f"{mode_name} is currently locked by The Tower.",
            "risk_score": 95,
            "lock": lock,
        }

    if mode_name in {"live_manual", "live_hybrid", "live_automated", "internal_trust_automated"}:
        if state.get("live_mode_lockdown") and mode_name in {"live_manual", "live_hybrid"}:
            return {
                "locked": True,
                "reason_code": "live_mode_lockdown_active",
                "human_reason": "Live Mode is currently locked by The Tower.",
                "risk_score": 95,
            }

        if state.get("automated_mode_lockdown") and mode_name in {"live_automated", "internal_trust_automated"}:
            return {
                "locked": True,
                "reason_code": "automated_mode_lockdown_active",
                "human_reason": "Automated Mode is currently locked by The Tower.",
                "risk_score": 100,
            }

    return None


def is_action_locked(action: str) -> Optional[Dict[str, Any]]:
    state = _load_state()

    locked_actions = state.get("locked_actions") or {}
    lock = locked_actions.get(action)

    if lock and lock.get("locked"):
        return {
            "locked": True,
            "reason_code": "action_lockdown_active",
            "human_reason": f"The action {action} is currently locked by The Tower.",
            "risk_score": 95,
            "lock": lock,
        }

    if action == "export" and state.get("export_lockdown"):
        return {
            "locked": True,
            "reason_code": "export_lockdown_active",
            "human_reason": "Exports are currently locked by The Tower.",
            "risk_score": 95,
        }

    if action == "broker_connect" and state.get("broker_bridge_lockdown"):
        return {
            "locked": True,
            "reason_code": "broker_bridge_lockdown_active",
            "human_reason": "Broker bridge access is currently locked by The Tower.",
            "risk_score": 100,
        }

    return None


def action_requires_step_up(action: str) -> bool:
    state = _load_state()
    required = state.get("step_up_required_actions") or {}
    return bool(required.get(action) is True)
