from typing import Dict


def detect_false_calm(signal: Dict, context: Dict) -> Dict:
    visible_vol = float(signal.get("visible_volatility", 0) or 0)
    hidden_risk = float(context.get("hidden_risk_score", 0) or 0)
    event_proximity = float(context.get("minutes_to_event", 99999) or 99999)

    if visible_vol < 30 and hidden_risk > 65:
        state = "present"
        reason = "quiet price behavior is masking elevated underlying risk"
    elif visible_vol < 35 and event_proximity < 1440:
        state = "present"
        reason = "calm tape may be misleading ahead of a nearby event"
    else:
        state = "absent"
        reason = "no strong false-calm condition detected"

    return {
        "false_calm_state": state,
        "false_calm_reason": reason,
    }
