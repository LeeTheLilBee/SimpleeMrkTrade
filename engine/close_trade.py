import json
from pathlib import Path
from datetime import datetime

from engine.trade_timeline import add_timeline_event
from engine.pdt_guard import can_close_position
from engine.account_state import release_trade_cap
from engine.explainability_engine import explain_exit

OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"
TRADE_LOG = "data/trade_log.json"


def _load(path, default):
    file_path = Path(path)
    if not file_path.exists():
        return default
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def close_position(symbol, exit_price, reason="manual"):
    open_positions = _load(OPEN_FILE, [])
    closed_positions = _load(CLOSED_FILE, [])
    trade_log = _load(TRADE_LOG, [])

    matched = None
    remaining = []

    for pos in open_positions:
        if matched is None and pos.get("symbol") == symbol:
            matched = pos
        else:
            remaining.append(pos)

    if not matched:
        return {
            "closed": False,
            "blocked": False,
            "reason": "position_not_found",
        }

    emergency = ("risk" in str(reason).lower()) or ("stop" in str(reason).lower())
    pdt_check = can_close_position(matched, emergency=emergency)

    if pdt_check.get("blocked"):
        return {
            "closed": False,
            "blocked": True,
            "reason": pdt_check.get("reason"),
            "meta": pdt_check.get("meta", {}),
        }

    exit_price = float(exit_price or 0)
    entry_price = float(matched.get("entry", matched.get("price", 0)) or 0)
    size = float(matched.get("size", 1) or 1)
    strategy = matched.get("strategy", "CALL")

    if strategy == "PUT":
        pnl = (entry_price - exit_price) * size
    else:
        pnl = (exit_price - entry_price) * size

    matched["exit_price"] = round(exit_price, 2)
    matched["closed_at"] = datetime.now().isoformat()
    matched["reason"] = reason
    matched["status"] = "CLOSED"
    matched["pnl"] = round(pnl, 2)
    matched["exit_explanation"] = explain_exit(reason, pnl)

    # restore principal + pnl back into account state
    capital_release = release_trade_cap(
        entry_price=entry_price,
        size=size,
        pnl=pnl,
        immediate=True,
    )

    closed_positions.append(matched)

    for trade in reversed(trade_log):
        if trade.get("symbol") == symbol and trade.get("status") == "OPEN":
            trade["status"] = "CLOSED"
            trade["exit_price"] = round(float(exit_price), 2)
            trade["closed_at"] = matched["closed_at"]
            trade["reason"] = reason
            trade["pnl"] = round(pnl, 2)
            trade["exit_explanation"] = matched["exit_explanation"]
            break

    _save(OPEN_FILE, remaining)
    _save(CLOSED_FILE, closed_positions)
    _save(TRADE_LOG, trade_log)

    add_timeline_event(symbol, "CLOSED", {
        "exit_price": round(exit_price, 2),
        "reason": reason,
        "pnl": round(pnl, 2),
        "size": size,
    })

    return {
        "closed": True,
        "blocked": False,
        "symbol": symbol,
        "exit_price": round(exit_price, 2),
        "reason": reason,
        "pnl": round(pnl, 2),
        "capital_release": capital_release,
        "meta": pdt_check.get("meta", {}),
    }
