from typing import Dict


def evaluate_weak_setup(
    edge_quality: Dict,
    clarity: Dict,
    alignment: Dict,
) -> Dict:
    edge_state = str(edge_quality.get("edge_quality_state", "weak"))
    clarity_state = str(clarity.get("clarity_state", "unclear"))
    alignment_state = str(alignment.get("alignment_state", "partial"))

    suppressed = False
    reason = "setup passes minimum standard"

    if edge_state in {"weak", "marginal"}:
        suppressed = True
        reason = "edge quality is too low"

    elif clarity_state in {"unclear", "murky"} and alignment_state != "aligned":
        suppressed = True
        reason = "setup lacks clarity and alignment"

    return {
        "suppressed": suppressed,
        "suppression_reason": reason,
    }
