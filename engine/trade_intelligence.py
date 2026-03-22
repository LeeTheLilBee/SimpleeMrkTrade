"""
===========================================================
TRADE INTELLIGENCE ENGINE
-----------------------------------------------------------
Unified intelligence object for:
- signals
- positions
- proof
- future options / decision trace layers

This engine is designed to answer:
- what is happening
- what is changing
- what matters next
- what would weaken or invalidate the setup
===========================================================
"""

from math import fabs


def _clamp(value, low=0, high=100):
    return max(low, min(high, int(round(value))))


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _infer_phase(score, time_in_trade, pnl_pct):
    if time_in_trade <= 1:
        return "Forming"
    if pnl_pct > 4 and score >= 70:
        return "Developing"
    if pnl_pct > 8:
        return "Extended"
    if score < 45:
        return "Under Pressure"
    return "Active"


def _infer_direction(current_score, previous_score):
    if previous_score is None:
        return "Stable"
    delta = current_score - previous_score
    if delta >= 8:
        return "Improving"
    if delta <= -8:
        return "Deteriorating"
    return "Stable"


def _infer_thesis_type(position):
    setup_type = (position.get("setup_type") or "").strip()
    if setup_type:
        return setup_type.title()

    thesis = (position.get("thesis_type") or "").strip()
    if thesis:
        return thesis.title()

    return "Continuation"


def _infer_thesis_status(score, pnl_pct, distance_to_stop_pct):
    if score >= 75 and pnl_pct >= 0:
        return "Intact"
    if score >= 60 and distance_to_stop_pct > 3:
        return "Slightly Weakening"
    if score >= 45:
        return "Weakening"
    if score >= 30:
        return "Breaking"
    return "Invalidated"


def _thesis_summary(thesis_type, thesis_status, trend_score, momentum_score):
    if thesis_status == "Intact":
        return f"The {thesis_type.lower()} thesis remains intact with supportive structure and usable follow-through."
    if thesis_status == "Slightly Weakening":
        return f"The {thesis_type.lower()} thesis is still alive, but early pressure is beginning to show."
    if thesis_status == "Weakening":
        return f"The {thesis_type.lower()} thesis is weakening as the setup loses some internal quality."
    if thesis_status == "Breaking":
        return f"The {thesis_type.lower()} thesis is breaking as trend and momentum support are deteriorating."
    return f"The {thesis_type.lower()} thesis is no longer behaving as expected and should be treated as invalidated."


def _action_bias(score, thesis_status, direction):
    if score >= 82 and direction == "Improving":
        return "Stay constructive, but keep discipline."
    if score >= 68:
        return "Hold and monitor closely."
    if score >= 55:
        return "Stay cautious and reduce complacency."
    if score >= 40:
        return "Risk is rising. Consider reducing exposure."
    return "Conditions are deteriorating. Strongly consider defensive action."


def _forward_paths(thesis_type, trend_score, momentum_score, volatility_score):
    primary = "Continuation higher if structure holds."
    secondary = "Range compression if momentum stalls."

    if thesis_type.lower() == "breakout":
        primary = "Breakout continuation if price holds above the trigger zone."
        secondary = "False-break consolidation if momentum fades."
    elif thesis_type.lower() == "pullback":
        primary = "Recovery continuation if buyers defend support."
        secondary = "Deeper pullback if support weakens."
    elif thesis_type.lower() == "reversal":
        primary = "Reversal follow-through if momentum keeps improving."
        secondary = "Failure back into prior trend if support is lost."
    elif thesis_type.lower() == "range":
        primary = "Mean reversion inside the range if conditions stay calm."
        secondary = "Range break if volatility expands."

    if volatility_score < 40:
        secondary = "Volatility expansion risk is rising if the market loses balance."

    return [primary, secondary]


def _invalidation_map(position, stop, current_price):
    key_support = position.get("key_support") or stop
    trigger = position.get("trigger_level") or None

    text = f"Loss of support near {round(_safe_float(key_support, stop), 2)} would materially weaken the setup."
    if trigger is not None:
        text += f" Failure to reclaim {round(_safe_float(trigger), 2)} would further reduce conviction."
    return text


def _top_damage_reasons(
    price_score,
    trend_score,
    momentum_score,
    volatility_score,
    signal_score,
    time_score,
    distance_to_stop_pct,
    confidence_delta,
):
    reasons = []

    if distance_to_stop_pct < 3:
        reasons.append("Price is approaching the stop zone.")
    if trend_score < 50:
        reasons.append("Trend structure is weakening.")
    if momentum_score < 50:
        reasons.append("Momentum is fading.")
    if volatility_score < 45:
        reasons.append("Volatility conditions are becoming less favorable.")
    if signal_score < 50:
        reasons.append("Signal quality is deteriorating.")
    if confidence_delta < -10:
        reasons.append("Confidence has dropped meaningfully since entry.")
    if time_score < 50:
        reasons.append("The trade is taking longer than expected to work.")

    if not reasons:
        reasons.append("No major damage signals are dominating right now.")

    return reasons[:3]


def _what_changed(current_score, previous_score, confidence_delta, volatility_score, trend_score):
    changes = []

    if previous_score is not None:
        delta = current_score - previous_score
        if delta >= 8:
            changes.append("Overall trade quality improved since the last check.")
        elif delta <= -8:
            changes.append("Overall trade quality deteriorated since the last check.")

    if confidence_delta >= 8:
        changes.append("Confidence improved versus entry conditions.")
    elif confidence_delta <= -8:
        changes.append("Confidence has declined versus entry conditions.")

    if volatility_score < 45:
        changes.append("Volatility pressure increased.")
    if trend_score < 50:
        changes.append("Trend support weakened.")

    if not changes:
        changes.append("No major change signals stand out since the last evaluation.")

    return changes[:3]


def build_trade_intelligence(position):
    """
    Build a single structured intelligence object.

    Expected optional fields on position:
    - entry
    - current_price
    - stop
    - target
    - score
    - previous_score
    - confidence_entry
    - confidence_now
    - time_in_trade
    - setup_type / thesis_type
    - key_support
    - trigger_level
    """

    entry = _safe_float(position.get("entry"), 0)
    current_price = _safe_float(position.get("current_price"), entry)
    stop = _safe_float(position.get("stop"), entry * 0.95 if entry else 0)
    target = _safe_float(position.get("target"), entry * 1.10 if entry else 0)
    score = _safe_float(position.get("score"), 50)
    previous_score = position.get("previous_score")
    previous_score = None if previous_score is None else _safe_float(previous_score, score)
    confidence_entry = _safe_float(position.get("confidence_entry"), 70)
    confidence_now = _safe_float(position.get("confidence_now"), score)
    time_in_trade = int(_safe_float(position.get("time_in_trade"), 1))

    pnl_pct = 0.0
    if entry:
        pnl_pct = ((current_price - entry) / entry) * 100.0

    distance_to_stop_pct = 999.0
    if current_price:
        distance_to_stop_pct = fabs((current_price - stop) / current_price) * 100.0

    distance_to_target_pct = 999.0
    if current_price and target:
        distance_to_target_pct = fabs((target - current_price) / current_price) * 100.0

    confidence_delta = confidence_now - confidence_entry

    # Multi-factor sub-scores
    price_score = 80
    if pnl_pct < 0:
        price_score -= 18
    if distance_to_stop_pct < 2:
        price_score -= 32
    elif distance_to_stop_pct < 5:
        price_score -= 16
    if distance_to_target_pct < 2 and pnl_pct > 5:
        price_score -= 6  # upside getting more limited

    trend_score = 75
    if score < 60:
        trend_score -= 20
    if pnl_pct < -2:
        trend_score -= 12
    if previous_score is not None and score < previous_score:
        trend_score -= 8

    momentum_score = 72
    if confidence_delta < 0:
        momentum_score -= min(22, abs(int(confidence_delta)))
    if pnl_pct < 0:
        momentum_score -= 10

    volatility_score = 68
    if distance_to_stop_pct < 3:
        volatility_score -= 18
    if time_in_trade > 5 and pnl_pct < 2:
        volatility_score -= 10

    signal_score = _clamp(confidence_now)
    time_score = _clamp(82 - (time_in_trade * 6))

    price_score = _clamp(price_score)
    trend_score = _clamp(trend_score)
    momentum_score = _clamp(momentum_score)
    volatility_score = _clamp(volatility_score)

    composite_score = _clamp(
        (price_score * 0.20)
        + (trend_score * 0.18)
        + (momentum_score * 0.15)
        + (volatility_score * 0.10)
        + (signal_score * 0.20)
        + (time_score * 0.17)
    )

    if composite_score >= 85:
        status = "Strong"
    elif composite_score >= 70:
        status = "Healthy"
    elif composite_score >= 55:
        status = "Caution"
    elif composite_score >= 40:
        status = "At Risk"
    else:
        status = "Critical"

    thesis_type = _infer_thesis_type(position)
    thesis_status = _infer_thesis_status(composite_score, pnl_pct, distance_to_stop_pct)
    direction = _infer_direction(composite_score, previous_score)
    phase = _infer_phase(composite_score, time_in_trade, pnl_pct)
    opportunity_score = _clamp(100 - distance_to_target_pct * 3 if distance_to_target_pct != 999 else 50)

    return {
        "snapshot": {
            "score": composite_score,
            "status": status,
            "direction": direction,
            "phase": phase,
        },
        "thesis": {
            "type": thesis_type,
            "status": thesis_status,
            "summary": _thesis_summary(thesis_type, thesis_status, trend_score, momentum_score),
        },
        "pressure_map": {
            "price": price_score,
            "trend": trend_score,
            "momentum": momentum_score,
            "volatility": volatility_score,
            "signal": signal_score,
            "time": time_score,
        },
        "damage_report": _top_damage_reasons(
            price_score=price_score,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
            signal_score=signal_score,
            time_score=time_score,
            distance_to_stop_pct=distance_to_stop_pct,
            confidence_delta=confidence_delta,
        ),
        "forward_paths": _forward_paths(
            thesis_type=thesis_type,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
        ),
        "invalidation_map": _invalidation_map(position, stop, current_price),
        "opportunity_score": opportunity_score,
        "action_bias": _action_bias(composite_score, thesis_status, direction),
        "what_changed": _what_changed(
            current_score=composite_score,
            previous_score=previous_score,
            confidence_delta=confidence_delta,
            volatility_score=volatility_score,
            trend_score=trend_score,
        ),
        "meta": {
            "entry": entry,
            "current_price": current_price,
            "stop": stop,
            "target": target,
            "pnl_pct": round(pnl_pct, 2),
            "distance_to_stop_pct": round(distance_to_stop_pct, 2) if distance_to_stop_pct != 999 else None,
            "distance_to_target_pct": round(distance_to_target_pct, 2) if distance_to_target_pct != 999 else None,
            "confidence_entry": round(confidence_entry, 2),
            "confidence_now": round(confidence_now, 2),
            "confidence_delta": round(confidence_delta, 2),
            "time_in_trade": time_in_trade,
        },
    }


def attach_trade_intelligence(positions):
    """
    Bulk helper for lists of position-like dicts.
    """
    enriched = []
    for position in positions:
        p = dict(position)
        p["intelligence"] = build_trade_intelligence(p)
        enriched.append(p)
    return enriched
