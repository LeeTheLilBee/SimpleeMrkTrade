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

        if vehicle_selected in {"RESEARCH_ONLY", "NONE"}:
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


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


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


def _norm_strategy(value: Any, default: str = "CALL") -> str:
    strategy = _safe_str(value, default).upper()
    return strategy if strategy else default


def _norm_vehicle(value: Any) -> str:
    vehicle = _safe_str(value, "RESEARCH_ONLY").upper()
    if vehicle in {"OPTION", "STOCK", "RESEARCH_ONLY", "NONE"}:
        return vehicle
    return "RESEARCH_ONLY"


def _candidate_score(trade: Dict[str, Any]) -> float:
    return _safe_float(trade.get("fused_score", trade.get("score", 0.0)), 0.0)


def _effective_cost(trade: Dict[str, Any]) -> float:
    minimum_trade_cost = _safe_float(trade.get("minimum_trade_cost"), 0.0)
    capital_required = _safe_float(trade.get("capital_required"), 0.0)
    estimated_cost = _safe_float(trade.get("estimated_cost"), 0.0)

    if minimum_trade_cost > 0:
        return minimum_trade_cost
    if capital_required > 0:
        return capital_required
    if estimated_cost > 0:
        return estimated_cost
    return 0.0


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


# ============================================================
# MODE / GOVERNOR / CAPACITY
# ============================================================

def resolve_market_mode(
    regime: str,
    breadth: str,
    volatility_payload: Dict[str, Any] | None = None,
) -> str:
    return market_mode(regime, breadth)


def _governor_snapshot(trading_mode: str | None = None) -> Dict[str, Any]:
    from engine.performance_tracker import performance_summary
    from engine.risk_governor import governor_status

    try:
        requested_mode = normalize_mode(trading_mode or "paper")
        entries_today_value = 0

        try:
            perf = performance_summary()
            if isinstance(perf, dict):
                entries_today_value = _safe_int(perf.get("entries_today", 0), 0)
        except Exception:
            entries_today_value = 0

        current_open = open_count()

        print("GOVERNOR ENTRY FEED:", {
            "entries_today_from_perf": entries_today_value,
            "open_positions": current_open,
            "requested_trading_mode": requested_mode,
        })

        gov = governor_status(
            current_open_positions=current_open,
            executed_entries_today=entries_today_value,
            trading_mode=requested_mode,
        )

        print("PROCESS SIGNALS GOVERNOR MODE CHECK:", {
            "requested_trading_mode": requested_mode,
            "governor_returned_mode": gov.get("trading_mode") if isinstance(gov, dict) else None,
        })

        return gov if isinstance(gov, dict) else {}

    except Exception as exc:
        print("PROCESS SIGNALS GOVERNOR SNAPSHOT FAILED:", {
            "error": str(exc),
            "fallback": "empty_governor",
        })
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


def _current_open_positions_from_governor(governor: Dict[str, Any]) -> int:
    try:
        if isinstance(governor, dict) and "current_open_positions" in governor:
            return max(0, _safe_int(governor.get("current_open_positions"), open_count()))
    except Exception:
        pass

    try:
        return max(0, open_count())
    except Exception:
        return 0


def _max_open_positions_from_context(mode_context: Dict[str, Any], default: int = 3) -> int:
    return max(0, _safe_int(_safe_dict(mode_context).get("max_open_positions", default), default))


def _queue_limit_from_context(mode_context: Dict[str, Any], default: int = 3) -> int:
    return max(0, _safe_int(_safe_dict(mode_context).get("queue_limit", default), default))


def _build_selection_capacity(
    *,
    execution_ready: List[Dict[str, Any]],
    governor: Dict[str, Any],
    mode_context: Dict[str, Any],
) -> Dict[str, Any]:
    affordable = affordable_trade_count(execution_ready)

    current_open_positions = _current_open_positions_from_governor(governor)
    max_open_positions = _max_open_positions_from_context(mode_context, 3)
    queue_limit = _queue_limit_from_context(mode_context, 3)

    remaining_position_slots = max(0, max_open_positions - current_open_positions)

    if affordable <= 0:
        selection_limit = 0
    else:
        selection_limit = min(
            affordable,
            queue_limit,
            remaining_position_slots,
        )

    capacity = {
        "affordable": affordable,
        "queue_limit": queue_limit,
        "current_open_positions": current_open_positions,
        "max_open_positions": max_open_positions,
        "remaining_position_slots": remaining_position_slots,
        "selection_limit": selection_limit,
    }

    print("PROCESS SIGNALS SELECTION CAPACITY:", capacity)

    return capacity


# ============================================================
# V2 OVERLAY SUPPORT
# ============================================================

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


# ============================================================
# LOGGING / PREMIUM FEED / CANDIDATE MEMORY
# ============================================================

def stronger_competing_setups(
    trade: Dict[str, Any],
    selected_trades: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    current_score = _candidate_score(trade)

    stronger: List[Dict[str, Any]] = []
    for other in selected_trades:
        if not isinstance(other, dict):
            continue

        other_symbol = other.get("symbol")
        other_strategy = other.get("strategy")
        other_score = _candidate_score(other)

        if other_symbol == trade.get("symbol") and other_strategy == trade.get("strategy"):
            continue

        if other_score >= current_score:
            stronger.append({
                "symbol": other_symbol,
                "strategy": other_strategy,
                "score": other_score,
            })

    stronger.sort(key=lambda x: _safe_float(x.get("score"), 0.0), reverse=True)
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
        "symbol": symbol,
        "strategy": trade.get("strategy"),
        "score": trade.get("fused_score", trade.get("score", 0)),
        "vehicle_selected": trade.get("vehicle_selected"),
        "blocked_at": trade.get("blocked_at"),
        "final_reason": trade.get("final_reason"),
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
        "vehicle_selected": trade.get("vehicle_selected"),
        "trading_mode": trade.get("trading_mode"),
    })


# ============================================================
# DEBUG HELPERS
# ============================================================

def _print_candidate_line(trade: Dict[str, Any]) -> None:
    print(
        f"{trade.get('symbol', 'UNKNOWN')} | "
        f"{trade.get('strategy', 'CALL')} | "
        f"{trade.get('fused_score', trade.get('score', 0))} | "
        f"{trade.get('confidence', 'LOW')} | "
        f"{trade.get('vehicle_selected', 'RESEARCH_ONLY')}"
    )


def _build_debug_row(
    *,
    symbol: str,
    strategy: str,
    fused: Dict[str, Any],
    score: float,
    confidence_value: str,
    breadth: str,
    mode: str,
    trading_mode: str,
    volatility_state: str,
    governor: Dict[str, Any],
    governor_reason: str,
    option_chain_count: int,
    best_option: Any,
    option_score: float,
    option_allowed: Any,
    option_reason: str,
    capital_available_now: float,
) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "starting_strategy": strategy,
        "final_strategy": fused.get("strategy", strategy),
        "score": fused.get("fused_score", score),
        "confidence": fused.get("confidence", confidence_value),
        "breadth": breadth,
        "mode": mode,
        "trading_mode": trading_mode,
        "volatility_state": volatility_state,
        "governor_blocked": bool(_safe_dict(governor).get("blocked", False)),
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
        "option_chain_count": option_chain_count,
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
        "effective_cost": _effective_cost(fused),
        "capital_available": capital_available_now,
    }


# ============================================================
# CORE PROCESSOR
# ============================================================

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
        (volatility_payload or {}).get(
            "state",
            (volatility_payload or {}).get("volatility", "NORMAL"),
        ),
        "NORMAL",
    ).upper()

    vix_value = (volatility_payload or {}).get("vix", "N/A")
    print("Volatility State:", volatility_state, "| VIX:", vix_value)

    capital_available_now = round(_safe_float(buying_power(), 0.0), 2)

    governor = _governor_snapshot(trading_mode=trading_mode)
    resolved_trading_mode = normalize_mode(
        governor.get("trading_mode") if isinstance(governor, dict) else trading_mode
    )
    resolved_trading_mode_context = build_mode_context(resolved_trading_mode)
    governor_reason = _governor_execution_block_reason(governor)

    current_open_positions_for_guard = _current_open_positions_from_governor(governor)
    max_open_positions_for_guard = _max_open_positions_from_context(
        resolved_trading_mode_context,
        3,
    )

    print("PROCESS SIGNALS POSITION CONTEXT:", {
        "resolved_trading_mode": resolved_trading_mode,
        "current_open_positions": current_open_positions_for_guard,
        "max_open_positions": max_open_positions_for_guard,
        "remaining_position_slots": max(
            0,
            max_open_positions_for_guard - current_open_positions_for_guard,
        ),
        "capital_available_now": capital_available_now,
    })

    for raw_trade in results:
        trade = dict(raw_trade) if isinstance(raw_trade, dict) else {}

        symbol = _norm_symbol(trade.get("symbol", "UNKNOWN"))
        strategy = _norm_strategy(trade.get("strategy", "CALL"), "CALL")
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
        trade["trading_mode_label"] = resolved_trading_mode_context.get(
            "mode_label",
            resolved_trading_mode,
        )
        trade["mode_context"] = resolved_trading_mode_context
        trade["volatility_state"] = volatility_state
        trade["breadth"] = breadth
        trade["option_chain"] = option_chain
        trade["capital_available"] = capital_available_now
        trade["governor"] = governor
        trade["governor_blocked"] = bool(_safe_dict(governor).get("blocked", False))
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
        except Exception as exc:
            print("OPTION PATH CHOICE FAILED:", {
                "symbol": symbol,
                "error": str(exc),
            })
            best_option, option_score, option_notes = None, -1, []

        if isinstance(best_option, dict) and best_option:
            try:
                option_allowed, option_reason = option_is_executable(best_option, min_score=60)
            except Exception:
                option_allowed, option_reason = False, "option_validation_failed"

            best_option["is_executable"] = bool(option_allowed)
            best_option["execution_reason"] = _safe_str(option_reason, "")
            best_option.setdefault("monitoring_mode", "OPTION_PREMIUM")
            best_option.setdefault(
                "price_reference",
                best_option.get("mark", best_option.get("selected_price_reference")),
            )
            best_option.setdefault(
                "selected_price_reference",
                best_option.get("price_reference", best_option.get("mark")),
            )
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

        fused["symbol"] = symbol
        fused["trading_mode"] = resolved_trading_mode
        fused["trading_mode_label"] = resolved_trading_mode_context.get(
            "mode_label",
            resolved_trading_mode,
        )
        fused["mode_context"] = resolved_trading_mode_context
        fused["capital_available"] = capital_available_now
        fused["option_allowed"] = option_allowed
        fused["option_reason"] = option_reason
        fused["best_option_found"] = bool(best_option)
        fused["governor"] = governor
        fused["governor_blocked"] = bool(_safe_dict(governor).get("blocked", False))
        fused["governor_reason"] = governor_reason
        fused["current_open_positions_seen"] = current_open_positions_for_guard
        fused["max_open_positions_seen"] = max_open_positions_for_guard

        print("OPTION VS STOCK CAPITAL:", {
            "symbol": symbol,
            "vehicle_selected": fused.get("vehicle_selected"),
            "has_option": bool(fused.get("option")),
            "capital_required": fused.get("capital_required"),
            "minimum_trade_cost": fused.get("minimum_trade_cost"),
            "effective_cost": _effective_cost(fused),
            "price": fused.get("price"),
            "shares": fused.get("size", fused.get("shares", 1)),
            "contracts": fused.get("contracts", 1),
        })

        debug_row = _build_debug_row(
            symbol=symbol,
            strategy=strategy,
            fused=fused,
            score=score,
            confidence_value=confidence_value,
            breadth=breadth,
            mode=mode,
            trading_mode=resolved_trading_mode,
            volatility_state=volatility_state,
            governor=governor,
            governor_reason=governor_reason,
            option_chain_count=len(option_chain),
            best_option=best_option,
            option_score=option_score,
            option_allowed=option_allowed,
            option_reason=option_reason,
            capital_available_now=capital_available_now,
        )

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
            fused["strategy"] = _norm_strategy(chosen_strategy, fused.get("strategy", strategy))
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

            log_rejection(
                fused,
                symbol,
                "breadth_blocked",
                "failed_breadth_filter",
                mode,
                breadth,
                volatility_state,
            )
            continue

        if fused["strategy"] == "NO_TRADE":
            fused["blocked_at"] = "strategy_router"
            fused["final_reason"] = "strategy_router_returned_no_trade"
            fused["final_reason_code"] = "strategy_router_returned_no_trade"
            fused = finalize_candidate_state(fused)

            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)

            log_rejection(
                fused,
                symbol,
                "strategy_router_blocked",
                "strategy_router_returned_no_trade",
                mode,
                breadth,
                volatility_state,
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
            if isinstance(existing_position, dict)
            else ""
        )

        if existing_position:
            fused["blocked_at"] = "duplicate_guard"
            fused["final_reason"] = "already_open_position"
            fused["final_reason_code"] = "already_open_position"
            fused = finalize_candidate_state(fused)

            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)

            log_rejection(
                fused,
                symbol,
                "position_duplication_blocked",
                "already_open_position",
                mode,
                breadth,
                volatility_state,
            )
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

            log_rejection(
                fused,
                symbol,
                "reentry_blocked",
                reason,
                mode,
                breadth,
                volatility_state,
            )
            continue

        score_ok = _candidate_score(fused) >= 90
        debug_row["score_allowed"] = score_ok

        if not score_ok:
            fused["blocked_at"] = "score_threshold"
            fused["final_reason"] = "failed_score_threshold"
            fused["final_reason_code"] = "failed_score_threshold"
            fused = finalize_candidate_state(fused)

            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
            debug_rows.append(debug_row)

            log_rejection(
                fused,
                symbol,
                "score_too_low",
                "failed_score_threshold",
                mode,
                breadth,
                volatility_state,
            )
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

            log_rejection(
                fused,
                symbol,
                "volatility_blocked",
                "failed_volatility_filter",
                mode,
                breadth,
                volatility_state,
            )
            continue

        if fused.get("option") and _norm_vehicle(fused.get("vehicle_selected")) == "OPTION" and not option_allowed:
            reason = _safe_str(option_reason, "weak_option_contract")
            fused["blocked_at"] = "option_executable"
            fused["final_reason"] = reason
            fused["final_reason_code"] = reason
            fused = finalize_candidate_state(fused)

            debug_row["blocked_at"] = fused.get("blocked_at", "")
            debug_row["final_reason"] = fused.get("final_reason", "")
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
            continue

        fused["research_approved"] = True
        fused["execution_ready"] = False
        fused["selected_for_execution"] = False

        guard = validate_selected_trade_for_execution(
            fused,
            capital_available=capital_available_now,
            trading_mode=resolved_trading_mode,
            current_open_positions=current_open_positions_for_guard,
            max_open_positions=max_open_positions_for_guard,
            kill_switch_enabled=False,
            session_healthy=True,
            broker_healthy=True,
        )

        guard = _safe_dict(guard)
        blocked = bool(guard.get("blocked", False))
        exec_reason = (
            _safe_str(guard.get("reason_code", ""), "")
            or _safe_str(guard.get("reason", ""), "")
            or "ok"
        )

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

    capacity = _build_selection_capacity(
        execution_ready=execution_ready,
        governor=governor,
        mode_context=resolved_trading_mode_context,
    )

    selection_limit = _safe_int(capacity.get("selection_limit", 0), 0)
    current_open_positions_for_selector = _safe_int(
        capacity.get("current_open_positions", current_open_positions_for_guard),
        current_open_positions_for_guard,
    )
    max_open_positions_for_selector = _safe_int(
        capacity.get("max_open_positions", max_open_positions_for_guard),
        max_open_positions_for_guard,
    )

    selected_trades: List[Dict[str, Any]] = []

    if execution_ready and selection_limit > 0:
        selected_trades = choose_execution_queue_option_b(
            execution_ready,
            limit=selection_limit,
            available_cash=capital_available_now,
            trading_mode=resolved_trading_mode,
            mode_context=resolved_trading_mode_context,
            current_open_positions=current_open_positions_for_selector,
            max_open_positions=max_open_positions_for_selector,
        )
    else:
        print("PROCESS SIGNALS SELECTOR SKIPPED:", {
            "execution_ready_count": len(execution_ready),
            "selection_limit": selection_limit,
            "reason": (
                "no_execution_ready"
                if not execution_ready
                else "no_remaining_capacity_or_affordability"
            ),
        })

    selected_keys = {
        (
            _norm_symbol(t.get("symbol", "")),
            _norm_strategy(t.get("strategy", "CALL"), "CALL"),
        )
        for t in selected_trades
        if isinstance(t, dict)
    }

    finalized_research_approved: List[Dict[str, Any]] = []
    finalized_selected_trades: List[Dict[str, Any]] = []

    for trade in research_approved:
        key = (
            _norm_symbol(trade.get("symbol", "")),
            _norm_strategy(trade.get("strategy", "CALL"), "CALL"),
        )

        if key in selected_keys:
            trade["selected_for_execution"] = True
            trade["execution_ready"] = True
            trade["research_approved"] = True
            trade["final_reason"] = "selected_for_execution"
            trade["final_reason_code"] = "selected_for_execution"
            trade["blocked_at"] = ""
            trade["selector_capacity"] = capacity
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
                extra={"selector_capacity": capacity},
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
            trade["selector_capacity"] = capacity
            trade = finalize_candidate_state(trade)

            finalized_research_approved.append(trade)

            log_candidate_decision(
                trade,
                status="execution_ready_not_selected",
                reason="approved_but_ranked_below_execution_cut",
                mode=mode,
                breadth=breadth,
                volatility_state=volatility_state,
                extra={"selector_capacity": capacity},
            )

        else:
            finalized_research_approved.append(trade)

    research_approved = finalized_research_approved
    selected_trades = finalized_selected_trades

    print("\nAPPROVAL DEBUG")
    for row in debug_rows:
        print(row)

    print("PROCESS SIGNALS FINAL SELECTION SUMMARY:", {
        "research_approved_count": len(research_approved),
        "execution_ready_count": len([t for t in research_approved if bool(t.get("execution_ready", False))]),
        "selected_count": len(selected_trades),
        "selected_symbols": [_norm_symbol(t.get("symbol")) for t in selected_trades],
        "capacity": capacity,
    })

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
            _print_candidate_line(trade)

    print("EXECUTION READY CANDIDATE INTELLIGENCE")
    execution_ready_now = [
        t for t in research_approved
        if bool(t.get("execution_ready", False))
    ]

    if not execution_ready_now:
        print("None")
    else:
        for trade in execution_ready_now:
            _print_candidate_line(trade)

    print("SELECTED FOR EXECUTION CANDIDATE INTELLIGENCE")
    if not selected_trades:
        print("None")
    else:
        for trade in selected_trades:
            _print_candidate_line(trade)

    return research_approved, selected_trades, mode, breadth, volatility_state


__all__ = [
    "process_signals",
    "resolve_market_mode",
    "stronger_competing_setups",
    "log_candidate_decision",
    "log_rejection",
    "log_approval",
]
