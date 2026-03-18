import json
from pathlib import Path
from datetime import datetime

FILE = "data/bot_log.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-300:], f, indent=2)

def log_bot(message, level="INFO"):
    data = _load()
    data.append({
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": str(message)
    })
    _save(data)
