from typing import Dict


def track_missed_opportunity(signal: Dict, decision: Dict) -> Dict:
    if decision.get("ready_state") == "ready_now" and decision.get("taken") is False:
        return {
            "missed": True,
            "reason": "valid setup not executed",
        }

    if decision.get("entry_state") == "missed":
        return {
            "missed": True,
            "reason": "entry arrived too late",
        }

    return {
        "missed": False,
        "reason": "no missed opportunity",
    }
