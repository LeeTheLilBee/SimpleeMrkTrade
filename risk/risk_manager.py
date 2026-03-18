def stop_loss_price(entry_price, atr=None, percent=0.03):
    if atr is not None:
        return entry_price - atr
    return entry_price * (1 - percent)

def take_profit_price(entry_price, atr=None, percent=0.08):
    if atr is not None:
        return entry_price + (atr * 2)
    return entry_price * (1 + percent)
