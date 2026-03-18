import json
from pathlib import Path

OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"

def portfolio_summary():
    open_positions = []
    closed_positions = []

    if Path(OPEN_FILE).exists():
        with open(OPEN_FILE, "r") as f:
            open_positions = json.load(f)

    if Path(CLOSED_FILE).exists():
        with open(CLOSED_FILE, "r") as f:
            closed_positions = json.load(f)

    realized = sum(pos.get("pnl", 0) for pos in closed_positions)

    return {
        "open_positions": len(open_positions),
        "closed_positions": len(closed_positions),
        "realized_pnl": round(realized, 2)
    }
