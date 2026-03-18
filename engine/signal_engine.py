def build_signal(price, sma20, rsi, volume_signal, breakout_signal):
    score = 0

    if price > sma20:
        score += 20

    if 40 <= rsi <= 60:
        score += 20
    elif rsi < 35:
        score += 30

    if volume_signal:
        score += 20

    if breakout_signal:
        score += 20

    return score
