from typing import Dict


def evaluate_alignment(
    decision: Dict,
    execution: Dict,
    regime: Dict,
    thesis: Dict,
    timeline: Dict,
    threat: Dict,
) -> Dict:
    ready_state = str(decision.get("ready_state", "watch") or "watch")
    entry_state = str(execution.get("entry_state", "wait") or "wait")
    regime_alignment = str(regime.get("regime_alignment", "neutral") or "neutral")
    thesis_quality = str(
        thesis.get("thesis_quality", {}).get("thesis_quality", "weak") or "weak"
    )
    timeline_phase = str(timeline.get("timeline_phase", "early") or "early")
    threat_level = str(
        threat.get("threat_score", {}).get("threat_level", "low") or "low"
    )

    score = 0
    reasons = []

    if ready_state == "ready_now":
        score += 25
        reasons.append("decision layer is ready now")
    elif ready_state == "ready_soon":
        score += 15
        reasons.append("decision layer is approaching readiness")
    elif ready_state == "watch":
        score += 5
        reasons.append("decision layer is still forming")
    else:
        score -= 25
        reasons.append("decision layer rejected the setup")

    if entry_state == "clean":
        score += 20
        reasons.append("execution layer sees a clean entry")
    elif entry_state == "acceptable":
        score += 10
        reasons.append("execution is valid but not ideal")
    elif entry_state in {"missed", "blocked"}:
        score -= 20
        reasons.append("execution layer does not support active deployment")

    if regime_alignment == "favored":
        score += 15
        reasons.append("regime supports the setup")
    elif regime_alignment == "caution":
        score -= 5
        reasons.append("regime calls for caution")
    elif regime_alignment == "suppressed":
        score -= 20
        reasons.append("regime suppresses the setup")

    if thesis_quality == "strong":
        score += 15
        reasons.append("thesis quality is strong")
    elif thesis_quality == "moderate":
        score += 8
        reasons.append("thesis is usable but not elite")
    else:
        score -= 10
        reasons.append("thesis quality is weak")

    if timeline_phase == "ready":
        score += 15
        reasons.append("timeline phase is ready")
    elif timeline_phase == "building":
        score += 8
        reasons.append("timeline phase is building")
    elif timeline_phase in {"exhausting", "broken"}:
        score -= 15
        reasons.append("timeline phase is no longer supportive")

    if threat_level == "low":
        score += 10
        reasons.append("threat level is low")
    elif threat_level == "medium":
        score += 0
        reasons.append("threat level is manageable")
    elif threat_level == "high":
        score -= 15
        reasons.append("threat level is elevated")
    else:
        score -= 30
        reasons.append("threat level is extreme")

    if score >= 65:
        state = "aligned"
        summary = "trade layers are broadly agreeing"
    elif score >= 40:
        state = "partial"
        summary = "trade has support, but alignment is incomplete"
    elif score >= 15:
        state = "conflicted"
        summary = "trade contains meaningful internal disagreement"
    else:
        state = "broken"
        summary = "trade does not hold together across layers"

    return {
        "alignment_state": state,
        "alignment_score": round(score, 2),
        "alignment_summary": summary,
        "alignment_reasons": reasons,
    }
