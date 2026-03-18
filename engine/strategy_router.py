from engine.strategy_engine import (
    momentum_strategy,
    mean_reversion_strategy,
    defensive_strategy
)
from engine.strategy_state import save_strategy_state

def choose_trade_strategy(regime, volatility_state, trend, score, rsi):
    if volatility_state == "HIGH_VOLATILITY":
        strategy = defensive_strategy(volatility_state, trend)
        payload = {
            "engine_mode": "DEFENSIVE",
            "selected_strategy": strategy
        }
        save_strategy_state(payload)
        return strategy

    if regime == "BULL_TREND":
        strategy = momentum_strategy(trend, score, rsi)
        payload = {
            "engine_mode": "MOMENTUM",
            "selected_strategy": strategy
        }
        save_strategy_state(payload)
        return strategy

    if regime == "BEAR_TREND":
        strategy = momentum_strategy(trend, score, rsi)
        payload = {
            "engine_mode": "BEAR_MOMENTUM",
            "selected_strategy": strategy
        }
        save_strategy_state(payload)
        return strategy

    strategy = mean_reversion_strategy(trend, rsi)
    payload = {
        "engine_mode": "MEAN_REVERSION",
        "selected_strategy": strategy
    }
    save_strategy_state(payload)
    return strategy
