import re

def password_policy_check(password: str):
    errors = []

    if len(password or "") < 10:
        errors.append("Password must be at least 10 characters long.")
    if not re.search(r"[A-Z]", password or ""):
        errors.append("Password must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password or ""):
        errors.append("Password must include at least one lowercase letter.")
    if not re.search(r"[0-9]", password or ""):
        errors.append("Password must include at least one number.")
    if not re.search(r"[^A-Za-z0-9]", password or ""):
        errors.append("Password must include at least one special character.")

    return {
        "ok": len(errors) == 0,
        "errors": errors
    }
