from engine.regime import get_market_regime
from engine.market_volatility import get_volatility_environment
from engine.signal_feed import push_signal
from engine.rsi_engine import calculate_rsi
from engine.volume_engine import volume_surge
from engine.breakout_engine import breakout
from engine.signal_engine import build_signal
from engine.confidence_engine import confidence
from engine.dashboard import dashboard
from engine.watchlist import get_watchlist
from engine.trend_strength import trend_strength
from engine.options_scanner import get_best_call
from engine.options_put_scanner import get_best_put
from engine.market_breadth import market_breadth
from engine.market_mode import market_mode
from engine.queue_manager_plus import queue_top_trades_plus
from engine.trade_ranker import final_trade_score
from engine.paper_portfolio import open_count, print_positions
from engine.position_cap import trade_slots_left
from engine.trade_history import executed_trade_count
from engine.daily_risk import trades_left_today
from engine.signal_history import remember_signal
from engine.atr_engine import calculate_atr
from engine.leaderboard import print_leaderboard
from engine.stock_fallback import stock_only_candidate
from engine.candidate_log import remember_candidate, show_candidates, clear_candidates
from engine.position_review import review_positions
from engine.data_utils import safe_download
from engine.execution_loop import execute_trades
from engine.capital_guard import affordable_trade_count
from engine.backtest_summary import print_backtest_summary
from engine.portfolio_summary import portfolio_summary
from engine.account_state import settle_cash
from engine.alerts import alert_trade
from engine.equity_curve import build_equity_curve
from engine.journal_export import export_journal
from engine.trade_analytics import analytics
from engine.performance_tracker import performance_summary
from engine.market_snapshot import save_market_snapshot
from engine.top_candidates_store import save_top_candidates
from engine.top_candidates_view import print_top_candidates
from engine.daily_report import write_daily_report
from engine.risk_governor import governor_status
from engine.unrealized_pnl import unrealized_pnl
from engine.strategy_performance import strategy_breakdown
from engine.drawdown_tracker import build_drawdown_history
from engine.strategy_router import choose_trade_strategy
from engine.trade_filter_plus import advanced_trade_filter
from engine.account_snapshot import account_snapshot
from engine.account_snapshot_view import print_account_snapshot
from engine.system_status import write_system_status
from engine.report_archive import archive_report
from engine.drawdown_brake import drawdown_brake
from engine.correlation_risk import correlation_risk_status
from engine.bot_status import write_bot_status

def scan_stock(symbol, regime):
    df = safe_download(symbol, period="3mo", auto_adjust=True, progress=False)

    if df is None or df.empty or len(df) < 50:
        print(symbol, "| Not enough data")
        return None

    price = float(df["Close"].iloc[-1].item())
    sma20 = float(df["Close"].rolling(20).mean().iloc[-1].item())

    rsi_series = calculate_rsi(df)
    rsi = float(rsi_series.iloc[-1].item())

    volume = volume_surge(df)
    breakout_signal = breakout(df)
    atr = calculate_atr(df)

    trend = "UPTREND" if price > sma20 else "DOWNTREND"
    trend_score = trend_strength(df)

    score = build_signal(price, sma20, rsi, volume, breakout_signal)
    score += trend_score * 10

    conf = confidence(score)
    dashboard(symbol, trend, rsi, score, conf)

    return {
        "symbol": symbol,
        "price": price,
        "trend": trend,
        "score": score,
        "confidence": conf,
        "rsi": rsi,
        "volume": volume,
        "breakout": breakout_signal,
        "atr": atr,
    }

def process_signals(results, regime, volatility_payload):
    breadth = market_breadth(results)
    mode = market_mode(regime, breadth)
    volatility_state = volatility_payload.get("volatility", "UNKNOWN")

    print("Market Breadth:", breadth)
    print("Market Mode:", mode)
    print("Volatility State:", volatility_state, "| VIX:", volatility_payload.get("vix"))

    approved_trades = []

    for item in results:
        symbol = item["symbol"]
        trend = item["trend"]
        score = item["score"]
        conf = item["confidence"]
        price = item["price"]
        atr = item["atr"]
        rsi = item["rsi"]

        strategy = choose_trade_strategy(regime, volatility_state, trend, score, rsi)
        approved = advanced_trade_filter(score, conf, volatility_state, strategy)

        if not approved:
            continue

        option = None

        if strategy == "CALL":
            option = get_best_call(symbol)
        elif strategy == "PUT":
            option = get_best_put(symbol)

        if option is None:
            candidate = stock_only_candidate(symbol, strategy, score, conf)
            remember_candidate(candidate)
            continue

        total_score = final_trade_score(score, option, price)

        trade = {
            "symbol": symbol,
            "strategy": strategy,
            "price": price,
            "score": total_score,
            "confidence": conf,
            "option": option,
            "atr": atr,
        }

        approved_trades.append(trade)
        remember_signal(symbol, total_score, strategy)
        push_signal(symbol, strategy, total_score, conf)

    print_leaderboard(approved_trades)
    print_top_candidates(approved_trades, limit=5)
    save_top_candidates(approved_trades, limit=10)

    slots = trade_slots_left(open_count())
    remaining = trades_left_today(executed_trade_count())
    affordable = affordable_trade_count(approved_trades)
    limit = min(slots, remaining, affordable)

    selected_trades = queue_top_trades_plus(approved_trades, limit=limit)

    for trade in selected_trades:
        alert_trade(trade)
        print(
            "APPROVED:",
            trade["symbol"],
            "| Strategy:",
            trade["strategy"],
            "| Confidence:",
            trade["confidence"],
        )
        if trade["option"]:
            print("Best Option:", trade["option"])

    save_market_snapshot(
        regime=regime,
        breadth=breadth,
        mode=mode,
        watchlist_count=len(results),
        approved_count=len(selected_trades),
    )

    return selected_trades, mode

def run():
    write_bot_status(True, "starting")
    try:
        settle_cash()
        clear_candidates()

        snapshot = account_snapshot()
        print_account_snapshot(snapshot)

        write_system_status(regime="STARTING", volatility="UNKNOWN", mode="BOOT")

        current_open = open_count()
        executed_today = executed_trade_count()

        governor = governor_status(
            current_open_positions=current_open,
            executed_trades_today=executed_today,
        )

        brake = drawdown_brake()
        corr = correlation_risk_status()

        print("Governor:", governor)
        print("Drawdown Brake:", brake)
        print("Correlation Risk:", corr)

        if brake["blocked"]:
            print("DRAWDOWN BRAKE BLOCKED NEW TRADES")
            write_bot_status(False, "blocked by drawdown brake")
            return

        if governor["blocked"]:
            print("RISK GOVERNOR BLOCKED NEW TRADES")
            print("Reasons:", governor["reasons"])

            print_positions()
            review_positions()

            build_equity_curve()
            report = write_daily_report()
            archive_report()
            write_system_status(
                regime="BLOCKED",
                volatility="UNKNOWN",
                mode="RISK_GOVERNOR_BLOCKED",
            )

            print("Performance:", performance_summary())
            print("Analytics:", analytics())
            print("Portfolio Summary:", portfolio_summary())
            print("Unrealized PnL:", unrealized_pnl())
            print("Strategy Performance:", strategy_breakdown())
            dd = build_drawdown_history()
            print("Drawdown History Built:", dd[-5:] if dd else [])
            print("Daily Report Written:", report["timestamp"])
            print("Final Account Snapshot:", account_snapshot())
            print_backtest_summary()
            write_bot_status(False, "blocked by governor")
            return

        regime = get_market_regime()
        volatility_payload = get_volatility_environment()

        print("Market Regime:", regime)
        print("Building rotating watchlist...")

        watchlist = get_watchlist()
        print("Watchlist:", watchlist)

        print("Scanning watchlist...")
        results = []

        for symbol in watchlist:
            result = scan_stock(symbol, regime)
            if result is not None:
                results.append(result)

        selected_trades, mode = process_signals(results, regime, volatility_payload)

        print("Processing trade queue...")
        execute_trades(selected_trades, limit=trades_left_today(executed_trade_count()))

        print_positions()
        review_positions()
        show_candidates()

        build_equity_curve()
        export_journal()
        report = write_daily_report()
        archive_report()
        write_system_status(
            regime=regime,
            volatility=volatility_payload.get("volatility", "UNKNOWN"),
            mode=mode,
        )

        print("Performance:", performance_summary())
        print("Analytics:", analytics())
        print("Portfolio Summary:", portfolio_summary())
        print("Unrealized PnL:", unrealized_pnl())
        print("Strategy Performance:", strategy_breakdown())
        dd = build_drawdown_history()
        print("Drawdown History Built:", dd[-5:] if dd else [])
        print("Daily Report Written:", report["timestamp"])
        print("Final Account Snapshot:", account_snapshot())
        print_backtest_summary()
        write_bot_status(False, "completed")
    except Exception as e:
        write_bot_status(False, f"error: {e}")
        raise

if __name__ == "__main__":
    run()
