def liquidity_pressure(option):
    volume = option.get("volume", 0)
    oi = option.get("openInterest", 0)

    if oi == 0:
        return "LOW"

    ratio = volume / oi

    if ratio >= 1.0:
        return "HIGH"
    if ratio >= 0.4:
        return "MEDIUM"
    return "LOW"
