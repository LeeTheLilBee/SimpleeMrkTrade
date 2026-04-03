from typing import Dict


def determine_minimum_change(trade: Dict, counterfactual_trigger: Dict) -> Dict:
    trigger = str(counterfactual_trigger.get("counterfactual_trigger", "unclear") or "unclear")

    minimum_change = "unclear"
    reason = "minimum change could not be isolated"

    if trigger == "timing":
        minimum_change = "improve_entry_timing"
        reason = "a cleaner entry window may have materially improved the result"
    elif trigger == "deception":
        minimum_change = "wait_for_truth_confirmation"
        reason = "the trade needed real confirmation before trust was justified"
    elif trigger == "intent":
        minimum_change = "require_better_market_intent"
        reason = "the market needed to behave more supportively before action"
    elif trigger == "structure":
        minimum_change = "upgrade_structure_quality"
        reason = "a better contract or structure may have made the trade viable"
    elif trigger == "thesis":
        minimum_change = "rebuild_the_thesis"
        reason = "the setup needed a stronger underlying case, not just better execution"
    elif trigger == "environment":
        minimum_change = "avoid_hostile_conditions"
        reason = "the same trade may have worked only in a cleaner environment"

    return {
        "minimum_change": minimum_change,
        "minimum_change_reason": reason,
    }
