from typing import List, Dict

from engine_v2.risk_philosophy import should_force_hold


def evaluate_do_nothing(decisions: List[Dict]) -> Dict:
    if should_force_hold(decisions):
        return {
            "do_nothing": True,
            "reason": "no setups meet the quality threshold",
        }

    return {
        "do_nothing": False,
        "reason": "at least one setup is strong enough to consider",
    }
