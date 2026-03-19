import json
from pathlib import Path
from datetime import datetime

RESEARCH_SIGNALS_FILE = "data/research_signals.json"

def _load(path, default):
    if not Path(path).exists():
        return default
    with open(path, "r") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data[-300:], f, indent=2)

def save_research_signal(trade, regime=None, mode=None, volatility=None, source="research"):
    data = _load(RESEARCH_SIGNALS_FILE, [])

    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": trade.get("symbol"),
        "strategy": trade.get("strategy"),
        "score": trade.get("score"),
        "confidence": trade.get("confidence"),
        "price": trade.get("price"),
        "source": source,
        "regime": regime,
        "mode": mode,
        "volatility": volatility,
    }

    data.append(entry)
    _save(RESEARCH_SIGNALS_FILE, data)
    return entry

def load_research_signals():
    return _load(RESEARCH_SIGNALS_FILE, [])
