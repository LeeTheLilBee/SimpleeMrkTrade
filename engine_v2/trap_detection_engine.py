from typing import Any, Dict, List


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def detect_trap(signal: Dict[str, Any]) -> Dict[str, Any]:
    volume = _safe_number(signal.get("volume_confirmation", 0))
    trend = _safe_number(signal.get("trend_strength", 0))
    extension = _safe_number(signal.get("extension_score", 0))
    sector = _safe_number(signal.get("sector_alignment", 0))

    trap_risk = "low"
    reasons: List[str] = []

    if extension > 70 and volume < 40:
        trap_risk = "high"
        reasons.append("extended without volume support")

    if trend < 40 and extension > 60:
        trap_risk = "high"
        reasons.append("weak trend on late move")

    if sector < 40 and trap_risk != "high":
        trap_risk = "medium"
        reasons.append("sector not supporting")

    return {
        "trap_risk": trap_risk,
        "trap_reasons": reasons,
    }
