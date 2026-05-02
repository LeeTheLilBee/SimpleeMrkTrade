from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from engine.trade_timeline import add_timeline_event
from engine.pdt_guard import can_close_position
from engine.account_state import release_trade_cap
from engine.explainability_engine import explain_exit
from engine.paper_portfolio import archive_closed_position

OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"
TRADE_LOG = "data/trade_log.json"
OPTION_CONTRACT_MULTIPLIER = 100


def _load(path, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path, data):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return default


def _safe_int(value, default=0):
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return default


def _safe_str(value, default=""):
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _normalize_reason(reason):
    return str(reason or "manual").strip().lower().replace(" ", "_")


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "").upper()


def _find_open_position(open_positions: List[Dict[str, Any]], symbol: str, trade_id: str = ""):
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")

    for idx, pos in enumerate(open_positions):
        row = _safe_dict(pos)
        if trade_id and _safe_str(row.get("trade_id"), "") == trade_id:
            return idx, dict(row)
        if symbol and _norm_symbol(row.get("symbol")) == symbol:
            return idx, dict(row)
    return -1, None


def _compute_pnl(position: Dict[str, Any], exit_price: float) -> float:
    vehicle_selected = _safe_str(
        position.get("vehicle_selected", position.get("vehicle", "STOCK")),
        "STOCK",
    ).upper()
    strategy = _safe_str(position.get("strategy", "CALL"), "CALL").upper()
    entry_price = _safe_float(position.get("entry", position.get("price", 0.0)), 0.0)

    if vehicle_selected == "OPTION":
        size = max(1, _safe_int(position.get("contracts", position.get("size", 1)), 1))
        multiplier = OPTION_CONTRACT_MULTIPLIER
    else:
        size = max(1, _safe_int(position.get("shares", position.get("size", 1)), 1))
        multiplier = 1

    if "PUT" in strategy:
        pnl = (entry_price - exit_price) * size * multiplier
    else:
        pnl = (exit_price - entry_price) * size * multiplier

    return round(pnl, 2)


def close_position(symbol, exit_price, reason="manual", trade_id=""):
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    reason = _normalize_reason(reason)

    open_positions = _load(OPEN_FILE, [])
    closed_positions = _load(CLOSED_FILE, [])
    trade_log = _load(TRADE_LOG, [])

    if not isinstance(open_positions, list):
        open_positions = []
    if not isinstance(closed_positions, list):
        closed_positions = []
    if not isinstance(trade_log, list):
        trade_log = []

    idx, matched = _find_open_position(open_positions, symbol=symbol, trade_id=trade_id)

    if matched is None or idx < 0:
        return {
            "closed": False,
            "blocked": False,
            "reason": "position_not_found",
        }

    emergency = ("risk" in reason) or ("stop" in reason)
    pdt_check = can_close_position(matched, emergency=emergency)

    if isinstance(pdt_check, dict) and pdt_check.get("blocked"):
        return {
            "closed": False,
            "blocked": True,
            "reason": pdt_check.get("reason"),
            "meta": pdt_check.get("meta", {}),
        }

    exit_price = _safe_float(exit_price, 0.0)
    if exit_price <= 0:
        exit_price = _safe_float(
            matched.get("option_current_price", matched.get("current_price", matched.get("entry", 0.0))),
            0.0,
        )

    pnl = _compute_pnl(matched, exit_price)
    closed_at = datetime.now().isoformat()

    matched["exit_price"] = round(exit_price, 4)
    matched["closed_at"] = closed_at
    matched["reason"] = reason
    matched["close_reason"] = reason
    matched["status"] = "CLOSED"
    matched["pnl"] = pnl
    matched["realized_pnl"] = pnl
    matched["unrealized_pnl"] = 0.0
    matched["exit_explanation"] = explain_exit(
        reason=reason,
        pnl=pnl,
        position=matched,
        exit_price=exit_price,
    )

    vehicle_selected = _safe_str(
        matched.get("vehicle_selected", matched.get("vehicle", "STOCK")),
        "STOCK",
    ).upper()
    entry_price = _safe_float(matched.get("entry", matched.get("price", 0.0)), 0.0)

    if vehicle_selected == "OPTION":
        size_for_release = max(1, _safe_int(matched.get("contracts", matched.get("size", 1)), 1))
        release_basis_entry = entry_price * OPTION_CONTRACT_MULTIPLIER
    else:
        size_for_release = max(1, _safe_int(matched.get("shares", matched.get("size", 1)), 1))
        release_basis_entry = entry_price

    capital_release = release_trade_cap(
        entry_price=release_basis_entry,
        size=size_for_release,
        pnl=pnl,
        immediate=True,
    )

    try:
        archived = archive_closed_position(
            matched,
            exit_price=exit_price,
            close_reason=reason,
            closed_at=closed_at,
            pnl=pnl,
            exit_explanation=matched["exit_explanation"],
            capital_release=capital_release,
        )
    except Exception:
        archived = matched
        closed_positions.append(matched)
        _save(CLOSED_FILE, closed_positions)

    remaining = [row for i, row in enumerate(open_positions) if i != idx]

    updated_trade = None
    resolved_trade_id = _safe_str(matched.get("trade_id"), "")

    for trade in reversed(trade_log):
        if not isinstance(trade, dict):
            continue

        same_trade_id = resolved_trade_id and _safe_str(trade.get("trade_id"), "") == resolved_trade_id
        same_symbol_open = (
            not resolved_trade_id
            and _safe_str(trade.get("symbol"), "").upper() == symbol
            and _safe_str(trade.get("status"), "").upper() in {"OPEN", "FILLED"}
        )

        if same_trade_id or same_symbol_open:
            trade["status"] = "CLOSED"
            trade["exit_price"] = round(exit_price, 4)
            trade["closed_at"] = closed_at
            trade["reason"] = reason
            trade["close_reason"] = reason
            trade["pnl"] = pnl
            trade["exit_explanation"] = matched["exit_explanation"]
            updated_trade = trade
            break

    _save(OPEN_FILE, remaining)
    _save(TRADE_LOG, trade_log)

    try:
        add_timeline_event(
            symbol,
            "CLOSED",
            {
                "trade_id": matched.get("trade_id"),
                "exit_price": round(exit_price, 4),
                "reason": reason,
                "pnl": pnl,
                "vehicle_selected": vehicle_selected,
                "contracts": matched.get("contracts", 0),
                "shares": matched.get("shares", 0),
            },
        )
    except Exception as e:
        print(f"[TIMELINE_CLOSE_EVENT:{symbol}] {e}")

    return {
        "closed": True,
        "blocked": False,
        "symbol": symbol,
        "trade_id": matched.get("trade_id", ""),
        "exit_price": round(exit_price, 4),
        "reason": reason,
        "pnl": pnl,
        "capital_release": capital_release,
        "meta": pdt_check.get("meta", {}) if isinstance(pdt_check, dict) else {},
        "closed_position": archived,
        "trade_log_row": updated_trade or {},
    }
