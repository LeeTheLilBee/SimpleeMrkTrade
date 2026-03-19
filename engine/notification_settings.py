import json
from pathlib import Path

FILE = "data/notification_settings.json"

def load_settings(username):
    if not Path(FILE).exists():
        return {}
    with open(FILE, "r") as f:
        data = json.load(f)
    return data.get(username, {
        "high_conviction_only": False,
        "research_alerts": True,
        "execution_alerts": True,
    })

def save_settings(username, settings):
    data = {}
    if Path(FILE).exists():
        with open(FILE, "r") as f:
            data = json.load(f)

    data[username] = settings

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
