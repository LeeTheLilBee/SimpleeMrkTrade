import json
from pathlib import Path
from datetime import datetime

FILE = "data/notifications.json"
PREFS_FILE = "data/user_preferences.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-300:], f, indent=2)

def _load_prefs():
    if not Path(PREFS_FILE).exists():
        return {}
    with open(PREFS_FILE, "r") as f:
        return json.load(f)

def _tier_rank(tier):
    order = {
        "Guest": 0,
        "Starter": 1,
        "Pro": 2,
        "Elite": 3
    }
    return order.get(tier, 0)

def _category_allowed(category, prefs):
    mapping = {
        "signal": prefs.get("signal_notifications", True),
        "risk": prefs.get("risk_notifications", True),
        "premium": prefs.get("premium_notifications", True),
        "system": prefs.get("system_notifications", True)
    }
    return mapping.get(category, True)

def push_notification(
    title,
    message,
    level="info",
    link=None,
    members_only=False,
    min_tier="Guest",
    category="system"
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
        "min_tier": min_tier,
        "category": category
    }
    data.append(entry)
    _save(data)
    return entry

def filtered_notifications_for_user(user_tier="Guest", logged_in=False, username=None):
    items = _load()
    prefs_data = _load_prefs()
    prefs = prefs_data.get(username, {
        "signal_notifications": True,
        "risk_notifications": True,
        "premium_notifications": True,
        "system_notifications": True
    })

    visible = []

    for item in items:
        if item.get("members_only") and not logged_in:
            continue

        required_tier = item.get("min_tier", "Guest")
        if _tier_rank(user_tier) < _tier_rank(required_tier):
            continue

        category = item.get("category", "system")
        if not _category_allowed(category, prefs):
            continue

        visible.append(item)

    return visible

def unread_count_for_user(user_tier="Guest", logged_in=False, username=None):
    items = filtered_notifications_for_user(
        user_tier=user_tier,
        logged_in=logged_in,
        username=username
    )
    return len([n for n in items if not n.get("read")])

def mark_all_read():
    data = _load()
    for item in data:
        item["read"] = True
    _save(data)
    return data
