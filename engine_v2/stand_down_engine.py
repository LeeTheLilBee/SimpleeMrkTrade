from typing import Dict


def evaluate_stand_down(
    capital_gate: Dict,
    late_entry: Dict,
    contradiction: Dict,
) -> Dict:
    gate = str(capital_gate.get("capital_gate_state", "caution"))
    late_blocked = bool(late_entry.get("late_entry_blocked", False))
    contradiction_state = str(contradiction.get("contradiction_state", "none"))

    stand_down = False
    reason = "no stand-down required"

    if gate == "deny":
        stand_down = True
        reason = "capital gate denied the trade"

    elif late_blocked:
        stand_down = True
        reason = "entry timing is no longer valid"

    elif contradiction_state == "severe":
        stand_down = True
        reason = "contradictions are too strong"

    return {
        "stand_down": stand_down,
        "stand_down_reason": reason,
    }
