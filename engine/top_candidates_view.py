from __future__ import annotations

from typing import Any, Dict, List


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _score(trade: Dict[str, Any]) -> float:
    trade = _safe_dict(trade)
    return _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0)


def _status_label(trade: Dict[str, Any]) -> str:
    trade = _safe_dict(trade)

    if bool(trade.get("selected_for_execution", False)):
        return "SELECTED"
    if bool(trade.get("execution_ready", False)):
        return "EXECUTION READY"
    if bool(trade.get("research_approved", False)):
        reason = _safe_str(trade.get("final_reason", ""), "")
        if reason.startswith("governor_blocked:") or _safe_str(trade.get("blocked_at"), "") == "execution_guard":
            return "RESEARCH QUALIFIED / EXECUTION PAUSED"
        return "RESEARCH QUALIFIED"
    return "RESEARCH ONLY"


def _reason_label(trade: Dict[str, Any]) -> str:
    trade = _safe_dict(trade)
    reason = (
        _safe_str(trade.get("final_reason_detail"), "")
        or _safe_str(trade.get("final_reason"), "")
        or _safe_str(trade.get("vehicle_reason"), "")
        or _safe_str(trade.get("best_vehicle_reason"), "")
        or "No reason recorded."
    )
    return reason


def print_top_candidates(trades: List[Dict[str, Any]], limit: int = 5):
    trades = trades if isinstance(trades, list) else []
    ranked = sorted(
        [t for t in trades if isinstance(t, dict)],
        key=_score,
        reverse=True,
    )

    print("TOP CANDIDATES")

    if not ranked:
        print("None")
        return

    for trade in ranked[:limit]:
        symbol = _safe_str(trade.get("symbol"), "UNKNOWN").upper()
        strategy = _safe_str(trade.get("strategy"), "N/A").upper()
        confidence = _safe_str(trade.get("confidence"), "LOW").upper()
        vehicle = _safe_str(trade.get("vehicle_selected"), "RESEARCH_ONLY").upper()
        status = _status_label(trade)
        reason = _reason_label(trade)

        print(
            symbol,
            "|", strategy,
            "| Score:", round(_score(trade), 2),
            "| Confidence:", confidence,
            "| Vehicle:", vehicle,
            "| Status:", status,
            "| Reason:", reason,
        )


__all__ = ["print_top_candidates"]
