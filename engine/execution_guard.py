def can_execute_trade(trade, buying_power_value):
    price = float(trade.get("price", 0))

    if price <= 0:
        return False

    if price > buying_power_value:
        return False

    return True
