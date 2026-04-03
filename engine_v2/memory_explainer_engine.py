from typing import Dict


def explain_memory_intelligence(memory_intelligence: Dict) -> Dict:
    state = str(memory_intelligence.get("composite_trust_state", "stable") or "stable")
    score = float(memory_intelligence.get("composite_trust_score", 50) or 50)

    if state == "reinforced":
        line = "Recent memory reinforces trust in this setup family."
    elif state == "stable":
        line = "Recent memory is supportive enough to keep trust intact."
    elif state == "fragile":
        line = "Recent memory weakens trust and calls for tighter selectivity."
    else:
        line = "Recent memory does not support normal conviction here."

    return {
        "memory_line": line,
        "memory_state": state,
        "memory_score": score,
    }
