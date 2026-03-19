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
    "stripe_price_id": None,
    "stripe_checkout_url": None,
    "stripe_portal_url": None,
    "last_event": None
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
    payload = DEFAULT.copy()
    payload.update(data.get(username, {}))
    return payload

def set_billing_status(
    username,
    plan,
    status="active",
    provider="mock",
    customer_id=None,
    subscription_id=None,
    checkout_url=None,
    portal_url=None,
    last_event=None
):
    data = _load()
    payload = DEFAULT.copy()
    payload.update({
        "plan": plan,
        "status": status,
        "renewal_date": datetime.now().date().isoformat(),
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "provider": provider,
        "portal_ready": provider in ["mock", "stripe", "internal"],
        "stripe_checkout_url": checkout_url,
        "stripe_portal_url": portal_url,
        "last_event": last_event
    })
    payload.update(STRIPE_PLAN_MAP.get(plan, {}))
    data[username] = payload
    _save(data)
    return payload

def update_billing_event(username, event_name, updates=None):
    data = _load()
    payload = DEFAULT.copy()
    payload.update(data.get(username, {}))
    payload["last_event"] = {
        "name": event_name,
        "timestamp": datetime.now().isoformat()
    }
    if updates:
        payload.update(updates)
    data[username] = payload
    _save(data)
    return payload

def create_stripe_checkout_placeholder(username, plan):
    status = get_billing_status(username)
    return {
        "username": username,
        "plan": plan,
        "price_id": STRIPE_PLAN_MAP.get(plan, {}).get("stripe_price_id"),
        "provider": "stripe",
        "checkout_url": f"/billing/stripe/simulated-success?user={username}&plan={plan}",
        "existing_status": status
    }

def create_stripe_portal_placeholder(username):
    status = get_billing_status(username)
    return {
        "username": username,
        "provider": "stripe",
        "portal_url": f"/billing/stripe/portal-view?user={username}",
        "existing_status": status
    }
