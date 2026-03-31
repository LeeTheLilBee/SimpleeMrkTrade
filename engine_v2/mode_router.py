from typing import Dict, Any

from engine_v2.user_defaults import get_user_defaults
from engine_v2.ui_state import get_ui_state


def resolve_user_modes(username: str) -> Dict[str, Any]:
    defaults = get_user_defaults(username)
    ui = get_ui_state(username)

    d = defaults.get("defaults", {})
    u = ui.get("current", {})

    intelligence_mode = u.get("intelligence_mode") or d.get("intelligence_mode", "hybrid")
    control_mode = u.get("control_mode") or d.get("control_mode", "manual")
    auto_scope = u.get("auto_scope") or d.get("auto_scope", "both")

    return {
        "intelligence_mode": intelligence_mode,
        "control_mode": control_mode,
        "auto_scope": auto_scope,
    }
