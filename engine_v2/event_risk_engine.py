from typing import Dict


def evaluate_event_risk(signal: Dict, context: Dict) -> Dict:
    event_type = str(context.get("event_type", "") or "").lower()
    minutes_to_event = float(context.get("minutes_to_event", 99999) or 99999)

    if not event_type:
        return {
            "event_risk_level": "low",
            "event_risk_reason": "no relevant scheduled event detected",
        }

    if minutes_to_event <= 1440:
        level = "high"
        reason = f"major event ({event_type}) is too close to entry timing"
    elif minutes_to_event <= 4320:
        level = "medium"
        reason = f"relevant event ({event_type}) is approaching"
    else:
        level = "low"
        reason = f"event ({event_type}) is not near enough to dominate the setup"

    return {
        "event_risk_level": level,
        "event_risk_reason": reason,
        "event_type": event_type,
        "minutes_to_event": minutes_to_event,
    }
