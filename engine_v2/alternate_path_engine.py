from typing import Dict


def determine_alternate_path(trade: Dict, counterfactual_trigger: Dict) -> Dict:
    trigger = str(counterfactual_trigger.get("counterfactual_trigger", "unclear") or "unclear")
    only_the_ones_allowed = bool(trade.get("only_the_ones_allowed", True))
    structure_quality = str(trade.get("contract_quality", "weak") or "weak")
    deception_level = str(trade.get("deception_level", "low") or "low")

    path = "stand_down"
    reason = "no better path could be justified from the current setup"

    if trigger == "timing":
        path = "wait_for_reset"
        reason = "the better path was patience until timing improved"
    elif trigger == "deception":
        path = "require_confirmation"
        reason = "the setup needed truth confirmation before action"
    elif trigger == "intent":
        path = "stand_down"
        reason = "the market was behaving too hostily to justify participation"
    elif trigger == "structure":
        if structure_quality in {"weak", "poor"}:
            path = "use_defined_risk"
            reason = "a tighter, more controlled structure would have been the better path"
    elif trigger == "thesis":
        path = "thesis_rebuild"
        reason = "the trade needed a stronger underlying idea before execution"
    elif trigger == "environment":
        path = "reduce_size"
        reason = "if participation was necessary, it needed less exposure"

    if not only_the_ones_allowed:
        path = "favor_alternate_symbol"
        reason = "the better path was probably the cleaner expression elsewhere"

    if deception_level == "severe":
        path = "stand_down"
        reason = "severe deception means no alternate execution path deserved action"

    return {
        "alternate_path": path,
        "alternate_path_reason": reason,
    }
