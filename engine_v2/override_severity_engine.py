from typing import Dict


def build_override_severity(explainability: Dict) -> Dict:
    override = explainability.get("override", {}) if isinstance(explainability, dict) else {}
    state = str(override.get("override_state", "none") or "none")

    if state == "hard_reject":
        severity = "severe"
    elif state in {"truth_override", "behavior_override"}:
        severity = "elevated"
    elif state in {"judgment_override"}:
        severity = "light"
    else:
        severity = "none"

    return {
        "override_severity": severity
    }
