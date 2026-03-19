import json
from pathlib import Path
from datetime import datetime

FILE = "data/billing_status.json"

def _load():
    if not Path(FILE).exists():
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_billing_status(username):
    data = _load()
    return data.get(username, {
        "plan": "Starter",
        "status": "inactive",
        "renewal_date": None,
        "customer_id": None,
        "subscription_id": None,
        "provider": "not_connected"
    })

def set_billing_status(username, plan, status="active", provider="mock", customer_id=None, subscription_id=None):
    data = _load()
    data[username] = {
        "plan": plan,
        "status": status,
        "renewal_date": datetime.now().date().isoformat(),
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "provider": provider
    }
    _save(data)
    return data[username]
