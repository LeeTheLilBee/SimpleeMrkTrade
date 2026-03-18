import json
from pathlib import Path

FILE = "data/trade_log.json"

def executed_trade_count():
    if not Path(FILE).exists():
        return 0
    with open(FILE, "r") as f:
        trades = json.load(f)
    return len(trades)
