from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

TRADE_FILE = "data/trade_log.json"
CURVE_FILE = "data/equity_curve.json"
DEFAULT_START_EQUITY = 1000.0


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
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path_str: str, payload: Any) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)
    with open(path_str, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def build_equity_curve(start_equity: float = DEFAULT_START_EQUITY) -> List[Dict[str, Any]]:
    trades = _safe_list(_read_json(TRADE_FILE, []))
    equity = _safe_float(start_equity, DEFAULT_START_EQUITY)

    curve: List[Dict[str, Any]] = [
        {
            "index": 0,
            "equity": round(equity, 2),
            "pnl": 0.0,
            "symbol": "",
            "trade_id": "",
            "timestamp": "",
            "strategy": "",
            "status": "START",
        }
    ]

    running_index = 1
    for row in trades:
        if not isinstance(row, dict):
            continue

        pnl = _safe_float(row.get("pnl", 0.0), 0.0)
        equity = round(equity + pnl, 2)

        curve.append(
            {
                "index": running_index,
                "equity": equity,
                "pnl": round(pnl, 2),
                "symbol": _safe_str(row.get("symbol"), ""),
                "trade_id": _safe_str(row.get("trade_id"), ""),
                "timestamp": _safe_str(
                    row.get("closed_at", row.get("timestamp", row.get("opened_at", ""))),
                    "",
                ),
                "strategy": _safe_str(row.get("strategy"), ""),
                "status": _safe_str(row.get("status"), "CLOSED"),
            }
        )
        running_index += 1

    _write_json(CURVE_FILE, curve)
    return curve
