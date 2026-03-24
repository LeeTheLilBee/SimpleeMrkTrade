import json
from pathlib import Path
from datetime import datetime

TRADE_FILE = "data/trade_log.json"


def load_trades():
    if not Path(TRADE_FILE).exists():
        return []
    with open(TRADE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def entries_today():
    today = datetime.now().date()
    count = 0

    for trade in load_trades():
        ts = _parse_ts(trade.get("timestamp"))
        if ts and ts.date() == today:
            count += 1

    return count


def closes_today():
    today = datetime.now().date()
    count = 0

    for trade in load_trades():
        ts = _parse_ts(trade.get("closed_at"))
        if ts and ts.date() == today and str(trade.get("status", "")).upper() == "CLOSED":
            count += 1

    return count


def round_trips_today():
    today = datetime.now().date()
    count = 0

    for trade in load_trades():
        open_ts = _parse_ts(trade.get("timestamp"))
        close_ts = _parse_ts(trade.get("closed_at"))

        if not open_ts or not close_ts:
            continue

        if open_ts.date() == today and close_ts.date() == today:
            count += 1

    return count


def realized_pnl_today():
    today = datetime.now().date()
    total = 0.0

    for trade in load_trades():
        ts = _parse_ts(trade.get("closed_at"))
        if ts and ts.date() == today:
            total += float(trade.get("pnl", 0) or 0)

    return round(total, 2)


def performance_summary():
    trades = load_trades()

    wins = 0
    losses = 0
    pnl_total = 0.0

    equity = 1000.0
    peak = equity
    drawdown = 0.0

    for trade in trades:
        pnl = float(trade.get("pnl", 0) or 0)
        pnl_total += pnl

        if pnl > 0:
            wins += 1
        elif pnl < 0:
            losses += 1

        equity += pnl
        if equity > peak:
            peak = equity

        dd = peak - equity
        if dd > drawdown:
            drawdown = dd

    total = len(trades)
    winrate = round(wins / total, 2) if total > 0 else 0

    return {
        "trades": total,
        "wins": wins,
        "losses": losses,
        "winrate": winrate,
        "total_pnl": round(pnl_total, 2),
        "max_drawdown": round(drawdown, 2),
        "entries_today": entries_today(),
        "closes_today": closes_today(),
        "round_trips_today": round_trips_today(),
        "realized_pnl_today": realized_pnl_today(),
    }
