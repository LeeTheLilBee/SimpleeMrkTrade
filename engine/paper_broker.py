from datetime import datetime


def apply_slippage(price, side="buy", slippage_bps=25):
    """
    slippage_bps = basis points
    25 bps = 0.25%
    """
    price = float(price or 0)
    slip = slippage_bps / 10000.0

    if side.lower() == "buy":
        return round(price * (1 + slip), 4)
    return round(price * (1 - slip), 4)


def estimate_commission(fill_price, size, per_share=0.005, min_commission=1.0):
    fill_price = float(fill_price or 0)
    size = float(size or 0)
    commission = max(min_commission, size * per_share)
    return round(commission, 2)


def place_order(symbol, strategy, requested_price, size, order_type="market"):
    requested_price = float(requested_price or 0)
    size = float(size or 0)

    buy_side = strategy.upper() in {"CALL", "BUY", "LONG", "LONG_CALL", "LONG_PUT"}
    fill_price = apply_slippage(
        requested_price,
        side="buy" if buy_side else "sell",
        slippage_bps=25,
    )

    commission = estimate_commission(fill_price, size)

    return {
        "symbol": symbol,
        "strategy": strategy,
        "order_type": order_type,
        "requested_price": round(requested_price, 4),
        "filled_price": round(fill_price, 4),
        "size": size,
        "commission": commission,
        "status": "FILLED",
        "timestamp": datetime.now().isoformat(),
    }
