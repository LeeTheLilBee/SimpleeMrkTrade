from __future__ import annotations
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

FILE = "data/trade_timeline.json"
MAX_ROWS = 1000


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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _ensure_parent() -> None:
    Path(FILE).parent.mkdir(parents=True, exist_ok=True)


def _load() -> List[Dict[str, Any]]:
    path = Path(FILE)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save(data: List[Dict[str, Any]]) -> None:
    _ensure_parent()
    trimmed = data[-MAX_ROWS:] if isinstance(data, list) else []
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, indent=2)


def add_trade_timeline_event(symbol, stage, details=None):
    data = _load()
    details = _safe_dict(details)

    entry = {
        "timestamp": _now_iso(),
        "symbol": _norm_symbol(symbol),
        "event": _safe_str(stage, "UNKNOWN").upper(),
        "trade_id": _safe_str(details.get("trade_id"), ""),
        "strategy": _safe_str(details.get("strategy"), ""),
        "source": _safe_str(details.get("source"), ""),
        "mode": _safe_str(details.get("mode", details.get("trading_mode")), ""),
        "details": deepcopy(details),
    }

    data.append(entry)
    _save(data)
    return entry


def load_trade_timeline(limit=None):
    data = _load()
    if isinstance(limit, int) and limit > 0:
        return data[-limit:]
    return data
