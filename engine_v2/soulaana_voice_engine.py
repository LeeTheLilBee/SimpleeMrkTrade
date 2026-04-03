from typing import Dict


def build_soulaana_voice(
    alignment: Dict,
    clarity: Dict,
    contradiction: Dict,
    decay: Dict,
    edge_quality: Dict,
    capital_gate: Dict,
    late_entry: Dict,
) -> Dict:
    alignment_state = str(alignment.get("alignment_state", "partial") or "partial")
    clarity_state = str(clarity.get("clarity_state", "unclear") or "unclear")
    contradiction_state = str(contradiction.get("contradiction_state", "none") or "none")
    decay_state = str(decay.get("decay_state", "active") or "active")
    edge_state = str(edge_quality.get("edge_quality_state", "weak") or "weak")
    capital_gate_state = str(capital_gate.get("capital_gate_state", "caution") or "caution")
    late_entry_blocked = bool(late_entry.get("late_entry_blocked", False))

    if late_entry_blocked:
        verdict = "This is late."
        insight = "The better version already passed."
        command_phrase = "Stand down."
    elif capital_gate_state == "deny":
        verdict = "No."
        insight = "This doesn’t deserve capital."
        command_phrase = "Do not deploy."
    elif contradiction_state in {"meaningful", "severe"}:
        verdict = "This conflicts."
        insight = "The trade is not telling one clean story."
        command_phrase = "Do not force it."
    elif edge_state == "elite" and alignment_state == "aligned" and clarity_state == "clear":
        verdict = "This holds."
        insight = "The trade is aligned, clear, and deserving of capital."
        command_phrase = "You can act."
    elif decay_state == "decaying":
        verdict = "This is fading."
        insight = "The edge is still present, but it is losing freshness."
        command_phrase = "Only act if execution is clean."
    elif clarity_state in {"murky", "unclear"}:
        verdict = "This doesn’t sit right."
        insight = "There is enough ambiguity here to reduce trust."
        command_phrase = "Wait."
    else:
        verdict = "This is usable."
        insight = "The trade is valid, but not one of the cleanest on the board."
        command_phrase = "Be selective."

    return {
        "soulaana_verdict": verdict,
        "soulaana_insight": insight,
        "soulaana_command_phrase": command_phrase,
    }
