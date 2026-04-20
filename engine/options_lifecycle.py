from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

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
            "top_ranked_contracts",
            "raw",
        ]

        for key in overwrite_keys:
            if trade_payload.get(key) is not None:
                merged[key] = trade_payload.get(key)

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

        selected_flag = (
            _safe_bool(trade_payload.get("selected_for_execution"), False)
            or _safe_bool(merged.get("selected_for_execution"), False)
        )
        merged["selected_for_execution"] = selected_flag

        merged["research_approved"] = _safe_bool(
            trade_payload.get("research_approved", merged.get("research_approved")),
            False,
        )
        merged["execution_ready"] = _safe_bool(
            trade_payload.get("execution_ready", merged.get("execution_ready")),
            False,
        )

        merged["trade_id"] = _safe_str(
            trade_payload.get("trade_id") or merged.get("trade_id"),
            "",
        )

        if merged["selected_for_execution"] and merged["execution_ready"]:
            current_stage = _safe_str(merged.get("lifecycle_stage"), "")
            if current_stage in {"", "EXECUTION_READY"}:
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
                    merged_lifecycle.get(
                        "vehicle_selected",
                        merged_lifecycle.get("selected_vehicle", "STOCK"),
                    ),
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
