import json
from datetime import datetime
from pathlib import Path

FILE = "data/notifications.json"

TIER_ORDER = {
    "free": 0,
    "guest": 0,
    "starter": 1,
    "pro": 2,
    "elite": 3,
    "master": 4,
}

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-400:], f, indent=2)

def push_notification(notif_type, message, trade_id=None, min_tier="starter", level="info"):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": notif_type,
        "message": message,
        "trade_id": trade_id,
        "tier_required": min_tier,
        "level": level,
    }
    data.append(entry)
    _save(data)
    return entry

def notifications_for_tier(user_tier):
    data = _load()
    current = TIER_ORDER.get((user_tier or "guest").lower(), 0)

    visible = []
    for item in data:
        required = TIER_ORDER.get((item.get("tier_required") or "starter").lower(), 1)
        if current >= required:
            visible.append(item)

    return sorted(visible, key=lambda x: x.get("timestamp", ""), reverse=True)

def clear_notifications():
    _save([])
    return True
