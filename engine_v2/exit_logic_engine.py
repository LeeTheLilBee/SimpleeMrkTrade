from typing import Dict


def build_exit_plan(signal: Dict, decision: Dict) -> Dict:
    ready_state = str(decision.get("ready_state", "watch") or "watch")
    structure_choice = str(decision.get("structure_choice", "watch_only") or "watch_only")
    trap_risk = str(decision.get("trap", {}).get("trap_risk", "low") or "low")

    exit_plan = "stand_aside"
    exit_reason = "execution is not active"

    if ready_state == "ready_now" and structure_choice != "watch_only":
        if trap_risk == "high":
            exit_plan = "tight_risk"
            exit_reason = "trade requires tight defense due to elevated trap risk"
        elif "spread" in structure_choice:
            exit_plan = "defined_risk_manage_to_target"
            exit_reason = "defined-risk spread can be managed toward target or time decay threshold"
        else:
            exit_plan = "scale_or_cut"
            exit_reason = "single-leg option should scale on strength or cut quickly on failure"
    elif ready_state == "ready_soon":
        exit_plan = "wait_for_confirmation"
        exit_reason = "do not plan exits before the entry is truly live"

    return {
        "exit_plan": exit_plan,
        "exit_reason": exit_reason,
    }
