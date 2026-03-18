import json
from datetime import datetime
from pathlib import Path

FILE = "data/premium_analysis.json"

def save_premium_analysis(trades, regime="UNKNOWN", volatility="UNKNOWN"):
    payload = []

    for trade in trades:
        symbol = trade.get("symbol")
        strategy = trade.get("strategy")
        score = trade.get("score")
        confidence = trade.get("confidence")
        price = trade.get("price")
        atr = trade.get("atr", 0)
        option = trade.get("option", {})

        stop = round(price - atr, 2) if atr else round(price * 0.97, 2)
        target = round(price + (atr * 2), 2) if atr else round(price * 1.08, 2)

        snippets = [
            f"{symbol} ranked as a high-priority setup based on multi-layer scoring.",
            f"Strategy bias is {strategy} with confidence at {confidence}.",
            f"Current market regime is {regime} and volatility state is {volatility}.",
            f"Trade score came in at {score}, which placed it in the premium review tier.",
        ]

        reasons = [
            "Trend and momentum aligned with the strategy direction.",
            "Market context allowed the setup to pass risk and volatility filters.",
            "Options contract selection met liquidity and ranking conditions.",
            "Capital-aware trade queue approved this candidate."
        ]

        payload.append({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "strategy": strategy,
            "score": score,
            "confidence": confidence,
            "price": round(price, 2),
            "stop": stop,
            "target": target,
            "option": option,
            "snippets": snippets,
            "reasons": reasons
        })

    with open(FILE, "w") as f:
        json.dump(payload, f, indent=2)

    return payload
