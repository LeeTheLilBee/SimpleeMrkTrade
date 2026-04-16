import json
from pathlib import Path
from datetime import datetime

FILE = "data/trade_log.json"


def _load_trades():
    if not Path(FILE).exists():
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _is_open_trade(trade):
    return str(trade.get("status", "")).upper().strip() == "OPEN"


def executed_trade_count():
    return sum(1 for trade in _load_trades() if _is_open_trade(trade))


def executed_trade_count_today():
    today = datetime.now().date()
    count = 0
    for trade in _load_trades():
        ts = _parse_ts(trade.get("timestamp"))
        if ts and ts.date() == today and _is_open_trade(trade):
            count += 1
    return count
