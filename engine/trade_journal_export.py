from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

from engine.trade_journal import read_trade_journal, write_trade_journal_snapshot


EXPORT_FILE = "data/trade_journal_export.csv"


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


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


def _flatten_journal_row(row: Dict[str, Any]) -> Dict[str, Any]:
    row = _safe_dict(row)
    summary = _safe_dict(row.get("summary"))
    monitor_debug = _safe_dict(row.get("monitor_debug"))

    return {
        "timestamp": _safe_str(row.get("timestamp"), ""),
        "journal_type": _safe_str(row.get("journal_type"), ""),
        "status": _safe_str(row.get("status"), ""),
        "trade_id": _safe_str(row.get("trade_id"), ""),
        "symbol": _safe_str(row.get("symbol"), ""),
        "strategy": _safe_str(row.get("strategy"), ""),
        "vehicle_selected": _safe_str(row.get("vehicle_selected"), ""),
        "entry": round(_safe_float(row.get("entry", 0.0), 0.0), 4),
        "current_price": round(_safe_float(row.get("current_price", 0.0), 0.0), 4),
        "option_current_price": round(_safe_float(row.get("option_current_price", 0.0), 0.0), 4),
        "underlying_price": round(_safe_float(row.get("underlying_price", 0.0), 0.0), 4),
        "exit_price": round(_safe_float(row.get("exit_price", 0.0), 0.0), 4),
        "stop": round(_safe_float(row.get("stop", 0.0), 0.0), 4),
        "target": round(_safe_float(row.get("target", 0.0), 0.0), 4),
        "pnl": round(_safe_float(row.get("pnl", 0.0), 0.0), 4),
        "unrealized_pnl": round(_safe_float(row.get("unrealized_pnl", 0.0), 0.0), 4),
        "readiness_score": round(_safe_float(row.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(row.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(row.get("rebuild_pressure", 0.0), 0.0), 4),
        "v2_score": round(_safe_float(row.get("v2_score", 0.0), 0.0), 4),
        "v2_reason": _safe_str(row.get("v2_reason"), ""),
        "monitoring_price_type": _safe_str(row.get("monitoring_price_type"), ""),
        "close_reason": _safe_str(row.get("close_reason"), ""),
        "final_reason": _safe_str(row.get("final_reason"), ""),
        "summary_status": _safe_str(summary.get("status"), ""),
        "summary_final_reason_code": _safe_str(summary.get("final_reason_code"), ""),
        "monitor_action": _safe_str(monitor_debug.get("final_action"), ""),
        "monitor_days_open": round(_safe_float(monitor_debug.get("days_open", 0.0), 0.0), 4),
    }


def export_trade_journal(path: str = EXPORT_FILE, refresh_snapshot: bool = True) -> str:
    if refresh_snapshot:
        rows = write_trade_journal_snapshot()
    else:
        rows = read_trade_journal()

    rows = _safe_list(rows)
    flattened = [_flatten_journal_row(row) for row in rows if isinstance(row, dict)]

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "timestamp",
        "journal_type",
        "status",
        "trade_id",
        "symbol",
        "strategy",
        "vehicle_selected",
        "entry",
        "current_price",
        "option_current_price",
        "underlying_price",
        "exit_price",
        "stop",
        "target",
        "pnl",
        "unrealized_pnl",
        "readiness_score",
        "promotion_score",
        "rebuild_pressure",
        "v2_score",
        "v2_reason",
        "monitoring_price_type",
        "close_reason",
        "final_reason",
        "summary_status",
        "summary_final_reason_code",
        "monitor_action",
        "monitor_days_open",
    ]

    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in flattened:
            writer.writerow(row)

    print(f"Journal exported: {p}")
    return str(p)
