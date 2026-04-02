from typing import Dict


def evaluate_entry_precision(signal: Dict, decision: Dict) -> Dict:
    extension_score = float(signal.get("extension_score", 0) or 0)
    pullback_quality = float(signal.get("pullback_quality", 0) or 0)
    ready_state = str(decision.get("ready_state", "watch") or "watch")

    entry_state = "wait"
    entry_reason = "entry is not ready"
    missed_entry = False

    if ready_state == "reject":
        entry_state = "blocked"
        entry_reason = "setup is rejected"
    elif ready_state == "watch":
        entry_state = "wait"
        entry_reason = "setup is still forming"
    elif ready_state == "ready_soon":
        entry_state = "prepare"
        entry_reason = "setup is improving, but entry is not fully clean"
    elif ready_state == "ready_now":
        if extension_score > 78:
            entry_state = "missed"
            entry_reason = "move is too extended to chase"
            missed_entry = True
        elif pullback_quality >= 60:
            entry_state = "clean"
            entry_reason = "entry quality is favorable"
        else:
            entry_state = "acceptable"
            entry_reason = "setup is valid, but entry is not perfect"

    return {
        "entry_state": entry_state,
        "entry_reason": entry_reason,
        "missed_entry": missed_entry,
    }
