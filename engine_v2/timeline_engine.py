from typing import Dict


def determine_timeline_phase(signal: Dict, decision: Dict, execution: Dict) -> Dict:
    trend = float(signal.get("trend_strength", 0))
    volume = float(signal.get("volume_confirmation", 0))
    extension = float(signal.get("extension_score", 0))
    entry_state = execution.get("entry_state", "wait")
    ready_state = decision.get("ready_state", "watch")

    phase = "early"
    reason = "setup is forming"

    if ready_state == "reject":
        return {
            "timeline_phase": "broken",
            "timeline_reason": "setup has failed validation",
        }

    if ready_state == "watch":
        phase = "early"
        reason = "conditions are still developing"

    elif ready_state == "ready_soon":
        phase = "building"
        reason = "conditions are improving toward execution"

    elif ready_state == "ready_now":
        if extension > 80:
            phase = "exhausting"
            reason = "move is extended and may be near completion"
        elif entry_state == "clean":
            phase = "ready"
            reason = "optimal entry window is present"
        else:
            phase = "building"
            reason = "setup is valid but entry is not fully optimal"

    if entry_state == "missed":
        phase = "expanding"
        reason = "move is already underway and entry window has passed"

    if trend < 40:
        phase = "broken"
        reason = "trend breakdown invalidates the setup"

    return {
        "timeline_phase": phase,
        "timeline_reason": reason,
    }
