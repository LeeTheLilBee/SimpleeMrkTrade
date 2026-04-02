from typing import Dict, List


def evaluate_signal_quality(decisions: List[Dict]) -> Dict:
    valid = [d for d in decisions if isinstance(d, dict)]
    ready_now = [d for d in valid if d.get("ready_state") == "ready_now"]
    rejects = [d for d in valid if d.get("ready_state") == "reject"]

    total = len(valid)

    if total == 0:
        return {
            "signal_quality_state": "unknown",
            "signal_quality_reason": "no decisions available",
        }

    ready_ratio = len(ready_now) / total
    reject_ratio = len(rejects) / total

    if ready_ratio >= 0.25 and reject_ratio <= 0.4:
        state = "sharp"
        reason = "signal board contains a healthy concentration of actionable ideas"
    elif ready_ratio >= 0.15:
        state = "crowded"
        reason = "board has opportunities, but quality is becoming compressed"
    elif reject_ratio >= 0.7:
        state = "thin"
        reason = "very few ideas are clearing thresholds"
    else:
        state = "noisy"
        reason = "signal flow is active, but actionable quality is not concentrated"

    return {
        "signal_quality_state": state,
        "signal_quality_reason": reason,
        "ready_ratio": round(ready_ratio, 4),
        "reject_ratio": round(reject_ratio, 4),
    }
