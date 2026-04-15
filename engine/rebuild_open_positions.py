from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

OPEN_FILE = "data/open_positions.json"
POSITIONS_FILE = "data/positions.json"
ACCOUNT_STATE_FILE = "data/account_state.json"
TRADE_LOG_FILE = "data/trade_log.json"
CLOSED_FILE = "data/closed_positions.json"

def _read_json(path: str, default: Any):
    p = Path(path)
    if not p.exists():
        return default
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _write_json(path: str, data: Any):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

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
        return float(value)
    except Exception:
        return float(default)

def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()

def rebuild_open_positions():
    account_state = _safe_dict(_read_json(ACCOUNT_STATE_FILE, {}))
    trade_history = _safe_list(account_state.get("trade_history", []))
    closed_positions = _safe_list(_read_json(CLOSED_FILE, []))
    trade_log = _safe_list(_read_json(TRADE_LOG_FILE, []))

    closed_trade_ids = set()
    closed_symbol_timestamps = set()

    for row in closed_positions:
        if not isinstance(row, dict):
            continue
        trade_id = _safe_str(row.get("trade_id"), "")
        if trade_id:
            closed_trade_ids.add(trade_id)
        symbol = _norm_symbol(row.get("symbol"))
        opened_at = _safe_str(row.get("opened_at"), "")
        if symbol and opened_at:
            closed_symbol_timestamps.add((symbol, opened_at))

    open_rows: List[Dict[str, Any]] = []

    for trade in trade_history:
        if not isinstance(trade, dict):
            continue
        if _safe_str(trade.get("status"), "").upper() != "OPEN":
            continue

        symbol = _norm_symbol(trade.get("symbol"))
        opened_at = _safe_str(trade.get("timestamp"), "")
        trade_id = _safe_str(trade.get("trade_id"), "")

        if trade_id and trade_id in closed_trade_ids:
            continue
        if symbol and opened_at and (symbol, opened_at) in closed_symbol_timestamps:
            continue

        price = _safe_float(trade.get("price", 0.0), 0.0)
        size = _safe_float(trade.get("size", 1.0), 1.0)

        if not symbol or price <= 0 or size <= 0:
            continue

        row = {
            "symbol": symbol,
            "strategy": _safe_str(trade.get("strategy"), "CALL").upper(),
            "price": round(price, 4),
            "entry": round(price, 4),
            "current_price": round(price, 4),
            "stop": round(price * 0.98, 4),
            "target": round(price * 1.04, 4),
            "size": size,
            "score": _safe_float(trade.get("score", 0.0), 0.0),
            "confidence": _safe_str(trade.get("confidence"), "UNKNOWN").upper(),
            "opened_at": opened_at,
            "timestamp": opened_at,
            "status": "OPEN",
            "trade_id": trade_id or f"{symbol}-CALL-{opened_at.replace(':','').replace('-','').replace('.','')}",
            "source": "rebuild_open_positions",
        }
        open_rows.append(row)

    deduped: List[Dict[str, Any]] = []
    seen = set()
    for row in open_rows:
        key = (_norm_symbol(row.get("symbol")), _safe_str(row.get("trade_id"), ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    _write_json(OPEN_FILE, deduped)
    _write_json(POSITIONS_FILE, deduped)

    print("REBUILT OPEN POSITIONS:", len(deduped))
    for row in deduped[:20]:
        print(
            row.get("symbol"),
            "| entry:", row.get("entry"),
            "| size:", row.get("size"),
            "| opened_at:", row.get("opened_at"),
            "| trade_id:", row.get("trade_id"),
        )

if __name__ == "__main__":
    rebuild_open_positions()
