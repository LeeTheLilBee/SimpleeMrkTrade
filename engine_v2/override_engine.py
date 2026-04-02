from typing import Dict


def evaluate_overrides(system_state: Dict, decision_context: Dict) -> Dict:
    governance_priority = bool(system_state.get("governance_priority", True))
    requested_action = str(decision_context.get("requested_action", "none") or "none")
    blocked_by_governance = bool(decision_context.get("blocked_by_governance", False))

    if governance_priority and blocked_by_governance:
        return {
            "override_applied": True,
            "override_reason": f"requested action ({requested_action}) was blocked by governance",
        }

    return {
        "override_applied": False,
        "override_reason": "no override required",
    }
