from typing import Dict

from engine_v2.timing_engine import evaluate_timing
from engine_v2.trap_detection_engine import detect_trap
from engine_v2.rejection_engine import evaluate_rejection
from engine_v2.correlation_engine import assign_correlation
from engine_v2.aggression_engine import determine_aggression


def build_decision(signal: Dict) -> Dict:
    timing = evaluate_timing(signal)
    trap = detect_trap(signal)
    rejection = evaluate_rejection(signal, timing, trap)
    correlation = assign_correlation(signal)

    if rejection["rejected"]:
        ready_state = "reject"
    elif timing["timing_state"] == "ideal":
        ready_state = "ready_now"
    elif timing["timing_state"] == "ready_soon":
        ready_state = "ready_soon"
    else:
        ready_state = "watch"

    decision = {
        "symbol": signal.get("symbol"),
        "ready_state": ready_state,
        "eligible": not rejection["rejected"],
        "timing_score": timing["timing_score"],
        "edge_score": signal.get("score", 0),
        "reject_reasons": rejection["reject_reasons"],
        **correlation,
    }

    decision.update(determine_aggression(decision))

    return decision
