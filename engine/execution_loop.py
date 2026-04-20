from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.account_state import buying_power, record_trade
from engine.bot_logger import log_bot as default_log_bot
from engine.paper_portfolio import add_position, get_position
from engine.trade_logger import log_trade_open
from engine.trade_summary import trade_summary
from engine.trade_timeline import add_timeline_event
from engine.observatory_mode import normalize_mode, build_mode_context, classify_reason_for_mode

try:
    from engine.premium_feed import write_premium_feed_item
except Exception:
    def write_premium_feed_item(_payload):
        return None


def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in _safe_list(items):
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def _safe_mode(trade: Dict[str, Any]) -> str:
    return _safe_str((trade or {}).get("mode"), "UNKNOWN")


def _write_skip_feed(trade: Dict[str, Any], summary: str) -> None:
    if not isinstance(trade, dict):
        return
    symbol = _norm_symbol(trade.get("symbol"))
    mode = _safe_mode(trade)
    write_premium_feed_item(
        {
            "title": f"{symbol} Skipped",
            "summary": summary,
            "pro_lines": [],
            "elite_lines": [],
            "timestamp": trade.get("timestamp"),
            "mode": mode,
            "symbol": symbol,
            "status": "SKIPPED",
            "final_reason": summary,
        }
    )


def _resolve_trade_mode(trade: Dict[str, Any], lifecycle: Dict[str, Any]) -> str:
    return normalize_mode(
        trade.get("trading_mode")
        or trade.get("execution_mode")
        or trade.get("mode")
        or lifecycle.get("trading_mode")
        or lifecycle.get("execution_mode")
        or lifecycle.get("mode")
        or _safe_dict(lifecycle.get("mode_context")).get("mode")
        or "paper"
    )


def _build_trade_mode_context(trade_mode: str, lifecycle: Dict[str, Any]) -> Dict[str, Any]:
    resolved = build_mode_context(trade_mode)
    incoming = _safe_dict(lifecycle.get("mode_context"))
    merged = dict(resolved)
    if incoming:
        for key, value in incoming.items():
            if value is not None:
                merged[key] = value
    merged["mode"] = normalize_mode(merged.get("mode", trade_mode))
    return merged


def _reason_is_hard(reason_code: str, mode_context: Dict[str, Any]) -> bool:
    if not reason_code:
        return False
    if reason_code in set(_safe_list(mode_context.get("hard_block_reasons"))):
        return True
    return classify_reason_for_mode(reason_code, mode_context.get("mode")) == "hard"


def _reason_is_soft(reason_code: str, mode_context: Dict[str, Any]) -> bool:
    if not reason_code:
        return False
    if reason_code in set(_safe_list(mode_context.get("soft_block_reasons"))):
        return True
    return classify_reason_for_mode(reason_code, mode_context.get("mode")) == "soft"


def _mode_allows_warning_pass(mode_context: Dict[str, Any]) -> bool:
    mode_name = normalize_mode(mode_context.get("mode"))
    if mode_name != "survey":
        return False
    if _safe_bool(mode_context.get("strict_execution_gate"), True):
        return False
    return _safe_bool(mode_context.get("execution_warning_only"), False)


def _should_reject_reason(reason_code: str, mode_context: Dict[str, Any]) -> bool:
    if not reason_code:
        return False
    if _reason_is_hard(reason_code, mode_context):
        return True
    if _reason_is_soft(reason_code, mode_context):
        return not _mode_allows_warning_pass(mode_context)
    return _safe_bool(mode_context.get("strict_execution_gate"), True)


def _guard_payload(
    *,
    decision: str,
    reason: str,
    reason_code: str,
    warnings: Optional[List[Any]] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "decision": _safe_str(decision, "REJECT").upper(),
        "guard_reason": _safe_str(reason, ""),
        "guard_reason_code": _safe_str(reason_code, ""),
        "warnings": _dedupe_keep_order(warnings or []),
        "guard_details": _safe_dict(details),
    }


def _append_result(
    results: List[Dict[str, Any]],
    *,
    success: bool,
    status: str,
    symbol: str,
    selected_vehicle: str,
    guard: Optional[Dict[str, Any]],
    execution_result: Optional[Dict[str, Any]],
    lifecycle_after: Optional[Dict[str, Any]],
    trade_mode: str,
    mode_context: Dict[str, Any],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {
        "success": bool(success),
        "status": _safe_str(status, "UNKNOWN").upper(),
        "symbol": _norm_symbol(symbol),
        "selected_vehicle": _safe_str(selected_vehicle, "UNKNOWN").upper(),
        "guard": _safe_dict(guard),
        "execution_result": _safe_dict(execution_result) if isinstance(execution_result, dict) else execution_result,
        "lifecycle_after": _safe_dict(lifecycle_after),
        "trading_mode": normalize_mode(trade_mode),
        "mode_context": _safe_dict(mode_context),
        "timestamp": _now_iso(),
    }
    if isinstance(extra, dict):
        payload.update(extra)
    results.append(payload)
    return payload


def _merge_execution_into_position(
    queued_trade: Dict[str, Any],
    lifecycle_after: Dict[str, Any],
    execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    queued_trade = _safe_dict(deepcopy(queued_trade))
    lifecycle_after = _safe_dict(deepcopy(lifecycle_after))
    execution_result = _safe_dict(deepcopy(execution_result))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    merged: Dict[str, Any] = {}
    merged.update(queued_trade)
    merged.update(lifecycle_after)

    symbol = _norm_symbol(
        merged.get("symbol")
        or execution_record.get("symbol")
        or queued_trade.get("symbol")
    )
    strategy = _safe_str(
        merged.get("strategy")
        or execution_record.get("strategy")
        or queued_trade.get("strategy"),
        "CALL",
    ).upper()
    trade_id = _safe_str(
        merged.get("trade_id")
        or execution_record.get("trade_id")
        or queued_trade.get("trade_id"),
        "",
    )

    selected_vehicle = _safe_str(
        merged.get("vehicle_selected", merged.get("vehicle", "STOCK")),
        "STOCK",
    ).upper()
    if selected_vehicle not in {"OPTION", "STOCK", "RESEARCH_ONLY"}:
        selected_vehicle = "STOCK"

    fill_price = _safe_float(
        execution_record.get(
            "fill_price",
            execution_record.get(
                "filled_price",
                merged.get("fill_price", merged.get("entry", merged.get("price", 0.0))),
            ),
        ),
        _safe_float(merged.get("entry", merged.get("price", 0.0)), 0.0),
    )

    requested_price = _safe_float(
        execution_record.get(
            "requested_price",
            merged.get("requested_price", merged.get("price", 0.0)),
        ),
        _safe_float(merged.get("price", 0.0), 0.0),
    )

    opened_at = _safe_str(
        merged.get("opened_at", execution_record.get("opened_at", _now_iso())),
        _now_iso(),
    )

    shares = _safe_int(
        execution_record.get("shares", merged.get("shares", merged.get("size", 0))),
        _safe_int(merged.get("shares", 0), 0),
    )
    contracts = _safe_int(
        execution_record.get("contracts", merged.get("contracts", 0)),
        _safe_int(merged.get("contracts", 0), 0),
    )
    filled_quantity = _safe_int(
        execution_record.get("filled_quantity", execution_record.get("quantity", 0)),
        0,
    )

    if selected_vehicle == "OPTION":
        contracts = max(1, contracts or filled_quantity or 1)
        shares = 0
        size = contracts
    elif selected_vehicle == "STOCK":
        shares = max(1, shares or filled_quantity or 1)
        contracts = 0
        size = shares
    else:
        shares = 0
        contracts = 0
        size = 0

    merged["symbol"] = symbol
    merged["strategy"] = strategy
    merged["trade_id"] = trade_id or f"{symbol}-{strategy}-{opened_at.replace(':', '').replace('-', '').replace('.', '')}"
    merged["vehicle_selected"] = selected_vehicle
    merged["vehicle"] = selected_vehicle
    merged["shares"] = shares
    merged["contracts"] = contracts
    merged["size"] = size
    merged["requested_price"] = round(requested_price, 4)
    merged["fill_price"] = round(fill_price, 4)
    merged["price"] = round(_safe_float(merged.get("price", fill_price), fill_price), 4)
    merged["entry"] = round(_safe_float(merged.get("entry", fill_price), fill_price), 4)
    merged["current_price"] = round(_safe_float(merged.get("current_price", fill_price), fill_price), 4)
    merged["stop"] = round(_safe_float(merged.get("stop"), 0.0), 4)
    merged["target"] = round(_safe_float(merged.get("target"), 0.0), 4)
    merged["commission"] = round(
        _safe_float(execution_record.get("commission", merged.get("commission", 0.0)), 0.0),
        4,
    )
    merged["opened_at"] = opened_at
    merged["timestamp"] = _safe_str(merged.get("timestamp"), opened_at)
    merged["status"] = "OPEN"
    merged["execution_result"] = execution_result
    merged["execution_status"] = _safe_str(
        execution_result.get("status", execution_record.get("status", "FILLED")),
        "FILLED",
    ).upper()
    merged["research_approved"] = bool(merged.get("research_approved", True))
    merged["execution_ready"] = bool(merged.get("execution_ready", True))
    merged["selected_for_execution"] = True
    merged["final_reason"] = _safe_str(merged.get("final_reason"), "executed")
    merged["final_reason_code"] = _safe_str(merged.get("final_reason_code"), "executed")
    return merged


def execute_trades(
    queue,
    limit=3,
    portfolio_context=None,
    max_open_positions=5,
    open_positions=None,
    kill_switch_enabled=False,
    session_healthy=True,
    broker_adapter=None,
    log_bot=None,
):
    from typing import Any, Dict, List
    from engine.execution_handoff import execute_via_adapter, summarize_execution_packet

    queue = queue if isinstance(queue, list) else []
    portfolio_context = portfolio_context if isinstance(portfolio_context, dict) else {}
    open_positions = open_positions if isinstance(open_positions, list) else []

    executed = 0
    results: List[Dict[str, Any]] = []
    remaining_queue: List[Dict[str, Any]] = []

    def _log(message: str, level: str = "INFO") -> None:
        logger = log_bot if callable(log_bot) else default_log_bot
        try:
            logger(message, level)
        except Exception:
            pass

    def _sync_trade_into_lifecycle(
        trade_payload: Dict[str, Any],
        lifecycle_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Preserve queue-selected state and upstream connections.
        Once a trade is selected for execution, the queued trade payload is the
        source of truth for execution-facing fields.
        """
        merged = dict(lifecycle_payload or {})

        overwrite_keys = [
            "trade_id",
            "research_approved",
            "execution_ready",
            "selected_for_execution",
            "selected_vehicle",
            "vehicle_selected",
            "vehicle",
            "final_decision",
            "final_reason",
            "final_reason_code",
            "decision_reason",
            "decision_reason_code",
            "score",
            "fused_score",
            "confidence",
            "strategy",
            "direction",
            "symbol",
            "contracts",
            "shares",
            "estimated_cost",
            "stock_price",
            "reserve_check",
            "warnings",
            "rejection_reasons",
            "mode",
            "trading_mode",
            "execution_mode",
            "mode_context",
            "contract",
            "capital_required",
            "minimum_trade_cost",
            "capital_available",
            "timestamp",
            "v2_score",
            "v2_reason",
            "v2_vehicle_bias",
            "readiness_score",
            "promotion_score",
            "rebuild_pressure",
            "option",
            "option_path",
            "stock_path",
            "governor",
        ]

        for key in overwrite_keys:
            if trade_payload.get(key) is not None:
                merged[key] = trade_payload.get(key)

        # normalize vehicle aliases both ways
        if trade_payload.get("vehicle_selected") is not None:
            merged["vehicle_selected"] = trade_payload.get("vehicle_selected")
            merged["selected_vehicle"] = trade_payload.get("vehicle_selected")
        elif trade_payload.get("selected_vehicle") is not None:
            merged["selected_vehicle"] = trade_payload.get("selected_vehicle")
            merged["vehicle_selected"] = trade_payload.get("selected_vehicle")
        elif merged.get("vehicle_selected") is not None and merged.get("selected_vehicle") in (None, ""):
            merged["selected_vehicle"] = merged.get("vehicle_selected")
        elif merged.get("selected_vehicle") is not None and merged.get("vehicle_selected") in (None, ""):
            merged["vehicle_selected"] = merged.get("selected_vehicle")

        # preserve explicit queue selection
        selected_flag = (
            _safe_bool(trade_payload.get("selected_for_execution"), False)
            or _safe_bool(merged.get("selected_for_execution"), False)
        )
        merged["selected_for_execution"] = selected_flag

        # preserve explicit readiness if already approved upstream
        merged["research_approved"] = _safe_bool(
            trade_payload.get("research_approved", merged.get("research_approved")),
            False,
        )
        merged["execution_ready"] = _safe_bool(
            trade_payload.get("execution_ready", merged.get("execution_ready")),
            False,
        )

        # preserve trade id aggressively
        merged["trade_id"] = _safe_str(
            trade_payload.get("trade_id") or merged.get("trade_id"),
            "",
        )

        # if the trade is selected and execution-ready, lifecycle should not fall backwards
        if merged["selected_for_execution"] and merged["execution_ready"]:
            merged["lifecycle_stage"] = merged.get("lifecycle_stage") or "SELECTED"
            if merged["lifecycle_stage"] == "EXECUTION_READY":
                merged["lifecycle_stage"] = "SELECTED"

        return merged

    for trade in queue:
        if executed >= limit:
            if isinstance(trade, dict):
                remaining_queue.append(trade)
            continue

        if not isinstance(trade, dict):
            _log("Skipped malformed queued trade payload.", "WARN")
            continue

        lifecycle = _safe_dict(trade.get("lifecycle"))
        merged_lifecycle = _sync_trade_into_lifecycle(trade, lifecycle)

        trade_mode = _resolve_trade_mode(trade, merged_lifecycle)
        mode_context = _build_trade_mode_context(trade_mode, merged_lifecycle)

        symbol = _norm_symbol(trade.get("symbol") or merged_lifecycle.get("symbol"))
        strategy = _safe_str(
            trade.get("strategy") or merged_lifecycle.get("strategy"),
            "CALL",
        ).upper()
        selected_vehicle = _safe_str(
            trade.get(
                "vehicle_selected",
                trade.get(
                    "selected_vehicle",
                    merged_lifecycle.get("vehicle_selected", merged_lifecycle.get("selected_vehicle", "STOCK")),
                ),
            ),
            "STOCK",
        ).upper()

        queue_limit = _safe_int(mode_context.get("queue_limit", limit), limit)
        if queue_limit > 0 and executed >= queue_limit:
            remaining_queue.append(trade)
            continue

        print("PRE-EXECUTION-HANDOFF-PREP:", {
            "symbol": symbol,
            "trade_id": _safe_str(trade.get("trade_id") or merged_lifecycle.get("trade_id"), ""),
            "research_approved": _safe_bool(merged_lifecycle.get("research_approved"), False),
            "execution_ready": _safe_bool(merged_lifecycle.get("execution_ready"), False),
            "selected_for_execution": _safe_bool(merged_lifecycle.get("selected_for_execution"), False),
            "vehicle_selected": selected_vehicle,
            "lifecycle_stage": merged_lifecycle.get("lifecycle_stage"),
            "trading_mode": trade_mode,
        })

        if not merged_lifecycle:
            reason_code = "missing_lifecycle"
            reason_text = "Skipped because the queued trade was missing its lifecycle object."
            _log(f"{symbol} skipped | {reason_code}", "WARN")
            _write_skip_feed(trade, reason_text)
            _append_result(
                results,
                success=False,
                status="REJECTED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard=_guard_payload(
                    decision="REJECT",
                    reason="Missing lifecycle object in queued trade.",
                    reason_code=reason_code,
                ),
                execution_result=None,
                lifecycle_after={},
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            continue

        merged_lifecycle["trading_mode"] = trade_mode
        merged_lifecycle["execution_mode"] = trade_mode
        merged_lifecycle["mode"] = trade_mode
        merged_lifecycle["mode_context"] = mode_context

        if not _safe_bool(merged_lifecycle.get("research_approved"), False):
            reason_code = "research_not_approved"
            reason_text = f"{symbol} skipped because research approval was not present."
            _log(f"{symbol} rejected | {reason_code}", "WARN")
            _write_skip_feed(trade, reason_text)
            add_timeline_event(symbol, "SKIPPED", {"reason": reason_code, "trading_mode": trade_mode})
            _append_result(
                results,
                success=False,
                status="REJECTED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard=_guard_payload(
                    decision="REJECT",
                    reason="Research approval missing.",
                    reason_code=reason_code,
                ),
                execution_result=None,
                lifecycle_after=merged_lifecycle,
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            continue

        lifecycle_reason_code = _safe_str(
            merged_lifecycle.get("final_reason_code"),
            "execution_not_ready",
        )
        lifecycle_reason_text = _safe_str(
            merged_lifecycle.get("final_reason"),
            "Lifecycle was not execution ready.",
        )

        if not _safe_bool(merged_lifecycle.get("execution_ready"), False):
            should_reject = _should_reject_reason(lifecycle_reason_code, mode_context)
            if should_reject:
                _log(f"{symbol} rejected | {lifecycle_reason_code}", "WARN")
                _write_skip_feed(trade, f"{symbol} skipped: {lifecycle_reason_text}")
                add_timeline_event(
                    symbol,
                    "SKIPPED",
                    {"reason": lifecycle_reason_code, "trading_mode": trade_mode},
                )
                _append_result(
                    results,
                    success=False,
                    status="REJECTED",
                    symbol=symbol,
                    selected_vehicle=selected_vehicle,
                    guard=_guard_payload(
                        decision="REJECT",
                        reason=lifecycle_reason_text,
                        reason_code=lifecycle_reason_code,
                    ),
                    execution_result=None,
                    lifecycle_after=merged_lifecycle,
                    trade_mode=trade_mode,
                    mode_context=mode_context,
                )
                continue
            else:
                merged_lifecycle.setdefault("warnings", [])
                merged_lifecycle["warnings"] = _dedupe_keep_order(
                    merged_lifecycle.get("warnings", []) + [lifecycle_reason_code]
                )

        existing = get_position(
            symbol,
            trade_id=_safe_str(
                trade.get("trade_id") or merged_lifecycle.get("trade_id"),
                "",
            ),
        )
        if existing:
            reason_code = "existing_open_position"
            _log(f"{symbol} rejected | {reason_code}", "WARN")
            _write_skip_feed(trade, f"{symbol} skipped because there is already an open position.")
            add_timeline_event(
                symbol,
                "SKIPPED",
                {"reason": reason_code, "trading_mode": trade_mode},
            )
            _append_result(
                results,
                success=False,
                status="REJECTED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard=_guard_payload(
                    decision="REJECT",
                    reason="Existing open position.",
                    reason_code=reason_code,
                ),
                execution_result=None,
                lifecycle_after=merged_lifecycle,
                trade_mode=trade_mode,
                mode_context=mode_context,
            )
            continue

        current_open_positions = len(open_positions)
        if current_open_positions >= max_open_positions:
            reason_code = "max_open_positions_reached"
            reason_text = "Execution blocked because the open-position cap has been reached."
            should_reject = _should_reject_reason(reason_code, mode_context)
            if should_reject:
                _log(f"{symbol} rejected | {reason_code}", "WARN")
                _write_skip_feed(trade, f"{symbol} skipped: {reason_text}")
                add_timeline_event(
                    symbol,
                    "SKIPPED",
                    {"reason": reason_code, "trading_mode": trade_mode},
                )
                _append_result(
                    results,
                    success=False,
                    status="REJECTED",
                    symbol=symbol,
                    selected_vehicle=selected_vehicle,
                    guard=_guard_payload(
                        decision="REJECT",
                        reason=reason_text,
                        reason_code=reason_code,
                        details={
                            "max_open_positions": max_open_positions,
                            "current_open_positions": current_open_positions,
                        },
                    ),
                    execution_result=None,
                    lifecycle_after=merged_lifecycle,
                    trade_mode=trade_mode,
                    mode_context=mode_context,
                )
                continue
            else:
                merged_lifecycle.setdefault("warnings", [])
                merged_lifecycle["warnings"] = _dedupe_keep_order(
                    merged_lifecycle.get("warnings", []) + [reason_code]
                )

        trade_for_execution = dict(trade)
        trade_for_execution["lifecycle"] = merged_lifecycle
        trade_for_execution["trade_id"] = _safe_str(
            trade.get("trade_id") or merged_lifecycle.get("trade_id"),
            "",
        )
        trade_for_execution["research_approved"] = _safe_bool(
            trade.get("research_approved", merged_lifecycle.get("research_approved")),
            False,
        )
        trade_for_execution["execution_ready"] = _safe_bool(
            trade.get("execution_ready", merged_lifecycle.get("execution_ready")),
            False,
        )
        trade_for_execution["selected_for_execution"] = (
            _safe_bool(trade.get("selected_for_execution"), False)
            or _safe_bool(merged_lifecycle.get("selected_for_execution"), False)
        )
        trade_for_execution["vehicle_selected"] = selected_vehicle
        trade_for_execution["selected_vehicle"] = selected_vehicle
        trade_for_execution["trading_mode"] = trade_mode
        trade_for_execution["execution_mode"] = trade_mode
        trade_for_execution["mode"] = trade_mode
        trade_for_execution["mode_context"] = mode_context

        print("PRE-EXECUTION-HANDOFF:", {
            "symbol": trade_for_execution.get("symbol"),
            "trade_id": trade_for_execution.get("trade_id"),
            "research_approved": trade_for_execution.get("research_approved"),
            "execution_ready": trade_for_execution.get("execution_ready"),
            "selected_for_execution": trade_for_execution.get("selected_for_execution"),
            "vehicle_selected": trade_for_execution.get("vehicle_selected"),
            "lifecycle_stage": _safe_dict(trade_for_execution.get("lifecycle")).get("lifecycle_stage"),
            "lifecycle_selected_for_execution": _safe_dict(trade_for_execution.get("lifecycle")).get("selected_for_execution"),
            "trading_mode": trade_for_execution.get("trading_mode"),
        })

        packet = execute_via_adapter(
            queued_trade=trade_for_execution,
            portfolio_context=portfolio_context,
            max_open_positions=max_open_positions,
            current_open_positions=current_open_positions,
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_adapter=broker_adapter,
        )
        packet = _safe_dict(packet)
        summary = _safe_dict(summarize_execution_packet(packet))
        lifecycle_after = _safe_dict(packet.get("lifecycle_after")) or dict(merged_lifecycle)
        execution_result = _safe_dict(packet.get("execution_result"))
        raw_guard = _safe_dict(packet.get("guard"))

        lifecycle_after["trading_mode"] = trade_mode
        lifecycle_after["execution_mode"] = trade_mode
        lifecycle_after["mode"] = trade_mode
        lifecycle_after["mode_context"] = mode_context
        lifecycle_after["trade_id"] = _safe_str(
            lifecycle_after.get("trade_id")
            or trade_for_execution.get("trade_id")
            or merged_lifecycle.get("trade_id"),
            "",
        )

        packet_success = _safe_bool(packet.get("success"), False)

        if not packet_success:
            reason_code = (
                _safe_str(summary.get("guard_reason_code"), "")
                or _safe_str(raw_guard.get("guard_reason_code"), "")
                or _safe_str(execution_result.get("reason_code"), "")
                or "execution_rejected"
            )
            reason_text = (
                _safe_str(summary.get("guard_reason"), "")
                or _safe_str(raw_guard.get("guard_reason"), "")
                or _safe_str(execution_result.get("reason"), "")
                or "Execution rejected."
            )
            should_reject = _should_reject_reason(reason_code, mode_context)
            decision = "REJECT" if should_reject else "WARN"

            lifecycle_after["blocked_at"] = lifecycle_after.get("blocked_at") or "execution_handoff"
            lifecycle_after["final_reason"] = reason_text
            lifecycle_after["final_reason_code"] = reason_code
            lifecycle_after["selected_for_execution"] = _safe_bool(
                lifecycle_after.get("selected_for_execution"),
                False,
            )

            if should_reject:
                lifecycle_after["execution_ready"] = False
                _log(f"{symbol} rejected | {reason_text}", "WARN")
                _write_skip_feed(trade, f"{symbol} skipped: {reason_text}")
                add_timeline_event(
                    symbol,
                    "SKIPPED",
                    {"reason": reason_code, "trading_mode": trade_mode},
                )
                _append_result(
                    results,
                    success=False,
                    status="REJECTED",
                    symbol=symbol,
                    selected_vehicle=selected_vehicle,
                    guard=_guard_payload(
                        decision=decision,
                        reason=reason_text,
                        reason_code=reason_code,
                        warnings=raw_guard.get("warnings", []),
                    ),
                    execution_result=execution_result,
                    lifecycle_after=lifecycle_after,
                    trade_mode=trade_mode,
                    mode_context=mode_context,
                )
                continue

            lifecycle_after.setdefault("warnings", [])
            lifecycle_after["warnings"] = _dedupe_keep_order(
                lifecycle_after.get("warnings", []) + [reason_code]
            )

        execution_record = _safe_dict(execution_result.get("execution_record"))
        position_payload = _merge_execution_into_position(
            queued_trade=trade_for_execution,
            lifecycle_after=lifecycle_after,
            execution_result=execution_result,
        )

        position_payload["trading_mode"] = trade_mode
        position_payload["execution_mode"] = trade_mode
        position_payload["mode"] = trade_mode
        position_payload["mode_context"] = mode_context
        position_payload["trade_id"] = _safe_str(
            position_payload.get("trade_id")
            or lifecycle_after.get("trade_id")
            or trade_for_execution.get("trade_id"),
            "",
        )
        position_payload["selected_for_execution"] = True
        position_payload["execution_ready"] = True

        try:
            stored_position = add_position(position_payload)
        except Exception as e:
            _log(f"{symbol} execution succeeded but add_position failed: {e}", "ERROR")
            _append_result(
                results,
                success=False,
                status="STORAGE_FAILED",
                symbol=symbol,
                selected_vehicle=selected_vehicle,
                guard=_guard_payload(
                    decision="REJECT",
                    reason=str(e),
                    reason_code="storage_failed",
                ),
                execution_result=execution_result,
                lifecycle_after=lifecycle_after,
                trade_mode=trade_mode,
                mode_context=mode_context,
                extra={"storage_error": str(e)},
            )
            continue

        fill_price = _safe_float(
            execution_record.get(
                "fill_price",
                execution_record.get("filled_price", stored_position.get("entry", 0.0)),
            ),
            _safe_float(stored_position.get("entry", 0.0), 0.0),
        )
        commission = _safe_float(
            execution_record.get("commission", stored_position.get("commission", 0.0)),
            0.0,
        )

        if stored_position.get("vehicle_selected") == "OPTION":
            quantity_for_account = _safe_int(stored_position.get("contracts", 1), 1)
        else:
            quantity_for_account = _safe_int(
                stored_position.get("shares", stored_position.get("size", 1)),
                1,
            )

        try:
            record_trade(symbol, fill_price, quantity_for_account)
        except Exception:
            pass

        try:
            log_trade_open(
                symbol,
                strategy,
                fill_price,
                quantity_for_account,
                _safe_float(stored_position.get("fused_score", stored_position.get("score", 0.0)), 0.0),
                _safe_str(stored_position.get("confidence", "LOW"), "LOW"),
            )
        except Exception:
            pass

        add_timeline_event(
            symbol,
            "OPENED",
            {
                "trade_id": stored_position.get("trade_id"),
                "strategy": strategy,
                "vehicle_selected": stored_position.get("vehicle_selected"),
                "requested_price": round(_safe_float(stored_position.get("requested_price", 0.0), 0.0), 4),
                "fill_price": round(fill_price, 4),
                "commission": round(commission, 4),
                "shares": stored_position.get("shares", 0),
                "contracts": stored_position.get("contracts", 0),
                "size": stored_position.get("size", 0),
                "stop": round(_safe_float(stored_position.get("stop", 0.0), 0.0), 4),
                "target": round(_safe_float(stored_position.get("target", 0.0), 0.0), 4),
                "mode": stored_position.get("mode"),
                "trading_mode": trade_mode,
                "fused_score": stored_position.get("fused_score", stored_position.get("score")),
                "v2_score": stored_position.get("v2_score"),
                "final_reason": stored_position.get("final_reason"),
                "final_reason_code": stored_position.get("final_reason_code"),
            },
        )

        try:
            trade_summary(stored_position)
        except Exception:
            pass

        open_positions.append(stored_position)
        executed += 1

        _log(
            f"{symbol} executed successfully | mode={trade_mode} "
            f"vehicle={stored_position.get('vehicle_selected')} "
            f"shares={stored_position.get('shares', 0)} "
            f"contracts={stored_position.get('contracts', 0)} "
            f"fill={round(fill_price, 4)} "
            f"trade_id={stored_position.get('trade_id')}",
            "SUCCESS",
        )

        _append_result(
            results,
            success=True,
            status="EXECUTED",
            symbol=symbol,
            selected_vehicle=_safe_str(stored_position.get("vehicle_selected"), selected_vehicle),
            guard=_guard_payload(
                decision="APPROVE",
                reason="Execution completed successfully.",
                reason_code="executed",
            ),
            execution_result=execution_result,
            lifecycle_after=lifecycle_after,
            trade_mode=trade_mode,
            mode_context=mode_context,
            extra={
                "stored_position": stored_position,
                "fill_price": fill_price,
                "commission": commission,
                "trade_id": stored_position.get("trade_id"),
            },
        )

    return {
        "executed_count": executed,
        "results": results,
        "remaining_queue": remaining_queue,
        "open_positions": open_positions,
    }
