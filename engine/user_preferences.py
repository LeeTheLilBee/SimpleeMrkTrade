import json
from pathlib import Path

FILE = "data/user_preferences.json"

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
    return data.get(username, {
        "email_notifications": True,
        "signal_notifications": True,
        "risk_notifications": True,
        "premium_notifications": True,
        "theme": "dark"
    })

def save_preferences(username, prefs):
    data = _load()
    data[username] = prefs
    _save(data)
    return prefs
