from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

TRADE_LOG_FILE = "data/trade_log.json"
CANONICAL_LEDGER_FILE = "data/canonical_ledger.json"

try:
    from engine.canonical_trade_state import (
        build_trade_log_row,
        build_execution_audit_row,
    )
except Exception:
    build_trade_log_row = None
    build_execution_audit_row = None


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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        return bool(value)
    except Exception:
        return bool(default)


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


def _load_trade_log_rows() -> List[Dict[str, Any]]:
    rows = _read_json(TRADE_LOG_FILE, [])
    return rows if isinstance(rows, list) else []


def _save_trade_log_rows(rows: List[Dict[str, Any]]) -> None:
    _write_json(TRADE_LOG_FILE, rows)


def _load_canonical_ledger_rows() -> List[Dict[str, Any]]:
    rows = _read_json(CANONICAL_LEDGER_FILE, [])
    return rows if isinstance(rows, list) else []


def _save_canonical_ledger_rows(rows: List[Dict[str, Any]]) -> None:
    _write_json(CANONICAL_LEDGER_FILE, rows)


def _best_price(payload: Dict[str, Any]) -> float:
    payload = _safe_dict(payload)
    option_obj = _safe_dict(payload.get("option"))
    execution_result = _safe_dict(payload.get("execution_result"))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    candidates = [
        payload.get("fill_price"),
        execution_result.get("fill_price"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        payload.get("entry"),
        payload.get("requested_price"),
        payload.get("price"),
        payload.get("current_price"),
        payload.get("market_price"),
        payload.get("underlying_price"),
        payload.get("latest_price"),
        option_obj.get("mark"),
        option_obj.get("last"),
    ]
    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return price
    return 0.0


def _derive_trade_id(symbol: str, strategy: str, opened_at: str) -> str:
    clean_ts = _safe_str(opened_at, _now_iso()).replace(":", "").replace("-", "").replace(".", "")
    return f"{symbol}-{strategy}-{clean_ts}"


def _normalize_trade_log_row(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = deepcopy(_safe_dict(payload))

    if callable(build_trade_log_row):
        try:
            row = build_trade_log_row(payload, event=_safe_str(payload.get("status"), "OPEN").upper())
            row["company_name"] = _safe_str(payload.get("company_name", payload.get("company", row.get("symbol", "UNKNOWN"))), row.get("symbol", "UNKNOWN"))
            row["sector"] = _safe_str(payload.get("sector"), "")
            row["option"] = _safe_dict(payload.get("option"))
            row["execution_result"] = _safe_dict(payload.get("execution_result"))
            row["exit_explanation"] = _safe_dict(payload.get("exit_explanation"))
            return row
        except Exception:
            pass

    symbol = _norm_symbol(payload.get("symbol"))
    strategy = _safe_str(payload.get("strategy"), "CALL").upper()
    timestamp = _safe_str(payload.get("timestamp"), _now_iso())
    opened_at = _safe_str(payload.get("opened_at"), timestamp)
    closed_at = _safe_str(payload.get("closed_at"), "")

    vehicle_selected = _safe_str(
        payload.get("vehicle_selected", payload.get("selected_vehicle", payload.get("vehicle", "STOCK"))),
        "STOCK",
    ).upper()
    if vehicle_selected not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        vehicle_selected = "STOCK"

    price = round(_best_price(payload), 4)
    entry = round(_safe_float(payload.get("entry", price), price), 4)
    fill_price = round(_safe_float(payload.get("fill_price", entry), entry), 4)
    requested_price = round(_safe_float(payload.get("requested_price", price), price), 4)
    current_price = round(_safe_float(payload.get("current_price", fill_price), fill_price), 4)
    exit_price = round(_safe_float(payload.get("exit_price", 0.0), 0.0), 4)

    shares = _safe_int(payload.get("shares", payload.get("size", 0)), 0)
    contracts = _safe_int(payload.get("contracts", 0), 0)
    size = _safe_int(payload.get("size", 0), 0)

    if vehicle_selected == "OPTION":
        contracts = max(1, contracts or size or 1)
        shares = 0
        size = contracts
    elif vehicle_selected == "STOCK":
        shares = max(1, shares or size or 1)
        contracts = 0
        size = shares
    else:
        shares = 0
        contracts = 0
        size = 0

    trade_id = _safe_str(payload.get("trade_id"), "")
    if not trade_id:
        trade_id = _derive_trade_id(symbol, strategy, opened_at)

    status = _safe_str(payload.get("status"), "OPEN").upper()
    if status not in {"OPEN", "CLOSED"}:
        status = "OPEN"

    return {
        "trade_id": trade_id,
        "timestamp": timestamp,
        "opened_at": opened_at,
        "closed_at": closed_at,
        "symbol": symbol,
        "company_name": _safe_str(payload.get("company_name", payload.get("company", symbol)), symbol),
        "sector": _safe_str(payload.get("sector"), ""),
        "strategy": strategy,
        "vehicle_selected": vehicle_selected,
        "vehicle": vehicle_selected,
        "shares": shares,
        "contracts": contracts,
        "size": size,
        "price": price,
        "entry": entry,
        "fill_price": fill_price,
        "requested_price": requested_price,
        "current_price": current_price,
        "exit_price": exit_price,
        "score": round(_safe_float(payload.get("score", payload.get("fused_score", 0.0)), 0.0), 4),
        "fused_score": round(_safe_float(payload.get("fused_score", payload.get("score", 0.0)), 0.0), 4),
        "confidence": _safe_str(payload.get("confidence"), "LOW").upper(),
        "status": status,
        "pnl": round(_safe_float(payload.get("pnl", 0.0), 0.0), 4),
        "reason": _safe_str(payload.get("reason", payload.get("close_reason", "")), ""),
        "decision_reason": _safe_str(payload.get("decision_reason"), ""),
        "final_reason": _safe_str(payload.get("final_reason"), ""),
        "final_reason_code": _safe_str(payload.get("final_reason_code"), ""),
        "research_approved": _safe_bool(payload.get("research_approved"), False),
        "execution_ready": _safe_bool(payload.get("execution_ready"), False),
        "selected_for_execution": _safe_bool(payload.get("selected_for_execution"), False),
        "capital_required": round(_safe_float(payload.get("capital_required", 0.0), 0.0), 4),
        "minimum_trade_cost": round(_safe_float(payload.get("minimum_trade_cost", 0.0), 0.0), 4),
        "capital_available": round(_safe_float(payload.get("capital_available", 0.0), 0.0), 4),
        "trading_mode": _safe_str(payload.get("trading_mode"), ""),
        "mode": _safe_str(payload.get("mode"), ""),
        "regime": _safe_str(payload.get("regime"), ""),
        "breadth": _safe_str(payload.get("breadth"), ""),
        "volatility_state": _safe_str(payload.get("volatility_state"), ""),
        "option": _safe_dict(payload.get("option")),
        "execution_result": _safe_dict(payload.get("execution_result")),
        "exit_explanation": _safe_dict(payload.get("exit_explanation")),
    }


def _build_audit_row(
    trade_state: Dict[str, Any],
    *,
    event_type: str,
    note: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    extra = _safe_dict(extra)

    if callable(build_execution_audit_row):
        try:
            return build_execution_audit_row(
                trade_state,
                event_type=event_type,
                note=note,
                extra=extra,
            )
        except Exception:
            pass

    row = {
        "timestamp": _now_iso(),
        "event_type": _safe_str(event_type, "UNKNOWN").upper(),
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "status": _safe_str(trade_state.get("status"), ""),
        "vehicle_selected": _safe_str(trade_state.get("vehicle_selected"), "STOCK").upper(),
        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),
        "note": _safe_str(note, ""),
        "payload": deepcopy(trade_state),
    }
    row.update(extra)
    return row


def _append_ledger_event(
    event_type: str,
    trade_state: Dict[str, Any],
    note: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    rows = _load_canonical_ledger_rows()
    row = _build_audit_row(
        trade_state,
        event_type=event_type,
        note=note,
        extra=extra,
    )
    rows.append(row)
    _save_canonical_ledger_rows(rows)
    return row


def _find_trade_index(
    trades: List[Dict[str, Any]],
    *,
    trade_id: str = "",
    symbol: str = "",
    opened_at: str = "",
    status: str = "",
) -> int:
    trade_id = _safe_str(trade_id, "")
    symbol = _norm_symbol(symbol)
    opened_at = _safe_str(opened_at, "")
    status = _safe_str(status, "").upper()

    for idx, row in enumerate(_safe_list(trades)):
        row = _safe_dict(row)
        row_trade_id = _safe_str(row.get("trade_id"), "")
        row_symbol = _norm_symbol(row.get("symbol"))
        row_opened_at = _safe_str(row.get("opened_at", row.get("timestamp", "")), "")
        row_status = _safe_str(row.get("status"), "").upper()

        if trade_id and row_trade_id == trade_id:
            return idx

        if not trade_id and symbol and opened_at:
            if row_symbol == symbol and row_opened_at == opened_at:
                if not status or row_status == status:
                    return idx

        if not trade_id and symbol and not opened_at:
            if row_symbol == symbol:
                if not status or row_status == status:
                    return idx

    return -1


def load_trade_log() -> List[Dict[str, Any]]:
    return _load_trade_log_rows()


def get_open_trade_rows() -> List[Dict[str, Any]]:
    return [
        row for row in _load_trade_log_rows()
        if _safe_str(row.get("status"), "").upper() == "OPEN"
    ]


def get_closed_trade_rows() -> List[Dict[str, Any]]:
    return [
        row for row in _load_trade_log_rows()
        if _safe_str(row.get("status"), "").upper() == "CLOSED"
    ]


def get_trade_log_row(trade_id: str = "", symbol: str = "", opened_at: str = "") -> Optional[Dict[str, Any]]:
    trades = _load_trade_log_rows()
    idx = _find_trade_index(
        trades,
        trade_id=trade_id,
        symbol=symbol,
        opened_at=opened_at,
    )
    if idx < 0:
        return None
    return _safe_dict(trades[idx])


def log_trade_open_from_position(position: Dict[str, Any]) -> Dict[str, Any]:
    trades = _load_trade_log_rows()
    row = _normalize_trade_log_row(position)
    row["status"] = "OPEN"
    row["closed_at"] = ""
    row["exit_price"] = 0.0
    row["pnl"] = round(_safe_float(row.get("pnl", 0.0), 0.0), 4)

    idx = _find_trade_index(
        trades,
        trade_id=row.get("trade_id", ""),
        symbol=row.get("symbol", ""),
        opened_at=row.get("opened_at", ""),
    )

    if idx >= 0:
        existing = _safe_dict(trades[idx])
        merged = dict(existing)
        merged.update(row)
        merged["status"] = "OPEN"
        merged["closed_at"] = ""
        merged["exit_price"] = 0.0
        trades[idx] = _normalize_trade_log_row(merged)
    else:
        trades.append(row)

    _save_trade_log_rows(trades)
    _append_ledger_event(
        "TRADE_OPEN",
        row,
        note=f"{row.get('symbol')} opened and logged.",
    )
    return row


def log_trade_open(
    symbol,
    strategy,
    price,
    size,
    score,
    confidence,
    trade_id: str = "",
    vehicle_selected: str = "STOCK",
) -> Dict[str, Any]:
    now = _now_iso()
    payload = {
        "trade_id": trade_id,
        "timestamp": now,
        "opened_at": now,
        "symbol": symbol,
        "strategy": strategy,
        "price": price,
        "entry": price,
        "fill_price": price,
        "size": size,
        "score": score,
        "fused_score": score,
        "confidence": confidence,
        "vehicle_selected": vehicle_selected,
        "status": "OPEN",
        "pnl": 0.0,
    }
    return log_trade_open_from_position(payload)


def log_trade_close_from_position(position: Dict[str, Any]) -> Dict[str, Any]:
    trades = _load_trade_log_rows()
    row = _normalize_trade_log_row(position)
    row["status"] = "CLOSED"
    row["closed_at"] = _safe_str(row.get("closed_at"), _now_iso())

    idx = _find_trade_index(
        trades,
        trade_id=row.get("trade_id", ""),
        symbol=row.get("symbol", ""),
    )

    if idx >= 0:
        existing = _safe_dict(trades[idx])
        merged = dict(existing)
        merged.update(row)
        merged["status"] = "CLOSED"
        merged["closed_at"] = _safe_str(merged.get("closed_at"), _now_iso())
        trades[idx] = _normalize_trade_log_row(merged)
        final_row = trades[idx]
    else:
        trades.append(row)
        final_row = row

    _save_trade_log_rows(trades)
    _append_ledger_event(
        "TRADE_CLOSE",
        final_row,
        note=f"{final_row.get('symbol')} closed and logged.",
    )
    return final_row


def log_trade_close(
    symbol,
    pnl: float,
    *,
    trade_id: str = "",
    exit_price: float = 0.0,
    close_reason: str = "",
) -> Dict[str, Any]:
    existing = get_trade_log_row(trade_id=trade_id, symbol=symbol) or {}
    payload = dict(existing)
    payload.update({
        "symbol": symbol,
        "trade_id": trade_id or existing.get("trade_id", ""),
        "status": "CLOSED",
        "closed_at": _now_iso(),
        "pnl": round(_safe_float(pnl, 0.0), 4),
        "exit_price": round(_safe_float(exit_price, 0.0), 4),
        "close_reason": _safe_str(close_reason, ""),
        "reason": _safe_str(close_reason, ""),
    })
    return log_trade_close_from_position(payload)


def log_trade_update(payload: Dict[str, Any]) -> Dict[str, Any]:
    trades = _load_trade_log_rows()
    row = _normalize_trade_log_row(payload)

    idx = _find_trade_index(
        trades,
        trade_id=row.get("trade_id", ""),
        symbol=row.get("symbol", ""),
        opened_at=row.get("opened_at", ""),
    )

    if idx >= 0:
        existing = _safe_dict(trades[idx])
        merged = dict(existing)
        merged.update(row)
        final_row = _normalize_trade_log_row(merged)
        trades[idx] = final_row
    else:
        final_row = row
        trades.append(final_row)

    _save_trade_log_rows(trades)
    _append_ledger_event(
        "TRADE_UPDATE",
        final_row,
        note=f"{final_row.get('symbol')} trade row updated.",
    )
    return final_row


def upsert_trade_row(payload: Dict[str, Any]) -> Dict[str, Any]:
    return log_trade_update(payload)


def append_trade_audit_event(
    trade_state: Dict[str, Any],
    *,
    event_type: str,
    note: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return _append_ledger_event(
        event_type,
        trade_state,
        note=note,
        extra=extra,
    )


def dedupe_trade_log() -> Dict[str, Any]:
    trades = _load_trade_log_rows()
    deduped: List[Dict[str, Any]] = []
    seen_by_trade_id: Dict[str, int] = {}
    removed = 0

    for raw in trades:
        row = _normalize_trade_log_row(raw)
        trade_id = _safe_str(row.get("trade_id"), "")

        if not trade_id:
            deduped.append(row)
            continue

        if trade_id not in seen_by_trade_id:
            seen_by_trade_id[trade_id] = len(deduped)
            deduped.append(row)
            continue

        existing_idx = seen_by_trade_id[trade_id]
        existing = _safe_dict(deduped[existing_idx])

        merged = dict(existing)
        existing_status = _safe_str(existing.get("status"), "").upper()
        row_status = _safe_str(row.get("status"), "").upper()

        if existing_status == "OPEN" and row_status == "CLOSED":
            merged.update(row)
        else:
            merged.update({k: v for k, v in row.items() if v not in ("", None, [], {})})

        deduped[existing_idx] = _normalize_trade_log_row(merged)
        removed += 1

    _save_trade_log_rows(deduped)

    return {
        "ok": True,
        "original_count": len(trades),
        "deduped_count": len(deduped),
        "removed_duplicates": removed,
    }


__all__ = [
    "load_trade_log",
    "get_trade_log_row",
    "get_open_trade_rows",
    "get_closed_trade_rows",
    "log_trade_open",
    "log_trade_open_from_position",
    "log_trade_close",
    "log_trade_close_from_position",
    "log_trade_update",
    "upsert_trade_row",
    "append_trade_audit_event",
    "dedupe_trade_log",
]
