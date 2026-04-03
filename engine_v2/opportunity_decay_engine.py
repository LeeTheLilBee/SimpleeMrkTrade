from typing import Dict


def evaluate_opportunity_decay(
    signal: Dict,
    execution: Dict,
    timeline: Dict,
    threat: Dict,
) -> Dict:
    extension = float(signal.get("extension_score", 0) or 0)
    entry_state = str(execution.get("entry_state", "wait") or "wait")
    timeline_phase = str(timeline.get("timeline_phase", "early") or "early")
    threat_level = str(threat.get("threat_score", {}).get("threat_level", "low") or "low")

    score = 0
    reasons = []

    if extension >= 85:
        score += 45
        reasons.append("move is heavily extended")
    elif extension >= 65:
        score += 25
        reasons.append("move is becoming extended")
    elif extension >= 45:
        score += 10
        reasons.append("some extension is present")

    if entry_state == "missed":
        score += 35
        reasons.append("entry window has already been missed")
    elif entry_state == "acceptable":
        score += 10
        reasons.append("entry is valid but not fresh")
    elif entry_state == "clean":
        score -= 10
        reasons.append("entry quality is still clean")

    if timeline_phase == "expanding":
        score += 20
        reasons.append("move is already underway")
    elif timeline_phase == "exhausting":
        score += 35
        reasons.append("setup is near exhaustion")
    elif timeline_phase == "ready":
        score -= 10
        reasons.append("timeline still supports action")

    if threat_level == "high":
        score += 10
        reasons.append("threat level accelerates decay risk")
    elif threat_level == "extreme":
        score += 20
        reasons.append("extreme threat sharply reduces opportunity life")

    if score <= 5:
        state = "durable"
        summary = "opportunity remains fresh enough to work with"
    elif score <= 25:
        state = "active"
        summary = "opportunity is live, but should not be delayed too long"
    elif score <= 55:
        state = "decaying"
        summary = "edge is fading and timing matters more now"
    else:
        state = "expired"
        summary = "the better version of this opportunity has likely passed"

    return {
        "decay_state": state,
        "decay_score": round(score, 2),
        "decay_summary": summary,
        "decay_reasons": reasons,
    }
