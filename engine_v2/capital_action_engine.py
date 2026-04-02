from typing import List, Dict

from engine_v2.risk_philosophy import should_force_hold


def determine_capital_action(decisions: List[Dict]) -> Dict:
    valid_decisions = [d for d in decisions if isinstance(d, dict)]

    if not valid_decisions:
        return {
            "capital_action": "hold",
            "reason": "no decisions available",
        }

    if should_force_hold(valid_decisions):
        return {
            "capital_action": "hold",
            "reason": "risk philosophy forced a no-trade state",
        }

    ready_now = [d for d in valid_decisions if d.get("ready_state") == "ready_now"]
    strong = [d for d in ready_now if d.get("priority_label") in {"kill_shot", "high"}]

    if strong:
        return {
            "capital_action": "deploy",
            "reason": "high-priority capital-worthy opportunities are available",
        }

    if ready_now:
        return {
            "capital_action": "reduce",
            "reason": "setups exist, but quality is not strong enough for full aggression",
        }

    return {
        "capital_action": "hold",
        "reason": "no clean ready-now opportunities are available",
    }
