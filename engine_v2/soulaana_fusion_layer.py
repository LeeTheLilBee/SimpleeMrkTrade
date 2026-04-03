from typing import Dict


def build_soulaana_fusion_layer(
    alignment: Dict,
    clarity: Dict,
    edge_quality: Dict,
    contradiction: Dict,
    capital_gate: Dict,
    late_entry: Dict,
    only_the_ones: Dict,
    cutthroat: Dict,
) -> Dict:
    """
    Final Soulaana judgment layer.

    This takes the major Soulaana intelligence outputs and turns them into:
    - soulaana_state
    - soulaana_score
    - soulaana_reason
    - soulaana_verdict
    - soulaana_command_phrase
    """

    soulaana_score = 0
    soulaana_reasons = []

    alignment_state = str(alignment.get("alignment_state", "partial") or "partial")
    clarity_score = float(clarity.get("clarity_score", 0) or 0)
    edge_state = str(edge_quality.get("edge_quality_state", "weak") or "weak")
    contradiction_count = int(contradiction.get("contradiction_count", 0) or 0)

    capital_gate_state = str(
        capital_gate.get("capital_gate_state", "caution") or "caution"
    )
    late_entry_blocked = bool(late_entry.get("late_entry_blocked", False))
    only_the_ones_allowed = bool(
        only_the_ones.get("only_the_ones_allowed", True)
    )
    final_block = bool(cutthroat.get("final_block", False))

    # ----------------------------
    # HARD BLOCKS
    # ----------------------------
    if final_block:
        return {
            "soulaana_state": "blocked",
            "soulaana_score": -100,
            "soulaana_reasons": ["cutthroat layer blocked trade"],
            "soulaana_verdict": "Stand down.",
            "soulaana_command_phrase": "Do not act.",
        }

    if capital_gate_state == "deny":
        return {
            "soulaana_state": "denied",
            "soulaana_score": -80,
            "soulaana_reasons": ["capital gate denied allocation"],
            "soulaana_verdict": "Not worth capital.",
            "soulaana_command_phrase": "Pass.",
        }

    if late_entry_blocked:
        return {
            "soulaana_state": "too_late",
            "soulaana_score": -60,
            "soulaana_reasons": ["entry timing no longer valid"],
            "soulaana_verdict": "Missed the move.",
            "soulaana_command_phrase": "Wait.",
        }

    # ----------------------------
    # NEGATIVE PRESSURE
    # ----------------------------
    if not only_the_ones_allowed:
        soulaana_score -= 25
        soulaana_reasons.append("not one of the best expressions")

    if contradiction_count > 0:
        contradiction_penalty = contradiction_count * 10
        soulaana_score -= contradiction_penalty
        soulaana_reasons.append(
            f"{contradiction_count} internal conflicts detected"
        )

    # ----------------------------
    # POSITIVE BUILD
    # ----------------------------
    if alignment_state == "aligned":
        soulaana_score += 25
        soulaana_reasons.append("layers aligned")
    elif alignment_state == "partial":
        soulaana_score += 10
        soulaana_reasons.append("partial alignment present")
    elif alignment_state == "conflicted":
        soulaana_score -= 10
        soulaana_reasons.append("alignment is conflicted")
    elif alignment_state == "broken":
        soulaana_score -= 25
        soulaana_reasons.append("alignment is broken")

    if clarity_score >= 100:
        soulaana_score += 30
        soulaana_reasons.append("exceptional clarity")
    elif clarity_score >= 70:
        soulaana_score += 15
        soulaana_reasons.append("good clarity")
    elif clarity_score >= 40:
        soulaana_score += 5
        soulaana_reasons.append("usable clarity")
    else:
        soulaana_score -= 10
        soulaana_reasons.append("clarity is weak")

    if edge_state == "elite":
        soulaana_score += 30
        soulaana_reasons.append("elite edge")
    elif edge_state == "strong":
        soulaana_score += 15
        soulaana_reasons.append("strong edge")
    elif edge_state == "usable":
        soulaana_score += 5
        soulaana_reasons.append("usable edge")
    elif edge_state == "marginal":
        soulaana_score -= 10
        soulaana_reasons.append("edge is marginal")
    else:
        soulaana_score -= 20
        soulaana_reasons.append("edge is weak")

    # ----------------------------
    # FINAL STATE
    # ----------------------------
    if soulaana_score >= 60:
        soulaana_state = "conviction"
        soulaana_verdict = "This holds."
        soulaana_command_phrase = "You can act."
    elif soulaana_score >= 25:
        soulaana_state = "valid"
        soulaana_verdict = "This is workable."
        soulaana_command_phrase = "Proceed carefully."
    elif soulaana_score >= 0:
        soulaana_state = "weak"
        soulaana_verdict = "This is fragile."
        soulaana_command_phrase = "Size down or wait."
    else:
        soulaana_state = "reject"
        soulaana_verdict = "This does not hold."
        soulaana_command_phrase = "Do not act."

    return {
        "soulaana_state": soulaana_state,
        "soulaana_score": soulaana_score,
        "soulaana_reasons": soulaana_reasons,
        "soulaana_verdict": soulaana_verdict,
        "soulaana_command_phrase": soulaana_command_phrase,
    }
