from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Tuple

from engine.canonical_trade_state import build_open_trade_state
from engine.canonical_execution_guard import validate_selected_trade_for_execution
from engine.observatory_mode import build_mode_context, normalize_mode


OPTION_CONTRACT_MULTIPLIER = 100
DEFAULT_OPTION_STOP_PCT = 0.65
DEFAULT_OPTION_TARGET_PCT = 1.60
DEFAULT_STOCK_STOP_PCT = 0.97
DEFAULT_STOCK_TARGET_PCT = 1.10


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


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


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "y", "on"}:
                return True
            if lowered in {"false", "0", "no", "n", "off"}:
                return False
        return bool(value)
    except Exception:
        return bool(default)


def _now_iso() -> str:
    return datetime.now().isoformat()


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _round4(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 4)


def _derive_trade_id(symbol: str, strategy: str, timestamp: str) -> str:
    clean_stamp = (
        _safe_str(timestamp, _now_iso())
        .replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("+", "")
        .replace("T", "")
    )
    return f"{symbol}-{strategy}-{clean_stamp}"


def _resolve_mode_context(
    trading_mode: str,
    incoming_mode_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    normalized_mode = normalize_mode(trading_mode or "paper")
    resolved = build_mode_context(normalized_mode)
    incoming = _safe_dict(incoming_mode_context)

    merged = dict(resolved)
    for key, value in incoming.items():
        if value is not None:
            merged[key] = value

    merged["mode"] = normalize_mode(merged.get("mode", normalized_mode))
    return merged


def _normalize_selected_vehicle(
    lifecycle_obj: Dict[str, Any],
    raw: Dict[str, Any],
) -> str:
    vehicle = _upper(
        lifecycle_obj.get("vehicle_selected")
        or lifecycle_obj.get("selected_vehicle")
        or lifecycle_obj.get("vehicle")
        or raw.get("vehicle_selected")
        or raw.get("selected_vehicle")
        or raw.get("vehicle"),
        "RESEARCH_ONLY",
    )

    if vehicle in {"OPTION", "OPTIONS"}:
        return "OPTION"
    if vehicle in {"STOCK", "EQUITY", "SHARES"}:
        return "STOCK"
    if vehicle in {"RESEARCH_ONLY", "RESEARCH", "NONE", "NO_TRADE"}:
        return "RESEARCH_ONLY"

    return "RESEARCH_ONLY"


def _find_option_like_payload(source: Dict[str, Any]) -> Dict[str, Any]:
    source = _safe_dict(source)

    direct_candidates = [
        source.get("option"),
        source.get("contract"),
        source.get("best_option"),
        source.get("best_option_preview"),
        source.get("selected_option"),
        source.get("option_contract"),
    ]

    for candidate in direct_candidates:
        candidate = _safe_dict(candidate)
        if candidate:
            return dict(candidate)

    lifecycle = _safe_dict(source.get("lifecycle"))
    for key in ["option", "contract", "best_option", "best_option_preview", "selected_option"]:
        candidate = _safe_dict(lifecycle.get(key))
        if candidate:
            return dict(candidate)

    raw = _safe_dict(source.get("raw"))
    for key in ["option", "contract", "best_option", "best_option_preview", "selected_option"]:
        candidate = _safe_dict(raw.get(key))
        if candidate:
            return dict(candidate)

    return {}


def _normalize_contract_payload(
    lifecycle_obj: Dict[str, Any],
    raw: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    lifecycle_obj = _safe_dict(lifecycle_obj)
    raw = _safe_dict(raw)

    contract = _safe_dict(lifecycle_obj.get("contract"))
    option = _safe_dict(lifecycle_obj.get("option"))

    if not contract:
        contract = _safe_dict(raw.get("contract"))
    if not option:
        option = _safe_dict(raw.get("option"))

    if not contract and not option:
        found = _find_option_like_payload(lifecycle_obj) or _find_option_like_payload(raw)
        contract = dict(found)
        option = dict(found)

    if option and not contract:
        contract = dict(option)
    if contract and not option:
        option = dict(contract)

    return dict(contract), dict(option)


def _contract_symbol(option: Dict[str, Any], fallback: Any = "") -> str:
    option = _safe_dict(option)
    return _safe_str(
        fallback
        or option.get("contract_symbol")
        or option.get("contractSymbol")
        or option.get("symbol")
        or option.get("option_symbol"),
        "",
    )


def _option_expiry(option: Dict[str, Any], fallback: Any = "") -> str:
    option = _safe_dict(option)
    return _safe_str(
        fallback
        or option.get("expiry")
        or option.get("expiration")
        or option.get("expirationDate")
        or option.get("lastTradeDate"),
        "",
    )


def _option_right(option: Dict[str, Any], strategy: str = "CALL", fallback: Any = "") -> str:
    option = _safe_dict(option)
    right = _upper(
        fallback
        or option.get("right")
        or option.get("type")
        or option.get("contract_type")
        or strategy,
        strategy,
    )

    if right in {"C", "CALLS"}:
        return "CALL"
    if right in {"P", "PUTS"}:
        return "PUT"
    if right in {"CALL", "PUT"}:
        return right
    return _upper(strategy, "CALL")


def _extract_option_fill_price(option: Dict[str, Any], fallback: float = 0.0) -> float:
    option = _safe_dict(option)

    candidates = [
        option.get("selected_price_reference"),
        option.get("price_reference"),
        option.get("mark"),
        option.get("mid"),
        option.get("last"),
        option.get("price"),
        option.get("ask"),
        option.get("bid"),
        fallback,
    ]

    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4)

    return 0.0


def _extract_underlying_price(source: Dict[str, Any], raw: Dict[str, Any] | None = None) -> float:
    source = _safe_dict(source)
    raw = _safe_dict(raw)

    candidates = [
        source.get("underlying_price"),
        source.get("current_underlying_price"),
        source.get("stock_price"),
        source.get("price"),
        raw.get("underlying_price"),
        raw.get("current_underlying_price"),
        raw.get("stock_price"),
        raw.get("price"),
    ]

    for value in candidates:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4)

    return 0.0


def _option_stop(entry_premium: float, existing: Any = None) -> float:
    existing_stop = _safe_float(existing, 0.0)
    if existing_stop > 0 and entry_premium > 0:
        # Protect against old underlying-based stops leaking into option trades.
        if existing_stop <= entry_premium * 5:
            return round(existing_stop, 4)

    return round(entry_premium * DEFAULT_OPTION_STOP_PCT, 4) if entry_premium > 0 else 0.0


def _option_target(entry_premium: float, existing: Any = None) -> float:
    existing_target = _safe_float(existing, 0.0)
    if existing_target > 0 and entry_premium > 0:
        # Protect against old underlying-based targets leaking into option trades.
        if existing_target <= entry_premium * 8:
            return round(existing_target, 4)

    return round(entry_premium * DEFAULT_OPTION_TARGET_PCT, 4) if entry_premium > 0 else 0.0


def _stock_stop(entry_price: float, existing: Any = None) -> float:
    existing_stop = _safe_float(existing, 0.0)
    if existing_stop > 0:
        return round(existing_stop, 4)
    return round(entry_price * DEFAULT_STOCK_STOP_PCT, 4) if entry_price > 0 else 0.0


def _stock_target(entry_price: float, existing: Any = None) -> float:
    existing_target = _safe_float(existing, 0.0)
    if existing_target > 0:
        return round(existing_target, 4)
    return round(entry_price * DEFAULT_STOCK_TARGET_PCT, 4) if entry_price > 0 else 0.0


def _normalize_execution_record(
    queued_trade: Dict[str, Any],
    execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    queued_trade = _safe_dict(queued_trade)
    execution_result = _safe_dict(execution_result)

    option = _safe_dict(queued_trade.get("option"))
    vehicle_selected = _upper(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle"),
        "STOCK",
    )
    symbol = _norm_symbol(queued_trade.get("symbol"))
    strategy = _upper(queued_trade.get("strategy"), "CALL")

    opened_at = _safe_str(
        execution_result.get("opened_at")
        or _safe_dict(execution_result.get("execution_record")).get("opened_at"),
        _now_iso(),
    )

    if vehicle_selected == "OPTION":
        fallback_option_price = _safe_float(
            queued_trade.get(
                "option_entry",
                queued_trade.get(
                    "entry_premium",
                    queued_trade.get("premium_entry", queued_trade.get("entry", 0.0)),
                ),
            ),
            0.0,
        )
        fill_price = _safe_float(execution_result.get("fill_price"), 0.0)
        if fill_price <= 0:
            fill_price = _extract_option_fill_price(option, fallback_option_price)

        filled_quantity = max(
            1,
            _safe_int(
                execution_result.get(
                    "filled_quantity",
                    queued_trade.get("contracts", queued_trade.get("quantity", 1)),
                ),
                1,
            ),
        )
        shares = 0
        contracts = filled_quantity
        underlying_price = _extract_underlying_price(queued_trade)

    else:
        fill_price = _safe_float(execution_result.get("fill_price"), 0.0)
        if fill_price <= 0:
            fill_price = _extract_underlying_price(queued_trade)

        filled_quantity = max(
            1,
            _safe_int(
                execution_result.get(
                    "filled_quantity",
                    queued_trade.get("shares", queued_trade.get("size", queued_trade.get("quantity", 1))),
                ),
                1,
            ),
        )
        shares = filled_quantity
        contracts = 0
        underlying_price = fill_price

    contract_symbol = _contract_symbol(option, queued_trade.get("contract_symbol") or queued_trade.get("option_symbol"))
    expiry = _option_expiry(option, queued_trade.get("expiry") or queued_trade.get("expiration"))
    right = _option_right(option, strategy, queued_trade.get("right"))

    record = {
        "trade_id": _safe_str(queued_trade.get("trade_id"), ""),
        "symbol": symbol,
        "strategy": strategy,
        "vehicle": vehicle_selected,
        "vehicle_selected": vehicle_selected,
        "selected_vehicle": vehicle_selected,
        "requested_price": _round4(queued_trade.get("requested_price", queued_trade.get("entry", fill_price)), fill_price),
        "fill_price": _round4(fill_price),
        "filled_price": _round4(fill_price),
        "filled_quantity": filled_quantity,
        "quantity": filled_quantity,
        "shares": shares,
        "contracts": contracts,
        "status": "FILLED",
        "opened_at": opened_at,
        "underlying_price": _round4(underlying_price),
        "current_underlying_price": _round4(underlying_price),
    }

    if vehicle_selected == "OPTION":
        mark = _round4(
            queued_trade.get(
                "mark",
                option.get("mark", option.get("selected_price_reference", option.get("price_reference", option.get("last", fill_price)))),
            ),
            fill_price,
        )

        record.update(
            {
                "contract_symbol": contract_symbol,
                "option_symbol": contract_symbol,
                "expiry": expiry,
                "expiration": expiry,
                "strike": _round4(queued_trade.get("strike", option.get("strike", 0.0))),
                "right": right,
                "bid": _round4(queued_trade.get("bid", option.get("bid", 0.0))),
                "ask": _round4(queued_trade.get("ask", option.get("ask", 0.0))),
                "mark": mark,
                "last": _round4(queued_trade.get("last", option.get("last", fill_price)), fill_price),
                "open_interest": _safe_int(
                    queued_trade.get("open_interest", option.get("open_interest", option.get("openInterest", 0))),
                    0,
                ),
                "volume": _safe_int(queued_trade.get("volume", option.get("volume", 0)), 0),
                "dte": _safe_int(queued_trade.get("dte", option.get("dte", option.get("daysToExpiration", 0))), 0),
                "entry_premium": _round4(fill_price),
                "premium_entry": _round4(fill_price),
                "option_entry": _round4(fill_price),
                "current_premium": _round4(fill_price),
                "premium_current": _round4(fill_price),
                "current_option_mark": _round4(fill_price),
                "option_current_price": _round4(fill_price),
                "monitoring_price_type": "OPTION_PREMIUM",
                "price_review_basis": "OPTION_PREMIUM_ONLY",
                "underlying_price_used_for_close_decision": False,
            }
        )

    else:
        # For STOCK fallback, preserve the fact that option research existed,
        # but do not let stale option contract fields make this look like an option position.
        record.update(
            {
                "monitoring_price_type": "UNDERLYING",
                "price_review_basis": "UNDERLYING",
                "underlying_price_used_for_close_decision": True,
                "stock_fallback_from_option_research": bool(option),
                "rejected_option_contract_symbol": contract_symbol if option else "",
                "rejected_option_reason": _safe_str(
                    queued_trade.get("option_reason")
                    or queued_trade.get("execution_reason")
                    or option.get("execution_reason"),
                    "",
                ),
            }
        )

    return record


def _normalize_execution_result(
    queued_trade: Dict[str, Any],
    raw_result: Dict[str, Any],
) -> Dict[str, Any]:
    queued_trade = _safe_dict(queued_trade)
    raw_result = _safe_dict(raw_result)

    vehicle_selected = _upper(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle"),
        "STOCK",
    )

    normalized = dict(raw_result)

    status = _upper(raw_result.get("status") or raw_result.get("order_status"), "FILLED")
    if status in {"EXECUTED", "SUCCESS", "COMPLETE", "COMPLETED"}:
        status = "FILLED"
    normalized["status"] = status

    execution_record = _normalize_execution_record(queued_trade, raw_result)

    fill_price = _safe_float(raw_result.get("fill_price", execution_record.get("fill_price", 0.0)), 0.0)
    if fill_price <= 0:
        fill_price = _safe_float(execution_record.get("fill_price"), 0.0)

    filled_quantity = _safe_int(
        raw_result.get("filled_quantity", execution_record.get("filled_quantity", 0)),
        0,
    )

    actual_cost = _safe_float(raw_result.get("actual_cost"), 0.0)
    if actual_cost <= 0 and fill_price > 0 and filled_quantity > 0:
        if vehicle_selected == "OPTION":
            actual_cost = round(fill_price * OPTION_CONTRACT_MULTIPLIER * filled_quantity + 1.0, 4)
        else:
            actual_cost = round(fill_price * filled_quantity + 1.0, 4)

    normalized["fill_price"] = _round4(fill_price)
    normalized["filled_quantity"] = filled_quantity
    normalized["actual_cost"] = _round4(actual_cost)
    normalized["reason"] = _safe_str(raw_result.get("reason"), "executed")
    normalized["reason_code"] = _safe_str(raw_result.get("reason_code"), "executed")
    normalized["execution_record"] = execution_record

    broker_order_id = _safe_str(raw_result.get("broker_order_id"), "")
    if not broker_order_id:
        broker_order_id = (
            f"SIM-{execution_record.get('symbol', 'UNKNOWN')}-"
            f"{_safe_str(execution_record.get('opened_at'), _now_iso()).replace(':', '').replace('-', '').replace('.', '')}"
        )
    normalized["broker_order_id"] = broker_order_id

    return normalized


def build_queued_trade_payload(
    lifecycle_obj: Dict[str, Any],
    *,
    mode: str = "paper",
) -> Dict[str, Any]:
    lifecycle_obj = deepcopy(_safe_dict(lifecycle_obj))
    raw = deepcopy(_safe_dict(lifecycle_obj.get("raw")))

    trading_mode = normalize_mode(
        mode
        or lifecycle_obj.get("trading_mode")
        or lifecycle_obj.get("execution_mode")
        or lifecycle_obj.get("mode")
        or raw.get("trading_mode")
        or raw.get("execution_mode")
        or raw.get("mode")
        or "paper"
    )

    mode_context = _resolve_mode_context(
        trading_mode,
        lifecycle_obj.get("mode_context") or raw.get("mode_context"),
    )

    symbol = _norm_symbol(lifecycle_obj.get("symbol") or raw.get("symbol"))
    strategy = _upper(lifecycle_obj.get("strategy") or raw.get("strategy"), "CALL")

    timestamp = _safe_str(
        lifecycle_obj.get("updated_at")
        or lifecycle_obj.get("timestamp")
        or raw.get("timestamp"),
        _now_iso(),
    )

    trade_id = _safe_str(
        lifecycle_obj.get("trade_id") or raw.get("trade_id"),
        _derive_trade_id(symbol, strategy, timestamp),
    )

    vehicle_selected = _normalize_selected_vehicle(lifecycle_obj, raw)
    contract, option = _normalize_contract_payload(lifecycle_obj, raw)

    underlying_price = _extract_underlying_price(lifecycle_obj, raw)
    option_price = _extract_option_fill_price(
        option,
        _safe_float(
            lifecycle_obj.get(
                "option_entry",
                lifecycle_obj.get(
                    "entry_premium",
                    lifecycle_obj.get("premium_entry", raw.get("option_entry", 0.0)),
                ),
            ),
            0.0,
        ),
    )

    payload: Dict[str, Any] = {}
    payload.update(raw)
    payload.update(lifecycle_obj)

    payload["symbol"] = symbol
    payload["strategy"] = strategy
    payload["trade_id"] = trade_id
    payload["timestamp"] = timestamp

    payload["trading_mode"] = trading_mode
    payload["execution_mode"] = trading_mode
    payload["mode"] = trading_mode
    payload["mode_context"] = mode_context

    payload["vehicle_selected"] = vehicle_selected
    payload["selected_vehicle"] = vehicle_selected
    payload["vehicle"] = vehicle_selected

    payload["research_approved"] = _safe_bool(
        lifecycle_obj.get("research_approved", raw.get("research_approved", True)),
        True,
    )
    payload["execution_ready"] = _safe_bool(
        lifecycle_obj.get("execution_ready", raw.get("execution_ready", True)),
        True,
    )
    payload["selected_for_execution"] = _safe_bool(
        lifecycle_obj.get("selected_for_execution", raw.get("selected_for_execution", False)),
        False,
    )

    payload["lifecycle_stage"] = _safe_str(
        lifecycle_obj.get("lifecycle_stage", raw.get("lifecycle_stage", "SELECTED")),
        "SELECTED",
    )
    payload["final_reason"] = _safe_str(
        lifecycle_obj.get("final_reason", raw.get("final_reason", "selected_for_execution")),
        "selected_for_execution",
    )
    payload["final_reason_code"] = _safe_str(
        lifecycle_obj.get("final_reason_code", raw.get("final_reason_code", "selected_for_execution")),
        "selected_for_execution",
    )
    payload["decision_reason"] = _safe_str(
        lifecycle_obj.get("decision_reason", raw.get("decision_reason", payload["final_reason"])),
        payload["final_reason"],
    )
    payload["decision_reason_code"] = _safe_str(
        lifecycle_obj.get("decision_reason_code", raw.get("decision_reason_code", payload["final_reason_code"])),
        payload["final_reason_code"],
    )

    payload["capital_required"] = _round4(lifecycle_obj.get("capital_required", raw.get("capital_required", 0.0)))
    payload["minimum_trade_cost"] = _round4(lifecycle_obj.get("minimum_trade_cost", raw.get("minimum_trade_cost", 0.0)))
    payload["capital_available"] = _round4(lifecycle_obj.get("capital_available", raw.get("capital_available", 0.0)))

    payload["contracts"] = _safe_int(lifecycle_obj.get("contracts", raw.get("contracts", 0)), 0)
    payload["shares"] = _safe_int(lifecycle_obj.get("shares", raw.get("shares", 0)), 0)

    if vehicle_selected == "OPTION" and payload["contracts"] <= 0:
        payload["contracts"] = 1
    if vehicle_selected == "STOCK" and payload["shares"] <= 0:
        payload["shares"] = 1

    if vehicle_selected == "OPTION":
        payload["shares"] = 0
    if vehicle_selected == "STOCK":
        payload["contracts"] = 0

    payload["contract"] = deepcopy(contract)
    payload["option"] = deepcopy(option)

    payload["underlying_price"] = _round4(underlying_price)
    payload["current_underlying_price"] = _round4(underlying_price)
    payload["stock_price"] = _round4(underlying_price)

    payload["option_contract_score"] = _round4(
        lifecycle_obj.get(
            "option_contract_score",
            raw.get("option_contract_score", option.get("contract_score", 0.0)),
        )
    )

    if vehicle_selected == "OPTION":
        contract_symbol = _contract_symbol(option, payload.get("contract_symbol") or payload.get("option_symbol"))
        expiry = _option_expiry(option, payload.get("expiry") or payload.get("expiration"))
        right = _option_right(option, strategy, payload.get("right"))

        payload["contract_symbol"] = contract_symbol
        payload["option_symbol"] = contract_symbol
        payload["expiry"] = expiry
        payload["expiration"] = expiry
        payload["strike"] = _round4(payload.get("strike", option.get("strike", 0.0)))
        payload["right"] = right

        payload["mark"] = _round4(
            payload.get(
                "mark",
                option.get(
                    "mark",
                    option.get("selected_price_reference", option.get("price_reference", option.get("last", option_price))),
                ),
            ),
            option_price,
        )
        payload["bid"] = _round4(payload.get("bid", option.get("bid", 0.0)))
        payload["ask"] = _round4(payload.get("ask", option.get("ask", 0.0)))
        payload["last"] = _round4(payload.get("last", option.get("last", option_price)), option_price)
        payload["open_interest"] = _safe_int(
            payload.get("open_interest", option.get("open_interest", option.get("openInterest", 0))),
            0,
        )
        payload["volume"] = _safe_int(payload.get("volume", option.get("volume", 0)), 0)
        payload["dte"] = _safe_int(payload.get("dte", option.get("dte", option.get("daysToExpiration", 0))), 0)

        payload["option_entry"] = _round4(option_price)
        payload["entry"] = _round4(option_price)
        payload["entry_price"] = _round4(option_price)
        payload["entry_premium"] = _round4(option_price)
        payload["premium_entry"] = _round4(option_price)
        payload["requested_price"] = _round4(option_price)

        payload["current_price"] = _round4(option_price)
        payload["current_premium"] = _round4(option_price)
        payload["premium_current"] = _round4(option_price)
        payload["current_option_mark"] = _round4(option_price)
        payload["option_current_price"] = _round4(option_price)

        option_stop = _option_stop(option_price, payload.get("option_stop") or payload.get("stop"))
        option_target = _option_target(option_price, payload.get("option_target") or payload.get("target"))

        payload["stop"] = option_stop
        payload["target"] = option_target
        payload["option_stop"] = option_stop
        payload["option_target"] = option_target

        payload["monitoring_price_type"] = "OPTION_PREMIUM"
        payload["monitoring_mode"] = "OPTION_PREMIUM"
        payload["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        payload["underlying_price_used_for_close_decision"] = False

        if payload["capital_required"] <= 0 and option_price > 0:
            payload["capital_required"] = _round4(option_price * OPTION_CONTRACT_MULTIPLIER * payload["contracts"])
        if payload["minimum_trade_cost"] <= 0 and option_price > 0:
            payload["minimum_trade_cost"] = _round4(option_price * OPTION_CONTRACT_MULTIPLIER * payload["contracts"] + 1.0)

    elif vehicle_selected == "STOCK":
        entry_price = _round4(underlying_price)

        payload["entry"] = entry_price
        payload["entry_price"] = entry_price
        payload["requested_price"] = entry_price
        payload["current_price"] = entry_price

        payload["stop"] = _stock_stop(entry_price, payload.get("stop"))
        payload["target"] = _stock_target(entry_price, payload.get("target"))

        payload["entry_premium"] = None
        payload["premium_entry"] = None
        payload["option_entry"] = None
        payload["current_premium"] = None
        payload["premium_current"] = None
        payload["current_option_mark"] = None
        payload["option_current_price"] = None
        payload["option_stop"] = None
        payload["option_target"] = None

        payload["monitoring_price_type"] = "UNDERLYING"
        payload["monitoring_mode"] = "UNDERLYING"
        payload["price_review_basis"] = "UNDERLYING"
        payload["underlying_price_used_for_close_decision"] = True

        # Do not let stale option identifiers make stock fallback look like an option.
        if option:
            payload["stock_fallback_from_option_research"] = True
            payload["rejected_option_contract_symbol"] = _contract_symbol(option)
            payload["rejected_option_reason"] = _safe_str(
                payload.get("option_reason")
                or payload.get("execution_reason")
                or option.get("execution_reason"),
                "",
            )

        payload["contract_symbol"] = ""
        payload["option_symbol"] = ""
        payload["expiry"] = ""
        payload["expiration"] = ""
        payload["strike"] = 0.0
        payload["right"] = strategy

        if payload["capital_required"] <= 0 and entry_price > 0:
            payload["capital_required"] = _round4(entry_price * payload["shares"])
        if payload["minimum_trade_cost"] <= 0 and entry_price > 0:
            payload["minimum_trade_cost"] = _round4(entry_price * payload["shares"] + 1.0)

    else:
        payload["monitoring_price_type"] = "RESEARCH_ONLY"
        payload["monitoring_mode"] = "RESEARCH_ONLY"
        payload["price_review_basis"] = "RESEARCH_ONLY"
        payload["underlying_price_used_for_close_decision"] = False

    payload["lifecycle"] = deepcopy(lifecycle_obj)

    payload["open_trade_state_preview"] = build_open_trade_state(
        payload,
        lifecycle=lifecycle_obj,
        execution_result={},
        mode=trading_mode,
        mode_context=mode_context,
    )

    return payload


def _simulate_fill(
    queued_trade: Dict[str, Any],
) -> Dict[str, Any]:
    queued_trade = _safe_dict(queued_trade)

    vehicle_selected = _upper(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle"),
        "STOCK",
    )
    option = _safe_dict(queued_trade.get("option"))
    symbol = _norm_symbol(queued_trade.get("symbol"))

    if vehicle_selected == "OPTION":
        fill_price = _extract_option_fill_price(
            option,
            _safe_float(
                queued_trade.get(
                    "option_entry",
                    queued_trade.get("entry_premium", queued_trade.get("premium_entry", queued_trade.get("entry", 0.0))),
                ),
                0.0,
            ),
        )
        quantity = max(1, _safe_int(queued_trade.get("contracts", queued_trade.get("quantity", 1)), 1))
        actual_cost = round(fill_price * OPTION_CONTRACT_MULTIPLIER * quantity, 4)
    else:
        fill_price = _extract_underlying_price(queued_trade)
        quantity = max(1, _safe_int(queued_trade.get("shares", queued_trade.get("size", queued_trade.get("quantity", 1))), 1))
        actual_cost = round(fill_price * quantity, 4)

    commission = 1.0
    actual_cost = round(actual_cost + commission, 4)
    opened_at = _now_iso()

    execution_record = _normalize_execution_record(
        queued_trade,
        {
            "fill_price": fill_price,
            "filled_quantity": quantity,
            "opened_at": opened_at,
            "commission": commission,
        },
    )

    return {
        "status": "FILLED",
        "fill_price": _round4(fill_price),
        "filled_quantity": quantity,
        "actual_cost": actual_cost,
        "broker_order_id": f"SIM-{symbol}-{opened_at.replace(':', '').replace('-', '').replace('.', '')}",
        "reason": "executed",
        "reason_code": "executed",
        "execution_record": execution_record,
    }


def execute_via_adapter(
    *,
    queued_trade: Dict[str, Any],
    portfolio_context: Dict[str, Any] | None = None,
    max_open_positions: int = 5,
    current_open_positions: int = 0,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
    broker_adapter: Any = None,
) -> Dict[str, Any]:
    queued_trade = deepcopy(_safe_dict(queued_trade))
    portfolio_context = _safe_dict(portfolio_context)

    trading_mode = normalize_mode(
        queued_trade.get("trading_mode")
        or queued_trade.get("execution_mode")
        or queued_trade.get("mode")
        or "paper"
    )
    mode_context = _resolve_mode_context(trading_mode, queued_trade.get("mode_context"))

    vehicle_selected = _upper(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle"),
        "RESEARCH_ONLY",
    )

    capital_available = _safe_float(
        queued_trade.get(
            "capital_available",
            portfolio_context.get("cash_available", portfolio_context.get("cash", portfolio_context.get("buying_power", 0.0))),
        ),
        0.0,
    )

    if current_open_positions >= max_open_positions:
        guard = {
            "blocked": True,
            "reason": "Max open positions reached.",
            "reason_code": "max_open_positions",
            "warnings": [],
            "details": {
                "current_open_positions": current_open_positions,
                "max_open_positions": max_open_positions,
            },
        }
    else:
        guard = validate_selected_trade_for_execution(
            queued_trade,
            capital_available=capital_available,
            trading_mode=trading_mode,
            current_open_positions=current_open_positions,
            max_open_positions=max_open_positions,
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_healthy=True,
        )

    lifecycle_after = deepcopy(_safe_dict(queued_trade.get("lifecycle")))

    lifecycle_after.update(
        {
            "trade_id": _safe_str(queued_trade.get("trade_id"), ""),
            "symbol": _norm_symbol(queued_trade.get("symbol")),
            "strategy": _upper(queued_trade.get("strategy"), "CALL"),
            "vehicle_selected": vehicle_selected,
            "selected_vehicle": vehicle_selected,
            "vehicle": vehicle_selected,
            "trading_mode": trading_mode,
            "execution_mode": trading_mode,
            "mode": trading_mode,
            "mode_context": mode_context,
            "capital_available": _round4(capital_available),
            "contract": deepcopy(_safe_dict(queued_trade.get("contract"))),
            "option": deepcopy(_safe_dict(queued_trade.get("option"))),
            "underlying_price": _extract_underlying_price(queued_trade),
            "current_underlying_price": _extract_underlying_price(queued_trade),
            "monitoring_price_type": _safe_str(queued_trade.get("monitoring_price_type"), ""),
            "monitoring_mode": _safe_str(queued_trade.get("monitoring_mode"), queued_trade.get("monitoring_price_type", "")),
            "price_review_basis": _safe_str(queued_trade.get("price_review_basis"), ""),
            "underlying_price_used_for_close_decision": _safe_bool(
                queued_trade.get("underlying_price_used_for_close_decision"),
                vehicle_selected == "STOCK",
            ),
            "readiness_score": _round4(queued_trade.get("readiness_score", 0.0)),
            "promotion_score": _round4(queued_trade.get("promotion_score", 0.0)),
            "rebuild_pressure": _round4(queued_trade.get("rebuild_pressure", 0.0)),
            "v2_score": _round4(queued_trade.get("v2_score", 0.0)),
            "v2_reason": _safe_str(queued_trade.get("v2_reason"), ""),
            "v2_vehicle_bias": _safe_str(queued_trade.get("v2_vehicle_bias"), ""),
        }
    )

    if _safe_bool(guard.get("blocked"), False):
        reason = _safe_str(guard.get("reason"), "Execution blocked.")
        reason_code = _safe_str(guard.get("reason_code"), "execution_blocked")

        lifecycle_after["execution_ready"] = False
        lifecycle_after["selected_for_execution"] = False
        lifecycle_after["lifecycle_stage"] = "EXECUTION_BLOCKED"
        lifecycle_after["final_decision"] = "REJECT"
        lifecycle_after["final_reason"] = reason
        lifecycle_after["final_reason_code"] = reason_code
        lifecycle_after["execution_reason"] = reason
        lifecycle_after["execution_reason_code"] = reason_code
        lifecycle_after["blocked_at"] = "execution_handoff"

        return {
            "success": False,
            "status": "REJECTED",
            "symbol": _norm_symbol(queued_trade.get("symbol")),
            "selected_vehicle": vehicle_selected,
            "guard": {
                "decision": "REJECT",
                "guard_reason": reason,
                "guard_reason_code": reason_code,
                "warnings": _safe_list(guard.get("warnings")),
                "guard_details": _safe_dict(guard.get("details")),
            },
            "execution_result": {},
            "lifecycle_after": lifecycle_after,
            "trading_mode": trading_mode,
            "mode_context": mode_context,
        }

    if callable(getattr(broker_adapter, "execute_trade", None)):
        raw_execution_result = _safe_dict(broker_adapter.execute_trade(queued_trade))
    else:
        raw_execution_result = _simulate_fill(queued_trade)

    execution_result = _normalize_execution_result(queued_trade, raw_execution_result)

    fill_price = _safe_float(execution_result.get("fill_price"), 0.0)
    filled_quantity = _safe_int(execution_result.get("filled_quantity"), 0)

    if fill_price <= 0 or filled_quantity <= 0:
        reason = "Execution returned invalid fill payload."
        reason_code = "invalid_fill_payload"

        lifecycle_after["execution_ready"] = False
        lifecycle_after["selected_for_execution"] = False
        lifecycle_after["lifecycle_stage"] = "EXECUTION_BLOCKED"
        lifecycle_after["final_decision"] = "REJECT"
        lifecycle_after["final_reason"] = reason
        lifecycle_after["final_reason_code"] = reason_code
        lifecycle_after["execution_reason"] = reason
        lifecycle_after["execution_reason_code"] = reason_code
        lifecycle_after["blocked_at"] = "execution_handoff"
        lifecycle_after["execution_result"] = execution_result

        return {
            "success": False,
            "status": "REJECTED",
            "symbol": _norm_symbol(queued_trade.get("symbol")),
            "selected_vehicle": vehicle_selected,
            "guard": {
                "decision": "REJECT",
                "guard_reason": reason,
                "guard_reason_code": reason_code,
                "warnings": _safe_list(guard.get("warnings")),
                "guard_details": _safe_dict(guard.get("details")),
            },
            "execution_result": execution_result,
            "lifecycle_after": lifecycle_after,
            "trading_mode": trading_mode,
            "mode_context": mode_context,
        }

    execution_record = _safe_dict(execution_result.get("execution_record"))

    lifecycle_after["execution_ready"] = True
    lifecycle_after["selected_for_execution"] = True
    lifecycle_after["lifecycle_stage"] = "ENTERED"
    lifecycle_after["final_decision"] = "APPROVE"
    lifecycle_after["final_reason"] = "Position entered."
    lifecycle_after["final_reason_code"] = "entered"
    lifecycle_after["execution_reason"] = "Position entered."
    lifecycle_after["execution_reason_code"] = "entered"
    lifecycle_after["fill_price"] = _round4(fill_price)
    lifecycle_after["filled_quantity"] = filled_quantity
    lifecycle_after["entered_at"] = _safe_str(execution_record.get("opened_at"), _now_iso())
    lifecycle_after["opened_at"] = _safe_str(execution_record.get("opened_at"), lifecycle_after["entered_at"])
    lifecycle_after["blocked_at"] = ""
    lifecycle_after["execution_result"] = execution_result
    lifecycle_after["execution_record"] = execution_record

    if vehicle_selected == "OPTION":
        entry_premium = _round4(fill_price)

        lifecycle_after["entry"] = entry_premium
        lifecycle_after["entry_price"] = entry_premium
        lifecycle_after["entry_premium"] = entry_premium
        lifecycle_after["premium_entry"] = entry_premium
        lifecycle_after["option_entry"] = entry_premium

        lifecycle_after["current_price"] = entry_premium
        lifecycle_after["current_premium"] = entry_premium
        lifecycle_after["premium_current"] = entry_premium
        lifecycle_after["current_option_mark"] = entry_premium
        lifecycle_after["option_current_price"] = entry_premium

        option_stop = _option_stop(entry_premium, queued_trade.get("option_stop") or queued_trade.get("stop"))
        option_target = _option_target(entry_premium, queued_trade.get("option_target") or queued_trade.get("target"))

        lifecycle_after["stop"] = option_stop
        lifecycle_after["target"] = option_target
        lifecycle_after["option_stop"] = option_stop
        lifecycle_after["option_target"] = option_target

        lifecycle_after["shares"] = 0
        lifecycle_after["contracts"] = max(1, _safe_int(execution_record.get("contracts", filled_quantity), filled_quantity))

        lifecycle_after["monitoring_price_type"] = "OPTION_PREMIUM"
        lifecycle_after["monitoring_mode"] = "OPTION_PREMIUM"
        lifecycle_after["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        lifecycle_after["underlying_price_used_for_close_decision"] = False

    elif vehicle_selected == "STOCK":
        entry_price = _round4(fill_price)

        lifecycle_after["entry"] = entry_price
        lifecycle_after["entry_price"] = entry_price
        lifecycle_after["current_price"] = entry_price

        lifecycle_after["entry_premium"] = None
        lifecycle_after["premium_entry"] = None
        lifecycle_after["option_entry"] = None
        lifecycle_after["current_premium"] = None
        lifecycle_after["premium_current"] = None
        lifecycle_after["current_option_mark"] = None
        lifecycle_after["option_current_price"] = None
        lifecycle_after["option_stop"] = None
        lifecycle_after["option_target"] = None

        lifecycle_after["stop"] = _stock_stop(entry_price, queued_trade.get("stop"))
        lifecycle_after["target"] = _stock_target(entry_price, queued_trade.get("target"))

        lifecycle_after["shares"] = max(1, _safe_int(execution_record.get("shares", filled_quantity), filled_quantity))
        lifecycle_after["contracts"] = 0

        lifecycle_after["monitoring_price_type"] = "UNDERLYING"
        lifecycle_after["monitoring_mode"] = "UNDERLYING"
        lifecycle_after["price_review_basis"] = "UNDERLYING"
        lifecycle_after["underlying_price_used_for_close_decision"] = True

    if execution_record:
        if vehicle_selected == "OPTION":
            lifecycle_after["contract_symbol"] = _safe_str(execution_record.get("contract_symbol"), "")
            lifecycle_after["option_symbol"] = _safe_str(execution_record.get("option_symbol") or execution_record.get("contract_symbol"), "")
            lifecycle_after["expiry"] = _safe_str(execution_record.get("expiry"), "")
            lifecycle_after["expiration"] = _safe_str(execution_record.get("expiration") or execution_record.get("expiry"), "")
            lifecycle_after["strike"] = _round4(execution_record.get("strike", 0.0))
            lifecycle_after["right"] = _safe_str(execution_record.get("right"), "")
            lifecycle_after["mark"] = _round4(execution_record.get("mark", fill_price), fill_price)
            lifecycle_after["bid"] = _round4(execution_record.get("bid", 0.0))
            lifecycle_after["ask"] = _round4(execution_record.get("ask", 0.0))
            lifecycle_after["last"] = _round4(execution_record.get("last", fill_price), fill_price)
            lifecycle_after["open_interest"] = _safe_int(execution_record.get("open_interest"), 0)
            lifecycle_after["volume"] = _safe_int(execution_record.get("volume"), 0)
            lifecycle_after["dte"] = _safe_int(execution_record.get("dte"), 0)
        else:
            lifecycle_after["contract_symbol"] = ""
            lifecycle_after["option_symbol"] = ""
            lifecycle_after["expiry"] = ""
            lifecycle_after["expiration"] = ""
            lifecycle_after["strike"] = 0.0
            lifecycle_after["right"] = _upper(queued_trade.get("strategy"), "CALL")

            if _safe_dict(queued_trade.get("option")):
                lifecycle_after["stock_fallback_from_option_research"] = True
                lifecycle_after["rejected_option_contract_symbol"] = _contract_symbol(_safe_dict(queued_trade.get("option")))
                lifecycle_after["rejected_option_reason"] = _safe_str(
                    queued_trade.get("option_reason")
                    or queued_trade.get("execution_reason")
                    or _safe_dict(queued_trade.get("option")).get("execution_reason"),
                    "",
                )

        lifecycle_after["underlying_price"] = _round4(
            execution_record.get("underlying_price", lifecycle_after.get("underlying_price", 0.0))
        )
        lifecycle_after["current_underlying_price"] = _round4(
            execution_record.get("current_underlying_price", lifecycle_after.get("underlying_price", 0.0))
        )

    return {
        "success": True,
        "status": "EXECUTED",
        "symbol": _norm_symbol(queued_trade.get("symbol")),
        "selected_vehicle": vehicle_selected,
        "guard": {
            "decision": "APPROVE",
            "guard_reason": "Execution completed successfully.",
            "guard_reason_code": "executed",
            "warnings": _safe_list(guard.get("warnings")),
            "guard_details": _safe_dict(guard.get("details")),
        },
        "execution_result": execution_result,
        "lifecycle_after": lifecycle_after,
        "trading_mode": trading_mode,
        "mode_context": mode_context,
    }


def summarize_execution_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(packet)
    guard = _safe_dict(packet.get("guard"))
    execution_result = _safe_dict(packet.get("execution_result"))
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    selected_vehicle = _upper(packet.get("selected_vehicle"), "RESEARCH_ONLY")

    return {
        "success": _safe_bool(packet.get("success"), False),
        "status": _safe_str(packet.get("status"), ""),
        "symbol": _norm_symbol(packet.get("symbol")),
        "selected_vehicle": selected_vehicle,
        "guard_reason": _safe_str(guard.get("guard_reason"), ""),
        "guard_reason_code": _safe_str(guard.get("guard_reason_code"), ""),
        "guard_warnings": _safe_list(guard.get("warnings")),
        "fill_price": _round4(execution_result.get("fill_price", 0.0)),
        "filled_quantity": _safe_int(execution_result.get("filled_quantity"), 0),
        "actual_cost": _round4(execution_result.get("actual_cost", 0.0)),
        "trade_id": _safe_str(lifecycle_after.get("trade_id"), ""),
        "lifecycle_stage_after": _safe_str(lifecycle_after.get("lifecycle_stage"), ""),
        "trading_mode": _safe_str(packet.get("trading_mode"), ""),
        "monitoring_price_type": _safe_str(lifecycle_after.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(lifecycle_after.get("price_review_basis"), ""),
        "contract_symbol": _safe_str(
            lifecycle_after.get("contract_symbol")
            or execution_record.get("contract_symbol"),
            "",
        ),
        "entry_premium": lifecycle_after.get("entry_premium"),
        "underlying_price": lifecycle_after.get("underlying_price"),
        "underlying_price_used_for_close_decision": _safe_bool(
            lifecycle_after.get("underlying_price_used_for_close_decision"),
            selected_vehicle == "STOCK",
        ),
    }


__all__ = [
    "build_queued_trade_payload",
    "execute_via_adapter",
    "summarize_execution_packet",
]
