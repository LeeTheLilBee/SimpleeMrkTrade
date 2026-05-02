from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from engine.position_monitor import monitor_open_positions
from engine.execution_source import get_execution_candidates
from engine.regime import get_market_regime
from engine.market_volatility import get_volatility_environment
from engine.signal_feed import push_signal
from engine.data_utils import safe_download
from engine.account_state import settle_cash
from engine.backtest_summary import print_backtest_summary
from engine.portfolio_summary import portfolio_summary
from engine.alerts import alert_trade
from engine.equity_curve import build_equity_curve
from engine.journal_export import export_journal
from engine.trade_analytics import analytics
from engine.performance_tracker import entries_today, performance_summary
from engine.risk_governor import governor_status
from engine.observatory_mode import (
    MODE_PAPER,
    normalize_mode,
    build_mode_context,
)
from engine.unrealized_pnl import unrealized_pnl
from engine.strategy_performance import strategy_breakdown
from engine.drawdown_tracker import build_drawdown_history
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
from engine.candidate_display import print_candidate_cards
from engine.candidate_log import show_candidates, clear_candidates
from engine.paper_portfolio import open_count, print_positions, show_positions
from engine.position_review import review_positions
from engine.watchlist import get_watchlist
from engine.execution_handoff import build_queued_trade_payload
from engine.options_lifecycle import build_options_lifecycle
from engine.process_signals import process_signals
from engine.execution_loop import execute_trades

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


def load_json(path, default):
    try:
        p = Path(path)
        if not p.exists():
            return default
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


def _safe_str(value, default=""):
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _norm_symbol(value):
    return _safe_str(value, "UNKNOWN").upper()


def _reduced_risk_mode(brake_payload, exposure_payload):
    return (
        _safe_dict(brake_payload).get("mode") == "REDUCED_RISK"
        or _safe_dict(exposure_payload).get("bucket") in ["ELEVATED", "HIGH"]
    )


def _trim_for_reduced_risk(selected_trades):
    return selected_trades[:1] if selected_trades else selected_trades


def _resolve_bot_mode(explicit_mode=None):
    return normalize_mode(explicit_mode or MODE_PAPER)


def _log_observatory_banner(mode_context, trading_mode):
    print("\n" + "=" * 80)
    print(
        f"THE OBSERVATORY ONLINE | {mode_context.get('mode_label', trading_mode)} | "
        f"{trading_mode.upper()}"
    )
    print("=" * 80 + "\n")


def _candidate_is_display_worthy(trade):
    if not isinstance(trade, dict):
        return False

    strategy = _safe_str(trade.get("strategy"), "CALL").upper()
    score = _safe_float(trade.get("fused_score", trade.get("score", 0)), 0.0)
    confidence_value = _safe_str(trade.get("confidence"), "LOW").upper()

    if strategy == "NO_TRADE":
        return False
    if score < 90:
        return False
    if confidence_value not in {"MEDIUM", "HIGH"}:
        return False

    return True


def _filter_display_candidates(candidates):
    if not isinstance(candidates, list):
        return []
    return [trade for trade in candidates if _candidate_is_display_worthy(trade)]


def scan_stock(symbol, regime):
    df = safe_download(symbol, period="3mo", auto_adjust=True, progress=False)

    if df is None or df.empty or len(df) < 50:
        print(symbol, "| Not enough data")
        log_bot(f"{symbol} skipped: not enough data", "WARN")
        return None

    return {
        "symbol": symbol,
        "regime": regime,
    }


def _build_execution_queue(selected_trades, resolved_trading_mode):
    execution_queue = []

    if not selected_trades:
        return execution_queue

    for candidate in selected_trades:
        option_chain = (
            candidate.get("option_chain", [])
            if isinstance(candidate.get("option_chain"), list)
            else []
        )

        print("PRE-LIFECYCLE CANDIDATE:", {
            "symbol": candidate.get("symbol"),
            "trade_id": candidate.get("trade_id"),
            "research_approved": candidate.get("research_approved"),
            "execution_ready": candidate.get("execution_ready"),
            "selected_for_execution": candidate.get("selected_for_execution"),
            "score": candidate.get("score"),
            "fused_score": candidate.get("fused_score"),
            "v2_score": candidate.get("v2_score"),
            "v2_reason": candidate.get("v2_reason"),
            "v2_vehicle_bias": candidate.get("v2_vehicle_bias"),
            "readiness_score": candidate.get("readiness_score"),
            "promotion_score": candidate.get("promotion_score"),
            "rebuild_pressure": candidate.get("rebuild_pressure"),
            "vehicle_selected": candidate.get("vehicle_selected"),
            "capital_required": candidate.get("capital_required"),
            "minimum_trade_cost": candidate.get("minimum_trade_cost"),
            "trading_mode": candidate.get("trading_mode", resolved_trading_mode),
        })

        lifecycle = build_options_lifecycle(
            candidate=candidate,
            option_chain=option_chain,
            account_context={"cash_available": _safe_float(candidate.get("capital_available", 0.0), 0.0)},
            mode=resolved_trading_mode,
            allow_stock_fallback=True,
        )

        print("POST-LIFECYCLE:", {
            "symbol": lifecycle.get("symbol"),
            "trade_id": lifecycle.get("trade_id"),
            "research_approved": lifecycle.get("research_approved"),
            "execution_ready": lifecycle.get("execution_ready"),
            "lifecycle_stage": lifecycle.get("lifecycle_stage"),
            "selected_vehicle": lifecycle.get("selected_vehicle"),
            "score": lifecycle.get("score"),
            "fused_score": lifecycle.get("fused_score"),
            "v2_score": lifecycle.get("v2_score"),
            "v2_reason": lifecycle.get("v2_reason"),
            "v2_vehicle_bias": lifecycle.get("v2_vehicle_bias"),
            "readiness_score": lifecycle.get("readiness_score"),
            "promotion_score": lifecycle.get("promotion_score"),
            "rebuild_pressure": lifecycle.get("rebuild_pressure"),
            "final_decision": lifecycle.get("final_decision"),
            "final_reason": lifecycle.get("final_reason"),
            "final_reason_code": lifecycle.get("final_reason_code"),
            "trading_mode": resolved_trading_mode,
        })

        if lifecycle.get("final_decision") in {"APPROVE", "WARN"}:
            queued_trade = build_queued_trade_payload(
                lifecycle,
                mode=resolved_trading_mode,
            )

            print("POST-QUEUE-PAYLOAD:", {
                "symbol": queued_trade.get("symbol"),
                "trade_id": queued_trade.get("trade_id"),
                "research_approved": queued_trade.get("research_approved"),
                "execution_ready": queued_trade.get("execution_ready"),
                "selected_for_execution": queued_trade.get("selected_for_execution"),
                "score": queued_trade.get("score"),
                "fused_score": queued_trade.get("fused_score"),
                "v2_score": queued_trade.get("v2_score"),
                "v2_reason": queued_trade.get("v2_reason"),
                "v2_vehicle_bias": queued_trade.get("v2_vehicle_bias"),
                "readiness_score": queued_trade.get("readiness_score"),
                "promotion_score": queued_trade.get("promotion_score"),
                "rebuild_pressure": queued_trade.get("rebuild_pressure"),
                "vehicle_selected": queued_trade.get("vehicle_selected"),
                "capital_required": queued_trade.get("capital_required"),
                "minimum_trade_cost": queued_trade.get("minimum_trade_cost"),
                "trading_mode": resolved_trading_mode,
            })

            execution_queue.append(queued_trade)

    return execution_queue


def run(trading_mode="paper"):
    trading_mode = _resolve_bot_mode(trading_mode)
    mode_context = build_mode_context(trading_mode)

    _log_observatory_banner(mode_context, trading_mode)

    write_bot_status(True, f"starting:{trading_mode}")
    log_bot(
        f"Bot run started in {mode_context['mode_label']} ({trading_mode})",
        "INFO",
    )
    push_activity(
        "SYSTEM",
        f"Bot run started in {mode_context['mode_label']} ({trading_mode})",
    )

    monitor_open_positions()

    try:
        settle_cash()
        clear_candidates()

        snapshot = account_snapshot()
        print_account_snapshot(snapshot)

        write_system_status(
            regime="STARTING",
            volatility="UNKNOWN",
            mode=f"BOOT_{trading_mode.upper()}",
        )

        governor = governor_status(
            current_open_positions=open_count(),
            executed_entries_today=entries_today(),
            executed_trades_today=entries_today(),
            trading_mode=trading_mode,
        )

        resolved_trading_mode = normalize_mode(
            governor.get("trading_mode") if isinstance(governor, dict) else trading_mode
        )
        resolved_mode_context = build_mode_context(resolved_trading_mode)

        print("RUN GOVERNOR MODE CHECK:", {
            "requested_trading_mode": trading_mode,
            "governor_returned_mode": governor.get("trading_mode") if isinstance(governor, dict) else None,
        })

        brake = drawdown_brake()
        corr = correlation_risk_status()
        sector_cap = sector_concentration_status()
        exposure = exposure_bucket_status()

        print("Mode Context:", resolved_mode_context)
        print("Governor:", governor)
        print("Drawdown Brake:", brake)
        print("Correlation Risk:", corr)
        print("Sector Cap:", sector_cap)
        print("Exposure Bucket:", exposure)

        regime = get_market_regime()
        volatility_payload = get_volatility_environment()
        volatility_state = volatility_payload.get("volatility", volatility_payload.get("state", "UNKNOWN"))
        sector_counts = sector_cap.get("sector_counts", {}) if isinstance(sector_cap, dict) else {}

        print("Market Regime:", regime)
        push_activity("MARKET", f"Market regime identified as {regime}")

        print("Building rotating watchlist...")
        watchlist = get_watchlist(limit=50, universe_limit=220)
        print("Watchlist:", watchlist)
        push_activity("WATCHLIST", f"Watchlist built with {len(watchlist)} symbols")

        print("Scanning watchlist aggressively...")
        results = get_execution_candidates(force_rebuild=True, watchlist=watchlist)
        display_candidates = _filter_display_candidates(results)
        print("Execution candidates:", [r.get("symbol") for r in results[:20]])
        print("Execution candidate count:", len(results))

        if display_candidates:
            try:
                print_candidate_cards(display_candidates[:12])
            except Exception:
                pass

        execution_universe = load_json("data/execution_universe.json", {})
        spotlight = execution_universe.get("spotlight", []) if isinstance(execution_universe, dict) else []
        print("Execution spotlight:", [r.get("symbol") for r in spotlight[:5]])

        push_activity("EXECUTION", f"Aggressive execution universe rebuilt with {len(results)} candidates")
        push_activity("SPOTLIGHT", f"Top spotlight contains {len(spotlight)} names")

        approved_trades, selected_trades, mode, breadth, volatility_state = process_signals(
            results,
            regime,
            volatility_payload,
            trading_mode=resolved_trading_mode,
        )

        push_activity(
            "QUEUE",
            (
                f"Approved {len(approved_trades)} research trades; "
                f"selected {len(selected_trades)} execution trades in market mode "
                f"{mode} / trading mode {resolved_mode_context['mode_label']}"
            ),
        )

        market_context = [
            f"Market regime: {regime}",
            f"Volatility state: {volatility_state}",
            f"Market breadth: {breadth}",
            f"Mode: {mode}",
            f"Trading mode: {resolved_trading_mode}",
            f"Trading mode label: {resolved_mode_context['mode_label']}",
            f"Mode shell: {resolved_mode_context['mode_shell']}",
            f"Theme family: {resolved_mode_context['theme_family']}",
        ]

        for trade in approved_trades:
            if not trade.get("trade_id"):
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
                trade_id=trade.get("trade_id"),
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
                    "trade_id": trade.get("trade_id"),
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                    "source": "research",
                    "trading_mode": resolved_trading_mode,
                },
            )

            append_trade_detail_timeline(
                trade.get("trade_id"),
                "RESEARCH_APPROVED",
                f"{trade['symbol']} approved in the research layer.",
                {
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                    "trading_mode": resolved_trading_mode,
                },
            )

            if trade.get("score", 0) >= 200:
                push_notification(
                    notif_type="HIGH_CONVICTION",
                    message=f"{trade['symbol']} high-conviction research setup detected (Score {trade['score']}).",
                    trade_id=trade.get("trade_id"),
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
                    trade_id=trade.get("trade_id"),
                    min_tier="elite",
                    level="info",
                    score=trade["score"],
                    strategy=trade["strategy"],
                    volatility=volatility_state,
                    source="research",
                )

        if brake.get("blocked"):
            write_bot_status(False, f"blocked_by_drawdown:{resolved_trading_mode}")
            push_activity("RISK", f"Blocked by drawdown brake in {resolved_trading_mode} mode")
            notify_trade_risk("PORTFOLIO", "Drawdown brake blocked new execution trades")
            push_notification(
                notif_type="RISK_WARNING",
                message=f"Execution blocked by drawdown brake in {resolved_trading_mode} mode.",
                min_tier="starter",
                level="warning",
                volatility=volatility_state,
                source="execution",
            )
            return

        if corr.get("blocked"):
            write_bot_status(False, f"blocked_by_correlation:{resolved_trading_mode}")
            push_activity("RISK", f"Blocked by correlation risk in {resolved_trading_mode} mode")
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
            write_bot_status(False, f"blocked_by_sector_cap:{resolved_trading_mode}")
            push_activity("RISK", f"Blocked by sector concentration cap in {resolved_trading_mode} mode")
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
            joined = ", ".join(governor.get("reasons", []))
            write_bot_status(False, f"blocked_by_governor:{resolved_trading_mode}")
            push_activity("RISK", f"Blocked by governor in {resolved_trading_mode} mode: {joined}")
            notify_trade_risk("PORTFOLIO", f"Governor blocked execution: {joined}")
            push_notification(
                notif_type="RISK_WARNING",
                message=f"Execution blocked by governor in {resolved_trading_mode} mode: {joined}",
                min_tier="starter",
                level="warning",
                volatility=volatility_state,
                source="execution",
            )
            return

        if _reduced_risk_mode(brake, exposure):
            selected_trades = _trim_for_reduced_risk(selected_trades)
            push_activity("RISK", f"Reduced-risk mode active in {resolved_trading_mode}: trimmed trade queue")

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

            print(
                "APPROVED:",
                trade["symbol"],
                "| Strategy:",
                trade["strategy"],
                "| Confidence:",
                trade["confidence"],
            )

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
                    "confidence": trade["confidence"],
                    "trading_mode": resolved_trading_mode,
                },
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
                    "trading_mode": resolved_trading_mode,
                },
            )

            append_trade_detail_timeline(
                trade["trade_id"],
                "EXECUTION_APPROVED",
                f"{trade['symbol']} approved in the execution layer.",
                {
                    "strategy": trade["strategy"],
                    "score": trade["score"],
                    "confidence": trade["confidence"],
                    "trading_mode": resolved_trading_mode,
                },
            )

            notify_trade_approved(trade)

            push_notification(
                notif_type="EXECUTION_APPROVED",
                message=f"{trade['symbol']} approved for execution review in {resolved_trading_mode} mode.",
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
        print("Trading mode:", resolved_trading_mode)
        print("Mode context:", resolved_mode_context)

        execution_queue = []

        if trades_remaining > 0 and selected_trades:
            print("SELECTED TRADES DEBUG SNAPSHOT:")
            for idx, row in enumerate(selected_trades):
                if not isinstance(row, dict):
                    print(f"[{idx}] NON-DICT:", type(row))
                    continue
                print(
                    f"[{idx}]",
                    {
                        "symbol": row.get("symbol"),
                        "trade_id": row.get("trade_id"),
                        "research_approved": row.get("research_approved"),
                        "execution_ready": row.get("execution_ready"),
                        "selected_for_execution": row.get("selected_for_execution"),
                        "score": row.get("score"),
                        "fused_score": row.get("fused_score"),
                        "v2_score": row.get("v2_score"),
                        "v2_reason": row.get("v2_reason"),
                        "v2_vehicle_bias": row.get("v2_vehicle_bias"),
                        "readiness_score": row.get("readiness_score"),
                        "promotion_score": row.get("promotion_score"),
                        "rebuild_pressure": row.get("rebuild_pressure"),
                        "vehicle_selected": row.get("vehicle_selected"),
                        "capital_required": row.get("capital_required"),
                        "minimum_trade_cost": row.get("minimum_trade_cost"),
                        "trading_mode": row.get("trading_mode"),
                    },
                )

            execution_queue = _build_execution_queue(
                selected_trades,
                resolved_trading_mode,
            )

            packet = execute_trades(
                execution_queue,
                limit=trades_remaining,
                trading_mode=resolved_trading_mode,
            )
            executed_results = packet.get("results", []) if isinstance(packet, dict) else []

            print("EXECUTION RESULTS COUNT:", len(executed_results))

            for result in executed_results:
                if not isinstance(result, dict):
                    print("EXECUTION RESULT MALFORMED:", type(result))
                    continue

                lifecycle_after = result.get("lifecycle_after", {}) or {}
                trade_id = (
                    _safe_dict(lifecycle_after.get("raw")).get("trade_id")
                    or lifecycle_after.get("trade_id")
                    or result.get("trade_id")
                )

                if result.get("success"):
                    symbol = lifecycle_after.get("symbol", result.get("symbol", "UNKNOWN"))

                    print("EXECUTION SUCCESS:", {
                        "symbol": symbol,
                        "trade_id": trade_id,
                        "reason": _safe_dict(result.get("guard")).get("guard_reason", "ok"),
                        "trading_mode": resolved_trading_mode,
                    })

                    add_trade_timeline_event(
                        symbol,
                        "EXECUTED",
                        {
                            "trade_id": trade_id,
                            "strategy": lifecycle_after.get("strategy"),
                            "score": lifecycle_after.get("score"),
                            "source": "execution",
                            "trading_mode": resolved_trading_mode,
                        },
                    )

                    append_trade_detail_timeline(
                        trade_id,
                        "EXECUTED",
                        f"{symbol} entered execution flow.",
                        {
                            "strategy": lifecycle_after.get("strategy"),
                            "score": lifecycle_after.get("score"),
                            "trading_mode": resolved_trading_mode,
                        },
                    )
                else:
                    symbol = result.get("symbol", "UNKNOWN")
                    rejection_reason = _safe_dict(result.get("guard")).get("guard_reason", "execution_rejected")

                    print("EXECUTION REJECTED:", {
                        "symbol": symbol,
                        "trade_id": trade_id,
                        "reason": rejection_reason,
                        "trading_mode": resolved_trading_mode,
                    })

                    if trade_id:
                        append_trade_detail_timeline(
                            trade_id,
                            "EXECUTION_REJECTED",
                            f"{symbol} failed execution: {rejection_reason}.",
                            {
                                "reason": rejection_reason,
                                "trading_mode": resolved_trading_mode,
                            },
                        )

                    push_notification(
                        notif_type="EXECUTION_REJECTED",
                        message=f"{symbol} execution rejected: {rejection_reason}",
                        trade_id=trade_id,
                        min_tier="starter",
                        level="warning",
                        volatility=volatility_state,
                        source="execution",
                    )

            print("POST-EXECUTION OPEN COUNT:", open_count())
            print("POST-EXECUTION OPEN POSITIONS SNAPSHOT:")
            show_positions()
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

                add_trade_timeline_event(
                    symbol,
                    "CLOSED",
                    {
                        "reason": reason,
                        "trade_id": trade_id,
                        "trading_mode": resolved_trading_mode,
                    },
                )

                notify_trade_closed(symbol, reason)

                append_trade_detail_timeline(
                    trade_id,
                    "CLOSED",
                    f"{symbol} closed with reason: {reason}.",
                    {
                        "reason": reason,
                        "trading_mode": resolved_trading_mode,
                    },
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
            mode=f"{mode}|{resolved_trading_mode}",
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

        write_bot_status(False, f"completed:{resolved_trading_mode}")
        push_activity(
            "SYSTEM",
            f"Bot run completed in {resolved_mode_context['mode_label']} ({resolved_trading_mode})",
        )

    except Exception as e:
        write_bot_status(False, f"error:{trading_mode}:{e}")
        push_activity("ERROR", f"Bot error in {trading_mode} mode: {e}")
        raise


if __name__ == "__main__":
    run()
