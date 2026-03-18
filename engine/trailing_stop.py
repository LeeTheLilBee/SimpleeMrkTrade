def trailing_stop(entry_price, current_price, atr):
    if atr is None or atr <= 0:
        return entry_price * 0.97

    stop = current_price - (2 * atr)
    floor = entry_price * 0.97

    return max(stop, floor)
