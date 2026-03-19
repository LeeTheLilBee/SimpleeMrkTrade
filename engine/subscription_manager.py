import json
from pathlib import Path

FILE = "data/users.json"

def load_users():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(FILE, "w") as f:
        json.dump(users, f, indent=2)

def update_user_tier(username, new_tier):
    users = load_users()

    for user in users:
        if user["username"] == username:
            user["tier"] = new_tier
            save_users(users)
            return True

    return False
