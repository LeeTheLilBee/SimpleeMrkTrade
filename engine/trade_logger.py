import json
from pathlib import Path
from datetime import datetime

FILE = "data/trade_log.json"

def log_trade_open(symbol, strategy, price, size, score, confidence):
    trades = []

    if Path(FILE).exists():
        with open(FILE, "r") as f:
            trades = json.load(f)

    trades.append({
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "strategy": strategy,
        "price": round(price, 2),
        "size": size,
        "score": score,
        "confidence": confidence,
        "status": "OPEN",
        "pnl": 0
    })

    with open(FILE, "w") as f:
        json.dump(trades, f, indent=2)
