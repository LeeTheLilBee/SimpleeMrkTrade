from typing import Dict


def build_memory_takeaway(final_brain: Dict) -> Dict:
    final_narrative = final_brain.get("final_narrative", {}) if isinstance(final_brain, dict) else {}
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}

    action = str(final_summary.get("action", "wait") or "wait")
    story = str(final_narrative.get("merged_story", "") or "").lower()

    takeaway = "No strong memory takeaway was produced."

    if action == "reject" and "timing degraded" in story:
        takeaway = "A trade can be directionally right and still deserve rejection if timing and truth collapse."
    elif action == "reject":
        takeaway = "Do not confuse surface strength with real trust."
    elif action == "wait":
        takeaway = "Patience can preserve edge better than forced execution."
    elif action in {"act", "cautious_act"}:
        takeaway = "When alignment survives every layer, disciplined action is justified."

    return {
        "memory_takeaway": takeaway
    }
