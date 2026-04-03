from typing import Dict


def evaluate_salvageability(
    trade: Dict,
    counterfactual_trigger: Dict,
    minimum_change: Dict,
) -> Dict:
    trigger = str(counterfactual_trigger.get("counterfactual_trigger", "unclear") or "unclear")
    change = str(minimum_change.get("minimum_change", "unclear") or "unclear")
    thesis_quality = str(trade.get("thesis_quality", "weak") or "weak")
    deception_level = str(trade.get("deception_level", "low") or "low")

    state = "conditionally_salvageable"
    reason = "the trade may have been recoverable under tighter conditions"

    if deception_level == "severe" and thesis_quality == "weak":
        state = "unsalvageable"
        reason = "the setup was too compromised to justify saving"
    elif trigger in {"timing", "structure"} and thesis_quality == "strong":
        state = "salvageable"
        reason = "the trade may have worked with a cleaner implementation"
    elif change in {"rebuild_the_thesis", "unclear"}:
        state = "unsalvageable"
        reason = "the setup needed more than tactical improvement"

    return {
        "salvageability_state": state,
        "salvageability_reason": reason,
    }
