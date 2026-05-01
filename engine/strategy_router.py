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


def _safe_str(value, default=""):
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _normalize_mode(value):
    text = _safe_str(value, "").upper()
    if text in {"SURVEY", "PAPER", "LIVE"}:
        return text
    return "PAPER"


def _normalize_regime(value):
    text = _safe_str(value, "").upper()
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
    if text == "NEUTRAL":
        return "NEUTRAL"
    return "SIDEWAYS"


def _normalize_breadth(value):
    text = _safe_str(value, "").upper()
    if text in {"BULL", "BULLISH", "POSITIVE", "STRONG", "RISK_ON", "UPTREND"}:
        return "BULLISH"
    if text in {"BEAR", "BEARISH", "NEGATIVE", "WEAK", "RISK_OFF", "DOWNTREND"}:
        return "BEARISH"
    return "NEUTRAL"


def _normalize_volatility(value):
    text = _safe_str(value, "").upper()
    if text in {"LOW", "LOW_VOL", "LOW_VOLATILITY", "CALM"}:
        return "LOW"
    if text in {"HIGH", "HIGH_VOL", "HIGH_VOLATILITY", "ELEVATED"}:
        return "HIGH"
    return "NORMAL"


def _normalize_strategy(value):
    text = _safe_str(value, "").upper()
    if text in {"CALL", "PUT", "NO_TRADE"}:
        return text
    return None


def _same_direction(a, b):
    return a in {"CALL", "PUT"} and b in {"CALL", "PUT"} and a == b


def _opposite_direction(a, b):
    return a in {"CALL", "PUT"} and b in {"CALL", "PUT"} and a != b


def _derive_trade_trend(regime, breadth):
    regime = _normalize_regime(regime)
    breadth = _normalize_breadth(breadth)

    if regime == "UPTREND":
        return "UPTREND"
    if regime == "DOWNTREND":
        return "DOWNTREND"

    if regime == "NEUTRAL":
        if breadth == "BULLISH":
            return "UPTREND"
        if breadth == "BEARISH":
            return "DOWNTREND"
        return "SIDEWAYS"

    if breadth == "BULLISH":
        return "UPTREND"
    if breadth == "BEARISH":
        return "DOWNTREND"

    return "SIDEWAYS"


def _build_bias(trend, breadth):
    if breadth == "BULLISH":
        return {
            "bullish_bias": True,
            "bearish_bias": False,
        }
    if breadth == "BEARISH":
        return {
            "bullish_bias": False,
            "bearish_bias": True,
        }
    return {
        "bullish_bias": trend == "UPTREND",
        "bearish_bias": trend == "DOWNTREND",
    }


def _score_tier(score):
    score = _safe_float(score, 0.0)
    if score >= 400:
        return "EXTREME"
    if score >= 220:
        return "VERY_HIGH"
    if score >= 120:
        return "HIGH"
    if score >= 90:
        return "VALID"
    return "WEAK"


def _can_soft_preserve_starting_strategy(
    *,
    starting_strategy,
    score,
    rsi,
    trend,
    breadth,
    vol,
    mode,
):
    if starting_strategy not in {"CALL", "PUT"}:
        return False

    if mode == "LIVE":
        return False

    score = _safe_float(score, 0.0)
    rsi = _safe_float(rsi, 50.0)
    tier = _score_tier(score)

    if starting_strategy == "CALL":
        directional_ok = breadth == "BULLISH" or trend == "UPTREND"
        if not directional_ok and tier not in {"VERY_HIGH", "EXTREME"}:
            return False
        if vol == "HIGH" and score < 140:
            return False
        if rsi >= 92 and score < 260:
            return False
        return score >= 120

    if starting_strategy == "PUT":
        directional_ok = breadth == "BEARISH" or trend == "DOWNTREND"
        if not directional_ok and tier not in {"VERY_HIGH", "EXTREME"}:
            return False
        if vol == "HIGH" and score < 140:
            return False
        if rsi <= 8 and score < 260:
            return False
        return score >= 120

    return False


def _can_hard_preserve_starting_strategy(
    *,
    starting_strategy,
    score,
    trend,
    breadth,
    mode,
):
    if starting_strategy not in {"CALL", "PUT"}:
        return False

    if mode == "LIVE":
        return False

    score = _safe_float(score, 0.0)
    tier = _score_tier(score)

    if tier not in {"VERY_HIGH", "EXTREME"}:
        return False

    if starting_strategy == "CALL":
        return breadth == "BULLISH" or trend == "UPTREND"

    if starting_strategy == "PUT":
        return breadth == "BEARISH" or trend == "DOWNTREND"

    return False


def _allow_reversal(
    *,
    starting_strategy,
    reversal_pick,
    score,
    rsi,
    trend,
    breadth,
):
    if starting_strategy not in {"CALL", "PUT"}:
        return False
    if reversal_pick not in {"CALL", "PUT"}:
        return False
    if reversal_pick == starting_strategy:
        return False

    score = _safe_float(score, 0.0)
    rsi = _safe_float(rsi, 50.0)

    if starting_strategy == "CALL" and reversal_pick == "PUT":
        if breadth == "BEARISH" and trend == "DOWNTREND" and score >= 120:
            return True
        if rsi >= 92 and score >= 320:
            return True
        return False

    if starting_strategy == "PUT" and reversal_pick == "CALL":
        if breadth == "BULLISH" and trend == "UPTREND" and score >= 120:
            return True
        if rsi <= 8 and score >= 320:
            return True
        return False

    return False


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
    raw_regime = market_regime
    breadth = _normalize_breadth(market_breadth)
    vol = _normalize_volatility(volatility_state)
    mode_name = _normalize_mode(mode)
    score = _safe_float(score)
    rsi = _safe_float(rsi, 50.0)
    symbol = _safe_str(symbol, "UNKNOWN")
    starting_strategy = _normalize_strategy(starting_strategy)

    normalized_regime = _normalize_regime(raw_regime)
    trend = _derive_trade_trend(normalized_regime, breadth)

    print(
        "RUN ROUTER INPUTS:",
        {
            "symbol": symbol,
            "score": score,
            "rsi": rsi,
            "market_regime": market_regime,
            "market_breadth": market_breadth,
            "volatility_state": volatility_state,
            "mode": mode_name,
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

    bias = _build_bias(trend, breadth)
    bullish_bias = bias["bullish_bias"]
    bearish_bias = bias["bearish_bias"]
    tier = _score_tier(score)

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
            elif _can_soft_preserve_starting_strategy(
                starting_strategy=starting_strategy,
                score=score,
                rsi=rsi,
                trend=trend,
                breadth=breadth,
                vol=vol,
                mode=mode_name,
            ):
                chosen = starting_strategy
                decision_reason = "soft_preserve_starting_strategy_after_defensive_mismatch"
            else:
                chosen = "NO_TRADE"
                decision_reason = "defensive_signal_not_aligned_with_bias"

        elif _opposite_direction(momentum_pick, starting_strategy):
            if _allow_reversal(
                starting_strategy=starting_strategy,
                reversal_pick=momentum_pick,
                score=score,
                rsi=rsi,
                trend=trend,
                breadth=breadth,
            ):
                chosen = momentum_pick
                decision_reason = "strong_momentum_reversal"
            elif _can_hard_preserve_starting_strategy(
                starting_strategy=starting_strategy,
                score=score,
                trend=trend,
                breadth=breadth,
                mode=mode_name,
            ):
                chosen = starting_strategy
                decision_reason = "hard_preserve_starting_strategy_over_momentum_reversal"
            else:
                chosen = "NO_TRADE"
                decision_reason = "momentum_reversal_not_allowed"

        elif _opposite_direction(mean_reversion_pick, starting_strategy):
            if _allow_reversal(
                starting_strategy=starting_strategy,
                reversal_pick=mean_reversion_pick,
                score=score,
                rsi=rsi,
                trend=trend,
                breadth=breadth,
            ):
                chosen = mean_reversion_pick
                decision_reason = "mean_reversion_reversal"
            elif _can_soft_preserve_starting_strategy(
                starting_strategy=starting_strategy,
                score=score,
                rsi=rsi,
                trend=trend,
                breadth=breadth,
                vol=vol,
                mode=mode_name,
            ):
                chosen = starting_strategy
                decision_reason = "soft_preserve_starting_strategy"
            else:
                chosen = "NO_TRADE"
                decision_reason = "starting_strategy_not_confirmed"

        elif _can_hard_preserve_starting_strategy(
            starting_strategy=starting_strategy,
            score=score,
            trend=trend,
            breadth=breadth,
            mode=mode_name,
        ):
            chosen = starting_strategy
            decision_reason = "hard_preserve_starting_strategy"

        elif _can_soft_preserve_starting_strategy(
            starting_strategy=starting_strategy,
            score=score,
            rsi=rsi,
            trend=trend,
            breadth=breadth,
            vol=vol,
            mode=mode_name,
        ):
            chosen = starting_strategy
            decision_reason = "soft_preserve_starting_strategy"

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
            if tier in {"VERY_HIGH", "EXTREME"}:
                if breadth == "BULLISH":
                    chosen = "CALL"
                    decision_reason = "high_score_bias_fallback_call"
                elif breadth == "BEARISH":
                    chosen = "PUT"
                    decision_reason = "high_score_bias_fallback_put"
                else:
                    chosen = "NO_TRADE"
                    decision_reason = "high_score_but_no_bias_alignment"
            else:
                chosen = "NO_TRADE"
                decision_reason = "no_signal"

    print(
        "ROUTER TRACE",
        {
            "symbol": symbol,
            "raw_regime": raw_regime,
            "normalized_regime": normalized_regime,
            "derived_trend": trend,
            "breadth": breadth,
            "volatility": vol,
            "mode": mode_name,
            "score": score,
            "score_tier": tier,
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

    first_upper = _safe_str(args[0], "").upper()

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
        second_upper = _safe_str(args[1], "").upper()
        third_upper = _safe_str(args[2], "").upper()

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
