from typing import Dict


def build_memory_trust_adjustment(memory_intelligence: Dict) -> Dict:
    composite_state = str(memory_intelligence.get("composite_trust_state", "stable") or "stable")
    composite_score = float(memory_intelligence.get("composite_trust_score", 50) or 50)
    family_trust = memory_intelligence.get("family_trust", {}) if isinstance(memory_intelligence, dict) else {}
    trust_state = str(family_trust.get("trust_state", "uncertain_trust") or "uncertain_trust")

    adjustment = 0
    reasons = []

    if composite_state == "reinforced":
        adjustment += 20
        reasons.append("memory reinforces current trust")
    elif composite_state == "stable":
        adjustment += 8
        reasons.append("memory is supportive enough to maintain trust")
    elif composite_state == "fragile":
        adjustment -= 12
        reasons.append("memory weakens normal trust")
    elif composite_state == "degraded":
        adjustment -= 25
        reasons.append("memory does not support normal conviction")

    if trust_state == "high_trust":
        adjustment += 8
        reasons.append("setup family is currently high trust")
    elif trust_state == "low_trust":
        adjustment -= 8
        reasons.append("setup family is currently low trust")
    elif trust_state == "minimal_trust":
        adjustment -= 15
        reasons.append("setup family is currently damaged")

    if composite_score >= 100:
        adjustment += 5
        reasons.append("composite trust is exceptionally strong")

    if adjustment >= 20:
        state = "strong_support"
    elif adjustment > 0:
        state = "supportive"
    elif adjustment == 0:
        state = "neutral"
    elif adjustment > -15:
        state = "cautious"
    else:
        state = "punitive"

    return {
        "memory_adjustment_state": state,
        "memory_adjustment_score": adjustment,
        "memory_adjustment_reasons": reasons,
    }
