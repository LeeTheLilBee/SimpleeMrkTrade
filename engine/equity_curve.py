import json
from pathlib import Path

TRADE_FILE = "data/trade_log.json"
CURVE_FILE = "data/equity_curve.json"

def build_equity_curve():
    equity = 1000
    curve = [equity]

    if Path(TRADE_FILE).exists():
        with open(TRADE_FILE, "r") as f:
            trades = json.load(f)

        for t in trades:
            equity += t.get("pnl", 0)
            curve.append(round(equity, 2))

    with open(CURVE_FILE, "w") as f:
        json.dump(curve, f, indent=2)

    return curve
