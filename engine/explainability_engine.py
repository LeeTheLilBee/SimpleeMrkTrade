from __future__ import annotations

from typing import Any, Dict, List, Optional


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def _norm_upper(value: Any, default: str = "UNKNOWN") -> str:
    text = _safe_str(value, "").upper()
    return text if text else default


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        text = _safe_str(item, "")
        if text and text not in seen:
            out.append(text)
            seen.add(text)
    return out


def _confidence_bucket(score: float) -> str:
    if score >= 90:
        return "HIGH"
    if score >= 70:
        return "MEDIUM"
    if score >= 50:
        return "LOW"
    return "VERY LOW"


def _readiness_label(readiness_score: float) -> str:
    if readiness_score >= 85:
        return "ready"
    if readiness_score >= 65:
        return "close"
    if readiness_score >= 40:
        return "watch"
    return "weak"


def _pressure_label(rebuild_pressure: float) -> str:
    if rebuild_pressure >= 80:
        return "severe pressure"
    if rebuild_pressure >= 60:
        return "elevated pressure"
    if rebuild_pressure >= 35:
        return "moderate pressure"
    return "contained pressure"


def _execution_label(execution_quality: float) -> str:
    if execution_quality >= 85:
        return "strong execution quality"
    if execution_quality >= 65:
        return "workable execution quality"
    if execution_quality >= 45:
        return "fragile execution quality"
    return "poor execution quality"


def _build_verdict_from_signal(signal: Dict[str, Any]) -> str:
    explicit = _norm_upper(signal.get("final_verdict", signal.get("verdict", "")), "")
    if explicit:
        return explicit

    eligible = bool(signal.get("eligible", False))
    score = _safe_float(signal.get("score", 0))
    readiness_score = _safe_float(signal.get("readiness_score", 0))
    rebuild_pressure = _safe_float(signal.get("rebuild_pressure", 0))

    if not eligible:
        return "BLOCK"
    if readiness_score >= 85 and rebuild_pressure < 45 and score >= 80:
        return "TAKE"
    if readiness_score >= 65 and rebuild_pressure < 65:
        return "WATCH"
    if rebuild_pressure >= 75:
        return "BLOCK"
    return "WAIT"


def _build_reason_from_signal(signal: Dict[str, Any]) -> str:
    explicit = _safe_str(signal.get("decision_reason", signal.get("reason", "")), "")
    if explicit:
        return explicit

    eligible = bool(signal.get("eligible", False))
    readiness_score = _safe_float(signal.get("readiness_score", 0))
    rebuild_pressure = _safe_float(signal.get("rebuild_pressure", 0))
    execution_quality = _safe_float(signal.get("execution_quality", 0))

    if not eligible:
        return "The setup is blocked because it is not currently eligible."
    if rebuild_pressure >= 75:
        return "The setup is under too much rebuild pressure to trust cleanly."
    if readiness_score >= 85 and execution_quality >= 65:
        return "The setup is sufficiently aligned across readiness and execution to justify action."
    if readiness_score >= 60:
        return "The setup has some structure, but still needs cleaner confirmation."
    return "The setup does not yet have enough structural quality to deserve action."


def explain_trade_decision(signal: Optional[Dict[str, Any]] = None, *args, **kwargs) -> Dict[str, Any]:
    signal = _safe_dict(signal)

    symbol = _norm_symbol(signal.get("symbol", "UNKNOWN"))
    score = _safe_float(signal.get("score", 0))
    confidence = _norm_upper(signal.get("confidence", _confidence_bucket(score)), "LOW")
    verdict = _build_verdict_from_signal(signal)
    reason = _build_reason_from_signal(signal)

    readiness_score = _safe_float(signal.get("readiness_score", 0))
    promotion_score = _safe_float(signal.get("promotion_score", 0))
    rebuild_pressure = _safe_float(signal.get("rebuild_pressure", 0))
    execution_quality = _safe_float(signal.get("execution_quality", 0))
    eligible = bool(signal.get("eligible", False))

    summary = (
        f"{symbol} is scoring {round(score, 1)} with {confidence} confidence. "
        f"Readiness is {_readiness_label(readiness_score)}. "
        f"Rebuild pressure is {_pressure_label(rebuild_pressure)}. "
        f"The setup is {'eligible' if eligible else 'not eligible'}."
    )

    notes = _dedupe_keep_order([
        f"Score: {round(score, 1)}",
        f"Confidence: {confidence}",
        f"Readiness: {round(readiness_score, 1)}",
        f"Promotion: {round(promotion_score, 1)}",
        f"Rebuild Pressure: {round(rebuild_pressure, 1)}",
        f"Execution Quality: {round(execution_quality, 1)}",
        f"Execution Read: {_execution_label(execution_quality)}",
    ])

    next_action = "Wait for better structure."
    if verdict == "TAKE":
        next_action = "Enter with discipline and defined risk."
    elif verdict == "WATCH":
        next_action = "Watch for confirmation before entry."
    elif verdict in {"BLOCK", "REJECT"}:
        next_action = "Do not force the setup."

    return {
        "symbol": symbol,
        "headline": f"{symbol} decision: {verdict}",
        "summary": summary,
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "why": reason,
        "notes": notes,
        "next_action": next_action,
    }


def build_rejection_analysis(trade: Optional[Dict[str, Any]] = None, reason_key: Optional[str] = None, *args, **kwargs) -> List[str]:
    trade = _safe_dict(trade)
    symbol = _norm_symbol(trade.get("symbol", "UNKNOWN"))
    score = _safe_float(trade.get("score", 0))
    readiness_score = _safe_float(trade.get("readiness_score", 0))
    rebuild_pressure = _safe_float(trade.get("rebuild_pressure", 0))
    eligible = trade.get("eligible")

    analysis: List[str] = []

    reason_key = _safe_str(reason_key, "").lower()
    if reason_key:
        analysis.append(f"Primary rejection key: {reason_key.replace('_', ' ')}.")

    if eligible is False:
        analysis.append("The setup failed eligibility requirements.")

    if score and score < 50:
        analysis.append(f"Score is too weak at {round(score, 1)}.")

    if readiness_score and readiness_score < 60:
        analysis.append(f"Readiness is too soft at {round(readiness_score, 1)}.")

    if rebuild_pressure >= 75:
        analysis.append(f"Rebuild pressure is too high at {round(rebuild_pressure, 1)}.")

    explicit_reason = _safe_str(trade.get("rejection_reason", ""), "")
    if explicit_reason:
        analysis.append(explicit_reason)

    if not analysis:
        analysis.append(f"{symbol} did not clear execution standards.")

    return _dedupe_keep_order(analysis)


def explain_rejection(trade: Optional[Dict[str, Any]] = None, reason_key: Optional[str] = None, *args, **kwargs) -> str:
    trade = _safe_dict(trade)
    symbol = _norm_symbol(trade.get("symbol", "UNKNOWN"))
    analysis = build_rejection_analysis(trade, reason_key)

    if analysis:
        return f"{symbol} rejected: " + " ".join(analysis[:3])

    return f"{symbol} rejected because the setup did not meet execution standards."


def explain_reentry_detail(payload: Optional[Dict[str, Any]] = None, *args, **kwargs) -> Dict[str, Any]:
    payload = _safe_dict(payload)

    symbol = _norm_symbol(payload.get("symbol", "UNKNOWN"))
    reentry_allowed = bool(payload.get("reentry_allowed", payload.get("allowed", False)))
    cooldown = _safe_int(payload.get("cooldown_minutes", payload.get("minutes_to_reentry", 0)), 0)
    reason = _safe_str(payload.get("reason", payload.get("decision_reason", "")), "")

    if not reason:
        reason = (
            "Re-entry is allowed because the guardrails are not currently blocking a new attempt."
            if reentry_allowed else
            "Re-entry is blocked because the system still sees unresolved risk or behavior pressure."
        )

    notes = []
    if cooldown > 0:
        notes.append(f"Cooldown remaining: {cooldown} minute(s).")

    for item in _safe_list(payload.get("learning_notes", [])):
        text = _safe_str(item, "")
        if text:
            notes.append(text)

    return {
        "symbol": symbol,
        "headline": f"{symbol} re-entry detail",
        "summary": f"{symbol} re-entry is {'allowed' if reentry_allowed else 'blocked'}.",
        "verdict": "ALLOW" if reentry_allowed else "WAIT",
        "reason": reason,
        "why": reason,
        "notes": _dedupe_keep_order(notes),
        "next_action": (
            "Re-enter only if the setup requalifies cleanly."
            if reentry_allowed else
            "Do not re-enter yet."
        ),
    }


def explain_exit(payload: Optional[Dict[str, Any]] = None, *args, **kwargs) -> Dict[str, Any]:
    payload = _safe_dict(payload)

    symbol = _norm_symbol(payload.get("symbol", "UNKNOWN"))
    pnl = _safe_float(payload.get("pnl", payload.get("realized_pnl", 0)), 0.0)
    exit_reason = _safe_str(payload.get("exit_reason", payload.get("reason", payload.get("decision_reason", ""))), "")
    exit_explanation = _safe_str(payload.get("exit_explanation", ""), "")

    if not exit_reason:
        exit_reason = (
            "The trade was closed profitably."
            if pnl > 0 else
            "The trade was closed to stop further damage."
            if pnl < 0 else
            "The trade was closed without a strong profit or loss outcome."
        )

    if not exit_explanation:
        exit_explanation = (
            "The system is preserving realized gains."
            if pnl > 0 else
            "The system is treating this as protective damage control."
            if pnl < 0 else
            "The system is treating this as a neutral close."
        )

    return {
        "symbol": symbol,
        "headline": f"{symbol} exit detail",
        "summary": exit_explanation,
        "verdict": "PROTECT" if pnl > 0 else "EXIT",
        "reason": exit_reason,
        "why": exit_reason,
        "notes": [
            f"PnL: {round(pnl, 2)}",
            exit_reason,
            exit_explanation,
        ],
        "next_action": "Review whether the exit matched the thesis and pressure profile.",
    }


def explain_position_state(payload: Optional[Dict[str, Any]] = None, *args, **kwargs) -> Dict[str, Any]:
    payload = _safe_dict(payload)

    symbol = _norm_symbol(payload.get("symbol", "UNKNOWN"))
    status = _safe_str(payload.get("status", "open"), "open").lower()
    pnl = _safe_float(payload.get("pnl", payload.get("unrealized_pnl", 0)), 0.0)

    agreement = _safe_dict(payload.get("system_agreement", {}))
    health = _safe_dict(payload.get("health", {}))

    agreement_score = _safe_int(agreement.get("score", 0), 0)
    health_score = _safe_int(health.get("score", 0), 0)
    direction = _norm_upper(payload.get("direction", payload.get("strategy", "")), "UNKNOWN")

    if status == "closed":
        verdict = "CLOSED"
        reason = "This position is already closed."
        next_action = "Review the finished trade."
    elif health_score >= 75 and agreement_score >= 75:
        verdict = "HOLD"
        reason = "The position still looks structurally healthy and aligned."
        next_action = "Let it work, but keep monitoring."
    elif health_score < 35 or agreement_score < 55:
        verdict = "PROTECT"
        reason = "The position is showing weakness in health, agreement, or both."
        next_action = "Reduce risk or prepare to close."
    else:
        verdict = "WATCH"
        reason = "The position is alive, but the structure is mixed."
        next_action = "Watch closely for either recovery or deterioration."

    summary = (
        f"{symbol} is a {direction} position with status {status}. "
        f"Agreement is {agreement_score}, health is {health_score}, "
        f"and current PnL is {round(pnl, 2)}."
    )

    return {
        "symbol": symbol,
        "headline": f"{symbol} position state",
        "summary": summary,
        "verdict": verdict,
        "reason": reason,
        "why": reason,
        "notes": [
            f"Status: {status}",
            f"Direction: {direction}",
            f"Agreement: {agreement_score}",
            f"Health: {health_score}",
            f"PnL: {round(pnl, 2)}",
        ],
        "next_action": next_action,
    }


def build_trade_explainability(signal: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return explain_trade_decision(signal)


def build_exit_explainability(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return explain_exit(payload)


def build_reentry_explainability(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return explain_reentry_detail(payload)


def build_rejection_explainability(payload: Optional[Dict[str, Any]] = None, reason_key: Optional[str] = None) -> Dict[str, Any]:
    return {
        "headline": f"{_norm_symbol(_safe_dict(payload).get('symbol', 'UNKNOWN'))} rejected",
        "summary": explain_rejection(payload, reason_key),
        "verdict": "REJECT",
        "reason": explain_rejection(payload, reason_key),
        "why": explain_rejection(payload, reason_key),
        "notes": build_rejection_analysis(payload, reason_key),
        "next_action": "Do not force the setup.",
    }
