import json
from pathlib import Path

FILE = "data/open_positions.json"


def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_position(trade):
    data = _load()
    data.append(dict(trade))
    _save(data)
    return trade


def open_count():
    return len(_load())


def show_positions():
    return _load()


def get_position(symbol):
    symbol = (symbol or "").upper()
    for pos in _load():
        if str(pos.get("symbol", "")).upper() == symbol:
            return pos
    return None


def replace_position(symbol, updated_position):
    symbol = (symbol or "").upper()
    data = _load()

    for i, pos in enumerate(data):
        if str(pos.get("symbol", "")).upper() == symbol:
            data[i] = dict(updated_position)
            _save(data)
            return updated_position

    return None


def remove_position(symbol):
    symbol = (symbol or "").upper()
    data = _load()

    remaining = []
    removed = None

    for pos in data:
        if removed is None and str(pos.get("symbol", "")).upper() == symbol:
            removed = pos
            continue
        remaining.append(pos)

    _save(remaining)
    return removed


def print_positions():
    positions = _load()
    print("OPEN POSITIONS:")

    if not positions:
        print("No open positions.")
        return

    for pos in positions:
        print(
            pos.get("symbol"),
            pos.get("strategy"),
            pos.get("score"),
            "| entry:",
            pos.get("entry", pos.get("price")),
            "| stop:",
            pos.get("stop"),
            "| target:",
            pos.get("target"),
            "| opened_at:",
            pos.get("opened_at"),
        )
