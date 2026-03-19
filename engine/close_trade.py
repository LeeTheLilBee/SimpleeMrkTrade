import json
from pathlib import Path
from engine.account_state import apply_realized_pnl
from engine.trade_timeline import add_timeline_event
from engine.bot_logger import log_bot
from engine.live_activity import push_activity

OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"
TRADE_LOG = "data/trade_log.json"

def _load(path, default):
    if not Path(path).exists():
        return default
    with open(path, "r") as f:
        return json.load(f)

def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def close_position(symbol, exit_price, reason):
    open_positions = _load(OPEN_FILE, [])
    closed_positions = _load(CLOSED_FILE, [])
    trade_log = _load(TRADE_LOG, [])

    remaining = []
    closed = None

    for pos in open_positions:
        if closed is None and pos["symbol"] == symbol:
            entry = float(pos["price"])
            pnl = exit_price - entry if pos["strategy"] == "CALL" else entry - exit_price
            pos["exit_price"] = round(exit_price, 2)
            pos["reason"] = reason
            pos["pnl"] = round(pnl, 2)
            closed = pos
        else:
            remaining.append(pos)

    _save(OPEN_FILE, remaining)

    if closed is not None:
        closed_positions.append(closed)
        _save(CLOSED_FILE, closed_positions)

        for trade in reversed(trade_log):
            if trade["symbol"] == symbol and trade.get("status") == "OPEN":
                trade["status"] = "CLOSED"
                trade["exit_price"] = round(exit_price, 2)
                trade["reason"] = reason
                trade["pnl"] = round(closed["pnl"], 2)
                break

        _save(TRADE_LOG, trade_log)
        apply_realized_pnl(closed["pnl"])
        add_timeline_event(symbol, "CLOSED", {
            "exit_price": round(exit_price, 2),
            "reason": reason,
            "pnl": round(closed["pnl"], 2)
        })
        log_bot(f"Closed {symbol} at {exit_price} due to {reason}", "INFO")
        push_activity(
            "CLOSE",
            f"{symbol} closed for {round(closed['pnl'], 2)} due to {reason}",
            symbol=symbol,
            meta={"exit_price": round(exit_price, 2), "pnl": round(closed["pnl"], 2), "reason": reason}
        )

    return closed
