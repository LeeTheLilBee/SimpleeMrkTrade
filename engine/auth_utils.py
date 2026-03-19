import json
import hashlib
import secrets
from pathlib import Path

LEGACY_FILE = "data/users.json"
SECURE_FILE = "data/users_secure.json"
FORCE_RESET_FILE = "data/force_password_resets.json"

def _load(path, default):
    if not Path(path).exists():
        return default
    with open(path, "r") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${digest}"

def _verify_password(password, stored_hash):
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, digest = stored_hash.split("$", 1)
    candidate = hashlib.sha256((salt + password).encode()).hexdigest()
    return secrets.compare_digest(candidate, digest)

def load_secure_users():
    return _load(SECURE_FILE, [])

def save_secure_users(users):
    _save(SECURE_FILE, users)

def ensure_secure_user_store():
    secure_users = load_secure_users()

    legacy_users = _load(LEGACY_FILE, [])

    if not secure_users and legacy_users:
        migrated = []
        for user in legacy_users:
            password = user.get("password", "")
            migrated.append({
                "username": user.get("username"),
                "email": user.get("email"),
                "password_hash": _hash_password(password) if password else "",
                "tier": user.get("tier", "Starter"),
                "role": user.get("role", "member")
            })
        save_secure_users(migrated)
        return migrated

    # also merge in any legacy users not already present
    if secure_users and legacy_users:
        existing = {u.get("username") for u in secure_users}
        changed = False
        for user in legacy_users:
            uname = user.get("username")
            if uname not in existing:
                secure_users.append({
                    "username": uname,
                    "email": user.get("email"),
                    "password_hash": _hash_password(user.get("password", "")) if user.get("password") else "",
                    "tier": user.get("tier", "Starter"),
                    "role": user.get("role", "member")
                })
                changed = True
        if changed:
            save_secure_users(secure_users)

    return load_secure_users()

def authenticate_user(username, password):
    users = ensure_secure_user_store()
    force_reset = _load(FORCE_RESET_FILE, {})

    for user in users:
        if user.get("username") == username and _verify_password(password, user.get("password_hash", "")):
            return {
                "username": user.get("username"),
                "email": user.get("email"),
                "tier": user.get("tier", "Starter"),
                "role": user.get("role", "member"),
                "force_password_reset": force_reset.get(username, False)
            }
    return None

def create_secure_user(username, password, email=None, tier="Starter", role="member"):
    users = ensure_secure_user_store()

    if any(u.get("username") == username for u in users):
        return False, "Username already exists."

    if email and any((u.get("email") or "").lower() == email.lower() for u in users if u.get("email")):
        return False, "Email already exists."

    users.append({
        "username": username,
        "email": email,
        "password_hash": _hash_password(password),
        "tier": tier,
        "role": role
    })
    save_secure_users(users)
    return True, "User created."

def reset_secure_password(username, new_password):
    users = ensure_secure_user_store()
    changed = False

    for user in users:
        if user.get("username") == username:
            user["password_hash"] = _hash_password(new_password)
            changed = True
            break

    if changed:
        save_secure_users(users)

    force_reset = _load(FORCE_RESET_FILE, {})
    if username in force_reset:
        force_reset[username] = False
        _save(FORCE_RESET_FILE, force_reset)

    return changed

def rename_secure_user(old_username, new_username):
    users = ensure_secure_user_store()

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
    save_secure_users(users)

    force_reset = _load(FORCE_RESET_FILE, {})
    if old_username in force_reset:
        force_reset[new_username] = force_reset.pop(old_username)
        _save(FORCE_RESET_FILE, force_reset)

    return True, "Username updated."

def update_secure_user_tier(username, new_tier):
    users = ensure_secure_user_store()
    changed = False

    for user in users:
        if user.get("username") == username:
            user["tier"] = new_tier
            changed = True
            break

    if changed:
        save_secure_users(users)

    return changed

def delete_secure_user(username):
    users = ensure_secure_user_store()
    new_users = [u for u in users if u.get("username") != username]

    if len(new_users) == len(users):
        return False, "User not found."

    save_secure_users(new_users)

    force_reset = _load(FORCE_RESET_FILE, {})
    if username in force_reset:
        del force_reset[username]
        _save(FORCE_RESET_FILE, force_reset)

    return True, "User deleted."

def seed_master_password(password):
    users = ensure_secure_user_store()

    found = False
    for user in users:
        if user.get("username") == "admin":
            user["password_hash"] = _hash_password(password)
            found = True
            break

    if not found:
        users.append({
            "username": "admin",
            "email": "admin@simpleemrktrade.local",
            "password_hash": _hash_password(password),
            "tier": "Elite",
            "role": "master"
        })

    save_secure_users(users)
    return True

def set_force_password_reset(username, required=True):
    data = _load(FORCE_RESET_FILE, {})
    data[username] = bool(required)
    _save(FORCE_RESET_FILE, data)
    return True

def get_force_password_reset(username):
    data = _load(FORCE_RESET_FILE, {})
    return bool(data.get(username, False))
