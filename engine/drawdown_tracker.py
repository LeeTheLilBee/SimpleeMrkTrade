import json
from pathlib import Path

TRADE_FILE="data/trade_log.json"
FILE="data/drawdown_history.json"

def build_drawdown_history():

    equity=1000
    peak=equity
    history=[]

    if Path(TRADE_FILE).exists():

        with open(TRADE_FILE) as f:
            trades=json.load(f)

        for t in trades:

            equity+=t.get("pnl",0)

            if equity>peak:
                peak=equity

            dd=peak-equity

            history.append({
                "equity":equity,
                "drawdown":dd
            })

    with open(FILE,"w") as f:
        json.dump(history,f,indent=2)

    return history
