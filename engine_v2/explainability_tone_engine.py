from typing import Dict


def build_explainability_tone(final_brain: Dict, explainability: Dict) -> Dict:
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}
    action = str(final_summary.get("action", "wait") or "wait")

    pressure = explainability.get("pressure", {}) if isinstance(explainability, dict) else {}
    balance = str(pressure.get("pressure_balance", "mixed") or "mixed")

    if action == "reject":
        tone = "danger"
    elif action == "wait" and balance == "hostile":
        tone = "caution"
    elif action in {"act", "cautious_act"} and balance == "supportive":
        tone = "conviction"
    elif "repairable" in str(explainability).lower():
        tone = "recovery"
    else:
        tone = "neutral"

    return {
        "explainability_tone": tone
    }
