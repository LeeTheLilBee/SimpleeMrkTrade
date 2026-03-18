from engine.institutional_ranker import institutional_score

def final_trade_score(stock_score, option, stock_price):
    return institutional_score(stock_score, option, stock_price)
