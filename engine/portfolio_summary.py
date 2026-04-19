from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _read_json(path_str: str, default: Any):
    path = Path(path_str)
    if not path.exists():
        return default
    try:
        with open(path_str, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def portfolio_summary():
    open_positions = _safe_list(_read_json(OPEN_FILE, []))
    closed_positions = _safe_list(_read_json(CLOSED_FILE, []))

    realized = 0.0
    unrealized = 0.0
    gross_capital_open = 0.0
    vehicle_mix = {"OPTION": 0, "STOCK": 0, "RESEARCH_ONLY": 0, "UNKNOWN": 0}

    for pos in closed_positions:
        if not isinstance(pos, dict):
            continue
        realized += _safe_float(pos.get("pnl", 0.0), 0.0)

    for pos in open_positions:
        if not isinstance(pos, dict):
            continue

        unrealized += _safe_float(
            pos.get("unrealized_pnl", pos.get("pnl", 0.0)),
            0.0,
        )
        gross_capital_open += _safe_float(
            pos.get("capital_required", pos.get("entry", pos.get("price", 0.0))),
            0.0,
        )

        vehicle = _safe_str(
            pos.get("vehicle_selected", pos.get("vehicle", "UNKNOWN")),
            "UNKNOWN",
        ).upper()
        if vehicle not in vehicle_mix:
            vehicle = "UNKNOWN"
        vehicle_mix[vehicle] += 1

    return {
        "open_positions": len(open_positions),
        "closed_positions": len(closed_positions),
        "realized_pnl": round(realized, 2),
        "unrealized_pnl": round(unrealized, 2),
        "gross_capital_open": round(gross_capital_open, 2),
        "vehicle_mix": vehicle_mix,
        "net_pnl": round(realized + unrealized, 2),
    }
