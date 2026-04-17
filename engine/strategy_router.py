from engine.strategy_engine import (
    momentum_strategy,
    mean_reversion_strategy,
    defensive_strategy,
)

KNOWN_REGIME_WORDS = {
    "UP",
    "UPTREND",
    "DOWN",
    "DOWNTREND",
    "SIDEWAYS",
    "BULL",
    "BULLISH",
    "BULL_TREND",
    "BEAR",
    "BEARISH",
    "BEAR_TREND",
    "AGGRESSIVE_BULL",
    "AGGRESSIVE_BEAR",
    "RISK_ON",
    "RISK_OFF",
    "TREND_UP",
    "TREND_DOWN",
    "NEUTRAL",
}

KNOWN_VOL_WORDS = {
    "LOW",
    "LOW_VOL",
    "LOW_VOLATILITY",
    "CALM",
    "NORMAL",
    "MEDIUM",
    "HIGH",
    "HIGH_VOL",
    "HIGH_VOLATILITY",
    "ELEVATED",
}

KNOWN_BREADTH_WORDS = {
    "BULL",
    "BULLISH",
    "POSITIVE",
    "STRONG",
    "RISK_ON",
    "BEAR",
    "BEARISH",
    "NEGATIVE",
    "WEAK",
    "RISK_OFF",
    "NEUTRAL",
    "UPTREND",
    "DOWNTREND",
    "SIDEWAYS",
}


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
    if text in {"BULL", "BULLISH", "POSITIVE", "STRONG", "RISK_ON", "UPTREND"}:
        return "BULLISH"
    if text in {"BEAR", "BEARISH", "NEGATIVE", "WEAK", "RISK_OFF", "DOWNTREND"}:
        return "BEARISH"
    return "NEUTRAL"


def _normalize_volatility(value):
    text = str(value or "").strip().upper()
    if text in {"LOW", "LOW_VOL", "LOW_VOLATILITY", "CALM"}:
        return "LOW"
    if text in {"HIGH", "HIGH_VOL", "HIGH_VOLATILITY", "ELEVATED"}:
        return "HIGH"
    return "NORMAL"


def _normalize_strategy(value):
    text = str(value or "").strip().upper()
    if text in {"CALL", "PUT", "NO_TRADE"}:
        return text
    return None


def _same_direction(a, b):
    return a in {"CALL", "PUT"} and b in {"CALL", "PUT"} and a == b


def _opposite_direction(a, b):
    return a in {"CALL", "PUT"} and b in {"CALL", "PUT"} and a != b


def _run_router(
    symbol,
    score,
    rsi,
    market_regime=None,
    market_breadth=None,
    volatility_state=None,
    mode=None,
    starting_strategy=None,
    **kwargs,
):
    raw_trend = market_regime if market_regime is not None else mode
    trend = _normalize_trend(raw_trend)
    breadth = _normalize_breadth(market_breadth)
    vol = _normalize_volatility(volatility_state)
    score = _safe_float(score)
    rsi = _safe_float(rsi, 50.0)
    symbol = str(symbol or "UNKNOWN")
    starting_strategy = _normalize_strategy(starting_strategy)

    print(
        "RUN ROUTER INPUTS:",
        {
            "symbol": symbol,
            "score": score,
            "rsi": rsi,
            "market_regime": market_regime,
            "market_breadth": market_breadth,
            "volatility_state": volatility_state,
            "mode": mode,
            "starting_strategy": starting_strategy,
            "extra_kwargs_seen": list(kwargs.keys()),
        },
    )

    momentum_pick = momentum_strategy(
        trend=trend,
        score=score,
        rsi=rsi,
        market_breadth=breadth,
        volatility_state=vol,
    )
    mean_reversion_pick = mean_reversion_strategy(
        trend=trend,
        rsi=rsi,
    )
    defensive_pick = defensive_strategy(
        volatility_state=vol,
        trend=trend,
    )

    momentum_pick = _normalize_strategy(momentum_pick) or "NO_TRADE"
    mean_reversion_pick = _normalize_strategy(mean_reversion_pick) or "NO_TRADE"
    defensive_pick = _normalize_strategy(defensive_pick) or "NO_TRADE"

    if breadth == "BULLISH":
        bullish_bias = True
        bearish_bias = False
    elif breadth == "BEARISH":
        bullish_bias = False
        bearish_bias = True
    else:
        bullish_bias = trend == "UPTREND"
        bearish_bias = trend == "DOWNTREND"

    chosen = "NO_TRADE"
    decision_reason = "no_valid_signal"

    if starting_strategy in {"CALL", "PUT"}:
        if _same_direction(momentum_pick, starting_strategy):
            chosen = momentum_pick
            decision_reason = "momentum_confirms_starting_strategy"
        elif _same_direction(mean_reversion_pick, starting_strategy):
            chosen = mean_reversion_pick
            decision_reason = "mean_reversion_confirms_starting_strategy"
        elif _same_direction(defensive_pick, starting_strategy):
            if starting_strategy == "CALL" and bullish_bias:
                chosen = defensive_pick
                decision_reason = "defensive_confirms_bullish_starting_strategy"
            elif starting_strategy == "PUT" and bearish_bias:
                chosen = defensive_pick
                decision_reason = "defensive_confirms_bearish_starting_strategy"
            else:
                chosen = "NO_TRADE"
                decision_reason = "defensive_signal_not_aligned_with_bias"
        elif _opposite_direction(momentum_pick, starting_strategy):
            chosen = momentum_pick
            decision_reason = "strong_momentum_reversal"
        else:
            chosen = "NO_TRADE"
            decision_reason = "starting_strategy_not_confirmed"
    else:
        if momentum_pick in {"CALL", "PUT"}:
            chosen = momentum_pick
            decision_reason = "momentum_primary"
        elif mean_reversion_pick in {"CALL", "PUT"}:
            chosen = mean_reversion_pick
            decision_reason = "mean_reversion_fallback"
        elif defensive_pick in {"CALL", "PUT"}:
            if defensive_pick == "CALL" and bullish_bias:
                chosen = defensive_pick
                decision_reason = "defensive_bullish_fallback"
            elif defensive_pick == "PUT" and bearish_bias:
                chosen = defensive_pick
                decision_reason = "defensive_bearish_fallback"
            else:
                chosen = "NO_TRADE"
                decision_reason = "defensive_not_aligned"
        else:
            chosen = "NO_TRADE"
            decision_reason = "no_signal"

    print(
        "ROUTER TRACE",
        {
            "symbol": symbol,
            "raw_trend": raw_trend,
            "normalized_trend": trend,
            "breadth": breadth,
            "volatility": vol,
            "score": score,
            "rsi": rsi,
            "starting_strategy": starting_strategy,
            "momentum_pick": momentum_pick,
            "mean_reversion_pick": mean_reversion_pick,
            "defensive_pick": defensive_pick,
            "final_choice": chosen,
            "decision_reason": decision_reason,
            "extra_kwargs_seen": list(kwargs.keys()),
        },
    )
    return chosen


def choose_strategy(
    symbol,
    score,
    rsi,
    market_regime=None,
    market_breadth=None,
    volatility_state=None,
    mode=None,
    starting_strategy=None,
    **kwargs,
):
    return _run_router(
        symbol=symbol,
        score=score,
        rsi=rsi,
        market_regime=market_regime,
        market_breadth=market_breadth,
        volatility_state=volatility_state,
        mode=mode,
        starting_strategy=starting_strategy,
        **kwargs,
    )


def choose_trade_strategy(*args, **kwargs):
    print("WRAPPER RAW ARGS:", args)
    print("WRAPPER RAW KWARGS:", kwargs)

    if kwargs:
        return _run_router(
            symbol=kwargs.pop("symbol", "UNKNOWN"),
            score=kwargs.pop("score", 0.0),
            rsi=kwargs.pop("rsi", 50.0),
            market_regime=kwargs.pop("market_regime", None),
            market_breadth=kwargs.pop("market_breadth", None),
            volatility_state=kwargs.pop("volatility_state", None),
            mode=kwargs.pop("mode", None),
            starting_strategy=kwargs.pop("starting_strategy", None),
            **kwargs,
        )

    args = list(args)

    if not args:
        return _run_router(
            symbol="UNKNOWN",
            score=0.0,
            rsi=50.0,
            market_regime=None,
            market_breadth=None,
            volatility_state=None,
            mode=None,
            starting_strategy=None,
        )

    first_upper = str(args[0]).strip().upper()

    if first_upper not in KNOWN_REGIME_WORDS:
        symbol = args[0] if len(args) > 0 else "UNKNOWN"
        score = args[1] if len(args) > 1 else 0.0
        rsi = args[2] if len(args) > 2 else 50.0
        market_regime = args[3] if len(args) > 3 else None
        market_breadth = args[4] if len(args) > 4 else None
        volatility_state = args[5] if len(args) > 5 else None
        mode = args[6] if len(args) > 6 else None
        starting_strategy = args[7] if len(args) > 7 else None

        return _run_router(
            symbol=symbol,
            score=score,
            rsi=rsi,
            market_regime=market_regime,
            market_breadth=market_breadth,
            volatility_state=volatility_state,
            mode=mode,
            starting_strategy=starting_strategy,
        )

    if len(args) >= 5:
        second_upper = str(args[1]).strip().upper()
        third_upper = str(args[2]).strip().upper()

        if second_upper in KNOWN_VOL_WORDS and third_upper in KNOWN_BREADTH_WORDS:
            market_regime = args[0]
            volatility_state = args[1]
            market_breadth = args[2]
            score = args[3]
            rsi = args[4]
            symbol = args[5] if len(args) > 5 else "UNKNOWN"
            mode = args[6] if len(args) > 6 else None
            starting_strategy = args[7] if len(args) > 7 else None

            return _run_router(
                symbol=symbol,
                score=score,
                rsi=rsi,
                market_regime=market_regime,
                market_breadth=market_breadth,
                volatility_state=volatility_state,
                mode=mode,
                starting_strategy=starting_strategy,
            )

    market_regime = args[0] if len(args) > 0 else None
    score = args[1] if len(args) > 1 else 0.0
    market_breadth = args[2] if len(args) > 2 else None
    volatility_state = args[3] if len(args) > 3 else None
    symbol = args[4] if len(args) > 4 else "UNKNOWN"
    rsi = args[5] if len(args) > 5 else 50.0
    mode = args[6] if len(args) > 6 else None
    starting_strategy = args[7] if len(args) > 7 else None

    return _run_router(
        symbol=symbol,
        score=score,
        rsi=rsi,
        market_regime=market_regime,
        market_breadth=market_breadth,
        volatility_state=volatility_state,
        mode=mode,
        starting_strategy=starting_strategy,
    )


print("STRATEGY ROUTER LOADED FROM:", __file__)
print("CHOOSE_STRATEGY FUNC:", choose_strategy)
print("CHOOSE_TRADE_STRATEGY FUNC:", choose_trade_strategy)
