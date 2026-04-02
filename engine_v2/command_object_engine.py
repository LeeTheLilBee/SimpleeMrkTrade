from typing import Dict


def build_command_object(master_decision: Dict) -> Dict:
    final_state = master_decision.get("final_state", "unknown")
    blocked = bool(master_decision.get("governance_blocked", False))
    symbol = master_decision.get("symbol", "")
    entry_state = master_decision.get("execution", {}).get("entry_state", "wait")
    next_action = master_decision.get("experience", {}).get("next_action", "wait")
    threat_level = master_decision.get("threat_level", "low")
    timeline_phase = master_decision.get("timeline", {}).get("timeline_phase", "unknown")

    if blocked:
        command = "block"
    elif final_state == "actionable" and entry_state in {"clean", "acceptable"}:
        command = "deploy"
    elif final_state == "prepare":
        command = "prepare"
    elif final_state == "monitor":
        command = "monitor"
    else:
        command = "stand_down"

    return {
        "symbol": symbol,
        "command": command,
        "final_state": final_state,
        "entry_state": entry_state,
        "next_action": next_action,
        "threat_level": threat_level,
        "timeline_phase": timeline_phase,
        "blocked": blocked,
    }
