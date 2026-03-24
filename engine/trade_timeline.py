import json
from pathlib import Path
from datetime import datetime

FILE = "data/trade_timeline.json"


def _load():
    if not Path(FILE).exists():
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data[-500:], f, indent=2)


def add_timeline_event(symbol, event, details=None):
    data = _load()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "event": event,
        "details": details or {}
    }
    data.append(entry)
    _save(data)
    return entry


def add_trade_timeline_event(symbol, stage, details=None):
    return add_timeline_event(symbol, stage, details)


def build_trade_timeline(trade):
    timeline = []

    score = trade.get("score", 0)
    prev_score = trade.get("previous_score", score)

    if score > prev_score:
        timeline.append("Structure improved")
    elif score < prev_score:
        timeline.append("Structure weakened")

    if trade.get("current_price", 0) > trade.get("entry", 0):
        timeline.append("Trade moved into profit zone")

    if trade.get("current_price", 0) < trade.get("stop", 0):
        timeline.append("Stop violation risk")

    timeline.append(f"Last evaluated at {datetime.now().strftime('%H:%M:%S')}")
    return timeline


def attach_timeline(positions):
    for p in positions:
        p["timeline"] = build_trade_timeline(p)
    return positions
