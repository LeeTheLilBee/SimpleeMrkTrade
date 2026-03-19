import json
from pathlib import Path

FILE = "data/closed_positions.json"

def closed_trade_stats():
    if not Path(FILE).exists():
        return {
            "closed_trades": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0,
            "realized_pnl": 0,
            "avg_win": 0,
            "avg_loss": 0
        }

    with open(FILE, "r") as f:
        trades = json.load(f)

    pnls = [float(t.get("pnl", 0)) for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]

    total = len(pnls)
    winrate = round(len(wins) / total, 2) if total else 0

    return {
        "closed_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "winrate": winrate,
        "realized_pnl": round(sum(pnls), 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0
    }
