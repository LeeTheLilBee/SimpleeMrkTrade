import json
from pathlib import Path

FILE = "data/notification_settings.json"

DEFAULT_SETTINGS = {
    "high_conviction_only": False,
    "research_alerts": True,
    "execution_alerts": True,
    "risk_alerts": True,
    "system_alerts": True,
    "min_score": 0,
    "strategy_filter": "ALL",
    "volatility_filter": "ALL",
}

def _load():
    if not Path(FILE).exists():
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_notification_settings(username):
    data = _load()
    settings = DEFAULT_SETTINGS.copy()
    settings.update(data.get(username, {}))
    return settings

def save_notification_settings(username, settings):
    data = _load()
    merged = DEFAULT_SETTINGS.copy()
    merged.update(settings)
    data[username] = merged
    _save(data)
    return merged
