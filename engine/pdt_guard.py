from datetime import datetime, timedelta
import json
from pathlib import Path


TRADE_LOG_FILE = "data/trade_log.json"
ACCOUNT_STATE_FILE = "data/account_state.json"


def _load_json(path, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def get_account_profile():
    state = _load_json(ACCOUNT_STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}

    return {
        "equity": float(state.get("equity", 0) or 0),
        "account_type": str(state.get("account_type", "margin")).lower(),
    }


def _recent_trade_log():
    trades = _load_json(TRADE_LOG_FILE, [])
    if not isinstance(trades, list):
        return []
    return [t for t in trades if isinstance(t, dict)]


def _rolling_5_business_day_cutoff():
    # simple rolling 7 calendar days approximation for now
    # good enough for engine control; can be upgraded later
    return datetime.now() - timedelta(days=7)


def count_recent_day_trades():
    cutoff = _rolling_5_business_day_cutoff()
    trades = _recent_trade_log()

    round_trips = 0
    for t in trades:
        ts = t.get("timestamp")
        status = str(t.get("status", "")).upper()
        opened = t.get("opened_at")
        closed = t.get("closed_at")

        if status != "CLOSED":
            continue

        try:
            ref = datetime.fromisoformat(closed or ts)
        except Exception:
            continue

        if ref < cutoff:
            continue

        try:
            open_dt = datetime.fromisoformat(opened) if opened else None
            close_dt = datetime.fromisoformat(closed) if closed else None
        except Exception:
            open_dt = None
            close_dt = None

        if open_dt and close_dt and open_dt.date() == close_dt.date():
            round_trips += 1

    return round_trips


def would_create_day_trade(open_position, action="close"):
    if action != "close":
        return False

    if not isinstance(open_position, dict):
        return False

    opened_at = open_position.get("opened_at")
    if not opened_at:
        return False

    try:
        opened_dt = datetime.fromisoformat(opened_at)
    except Exception:
        return False

    return opened_dt.date() == datetime.now().date()


def pdt_status_preview():
    profile = get_account_profile()
    equity = profile["equity"]
    account_type = profile["account_type"]
    recent_day_trades = count_recent_day_trades()

    restricted = account_type == "margin" and equity < 25000

    remaining = None
    if restricted:
        remaining = max(0, 3 - recent_day_trades)

    return {
        "account_type": account_type,
        "equity": equity,
        "pdt_restricted": restricted,
        "recent_day_trades": recent_day_trades,
        "remaining_day_trades": remaining,
    }


def can_open_new_position():
    profile = get_account_profile()
    return {
        "blocked": False,
        "reason": None,
        "meta": {
            "account_type": profile["account_type"],
            "equity": profile["equity"],
        }
    }


def can_close_position(open_position, emergency=False):
    profile = get_account_profile()
    equity = profile["equity"]
    account_type = profile["account_type"]

    if account_type != "margin":
        return {
            "blocked": False,
            "reason": None,
            "meta": {
                "account_type": account_type,
                "equity": equity,
                "pdt_restricted": False,
            }
        }

    if equity >= 25000:
        return {
            "blocked": False,
            "reason": None,
            "meta": {
                "account_type": account_type,
                "equity": equity,
                "pdt_restricted": False,
            }
        }

    if emergency:
        return {
            "blocked": False,
            "reason": None,
            "meta": {
                "account_type": account_type,
                "equity": equity,
                "pdt_restricted": True,
                "emergency_override": True,
            }
        }

    if not would_create_day_trade(open_position, action="close"):
        return {
            "blocked": False,
            "reason": None,
            "meta": {
                "account_type": account_type,
                "equity": equity,
                "pdt_restricted": True,
                "would_create_day_trade": False,
            }
        }

    recent_day_trades = count_recent_day_trades()
    if recent_day_trades >= 3:
        return {
            "blocked": True,
            "reason": "pdt_limit_under_25k",
            "meta": {
                "account_type": account_type,
                "equity": equity,
                "pdt_restricted": True,
                "recent_day_trades": recent_day_trades,
                "remaining_day_trades": 0,
            }
        }

    return {
        "blocked": False,
        "reason": None,
        "meta": {
            "account_type": account_type,
            "equity": equity,
            "pdt_restricted": True,
            "recent_day_trades": recent_day_trades,
            "remaining_day_trades": max(0, 3 - recent_day_trades),
        }
    }
