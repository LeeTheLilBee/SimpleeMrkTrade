from typing import Dict, Any


def _safe_str(x: Any, default: str = "") -> str:
    try:
        return str(x)
    except Exception:
        return default


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def build_canonical_decision_object(row: Dict[str, Any]) -> Dict[str, Any]:
    row = row or {}

    final_decision = row.get("final_decision", {}) if isinstance(row.get("final_decision", {}), dict) else {}

    final_verdict = _safe_str(
        final_decision.get("final_verdict", row.get("final_verdict", "WATCH"))
    ).upper().strip() or "WATCH"

    decision_reason = _safe_str(
        final_decision.get("decision_reason", row.get("decision_reason", "No decision reason available."))
    ).strip()

    # CRITICAL FIX:
    # Canonical must inherit the final decision confidence first.
    decision_confidence = _safe_str(
        final_decision.get("decision_confidence", row.get("confidence", "LOW"))
    ).upper().strip() or "LOW"

    readiness_score = _safe_float(row.get("readiness_score", 0))
    promotion_score = _safe_float(row.get("promotion_score", 0))
    rebuild_pressure = _safe_float(row.get("rebuild_pressure", 0))
    execution_quality = _safe_float(row.get("execution_quality", 0))
    eligible = bool(row.get("eligible", False))

    row_gates = row.get("gates", {}) if isinstance(row.get("gates", {}), dict) else {}

    readiness_gate = bool(row.get("readiness_gate_passed", row_gates.get("readiness", False)))
    promotion_gate = bool(row.get("promotion_gate_passed", row_gates.get("promotion", False)))
    rebuild_gate = bool(row.get("rebuild_gate_passed", row_gates.get("rebuild", False)))

    setup_family = _safe_str(row.get("setup_family", "unknown")).strip().lower() or "unknown"
    entry_quality = _safe_str(row.get("entry_quality", "unknown")).strip().lower() or "unknown"

    blockers = []
    supports = []

    if not readiness_gate:
        blockers.append("failed_readiness_gate")
    else:
        supports.append("readiness_gate_passed")

    if not promotion_gate:
        blockers.append("failed_promotion_gate")
    else:
        supports.append("promotion_gate_passed")

    if not rebuild_gate:
        blockers.append("failed_rebuild_gate")
    else:
        supports.append("rebuild_gate_passed")

    if rebuild_pressure >= 25:
        blockers.append("elevated_rebuild_pressure")

    if readiness_score >= 180:
        supports.append("strong_readiness")
    elif readiness_score < 115:
        blockers.append("weak_readiness")

    if promotion_score >= 110:
        supports.append("strong_promotion")
    elif promotion_score < 95:
        blockers.append("weak_promotion")

    if execution_quality >= 210:
        supports.append("strong_execution")
    elif execution_quality < 180:
        blockers.append("weak_execution")

    if final_verdict == "BLOCK":
        allowed_action = "AVOID"
    else:
        allowed_action = final_verdict

    return {
        "symbol": _safe_str(row.get("symbol", "")).upper().strip(),
        "final_verdict": final_verdict,
        "decision_reason": decision_reason,
        "decision_confidence": decision_confidence,
        "allowed_action": allowed_action,
        "eligible": eligible,
        "timing_phase": _safe_str(row.get("timing_phase", "")).strip(),
        "setup_family": setup_family,
        "entry_quality": entry_quality,
        "readiness_score": readiness_score,
        "promotion_score": promotion_score,
        "rebuild_pressure": rebuild_pressure,
        "execution_quality": execution_quality,
        "gates": {
            "readiness": readiness_gate,
            "promotion": promotion_gate,
            "rebuild": rebuild_gate,
        },
        "dominant_blockers": list(dict.fromkeys(blockers)),
        "dominant_supports": list(dict.fromkeys(supports)),
    }
