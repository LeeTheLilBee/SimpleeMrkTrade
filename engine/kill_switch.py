def should_kill_position(pos):
    score = pos.get("health_score", 100)
    warning = pos.get("warning")

    # 🔴 HARD KILL
    if score < 25:
        return True, "CRITICAL WEAKNESS"

    # 🟠 EARLY EXIT
    if score < 40 and warning == "DEGRADING":
        return True, "DEGRADING TRADE"

    # 🟡 MOMENTUM LOSS
    if warning == "LOSING MOMENTUM":
        return True, "MOMENTUM LOST"

    return False, None
