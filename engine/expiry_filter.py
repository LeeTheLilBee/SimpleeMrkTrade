from datetime import datetime

def valid_expiry(expiry):
    try:
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
    except Exception:
        return False

    days = (expiry_date - datetime.today()).days
    return 3 <= days <= 30
