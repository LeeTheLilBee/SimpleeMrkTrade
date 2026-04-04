from typing import Dict, List


def build_pressure_breakdown(final_brain: Dict) -> Dict:
    final_narrative = final_brain.get("final_narrative", {}) if isinstance(final_brain, dict) else {}
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    final_summary = final_output.get("final_summary", {}) if isinstance(final_output, dict) else {}
    truth_notes = final_output.get("truth_notes", {}) if isinstance(final_output.get("truth_notes", {}), dict) else {}

    reasons = list(final_summary.get("reasons", []) or [])
    final_action = str(final_summary.get("action", "wait") or "wait")
    hard_reject = bool(truth_notes.get("hard_reject", False))

    supportive: List[str] = []
    restrictive: List[str] = []

    for item in reasons:
        text = str(item or "").lower()

        if any(word in text for word in ["support", "aligned", "clarity", "edge", "trust", "memory"]):
            supportive.append(str(item))
        else:
            restrictive.append(str(item))

    story = str(final_narrative.get("merged_story", "") or "").lower()

    if "timing degraded" in story:
        restrictive.append("timing degraded the opportunity")
    if "meaningful correction" in story:
        supportive.append("the setup may have been repairable under better conditions")

    def _dedupe(items: List[str]) -> List[str]:
        seen = set()
        out = []
        for item in items:
            if item and item not in seen:
                out.append(item)
                seen.add(item)
        return out

    supportive = _dedupe(supportive)
    restrictive = _dedupe(restrictive)

    support_count = len(supportive)
    restrict_count = len(restrictive)

    if hard_reject:
        balance = "hostile"
    elif final_action == "reject":
        if restrict_count >= support_count:
            balance = "hostile"
        else:
            balance = "mixed"
    elif restrict_count > support_count:
        balance = "hostile"
    elif support_count > restrict_count:
        balance = "supportive"
    else:
        balance = "mixed"

    return {
        "supportive_pressures": supportive,
        "restrictive_pressures": restrictive,
        "pressure_balance": balance,
    }
