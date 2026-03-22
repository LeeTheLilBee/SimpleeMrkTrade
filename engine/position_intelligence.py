
def build_position_intelligence(position):
    """
    Build structured intelligence for positions.
    """

    score = position.get("score", 50)

    if score >= 80:
        status = "strong"
        direction = "improving"
        phase = "developing"
    elif score >= 60:
        status = "stable"
        direction = "steady"
        phase = "active"
    elif score >= 40:
        status = "weakening"
        direction = "slipping"
        phase = "under pressure"
    else:
        status = "at risk"
        direction = "deteriorating"
        phase = "critical"

    thesis_state = "intact" if score >= 60 else "under pressure"

    damage = []
    if score < 70:
        damage.append("Momentum weakening")
    if score < 60:
        damage.append("Trend strength fading")
    if score < 50:
        damage.append("Volatility risk increasing")

    if not damage:
        damage = ["No major damage detected"]

    forward_paths = [
        "Continuation higher if structure holds",
        "Consolidation if momentum stalls"
    ]

    invalidation = "Break of key support would invalidate setup"

    opportunity_score = max(0, 100 - score)

    if score >= 70:
        action_bias = "Hold and monitor"
    elif score >= 50:
        action_bias = "Stay cautious"
    else:
        action_bias = "Reduce exposure"

    return {
        "snapshot": {
            "score": score,
            "status": status,
            "direction": direction,
            "phase": phase
        },
        "thesis": {
            "state": thesis_state,
            "summary": "The setup remains aligned with current conditions but requires monitoring."
        },
        "damage": damage[:3],
        "forward_paths": forward_paths,
        "invalidation": invalidation,
        "opportunity_score": opportunity_score,
        "action_bias": action_bias
    }
