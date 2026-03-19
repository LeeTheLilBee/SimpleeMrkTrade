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

def push_notification(
    title,
    message,
    level="info",
    link=None,
    members_only=False,
    min_tier="Guest"
):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "message": message,
        "level": level,
        "link": link,
        "read": False,
        "members_only": members_only,
        "min_tier": min_tier
    }
    data.append(entry)
    _save(data)
    return entry

def list_notifications():
    return _load()

def unread_count_for_user(user_tier="Guest", logged_in=False):
    items = filtered_notifications_for_user(user_tier=user_tier, logged_in=logged_in)
    return len([n for n in items if not n.get("read")])

def mark_all_read():
    data = _load()
    for item in data:
        item["read"] = True
    _save(data)
    return data

def _tier_rank(tier):
    order = {
        "Guest": 0,
        "Starter": 1,
        "Pro": 2,
        "Elite": 3
    }
    return order.get(tier, 0)

def filtered_notifications_for_user(user_tier="Guest", logged_in=False):
    items = _load()
    visible = []

    for item in items:
        if item.get("members_only") and not logged_in:
            continue

        required_tier = item.get("min_tier", "Guest")
        if _tier_rank(user_tier) < _tier_rank(required_tier):
            continue

        visible.append(item)

    return visible
