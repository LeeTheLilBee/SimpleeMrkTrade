from typing import Dict


def attribute_outcome(trade: Dict) -> Dict:
    pnl = float(trade.get("pnl", 0))
    timing = trade.get("timing_score", 0)
    structure = trade.get("structure_choice", "unknown")
    entry_state = trade.get("entry_state", "unknown")

    if pnl > 0:
        outcome = "win"
    else:
        outcome = "loss"

    reason = "unclear"

    if outcome == "loss":
        if entry_state == "missed":
            reason = "chasing entry"
        elif timing < 50:
            reason = "poor timing"
        elif structure == "watch_only":
            reason = "invalid structure"
        else:
            reason = "idea failure"

    return {
        "outcome": outcome,
        "outcome_reason": reason,
    }
