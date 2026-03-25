import json
from pathlib import Path

CLOSED_FILE = "data/closed_positions.json"


def _load_closed():
    path = Path(CLOSED_FILE)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_latest_closed_trade(symbol):
    rows = [r for r in _load_closed() if r.get("symbol") == symbol]
    if not rows:
        return None
    rows.sort(key=lambda r: r.get("closed_at", ""), reverse=True)
    return rows[0]


def reentry_allowed(trade):
    symbol = trade.get("symbol")
    latest = get_latest_closed_trade(symbol)
    if not latest:
        return True, "no_recent_closed_trade"

    recent_reason = str(latest.get("reason", "")).lower()
    guarded_reasons = {
        "cut_weakness",
        "no_follow_through",
        "structure_deterioration",
        "time_exit",
        "risk_alert",
    }

    if recent_reason not in guarded_reasons:
        return True, "recent_close_not_guarded"

    new_score = float(trade.get("score", 0) or 0)
    old_score = float(latest.get("score", 0) or 0)

    new_conf = str(trade.get("confidence", "")).upper()
    old_conf = str(latest.get("confidence", "")).upper()

    new_price = float(trade.get("price", 0) or 0)
    old_exit = float(latest.get("exit_price", latest.get("current_price", 0)) or 0)

    strategy = str(trade.get("strategy", "CALL")).upper()
    trend = str(trade.get("trend", "UPTREND")).upper()

    score_improved = new_score >= old_score + 10
    confidence_ok = (new_conf == old_conf) or (new_conf == "HIGH" and old_conf in {"LOW", "MEDIUM"})
    price_reclaimed = new_price > old_exit * 1.002 if strategy == "CALL" else new_price < old_exit * 0.998
    trend_ok = trend == "UPTREND" if strategy == "CALL" else trend == "DOWNTREND"

    if score_improved and confidence_ok and price_reclaimed and trend_ok:
        return True, "reentry_conditions_met"

    reasons = []
    if not score_improved:
        reasons.append("score_not_improved_enough")
    if not confidence_ok:
        reasons.append("confidence_not_improved")
    if not price_reclaimed:
        reasons.append("price_not_reclaimed")
    if not trend_ok:
        reasons.append("trend_not_supportive")

    return False, ",".join(reasons)
