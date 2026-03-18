import json
from pathlib import Path
from engine.portfolio_summary import portfolio_summary

TRADE_FILE = "data/trade_log.json"

def analytics():
    trades = []
    if Path(TRADE_FILE).exists():
        with open(TRADE_FILE, "r") as f:
            trades = json.load(f)

    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    strategies = {}

    for t in trades:
        s = t.get("strategy", "UNKNOWN")
        strategies[s] = strategies.get(s, 0) + 1

    winrate = round(wins / len(trades), 2) if trades else 0

    return {
        "trades": len(trades),
        "winrate": winrate,
        "strategies": strategies,
        "last_trade": trades[-1]["symbol"] if trades else None,
        "portfolio": portfolio_summary()
    }
