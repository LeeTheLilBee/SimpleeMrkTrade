from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from engine.account_state import release_trade_cap
from engine.explainability_engine import explain_exit
from engine.pdt_guard import can_close_position
from engine.paper_portfolio import (
    archive_closed_position,
    get_position,
    remove_position,
    show_positions,
)
from engine.trade_timeline import add_timeline_event

TRADE_LOG = "data/trade_log.json"
TRADE_DETAILS = "data/trade_details.json"


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


def _normalize_reason(reason: Any) -> str:
    return _safe_str(reason, "manual").lower().replace(" ", "_")


def _now_iso() -> str:
    return datetime.now().isoformat()


def _load(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path: str, data: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _update_trade_log_close(
    symbol: str,
    trade_id: str,
    close_payload: Dict[str, Any],
) -> None:
    trade_log = _load(TRADE_LOG, [])
    trade_log = _safe_list(trade_log)

    matched = False
    for row in reversed(trade_log):
        if not isinstance(row, dict):
            continue

        row_symbol = _norm_symbol(row.get("symbol"))
        row_trade_id = _safe_str(row.get("trade_id"), "")
        row_status = _safe_str(row.get("status"), "").upper()

        same_trade = trade_id and row_trade_id == trade_id
        same_symbol_open = (not trade_id) and row_symbol == symbol and row_status == "OPEN"

        if same_trade or same_symbol_open:
            row["status"] = "CLOSED"
            row["exit_price"] = close_payload.get("exit_price")
            row["closed_at"] = close_payload.get("closed_at")
            row["reason"] = close_payload.get("reason")
            row["pnl"] = close_payload.get("pnl")
            row["exit_explanation"] = close_payload.get("exit_explanation")
            matched = True
            break

    if not matched:
        trade_log.append(
            {
                "timestamp": close_payload.get("closed_at"),
                "trade_id": trade_id,
                "symbol": symbol,
                "strategy": close_payload.get("strategy"),
                "price": close_payload.get("entry"),
                "size": close_payload.get("size"),
                "score": close_payload.get("score"),
                "confidence": close_payload.get("confidence"),
                "status": "CLOSED",
                "pnl": close_payload.get("pnl"),
                "exit_price": close_payload.get("exit_price"),
                "closed_at": close_payload.get("closed_at"),
                "reason": close_payload.get("reason"),
                "exit_explanation": close_payload.get("exit_explanation"),
            }
        )

    _save(TRADE_LOG, trade_log)


def _append_trade_details_close(close_payload: Dict[str, Any]) -> None:
    details = _load(TRADE_DETAILS, [])
    details = _safe_list(details)

    details.append(
        {
            "trade_id": close_payload.get("trade_id"),
            "timestamp": close_payload.get("closed_at"),
            "symbol": close_payload.get("symbol"),
            "strategy": close_payload.get("strategy"),
            "source": "close_trade",
            "event": "CLOSED",
            "entry": close_payload.get("entry"),
            "exit_price": close_payload.get("exit_price"),
            "size": close_payload.get("size"),
            "pnl": close_payload.get("pnl"),
            "reason": close_payload.get("reason"),
            "exit_explanation": close_payload.get("exit_explanation"),
        }
    )

    _save(TRADE_DETAILS, details)


def close_position(symbol: str, exit_price: float, reason: str = "manual", trade_id: str = "") -> Dict[str, Any]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    reason = _normalize_reason(reason)

    matched = get_position(symbol, trade_id=trade_id)
    if not matched:
        return {
            "closed": False,
            "blocked": False,
            "reason": "position_not_found",
            "symbol": symbol,
            "trade_id": trade_id,
        }

    matched = dict(matched)
    emergency = ("risk" in reason) or ("stop" in reason)

    pdt_check = can_close_position(matched, emergency=emergency)
    if isinstance(pdt_check, dict) and pdt_check.get("blocked"):
        return {
            "closed": False,
            "blocked": True,
            "reason": pdt_check.get("reason"),
            "symbol": symbol,
            "trade_id": _safe_str(matched.get("trade_id"), trade_id),
            "meta": pdt_check.get("meta", {}),
        }

    exit_price = _safe_float(exit_price, 0.0)
    entry_price = _safe_float(matched.get("entry", matched.get("price", 0.0)), 0.0)
    size = _safe_float(matched.get("size", 1.0), 1.0)
    strategy = _safe_str(matched.get("strategy"), "CALL").upper()

    if strategy == "PUT":
        pnl = (entry_price - exit_price) * size
    else:
        pnl = (exit_price - entry_price) * size
    pnl = round(pnl, 2)

    closed_at = _now_iso()
    resolved_trade_id = _safe_str(matched.get("trade_id"), trade_id)

    exit_explanation = explain_exit(
        {
            "symbol": symbol,
            "pnl": pnl,
            "reason": reason,
            "exit_reason": reason,
            "decision_reason": reason,
            "position": matched,
            "exit_price": round(exit_price, 2),
        }
    )

    close_payload = dict(matched)
    close_payload["symbol"] = symbol
    close_payload["trade_id"] = resolved_trade_id
    close_payload["exit_price"] = round(exit_price, 2)
    close_payload["closed_at"] = closed_at
    close_payload["reason"] = reason
    close_payload["status"] = "CLOSED"
    close_payload["pnl"] = pnl
    close_payload["exit_explanation"] = exit_explanation
    close_payload["entry"] = round(entry_price, 4)
    close_payload["size"] = size
    close_payload["strategy"] = strategy

    removed = remove_position(symbol, trade_id=resolved_trade_id, reason=reason)
    if not removed:
        return {
            "closed": False,
            "blocked": False,
            "reason": "position_remove_failed",
            "symbol": symbol,
            "trade_id": resolved_trade_id,
        }

    archived = archive_closed_position(close_payload)

    capital_release = release_trade_cap(
        entry_price=entry_price,
        size=size,
        pnl=pnl,
        immediate=True,
    )

    _update_trade_log_close(symbol, resolved_trade_id, close_payload)
    _append_trade_details_close(close_payload)

    try:
        add_timeline_event(
            symbol,
            "CLOSED",
            {
                "trade_id": resolved_trade_id,
                "exit_price": round(exit_price, 2),
                "reason": reason,
                "pnl": pnl,
                "size": size,
            },
        )
    except Exception as e:
        print(f"[TIMELINE_CLOSE_EVENT:{symbol}] {e}")

    return {
        "closed": True,
        "blocked": False,
        "symbol": symbol,
        "trade_id": resolved_trade_id,
        "exit_price": round(exit_price, 2),
        "reason": reason,
        "pnl": pnl,
        "capital_release": capital_release,
        "archived": bool(archived),
        "remaining_open_positions": len(show_positions()),
        "meta": pdt_check.get("meta", {}) if isinstance(pdt_check, dict) else {},
    }
