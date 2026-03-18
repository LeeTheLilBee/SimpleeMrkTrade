import json
from pathlib import Path

FILE = "data/open_positions.json"

def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_position(trade):
    data = _load()
    data.append(trade)
    _save(data)

def open_count():
    return len(_load())

def show_positions():
    return _load()

def print_positions():
    positions = _load()
    print("OPEN POSITIONS:")
    if not positions:
        print("No open positions.")
        return
    for pos in positions:
        print(pos["symbol"], pos["strategy"], pos["score"])
