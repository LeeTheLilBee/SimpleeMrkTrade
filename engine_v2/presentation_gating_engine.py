from typing import Dict


def gate_presentation_by_policy(payload: Dict, policy: Dict) -> Dict:
    gated = dict(payload)

    highlights = list(gated.get("highlights", []) or [])
    gated["highlights"] = highlights[: int(policy.get("show_highlights_count", 2))]

    if not policy.get("show_narrative", False):
        gated["narrative"] = ""

    if not policy.get("show_system_flags", False):
        gated["system_flags"] = []

    return gated
