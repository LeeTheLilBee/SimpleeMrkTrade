import json
from pathlib import Path
from datetime import datetime

FILE = "data/admin_audit_log.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data[-500:], f, indent=2)

def log_admin_action(actor, action, target=None, details=None):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "actor": actor,
        "action": action,
        "target": target,
        "details": details or {}
    }
    data.append(entry)
    _save(data)
    return entry

def get_admin_audit_log():
    return _load()
