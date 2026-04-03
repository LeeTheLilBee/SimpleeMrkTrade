from typing import Dict


def gate_summary_by_policy(summary: Dict, policy: Dict) -> Dict:
    gated = dict(summary)

    if not policy.get("show_score", False):
        gated["score"] = None

    if not policy.get("show_grade", False):
        gated["grade"] = None

    if not policy.get("show_confidence", True):
        gated["confidence"] = None

    reasons = gated.get("reasons", []) or []
    gated["reasons"] = reasons[: int(policy.get("show_reasons_count", 1))]

    return gated
