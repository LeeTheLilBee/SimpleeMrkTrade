import json
from pathlib import Path
from datetime import datetime

FILE = "data/research_signals.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-300:], f, indent=2)

def save_research_signal(trade, regime=None, mode=None, volatility=None, source="research"):
    data = _load()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": trade.get("symbol"),
        "strategy": trade.get("strategy"),
        "score": trade.get("score"),
        "confidence": trade.get("confidence"),
        "price": trade.get("price"),
        "trade_id": trade.get("trade_id"),  # 🔥 THIS IS THE FIX
        "source": source,
        "regime": regime,
        "mode": mode,
        "volatility": volatility,
    }

    data.append(entry)
    _save(data)
    return entry
