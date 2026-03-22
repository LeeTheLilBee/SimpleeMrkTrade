from datetime import datetime

def log_trade_state(positions):
    journal = []

    for p in positions:
        journal.append({
            "symbol": p["symbol"],
            "health": p["health"]["score"],
            "action": p["health"]["action"],
            "timestamp": datetime.now().isoformat()
        })

    return journal
