from __future__ import annotations
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path("data/user_portfolios")
BASE_DIR.mkdir(parents=True, exist_ok=True)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _now_iso() -> str:
    return datetime.now().isoformat()


def _normalize_username(username: Any) -> str:
    text = _safe_str(username, "unknown_user").lower().replace(" ", "_")
    return "".join(ch for ch in text if ch.isalnum() or ch in {"_", "-"})


def _portfolio_path(username):
    return BASE_DIR / f"{_normalize_username(username)}_portfolio.json"


def _default_portfolio(username=""):
    return {
        "username": _normalize_username(username),
        "broker": None,
        "linked": False,
        "positions": [],
        "cash": 0.0,
        "buying_power": 0.0,
        "notes": "",
        "updated_at": _now_iso(),
    }


def _normalize_position(row: Any) -> Dict[str, Any]:
    row = _safe_dict(row)
    return {
        "symbol": _safe_str(row.get("symbol"), "").upper(),
        "strategy": _safe_str(row.get("strategy"), ""),
        "shares": int(_safe_float(row.get("shares"), 0)),
        "contracts": int(_safe_float(row.get("contracts"), 0)),
        "entry": round(_safe_float(row.get("entry"), 0.0), 4),
        "current_price": round(_safe_float(row.get("current_price"), 0.0), 4),
        "stop": round(_safe_float(row.get("stop"), 0.0), 4),
        "target": round(_safe_float(row.get("target"), 0.0), 4),
        "vehicle_selected": _safe_str(row.get("vehicle_selected", row.get("vehicle", "")), "").upper(),
        "notes": _safe_str(row.get("notes"), ""),
    }


def load_user_portfolio(username):
    path = _portfolio_path(username)
    if not path.exists():
        return _default_portfolio(username)

    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        return _default_portfolio(username)

    payload = _safe_dict(payload)
    out = _default_portfolio(username)
    out.update(payload)

    out["username"] = _normalize_username(username)
    out["broker"] = _safe_str(out.get("broker"), "") or None
    out["linked"] = bool(out.get("linked", False))
    out["cash"] = round(_safe_float(out.get("cash"), 0.0), 2)
    out["buying_power"] = round(_safe_float(out.get("buying_power"), 0.0), 2)
    out["notes"] = _safe_str(out.get("notes"), "")
    out["positions"] = [_normalize_position(p) for p in _safe_list(out.get("positions"))]
    out["updated_at"] = _safe_str(out.get("updated_at"), _now_iso())
    return out


def save_user_portfolio(username, payload):
    current = load_user_portfolio(username)
    incoming = _safe_dict(payload)

    current.update(incoming)
    current["username"] = _normalize_username(username)
    current["broker"] = _safe_str(current.get("broker"), "") or None
    current["linked"] = bool(current.get("linked", False))
    current["cash"] = round(_safe_float(current.get("cash"), 0.0), 2)
    current["buying_power"] = round(_safe_float(current.get("buying_power"), 0.0), 2)
    current["notes"] = _safe_str(current.get("notes"), "")
    current["positions"] = [_normalize_position(p) for p in _safe_list(current.get("positions"))]
    current["updated_at"] = _now_iso()

    path = _portfolio_path(username)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)

    return current


def save_mock_portfolio_from_form(username, broker, cash, buying_power, notes, positions):
    payload = {
        "broker": _safe_str(broker, "") or None,
        "linked": True,
        "cash": _safe_float(cash, 0.0),
        "buying_power": _safe_float(buying_power, 0.0),
        "notes": _safe_str(notes, ""),
        "positions": _safe_list(positions),
    }
    return save_user_portfolio(username, payload)


def clear_user_portfolio(username):
    payload = _default_portfolio(username)
    return save_user_portfolio(username, payload)
