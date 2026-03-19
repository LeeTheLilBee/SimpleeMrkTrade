import json
from pathlib import Path

USERS_FILE = "data/users.json"
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

def load_users():
    return _load(USERS_FILE, [])

def save_users(users):
    _save(USERS_FILE, users)

def list_users():
    users = load_users()
    billing = _load(BILLING_FILE, {})
    rows = []

    for user in users:
        username = user.get("username")
        rows.append({
            "username": username,
            "tier": user.get("tier", "Starter"),
            "role": user.get("role", "member"),
            "billing_status": billing.get(username, {}).get("status", "inactive"),
            "billing_plan": billing.get(username, {}).get("plan", user.get("tier", "Starter"))
        })

    return rows

def get_user(username):
    users = load_users()
    prefs = _load(PREFS_FILE, {})
    billing = _load(BILLING_FILE, {})

    for user in users:
        if user.get("username") == username:
            return {
                "user": user,
                "preferences": prefs.get(username, DEFAULT_PREFS.copy()),
                "billing": billing.get(username, DEFAULT_BILLING.copy())
            }
    return None

def update_user_tier(username, new_tier):
    users = load_users()
    changed = False

    for user in users:
        if user.get("username") == username:
            user["tier"] = new_tier
            changed = True
            break

    if changed:
        save_users(users)

    return changed

def reset_user_password(username, new_password):
    users = load_users()
    changed = False

    for user in users:
        if user.get("username") == username:
            user["password"] = new_password
            changed = True
            break

    if changed:
        save_users(users)

    return changed

def rename_user(old_username, new_username):
    users = load_users()
    prefs = _load(PREFS_FILE, {})
    billing = _load(BILLING_FILE, {})

    if any(u.get("username") == new_username for u in users):
        return False, "Username already exists."

    target = None
    for user in users:
        if user.get("username") == old_username:
            target = user
            break

    if not target:
        return False, "User not found."

    target["username"] = new_username
    save_users(users)

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

def create_user(username, password, tier="Starter", role="member"):
    users = load_users()

    if any(u.get("username") == username for u in users):
        return False, "Username already exists."

    users.append({
        "username": username,
        "password": password,
        "tier": tier,
        "role": role
    })
    save_users(users)

    prefs = _load(PREFS_FILE, {})
    prefs[username] = DEFAULT_PREFS.copy()
    _save(PREFS_FILE, prefs)

    billing = _load(BILLING_FILE, {})
    billing[username] = DEFAULT_BILLING.copy()
    billing[username]["plan"] = tier
    _save(BILLING_FILE, billing)

    return True, "User created."

def delete_user(username):
    users = load_users()
    new_users = [u for u in users if u.get("username") != username]

    if len(new_users) == len(users):
        return False, "User not found."

    save_users(new_users)

    prefs = _load(PREFS_FILE, {})
    if username in prefs:
        del prefs[username]
        _save(PREFS_FILE, prefs)

    billing = _load(BILLING_FILE, {})
    if username in billing:
        del billing[username]
        _save(BILLING_FILE, billing)

    return True, "User deleted."
