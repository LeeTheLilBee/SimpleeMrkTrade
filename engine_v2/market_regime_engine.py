from typing import Dict


def detect_market_regime(market_data: Dict) -> Dict:
    trend = float(market_data.get("trend_strength", 0))
    volatility = float(market_data.get("volatility_level", 0))
    breadth = float(market_data.get("breadth_score", 0))

    if trend > 70 and volatility < 60:
        regime = "trending"
    elif volatility > 75:
        regime = "volatile"
    elif trend < 40 and volatility < 60:
        regime = "choppy"
    else:
        regime = "neutral"

    return {
        "market_regime": regime,
        "trend_strength": trend,
        "volatility_level": volatility,
        "breadth_score": breadth,
    }
