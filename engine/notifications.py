import json
from pathlib import Path
from datetime import datetime

FILE = "data/notifications.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-300:], f, indent=2)

def push_notification(title, message, level="info", link=None):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "message": message,
        "level": level,
        "link": link,
        "read": False
    }
    data.append(entry)
    _save(data)
    return entry

def list_notifications():
    return _load()

def unread_count():
    return len([n for n in _load() if not n.get("read")])

def mark_all_read():
    data = _load()
    for item in data:
        item["read"] = True
    _save(data)
    return data
