from typing import Dict, List


def detect_contradictions(
    decision: Dict,
    execution: Dict,
    alignment: Dict,
    thesis: Dict,
    timeline: Dict,
    threat: Dict,
    decay: Dict,
    regime: Dict,
) -> Dict:
    issues: List[str] = []

    ready_state = str(decision.get("ready_state", "watch") or "watch")
    entry_state = str(execution.get("entry_state", "wait") or "wait")
    alignment_state = str(alignment.get("alignment_state", "partial") or "partial")
    thesis_quality = str(thesis.get("thesis_quality", {}).get("thesis_quality", "weak") or "weak")
    timeline_phase = str(timeline.get("timeline_phase", "early") or "early")
    threat_level = str(threat.get("threat_score", {}).get("threat_level", "low") or "low")
    decay_state = str(decay.get("decay_state", "active") or "active")
    regime_alignment = str(regime.get("regime_alignment", "neutral") or "neutral")

    if ready_state == "ready_now" and threat_level == "extreme":
        issues.append("decision is ready, but threat is extreme")

    if ready_state == "ready_now" and decay_state == "expired":
        issues.append("decision is ready, but opportunity is expired")

    if entry_state == "clean" and regime_alignment == "suppressed":
        issues.append("execution is clean, but regime suppresses the setup")

    if thesis_quality == "strong" and alignment_state in {"conflicted", "broken"}:
        issues.append("thesis is strong, but trade alignment is weak")

    if timeline_phase == "ready" and threat_level == "high":
        issues.append("timeline is ready, but threat remains elevated")

    if ready_state == "reject" and entry_state in {"clean", "acceptable"}:
        issues.append("execution appears usable despite trade rejection")

    count = len(issues)

    if count == 0:
        state = "none"
        reason = "no meaningful internal contradictions detected"
    elif count == 1:
        state = "light"
        reason = "minor contradiction detected"
    elif count <= 3:
        state = "meaningful"
        reason = "multiple layers are disagreeing"
    else:
        state = "severe"
        reason = "trade contains heavy internal conflict"

    return {
        "contradiction_state": state,
        "contradiction_count": count,
        "contradiction_reason": reason,
        "contradiction_issues": issues,
    }
