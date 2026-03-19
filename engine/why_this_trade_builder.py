import json
from datetime import datetime

FILE = "data/why_this_trade.json"

def save_why_this_trade(trades, regime="UNKNOWN", volatility="UNKNOWN", mode="UNKNOWN"):
    payload = []

    for trade in trades:
        symbol = trade.get("symbol")
        strategy = trade.get("strategy")
        score = trade.get("score")
        confidence = trade.get("confidence")
        price = float(trade.get("price", 0))
        atr = float(trade.get("atr", 0) or 0)

        # SAFE stop/target logic
        if atr > 0:
            stop = round(price - atr, 2)
            target = round(price + (atr * 2), 2)
        else:
            stop = round(price * 0.97, 2)
            target = round(price * 1.08, 2)

        payload.append({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "strategy": strategy,
            "score": score,
            "confidence": confidence,
            "entry": round(price, 2),
            "stop": stop,
            "target": target,

            "market_context": [
                f"The system identified the market regime as {regime}.",
                f"Volatility conditions were classified as {volatility}.",
                f"The system shifted into {mode} mode based on internal conditions."
            ],

            "why_selected": [
                "This setup ranked highly relative to other opportunities in the same scan.",
                "The signal passed multi-layer scoring, filtering, and ranking logic.",
                "The direction aligned with current market structure and momentum.",
                "Capital allocation rules allowed this trade to be considered executable."
            ],

            "how_to_think_about_it": [
                "This is a probability-based setup, not a guaranteed outcome.",
                "Respect the stop level — that defines risk.",
                "Targets represent expected range expansion, not certainty.",
                "Use this to understand structure, not blindly copy trades."
            ]
        })

    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)

    return payload
