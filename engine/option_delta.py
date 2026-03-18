def delta_score(strike, price):
    distance = abs(strike - price) / price

    if distance < 0.02:
        return 30
    if distance < 0.05:
        return 20
    if distance < 0.10:
        return 10
    return 0
