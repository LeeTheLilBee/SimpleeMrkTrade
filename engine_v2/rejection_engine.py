from typing import Any, Dict, List


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def evaluate_rejection(signal: Dict[str, Any], timing: Dict, trap: Dict) -> Dict[str, Any]:
    reasons: List[str] = []

    if trap.get("trap_risk") == "high":
        reasons.append("trap risk too high")

    if timing.get("timing_state") == "too_late":
        reasons.append("move already too extended")

    if _safe_number(signal.get("liquidity_score", 100)) < 40:
        reasons.append("liquidity too weak")

    if _safe_number(signal.get("structure_quality", 100)) < 40:
        reasons.append("structure not worth trading")

    return {
        "rejected": len(reasons) > 0,
        "reject_reasons": reasons,
    }
