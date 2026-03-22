def evaluate_position_health(trade):
    score = trade.get("score", 0)
    prev_score = trade.get("previous_score", score)

    entry = trade.get("entry", 0)
    current = trade.get("current_price", entry)
    stop = trade.get("stop", entry)
    target = trade.get("target", entry)

    # ---------------------------
    # COMPONENTS
    # ---------------------------

    # Score strength
    if score >= 180:
        score_component = 90
    elif score >= 130:
        score_component = 70
    elif score >= 90:
        score_component = 50
    else:
        score_component = 30

    # Score direction
    delta = score - prev_score

    if delta > 0:
        direction = "improving"
    elif delta < 0:
        direction = "deteriorating"
    else:
        direction = "stable"

    # Price progress
    if target > entry:
        progress = (current - entry) / max((target - entry), 1)
    else:
        progress = 0

    progress = max(0, min(progress, 1))

    # Risk distance
    risk_distance = abs(current - stop) / max(abs(entry - stop), 1)

    # ---------------------------
    # HEALTH SCORE
    # ---------------------------
    health_score = int(
        (score_component * 0.5) +
        (progress * 100 * 0.3) +
        (risk_distance * 100 * 0.2)
    )

    health_score = max(0, min(health_score, 100))

    # ---------------------------
    # LABEL
    # ---------------------------
    if health_score >= 85:
        label = "Elite"
    elif health_score >= 70:
        label = "Strong"
    elif health_score >= 55:
        label = "Healthy"
    elif health_score >= 40:
        label = "At Risk"
    else:
        label = "Critical"

    # ---------------------------
    # BREAKDOWN (WHY)
    # ---------------------------
    breakdown = []

    if delta < 0:
        breakdown.append("Score deterioration detected")

    if progress < 0.3:
        breakdown.append("Weak follow-through from entry")

    if risk_distance < 0.5:
        breakdown.append("Price nearing stop level")

    if score < 90:
        breakdown.append("Low structural strength")

    # ---------------------------
    # DEGRADATION LEVEL
    # ---------------------------
    if delta < -20:
        degradation = "sharp"
    elif delta < -5:
        degradation = "moderate"
    else:
        degradation = "stable"

    # ---------------------------
    # ACTION LADDER
    # ---------------------------
    if health_score >= 85:
        action = "Press advantage / hold strong"
    elif health_score >= 70:
        action = "Hold / manage position"
    elif health_score >= 55:
        action = "Reduce exposure slightly"
    elif health_score >= 40:
        action = "Defensive posture / tighten risk"
    else:
        action = "Exit or protect capital"

    # ---------------------------
    # EVENT TRIGGERS
    # ---------------------------
    events = []

    if degradation == "sharp":
        events.append("Structure breakdown event")

    if health_score < 50:
        events.append("Health critical threshold")

    if risk_distance < 0.3:
        events.append("Stop proximity warning")

    return {
        "score": health_score,
        "label": label,
        "direction": direction,
        "progress": round(progress, 2),
        "breakdown": breakdown,
        "degradation": degradation,
        "action": action,
        "events": events
    }


def attach_position_health(positions):
    enriched = []

    for p in positions:
        p["health"] = evaluate_position_health(p)
        enriched.append(p)

    return enriched
