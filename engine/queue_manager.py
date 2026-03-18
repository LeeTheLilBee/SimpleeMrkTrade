from engine.trade_queue import add_trade
from engine.sector_cap import sector_allowed

def queue_top_trades(trades, limit=3):
    ranked = sorted(trades, key=lambda x: x["score"], reverse=True)
    selected = []

    for trade in ranked:
        if len(selected) >= limit:
            break
        if sector_allowed(selected, trade["symbol"]):
            selected.append(trade)
            add_trade(trade)

    return selected
