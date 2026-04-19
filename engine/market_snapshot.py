from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


FILE = "data/market_snapshot.json"


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _write_json(path_str: str, payload: Any) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)
    with open(path_str, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def save_market_snapshot(regime, breadth, mode, watchlist_count, approved_count):
    payload: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "regime": _safe_str(regime, "UNKNOWN"),
        "breadth": _safe_str(breadth, "UNKNOWN"),
        "mode": _safe_str(mode, "UNKNOWN"),
        "watchlist_count": _safe_int(watchlist_count, 0),
        "approved_count": _safe_int(approved_count, 0),
    }
    _write_json(FILE, payload)
    return payload
