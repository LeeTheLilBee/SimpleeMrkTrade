import json
from pathlib import Path
from datetime import datetime

FILE = "data/billing_status.json"

DEFAULT = {
    "plan": "Starter",
    "status": "inactive",
    "renewal_date": None,
    "customer_id": None,
    "subscription_id": None,
    "provider": "not_connected",
    "checkout_ready": False,
    "portal_ready": False,
    "stripe_price_id": None
}

STRIPE_PLAN_MAP = {
    "Starter": {
        "stripe_price_id": "price_starter_placeholder",
        "checkout_ready": True
    },
    "Pro": {
        "stripe_price_id": "price_pro_placeholder",
        "checkout_ready": True
    },
    "Elite": {
        "stripe_price_id": "price_elite_placeholder",
        "checkout_ready": True
    }
}

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
    status = DEFAULT.copy()
    status.update(data.get(username, {}))
    return status

def set_billing_status(username, plan, status="active", provider="mock", customer_id=None, subscription_id=None):
    data = _load()
    payload = DEFAULT.copy()
    payload.update({
        "plan": plan,
        "status": status,
        "renewal_date": datetime.now().date().isoformat(),
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "provider": provider,
        "portal_ready": provider in ["mock", "stripe", "internal"]
    })
    payload.update(STRIPE_PLAN_MAP.get(plan, {}))
    data[username] = payload
    _save(data)
    return payload
