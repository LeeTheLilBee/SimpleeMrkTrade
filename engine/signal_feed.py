import json
from pathlib import Path
from datetime import datetime

FILE = "data/live_signals.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-200:], f, indent=2)

def push_signal(symbol, strategy, score, confidence, trade_id=None):
    data = _load()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "strategy": strategy,
        "score": score,
        "confidence": confidence,
        "trade_id": trade_id
    }

    data.append(entry)
    _save(data)
