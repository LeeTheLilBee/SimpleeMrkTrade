import json
from datetime import datetime

FILE = "data/why_this_trade.json"

def save_why_this_trade(trades, regime="UNKNOWN", volatility="UNKNOWN", mode="UNKNOWN"):
    payload = []

    for trade in trades:
        symbol = trade.get("symbol")
        strategy = trade.get("strategy")
        score = trade.get("score")
        confidence = trade.get("confidence")
        price = trade.get("price")
        atr = float(trade.get("atr", 0) or 0)

        stop = round(price - atr, 2) if atr else round(price * 0.97, 2)
        target = round(price + (atr * 2), 2) if
