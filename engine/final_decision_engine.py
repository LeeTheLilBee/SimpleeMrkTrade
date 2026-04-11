"""
FINAL DECISION ENGINE
Calibrated for:
- strong continuation grace
- medium rebuild tolerance
- confidence alignment with real structure
- support for both nested gates and flat gate fields
"""

from typing import Dict, Any


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def _safe_str(x, default=""):
    try:
        return str(x)
    except Exception:
        return default


def _resolve_gates(context: Dict[str, Any]) -> Dict[str, bool]:
    context = context if isinstance(context, dict) else {}
    nested_gates = context.get("gates", {}) if isinstance(context.get("gates", {}), dict) else {}

    readiness_gate = bool(
        context.get("readiness_gate_passed", nested_gates.get("readiness", False))
    )
    promotion_gate = bool(
        context.get("promotion_gate_passed", nested_gates.get("promotion", False))
    )
    rebuild_gate = bool(
        context.get("rebuild_gate_passed", nested_gates.get("rebuild", False))
    )

    return {
        "readiness": readiness_gate,
        "promotion": promotion_gate,
        "rebuild": rebuild_gate,
    }


def calibrate_decision_confidence(context: Dict[str, Any]) -> str:
    readiness = _safe_float(context.get("readiness_score", 0))
    promotion = _safe_float(context.get("promotion_score", 0))
    rebuild = _safe_float(context.get("rebuild_pressure", 0))
    execution = _safe_float(context.get("execution_quality", 0))
    setup_family = _safe_str(context.get("setup_family", "unknown")).strip().lower()

    gates = _resolve_gates(context)
    readiness_ok = gates["readiness"]
    promotion_ok = gates["promotion"]
    rebuild_ok = gates["rebuild"]

    if (
        readiness >= 205
        and promotion >= 185
        and rebuild <= 5
        and execution >= 220
        and readiness_ok
        and promotion_ok
        and rebuild_ok
    ):
        return "HIGH"

    if (
        setup_family == "continuation"
        and readiness >= 200
        and promotion >= 120
        and rebuild <= 20
        and execution >= 225
        and readiness_ok
        and promotion_ok
        and rebuild_ok
    ):
        return "MEDIUM"

    if (
        readiness >= 170
        and promotion >= 120
        and rebuild <= 22
        and execution >= 200
        and readiness_ok
        and promotion_ok
        and rebuild_ok
    ):
        return "MEDIUM"

    if readiness >= 200 and execution >= 210 and readiness_ok and rebuild_ok:
        return "MEDIUM"

    return "LOW"


def build_final_decision(context: Dict[str, Any]) -> Dict[str, Any]:
    context = context if isinstance(context, dict) else {}

    symbol = context.get("symbol")
    eligible = bool(context.get("eligible", False))
    rebuild = _safe_float(context.get("rebuild_pressure", 0))
    readiness = _safe_float(context.get("readiness_score", 0))
    promotion = _safe_float(context.get("promotion_score", 0))
    execution = _safe_float(context.get("execution_quality", 0))
    setup_family = _safe_str(context.get("setup_family", "unknown")).strip().lower()
    calibrated_signal_confidence = _safe_str(context.get("confidence", "LOW")).upper().strip()

    decision_confidence = calibrate_decision_confidence(context)

    if not eligible:
        return {
            "symbol": symbol,
            "final_verdict": "BLOCK",
            "decision_reason": "Setup failed eligibility gates.",
            "decision_confidence": "LOW",
        }

    if rebuild >= 30:
        return {
            "symbol": symbol,
            "final_verdict": "BLOCK",
            "decision_reason": "Rebuild pressure too high.",
            "decision_confidence": "LOW",
        }

    if decision_confidence == "HIGH" and calibrated_signal_confidence == "HIGH":
        return {
            "symbol": symbol,
            "final_verdict": "TAKE",
            "decision_reason": "High execution quality with strong setup",
            "decision_confidence": "HIGH",
        }

    if (
        setup_family == "continuation"
        and decision_confidence == "MEDIUM"
        and readiness >= 200
        and promotion >= 120
        and rebuild <= 20
        and execution >= 225
    ):
        return {
            "symbol": symbol,
            "final_verdict": "WATCH",
            "decision_reason": "Strong continuation setup with pressure still needing respect",
            "decision_confidence": "MEDIUM",
        }

    if calibrated_signal_confidence == "LOW" and decision_confidence == "LOW":
        return {
            "symbol": symbol,
            "final_verdict": "WATCH",
            "decision_reason": "Insufficient alignment across engine layers",
            "decision_confidence": "LOW",
        }

    if decision_confidence in {"HIGH", "MEDIUM"} or calibrated_signal_confidence == "MEDIUM":
        return {
            "symbol": symbol,
            "final_verdict": "WATCH",
            "decision_reason": "Setup is valid but not strong enough for immediate entry",
            "decision_confidence": "MEDIUM",
        }

    return {
        "symbol": symbol,
        "final_verdict": "WATCH",
        "decision_reason": "Insufficient alignment across engine layers",
        "decision_confidence": "LOW",
    }
