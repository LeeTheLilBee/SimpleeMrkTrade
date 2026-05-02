from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.canonical_trade_state import (
    build_open_trade_state,
    build_closed_trade_state,
    build_trade_log_row,
    build_execution_audit_row,
)

OPEN_FILE = "data/open_positions.json"
POSITIONS_FILE = "data/positions.json"
LEGACY_USER_POSITIONS_FILE = "data/user_positions.json"
CLOSED_FILE = "data/closed_positions.json"
CANONICAL_LEDGER_FILE = "data/canonical_ledger.json"


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


def _ensure_parent(path_str: str) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)


def _read_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return deepcopy(default)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return deepcopy(default)


def _write_json(path_str: str, payload: Any) -> None:
    _ensure_parent(path_str)
    with open(path_str, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _load_open_positions() -> List[Dict[str, Any]]:
    rows = _read_json(OPEN_FILE, [])
    return rows if isinstance(rows, list) else []


def _load_closed_positions() -> List[Dict[str, Any]]:
    rows = _read_json(CLOSED_FILE, [])
    return rows if isinstance(rows, list) else []


def _load_canonical_ledger() -> List[Dict[str, Any]]:
    rows = _read_json(CANONICAL_LEDGER_FILE, [])
    return rows if isinstance(rows, list) else []


def _write_open_positions(rows: List[Dict[str, Any]]) -> None:
    _write_json(OPEN_FILE, rows)
    _write_json(POSITIONS_FILE, rows)
    _write_json(LEGACY_USER_POSITIONS_FILE, rows)


def _write_closed_positions(rows: List[Dict[str, Any]]) -> None:
    _write_json(CLOSED_FILE, rows)


def _best_mode(payload: Dict[str, Any], mode: str = "") -> str:
    payload = _safe_dict(payload)
    return _safe_str(mode or payload.get("trading_mode") or payload.get("execution_mode") or payload.get("mode"), "")


def _best_mode_context(payload: Dict[str, Any], mode_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = _safe_dict(payload)
    merged = {}
    if isinstance(payload.get("mode_context"), dict):
        merged.update(payload.get("mode_context"))
    if isinstance(mode_context, dict):
        merged.update(mode_context)
    return merged


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


def _append_trade_log_event(event_type: str, trade_state: Dict[str, Any]) -> None:
    payload = build_trade_log_row(trade_state, event=event_type)
    _append_ledger_event(event_type, payload)


def _append_audit_event(event_type: str, trade_state: Dict[str, Any], note: str = "", extra: Optional[Dict[str, Any]] = None) -> None:
    payload = build_execution_audit_row(
        trade_state,
        event_type=event_type,
        note=note,
        extra=extra or {},
    )
    _append_ledger_event(event_type, payload)


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
        pos = _safe_dict(pos)
        pos_symbol = _norm_symbol(pos.get("symbol"))
        pos_trade_id = _safe_str(pos.get("trade_id"), "")
        pos_opened_at = _safe_str(pos.get("opened_at"), "")

        if trade_id and pos_trade_id == trade_id:
            return idx
        if symbol and opened_at and pos_symbol == symbol and pos_opened_at == opened_at:
            return idx
    return -1


def _find_closed_index(closed_positions: List[Dict[str, Any]], trade_id: str = "") -> int:
    trade_id = _safe_str(trade_id, "")
    if not trade_id:
        return -1
    for idx, row in enumerate(closed_positions):
        if _safe_str(_safe_dict(row).get("trade_id"), "") == trade_id:
            return idx
    return -1


def _normalize_open_trade(
    source_trade: Dict[str, Any],
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_trade = deepcopy(_safe_dict(source_trade))
    lifecycle = deepcopy(_safe_dict(lifecycle))
    execution_result = deepcopy(_safe_dict(execution_result))

    resolved_mode = _best_mode(source_trade, mode=mode)
    resolved_mode_context = _best_mode_context(source_trade, mode_context=mode_context)

    state = build_open_trade_state(
        source_trade,
        lifecycle=lifecycle,
        execution_result=execution_result,
        mode=resolved_mode,
        mode_context=resolved_mode_context,
    )

    state["status"] = "OPEN"
    state["timestamp"] = _safe_str(state.get("timestamp"), _now_iso())
    state["opened_at"] = _safe_str(state.get("opened_at"), state["timestamp"])
    state["closed_at"] = ""
    state["exit_price"] = 0.0
    state["close_reason"] = ""
    state["exit_explanation"] = _safe_dict(state.get("exit_explanation"))
    return state


def _normalize_closed_trade(
    position: Dict[str, Any],
    *,
    exit_price: Optional[float] = None,
    close_reason: str = "",
    closed_at: str = "",
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    position = deepcopy(_safe_dict(position))

    normalized = build_closed_trade_state(
        position,
        exit_price=float(exit_price if exit_price is not None else position.get("exit_price", 0.0) or 0.0),
        close_reason=_safe_str(close_reason or position.get("close_reason") or position.get("reason"), "manual"),
        closed_at=_safe_str(closed_at, _now_iso()),
        pnl=float(pnl if pnl is not None else position.get("pnl", 0.0) or 0.0),
        exit_explanation=_safe_dict(exit_explanation or position.get("exit_explanation")),
        capital_release=_safe_dict(capital_release or position.get("capital_release")),
    )
    normalized["status"] = "CLOSED"
    return normalized


def clear_open_positions() -> None:
    _write_open_positions([])
    _append_ledger_event(
        "OPEN_CLEAR",
        {"symbol": "", "trade_id": "", "note": "All open positions cleared."},
    )


def open_count() -> int:
    return len(_load_open_positions())


def show_positions() -> List[Dict[str, Any]]:
    return _load_open_positions()


def show_closed_positions() -> List[Dict[str, Any]]:
    return _load_closed_positions()


def get_position(symbol: str, trade_id: str = "") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    for pos in _load_open_positions():
        pos = _safe_dict(pos)
        if trade_id and _safe_str(pos.get("trade_id"), "") == trade_id:
            return pos
        if symbol and _norm_symbol(pos.get("symbol")) == symbol:
            return pos
    return None


def add_position(
    trade: Dict[str, Any],
    allow_replace: bool = False,
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    normalized = _normalize_open_trade(
        trade,
        lifecycle=lifecycle,
        execution_result=execution_result,
        mode=mode,
        mode_context=mode_context,
    )

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
                f"Open position already exists for {normalized.get('symbol')} ({normalized.get('trade_id')})."
            )
        prior = _safe_dict(open_positions[idx])
        merged = dict(prior)
        merged.update(normalized)
        normalized = _normalize_open_trade(merged)
        open_positions[idx] = normalized
        event_type = "POSITION_REPLACED_ON_ADD"
    else:
        open_positions.append(normalized)
        event_type = "POSITION_OPENED"

    _write_open_positions(open_positions)
    _append_trade_log_event(event_type, normalized)
    _append_audit_event(event_type, normalized, note="Open position stored.")
    return normalized


def replace_position(
    symbol: str,
    updated_position: Dict[str, Any],
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    updated_position = deepcopy(_safe_dict(updated_position))

    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=symbol or _norm_symbol(updated_position.get("symbol")),
        trade_id=_safe_str(updated_position.get("trade_id"), ""),
        opened_at=_safe_str(updated_position.get("opened_at"), ""),
    )

    if idx < 0:
        return None

    prior = _safe_dict(open_positions[idx])
    merged = dict(prior)
    merged.update(updated_position)

    normalized = _normalize_open_trade(
        merged,
        lifecycle=lifecycle,
        execution_result=execution_result,
        mode=mode,
        mode_context=mode_context,
    )
    normalized["symbol"] = _norm_symbol(normalized.get("symbol", symbol))
    normalized["status"] = "OPEN"

    open_positions[idx] = normalized
    _write_open_positions(open_positions)
    _append_trade_log_event("POSITION_UPDATED", normalized)
    _append_audit_event("POSITION_UPDATED", normalized, note="Open position updated.")
    return normalized


def remove_position(symbol: str, trade_id: str = "", reason: str = "removed") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    open_positions = _load_open_positions()

    idx = _find_open_index(open_positions, symbol=symbol, trade_id=trade_id)
    if idx < 0:
        return None

    removed = _safe_dict(open_positions.pop(idx))
    _write_open_positions(open_positions)

    payload = dict(removed)
    payload["remove_reason"] = _safe_str(reason, "removed")
    _append_trade_log_event("POSITION_REMOVED", payload)
    _append_audit_event("POSITION_REMOVED", payload, note=payload["remove_reason"])
    return removed


def archive_closed_position(
    position: Dict[str, Any],
    *,
    exit_price: Optional[float] = None,
    close_reason: str = "",
    closed_at: str = "",
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    closed_positions = _load_closed_positions()

    normalized = _normalize_closed_trade(
        position,
        exit_price=exit_price,
        close_reason=close_reason,
        closed_at=closed_at,
        pnl=pnl,
        exit_explanation=exit_explanation,
        capital_release=capital_release,
    )

    existing_idx = _find_closed_index(
        closed_positions,
        trade_id=_safe_str(normalized.get("trade_id"), ""),
    )

    if existing_idx >= 0:
        prior = _safe_dict(closed_positions[existing_idx])
        merged = dict(prior)
        merged.update(normalized)
        normalized = _normalize_closed_trade(merged)
        closed_positions[existing_idx] = normalized
        event_type = "POSITION_CLOSED_UPDATED"
    else:
        closed_positions.append(normalized)
        event_type = "POSITION_CLOSED"

    _write_closed_positions(closed_positions)
    _append_trade_log_event(event_type, normalized)
    _append_audit_event(event_type, normalized, note=normalized.get("close_reason", "closed"))
    return normalized


def close_position(
    symbol: str,
    *,
    trade_id: str = "",
    exit_price: Optional[float] = None,
    close_reason: str = "manual",
    closed_at: str = "",
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    open_positions = _load_open_positions()

    idx = _find_open_index(open_positions, symbol=symbol, trade_id=trade_id)
    if idx < 0:
        return None

    open_trade = _safe_dict(open_positions.pop(idx))
    _write_open_positions(open_positions)

    closed = archive_closed_position(
        open_trade,
        exit_price=exit_price,
        close_reason=close_reason,
        closed_at=closed_at,
        pnl=pnl,
        exit_explanation=exit_explanation,
        capital_release=capital_release,
    )
    return closed


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
            pos.get("fused_score", pos.get("score")),
            "| vehicle:",
            pos.get("vehicle_selected"),
            "| entry:",
            pos.get("entry", pos.get("price")),
            "| stop:",
            pos.get("stop"),
            "| target:",
            pos.get("target"),
            "| trade_id:",
            pos.get("trade_id"),
            "| opened_at:",
            pos.get("opened_at"),
        )


def print_closed_positions() -> None:
    positions = _load_closed_positions()
    print("CLOSED POSITIONS:")
    if not positions:
        print("No closed positions.")
        return

    for pos in positions:
        print(
            pos.get("symbol"),
            pos.get("strategy"),
            "| pnl:",
            pos.get("pnl"),
            "| exit_price:",
            pos.get("exit_price"),
            "| trade_id:",
            pos.get("trade_id"),
            "| closed_at:",
            pos.get("closed_at"),
            "| reason:",
            pos.get("close_reason"),
        )
