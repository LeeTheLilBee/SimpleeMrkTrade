from datetime import datetime

def log_trade_state(positions):
    journal = []

    for p in positions:
        journal.append({
            "symbol": p["symbol"],
            "health": p["health"]["score"],
            "action": p["health"]["action"],
            "timestamp": datetime.now().isoformat()
        })

    return journal%%writefile /content/SimpleeMrkTrade/engine/trade_journal.py
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import json

from engine.paper_portfolio import show_positions, show_closed_positions
from engine.canonical_trade_state import summarize_trade_state


JOURNAL_FILE = "data/trade_journal.json"


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
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _read_json(path: str, default: Any) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _build_open_journal_row(position: Dict[str, Any]) -> Dict[str, Any]:
    position = _safe_dict(position)
    summary = summarize_trade_state(position)

    return {
        "timestamp": _now_iso(),
        "journal_type": "OPEN_POSITION_SNAPSHOT",
        "status": "OPEN",
        "trade_id": _safe_str(position.get("trade_id"), ""),
        "symbol": _norm_symbol(position.get("symbol")),
        "strategy": _safe_str(position.get("strategy"), "CALL").upper(),
        "vehicle_selected": _safe_str(position.get("vehicle_selected"), "STOCK").upper(),
        "entry": round(_safe_float(position.get("entry", 0.0), 0.0), 4),
        "current_price": round(_safe_float(position.get("current_price", 0.0), 0.0), 4),
        "stop": round(_safe_float(position.get("stop", 0.0), 0.0), 4),
        "target": round(_safe_float(position.get("target", 0.0), 0.0), 4),
        "pnl": round(_safe_float(position.get("pnl", 0.0), 0.0), 4),
        "readiness_score": round(_safe_float(position.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(position.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(position.get("rebuild_pressure", 0.0), 0.0), 4),
        "v2_score": round(_safe_float(position.get("v2_score", 0.0), 0.0), 4),
        "v2_reason": _safe_str(position.get("v2_reason"), ""),
        "monitoring_price_type": _safe_str(position.get("monitoring_price_type"), ""),
        "final_reason": _safe_str(position.get("final_reason"), ""),
        "monitor_debug": _safe_dict(position.get("monitor_debug")),
        "summary": summary,
    }


def _build_closed_journal_row(position: Dict[str, Any]) -> Dict[str, Any]:
    position = _safe_dict(position)
    summary = summarize_trade_state(position)

    return {
        "timestamp": _now_iso(),
        "journal_type": "CLOSED_POSITION_SNAPSHOT",
        "status": "CLOSED",
        "trade_id": _safe_str(position.get("trade_id"), ""),
        "symbol": _norm_symbol(position.get("symbol")),
        "strategy": _safe_str(position.get("strategy"), "CALL").upper(),
        "vehicle_selected": _safe_str(position.get("vehicle_selected"), "STOCK").upper(),
        "entry": round(_safe_float(position.get("entry", 0.0), 0.0), 4),
        "exit_price": round(_safe_float(position.get("exit_price", 0.0), 0.0), 4),
        "pnl": round(_safe_float(position.get("pnl", 0.0), 0.0), 4),
        "close_reason": _safe_str(position.get("close_reason", position.get("reason", "")), ""),
        "final_reason": _safe_str(position.get("final_reason"), ""),
        "summary": summary,
    }


def build_trade_journal_snapshot() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    try:
        open_positions = show_positions()
    except Exception:
        open_positions = []

    try:
        closed_positions = show_closed_positions()
    except Exception:
        closed_positions = []

    for position in _safe_list(open_positions):
        if isinstance(position, dict):
            rows.append(_build_open_journal_row(position))

    for position in _safe_list(closed_positions):
        if isinstance(position, dict):
            rows.append(_build_closed_journal_row(position))

    rows.sort(key=lambda row: _safe_str(row.get("timestamp"), ""), reverse=True)
    return rows


def write_trade_journal_snapshot() -> List[Dict[str, Any]]:
    rows = build_trade_journal_snapshot()
    _write_json(JOURNAL_FILE, rows)
    return rows


def read_trade_journal() -> List[Dict[str, Any]]:
    rows = _read_json(JOURNAL_FILE, [])
    return rows if isinstance(rows, list) else []


def log_trade_state(positions=None) -> List[Dict[str, Any]]:
    """
    Compatibility wrapper for older callers.
    If positions are passed, snapshot those.
    Otherwise snapshot canonical open/closed portfolio state.
    """
    if isinstance(positions, list):
        rows = []
        for position in positions:
            if isinstance(position, dict):
                status = _safe_str(position.get("status"), "OPEN").upper()
                if status == "CLOSED":
                    rows.append(_build_closed_journal_row(position))
                else:
                    rows.append(_build_open_journal_row(position))
        _write_json(JOURNAL_FILE, rows)
        return rows

    return write_trade_journal_snapshot()
