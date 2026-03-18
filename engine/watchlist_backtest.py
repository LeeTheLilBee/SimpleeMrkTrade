from engine.backtest_engine import simple_backtest
from engine.watchlist import get_watchlist

def backtest_watchlist():
    results = []

    for symbol in get_watchlist():
        results.append(simple_backtest(symbol))

    return results
