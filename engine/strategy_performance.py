import json
from pathlib import Path

FILE = "data/trade_log.json"

def strategy_breakdown():

    if not Path(FILE).exists():
        return {}

    with open(FILE) as f:
        trades = json.load(f)

    stats = {}

    for t in trades:

        strat = t.get("strategy","UNKNOWN")

        if strat not in stats:
            stats[strat] = {
                "trades":0,
                "wins":0,
                "pnl":0
            }

        stats[strat]["trades"] += 1

        pnl = t.get("pnl",0)

        stats[strat]["pnl"] += pnl

        if pnl > 0:
            stats[strat]["wins"] += 1

    for strat in stats:

        trades = stats[strat]["trades"]
        wins = stats[strat]["wins"]

        stats[strat]["winrate"] = round(wins/trades,2) if trades else 0

    return stats
