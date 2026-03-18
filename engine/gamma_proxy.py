def gamma_proxy(option, stock_price):
    if option is None:
        return 0

    strike = option.get("strike", 0)

    if stock_price == 0:
        return 0

    distance = abs(strike - stock_price) / stock_price

    if distance <= 0.01:
        return 30
    if distance <= 0.03:
        return 20
    if distance <= 0.05:
        return 10

    return 0
