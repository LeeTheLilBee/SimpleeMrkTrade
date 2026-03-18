from engine.account_state import buying_power

def affordable_trade_count(trades):
    bp = buying_power()
    count = 0

    ranked = sorted(trades, key=lambda x: x["price"])

    for trade in ranked:
        if trade["price"] <= bp:
            count += 1
            bp -= trade["price"]

    return count
