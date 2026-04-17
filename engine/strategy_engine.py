from typing import Optional


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _normalize_trend(trend):
    text = str(trend or "").strip().upper()

    if text in {
        "UP",
        "UPTREND",
        "BULL",
        "BULLISH",
        "BULL_TREND",
        "AGGRESSIVE_BULL",
        "RISK_ON",
        "TREND_UP",
    }:
        return "UPTREND"

    if text in {
        "DOWN",
        "DOWNTREND",
        "BEAR",
        "BEARISH",
        "BEAR_TREND",
        "AGGRESSIVE_BEAR",
        "RISK_OFF",
        "TREND_DOWN",
    }:
        return "DOWNTREND"

    return "SIDEWAYS"


def _normalize_breadth(value):
    text = str(value or "").strip().upper()

    if text in {"BULL", "BULLISH", "POSITIVE", "STRONG", "RISK_ON"}:
        return "BULLISH"
    if text in {"BEAR", "BEARISH", "NEGATIVE", "WEAK", "RISK_OFF"}:
        return "BEARISH"
    return "NEUTRAL"


def _normalize_volatility(value):
    text = str(value or "").strip().upper()

    if text in {"LOW", "LOW_VOL", "LOW_VOLATILITY", "CALM"}:
        return "LOW"
    if text in {"HIGH", "HIGH_VOL", "HIGH_VOLATILITY", "ELEVATED"}:
        return "HIGH"
    return "NORMAL"


def _score_band(score):
    score = _safe_float(score)
    if score >= 300:
        return "EXTREME"
    if score >= 220:
        return "ELITE"
    if score >= 150:
        return "STRONG"
    if score >= 95:
        return "PASS"
    return "WEAK"


def momentum_strategy(trend, score, rsi, market_breadth, volatility_state):
    trend = _normalize_trend(trend)
    score = _safe_float(score)
    rsi = _safe_float(rsi, 50.0)
    market_breadth = _normalize_breadth(market_breadth)
    volatility_state = _normalize_volatility(volatility_state)

    if trend != "UPTREND":
        return "NO_TRADE"

    if score >= 260 and 48 <= rsi <= 76:
        return "CALL"

    if score >= 185 and 45 <= rsi <= 78:
        if market_breadth == "BULLISH" and volatility_state in {"NORMAL", "LOW"}:
            return "CALL"

    if score >= 140 and 50 <= rsi <= 72:
        if market_breadth == "BULLISH" and volatility_state == "LOW":
            return "CALL"

    return "NO_TRADE"


def mean_reversion_strategy(trend, rsi):
    trend = _normalize_trend(trend)
    rsi = _safe_float(rsi, 50.0)

    if trend == "SIDEWAYS":
        if rsi <= 30:
            return "CALL"
        if rsi >= 70:
            return "PUT"
        return "NO_TRADE"

    if trend == "UPTREND":
        if rsi <= 35:
            return "CALL"
        return "NO_TRADE"

    if trend == "DOWNTREND":
        if rsi >= 65:
            return "PUT"
        return "NO_TRADE"

    return "NO_TRADE"


def defensive_strategy(volatility_state, trend):
    vol = _normalize_volatility(volatility_state)
    trend = _normalize_trend(trend)

    if vol == "HIGH":
        if trend == "UPTREND":
            return "CALL"
        if trend == "DOWNTREND":
            return "PUT"
        return "NO_TRADE"

    if trend == "UPTREND":
        return "CALL"
    if trend == "DOWNTREND":
        return "PUT"

    return "NO_TRADE"
