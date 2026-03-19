import json
from pathlib import Path
from datetime import datetime

FILE = "data/live_activity.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-300:], f, indent=2)

def push_activity(event_type, message, symbol=None, meta=None):
    data = _load()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "message": message,
        "symbol": symbol,
        "meta": meta or {}
    }

    data.append(entry)
    _save(data)

    return entry
