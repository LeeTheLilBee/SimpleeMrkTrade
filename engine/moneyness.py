def valid_call_strike(stock_price, strike):
    return stock_price * 0.90 <= strike <= stock_price * 1.10

def valid_put_strike(stock_price, strike):
    return stock_price * 0.90 <= strike <= stock_price * 1.10
