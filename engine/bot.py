from engine.explainability_engine import (
    explain_trade_decision,
    explain_rejection,
    build_rejection_analysis,
    explain_reentry_detail,
)
from engine.position_monitor import monitor_open_positions
from engine.execution_source import get_execution_candidates
from engine.regime import get_market_regime
from engine.market_volatility import get_volatility_environment
from engine.options_intelligence import (
    choose_best_option,
    option_is_executable,
    explain_option_choice,
)

from engine.premium_feed import write_premium_feed_item
from engine.options_lifecycle import build_options_lifecycle
from engine.execution_handoff import build_queued_trade_payload
from engine.reentry_guard import reentry_allowed
from engine.signal_feed import push_signal
from engine.rsi_engine import calculate_rsi
from engine.volume_engine import volume_surge
from engine.breakout_engine import breakout
from engine.signal_engine import build_signal
from engine.canonical_candidate import build_canonical_candidate
from engine.candidate_display import print_candidate_cards
from engine.candidate_log import remember_candidate, show_candidates, clear_candidates
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
from engine.paper_portfolio import open_count, print_positions, show_positions, get_position
from engine.position_cap import trade_slots_left
from engine.trade_history import executed_trade_count
from engine.daily_risk import trades_left_today
from engine.signal_history import remember_signal
from engine.atr_engine import calculate_atr
from engine.leaderboard import print_leaderboard
from engine.position_review import review_positions
from engine.data_utils import safe_download
from engine.execution_loop import execute_trades
from engine.capital_guard import affordable_trade_count
from engine.backtest_summary import print_backtest_summary
from engine.portfolio_summary import portfolio_summary
from engine.account_state import settle_cash, buying_power
from engine.alerts import alert_trade
from engine.equity_curve import build_equity_curve
from engine.journal_export import export_journal
from engine.trade_analytics import analytics
from engine.performance_tracker import entries_today, performance_summary
from engine.market_snapshot import save_market_snapshot
from engine.top_candidates_store import save_top_candidates
from engine.top_candidates_view import print_top_candidates
from engine.daily_report import write_daily_report
from engine.risk_governor import governor_status
from engine.observatory_mode import (
    MODE_SURVEY,
    MODE_PAPER,
    MODE_LIVE,
    normalize_mode,
    get_mode_config,
    build_mode_payload,
    build_mode_context,
)
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

import json
from pathlib import Path

def load_json(path, default):
    try:
        p = Path(path)
        if not p.exists():
            return default
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default
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


def _resolve_bot_mode(explicit_mode=None):
    return normalize_mode(explicit_mode or MODE_PAPER)


def _mode_context(explicit_mode=None):
    mode = _resolve_bot_mode(explicit_mode)
    cfg = get_mode_config(mode)
    payload = build_mode_payload(mode)
    return mode, cfg, payload


def _governor_allows_execution(governor, mode):
    if not isinstance(governor, dict):
        return False

    if mode == MODE_SURVEY:
        hard_reasons = {
            "daily_entry_cap",
            "max_drawdown_hit",
            "max_open_positions",
            "max_daily_loss_hit",
            "kill_switch",
        }
        reasons = set(governor.get("reasons", []) or [])
        return len(reasons.intersection(hard_reasons)) == 0

    return bool(governor.get("ok_to_trade", False))


def validate_contract_executable(contract: dict) -> tuple[bool, str]:
    if not contract:
        return False, "no_contract"

    bid = float(contract.get("bid") or 0.0)
    ask = float(contract.get("ask") or 0.0)
    mark = float(contract.get("mark") or 0.0)
    last = float(contract.get("last") or 0.0)
    spread = float(contract.get("spread") or contract.get("bidAskSpread") or 0.0)
    spread_pct = float(contract.get("spread_pct") or 0.0)
    volume = int(contract.get("volume") or 0)
    open_interest = int(contract.get("open_interest") or 0)
    dte = int(contract.get("dte") or 0)

    # do not open fresh positions into same-day expiry junk
    if dte <= 0:
        return False, "dte_too_low"

    # reject dust/lottery pricing
    if ask <= 0.05 or mark <= 0.05:
        return False, "premium_too_small"

    # reject fake-looking chain artifacts
    if bid <= 0.0 and ask <= 0.01:
        return False, "stale_or_dust_contract"

    # reject illiquid contracts
    if volume < 100:
        return False, "volume_too_low"

    if open_interest < 500:
        return False, "open_interest_too_low"

    # reject ugly spreads
    if spread >= 0.50:
        return False, "spread_too_wide"

    if spread_pct >= 0.20:
        return False, "spread_pct_too_wide"

    # sanity: require some usable pricing
    if last <= 0.0 and mark <= 0.0:
        return False, "no_usable_price"

    return True, "ok"


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
        "status": status,
        "reason": reason,
        "mode": mode,
        "breadth": breadth,
        "volatility_state": volatility_state,
        "timestamp": trade.get("timestamp"),
        "why": trade.get("why", []),
        "rejection_reason": trade.get("rejection_reason"),
        "rejection_analysis": trade.get("rejection_analysis", []),
        "option": trade.get("option"),
        "option_contract_score": trade.get("option_contract_score"),
        "option_explanation": trade.get("option_explanation", []),
        "trade_id": trade.get("trade_id"),
        "stronger_competing_setups": trade.get("stronger_competing_setups", []),
    }
    if extra:
        payload.update(extra)
    remember_candidate(payload)


def clamp_stock_trade_size_to_cash_reserve(price, cash, min_cash_reserve=100.0, commission=1.0):
    try:
        price = float(price or 0)
        cash = float(cash or 0)
        min_cash_reserve = float(min_cash_reserve or 100.0)
        commission = float(commission or 1.0)
    except Exception:
        return 0

    if price <= 0:
        return 0

    spendable_cash = cash - min_cash_reserve - commission
    if spendable_cash <= 0:
        return 0

    max_size = int(spendable_cash // price)
    return max(0, max_size)


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _safe_str(value, default=""):
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _candidate_is_display_worthy(trade):
    if not isinstance(trade, dict):
        return False

    strategy = _safe_str(trade.get("strategy"), "CALL").upper()
    score = _safe_float(trade.get("score", 0), 0.0)
    confidence = _safe_str(trade.get("confidence"), "LOW").upper()

    if strategy == "NO_TRADE":
        return False

    if score < 90:
        return False

    if confidence not in {"MEDIUM", "HIGH"}:
        return False

    return True


def _filter_display_candidates(candidates):
    if not isinstance(candidates, list):
        return []
    return [trade for trade in candidates if _candidate_is_display_worthy(trade)]


def _approved_or_nearly_approved_debug_rows(debug_rows):
    clean = []
    for row in debug_rows:
        if not isinstance(row, dict):
            continue

        if row.get("approved") is True:
            clean.append(row)
            continue

        blocked_at = _safe_str(row.get("blocked_at"))
        final_reason = _safe_str(row.get("final_reason"))

        if blocked_at == "execution_guard" and final_reason in {
            "cash_reserve_would_be_broken",
            "max_open_positions_reached",
            "cash_reserve_already_too_low",
        }:
            clean.append(row)

    return clean


def stronger_competing_setups(trade, selected_trades):
    current_score = float(trade.get("score", 0) or 0)

    stronger = []
    for other in selected_trades:
        other_symbol = other.get("symbol")
        other_strategy = other.get("strategy")
        other_score = float(other.get("score", 0) or 0)

        if other_symbol == trade.get("symbol") and other_strategy == trade.get("strategy"):
            continue

        if other_score >= current_score:
            stronger.append({
                "symbol": other_symbol,
                "strategy": other_strategy,
                "score": other_score,
            })

    stronger.sort(key=lambda x: x["score"], reverse=True)
    return stronger


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


def resolve_market_mode(regime, breadth, volatility_payload=None):
    return market_mode(regime, breadth)


def log_rejection(trade, symbol, reason_key, machine_reason, mode, breadth, volatility_state):
    trade["rejection_reason"] = explain_rejection(trade, reason_key)
    trade["rejection_analysis"] = build_rejection_analysis(
        trade,
        reason_key,
        machine_reason,
    )

    summary = trade.get("rejection_reason", "Rejected for unspecified reason.")

    if str(machine_reason).startswith("reentry_blocked:"):
        detail = str(machine_reason).split("reentry_blocked:", 1)[1]
        clean_detail = explain_reentry_detail(detail)
        summary = f"{summary} Specifically, {clean_detail}."

    trade["rejection_reason"] = summary

    write_premium_feed_item({
        "title": f"{symbol} Rejected",
        "summary": summary,
        "pro_lines": trade.get("rejection_analysis", []),
        "elite_lines": trade.get("option_explanation", []),
        "timestamp": trade.get("timestamp"),
        "mode": mode,
        "stronger_competing_setups": trade.get("stronger_competing_setups", []),
    })

    log_candidate_decision(
        trade,
        status="rejected",
        reason=machine_reason,
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
        extra={
            "rejection_analysis": trade.get("rejection_analysis", []),
            "stronger_competing_setups": trade.get("stronger_competing_setups", []),
        },
    )


def log_approval(trade, mode, regime, breadth, volatility_state):
    symbol = str(trade.get("symbol", "UNKNOWN") or "UNKNOWN").upper().strip()

    why_value = trade.get("why", [])
    why_lines = []

    if isinstance(why_value, list):
        why_lines = [str(x).strip() for x in why_value if str(x).strip()]
    elif isinstance(why_value, dict):
        for v in why_value.values():
            text = str(v).strip()
            if text:
                why_lines.append(text)
    elif isinstance(why_value, str):
        text = why_value.strip()
        if text:
            why_lines = [text]

    option_value = trade.get("option_explanation", [])
    option_lines = []
    if isinstance(option_value, list):
        option_lines = [str(x).strip() for x in option_value if str(x).strip()]
    elif isinstance(option_value, dict):
        for v in option_value.values():
            text = str(v).strip()
            if text:
                option_lines.append(text)
    elif isinstance(option_value, str):
        text = option_value.strip()
        if text:
            option_lines = [text]

    summary_line = (
        why_lines[0]
        if why_lines
        else "High-conviction setup aligned with system conditions."
    )

    trade["why"] = why_lines
    trade["option_explanation"] = option_lines

    write_premium_feed_item({
        "title": f"{symbol} Approved",
        "summary": summary_line,
        "pro_lines": why_lines,
        "elite_lines": option_lines,
        "timestamp": trade.get("timestamp"),
        "mode": mode,
        "regime": regime,
        "breadth": breadth,
        "volatility_state": volatility_state,
        "symbol": symbol,
        "strategy": trade.get("strategy", "CALL"),
        "score": trade.get("score", 0),
        "confidence": trade.get("confidence", "LOW"),
    })

def process_signals(results, regime, volatility_payload, trading_mode="paper"):
    """
    Fused signal processor.

    Core behavior:
    - research approval is separate from execution readiness
    - V2 overlay can influence conviction and vehicle choice
    - options and stock fallback are decided inside one candidate path
    - Soulaana can still surface strong research even if execution is blocked
    - execution queue only sees execution-ready candidates
    - every candidate is normalized before it is logged, remembered, or displayed
    """
    from engine.candidate_fusion import build_fused_candidate, finalize_candidate_state
    from engine.observatory_mode import (
        normalize_mode,
        build_mode_context,
        apply_mode_to_execution_guard,
    )

    trading_mode = normalize_mode(trading_mode)
    trading_mode_context = build_mode_context(trading_mode)

    def _safe_float(value, default=0.0):
        try:
            return float(value)
        except Exception:
            return float(default)

    def _safe_str(value, default=""):
        try:
            text = str(value).strip()
            return text if text else default
        except Exception:
            return default

    def _safe_list(value):
        return value if isinstance(value, list) else []

    def _safe_dict(value):
        return value if isinstance(value, dict) else {}

    def _norm_symbol(value):
        return _safe_str(value, "UNKNOWN").upper()

    def _remember_candidate_row(
        trade,
        *,
        status,
        reason,
        mode,
        trading_mode_value,
        breadth,
        volatility_state,
        capital_required,
        capital_available,
        selected_for_execution=False,
        extra=None,
    ):
        payload = {}
        try:
            payload = build_canonical_candidate(
                trade,
                status=status,
                reason=reason,
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
                decision_reason=reason,
                selected_for_execution=selected_for_execution,
                capital_required=capital_required,
                capital_available=capital_available,
            )
        except Exception:
            payload = {
                "symbol": trade.get("symbol", "UNKNOWN"),
                "strategy": trade.get("strategy", "CALL"),
                "score": _safe_float(trade.get("fused_score", trade.get("score", 0)), 0.0),
                "confidence": _safe_str(trade.get("confidence", "LOW"), "LOW"),
                "status": status,
                "reason": reason,
                "decision_reason": reason,
                "mode": mode,
                "trading_mode": trading_mode_value,
                "breadth": breadth,
                "volatility_state": volatility_state,
                "capital_required": capital_required,
                "capital_available": capital_available,
                "selected_for_execution": selected_for_execution,
                "timestamp": trade.get("timestamp"),
                "vehicle_selected": trade.get("vehicle_selected", "RESEARCH_ONLY"),
                "minimum_trade_cost": trade.get("minimum_trade_cost", 0.0),
                "research_approved": bool(trade.get("research_approved", False)),
                "execution_ready": bool(trade.get("execution_ready", False)),
                "blocked_at": trade.get("blocked_at", ""),
                "final_reason": trade.get("final_reason", reason),
                "vehicle_reason": trade.get("vehicle_reason", ""),
            }
        if isinstance(extra, dict):
            payload.update(extra)
        payload["trading_mode"] = trading_mode_value
        try:
            remember_candidate(payload)
        except Exception:
            pass
        trade["candidate_display"] = payload
        return payload

    def _get_v2_overlay(symbol, trade):
        try:
            if "get_v2_candidate_overlay" in globals():
                row = get_v2_candidate_overlay(symbol, trade)
                return row if isinstance(row, dict) else {}
        except Exception:
            pass
        try:
            if "get_v2_signal_overlay" in globals():
                row = get_v2_signal_overlay(symbol, trade)
                return row if isinstance(row, dict) else {}
        except Exception:
            pass
        return {}

    def _governor_snapshot(trading_mode=None):
        try:
            requested_mode = normalize_mode(trading_mode or "paper")
            entries_today = 0
            try:
                perf = performance_summary()
                if isinstance(perf, dict):
                    entries_today = int(_safe_float(perf.get("entries_today", 0), 0))
            except Exception:
                entries_today = 0

            print("GOVERNOR ENTRY FEED:", {
                "entries_today_from_perf": entries_today,
                "open_positions": open_count(),
                "requested_trading_mode": requested_mode,
            })

            gov = governor_status(
                current_open_positions=open_count(),
                executed_entries_today=entries_today,
                trading_mode=requested_mode,
            )

            print("PROCESS SIGNALS GOVERNOR MODE CHECK:", {
                "requested_trading_mode": requested_mode,
                "governor_returned_mode": gov.get("trading_mode") if isinstance(gov, dict) else None,
            })
            return gov if isinstance(gov, dict) else {}
        except Exception:
            return {}

    def _governor_execution_block_reason(governor):
        if not isinstance(governor, dict):
            return ""
        if not bool(governor.get("blocked", False)):
            return ""
        reasons = _safe_list(governor.get("reasons", []))
        if reasons:
            return f"governor_blocked:{reasons[0]}"
        return "governor_blocked"

    def _sync_debug_from_fused(debug_row, fused):
        debug_row["vehicle_selected"] = fused.get("vehicle_selected", "RESEARCH_ONLY")
        debug_row["capital_required"] = fused.get("capital_required", 0.0)
        debug_row["minimum_trade_cost"] = fused.get("minimum_trade_cost", 0.0)
        debug_row["research_approved"] = bool(fused.get("research_approved", False))
        debug_row["execution_ready"] = bool(fused.get("execution_ready", False))
        debug_row["selected_for_execution"] = bool(fused.get("selected_for_execution", False))
        debug_row["blocked_at"] = fused.get("blocked_at", debug_row.get("blocked_at", ""))
        debug_row["final_reason"] = fused.get("final_reason", debug_row.get("final_reason", ""))
        debug_row["trading_mode"] = fused.get("trading_mode", debug_row.get("trading_mode", trading_mode))
        return debug_row

    def _finalize_for_exit(fused, debug_row, blocked_at="", reason=""):
        if blocked_at:
            fused["blocked_at"] = blocked_at
        if reason:
            fused["final_reason"] = reason
        fused = finalize_candidate_state(fused)
        debug_row = _sync_debug_from_fused(debug_row, fused)
        return fused, debug_row

    results = _safe_list(results)
    research_approved = []
    execution_ready = []
    debug_rows = []

    breadth = market_breadth(results)
    print("Market Breadth:", breadth)

    mode = resolve_market_mode(regime, breadth, volatility_payload)
    print("Market Mode:", mode)

    volatility_state = _safe_str((volatility_payload or {}).get("state", "NORMAL"), "NORMAL")
    vix_value = (volatility_payload or {}).get("vix", "N/A")
    print("Volatility State:", volatility_state, "| VIX:", vix_value)

    capital_available_now = round(_safe_float(buying_power(), 0.0), 2)

    governor = _governor_snapshot(trading_mode=trading_mode)
    resolved_trading_mode = normalize_mode(
        governor.get("trading_mode") if isinstance(governor, dict) else trading_mode
    )
    resolved_trading_mode_context = build_mode_context(resolved_trading_mode)
    governor_reason = _governor_execution_block_reason(governor)

    for raw_trade in results:
        trade = dict(raw_trade) if isinstance(raw_trade, dict) else {}

        symbol = _norm_symbol(trade.get("symbol", "UNKNOWN"))
        strategy = _safe_str(trade.get("strategy", "CALL"), "CALL").upper()
        score = _safe_float(trade.get("score", 0), 0.0)
        confidence = _safe_str(trade.get("confidence", "LOW"), "LOW").upper()
        price = _safe_float(
            trade.get("price", trade.get("current_price", trade.get("entry", 0))),
            0.0,
        )
        atr = _safe_float(trade.get("atr", 0), 0.0)
        trend = _safe_str(trade.get("trend", "UPTREND"), "UPTREND").upper()
        rsi = _safe_float(trade.get("rsi", 55), 55.0)
        option_chain = _safe_list(trade.get("option_chain", []))

        trade["symbol"] = symbol
        trade["strategy"] = strategy
        trade["price"] = price
        trade["atr"] = atr
        trade["trend"] = trend
        trade["rsi"] = rsi
        trade["regime"] = regime
        trade["mode"] = mode
        trade["trading_mode"] = resolved_trading_mode
        trade["trading_mode_label"] = resolved_trading_mode_context.get("mode_label", resolved_trading_mode)
        trade["volatility_state"] = volatility_state
        trade["breadth"] = breadth
        trade["option_chain"] = option_chain

        print("OPTION PATH PRECHECK:", {
            "symbol": symbol,
            "strategy": strategy,
            "price": price,
            "option_chain_count": len(option_chain),
            "has_option_chain": bool(option_chain),
        })

        best_option = None
        option_score = -1
        option_notes = []

        try:
            best_option, option_score, option_notes = choose_best_option(
                option_chain,
                price,
                strategy,
                trade=trade,
            )
        except Exception:
            best_option, option_score, option_notes = None, -1, []

        print("OPTION PATH CHOICE:", {
            "symbol": symbol,
            "best_option_found": bool(best_option),
            "option_score": option_score,
            "option_notes": option_notes,
            "best_option_preview": best_option if isinstance(best_option, dict) else None,
        })

        if isinstance(best_option, dict) and best_option:
            try:
                option_allowed, option_reason = option_is_executable(
                    best_option,
                    min_score=60,
                )
            except Exception:
                option_allowed, option_reason = False, "option_validation_failed"
            best_option["is_executable"] = bool(option_allowed)
            best_option["execution_reason"] = _safe_str(option_reason, "")
        else:
            option_allowed, option_reason = False, "no_option_contract"

        v2_row = _get_v2_overlay(symbol, trade)

        fused = build_fused_candidate(
            trade,
            best_option=best_option,
            option_score=option_score,
            option_notes=option_notes,
            v2_row=v2_row,
            governor=governor,
            buying_power=capital_available_now,
            commission=1.0,
        )

        fused["trading_mode"] = resolved_trading_mode
        fused["trading_mode_label"] = resolved_trading_mode_context.get("mode_label", resolved_trading_mode)

        print("OPTION VS STOCK CAPITAL:", {
            "symbol": symbol,
            "vehicle_selected": fused.get("vehicle_selected"),
            "has_option": bool(fused.get("option")),
            "capital_required": fused.get("capital_required"),
            "minimum_trade_cost": fused.get("minimum_trade_cost"),
            "price": fused.get("price"),
            "shares": fused.get("size", fused.get("shares", 1)),
            "contracts": fused.get("contracts", 1),
        })

        debug_row = {
            "symbol": symbol,
            "starting_strategy": strategy,
            "final_strategy": fused.get("strategy", strategy),
            "score": fused.get("fused_score", score),
            "confidence": fused.get("confidence", confidence),
            "breadth": breadth,
            "mode": mode,
            "trading_mode": resolved_trading_mode,
            "volatility_state": volatility_state,
            "governor_blocked": bool(governor.get("blocked", False)),
            "governor_reason": governor_reason,
            "breadth_allowed": None,
            "chosen_strategy": None,
            "duplicate_open_found": None,
            "duplicate_trade_id": "",
            "reentry_allowed": None,
            "reentry_reason": "",
            "execution_guard_blocked": None,
            "execution_guard_reason": "",
            "score_allowed": None,
            "volatility_allowed": None,
            "option_chain_count": len(option_chain),
            "best_option_found": bool(best_option),
            "option_contract_score": option_score,
            "option_allowed": option_allowed if best_option else None,
            "option_reason": option_reason if best_option else "",
            "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
            "capital_affordable": bool(fused.get("stock_affordable") or fused.get("option_affordable")),
            "research_approved": False,
            "execution_ready": False,
            "selected_for_execution": False,
            "blocked_at": "",
            "final_reason": "",
            "capital_required": fused.get("capital_required", 0.0),
            "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
            "capital_available": capital_available_now,
        }

        chosen_strategy = choose_trade_strategy(
            symbol=symbol,
            score=score,
            rsi=rsi,
            market_regime=regime,
            market_breadth=breadth,
            volatility_state=volatility_state,
            mode=resolved_trading_mode,
            starting_strategy=strategy,
        )
        debug_row["chosen_strategy"] = chosen_strategy

        if chosen_strategy:
            fused["strategy"] = _safe_str(
                chosen_strategy,
                fused.get("strategy", strategy),
            ).upper()
            debug_row["final_strategy"] = fused["strategy"]

        breadth_ok = breadth_allows_trade(fused["strategy"], breadth)
        debug_row["breadth_allowed"] = breadth_ok

        if not breadth_ok:
            reason = "failed_breadth_filter"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "breadth_guard", reason)
            debug_rows.append(debug_row)
            log_rejection(
                fused,
                symbol,
                "breadth_blocked",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            _remember_candidate_row(
                fused,
                status="rejected",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        if fused["strategy"] == "NO_TRADE":
            reason = "strategy_router_returned_no_trade"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "strategy_router", reason)
            debug_rows.append(debug_row)
            log_rejection(
                fused,
                symbol,
                "strategy_router_blocked",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            _remember_candidate_row(
                fused,
                status="rejected",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        existing_position = None
        try:
            existing_position = get_position(symbol)
        except Exception:
            existing_position = None

        debug_row["duplicate_open_found"] = bool(existing_position)
        debug_row["duplicate_trade_id"] = (
            _safe_str(existing_position.get("trade_id", ""), "")
            if isinstance(existing_position, dict) else ""
        )

        print("DUP CHECK:", symbol, bool(existing_position))

        if existing_position:
            reason = "already_open_position"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "duplicate_guard", reason)
            debug_rows.append(debug_row)
            log_rejection(
                fused,
                symbol,
                "position_duplication_blocked",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            _remember_candidate_row(
                fused,
                status="rejected",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "existing_trade_id": debug_row["duplicate_trade_id"],
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        allowed_reentry, reentry_reason = reentry_allowed(fused)
        debug_row["reentry_allowed"] = allowed_reentry
        debug_row["reentry_reason"] = reentry_reason

        if not allowed_reentry:
            reason = f"reentry_blocked:{reentry_reason}"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "reentry_guard", reason)
            debug_rows.append(debug_row)
            log_rejection(
                fused,
                symbol,
                "reentry_blocked",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            _remember_candidate_row(
                fused,
                status="rejected",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        score_ok = _safe_float(
            fused.get("fused_score", fused.get("score", 0.0)),
            0.0,
        ) >= 90
        debug_row["score_allowed"] = score_ok

        if not score_ok:
            reason = "failed_score_threshold"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "score_threshold", reason)
            debug_rows.append(debug_row)
            log_rejection(
                fused,
                symbol,
                "score_too_low",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            _remember_candidate_row(
                fused,
                status="rejected",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        volatility_ok = not (
            volatility_state == "ELEVATED"
            and fused.get("confidence", "LOW") == "LOW"
        )
        debug_row["volatility_allowed"] = volatility_ok

        if not volatility_ok:
            reason = "failed_volatility_filter"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "volatility_guard", reason)
            debug_rows.append(debug_row)
            log_rejection(
                fused,
                symbol,
                "volatility_blocked",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            _remember_candidate_row(
                fused,
                status="rejected",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        if fused.get("option"):
            debug_row["option_allowed"] = option_allowed
            debug_row["option_reason"] = option_reason
            if not option_allowed and fused.get("vehicle_selected") == "OPTION":
                reason = _safe_str(option_reason, "weak_option_contract")
                fused, debug_row = _finalize_for_exit(fused, debug_row, "option_executable", reason)
                debug_rows.append(debug_row)
                log_rejection(
                    fused,
                    symbol,
                    "weak_option_contract",
                    reason,
                    mode,
                    breadth,
                    volatility_state,
                )
                _remember_candidate_row(
                    fused,
                    status="rejected",
                    reason=reason,
                    mode=mode,
                    trading_mode_value=resolved_trading_mode,
                    breadth=breadth,
                    volatility_state=volatility_state,
                    capital_required=fused.get("capital_required", 0.0),
                    capital_available=capital_available_now,
                    extra={
                        "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                        "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                        "blocked_at": fused.get("blocked_at", ""),
                        "final_reason": fused.get("final_reason", reason),
                    },
                )
                continue

        fused["research_approved"] = True
        fused["execution_ready"] = False
        fused["selected_for_execution"] = False
        debug_row["research_approved"] = True

        if governor_reason:
            fused, debug_row = _finalize_for_exit(fused, debug_row, "governor", governor_reason)
            research_approved.append(fused)
            debug_rows.append(debug_row)
            _remember_candidate_row(
                fused,
                status="research_approved_not_execution_ready",
                reason=governor_reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "research_approved": bool(fused.get("research_approved", False)),
                    "execution_ready": bool(fused.get("execution_ready", False)),
                    "governor": governor,
                    "governor_blocked": bool(governor.get("blocked", False)),
                    "governor_reason": governor_reason,
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", governor_reason),
                },
            )
            continue

        exec_guard = can_execute_trade(fused, capital_available_now)
        exec_guard = apply_mode_to_execution_guard(exec_guard, resolved_trading_mode)

        if isinstance(exec_guard, dict):
            blocked = bool(exec_guard.get("blocked", False))
            exec_reason = _safe_str(exec_guard.get("reason", ""), "")
        else:
            blocked = True
            exec_reason = "invalid_execution_guard_response"

        debug_row["execution_guard_blocked"] = blocked
        debug_row["execution_guard_reason"] = exec_reason

        if blocked:
            reason = exec_reason or "execution_guard_blocked"
            fused, debug_row = _finalize_for_exit(fused, debug_row, "execution_guard", reason)
            research_approved.append(fused)
            debug_rows.append(debug_row)
            _remember_candidate_row(
                fused,
                status="research_approved_not_execution_ready",
                reason=reason,
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=fused.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                    "research_approved": bool(fused.get("research_approved", False)),
                    "execution_ready": bool(fused.get("execution_ready", False)),
                    "blocked_at": fused.get("blocked_at", ""),
                    "final_reason": fused.get("final_reason", reason),
                },
            )
            continue

        fused["blocked_at"] = ""
        fused["final_reason"] = "execution_ready"
        fused["research_approved"] = True
        fused["execution_ready"] = True
        fused["selected_for_execution"] = False
        fused = finalize_candidate_state(fused)

        debug_row = _sync_debug_from_fused(debug_row, fused)
        debug_row["final_reason"] = "execution_ready"

        debug_rows.append(debug_row)
        research_approved.append(fused)
        execution_ready.append(fused)

        log_approval(fused, mode, regime, breadth, volatility_state)

        _remember_candidate_row(
            fused,
            status="execution_ready",
            reason="execution_ready",
            mode=mode,
            trading_mode_value=resolved_trading_mode,
            breadth=breadth,
            volatility_state=volatility_state,
            capital_required=fused.get("capital_required", 0.0),
            capital_available=capital_available_now,
            extra={
                "minimum_trade_cost": fused.get("minimum_trade_cost", 0.0),
                "vehicle_selected": fused.get("vehicle_selected", "RESEARCH_ONLY"),
                "research_approved": True,
                "execution_ready": True,
                "blocked_at": fused.get("blocked_at", ""),
                "final_reason": fused.get("final_reason", "execution_ready"),
            },
        )

    print("\nAPPROVAL DEBUG")
    for row in debug_rows:
        print(row)

    if research_approved:
        print_leaderboard(research_approved)
        print_top_candidates(research_approved, limit=5)
        save_top_candidates(research_approved, limit=10)
    else:
        print("No approved trades.")
        print("TOP CANDIDATES None")

    affordable = affordable_trade_count(execution_ready)
    selection_limit = min(affordable, 3) if affordable > 0 else 0
    selected_trades = []

    if execution_ready and selection_limit > 0:
        selected_trades = queue_top_trades_plus(execution_ready, limit=selection_limit)

    selected_keys = {
        (
            _norm_symbol(t.get("symbol", "")),
            _safe_str(t.get("strategy", "CALL"), "CALL").upper(),
        )
        for t in selected_trades
        if isinstance(t, dict)
    }

    print("RESEARCH APPROVED CANDIDATE INTELLIGENCE")
    if not research_approved:
        print("None")
    else:
        for trade in research_approved:
            print(
                f"{trade.get('symbol', 'UNKNOWN')} | "
                f"{trade.get('strategy', 'CALL')} | "
                f"{trade.get('fused_score', trade.get('score', 0))} | "
                f"{trade.get('confidence', 'LOW')} | "
                f"{trade.get('vehicle_selected', 'RESEARCH_ONLY')}"
            )

    print("EXECUTION READY CANDIDATE INTELLIGENCE")
    if not execution_ready:
        print("None")
    else:
        for trade in execution_ready:
            print(
                f"{trade.get('symbol', 'UNKNOWN')} | "
                f"{trade.get('strategy', 'CALL')} | "
                f"{trade.get('fused_score', trade.get('score', 0))} | "
                f"{trade.get('confidence', 'LOW')} | "
                f"{trade.get('vehicle_selected', 'RESEARCH_ONLY')}"
            )

    for trade in research_approved:
        key = (
            _norm_symbol(trade.get("symbol", "")),
            _safe_str(trade.get("strategy", "CALL"), "CALL").upper(),
        )
        if key in selected_keys:
            trade["selected_for_execution"] = True
            trade["final_reason"] = "selected_for_execution"
            trade["blocked_at"] = ""
            trade = finalize_candidate_state(trade)
            log_candidate_decision(
                trade,
                status="selected",
                reason="selected_for_execution",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            _remember_candidate_row(
                trade,
                status="selected",
                reason="selected_for_execution",
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=trade.get("capital_required", 0.0),
                capital_available=capital_available_now,
                selected_for_execution=True,
                extra={
                    "minimum_trade_cost": trade.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": trade.get("vehicle_selected", "RESEARCH_ONLY"),
                    "research_approved": bool(trade.get("research_approved", False)),
                    "execution_ready": bool(trade.get("execution_ready", False)),
                    "selected_for_execution": True,
                    "blocked_at": trade.get("blocked_at", ""),
                    "final_reason": trade.get("final_reason", "selected_for_execution"),
                },
            )
        elif trade.get("execution_ready"):
            stronger = stronger_competing_setups(trade, selected_trades)
            trade["stronger_competing_setups"] = stronger
            trade["rejection_reason"] = explain_rejection(trade, "not_selected")
            trade["rejection_analysis"] = build_rejection_analysis(
                trade,
                "not_selected",
                "approved_but_ranked_below_execution_cut",
            )
            trade["final_reason"] = "approved_but_ranked_below_execution_cut"
            trade["blocked_at"] = ""
            trade = finalize_candidate_state(trade)
            log_candidate_decision(
                trade,
                status="execution_ready_not_selected",
                reason="approved_but_ranked_below_execution_cut",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
                extra={
                    "stronger_competing_setups": trade.get("stronger_competing_setups", []),
                    "rejection_analysis": trade.get("rejection_analysis", []),
                },
            )
            _remember_candidate_row(
                trade,
                status="execution_ready_not_selected",
                reason="approved_but_ranked_below_execution_cut",
                mode=mode,
                trading_mode_value=resolved_trading_mode,
                breadth=breadth,
                volatility_state=volatility_state,
                capital_required=trade.get("capital_required", 0.0),
                capital_available=capital_available_now,
                extra={
                    "stronger_competing_setups": trade.get("stronger_competing_setups", []),
                    "rejection_analysis": trade.get("rejection_analysis", []),
                    "minimum_trade_cost": trade.get("minimum_trade_cost", 0.0),
                    "vehicle_selected": trade.get("vehicle_selected", "RESEARCH_ONLY"),
                    "research_approved": True,
                    "execution_ready": True,
                    "selected_for_execution": False,
                    "blocked_at": trade.get("blocked_at", ""),
                    "final_reason": trade.get("final_reason", "approved_but_ranked_below_execution_cut"),
                },
            )

    return research_approved, selected_trades, mode, breadth, volatility_state


def run(trading_mode="paper"):
    from engine.observatory_mode import normalize_mode, build_mode_context

    trading_mode = normalize_mode(trading_mode)
    mode_context = build_mode_context(trading_mode)

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
        volatility_state = volatility_payload.get("volatility", "UNKNOWN")
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
                trade_id=trade_id,
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
                    "trading_mode": resolved_trading_mode,
                },
            )

            append_trade_detail_timeline(
                trade_id,
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
            cash_available = round(_safe_float(buying_power(), 0.0), 2)

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
                    account_context={"cash_available": cash_available},
                    mode=resolved_trading_mode,
                    allow_stock_fallback=True,
                )

                print("POST-LIFECYCLE:", {
                    "symbol": lifecycle.get("symbol"),
                    "research_approved": lifecycle.get("research_approved"),
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
                    "final_reason": lifecycle.get("final_reason"),
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

            packet = execute_trades(execution_queue, limit=trades_remaining)
            executed_results = packet.get("results", []) if isinstance(packet, dict) else []

            for result in executed_results:
                if not isinstance(result, dict) or not result.get("success"):
                    continue

                lifecycle_after = result.get("lifecycle_after", {}) or {}
                symbol = lifecycle_after.get("symbol", "UNKNOWN")
                trade_id = lifecycle_after.get("raw", {}).get("trade_id")

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
