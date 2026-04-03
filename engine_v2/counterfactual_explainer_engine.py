from typing import Dict


def explain_counterfactual(
    counterfactual_trigger: Dict,
    minimum_change: Dict,
    alternate_path: Dict,
    salvageability: Dict,
) -> Dict:
    trigger = str(counterfactual_trigger.get("counterfactual_trigger", "unclear") or "unclear")
    trigger_reason = str(counterfactual_trigger.get("counterfactual_trigger_reason", "") or "")
    change_reason = str(minimum_change.get("minimum_change_reason", "") or "")
    alt_reason = str(alternate_path.get("alternate_path_reason", "") or "")
    salvage_state = str(salvageability.get("salvageability_state", "conditionally_salvageable") or "conditionally_salvageable")
    salvage_reason = str(salvageability.get("salvageability_reason", "") or "")

    line = "The outcome may have changed under different conditions."

    if salvage_state == "salvageable":
        line = "This trade may have worked with one meaningful correction."
    elif salvage_state == "conditionally_salvageable":
        line = "This trade needed tighter conditions to deserve trust."
    elif salvage_state == "unsalvageable":
        line = "This trade was not worth saving in its current form."

    return {
        "counterfactual_line": line,
        "counterfactual_trigger_reason": trigger_reason,
        "counterfactual_change_reason": change_reason,
        "counterfactual_alternate_path_reason": alt_reason,
        "counterfactual_salvage_reason": salvage_reason,
    }
