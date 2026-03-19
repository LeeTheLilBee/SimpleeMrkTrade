import json
from pathlib import Path
from engine.auth_utils import (
    load_secure_users,
    create_secure_user,
    reset_secure_password,
    rename_secure_user,
    update_secure_user_tier,
    delete_secure_user,
    set_force_password_reset,
    get_force_password_reset,
)

PREFS_FILE = "data/user_preferences.json"
BILLING_FILE = "data/billing_status.json"

DEFAULT_PREFS = {
    "email_notifications": True,
    "signal_notifications": True,
    "risk_notifications": True,
    "premium_notifications": True,
    "system_notifications": True,
    "theme": "dark"
}

DEFAULT_BILLING = {
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

def _load(path, default):
    if not Path(path).exists():
        return default
    with open(path, "r") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def list_users():
    users = load_secure_users()
    billing = _load(BILLING_FILE, {})
    rows = []

    for user in users:
        username = user.get("username")
        rows.append({
            "username": username,
            "email": user.get("email"),
            "tier": user.get("tier", "Starter"),
            "role": user.get("role", "member"),
            "billing_status": billing.get(username, {}).get("status", "inactive"),
            "billing_plan": billing.get(username, {}).get("plan", user.get("tier", "Starter")),
            "force_password_reset": get_force_password_reset(username)
        })

    return rows

def get_user(username):
    users = load_secure_users()
    prefs = _load(PREFS_FILE, {})
    billing = _load(BILLING_FILE, {})

    for user in users:
        if user.get("username") == username:
            safe_user = {
                "username": user.get("username"),
                "email": user.get("email"),
                "tier": user.get("tier", "Starter"),
                "role": user.get("role", "member"),
                "force_password_reset": get_force_password_reset(username)
            }
            return {
                "user": safe_user,
                "preferences": prefs.get(username, DEFAULT_PREFS.copy()),
                "billing": billing.get(username, DEFAULT_BILLING.copy())
            }
    return None

def update_user_tier(username, new_tier):
    return update_secure_user_tier(username, new_tier)

def reset_user_password(username, new_password):
    return reset_secure_password(username, new_password)

def rename_user(old_username, new_username):
    ok, msg = rename_secure_user(old_username, new_username)
    if not ok:
        return ok, msg

    prefs = _load(PREFS_FILE, {})
    billing = _load(BILLING_FILE, {})

    if old_username in prefs:
        prefs[new_username] = prefs.pop(old_username)
        _save(PREFS_FILE, prefs)

    if old_username in billing:
        billing[new_username] = billing.pop(old_username)
        _save(BILLING_FILE, billing)

    return True, "Username updated."

def set_billing_status(username, status=None, plan=None, provider=None):
    billing = _load(BILLING_FILE, {})
    current = billing.get(username, DEFAULT_BILLING.copy())

    if status is not None:
        current["status"] = status
    if plan is not None:
        current["plan"] = plan
    if provider is not None:
        current["provider"] = provider

    billing[username] = current
    _save(BILLING_FILE, billing)
    return current

def create_user(username, password, email=None, tier="Starter", role="member"):
    ok, msg = create_secure_user(username, password, email=email, tier=tier, role=role)
    if not ok:
        return ok, msg

    prefs = _load(PREFS_FILE, {})
    prefs[username] = DEFAULT_PREFS.copy()
    _save(PREFS_FILE, prefs)

    billing = _load(BILLING_FILE, {})
    billing[username] = DEFAULT_BILLING.copy()
    billing[username]["plan"] = tier
    _save(BILLING_FILE, billing)

    return True, "User created."

def delete_user(username):
    ok, msg = delete_secure_user(username)
    if not ok:
        return ok, msg

    prefs = _load(PREFS_FILE, {})
    if username in prefs:
        del prefs[username]
        _save(PREFS_FILE, prefs)

    billing = _load(BILLING_FILE, {})
    if username in billing:
        del billing[username]
        _save(BILLING_FILE, billing)

    return True, "User deleted."

def force_password_reset(username, required=True):
    return set_force_password_reset(username, required)
