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


def explain_rejection(trade, reason_key):
    symbol = trade.get("symbol", "This setup")

    base = f"{symbol} was not taken."

    mapping = {
        "breadth_blocked": "Market participation did not support the direction of this setup.",
        "mode_blocked": "Current market mode favors defensive positioning and did not allow this structure.",
        "execution_blocked": "Execution controls prevented entry despite the setup conditions.",
        "score_too_low": "The setup did not meet the internal quality threshold required for deployment.",
        "volatility_blocked": "Volatility conditions reduced confidence below acceptable levels.",
        "weak_option_contract": "No suitable option contract provided efficient exposure for this idea.",
        "reentry_blocked": "The system requires stronger confirmation before re-entering this symbol.",
        "not_selected": "The setup passed filters but ranked below stronger opportunities.",
    }

    detail = mapping.get(reason_key, "The setup was filtered out by system controls.")

    return f"{base} {detail}"


def build_rejection_analysis(trade, reason_key, machine_reason=None):
    symbol = trade.get("symbol", "This setup")
    score = trade.get("score", "N/A")
    confidence = trade.get("confidence", "N/A")
    mode = trade.get("mode", "UNKNOWN")
    breadth = trade.get("breadth", "UNKNOWN")
    volatility = trade.get("volatility_state", "UNKNOWN")

    lines = [
        f"{symbol} came through the engine with a score of {score} and {str(confidence).lower()} confidence.",
        f"The system was operating in {str(mode).replace('_', ' ').title()} mode with {str(breadth).lower()} breadth and {str(volatility).lower()} volatility conditions.",
    ]

    if reason_key == "breadth_blocked":
        lines.append("The broader market participation profile did not support the direction required for this setup.")

    elif reason_key == "mode_blocked":
        lines.append("The market environment forced a more defensive posture, and this setup did not fit that posture.")

    elif reason_key == "execution_blocked":
        lines.append("The structure may have been acceptable, but capital, risk, or execution controls prevented deployment.")

    elif reason_key == "score_too_low":
        lines.append("The setup did not clear the internal quality bar needed to compete for capital.")

    elif reason_key == "volatility_blocked":
        lines.append("Volatility conditions made the setup too unstable relative to its conviction level.")

    elif reason_key == "weak_option_contract":
        lines.append("The underlying idea was not matched by an efficient or liquid enough option contract.")

    elif reason_key == "reentry_blocked":
        lines.append("The symbol was recently exited, and the system requires materially better re-entry conditions before trying again.")

    elif reason_key == "not_selected":
        lines.append("The setup passed baseline checks, but stronger competing opportunities were prioritized instead.")
        stronger = trade.get("stronger_competing_setups", [])
        if stronger:
            lead = stronger[0]
            lines.append(
                f"The leading competing setup was {lead.get('symbol', 'UNKNOWN')} "
                f"{lead.get('strategy', 'N/A')} with a score of {lead.get('score', 'N/A')}."
            )

    else:
        lines.append("The setup was filtered out by system-level controls before execution.")

    if machine_reason:
        machine_text = str(machine_reason).replace("_", " ")
        lines.append(f"Internal trigger: {machine_text}.")

    return lines


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


def explain_reentry_detail(detail_string):
    mapping = {
        "score_not_improved_enough": "score has not improved enough",
        "confidence_not_improved": "confidence has not strengthened",
        "price_not_reclaimed": "price has not reclaimed strength",
        "trend_not_supportive": "trend does not support the trade direction",
    }

    parts = str(detail_string).split(",")
    translated = [mapping.get(p.strip(), p.strip().replace("_", " ")) for p in parts if p.strip()]

    if not translated:
        return ""

    if len(translated) == 1:
        return translated[0]

    return ", ".join(translated[:-1]) + " and " + translated[-1]


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
