from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _parse_dt(value: Any) -> Optional[datetime]:
    """
    Parse a timestamp and normalize it to naive UTC.

    Why:
    Some rows are stored as naive ISO timestamps:
        2026-05-03T00:30:55.734071

    Some rows may be timezone-aware:
        2026-05-03T00:30:55.734071+00:00

    Python crashes if we compare naive and aware datetimes directly.
    This function makes all parsed datetimes comparable.
    """
    if value is None or value == "":
        return None

    if isinstance(value, datetime):
        dt = value
    else:
        text = _safe_str(value, "")
        if not text:
            return None

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(text)
        except Exception:
            return None

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt


def _now_naive_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_account_profile():
    state = _load_json(ACCOUNT_STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}

    return {
        "equity": _safe_float(state.get("equity", 0), 0.0),
        "account_type": _safe_str(state.get("account_type", "margin"), "margin").lower(),
    }


def _recent_trade_log() -> List[Dict[str, Any]]:
    trades = _load_json(TRADE_LOG_FILE, [])
    if not isinstance(trades, list):
        return []
    return [t for t in trades if isinstance(t, dict)]


def _rolling_5_business_day_cutoff():
    # Simple rolling 7 calendar days approximation for now.
    # Good enough for engine control; can be upgraded later.
    return _now_naive_utc() - timedelta(days=7)


def count_recent_day_trades():
    cutoff = _rolling_5_business_day_cutoff()
    trades = _recent_trade_log()

    round_trips = 0

    for t in trades:
        status = _safe_str(t.get("status", ""), "").upper()
        if status != "CLOSED":
            continue

        ts = t.get("timestamp")
        opened = t.get("opened_at")
        closed = t.get("closed_at")

        ref = _parse_dt(closed or ts)
        if ref is None:
            continue

        # Both ref and cutoff are now naive UTC, so this cannot crash.
        if ref < cutoff:
            continue

        open_dt = _parse_dt(opened)
        close_dt = _parse_dt(closed)

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

    opened_dt = _parse_dt(opened_at)
    if opened_dt is None:
        return False

    return opened_dt.date() == _now_naive_utc().date()


def pdt_status_preview():
    profile = get_account_profile()
    equity = profile["equity"]
    account_type = profile["account_type"]
    recent_day_trades = count_recent_day_trades()

    pdt_sensitive = account_type == "margin" and equity < 25000
    pdt_restricted = pdt_sensitive and recent_day_trades >= 3

    remaining = None
    if pdt_sensitive:
        remaining = max(0, 3 - recent_day_trades)

    return {
        "account_type": account_type,
        "equity": equity,
        "pdt_sensitive": pdt_sensitive,
        "pdt_restricted": pdt_restricted,
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
        },
    }


def can_open_position(*args, **kwargs):
    """
    Compatibility alias for callers that expect can_open_position.
    Opening a position does not itself create a day trade.
    """
    return can_open_new_position()


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
            },
        }

    if equity >= 25000:
        return {
            "blocked": False,
            "reason": None,
            "meta": {
                "account_type": account_type,
                "equity": equity,
                "pdt_restricted": False,
            },
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
            },
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
            },
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
                "would_create_day_trade": True,
            },
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
            "would_create_day_trade": True,
        },
    }
