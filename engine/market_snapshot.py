import json

FILE = "data/market_snapshot.json"

def save_market_snapshot(regime, breadth, mode, watchlist_count, approved_count):
    payload = {
        "regime": regime,
        "breadth": breadth,
        "mode": mode,
        "watchlist_count": watchlist_count,
        "approved_count": approved_count
    }

    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)
