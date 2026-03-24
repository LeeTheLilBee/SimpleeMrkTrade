trade_queue = []


def add_trade(trade):
    trade_queue.append(dict(trade))
    return trade


def next_trade():
    if not trade_queue:
        return None
    return trade_queue.pop(0)


def clear_trade_queue():
    trade_queue.clear()


def queue_size():
    return len(trade_queue)


def show_trade_queue():
    return list(trade_queue)
