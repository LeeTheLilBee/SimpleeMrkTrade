from engine.watchlist_backtest import backtest_watchlist

def print_backtest_summary():
    results = backtest_watchlist()

    total_trades = sum(r["trades"] for r in results)
    total_wins = sum(r["wins"] for r in results)

    rate = 0
    if total_trades > 0:
        rate = total_wins / total_trades

    print("BACKTEST SUMMARY")
    print("Trades:", total_trades)
    print("Wins:", total_wins)
    print("Win Rate:", round(rate, 2))
