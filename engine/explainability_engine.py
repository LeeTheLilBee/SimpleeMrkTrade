"""
EXPLAINABILITY ENGINE
Modern explainability layer for the live engine stack.

This module builds:
- structured reasoning
- rejection explanations
- normalized explainability objects
for signals, trades, and positions.
"""

from typing import Any, Dict, List


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _safe_str(x: Any, default: str = "") -> str:
    try:
        return str(x)
    except Exception:
        return default


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _safe_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _normalize_verdict(payload: Dict[str, Any]) -> str:
    final_decision = _safe_dict(payload.get("final_decision", {}))
    canonical = _safe_dict(payload.get("canonical_decision", {}))

    verdict = _safe_str(payload.get("final_verdict", "")).strip().upper()
    if verdict:
        return verdict

    verdict = _safe_str(final_decision.get("final_verdict", "")).strip().upper()
    if verdict:
        return verdict

    verdict = _safe_str(canonical.get("final_verdict", "")).strip().upper()
    if verdict:
        return verdict

    return "WATCH"


def _normalize_confidence(payload: Dict[str, Any]) -> str:
    final_decision = _safe_dict(payload.get("final_decision", {}))
    canonical = _safe_dict(payload.get("canonical_decision", {}))

    confidence = _safe_str(final_decision.get("decision_confidence", "")).strip().upper()
    if confidence in {"HIGH", "MEDIUM", "LOW"}:
        return confidence

    confidence = _safe_str(canonical.get("decision_confidence", "")).strip().upper()
    if confidence in {"HIGH", "MEDIUM", "LOW"}:
        return confidence

    confidence = _safe_str(payload.get("confidence", "")).strip().upper()
    if confidence in {"HIGH", "MEDIUM", "LOW"}:
        return confidence

    return "LOW"

def _resolve_gates(payload: Dict[str, Any]) -> Dict[str, bool]:
    payload = payload if isinstance(payload, dict) else {}
    nested_gates = _safe_dict(payload.get("gates", {}))

    return {
        "readiness": bool(payload.get("readiness_gate_passed", nested_gates.get("readiness", False))),
        "promotion": bool(payload.get("promotion_gate_passed", nested_gates.get("promotion", False))),
        "rebuild": bool(payload.get("rebuild_gate_passed", nested_gates.get("rebuild", False))),
    }


def explain_trade_decision(
    trade: Dict[str, Any],
    mode: Any = None,
    regime: Any = None,
    breadth: Any = None,
    volatility: Any = None,
) -> List[str]:
    trade = trade if isinstance(trade, dict) else {}

    reasons: List[str] = []

    symbol = _safe_str(trade.get("symbol", "This setup")).strip() or "This setup"
    verdict = _normalize_verdict(trade)
    confidence = _normalize_confidence(trade)

    readiness = _safe_float(trade.get("readiness_score", 0))
    promotion = _safe_float(trade.get("promotion_score", 0))
    rebuild = _safe_float(trade.get("rebuild_pressure", 0))
    execution = _safe_float(trade.get("execution_quality", 0))

    setup_family = _safe_str(trade.get("setup_family", "unknown")).strip().lower()
    entry_quality = _safe_str(trade.get("entry_quality", "unknown")).strip().lower()

    gates = _resolve_gates(trade)

    reasons.append(f"{symbol} is currently a {verdict} with {confidence.lower()} confidence.")

    if readiness >= 205:
        reasons.append("Readiness is elite and the structure is strong.")
    elif readiness >= 180:
        reasons.append("Readiness is strong enough to respect.")
    elif readiness >= 140:
        reasons.append("Readiness is developing but not elite.")
    else:
        reasons.append("Readiness is still too weak to trust aggressively.")

    if promotion >= 185:
        reasons.append("Promotion quality is strong enough to support action.")
    elif promotion >= 120:
        reasons.append("Promotion is valid, but it is not fully mature yet.")
    else:
        reasons.append("Promotion quality is still too soft for immediate trust.")

    if rebuild >= 25:
        reasons.append("Rebuild pressure is high and materially reduces trust.")
    elif rebuild >= 18:
        reasons.append("Rebuild pressure is meaningful and still needs respect.")
    elif rebuild >= 10:
        reasons.append("Rebuild pressure is present but manageable.")
    else:
        reasons.append("Rebuild pressure is low enough not to dominate the setup.")

    if execution >= 225:
        reasons.append("Execution quality is elite.")
    elif execution >= 205:
        reasons.append("Execution quality is strong.")
    elif execution >= 190:
        reasons.append("Execution quality is decent but not exceptional.")
    else:
        reasons.append("Execution quality is not strong enough to rescue a weak setup.")

    if setup_family and setup_family != "unknown":
        reasons.append(f"Setup family is {setup_family}.")
    if entry_quality and entry_quality != "unknown":
        reasons.append(f"Entry quality is {entry_quality}.")

    if gates["readiness"] and gates["promotion"] and gates["rebuild"]:
        reasons.append("All three core gates are currently passing.")
    else:
        failed = []
        if not gates["readiness"]:
            failed.append("readiness")
        if not gates["promotion"]:
            failed.append("promotion")
        if not gates["rebuild"]:
            failed.append("rebuild")
        if failed:
            reasons.append(f"Failed gates: {', '.join(failed)}.")

    if mode:
        reasons.append(f"Market mode at decision time: {mode}.")
    if regime:
        reasons.append(f"Broader regime context: {regime}.")
    if breadth:
        reasons.append(f"Market breadth context: {breadth}.")
    if volatility:
        reasons.append(f"Volatility state: {volatility}.")

    return reasons


def explain_rejection(trade: Dict[str, Any], reason_key: str) -> str:
    symbol = _safe_str(trade.get("symbol", "This setup")).strip() or "This setup"

    base = f"{symbol} was not taken."

    mapping = {
        "breadth_blocked": "Market participation did not support the direction of this setup.",
        "mode_blocked": "Current market mode did not support this structure.",
        "execution_blocked": "Execution controls prevented entry despite the setup conditions.",
        "score_too_low": "The setup did not meet the internal quality threshold required for deployment.",
        "volatility_blocked": "Volatility conditions reduced trust below acceptable levels.",
        "weak_option_contract": "No suitable contract provided efficient exposure for this idea.",
        "reentry_blocked": "The system requires stronger confirmation before re-entering this symbol.",
        "not_selected": "The setup passed filters but ranked below stronger opportunities.",
        "failed_readiness_gate": "Readiness was not strong enough.",
        "failed_promotion_gate": "Promotion quality was not strong enough.",
        "failed_rebuild_gate": "Rebuild pressure was too high.",
        "high_rebuild_pressure": "Repair burden was too heavy to justify action.",
    }

    detail = mapping.get(reason_key, "The setup was filtered out by system controls.")
    return f"{base} {detail}"


def build_rejection_analysis(
    trade: Dict[str, Any],
    reason_key: str,
    machine_reason: Any = None,
) -> List[str]:
    trade = trade if isinstance(trade, dict) else {}

    symbol = _safe_str(trade.get("symbol", "This setup")).strip() or "This setup"
    readiness = _safe_float(trade.get("readiness_score", 0))
    promotion = _safe_float(trade.get("promotion_score", 0))
    rebuild = _safe_float(trade.get("rebuild_pressure", 0))
    execution = _safe_float(trade.get("execution_quality", 0))
    confidence = _normalize_confidence(trade)

    lines = [
        f"{symbol} came through the engine with {confidence.lower()} confidence.",
        f"Readiness was {readiness}, promotion was {promotion}, rebuild pressure was {rebuild}, and execution quality was {execution}.",
        explain_rejection(trade, reason_key),
    ]

    if machine_reason:
        lines.append(f"System reason: {machine_reason}")

    return lines


def build_explainability_object(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}

    symbol = _safe_str(payload.get("symbol", "")).strip().upper()
    verdict = _normalize_verdict(payload)
    confidence = _normalize_confidence(payload)

    readiness = _safe_float(payload.get("readiness_score", 0))
    promotion = _safe_float(payload.get("promotion_score", 0))
    rebuild = _safe_float(payload.get("rebuild_pressure", 0))
    execution = _safe_float(payload.get("execution_quality", 0))
    setup_family = _safe_str(payload.get("setup_family", "unknown")).strip().lower()
    entry_quality = _safe_str(payload.get("entry_quality", "unknown")).strip().lower()

    gates = _resolve_gates(payload)

    supports: List[str] = []
    blockers: List[str] = []
    pressures: List[str] = []
    improvements: List[str] = []

    if gates["readiness"]:
        supports.append("readiness gate passed")
    else:
        blockers.append("readiness gate failed")

    if gates["promotion"]:
        supports.append("promotion gate passed")
    else:
        blockers.append("promotion gate failed")

    if gates["rebuild"]:
        supports.append("rebuild gate passed")
    else:
        blockers.append("rebuild gate failed")

    if readiness >= 205:
        supports.append("elite readiness")
    elif readiness >= 180:
        supports.append("strong readiness")
    elif readiness < 115:
        blockers.append("weak readiness")

    if promotion >= 185:
        supports.append("elite promotion")
    elif promotion >= 120:
        supports.append("valid promotion")
    elif promotion < 95:
        blockers.append("weak promotion")

    if execution >= 225:
        supports.append("elite execution quality")
    elif execution >= 205:
        supports.append("strong execution quality")
    elif execution < 180:
        blockers.append("weak execution quality")

    if rebuild >= 25:
        pressures.append("rebuild pressure is high")
        blockers.append("repair burden is too heavy")
    elif rebuild >= 18:
        pressures.append("rebuild pressure is meaningful")
    elif rebuild >= 10:
        pressures.append("rebuild pressure is present")
    else:
        supports.append("clean rebuild profile")

    if setup_family == "continuation":
        supports.append("continuation setups are structurally favored")
    elif setup_family == "breakout":
        supports.append("breakout structure can be strong when clean")
    elif setup_family == "pullback":
        pressures.append("pullbacks need cleaner confirmation")
    elif setup_family == "unknown":
        pressures.append("setup family is not fully classified")

    if entry_quality == "high_conviction":
        supports.append("entry quality is strong")
    elif entry_quality == "acceptable":
        pressures.append("entry quality is only acceptable")
    elif entry_quality == "weak":
        blockers.append("entry quality is weak")

    if confidence == "LOW":
        blockers.append("confidence is too low for aggressive trust")
        improvements.append("confidence needs to recover before aggressive action makes sense")
    elif confidence == "MEDIUM":
        improvements.append("the setup needs more proof before immediate entry")
    elif confidence == "HIGH":
        supports.append("confidence is high enough to consider action")

    if rebuild >= 10:
        improvements.append("rebuild pressure needs to come down before trust can expand")

    if promotion < 145 and verdict != "BLOCK":
        improvements.append("promotion quality needs to strengthen before immediate entry makes sense")

    if not improvements:
        improvements.append("keep execution clean and do not get sloppy managing the trade")

    if verdict == "TAKE":
        headline = f"{symbol} is approved." if symbol else "This setup is approved."
        summary = "The setup is aligned strongly enough for action."
    elif verdict == "BLOCK":
        headline = f"{symbol} is blocked." if symbol else "This setup is blocked."
        summary = "The engine does not believe this setup is safe enough to act on."
    else:
        headline = f"{symbol} needs more proof." if symbol else "This setup needs more proof."
        if setup_family == "continuation" and confidence == "MEDIUM" and rebuild >= 18:
            summary = "This is a strong continuation setup, but the pressure underneath still needs respect."
        elif confidence == "LOW":
            summary = "The setup has some pieces, but trust is too weak right now."
        else:
            summary = "The setup is credible, but it still needs more proof before immediate entry."

    return {
        "symbol": symbol,
        "headline": headline,
        "summary": summary,
        "verdict": verdict,
        "confidence": confidence,
        "supports": list(dict.fromkeys(supports)),
        "blockers": list(dict.fromkeys(blockers)),
        "pressures": list(dict.fromkeys(pressures)),
        "improvements": list(dict.fromkeys(improvements)),
        "readiness_score": readiness,
        "promotion_score": promotion,
        "rebuild_pressure": rebuild,
        "execution_quality": execution,
        "setup_family": setup_family,
        "entry_quality": entry_quality,
        "gates": gates,
        "reasons": explain_trade_decision(payload),
    }


def build_signal_explainability(signal: Dict[str, Any]) -> Dict[str, Any]:
    return build_explainability_object(signal)


def build_trade_explainability(trade: Dict[str, Any]) -> Dict[str, Any]:
    explainability = build_explainability_object(trade)

    pnl = _safe_float(trade.get("pnl", 0.0))
    outcome = _safe_str(trade.get("outcome", "")).strip().lower()

    if not outcome:
        if pnl > 0:
            outcome = "win"
        elif pnl < 0:
            outcome = "loss"
        else:
            outcome = "flat"

    explainability["trade_outcome"] = outcome
    explainability["pnl"] = pnl

    if outcome == "win":
        explainability["summary"] = "The trade followed through well enough to validate the decision."
    elif outcome == "loss":
        explainability["summary"] = "The trade failed to hold together well enough, so the engine should treat it as learning."
    elif outcome == "flat":
        explainability["summary"] = "The trade did not create enough edge to matter, which still teaches the engine something."

    return explainability


def build_position_explainability(position: Dict[str, Any]) -> Dict[str, Any]:
    explainability = build_explainability_object(position)

    timing_phase = _safe_str(position.get("timing_phase", "")).strip().lower()
    if timing_phase:
        explainability["timing_phase"] = timing_phase

    if timing_phase == "too_early_to_cut":
        explainability["summary"] = "The position is under pressure, but the engine still believes it is too early to abandon it."
    elif timing_phase == "late":
        explainability["summary"] = "The position is late enough that discipline around exits matters more now."
    elif timing_phase == "hold_zone":
        explainability["summary"] = "The position is still inside a normal hold-and-monitor zone."

    return explainability
