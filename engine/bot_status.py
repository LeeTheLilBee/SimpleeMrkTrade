import json
from datetime import datetime

FILE = "data/bot_status.json"

def write_bot_status(running=False, message="idle"):
    payload = {
        "running": running,
        "last_run": datetime.now().isoformat(),
        "last_message": message
    }
    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)
    return payload
