from datetime import datetime


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
