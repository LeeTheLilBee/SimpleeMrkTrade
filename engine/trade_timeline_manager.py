import json
from pathlib import Path
from datetime import datetime

FILE = "data/trade_timeline.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-500:], f, indent=2)

def add_trade_timeline_event(symbol, stage, details=None):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "event": stage,
        "details": details or {}
    }
    data.append(entry)
    _save(data)
    return entry
