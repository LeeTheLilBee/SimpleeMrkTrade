trade_queue = []

def add_trade(trade):
    trade_queue.append(trade)

def next_trade():
    if not trade_queue:
        return None
    return trade_queue.pop(0)
