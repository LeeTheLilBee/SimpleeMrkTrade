from engine.market_maker_signal import market_maker_signal
from engine.gamma_proxy import gamma_proxy

def institutional_score(signal_score, option, stock_price):
    score = signal_score

    if option:
        score += option.get("score", 0)
        score += market_maker_signal(option)
        score += gamma_proxy(option, stock_price)

    return score
