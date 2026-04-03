from typing import Dict


def evaluate_late_entry_killer(
    execution: Dict,
    decay: Dict,
    timeline: Dict,
) -> Dict:
    entry_state = str(execution.get("entry_state", "wait") or "wait")
    decay_state = str(decay.get("decay_state", "active") or "active")
    timeline_phase = str(timeline.get("timeline_phase", "early") or "early")

    blocked = False
    reason = "entry timing is still usable"

    if entry_state == "missed":
        blocked = True
        reason = "entry window has already been missed"
    elif decay_state == "expired":
        blocked = True
        reason = "the better version of this opportunity has already passed"
    elif timeline_phase in {"expanding", "exhausting"} and entry_state != "clean":
        blocked = True
        reason = "move is too advanced to justify a new entry"

    return {
        "late_entry_blocked": blocked,
        "late_entry_reason": reason,
    }
