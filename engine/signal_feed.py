import json
from pathlib import Path
from datetime import datetime

FILE = "data/live_signals.json"
MAX_SIGNALS = 100

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-MAX_SIGNALS:], f, indent=2)

def push_signal(symbol, strategy, score, confidence, trade_id=None, source="execution", mode=None, volatility=None):
    data = _load()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "strategy": strategy,
        "score": score,
        "confidence": confidence,
        "trade_id": trade_id,
        "source": source,
        "mode": mode,
        "volatility": volatility,
    }

    data.append(entry)
    _save(data)
    return entry

def load_signals():
    return _load()

def tier_signal_limit(tier):
    tier = (tier or "").lower()

    if tier == "guest":
        return 2
    if tier == "free":
        return 3
    if tier == "starter":
        return 5
    if tier == "pro":
        return 10
    if tier == "elite":
        return 100

    return 3
    
def grouped_signals(limit_per_symbol=None):
    data = sorted(_load(), key=lambda x: x.get("timestamp", ""), reverse=True)
    grouped = {}

    for item in data:
        symbol = item.get("symbol", "UNKNOWN")
        grouped.setdefault(symbol, []).append(item)

    boards = []
    for symbol, items in grouped.items():
        latest = items[0] if items else {}
        trimmed = items[:limit_per_symbol] if limit_per_symbol else items
        boards.append({
            "symbol": symbol,
            "latest_score": latest.get("score"),
            "latest_confidence": latest.get("confidence"),
            "latest_strategy": latest.get("strategy"),
            "latest_trade_id": latest.get("trade_id"),
            "latest_timestamp": latest.get("timestamp"),
            "signals": trimmed,
            "signal_count": len(items),
        })

    boards.sort(key=lambda x: (x.get("latest_score") or 0), reverse=True)
    return boards
