
# ============================================================
# OBSERVATORY_PATCH_SELECTED_TRADE_STRATEGY_CANONICAL_KEYS_20260513
# engine/alerts.py
# Purpose:
# - Compatibility-safe alert helpers.
# - Never crash because a candidate uses final_strategy/starting_strategy/chosen_strategy
#   instead of the legacy strategy key.
# ============================================================

def _safe_str(value, default=""):
    try:
        if value is None:
            return default
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _resolve_strategy(trade):
    if not isinstance(trade, dict):
        return "UNKNOWN"

    strategy = (
        trade.get("strategy")
        or trade.get("final_strategy")
        or trade.get("chosen_strategy")
        or trade.get("starting_strategy")
        or trade.get("direction")
        or trade.get("side")
        or "UNKNOWN"
    )

    strategy = _safe_str(strategy, "UNKNOWN").upper()

    if strategy in {"", "NONE", "NULL", "NAN"}:
        return "UNKNOWN"

    return strategy


def _resolve_symbol(trade):
    if not isinstance(trade, dict):
        return "UNKNOWN"
    return _safe_str(trade.get("symbol"), "UNKNOWN").upper()


def _resolve_confidence(trade):
    if not isinstance(trade, dict):
        return "UNKNOWN"
    return _safe_str(
        trade.get("confidence")
        or trade.get("base_confidence")
        or trade.get("v2_confidence"),
        "UNKNOWN",
    ).upper()


def _resolve_score(trade):
    if not isinstance(trade, dict):
        return 0.0
    return _safe_float(
        trade.get("score")
        or trade.get("fused_score")
        or trade.get("base_score")
        or trade.get("v2_score"),
        0.0,
    )


def _resolve_vehicle(trade):
    if not isinstance(trade, dict):
        return "UNKNOWN"
    return _safe_str(
        trade.get("vehicle_selected")
        or trade.get("selected_vehicle")
        or trade.get("vehicle")
        or trade.get("asset_type")
        or trade.get("instrument_type"),
        "UNKNOWN",
    ).upper()


def normalize_alert_trade(trade):
    """
    Returns a shallow copy with legacy keys restored.
    This protects old bot/report/alert paths while newer candidate objects evolve.
    """
    if not isinstance(trade, dict):
        return {
            "symbol": "UNKNOWN",
            "strategy": "UNKNOWN",
            "confidence": "UNKNOWN",
            "score": 0.0,
            "vehicle_selected": "UNKNOWN",
        }

    row = dict(trade)

    strategy = _resolve_strategy(row)
    symbol = _resolve_symbol(row)
    confidence = _resolve_confidence(row)
    score = _resolve_score(row)
    vehicle = _resolve_vehicle(row)

    row.setdefault("symbol", symbol)
    row.setdefault("strategy", strategy)
    row.setdefault("final_strategy", strategy)
    row.setdefault("chosen_strategy", strategy)
    row.setdefault("starting_strategy", strategy)
    row.setdefault("direction", strategy)
    row.setdefault("confidence", confidence)
    row.setdefault("score", score)
    row.setdefault("vehicle_selected", vehicle)

    return row


def alert_trade(trade):
    row = normalize_alert_trade(trade)

    print(
        "ALERT:",
        row.get("symbol", "UNKNOWN"),
        "|",
        row.get("strategy", "UNKNOWN"),
        "| Score:",
        row.get("score", 0),
        "| Confidence:",
        row.get("confidence", "UNKNOWN"),
        "| Vehicle:",
        row.get("vehicle_selected", row.get("vehicle", "UNKNOWN")),
    )

    return row


def notify_trade_risk(symbol, message):
    print(
        "RISK ALERT:",
        _safe_str(symbol, "PORTFOLIO"),
        "|",
        _safe_str(message, "Risk notification"),
    )


def notify_trade_edge(symbol, reasons=None):
    if reasons is None:
        reasons = []

    if isinstance(reasons, (list, tuple)):
        reason_text = "; ".join(_safe_str(r, "") for r in reasons if _safe_str(r, ""))
    else:
        reason_text = _safe_str(reasons, "")

    print(
        "EDGE ALERT:",
        _safe_str(symbol, "UNKNOWN"),
        "|",
        reason_text or "Premium edge detected",
    )
