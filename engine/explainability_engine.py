def explain_trade_decision(trade, mode=None, regime=None, breadth=None, volatility=None):
    reasons = []

    score = float(trade.get("score", 0) or 0)
    confidence = str(trade.get("confidence", "LOW")).upper()
    trend = str(trade.get("trend", "")).upper()
    strategy = trade.get("strategy", "UNKNOWN")

    if score >= 200:
        reasons.append("High conviction signal strength.")
    elif score >= 150:
        reasons.append("Strong signal quality with meaningful alignment.")
    elif score >= 100:
        reasons.append("Moderate signal strength with developing structure.")
    else:
        reasons.append("Trade passed the minimum threshold for consideration.")

    if confidence == "HIGH":
        reasons.append("Confidence is high based on the current signal stack.")
    elif confidence == "MEDIUM":
        reasons.append("Confidence is moderate, so trade quality is acceptable but not elite.")
    else:
        reasons.append("Confidence is lower, so this trade should be handled cautiously.")

    if trend == "UPTREND" and strategy == "CALL":
        reasons.append("Strategy is aligned with the current upward trend.")
    elif trend == "DOWNTREND" and strategy == "PUT":
        reasons.append("Strategy is aligned with the current downward trend.")

    if mode:
        reasons.append(f"Market mode at decision time: {mode}.")

    if regime:
        reasons.append(f"Broader regime context: {regime}.")

    if breadth:
        reasons.append(f"Market breadth context: {breadth}.")

    if volatility:
        reasons.append(f"Volatility state: {volatility}.")

    return reasons


def explain_rejection(trade, reason):
    mapping = {
        "sector_blocked": "Rejected because the portfolio already has too much exposure in this sector.",
        "correlation_blocked": "Rejected because the symbol is too correlated with existing exposure.",
        "breadth_blocked": "Rejected because market breadth does not support this setup.",
        "execution_blocked": "Rejected because execution controls did not allow the trade.",
        "buying_power": "Rejected because there was not enough buying power.",
        "buying_power_min_size": "Rejected because the account could not afford even the minimum size.",
        "existing_open_position": "Rejected because a position in this symbol is already open.",
        "daily_entry_cap": "Rejected because the daily entry limit was reached.",
        "governor_blocked": "Rejected by governor rules.",
        "not_selected": "Approved in research but not selected for execution.",
    }
    return mapping.get(reason, f"Rejected due to: {reason}.")


def explain_exit(reason, pnl):
    pnl = float(pnl or 0)

    if reason == "take_profit":
        return "Position closed because the target zone was reached and profit was secured."
    if reason == "stop_loss":
        return "Position closed because the stop level was breached and risk control took priority."
    if reason == "no_follow_through":
        return "Position closed because price failed to follow through after entry."
    if reason == "time_exit":
        return "Position closed because the trade became stale and capital was better used elsewhere."
    if reason == "structure_deterioration":
        return "Position closed because the underlying setup weakened after entry."
    if reason == "profit_protect":
        return "Position closed to protect gains after the move began to lose strength."
    if reason == "manual":
        return "Position was closed manually."

    direction = "profit" if pnl >= 0 else "loss"
    return f"Position closed due to {reason}, resulting in a {direction} of {round(pnl, 2)}."


def explain_position_state(position, current_price=None):
    entry = float(position.get("entry", position.get("price", 0)) or 0)
    target = float(position.get("target", entry) or entry)
    stop = float(position.get("stop", entry) or entry)
    current = float(current_price if current_price is not None else position.get("current_price", entry) or entry)
    score = float(position.get("score", 0) or 0)
    prev_score = float(position.get("previous_score", score) or score)

    lines = []

    if current > entry:
        lines.append("The trade is currently above entry and is in profit territory.")
    elif current < entry:
        lines.append("The trade is currently below entry and is under pressure.")
    else:
        lines.append("The trade is currently sitting near entry.")

    if current >= target:
        lines.append("The trade is at or above target.")
    elif current <= stop:
        lines.append("The trade is at or below the stop level.")
    else:
        lines.append("The trade is still between stop and target.")

    if score > prev_score:
        lines.append("Signal structure is improving relative to the prior reading.")
    elif score < prev_score:
        lines.append("Signal structure is weakening relative to the prior reading.")
    else:
        lines.append("Signal structure is stable relative to the prior reading.")

    return lines
