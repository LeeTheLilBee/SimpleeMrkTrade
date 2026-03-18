from engine.trade_queue import add_trade
from engine.sector_cap import sector_allowed
from engine.correlation_filter import correlation_allowed

def queue_top_trades_plus(trades, limit=3):
    ranked = sorted(trades, key=lambda x: x["score"], reverse=True)
    selected = []

    for trade in ranked:
        if len(selected) >= limit:
            break

        if not sector_allowed(selected, trade["symbol"]):
            continue

        if not correlation_allowed(selected, trade["symbol"]):
            continue

        selected.append(trade)
        add_trade(trade)

    return selected
