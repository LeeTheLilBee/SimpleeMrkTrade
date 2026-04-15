from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"
POSITIONS_FILE = "data/positions.json"
CANONICAL_LEDGER_FILE = "data/canonical_ledger.json"


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


def _now_iso() -> str:
    return datetime.now().isoformat()


def _read_json(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _write_json(path: str, data: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_open_positions() -> List[Dict[str, Any]]:
    rows = _read_json(OPEN_FILE, [])
    return [row for row in _safe_list(rows) if isinstance(row, dict)]


def _load_closed_positions() -> List[Dict[str, Any]]:
    rows = _read_json(CLOSED_FILE, [])
    return [row for row in _safe_list(rows) if isinstance(row, dict)]


def _load_canonical_ledger() -> List[Dict[str, Any]]:
    rows = _read_json(CANONICAL_LEDGER_FILE, [])
    return [row for row in _safe_list(rows) if isinstance(row, dict)]


def _trade_identity(trade: Dict[str, Any]) -> str:
    trade = _safe_dict(trade)
    trade_id = _safe_str(trade.get("trade_id"), "")
    if trade_id:
        return trade_id
    symbol = _norm_symbol(trade.get("symbol"))
    strategy = _safe_str(trade.get("strategy"), "UNKNOWN").upper()
    opened_at = _safe_str(trade.get("opened_at"), trade.get("timestamp"))
    return f"{symbol}|{strategy}|{opened_at}"


def _position_identity(symbol: str, trade_id: str = "", opened_at: str = "") -> str:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    opened_at = _safe_str(opened_at, "")
    if trade_id:
        return f"{symbol}|{trade_id}"
    return f"{symbol}|{opened_at}" if opened_at else symbol


def _normalize_trade(raw_trade: Dict[str, Any]) -> Dict[str, Any]:
    trade = deepcopy(_safe_dict(raw_trade))

    symbol = _norm_symbol(trade.get("symbol"))
    if not symbol:
        raise ValueError("Trade is missing symbol.")

    strategy = _safe_str(trade.get("strategy"), "CALL").upper()
    price = _safe_float(
        trade.get("entry", trade.get("fill_price", trade.get("price", 0.0))),
        0.0,
    )
    current_price = _safe_float(trade.get("current_price", price), price)
    stop = _safe_float(trade.get("stop", round(price * 0.97, 2)), round(price * 0.97, 2))
    target = _safe_float(trade.get("target", round(price * 1.04, 2)), round(price * 1.04, 2))
    size = _safe_float(trade.get("size", 1.0), 1.0)

    opened_at = _safe_str(trade.get("opened_at"), "")
    timestamp = _safe_str(trade.get("timestamp"), opened_at or _now_iso())
    if not opened_at:
        opened_at = timestamp

    normalized = dict(trade)
    normalized["symbol"] = symbol
    normalized["strategy"] = strategy
    normalized["price"] = round(price, 4)
    normalized["entry"] = round(price, 4)
    normalized["current_price"] = round(current_price, 4)
    normalized["stop"] = round(stop, 4)
    normalized["target"] = round(target, 4)
    normalized["size"] = size
    normalized["opened_at"] = opened_at
    normalized["timestamp"] = timestamp
    normalized["status"] = _safe_str(trade.get("status"), "OPEN").upper()

    if not _safe_str(normalized.get("trade_id"), ""):
        normalized["trade_id"] = (
            f"{symbol}-{strategy}-{opened_at.replace(':', '').replace('-', '').replace('.', '')}"
        )

    return normalized


def _append_ledger_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    ledger = _load_canonical_ledger()
    event = {
        "timestamp": _now_iso(),
        "event_type": _safe_str(event_type, "UNKNOWN").upper(),
        "symbol": _norm_symbol(payload.get("symbol")),
        "trade_id": _safe_str(payload.get("trade_id"), ""),
        "payload": deepcopy(_safe_dict(payload)),
    }
    ledger.append(event)
    _write_json(CANONICAL_LEDGER_FILE, ledger)
    return event


def _sync_positions_mirror(open_positions: Optional[List[Dict[str, Any]]] = None) -> None:
    if open_positions is None:
        open_positions = _load_open_positions()
    _write_json(POSITIONS_FILE, open_positions)


def _find_open_index(
    open_positions: List[Dict[str, Any]],
    *,
    symbol: str,
    trade_id: str = "",
    opened_at: str = "",
) -> int:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    opened_at = _safe_str(opened_at, "")

    for idx, pos in enumerate(open_positions):
        pos_symbol = _norm_symbol(pos.get("symbol"))
        pos_trade_id = _safe_str(pos.get("trade_id"), "")
        pos_opened_at = _safe_str(pos.get("opened_at"), "")

        if trade_id and pos_trade_id == trade_id:
            return idx
        if symbol and opened_at and pos_symbol == symbol and pos_opened_at == opened_at:
            return idx
        if symbol and not trade_id and not opened_at and pos_symbol == symbol:
            return idx

    return -1


def clear_open_positions() -> None:
    _write_json(OPEN_FILE, [])
    _sync_positions_mirror([])
    _append_ledger_event("OPEN_CLEAR", {"symbol": "", "trade_id": "", "note": "All open positions cleared."})


def open_count() -> int:
    return len(_load_open_positions())


def show_positions() -> List[Dict[str, Any]]:
    return _load_open_positions()


def get_position(symbol: str, trade_id: str = "") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    for pos in _load_open_positions():
        if trade_id and _safe_str(pos.get("trade_id"), "") == trade_id:
            return pos
        if symbol and _norm_symbol(pos.get("symbol")) == symbol:
            return pos
    return None


def add_position(trade: Dict[str, Any], allow_replace: bool = False) -> Dict[str, Any]:
    normalized = _normalize_trade(trade)
    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=normalized.get("symbol", ""),
        trade_id=normalized.get("trade_id", ""),
        opened_at=normalized.get("opened_at", ""),
    )

    if idx >= 0:
        if not allow_replace:
            raise ValueError(
                f"Open position already exists for {normalized.get('symbol')} "
                f"({normalized.get('trade_id')})."
            )
        open_positions[idx] = normalized
        event_type = "POSITION_REPLACED_ON_ADD"
    else:
        open_positions.append(normalized)
        event_type = "POSITION_OPENED"

    _write_json(OPEN_FILE, open_positions)
    _sync_positions_mirror(open_positions)
    _append_ledger_event(event_type, normalized)
    return normalized


def replace_position(symbol: str, updated_position: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    updated = _normalize_trade(updated_position)
    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=symbol or updated.get("symbol", ""),
        trade_id=updated.get("trade_id", ""),
        opened_at=updated.get("opened_at", ""),
    )

    if idx < 0:
        return None

    prior = _safe_dict(open_positions[idx])
    merged = dict(prior)
    merged.update(updated)
    merged["symbol"] = _norm_symbol(merged.get("symbol", symbol))
    merged["status"] = "OPEN"

    open_positions[idx] = merged
    _write_json(OPEN_FILE, open_positions)
    _sync_positions_mirror(open_positions)
    _append_ledger_event("POSITION_UPDATED", merged)
    return merged


def remove_position(symbol: str, trade_id: str = "", reason: str = "removed") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    open_positions = _load_open_positions()

    idx = _find_open_index(open_positions, symbol=symbol, trade_id=trade_id)
    if idx < 0:
        return None

    removed = open_positions.pop(idx)
    _write_json(OPEN_FILE, open_positions)
    _sync_positions_mirror(open_positions)

    event_payload = dict(removed)
    event_payload["remove_reason"] = _safe_str(reason, "removed")
    _append_ledger_event("POSITION_REMOVED", event_payload)
    return removed


def archive_closed_position(closed_trade: Dict[str, Any]) -> Dict[str, Any]:
    closed_positions = _load_closed_positions()
    normalized = deepcopy(_safe_dict(closed_trade))
    normalized["symbol"] = _norm_symbol(normalized.get("symbol"))
    normalized["status"] = "CLOSED"
    normalized["closed_at"] = _safe_str(normalized.get("closed_at"), _now_iso())

    trade_id = _safe_str(normalized.get("trade_id"), "")
    exists = False
    for item in closed_positions:
        if trade_id and _safe_str(item.get("trade_id"), "") == trade_id:
            exists = True
            break

    if not exists:
        closed_positions.append(normalized)
        _write_json(CLOSED_FILE, closed_positions)
        _append_ledger_event("POSITION_CLOSED", normalized)

    return normalized


def print_positions() -> None:
    positions = _load_open_positions()
    print("OPEN POSITIONS:")
    if not positions:
        print("No open positions.")
        return

    for pos in positions:
        print(
            pos.get("symbol"),
            pos.get("strategy"),
            pos.get("score"),
            "| entry:",
            pos.get("entry", pos.get("price")),
            "| stop:",
            pos.get("stop"),
            "| target:",
            pos.get("target"),
            "| size:",
            pos.get("size"),
            "| opened_at:",
            pos.get("opened_at"),
            "| trade_id:",
            pos.get("trade_id"),
        )
