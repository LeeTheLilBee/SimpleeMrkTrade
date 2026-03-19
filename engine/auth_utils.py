import json
import hashlib
import secrets
from pathlib import Path

LEGACY_FILE = "data/users.json"
SECURE_FILE = "data/users_secure.json"

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
    if secure_users:
        return secure_users

    legacy_users = _load(LEGACY_FILE, [])
    migrated = []

    for user in legacy_users:
        password = user.get("password", "")
        migrated.append({
            "username": user.get("username"),
            "password_hash": _hash_password(password) if password else "",
            "tier": user.get("tier", "Starter"),
            "role": user.get("role", "member")
        })

    if migrated:
        save_secure_users(migrated)

    return migrated

def authenticate_user(username, password):
    users = ensure_secure_user_store()

    for user in users:
        if user.get("username") == username and _verify_password(password, user.get("password_hash", "")):
            return {
                "username": user.get("username"),
                "tier": user.get("tier", "Starter"),
                "role": user.get("role", "member")
            }
    return None

def create_secure_user(username, password, tier="Starter", role="member"):
    users = ensure_secure_user_store()

    if any(u.get("username") == username for u in users):
        return False, "Username already exists."

    users.append({
        "username": username,
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
            "password_hash": _hash_password(password),
            "tier": "Elite",
            "role": "master"
        })

    save_secure_users(users)
    return True
