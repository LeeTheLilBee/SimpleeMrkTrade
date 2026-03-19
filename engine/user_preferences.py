import json
from pathlib import Path

FILE = "data/user_preferences.json"

DEFAULT_PREFS = {
    "email_notifications": True,
    "signal_notifications": True,
    "risk_notifications": True,
    "premium_notifications": True,
    "system_notifications": True,
    "theme": "dark"
}

def _load():
    if not Path(FILE).exists():
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_preferences(username):
    data = _load()
    prefs = data.get(username, {})
    merged = DEFAULT_PREFS.copy()
    merged.update(prefs)
    return merged

def save_preferences(username, prefs):
    data = _load()
    merged = DEFAULT_PREFS.copy()
    merged.update(prefs)
    data[username] = merged
    _save(data)
    return merged
