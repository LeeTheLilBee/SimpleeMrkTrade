from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CLOSED_FILE = "data/closed_positions.json"


# ============================================================
# SAFE HELPERS
# ============================================================

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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


# ============================================================
# CLOSED TRADE ACCESS
# ============================================================

def _load_closed() -> List[Dict[str, Any]]:
    path = Path(CLOSED_FILE)
    if not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_latest_closed_trade(symbol: str) -> Optional[Dict[str, Any]]:
    clean_symbol = _norm_symbol(symbol)
    if not clean_symbol:
        return None

    rows = [
        row for row in _load_closed()
        if isinstance(row, dict) and _norm_symbol(row.get("symbol", "")) == clean_symbol
    ]

    if not rows:
        return None

    rows.sort(
        key=lambda row: _safe_str(
            row.get("closed_at", row.get("timestamp", row.get("updated_at", ""))),
            "",
        ),
        reverse=True,
    )
    return rows[0]


# ============================================================
# REENTRY SCORING
# ============================================================

def build_reentry_diagnosis(trade: Dict[str, Any]) -> Dict[str, Any]:
    trade = trade if isinstance(trade, dict) else {}

    symbol = _norm_symbol(trade.get("symbol", ""))
    latest = get_latest_closed_trade(symbol)

    if not latest:
        return {
            "symbol": symbol,
            "allowed": True,
            "severity": "none",
            "reason": "no_recent_closed_trade",
            "reasons": [],
            "score": 100,
            "guarded": False,
            "latest_closed_trade": None,
        }

    recent_reason = _safe_str(
        latest.get("reason", latest.get("exit_reason", latest.get("close_reason", ""))),
        "",
    ).lower()

    guarded_reasons = {
        "cut_weakness",
        "cut_on_weakness",
        "no_follow_through",
        "structure_deterioration",
        "time_exit",
        "risk_alert",
        "capital_protection_exit",
        "stopped_out",
        "manual_exit_loss",
        "stop_loss",
        "failed_clean",
        "weak_followthrough",
    }

    if recent_reason not in guarded_reasons:
        return {
            "symbol": symbol,
            "allowed": True,
            "severity": "none",
            "reason": "recent_close_not_guarded",
            "reasons": [],
            "score": 95,
            "guarded": False,
            "latest_closed_trade": latest,
        }

    new_score = _safe_float(trade.get("score", 0), 0.0)
    old_score = _safe_float(latest.get("score", 0), 0.0)

    new_conf = _safe_str(trade.get("confidence", "LOW"), "LOW").upper()
    old_conf = _safe_str(latest.get("confidence", "LOW"), "LOW").upper()

    new_price = _safe_float(
        trade.get("price", trade.get("current_price", trade.get("entry", 0))),
        0.0,
    )
    old_exit = _safe_float(
        latest.get("exit_price", latest.get("current_price", latest.get("price", 0))),
        0.0,
    )

    strategy = _safe_str(trade.get("strategy", "CALL"), "CALL").upper()
    trend = _safe_str(trade.get("trend", ""), "").upper()
    rsi = _safe_float(trade.get("rsi", 55), 55.0)

    score_delta = new_score - old_score
    strong_score = new_score >= 180
    decent_score = new_score >= 120

    confidence_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "STRONG": 4}
    new_conf_rank = confidence_rank.get(new_conf, 0)
    old_conf_rank = confidence_rank.get(old_conf, 0)

    confidence_improved = new_conf_rank > old_conf_rank
    confidence_held = new_conf_rank == old_conf_rank
    confidence_ok = confidence_improved or (confidence_held and new_conf_rank >= 2)

    if strategy == "CALL":
        trend_ok = trend in {"UPTREND", "BULLISH", "BULL_TREND"}
        price_reclaimed = (old_exit <= 0) or (new_price >= old_exit * 1.001)
        momentum_ok = rsi >= 52
    else:
        trend_ok = trend in {"DOWNTREND", "BEARISH", "BEAR_TREND"}
        price_reclaimed = (old_exit <= 0) or (new_price <= old_exit * 0.999)
        momentum_ok = rsi <= 48

    score_improved_hard = score_delta >= 10
    score_improved_soft = score_delta >= 3 or strong_score

    reasons = []
    caution_reasons = []

    if not score_improved_soft:
        reasons.append("score_not_improved_enough")

    if not confidence_ok and not strong_score:
        reasons.append("confidence_not_improved")

    if not trend_ok:
        reasons.append("trend_not_supportive")

    if not price_reclaimed:
        if strong_score and trend_ok:
            caution_reasons.append("price_not_fully_reclaimed")
        else:
            reasons.append("price_not_reclaimed")

    if not momentum_ok:
        if decent_score and trend_ok:
            caution_reasons.append("momentum_not_clean")
        else:
            reasons.append("momentum_not_supportive")

    # --------------------------------------------------------
    # DECISION LAYER
    # --------------------------------------------------------
    # hard allow
    if score_improved_hard and confidence_ok and trend_ok and price_reclaimed:
        return {
            "symbol": symbol,
            "allowed": True,
            "severity": "clear",
            "reason": "reentry_conditions_met",
            "reasons": [],
            "score": 100,
            "guarded": True,
            "latest_closed_trade": latest,
        }

    # soft allow for very strong setups
    if strong_score and trend_ok and (confidence_ok or new_conf in {"HIGH", "STRONG"}):
        if len(reasons) <= 1:
            merged = reasons + caution_reasons
            return {
                "symbol": symbol,
                "allowed": True,
                "severity": "caution",
                "reason": "reentry_allowed_with_caution",
                "reasons": merged,
                "score": 72,
                "guarded": True,
                "latest_closed_trade": latest,
            }

    # moderate allow for decent setups with only minor issues
    if decent_score and trend_ok and len(reasons) == 0:
        return {
            "symbol": symbol,
            "allowed": True,
            "severity": "caution",
            "reason": "reentry_soft_pass",
            "reasons": caution_reasons,
            "score": 65,
            "guarded": True,
            "latest_closed_trade": latest,
        }

    merged = reasons + caution_reasons

    return {
        "symbol": symbol,
        "allowed": False,
        "severity": "block",
        "reason": ",".join(merged) if merged else "reentry_blocked",
        "reasons": merged,
        "score": 20,
        "guarded": True,
        "latest_closed_trade": latest,
    }


# ============================================================
# PUBLIC API
# ============================================================

def reentry_allowed(trade: Dict[str, Any]) -> Tuple[bool, str]:
    diagnosis = build_reentry_diagnosis(trade)
    return bool(diagnosis.get("allowed", False)), _safe_str(diagnosis.get("reason", "reentry_blocked"), "reentry_blocked")


def explain_reentry_status(trade: Dict[str, Any]) -> Dict[str, Any]:
    diagnosis = build_reentry_diagnosis(trade)

    severity = diagnosis.get("severity", "block")
    reasons = diagnosis.get("reasons", []) or []

    if severity == "clear":
        headline = "Reentry conditions are clean."
        summary = "The prior exit is no longer acting like a meaningful blocker."
    elif severity == "caution":
        headline = "Reentry is allowed, but not fully clean."
        summary = "The setup regained enough strength to be considered, but it still carries some scar tissue."
    else:
        headline = "Reentry is blocked."
        summary = "The setup has not done enough yet to justify another attempt."

    return {
        "headline": headline,
        "summary": summary,
        "allowed": diagnosis.get("allowed", False),
        "severity": severity,
        "reason": diagnosis.get("reason", ""),
        "reasons": reasons,
        "symbol": diagnosis.get("symbol", ""),
    }
