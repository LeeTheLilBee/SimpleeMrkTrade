from typing import Dict


def explain_causality(causality: Dict, win_quality: Dict, loss_quality: Dict) -> Dict:
    state = str(causality.get("causality_state", "unclear") or "unclear")
    reason = str(causality.get("causality_reason", "") or "")

    if state == "correct_thesis_correct_execution":
        line = "The trade worked for the right reasons."
    elif state == "correct_thesis_bad_timing":
        line = "The idea may have been right, but the timing degraded it."
    elif state == "bad_thesis":
        line = "The trade failed because the setup itself was not trustworthy."
    elif state == "environment_overpowered_trade":
        line = "The environment was hostile enough to overpower the idea."
    elif state == "lucky_win_under_bad_conditions":
        line = "The trade won, but the win should not be overtrusted."
    else:
        line = "The trade outcome needs a more careful read."

    return {
        "causality_line": line,
        "causality_detail": reason,
        "win_quality": win_quality.get("win_quality"),
        "loss_quality": loss_quality.get("loss_quality"),
    }
