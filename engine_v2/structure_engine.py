from typing import Dict


def choose_structure(signal: Dict, decision: Dict) -> Dict:
    direction = str(signal.get("direction", "") or "").upper()
    iv_context = str(signal.get("iv_context", "normal") or "normal").lower()
    timing_state = str(decision.get("ready_state", "watch") or "watch").lower()
    structure_quality = float(signal.get("structure_quality", 50) or 50)

    structure_choice = "watch_only"
    structure_reason = "idea is not ready for execution"

    if decision.get("ready_state") in {"reject", "watch"}:
        return {
            "structure_choice": structure_choice,
            "structure_reason": structure_reason,
        }

    if direction == "CALL":
        if iv_context in {"high", "rich"}:
            structure_choice = "call_debit_spread"
            structure_reason = "bullish idea with rich volatility favors defined-risk premium efficiency"
        else:
            structure_choice = "long_call"
            structure_reason = "bullish idea with normal volatility can use direct upside expression"
    elif direction == "PUT":
        if iv_context in {"high", "rich"}:
            structure_choice = "put_debit_spread"
            structure_reason = "bearish idea with rich volatility favors defined-risk premium efficiency"
        else:
            structure_choice = "long_put"
            structure_reason = "bearish idea with normal volatility can use direct downside expression"
    else:
        structure_choice = "watch_only"
        structure_reason = "direction is unclear, so execution should wait"

    if structure_quality < 45:
        structure_choice = "watch_only"
        structure_reason = "structure quality is too weak for clean execution"

    if timing_state == "ready_soon":
        structure_reason += "; timing is improving but not fully clean yet"

    return {
        "structure_choice": structure_choice,
        "structure_reason": structure_reason,
    }
