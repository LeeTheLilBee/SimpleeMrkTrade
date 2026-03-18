def check_exit(current_price, stop_price, target_price):
    if current_price <= stop_price:
        return "STOP_LOSS"
    if current_price >= target_price:
        return "TAKE_PROFIT"
    return "HOLD"
