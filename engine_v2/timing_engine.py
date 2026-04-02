from typing import Any, Dict


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def evaluate_timing(signal: Dict[str, Any]) -> Dict[str, Any]:
    extension_score = _safe_number(signal.get("extension_score", 0))
    pullback_quality = _safe_number(signal.get("pullback_quality", 0))
    volatility_state = str(signal.get("volatility_state", "normal") or "normal")

    if extension_score > 75:
        timing_state = "too_late"
    elif extension_score > 55:
        timing_state = "extended"
    elif pullback_quality > 60:
        timing_state = "ideal"
    elif pullback_quality > 40:
        timing_state = "ready_soon"
    else:
        timing_state = "early"

    chasing_risk = extension_score > 70 and pullback_quality < 30

    timing_score = max(0.0, min(100.0, 100.0 - extension_score + pullback_quality))

    return {
        "timing_state": timing_state,
        "chasing_risk": chasing_risk,
        "timing_score": round(timing_score, 2),
    }
