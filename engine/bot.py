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
from engine.bot_status import write_bot_status
from engine.bot_logger import log_bot
from engine.premium_analysis_builder import save_premium_analysis
from engine.why_this_trade_builder import save_why_this_trade
from engine.live_activity import push_activity
from engine.auto_close_positions import auto_close_positions
from engine.notifications import push_notification

try:
    from engine.drawdown_brake import drawdown_brake
except Exception:
    def drawdown_brake():
        return {"blocked": False, "mode": "NORMAL", "reason": "drawdown brake unavailable"}

try:
    from engine.correlation_risk import correlation_risk_status
except Exception:
    def correlation_risk_status():
        return {"blocked": False, "crowded_sectors": {}, "reason": "correlation risk unavailable"}

try:
    from engine.sector_concentration_cap import sector_concentration_status
except Exception:
    def sector_concentration_status():
        return {"blocked": False, "sector_counts": {}, "reason": "sector cap unavailable"}

try:
    from engine.exposure_buckets import exposure_bucket_status
except Exception:
    def exposure_bucket_status():
        return {"blocked": False, "bucket": "NORMAL", "reason": "exposure buckets unavailable"}

def _reduced_risk_mode(brake_payload, exposure_payload):
    return brake_payload.get("mode") == "REDUCED_RISK" or exposure_payload.get("bucket") in ["ELEVATED", "HIGH"]

def _trim_for_reduced_risk(selected_trades):
    return selected_trades[:1] if selected_trades else selected_trades

def scan_stock(symbol, regime):
    df = safe_download(symbol, period="3mo", auto_adjust=True, progress=False)

    if df is None or df.empty or len(df) < 50:
        print(symbol, "| Not enough data")
        log_bot(f"{symbol} skipped: not enough data", "WARN")
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
        print("APPROVED:", trade["symbol"], "| Strategy:", trade["strategy"], "| Confidence:", trade["confidence"])
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
    log_bot("Bot run started", "INFO")
    push_activity("SYSTEM", "Bot run started")
    push_notification("Bot Started", "A new bot cycle has started.", "info", "/live-activity", True, "Starter", "system")

    try:
        settle_cash()
        clear_candidates()

        snapshot = account_snapshot()
        print_account_snapshot(snapshot)
        write_system_status(regime="STARTING", volatility="UNKNOWN", mode="BOOT")

        governor = governor_status(
            current_open_positions=open_count(),
            executed_trades_today=executed_trade_count(),
        )

        brake = drawdown_brake()
        corr = correlation_risk_status()
        sector_cap = sector_concentration_status()
        exposure = exposure_bucket_status()

        print("Governor:", governor)
        print("Drawdown Brake:", brake)
        print("Correlation Risk:", corr)
        print("Sector Cap:", sector_cap)
        print("Exposure Bucket:", exposure)

        if brake.get("blocked"):
            write_bot_status(False, "blocked by drawdown brake")
            push_activity("RISK", "Blocked by drawdown brake")
            push_notification("Risk Block", "Drawdown brake blocked new trades.", "warning", "/live-activity", True, "Pro", "risk")
            return

        if corr.get("blocked"):
            write_bot_status(False, "blocked by correlation risk")
            push_activity("RISK", "Blocked by correlation risk")
            push_notification("Risk Block", "Correlation risk blocked new trades.", "warning", "/live-activity", True, "Pro", "risk")
            return

        if sector_cap.get("blocked"):
            write_bot_status(False, "blocked by sector cap")
            push_activity("RISK", "Blocked by sector concentration cap")
            push_notification("Sector Cap Triggered", "Sector concentration blocked new trades.", "warning", "/live-activity", True, "Pro", "risk")
            return

        regime = get_market_regime()
        volatility_payload = get_volatility_environment()

        print("Market Regime:", regime)
        push_activity("MARKET", f"Market regime identified as {regime}")

        print("Building rotating watchlist...")
        watchlist = get_watchlist()
        print("Watchlist:", watchlist)
        push_activity("WATCHLIST", f"Watchlist built with {len(watchlist)} symbols")

        print("Scanning watchlist...")
        results = []

        for symbol in watchlist:
            result = scan_stock(symbol, regime)
            if result is not None:
                results.append(result)

        selected_trades, mode = process_signals(results, regime, volatility_payload)
        push_activity("QUEUE", f"Selected {len(selected_trades)} trades in mode {mode}")

        if _reduced_risk_mode(brake, exposure):
            selected_trades = _trim_for_reduced_risk(selected_trades)
            push_activity("RISK", "Reduced-risk mode active: trimmed trade queue")
            push_notification("Reduced Risk Mode", "Trade queue was trimmed due to elevated portfolio stress.", "warning", "/positions", True, "Pro", "risk")

        save_premium_analysis(
            selected_trades,
            regime=regime,
            volatility=volatility_payload.get("volatility", "UNKNOWN")
        )

        save_why_this_trade(
            selected_trades,
            regime=regime,
            volatility=volatility_payload.get("volatility", "UNKNOWN"),
            mode=mode
        )

        for trade in selected_trades:
            push_activity(
                "SIGNAL",
                f"{trade['symbol']} approved as {trade['strategy']} with score {trade['score']}",
                symbol=trade["symbol"],
                meta={
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"]
                }
            )
            push_notification(
                "New Approved Trade",
                f"{trade['symbol']} approved as {trade['strategy']} with score {trade['score']}.",
                "success",
                "/signals",
                True,
                "Starter",
                "signal"
            )
            push_notification(
                "Premium Setup Context",
                f"{trade['symbol']} has premium reasoning available.",
                "info",
                "/why-this-trade",
                True,
                "Pro",
                "premium"
            )

        print("Processing trade queue...")
        execute_trades(selected_trades, limit=trades_left_today(executed_trade_count()))

        print_positions()
        review_positions()

        closed_now = auto_close_positions()
        if closed_now:
            push_activity("AUTO_CLOSE", f"Auto-closed {len(closed_now)} position(s)")
            push_notification("Positions Closed", f"{len(closed_now)} position(s) were auto-closed.", "warning", "/closed-trades", True, "Pro", "risk")

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
        push_activity("SYSTEM", "Bot run completed")
        push_notification("Bot Completed", "The latest bot cycle finished successfully.", "success", "/reports", True, "Starter", "system")

    except Exception as e:
        write_bot_status(False, f"error: {e}")
        push_activity("ERROR", f"Bot error: {e}")
        push_notification("Bot Error", f"{e}", "error", "/live-activity", True, "Pro", "system")
        raise

if __name__ == "__main__":
    run()
