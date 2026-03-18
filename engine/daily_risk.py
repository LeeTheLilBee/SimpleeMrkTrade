MAX_DAILY_TRADES = 3

def trades_left_today(executed_count):
    return max(0, MAX_DAILY_TRADES - executed_count)

def can_trade_today(executed_count):
    return executed_count < MAX_DAILY_TRADES
