import json
from pathlib import Path

TRADE_FILE = "data/trade_log.json"

def load_trades():
    if not Path(TRADE_FILE).exists():
        return []
    with open(TRADE_FILE, "r") as f:
        return json.load(f)

def performance_summary():
    trades = load_trades()

    wins = 0
    losses = 0
    pnl_total = 0

    equity = 1000
    peak = equity
    drawdown = 0

    for trade in trades:
        pnl = trade.get("pnl", 0)
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
        "max_drawdown": round(drawdown, 2)
    }
