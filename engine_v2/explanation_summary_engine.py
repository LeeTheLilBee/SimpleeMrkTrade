from typing import Dict


def build_explanation_summary(final_brain: Dict) -> Dict:
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}

    action = str(final_summary.get("action", "wait") or "wait")
    confidence = str(final_summary.get("confidence", "low") or "low")
    verdict = str(final_summary.get("verdict", "No verdict available.") or "No verdict available.")
    insight = str(final_summary.get("insight", "No insight available.") or "No insight available.")
    story = str(final_summary.get("story", "") or "")

    summary_line = f"{verdict} {insight}".strip()

    if not summary_line:
        summary_line = "No final explanation available."

    return {
        "explanation_action": action,
        "explanation_confidence": confidence,
        "explanation_verdict": verdict,
        "explanation_insight": insight,
        "explanation_story": story,
        "explanation_summary_line": summary_line,
    }
