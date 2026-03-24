from engine.explainability_engine import explain_trade_decision, explain_rejection
from engine.performance_tracker import entries_today
from engine.position_monitor import monitor_open_positions
from engine.execution_source import get_execution_candidates
from engine.regime import get_market_regime
from engine.explainability_engine import explain_exit
from engine.candidate_log import remember_candidate
from engine.market_volatility import get_volatility_environment
from engine.signal_feed import push_signal
from engine.rsi_engine import calculate_rsi
from engine.volume_engine import volume_surge
from engine.breakout_engine import breakout
from engine.signal_engine import build_signal
from engine.execution_guard import can_execute_trade
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
from engine.candidate_log import show_candidates, clear_candidates
from engine.position_review import review_positions
from engine.data_utils import safe_download
from engine.execution_loop import execute_trades
from engine.capital_guard import affordable_trade_count
from engine.backtest_summary import print_backtest_summary
from engine.portfolio_summary import portfolio_summary
from engine.account_state import settle_cash
from engine.account_state import buying_power
from engine.alerts import alert_trade
from engine.equity_curve import build_equity_curve
from engine.journal_export import export_journal
from engine.trade_analytics import analytics
from engine.performance_tracker import entries_today
from engine.performance_tracker import performance_summary
from engine.market_snapshot import save_market_snapshot
from engine.top_candidates_store import save_top_candidates
from engine.top_candidates_view import print_top_candidates
from engine.daily_report import write_daily_report
from engine.risk_governor import governor_status
from engine.unrealized_pnl import unrealized_pnl
from engine.strategy_performance import strategy_breakdown
from engine.breadth_filter import breadth_allows_trade
from engine.drawdown_tracker import build_drawdown_history
from engine.strategy_router import choose_trade_strategy
from engine.trade_filter_plus import advanced_trade_filter
from engine.account_snapshot import account_snapshot
from engine.account_snapshot_view import print_account_snapshot
from engine.system_status import write_system_status
from engine.report_archive import archive_report
from engine.bot_status import write_bot_status
from engine.bot_logger import log_bot
from engine.live_activity import push_activity
from engine.auto_close_positions import auto_close_positions

from engine.premium_intelligence import (
    save_premium_analysis,
    save_research_premium_analysis,
)
from engine.trade_timeline_manager import add_trade_timeline_event
from engine.smart_notification_router import (
    notify_trade_approved,
    notify_trade_risk,
    notify_trade_closed,
    notify_trade_edge,
)
from engine.research_signal_writer import save_research_signal
from engine.trade_detail_builder import (
    build_trade_detail,
    save_trade_detail,
    append_trade_detail_timeline,
)
from engine.notification_engine import push_notification

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


def log_candidate_decision(
    trade,
    status,
    reason,
    mode=None,
    breadth=None,
    volatility_state=None,
    extra=None,
):
    payload = {
        "symbol": trade.get("symbol"),
        "strategy": trade.get("strategy"),
        "score": trade.get("score"),
        "confidence": trade.get("confidence"),
        "price": trade.get("price"),
        "status": status,  # selected | approved_not_selected | rejected
        "reason": reason,
        "mode": mode,
        "breadth": breadth,
        "volatility_state": volatility_state,
        "timestamp": trade.get("timestamp"),
    }

    if extra:
        payload.update(extra)

    remember_candidate(payload)


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


def log_candidate_decision(
    trade,
    status,
    reason,
    mode=None,
    breadth=None,
    volatility_state=None,
    extra=None,
):
    payload = {
        "symbol": trade.get("symbol"),
        "strategy": trade.get("strategy"),
        "score": trade.get("score"),
        "confidence": trade.get("confidence"),
        "price": trade.get("price"),
        "status": status,  # selected | approved_not_selected | rejected
        "reason": reason,
        "mode": mode,
        "breadth": breadth,
        "volatility_state": volatility_state,
        "timestamp": trade.get("timestamp"),
        "why": trade.get("why", []),
        "rejection_reason": trade.get("rejection_reason"),
    }

    if extra:
        payload.update(extra)

    remember_candidate(payload)


def resolve_market_mode(regime, breadth, volatility_payload):
    try:
        return market_mode(regime, breadth, volatility_payload)
    except TypeError:
        try:
            vol_state = volatility_payload.get("state", "NORMAL")
            return market_mode(regime, breadth, vol_state)
        except TypeError:
            return market_mode(regime, breadth)


def process_signals(results, regime, volatility_payload):
    approved_trades = []

    breadth = market_breadth(results)
    print("Market Breadth:", breadth)

    mode = resolve_market_mode(regime, breadth, volatility_payload)
    print("Market Mode:", mode)

    volatility_state = volatility_payload.get("state", "NORMAL")
    print(
        "Volatility State:",
        volatility_state,
        "| VIX:",
        volatility_payload.get("vix", "N/A"),
    )

    for trade in results:
        symbol = trade.get("symbol", "UNKNOWN")
        strategy = trade.get("strategy", "CALL")
        score = float(trade.get("score", 0) or 0)
        confidence = trade.get("confidence", "LOW")
        price = float(trade.get("price", 0) or 0)
        atr = float(trade.get("atr", 0) or 0)
        trend = trade.get("trend", "UPTREND")
        rsi = float(trade.get("rsi", 55) or 55)

        trade["strategy"] = strategy
        trade["price"] = price
        trade["atr"] = atr
        trade["trend"] = trend
        trade["rsi"] = rsi
        trade["regime"] = regime
        trade["mode"] = mode
        trade["volatility_state"] = volatility_state
        trade["breadth"] = breadth

        if not breadth_allows_trade(strategy, breadth):
            trade["rejection_reason"] = explain_rejection(trade, "breadth_blocked")
            log_candidate_decision(
                trade,
                status="rejected",
                reason="failed_breadth_filter",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            continue

        chosen_strategy = choose_trade_strategy(
            regime,
            volatility_state,
            trend,
            score,
            rsi,
        )
        if chosen_strategy and strategy != chosen_strategy:
            trade["strategy"] = chosen_strategy
            strategy = chosen_strategy

        if mode == "DEFENSIVE_BEAR" and strategy != "CALL":
            trade["rejection_reason"] = explain_rejection(trade, "execution_blocked")
            log_candidate_decision(
                trade,
                status="rejected",
                reason="failed_mode_filter",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            continue

        exec_guard = can_execute_trade(trade, buying_power())
        if isinstance(exec_guard, dict):
            blocked = exec_guard.get("blocked", False)
            exec_reason = exec_guard.get("reason", "failed_execution_guard")
        else:
            blocked = not bool(exec_guard)
            exec_reason = "failed_execution_guard"

        if blocked:
            trade["rejection_reason"] = explain_rejection(trade, "execution_blocked")
            log_candidate_decision(
                trade,
                status="rejected",
                reason=exec_reason,
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            continue

        if score < 90:
            trade["rejection_reason"] = explain_rejection(trade, "execution_blocked")
            log_candidate_decision(
                trade,
                status="rejected",
                reason="failed_score_threshold",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            continue

        if volatility_state == "ELEVATED" and confidence == "LOW":
            trade["rejection_reason"] = explain_rejection(trade, "execution_blocked")
            log_candidate_decision(
                trade,
                status="rejected",
                reason="failed_volatility_filter",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            continue

        option = trade.get("option")
        if option:
            trade["option"] = option

        # STEP 4: approval explanation gets attached ONLY after the trade passes filters
        trade["why"] = explain_trade_decision(
            trade,
            mode=mode,
            regime=regime,
            breadth=breadth,
            volatility=volatility_state,
        )

        approved_trades.append(trade)

    print_leaderboard(approved_trades)
    print_top_candidates(approved_trades, limit=5)
    save_top_candidates(approved_trades, limit=10)

    affordable = affordable_trade_count(approved_trades)
    limit = min(affordable, 3) if affordable > 0 else 0
    if approved_trades and limit <= 0:
        limit = 1

    selected_trades = queue_top_trades_plus(approved_trades, limit=limit)
    selected_keys = {
        (t.get("symbol"), t.get("strategy"))
        for t in selected_trades
    }

    for trade in approved_trades:
        key = (trade.get("symbol"), trade.get("strategy"))
        if key in selected_keys:
            log_candidate_decision(
                trade,
                status="selected",
                reason="selected_for_execution",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
        else:
            trade["rejection_reason"] = explain_rejection(trade, "not_selected")
            log_candidate_decision(
                trade,
                status="approved_not_selected",
                reason="approved_but_ranked_below_execution_cut",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )

    return approved_trades, selected_trades, mode, breadth, volatility_state


def run():
    write_bot_status(True, "starting")
    log_bot("Bot run started", "INFO")
    push_activity("SYSTEM", "Bot run started")

    monitor_open_positions()

    try:
        settle_cash()
        clear_candidates()

        snapshot = account_snapshot()
        print_account_snapshot(snapshot)

        write_system_status(regime="STARTING", volatility="UNKNOWN", mode="BOOT")

        governor = governor_status(
            current_open_positions=open_count(),
            executed_trades_today=entries_today(),
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

        regime = get_market_regime()
        volatility_payload = get_volatility_environment()
        volatility_state = volatility_payload.get("volatility", "UNKNOWN")
        sector_counts = sector_cap.get("sector_counts", {}) if isinstance(sector_cap, dict) else {}

        print("Market Regime:", regime)
        push_activity("MARKET", f"Market regime identified as {regime}")

        print("Building rotating watchlist...")
        watchlist = get_watchlist()
        print("Watchlist:", watchlist)
        push_activity("WATCHLIST", f"Watchlist built with {len(watchlist)} symbols")

        print("Scanning watchlist...")
        results = get_execution_candidates()

        print("Execution candidates:", [r.get("symbol") for r in results[:15]])
        print("Execution candidate count:", len(results))

        approved_trades, selected_trades, mode, breadth, volatility_state = process_signals(results, regime, volatility_payload)
        push_activity(
            "QUEUE",
            f"Approved {len(approved_trades)} research trades; selected {len(selected_trades)} execution trades in mode {mode}"
        )

        market_context = [
            f"Market regime: {regime}",
            f"Volatility state: {volatility_state}",
            f"Market breadth: {breadth}",
            f"Mode: {mode}",
        ]

        for trade in approved_trades:
            trade_id, detail = build_trade_detail(
                trade,
                market_context=market_context,
                volatility_state=volatility_state,
                sector_counts=sector_counts,
            )
            save_trade_detail(detail)
            trade["trade_id"] = trade_id

            push_signal(
                trade["symbol"],
                trade["strategy"],
                trade["score"],
                trade["confidence"],
                trade_id=trade_id
            )

            save_research_signal(
                trade,
                regime=regime,
                mode=mode,
                volatility=volatility_state,
                source="research",
            )

            add_trade_timeline_event(
                trade["symbol"],
                "RESEARCH_APPROVED",
                {
                    "trade_id": trade_id,
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                    "source": "research",
                }
            )

            append_trade_detail_timeline(
                trade_id,
                "RESEARCH_APPROVED",
                f"{trade['symbol']} approved in the research layer.",
                {
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                }
            )

            if trade.get("score", 0) >= 200:
                push_notification(
                    notif_type="HIGH_CONVICTION",
                    message=f"{trade['symbol']} high-conviction research setup detected (Score {trade['score']}).",
                    trade_id=trade_id,
                    min_tier="pro",
                    level="success",
                    score=trade["score"],
                    strategy=trade["strategy"],
                    volatility=volatility_state,
                    source="research",
                )

            if trade.get("score", 0) >= 120:
                research_entry = save_research_premium_analysis(
                    trade,
                    market_context=market_context,
                    mode=mode,
                    regime=regime,
                    volatility=volatility_state,
                )
                notify_trade_edge(trade["symbol"], research_entry.get("reasons", []))

                push_notification(
                    notif_type="RESEARCH_ALPHA",
                    message=f"{trade['symbol']} research alpha added to premium intelligence.",
                    trade_id=trade_id,
                    min_tier="elite",
                    level="info",
                    score=trade["score"],
                    strategy=trade["strategy"],
                    volatility=volatility_state,
                    source="research",
                )

        if brake.get("blocked"):
            write_bot_status(False, "blocked by drawdown brake")
            push_activity("RISK", "Blocked by drawdown brake")
            notify_trade_risk("PORTFOLIO", "Drawdown brake blocked new execution trades")
            push_notification(
                notif_type="RISK_WARNING",
                message="Execution blocked by drawdown brake.",
                min_tier="starter",
                level="warning",
                volatility=volatility_state,
                source="execution",
            )
            return

        if corr.get("blocked"):
            write_bot_status(False, "blocked by correlation risk")
            push_activity("RISK", "Blocked by correlation risk")
            notify_trade_risk("PORTFOLIO", corr.get("reason", "Correlation block"))
            push_notification(
                notif_type="RISK_WARNING",
                message=f"Execution blocked by correlation risk: {corr.get('reason', 'Correlation block')}",
                min_tier="starter",
                level="warning",
                volatility=volatility_state,
                source="execution",
            )
            return

        if sector_cap.get("blocked"):
            write_bot_status(False, "blocked by sector concentration cap")
            push_activity("RISK", "Blocked by sector concentration cap")
            notify_trade_risk("PORTFOLIO", sector_cap.get("reason", "Sector cap block"))
            push_notification(
                notif_type="RISK_WARNING",
                message=f"Execution blocked by sector cap: {sector_cap.get('reason', 'Sector cap block')}",
                min_tier="starter",
                level="warning",
                volatility=volatility_state,
                source="execution",
            )
            return

        if governor.get("blocked"):
            write_bot_status(False, "blocked by governor")
            joined = ", ".join(governor.get("reasons", []))
            push_activity("RISK", f"Blocked by governor: {joined}")
            notify_trade_risk("PORTFOLIO", f"Governor blocked execution: {joined}")
            push_notification(
                notif_type="RISK_WARNING",
                message=f"Execution blocked by governor: {joined}",
                min_tier="starter",
                level="warning",
                volatility=volatility_state,
                source="execution",
            )
            return

        if _reduced_risk_mode(brake, exposure):
            selected_trades = _trim_for_reduced_risk(selected_trades)
            push_activity("RISK", "Reduced-risk mode active: trimmed trade queue")

        for trade in selected_trades:
            if not trade.get("trade_id"):
                trade_id, detail = build_trade_detail(
                    trade,
                    market_context=market_context,
                    volatility_state=volatility_state,
                    sector_counts=sector_counts,
                )
                save_trade_detail(detail)
                trade["trade_id"] = trade_id

            alert_trade(trade)

            print("APPROVED:", trade["symbol"], "| Strategy:", trade["strategy"], "| Confidence:", trade["confidence"])
            if trade.get("option"):
                print("Best Option:", trade["option"])

            push_activity(
                "SIGNAL",
                f"{trade['symbol']} approved as {trade['strategy']} with score {trade['score']}",
                symbol=trade["symbol"],
                meta={
                    "trade_id": trade["trade_id"],
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"]
                }
            )

            add_trade_timeline_event(
                trade["symbol"],
                "EXECUTION_APPROVED",
                {
                    "trade_id": trade["trade_id"],
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                    "source": "execution",
                }
            )

            append_trade_detail_timeline(
                trade["trade_id"],
                "EXECUTION_APPROVED",
                f"{trade['symbol']} approved in the execution layer.",
                {
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                }
            )

            notify_trade_approved(trade)

            push_notification(
                notif_type="EXECUTION_APPROVED",
                message=f"{trade['symbol']} approved for live execution review.",
                trade_id=trade["trade_id"],
                min_tier="starter",
                level="info",
                score=trade["score"],
                strategy=trade["strategy"],
                volatility=volatility_state,
                source="execution",
            )

            if trade.get("score", 0) >= 120:
                premium_entry = save_premium_analysis(
                    trade,
                    market_context=market_context,
                    mode=mode,
                    regime=regime,
                    volatility=volatility_state,
                    source="execution",
                )
                notify_trade_edge(trade["symbol"], premium_entry.get("reasons", []))

        print("Processing trade queue...")

        today_count = entries_today()
        trades_remaining = max(0, 3 - today_count)

        print("Trades today:", today_count)
        print("Trades remaining today:", trades_remaining)
        print("Selected trades for execution:", [t.get("symbol") for t in selected_trades])

        if trades_remaining > 0 and selected_trades:
            execute_trades(selected_trades, limit=trades_remaining)

            for trade in selected_trades[:trades_remaining]:
              add_trade_timeline_event(
                  trade["symbol"],
                  "EXECUTED",
                  {
                      "trade_id": trade.get("trade_id"),
                      "strategy": trade["strategy"],
                      "score": trade["score"],
                      "source": "execution",
                  }
              )

              append_trade_detail_timeline(
                  trade.get("trade_id"),
                  "EXECUTED",
                  f"{trade['symbol']} entered execution flow.",
                  {
                      "strategy": trade["strategy"],
                      "score": trade["score"],
                  }
              )
        else:
            print("No trades executed. Either no selected trades or no daily capacity left.")

        print_positions()
        review_positions()

        closed_now = auto_close_positions()
        if closed_now:
            push_activity("AUTO_CLOSE", f"Auto-closed {len(closed_now)} position(s)")
            for closed in closed_now:
                symbol = closed.get("symbol", "UNKNOWN")
                reason = closed.get("reason", "AUTO_CLOSE")
                trade_id = closed.get("trade_id")

                add_trade_timeline_event(symbol, "CLOSED", {"reason": reason, "trade_id": trade_id})
                notify_trade_closed(symbol, reason)

                append_trade_detail_timeline(
                    trade_id,
                    "CLOSED",
                    f"{symbol} closed with reason: {reason}.",
                    {"reason": reason}
                )

                push_notification(
                    notif_type="AUTO_CLOSE",
                    message=f"{symbol} position auto-closed: {reason}",
                    trade_id=trade_id,
                    min_tier="starter",
                    level="warning",
                    volatility=volatility_state,
                    source="execution",
                )

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

    except Exception as e:
        write_bot_status(False, f"error: {e}")
        push_activity("ERROR", f"Bot error: {e}")
        raise


if __name__ == "__main__":
    run()
