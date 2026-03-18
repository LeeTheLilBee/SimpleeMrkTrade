MAX_OPEN_TRADES = 3

def trade_slots_left(current_open):
    return max(0, MAX_OPEN_TRADES - current_open)
