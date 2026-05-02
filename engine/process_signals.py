from __future__ import annotations

from typing import Any, Dict, List, Tuple

from engine.execution_selector import choose_execution_queue_option_b
from engine.options_intelligence import choose_best_option, option_is_executable
from engine.canonical_candidate import build_canonical_candidate
from engine.candidate_log import remember_candidate
from engine.explainability_engine import (
    explain_rejection,
    build_rejection_analysis,
    explain_reentry_detail,
)
from engine.premium_feed import write_premium_feed_item
from engine.paper_portfolio import open_count, get_position
from engine.account_state import buying_power
from engine.capital_guard import affordable_trade_count
from engine.market_breadth import market_breadth
from engine.market_mode import market_mode
from engine.breadth_filter import breadth_allows_trade
from engine.strategy_router import choose_trade_strategy
from engine.reentry_guard import reentry_allowed
from engine.observatory_mode import normalize_mode, build_mode_context
from engine.top_candidates_store import save_top_candidates
from engine.top_candidates_view import print_top_candidates
from engine.leaderboard import print_leaderboard

try:
    from engine.canonical_execution_guard import validate_selected_trade_for_execution
except Exception:
    def validate_selected_trade_for_execution(
        trade,
        capital_available=0.0,
        trading_mode="paper",
        current_open_positions=0,
        max_open_positions=5,
        kill_switch_enabled=False,
        session_healthy=True,
        broker_healthy=True,
    ):
        trade = trade if isinstance(trade, dict) else {}
        vehicle_selected = str(trade.get("vehicle_selected", "RESEARCH_ONLY") or "RESEARCH_ONLY").upper()
        minimum_trade_cost = float(trade.get("minimum_trade_cost", 0.0) or 0.0)

        if kill_switch_enabled:
            return {
                "blocked": True,
                "reason": "Kill switch is enabled.",
                "reason_code": "kill_switch_enabled",
                "warnings": [],
                "details": {},
            }
        if not session_healthy:
            return {
                "blocked": True,
                "reason": "Session unhealthy.",
                "reason_code": "session_unhealthy",
                "warnings": [],
                "details": {},
            }
        if not broker_healthy:
            return {
                "blocked": True,
                "reason": "Broker unhealthy.",
                "reason_code": "broker_unhealthy",
                "warnings": [],
                "details": {},
            }
        if current_open_positions >= max_open_positions:
            return {
                "blocked": True,
                "reason": "Max open positions reached.",
                "reason_code": "max_open_positions_reached",
                "warnings": [],
                "details": {
                    "current_open_positions": current_open_positions,
                    "max_open_positions": max_open_positions,
                },
            }
        if vehicle_selected == "RESEARCH_ONLY":
            return {
                "blocked": True,
                "reason": "Research-only candidate cannot execute.",
                "reason_code": "research_only_candidate",
                "warnings": [],
                "details": {},
            }
        if minimum_trade_cost > 0 and float(capital_available or 0.0) < minimum_trade_cost:
            return {
                "blocked": True,
                "reason": "Insufficient capital.",
                "reason_code": "insufficient_capital",
                "warnings": [],
                "details": {
                    "capital_available": float(capital_available or 0.0),
                    "minimum_trade_cost": minimum_trade_cost,
                },
            }
        return {
            "blocked": False,
            "reason": "ok",
            "reason_code": "ok",
            "warnings": [],
            "details": {},
        }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def resolve_market_mode(regime: str, breadth: str, volatility_payload: Dict[str, Any] | None = None) -> str:
    return market_mode(regime, breadth)


def _normalize_why_lines(value: Any) -> List[str]:
    lines: List[str] = []
    if isinstance(value, list):
        lines = [str(x).strip() for x in value if str(x).strip()]
    elif isinstance(value, dict):
        for v in value.values():
            text = str(v).strip()
            if text:
                lines.append(text)
    elif isinstance(value, str):
        text = value.strip()
        if text:
            lines = [text]
    return lines


def stronger_competing_setups(trade: Dict[str, Any], selected_trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    current_score = _safe_float(trade.get("fused_score", trade.get("score", 0)), 0.0)

    stronger: List[Dict[str, Any]] = []
    for other in selected_trades:
        other_symbol = other.get("symbol")
        other_strategy = other.get("strategy")
        other_score = _safe_float(other.get("fused_score", other.get("score", 0)), 0.0)

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


def log_candidate_decision(
    trade: Dict[str, Any],
    status: str,
    reason: str,
    mode: str | None = None,
    breadth: str | None = None,
    volatility_state: str | None = None,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    payload = build_canonical_candidate(
        trade,
        status=status,
        reason=reason,
        mode=mode or trade.get("mode", ""),
        breadth=breadth or trade.get("breadth", ""),
        volatility_state=volatility_state or trade.get("volatility_state", ""),
        decision_reason=reason,
        selected_for_execution=bool(trade.get("selected_for_execution", False)),
        capital_required=_safe_float(trade.get("capital_required", 0.0), 0.0),
        capital_available=_safe_float(trade.get("capital_available", 0.0), 0.0),
        stronger_competing_setups=_safe_list(trade.get("stronger_competing_setups", [])),
    )
    if extra:
        payload.update(extra)
    remember_candidate(payload)
    trade["candidate_display"] = payload
    return payload


def log_rejection(
    trade: Dict[str, Any],
    symbol: str,
    reason_key: str,
    machine_reason: str,
    mode: str,
    breadth: str,
    volatility_state: str,
) -> None:
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
        "trading_mode": trade.get("trading_mode"),
    })

    log_candidate_decision(
        trade,
        status="rejected",
        reason=machine_reason,
        mode=mode,
        breadth=breadth,
        volatility_state=volatility_state,
    )


def log_approval(
    trade: Dict[str, Any],
    mode: str,
    regime: str,
    breadth: str,
    volatility_state: str,
) -> None:
    symbol = _norm_symbol(trade.get("symbol", "UNKNOWN"))
    why_lines = _normalize_why_lines(trade.get("why", []))
    option_lines = _normalize_why_lines(trade.get("option_explanation", []))

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
        "score": trade.get("fused_score", trade.get("score", 0)),
        "confidence": trade.get("confidence", "LOW"),
        "trading_mode": trade.get("trading_mode"),
    })


def _get_v2_overlay(symbol: str, trade: Dict[str, Any]) -> Dict[str, Any]:
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


def _governor_snapshot(trading_mode: str | None = None) -> Dict[str, Any]:
    from engine.performance_tracker import performance_summary
    from engine.risk_governor import governor_status

    try:
        requested_mode = normalize_mode(trading_mode or "paper")
        entries_today_value = 0

        try:
            perf = performance_summary()
            if isinstance(perf, dict):
                entries_today_value = int(_safe_float(perf.get("entries_today", 0), 0))
        except Exception:
            entries_today_value = 0

        print("GOVERNOR ENTRY FEED:", {
            "entries_today_from_perf": entries_today_value,
            "open_positions": open_count(),
            "requested_trading_mode": requested_mode,
        })

        gov = governor_status(
            current_open_positions=open_count(),
            executed_entries_today=entries_today_value,
            trading_mode=requested_mode,
        )

        print("PROCESS SIGNALS GOVERNOR MODE CHECK:", {
            "requested_trading_mode": requested_mode,
            "governor_returned_mode": gov.get("trading_mode") if isinstance(gov, dict) else None,
        })

        return gov if isinstance(gov, dict) else {}
    except Exception:
        return {}


def _governor_execution_block_reason(governor: Dict[str, Any]) -> str:
    if not isinstance(governor, dict):
        return ""
    if not bool(governor.get("blocked", False)):
        return ""
    reasons = _safe_list(governor.get("reasons", []))
    if reasons:
        return f"governor_blocked:{reasons[0]}"
    return "governor_blocked"


def process_signals(
    results: List[Dict[str, Any]],
    regime: str,
    volatility_payload: Dict[str, Any] | None,
    trading_mode: str = "paper",
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str, str, str]:
    from engine.candidate_fusion import build_fused_candidate, finalize_candidate_state

    trading_mode = normalize_mode(trading_mode)

    results = _safe_list(results)
    research_approved: List[Dict[str, Any]] = []
    execution_ready: List[Dict[str, Any]] = []
    debug_rows: List[Dict[str, Any]] = []

    breadth = market_breadth(results)
    print("Market Breadth:", breadth)

    mode = resolve_market_mode(regime, breadth, volatility_payload or {})
    print("Market Mode:", mode)

    volatility_state = _safe_str(
        (volatility_payload or {}).get("state", (volatility_payload or {}).get("volatility", "NORMAL")),
        "NORMAL",
    )
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
        confidence_value = _safe_str(trade.get("confidence", "LOW"), "LOW").upper()
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
        trade["mode_context"] = resolved_trading_mode_context
        trade["volatility_state"] = volatility_state
        trade["breadth"] = breadth
        trade["option_chain"] = option_chain
        trade["capital_available"] = capital_available_now
        trade["governor"] = governor
        trade["governor_blocked"] = bool(governor.get("blocked", False))
        trade["governor_reason"] = governor_reason

        print("OPTION PATH PRECHECK:", {
            "symbol": symbol,
            "strategy": strategy,
            "price": price,
            "option_chain_count": len(option_chain),
            "has_option_chain": bool(option_chain),
        })

        best_option = None
        option_score = -1
        option_notes: List[str] = []

        try:
            best_option, option_score, option_notes = choose_best_option(
                option_chain,
                price,
                strategy,
                trade=trade,
            )
        except Exception:
            best_option, option_score, option_notes = None, -1, []

        if isinstance(best_option, dict) and best_option:
            try:
                option_allowed, option_reason = option_is_executable(best_option, min_score=60)
            except Exception:
                option_allowed, option_reason = False, "option_validation_failed"

            best_option["is_executable"] = bool(option_allowed)
            best_option["execution_reason"] = _safe_str(option_reason, "")
        else:
            option_allowed, option_reason = False, "no_option_contract"

        print("OPTION PATH CHOICE:", {
            "symbol": symbol,
            "best_option_found": bool(best_option),
            "option_score": option_score,
            "option_notes": option_notes,
            "best_option_preview": best_option if isinstance(best_option, dict) else None,
        })

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
        fused["mode_context"] = resolved_trading_mode_context
        fused["capital_available"] = capital_available_now
        fused["option_allowed"] = option_allowed
        fused["option_reason"] = option_reason
        fused["best_option_found"] = bool(best_option)

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
            "confidence": fused.get("confidence", confidence_value),
            "breadth": breadth,
            "mode": mode,
            "trading_mode": resolved_trading_mode,
            "volatility_state": volatility_state,
            "governor_blocked": bool(governor.get("blocked", False)),
            "governor_reason": governor_reason,
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
            fused["strategy"] = _safe_str(chosen_strategy, fused.get("strategy", strategy)).upper()
            debug_row["final_strategy"] = fused["strategy"]

        breadth_ok = breadth_allows_trade(fused["strategy"], breadth)
        debug_row["breadth_allowed"] = breadth_ok
        if not breadth_ok:
            fused["blocked_at"] = "breadth_guard"
            fused["final_reason"] = "failed_breadth_filter"
            fused["final_reason_code"] = "failed_breadth_filter"
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "breadth_blocked", "failed_breadth_filter", mode, breadth, volatility_state)
            continue

        if fused["strategy"] == "NO_TRADE":
            fused["blocked_at"] = "strategy_router"
            fused["final_reason"] = "strategy_router_returned_no_trade"
            fused["final_reason_code"] = "strategy_router_returned_no_trade"
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "strategy_router_blocked", "strategy_router_returned_no_trade", mode, breadth, volatility_state)
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

        if existing_position:
            fused["blocked_at"] = "duplicate_guard"
            fused["final_reason"] = "already_open_position"
            fused["final_reason_code"] = "already_open_position"
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "position_duplication_blocked", "already_open_position", mode, breadth, volatility_state)
            continue

        allowed_reentry, reentry_reason = reentry_allowed(fused)
        debug_row["reentry_allowed"] = allowed_reentry
        debug_row["reentry_reason"] = reentry_reason

        if not allowed_reentry:
            reason = f"reentry_blocked:{reentry_reason}"
            fused["blocked_at"] = "reentry_guard"
            fused["final_reason"] = reason
            fused["final_reason_code"] = reason
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "reentry_blocked", reason, mode, breadth, volatility_state)
            continue

        score_ok = _safe_float(fused.get("fused_score", fused.get("score", 0.0)), 0.0) >= 90
        debug_row["score_allowed"] = score_ok
        if not score_ok:
            fused["blocked_at"] = "score_threshold"
            fused["final_reason"] = "failed_score_threshold"
            fused["final_reason_code"] = "failed_score_threshold"
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "score_too_low", "failed_score_threshold", mode, breadth, volatility_state)
            continue

        volatility_ok = not (
            volatility_state == "ELEVATED"
            and fused.get("confidence", "LOW") == "LOW"
        )
        debug_row["volatility_allowed"] = volatility_ok
        if not volatility_ok:
            fused["blocked_at"] = "volatility_guard"
            fused["final_reason"] = "failed_volatility_filter"
            fused["final_reason_code"] = "failed_volatility_filter"
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "volatility_blocked", "failed_volatility_filter", mode, breadth, volatility_state)
            continue

        if fused.get("option") and fused.get("vehicle_selected") == "OPTION" and not option_allowed:
            reason = _safe_str(option_reason, "weak_option_contract")
            fused["blocked_at"] = "option_executable"
            fused["final_reason"] = reason
            fused["final_reason_code"] = reason
            fused = finalize_candidate_state(fused)
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_rejection(fused, symbol, "weak_option_contract", reason, mode, breadth, volatility_state)
            continue

        fused["research_approved"] = True
        fused["execution_ready"] = False
        fused["selected_for_execution"] = False

        guard = validate_selected_trade_for_execution(
            fused,
            capital_available=capital_available_now,
            trading_mode=resolved_trading_mode,
            current_open_positions=open_count(),
            max_open_positions=5,
            kill_switch_enabled=False,
            session_healthy=True,
            broker_healthy=True,
        )

        blocked = bool(_safe_dict(guard).get("blocked", False))
        exec_reason = _safe_str(_safe_dict(guard).get("reason_code", ""), "") or _safe_str(_safe_dict(guard).get("reason", ""), "")

        if governor_reason:
            blocked = True
            exec_reason = governor_reason

        debug_row["execution_guard_blocked"] = blocked
        debug_row["execution_guard_reason"] = exec_reason

        if blocked:
            fused["blocked_at"] = "execution_guard"
            fused["final_reason"] = exec_reason or "execution_guard_blocked"
            fused["final_reason_code"] = exec_reason or "execution_guard_blocked"
            fused = finalize_candidate_state(fused)
            research_approved.append(fused)
            debug_row["research_approved"] = True
            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)
            log_candidate_decision(
                fused,
                status="research_approved_not_execution_ready",
                reason=fused["final_reason"],
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )
            continue

        fused["blocked_at"] = ""
        fused["final_reason"] = "execution_ready"
        fused["final_reason_code"] = "execution_ready"
        fused["research_approved"] = True
        fused["execution_ready"] = True
        fused["selected_for_execution"] = False
        fused = finalize_candidate_state(fused)

        debug_row["research_approved"] = True
        debug_row["execution_ready"] = True
        debug_row["final_reason"] = "execution_ready"
        debug_rows.append(debug_row)

        research_approved.append(fused)
        execution_ready.append(fused)

        log_approval(fused, mode, regime, breadth, volatility_state)
        log_candidate_decision(
            fused,
            status="execution_ready",
            reason="execution_ready",
            mode=mode,
            breadth=breadth,
            volatility_state=volatility_state,
        )

    affordable = affordable_trade_count(execution_ready)
    selection_limit = min(affordable, 3) if affordable > 0 else 0

    selected_trades: List[Dict[str, Any]] = []
    if execution_ready and selection_limit > 0:
        selected_trades = choose_execution_queue_option_b(
            execution_ready,
            limit=selection_limit,
            available_cash=capital_available_now,
            trading_mode=resolved_trading_mode,
            mode_context=resolved_trading_mode_context,
        )

    selected_keys = {
        (
            _norm_symbol(t.get("symbol", "")),
            _safe_str(t.get("strategy", "CALL"), "CALL").upper(),
        )
        for t in selected_trades
        if isinstance(t, dict)
    }

    finalized_research_approved: List[Dict[str, Any]] = []
    finalized_selected_trades: List[Dict[str, Any]] = []

    for trade in research_approved:
        key = (
            _norm_symbol(trade.get("symbol", "")),
            _safe_str(trade.get("strategy", "CALL"), "CALL").upper(),
        )

        if key in selected_keys:
            trade["selected_for_execution"] = True
            trade["execution_ready"] = True
            trade["research_approved"] = True
            trade["final_reason"] = "selected_for_execution"
            trade["final_reason_code"] = "selected_for_execution"
            trade["blocked_at"] = ""
            trade = finalize_candidate_state(trade)

            finalized_research_approved.append(trade)
            finalized_selected_trades.append(trade)

            log_candidate_decision(
                trade,
                status="selected",
                reason="selected_for_execution",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
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
            trade["selected_for_execution"] = False
            trade["final_reason"] = "approved_but_ranked_below_execution_cut"
            trade["final_reason_code"] = "approved_but_ranked_below_execution_cut"
            trade["blocked_at"] = ""
            trade = finalize_candidate_state(trade)

            finalized_research_approved.append(trade)

            log_candidate_decision(
                trade,
                status="execution_ready_not_selected",
                reason="approved_but_ranked_below_execution_cut",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
            )

        else:
            finalized_research_approved.append(trade)

    research_approved = finalized_research_approved
    selected_trades = finalized_selected_trades

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
    execution_ready_now = [t for t in research_approved if bool(t.get("execution_ready", False))]
    if not execution_ready_now:
        print("None")
    else:
        for trade in execution_ready_now:
            print(
                f"{trade.get('symbol', 'UNKNOWN')} | "
                f"{trade.get('strategy', 'CALL')} | "
                f"{trade.get('fused_score', trade.get('score', 0))} | "
                f"{trade.get('confidence', 'LOW')} | "
                f"{trade.get('vehicle_selected', 'RESEARCH_ONLY')}"
            )

    print("SELECTED FOR EXECUTION CANDIDATE INTELLIGENCE")
    if not selected_trades:
        print("None")
    else:
        for trade in selected_trades:
            print(
                f"{trade.get('symbol', 'UNKNOWN')} | "
                f"{trade.get('strategy', 'CALL')} | "
                f"{trade.get('fused_score', trade.get('score', 0))} | "
                f"{trade.get('confidence', 'LOW')} | "
                f"{trade.get('vehicle_selected', 'RESEARCH_ONLY')}"
            )

    return research_approved, selected_trades, mode, breadth, volatility_state


__all__ = [
    "process_signals",
    "resolve_market_mode",
    "stronger_competing_setups",
    "log_candidate_decision",
    "log_rejection",
    "log_approval",
]
