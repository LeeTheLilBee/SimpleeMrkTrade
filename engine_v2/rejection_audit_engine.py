from typing import Dict


def audit_rejection(signal: Dict, decision: Dict, future_outcome: Dict) -> Dict:
    rejected = decision.get("ready_state") == "reject"
    outcome = future_outcome.get("outcome")

    if not rejected:
        return {"audit": "not_applicable"}

    if outcome == "win":
        return {
            "audit": "false_rejection",
            "note": "rejected setup later performed well",
        }

    return {
        "audit": "correct_rejection",
        "note": "rejection prevented a poor trade",
    }
