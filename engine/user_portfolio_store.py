import json
from pathlib import Path

BASE_DIR = Path("data/user_portfolios")
BASE_DIR.mkdir(parents=True, exist_ok=True)

def _portfolio_path(username):
    return BASE_DIR / f"{username}_portfolio.json"

def load_user_portfolio(username):
    path = _portfolio_path(username)
    if not path.exists():
        return {
            "broker": None,
            "linked": False,
            "positions": [],
            "cash": 0,
            "buying_power": 0,
            "notes": "",
        }
    with open(path, "r") as f:
        return json.load(f)

def save_user_portfolio(username, payload):
    path = _portfolio_path(username)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return payload

def save_mock_portfolio_from_form(username, broker, cash, buying_power, notes, positions):
    payload = {
        "broker": broker,
        "linked": True,
        "cash": float(cash or 0),
        "buying_power": float(buying_power or 0),
        "notes": notes or "",
        "positions": positions,
    }
    return save_user_portfolio(username, payload)

def clear_user_portfolio(username):
    payload = {
        "broker": None,
        "linked": False,
        "positions": [],
        "cash": 0,
        "buying_power": 0,
        "notes": "",
    }
    return save_user_portfolio(username, payload)
