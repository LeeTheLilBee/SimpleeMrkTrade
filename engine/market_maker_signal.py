from engine.liquidity_detector import liquidity_pressure

def market_maker_signal(option):
    if option is None:
        return 0

    pressure = liquidity_pressure(option)
    score = 0

    if pressure == "HIGH":
        score += 30
    elif pressure == "MEDIUM":
        score += 15

    if option.get("openInterest", 0) > 2000:
        score += 20

    if option.get("volume", 0) > 1000:
        score += 20

    return score
