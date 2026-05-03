from __future__ import annotations

"""
Observatory Execution Loop

Purpose:
    Own the execution step after candidate selection.

Why this file exists:
    execute_trades() used to live inside the executive loop, which made execution
    persistence too muddy. The system could select an OPTION contract, then save
    the open position as a STOCK shell carrying option metadata. That created
    downstream monitor/review/close bugs.

Canonical rule:
    The selected vehicle controls the saved open-position shape.

    OPTION:
        - contracts > 0
        - shares = 0
        - entry/current_price are option premium values
        - underlying_price is context only
        - monitoring_price_type = OPTION_PREMIUM
        - price_review_basis = OPTION_PREMIUM_ONLY

    STOCK:
        - shares > 0
        - contracts = 0
        - entry/current_price are underlying stock values
        - monitoring_price_type = UNDERLYING
        - price_review_basis = STOCK_PRICE

Compatibility:
    - Keeps execute_trades() public API.
    - Keeps execute_via_adapter() handoff.
    - Keeps add_position() persistence.
    - Adds strong normalization before add_position().
"""

import json
import math
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from engine.execution_handoff import execute_via_adapter, summarize_execution_packet
from engine.paper_portfolio import add_position, open_count


OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

DEFAULT_OPTION_STOP_LOSS_PCT = 0.35
DEFAULT_OPTION_TARGET_GAIN_PCT = 0.60

DEFAULT_STOCK_STOP_LOSS_PCT = 0.03
DEFAULT_STOCK_TARGET_GAIN_PCT = 0.10


# =============================================================================
# Safe helpers
# =============================================================================

def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _upper(value: Any, default: str = "") -> str:
    text = _safe_str(value, default).upper()
    return text if text else default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return float(default)
        return number
    except Exception:
        return float(default)


def _safe_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return None
            value = cleaned
        number = float(value)
        if math.isnan(number) or math.isinf(number):
            return None
        return number
    except Exception:
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return int(default)
        if isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _safe_bool(value: Any, default: bool = False) -> bool:
    try:
        if value is None:
            return bool(default)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1", "y"}:
                return True
            if lowered in {"false", "no", "0", "n"}:
                return False
        return bool(value)
    except Exception:
        return bool(default)


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _load_json(path: str, default: Any) -> Any:
    try:
        p = Path(path)
        if not p.exists():
            return default
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: str, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _first_present(payload: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    payload = _safe_dict(payload)
    for key in keys:
        if key in payload and payload.get(key) not in (None, ""):
            return payload.get(key)
    return default


def _first_float(payload: Dict[str, Any], keys: List[str]) -> Optional[float]:
    payload = _safe_dict(payload)
    for key in keys:
        value = _safe_optional_float(payload.get(key))
        if value is not None:
            return value
    return None


def _first_str(payload: Dict[str, Any], keys: List[str], default: str = "") -> str:
    payload = _safe_dict(payload)
    for key in keys:
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


# =============================================================================
# Vehicle / contract extraction
# =============================================================================

def _selected_vehicle(payload: Dict[str, Any]) -> str:
    payload = _safe_dict(payload)

    raw = _upper(
        payload.get(
            "vehicle_selected",
            payload.get(
                "selected_vehicle",
                payload.get("vehicle", payload.get("asset_type", payload.get("instrument_type", ""))),
            ),
        ),
        "",
    )

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return VEHICLE_OPTION

    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return VEHICLE_STOCK

    if raw in {"RESEARCH_ONLY", "RESEARCH"}:
        return VEHICLE_RESEARCH_ONLY

    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))
    contract_symbol = _first_str(
        payload,
        ["contract_symbol", "option_symbol", "option_contract_symbol", "selected_contract_symbol", "occ_symbol"],
        "",
    )

    if option or contract or contract_symbol:
        contracts = _safe_int(payload.get("contracts", payload.get("contract_count", 0)), 0)
        shares = _safe_int(payload.get("shares", payload.get("quantity", payload.get("qty", 0))), 0)

        if contracts > 0 or shares <= 0:
            return VEHICLE_OPTION

    return VEHICLE_STOCK


def _direction(strategy: Any) -> str:
    text = _upper(strategy, "CALL")
    if "PUT" in text or "SHORT" in text:
        return "SHORT"
    return "LONG"


def _extract_option_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = _safe_dict(payload)

    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))
    selected_contract = _safe_dict(payload.get("selected_contract"))
    best_option = _safe_dict(payload.get("best_option"))
    option_preview = _safe_dict(payload.get("best_option_preview"))

    merged: Dict[str, Any] = {}
    merged.update(option_preview)
    merged.update(best_option)
    merged.update(selected_contract)
    merged.update(contract)
    merged.update(option)

    contract_symbol = (
        _first_str(
            payload,
            [
                "contract_symbol",
                "option_symbol",
                "option_contract_symbol",
                "selected_contract_symbol",
                "occ_symbol",
            ],
            "",
        )
        or _first_str(
            merged,
            [
                "contractSymbol",
                "contract_symbol",
                "option_symbol",
                "selected_contract_symbol",
                "occ_symbol",
                "symbol",
            ],
            "",
        )
    )

    expiry = (
        _first_str(
            payload,
            ["expiry", "expiration", "expiration_date", "contract_expiry"],
            "",
        )
        or _first_str(
            merged,
            ["expiration", "expiry", "expiration_date", "contract_expiry"],
            "",
        )
    )

    right = _upper(
        _first_str(
            payload,
            ["right", "option_type", "call_put", "contract_right"],
            "",
        )
        or _first_str(
            merged,
            ["right", "option_type", "call_put", "contract_right"],
            "",
        ),
        "",
    )

    if right in {"C", "CALLS"}:
        right = "CALL"
    elif right in {"P", "PUTS"}:
        right = "PUT"

    strike = _first_float(payload, ["strike", "strike_price", "contract_strike"])
    if strike is None:
        strike = _first_float(merged, ["strike", "strike_price", "contract_strike"])

    bid = _first_float(payload, ["option_bid", "bid"])
    if bid is None:
        bid = _first_float(merged, ["bid"])

    ask = _first_float(payload, ["option_ask", "ask"])
    if ask is None:
        ask = _first_float(merged, ["ask"])

    last = _first_float(payload, ["option_last", "last"])
    if last is None:
        last = _first_float(merged, ["last", "last_price"])

    mark = _first_float(
        payload,
        [
            "current_option_mark",
            "option_current_mark",
            "option_mark",
            "mark",
            "current_premium",
            "premium_current",
            "selected_price_reference",
            "price_reference",
        ],
    )
    if mark is None:
        mark = _first_float(
            merged,
            [
                "current_option_mark",
                "option_current_mark",
                "option_mark",
                "current_mark",
                "mark",
                "mid",
                "selected_price_reference",
                "price_reference",
            ],
        )

    selected_price_reference = _first_float(
        payload,
        ["selected_price_reference", "price_reference", "option_price_reference", "fill_price", "executed_price"],
    )
    if selected_price_reference is None:
        selected_price_reference = _first_float(
            merged,
            ["selected_price_reference", "price_reference", "fill_price", "executed_price", "mark", "ask", "last"],
        )

    return {
        "symbol": _norm_symbol(payload.get("symbol", merged.get("underlying_symbol", merged.get("symbol", "")))),
        "contractSymbol": contract_symbol,
        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "expiration": expiry,
        "expiry": expiry,
        "right": right,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "selected_price_reference": selected_price_reference,
        "price_reference": selected_price_reference if selected_price_reference is not None else mark,
        "volume": _safe_int(payload.get("volume", merged.get("volume")), 0),
        "open_interest": _safe_int(payload.get("open_interest", merged.get("open_interest", merged.get("oi"))), 0),
        "implied_volatility": _safe_float(
            payload.get("implied_volatility", merged.get("implied_volatility")),
            0.0,
        ),
        "in_the_money": _safe_bool(payload.get("in_the_money", merged.get("in_the_money")), False),
        "spread": _safe_float(payload.get("spread", merged.get("spread")), 0.0),
        "spread_pct": _safe_float(payload.get("spread_pct", merged.get("spread_pct")), 0.0),
        "distance_pct": _safe_float(payload.get("distance_pct", merged.get("distance_pct")), 0.0),
        "contract_score": _safe_float(
            payload.get("contract_score", merged.get("contract_score")),
            0.0,
        ),
        "trade_intent": _safe_str(payload.get("trade_intent", merged.get("trade_intent")), ""),
        "dte": _safe_int(payload.get("dte", merged.get("dte")), 0),
        "monitoring_mode": "OPTION_PREMIUM",
        "is_executable": _safe_bool(payload.get("is_executable", merged.get("is_executable")), True),
        "execution_reason": _safe_str(payload.get("execution_reason", merged.get("execution_reason")), "ok"),
        "contract_notes": _safe_list(payload.get("contract_notes", merged.get("contract_notes"))),
    }


def _mid_from_bid_ask(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0:
        return None
    if ask < bid:
        return None
    return round((bid + ask) / 2.0, 4)


def _option_premium(payload: Dict[str, Any], execution_result: Dict[str, Any], contract: Dict[str, Any]) -> float:
    direct_candidates = [
        execution_result.get("fill_price"),
        execution_result.get("executed_price"),
        execution_result.get("average_fill_price"),
        execution_result.get("avg_fill_price"),
        payload.get("fill_price"),
        payload.get("executed_price"),
        payload.get("entry_premium"),
        payload.get("premium_entry"),
        payload.get("option_entry"),
        payload.get("option_entry_price"),
        payload.get("current_option_mark"),
        payload.get("current_premium"),
        payload.get("selected_price_reference"),
        payload.get("price_reference"),
        contract.get("selected_price_reference"),
        contract.get("price_reference"),
        contract.get("mark"),
        contract.get("last"),
    ]

    for candidate in direct_candidates:
        value = _safe_float(candidate, 0.0)
        if value > 0:
            return round(value, 4)

    mid = _mid_from_bid_ask(
        _safe_optional_float(contract.get("bid")),
        _safe_optional_float(contract.get("ask")),
    )
    if mid is not None and mid > 0:
        return round(mid, 4)

    ask = _safe_float(contract.get("ask"), 0.0)
    if ask > 0:
        return round(ask, 4)

    return 0.0


def _underlying_price(payload: Dict[str, Any], execution_result: Dict[str, Any]) -> float:
    value = _first_float(
        payload,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "price",
            "current_price",
        ],
    )
    if value is not None and value > 0:
        return round(value, 4)

    value = _first_float(
        execution_result,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "market_price",
        ],
    )
    if value is not None and value > 0:
        return round(value, 4)

    return 0.0


def _stock_price(payload: Dict[str, Any], execution_result: Dict[str, Any]) -> float:
    value = _first_float(
        execution_result,
        ["fill_price", "executed_price", "average_fill_price", "avg_fill_price"],
    )
    if value is not None and value > 0:
        return round(value, 4)

    value = _first_float(
        payload,
        ["entry", "entry_price", "price", "current_price", "underlying_price", "stock_price"],
    )
    if value is not None and value > 0:
        return round(value, 4)

    return 0.0


def _extract_trade_id(packet: Dict[str, Any]) -> str:
    packet = _safe_dict(packet)
    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_result = _safe_dict(packet.get("execution_result"))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    return _safe_str(
        lifecycle_after.get("trade_id")
        or execution_record.get("trade_id")
        or execution_result.get("trade_id")
        or packet.get("trade_id"),
        "",
    )


# =============================================================================
# Position normalization before add_position()
# =============================================================================

def _normalize_option_lifecycle_for_position(
    lifecycle_after: Dict[str, Any],
    execution_result: Dict[str, Any],
    trading_mode: str,
    mode_context: Dict[str, Any],
) -> Dict[str, Any]:
    pos = deepcopy(_safe_dict(lifecycle_after))

    symbol = _norm_symbol(pos.get("symbol"))
    strategy = _upper(pos.get("strategy", pos.get("final_strategy", pos.get("starting_strategy", "CALL"))), "CALL")
    trade_id = _safe_str(pos.get("trade_id"), f"{symbol}-{strategy}-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    contract = _extract_option_payload(pos)
    premium = _option_premium(pos, execution_result, contract)
    underlying = _underlying_price(pos, execution_result)

    contracts = _safe_int(
        pos.get(
            "contracts",
            pos.get("contract_count", pos.get("quantity", pos.get("qty", 1))),
        ),
        1,
    )
    contracts = max(1, contracts)

    stop = _first_float(
        pos,
        ["option_stop", "premium_stop", "stop_premium", "contract_stop", "stop_loss_premium"],
    )
    target = _first_float(
        pos,
        ["option_target", "premium_target", "target_premium", "contract_target", "take_profit_premium"],
    )

    if stop is None or stop <= 0:
        stop = premium * (1.0 - DEFAULT_OPTION_STOP_LOSS_PCT) if premium > 0 else 0.0

    if target is None or target <= 0:
        target = premium * (1.0 + DEFAULT_OPTION_TARGET_GAIN_PCT) if premium > 0 else 0.0

    stop = round(max(0.01, stop), 4) if stop > 0 else 0.0
    target = round(max(0.01, target), 4) if target > 0 else 0.0

    actual_cost = _safe_float(
        execution_result.get("actual_cost"),
        premium * OPTION_CONTRACT_MULTIPLIER * contracts,
    )
    if actual_cost <= 0 and premium > 0:
        actual_cost = premium * OPTION_CONTRACT_MULTIPLIER * contracts

    commission = _safe_float(execution_result.get("commission"), 0.0)

    pos["symbol"] = symbol
    pos["trade_id"] = trade_id
    pos["strategy"] = strategy
    pos["side"] = strategy
    pos["direction"] = strategy

    pos["vehicle"] = VEHICLE_OPTION
    pos["vehicle_selected"] = VEHICLE_OPTION
    pos["selected_vehicle"] = VEHICLE_OPTION
    pos["asset_type"] = VEHICLE_OPTION
    pos["instrument_type"] = VEHICLE_OPTION

    pos["contracts"] = contracts
    pos["contract_count"] = contracts
    pos["quantity"] = contracts
    pos["qty"] = contracts
    pos["size"] = contracts
    pos["shares"] = 0

    pos["entry"] = premium
    pos["entry_price"] = premium
    pos["fill_price"] = premium
    pos["executed_price"] = premium
    pos["current_price"] = premium

    pos["entry_premium"] = premium
    pos["premium_entry"] = premium
    pos["option_entry"] = premium
    pos["option_entry_price"] = premium
    pos["current_premium"] = premium
    pos["premium_current"] = premium
    pos["current_option_mark"] = premium
    pos["option_current_mark"] = premium
    pos["option_current_price"] = premium
    pos["current_option_price"] = premium

    pos["stop"] = stop
    pos["target"] = target
    pos["option_stop"] = stop
    pos["premium_stop"] = stop
    pos["option_target"] = target
    pos["premium_target"] = target

    pos["underlying_price"] = underlying
    pos["current_underlying_price"] = underlying
    pos["stock_price"] = underlying

    pos["monitoring_price_type"] = "OPTION_PREMIUM"
    pos["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    pos["underlying_price_used_for_close_decision"] = False
    pos["pnl_basis"] = "option_premium_x_100"

    contract_symbol = _safe_str(contract.get("contract_symbol") or contract.get("contractSymbol"), "")
    if contract_symbol:
        pos["contract_symbol"] = contract_symbol
        pos["option_symbol"] = contract_symbol
        pos["option_contract_symbol"] = contract_symbol

    expiry = _safe_str(contract.get("expiry") or contract.get("expiration"), "")
    if expiry:
        pos["expiry"] = expiry
        pos["expiration"] = expiry
        pos["expiration_date"] = expiry

    right = _upper(contract.get("right"), "")
    if right:
        pos["right"] = right
        pos["option_type"] = right
        pos["call_put"] = right

    strike = _safe_optional_float(contract.get("strike"))
    if strike is not None:
        pos["strike"] = strike
        pos["strike_price"] = strike

    pos["option"] = contract
    pos["contract"] = contract

    pos["capital_required"] = round(actual_cost, 4)
    pos["minimum_trade_cost"] = round(actual_cost + commission, 4)
    pos["effective_cost"] = round(actual_cost + commission, 4)
    pos["actual_cost"] = round(actual_cost, 4)
    pos["commission"] = round(commission, 4)

    pos["opened_at"] = _safe_str(pos.get("opened_at"), _now_iso())
    pos["timestamp"] = _safe_str(pos.get("timestamp"), pos["opened_at"])
    pos["status"] = "OPEN"
    pos["position_status"] = "OPEN"
    pos["lifecycle_stage"] = "ENTERED"

    pos["trading_mode"] = trading_mode
    pos["mode"] = trading_mode
    pos["mode_context"] = mode_context

    pos["execution_result"] = execution_result
    pos["execution_normalized_by"] = "engine.execution_loop"
    pos["execution_position_shape"] = "OPTION_PREMIUM_POSITION"

    return pos


def _normalize_stock_lifecycle_for_position(
    lifecycle_after: Dict[str, Any],
    execution_result: Dict[str, Any],
    trading_mode: str,
    mode_context: Dict[str, Any],
) -> Dict[str, Any]:
    pos = deepcopy(_safe_dict(lifecycle_after))

    symbol = _norm_symbol(pos.get("symbol"))
    strategy = _upper(pos.get("strategy", pos.get("final_strategy", pos.get("starting_strategy", "CALL"))), "CALL")
    trade_id = _safe_str(pos.get("trade_id"), f"{symbol}-{strategy}-{datetime.now().strftime('%Y%m%d%H%M%S')}")

    entry = _stock_price(pos, execution_result)
    direction = _direction(strategy)

    shares = _safe_int(
        pos.get("shares", pos.get("quantity", pos.get("qty", pos.get("size", 1)))),
        1,
    )
    shares = max(1, shares)

    stop = _first_float(pos, ["stock_stop", "stop", "stop_loss"])
    target = _first_float(pos, ["stock_target", "target", "take_profit"])

    if direction == "SHORT":
        stop_default = entry * (1.0 + DEFAULT_STOCK_STOP_LOSS_PCT)
        target_default = entry * (1.0 - DEFAULT_STOCK_TARGET_GAIN_PCT)
    else:
        stop_default = entry * (1.0 - DEFAULT_STOCK_STOP_LOSS_PCT)
        target_default = entry * (1.0 + DEFAULT_STOCK_TARGET_GAIN_PCT)

    if stop is None or stop <= 0:
        stop = stop_default if entry > 0 else 0.0

    if target is None or target <= 0:
        target = target_default if entry > 0 else 0.0

    actual_cost = _safe_float(execution_result.get("actual_cost"), entry * shares)
    if actual_cost <= 0 and entry > 0:
        actual_cost = entry * shares

    commission = _safe_float(execution_result.get("commission"), 0.0)

    pos["symbol"] = symbol
    pos["trade_id"] = trade_id
    pos["strategy"] = strategy
    pos["side"] = strategy
    pos["direction"] = strategy

    pos["vehicle"] = VEHICLE_STOCK
    pos["vehicle_selected"] = VEHICLE_STOCK
    pos["selected_vehicle"] = VEHICLE_STOCK
    pos["asset_type"] = VEHICLE_STOCK
    pos["instrument_type"] = VEHICLE_STOCK

    pos["shares"] = shares
    pos["quantity"] = shares
    pos["qty"] = shares
    pos["size"] = shares
    pos["contracts"] = 0
    pos["contract_count"] = 0

    pos["entry"] = round(entry, 4)
    pos["entry_price"] = round(entry, 4)
    pos["fill_price"] = round(entry, 4)
    pos["executed_price"] = round(entry, 4)
    pos["current_price"] = round(entry, 4)
    pos["underlying_price"] = round(entry, 4)
    pos["current_underlying_price"] = round(entry, 4)
    pos["stock_price"] = round(entry, 4)

    pos["entry_premium"] = None
    pos["premium_entry"] = None
    pos["current_premium"] = None
    pos["premium_current"] = None
    pos["current_option_mark"] = None
    pos["option_current_price"] = None

    pos["stop"] = round(stop, 4) if stop > 0 else 0.0
    pos["target"] = round(target, 4) if target > 0 else 0.0

    pos["monitoring_price_type"] = "UNDERLYING"
    pos["price_review_basis"] = "STOCK_PRICE"
    pos["underlying_price_used_for_close_decision"] = True
    pos["pnl_basis"] = "stock_price_x_shares"

    pos["capital_required"] = round(actual_cost, 4)
    pos["minimum_trade_cost"] = round(actual_cost + commission, 4)
    pos["effective_cost"] = round(actual_cost + commission, 4)
    pos["actual_cost"] = round(actual_cost, 4)
    pos["commission"] = round(commission, 4)

    pos["opened_at"] = _safe_str(pos.get("opened_at"), _now_iso())
    pos["timestamp"] = _safe_str(pos.get("timestamp"), pos["opened_at"])
    pos["status"] = "OPEN"
    pos["position_status"] = "OPEN"
    pos["lifecycle_stage"] = "ENTERED"

    pos["trading_mode"] = trading_mode
    pos["mode"] = trading_mode
    pos["mode_context"] = mode_context

    pos["execution_result"] = execution_result
    pos["execution_normalized_by"] = "engine.execution_loop"
    pos["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

    return pos


def _normalize_lifecycle_for_position(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(packet)

    lifecycle_after = deepcopy(_safe_dict(packet.get("lifecycle_after")))
    execution_result = deepcopy(_safe_dict(packet.get("execution_result")))

    trading_mode = _safe_str(
        packet.get("trading_mode", lifecycle_after.get("trading_mode", lifecycle_after.get("mode", "paper"))),
        "paper",
    )
    mode_context = _safe_dict(packet.get("mode_context", lifecycle_after.get("mode_context")))

    vehicle = _selected_vehicle(lifecycle_after)

    if vehicle == VEHICLE_OPTION:
        return _normalize_option_lifecycle_for_position(
            lifecycle_after=lifecycle_after,
            execution_result=execution_result,
            trading_mode=trading_mode,
            mode_context=mode_context,
        )

    if vehicle == VEHICLE_RESEARCH_ONLY:
        lifecycle_after["vehicle"] = VEHICLE_RESEARCH_ONLY
        lifecycle_after["vehicle_selected"] = VEHICLE_RESEARCH_ONLY
        lifecycle_after["monitoring_price_type"] = "RESEARCH_ONLY"
        lifecycle_after["price_review_basis"] = "NO_POSITION"
        lifecycle_after["status"] = "RESEARCH_ONLY"
        lifecycle_after["position_status"] = "RESEARCH_ONLY"
        lifecycle_after["execution_normalized_by"] = "engine.execution_loop"
        lifecycle_after["execution_position_shape"] = "RESEARCH_ONLY_NO_POSITION"
        return lifecycle_after

    return _normalize_stock_lifecycle_for_position(
        lifecycle_after=lifecycle_after,
        execution_result=execution_result,
        trading_mode=trading_mode,
        mode_context=mode_context,
    )


# =============================================================================
# Logging
# =============================================================================

def _append_trade_log(packet: Dict[str, Any], position: Dict[str, Any]) -> None:
    trade_log = _load_json("data/trade_log.json", [])
    if not isinstance(trade_log, list):
        trade_log = []

    packet = _safe_dict(packet)
    position = _safe_dict(position)

    lifecycle_after = _safe_dict(packet.get("lifecycle_after"))
    execution_result = _safe_dict(packet.get("execution_result"))
    execution_record = _safe_dict(execution_result.get("execution_record"))

    vehicle = _selected_vehicle(position)

    trade_log.append({
        "timestamp": _safe_str(position.get("opened_at"), _now_iso()),
        "trade_id": _safe_str(position.get("trade_id"), ""),
        "symbol": _norm_symbol(position.get("symbol")),
        "strategy": _upper(position.get("strategy", "CALL"), "CALL"),
        "vehicle": vehicle,
        "vehicle_selected": vehicle,
        "action": "OPEN",
        "status": "FILLED",
        "fill_price": round(_safe_float(position.get("fill_price", position.get("entry", 0.0)), 0.0), 4),
        "entry": round(_safe_float(position.get("entry", 0.0), 0.0), 4),
        "entry_price": round(_safe_float(position.get("entry_price", position.get("entry", 0.0)), 0.0), 4),
        "current_price": round(_safe_float(position.get("current_price", 0.0), 0.0), 4),
        "underlying_price": round(_safe_float(position.get("underlying_price", 0.0), 0.0), 4),
        "current_underlying_price": round(_safe_float(position.get("current_underlying_price", 0.0), 0.0), 4),
        "entry_premium": round(_safe_float(position.get("entry_premium", 0.0), 0.0), 4),
        "current_premium": round(_safe_float(position.get("current_premium", 0.0), 0.0), 4),
        "current_option_mark": round(_safe_float(position.get("current_option_mark", 0.0), 0.0), 4),
        "quantity": _safe_int(position.get("size", position.get("quantity", 0)), 0),
        "shares": _safe_int(position.get("shares", 0), 0),
        "contracts": _safe_int(position.get("contracts", 0), 0),
        "commission": round(_safe_float(position.get("commission", 0.0), 0.0), 4),
        "actual_cost": round(_safe_float(position.get("actual_cost", execution_result.get("actual_cost", 0.0)), 0.0), 4),
        "capital_required": round(_safe_float(position.get("capital_required", 0.0), 0.0), 4),
        "broker_order_id": _safe_str(execution_result.get("broker_order_id"), ""),
        "trading_mode": _safe_str(packet.get("trading_mode", lifecycle_after.get("trading_mode", "paper")), "paper"),
        "reason": _safe_str(lifecycle_after.get("final_reason", execution_result.get("reason", "entered")), "entered"),
        "reason_code": _safe_str(
            lifecycle_after.get("final_reason_code", execution_result.get("reason_code", "entered")),
            "entered",
        ),
        "monitoring_price_type": _safe_str(position.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(position.get("price_review_basis"), ""),
        "underlying_price_used_for_close_decision": _safe_bool(
            position.get("underlying_price_used_for_close_decision"),
            vehicle != VEHICLE_OPTION,
        ),
        "contract_symbol": _safe_str(position.get("contract_symbol", position.get("option_symbol")), ""),
        "expiry": _safe_str(position.get("expiry", position.get("expiration")), ""),
        "strike": _safe_float(position.get("strike"), 0.0),
        "right": _safe_str(position.get("right"), ""),
        "execution_position_shape": _safe_str(position.get("execution_position_shape"), ""),
        "execution_record": execution_record,
    })

    _write_json("data/trade_log.json", trade_log)


def _persist_executed_trade(packet: Dict[str, Any]) -> Dict[str, Any]:
    packet = _safe_dict(packet)

    normalized_lifecycle = _normalize_lifecycle_for_position(packet)

    vehicle = _selected_vehicle(normalized_lifecycle)

    if vehicle == VEHICLE_RESEARCH_ONLY:
        return {
            "persisted": False,
            "blocked": True,
            "reason": "research_only_not_persisted_as_open_position",
            "normalized_lifecycle": normalized_lifecycle,
            "persisted_via_module": False,
        }

    execution_result = _safe_dict(packet.get("execution_result"))
    trading_mode = _safe_str(packet.get("trading_mode", normalized_lifecycle.get("trading_mode", "paper")), "paper")
    mode_context = _safe_dict(packet.get("mode_context", normalized_lifecycle.get("mode_context")))

    position = add_position(
        normalized_lifecycle,
        allow_replace=False,
        lifecycle=normalized_lifecycle,
        execution_result=execution_result,
        mode=trading_mode,
        mode_context=mode_context,
    )

    _append_trade_log(packet, position)

    return {
        "persisted": True,
        "position": position,
        "persisted_via_module": True,
        "normalized_vehicle": vehicle,
        "execution_position_shape": _safe_str(normalized_lifecycle.get("execution_position_shape"), ""),
    }


# =============================================================================
# Public execution loop
# =============================================================================

def execute_trades(
    queue: List[Dict[str, Any]] | None,
    limit: int = 3,
    portfolio_context: Dict[str, Any] | None = None,
    broker_adapter: Any = None,
    trading_mode: str | None = None,
    max_open_positions: int = 5,
    current_open_positions: int | None = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
) -> Dict[str, Any]:
    queue = queue if isinstance(queue, list) else []
    portfolio_context = _safe_dict(portfolio_context)

    results: List[Dict[str, Any]] = []
    summaries: List[Dict[str, Any]] = []

    executed = 0
    rejected = 0
    skipped = 0
    persisted = 0
    persistence_blocked = 0

    open_positions_running = (
        _safe_int(current_open_positions, open_count())
        if current_open_positions is not None
        else _safe_int(open_count(), 0)
    )

    remaining_slots = max(0, _safe_int(max_open_positions, 0) - open_positions_running)
    effective_limit = min(max(0, _safe_int(limit, 0)), remaining_slots)

    print("EXECUTION LOOP START:", {
        "queue_size": len(queue),
        "requested_limit": limit,
        "max_open_positions": max_open_positions,
        "current_open_positions": open_positions_running,
        "remaining_slots": remaining_slots,
        "effective_limit": effective_limit,
        "trading_mode": trading_mode or portfolio_context.get("trading_mode") or portfolio_context.get("mode") or "paper",
    })

    for queued_trade in queue:
        if executed >= effective_limit:
            break

        queued_trade = deepcopy(_safe_dict(queued_trade))

        if not queued_trade:
            skipped += 1
            continue

        resolved_mode = _safe_str(
            trading_mode
            or queued_trade.get("trading_mode")
            or queued_trade.get("execution_mode")
            or queued_trade.get("mode")
            or portfolio_context.get("trading_mode")
            or portfolio_context.get("mode"),
            "paper",
        )

        print("PRE-EXECUTION-HANDOFF:", {
            "symbol": queued_trade.get("symbol"),
            "trade_id": queued_trade.get("trade_id"),
            "research_approved": queued_trade.get("research_approved"),
            "execution_ready": queued_trade.get("execution_ready"),
            "selected_for_execution": queued_trade.get("selected_for_execution"),
            "vehicle_selected": queued_trade.get("vehicle_selected"),
            "contracts": queued_trade.get("contracts"),
            "shares": queued_trade.get("shares"),
            "has_option": bool(_safe_dict(queued_trade.get("option")) or _safe_dict(queued_trade.get("contract"))),
            "contract_symbol": queued_trade.get("contract_symbol")
                or _safe_dict(queued_trade.get("option")).get("contractSymbol")
                or _safe_dict(queued_trade.get("option")).get("contract_symbol"),
            "lifecycle_stage": queued_trade.get("lifecycle_stage"),
            "trading_mode": resolved_mode,
        })

        packet = execute_via_adapter(
            queued_trade=queued_trade,
            portfolio_context=portfolio_context,
            max_open_positions=max_open_positions,
            current_open_positions=open_positions_running,
            kill_switch_enabled=kill_switch_enabled,
            session_healthy=session_healthy,
            broker_adapter=broker_adapter,
        )

        packet = _safe_dict(packet)
        packet["trade_id"] = _extract_trade_id(packet) or _safe_str(queued_trade.get("trade_id"), "")
        packet["trading_mode"] = _safe_str(packet.get("trading_mode", resolved_mode), resolved_mode)

        if "mode_context" not in packet and "mode_context" in queued_trade:
            packet["mode_context"] = queued_trade.get("mode_context")

        if _safe_bool(packet.get("success"), False):
            persistence = _persist_executed_trade(packet)
            packet["persistence"] = persistence

            if _safe_bool(persistence.get("persisted"), False):
                persisted += 1
                open_positions_running += 1

            else:
                persistence_blocked += 1

            executed += 1

            position = _safe_dict(persistence.get("position"))
            if position:
                print("EXECUTION PERSISTED:", {
                    "symbol": position.get("symbol"),
                    "trade_id": position.get("trade_id"),
                    "vehicle": position.get("vehicle"),
                    "vehicle_selected": position.get("vehicle_selected"),
                    "shares": position.get("shares"),
                    "contracts": position.get("contracts"),
                    "entry": position.get("entry"),
                    "current_price": position.get("current_price"),
                    "entry_premium": position.get("entry_premium"),
                    "current_premium": position.get("current_premium"),
                    "underlying_price": position.get("underlying_price"),
                    "monitoring_price_type": position.get("monitoring_price_type"),
                    "price_review_basis": position.get("price_review_basis"),
                    "execution_position_shape": position.get("execution_position_shape"),
                })
            else:
                print("EXECUTION NOT PERSISTED:", persistence)

        else:
            rejected += 1
            print("EXECUTION REJECTED:", {
                "symbol": queued_trade.get("symbol"),
                "trade_id": packet.get("trade_id"),
                "reason": packet.get("reason"),
                "reason_code": packet.get("reason_code"),
                "execution_result": packet.get("execution_result"),
            })

        summaries.append(summarize_execution_packet(packet))
        results.append(packet)

    print("EXECUTION LOOP SUMMARY:", {
        "queue_size": len(queue),
        "processed": len(results),
        "executed": executed,
        "persisted": persisted,
        "persistence_blocked": persistence_blocked,
        "rejected": rejected,
        "skipped": skipped,
        "open_positions_after": open_positions_running,
        "remaining_slots_before_execution": remaining_slots,
        "effective_limit": effective_limit,
    })

    return {
        "results": results,
        "summaries": summaries,
        "executed": executed,
        "persisted": persisted,
        "persistence_blocked": persistence_blocked,
        "rejected": rejected,
        "skipped": skipped,
        "processed": len(results),
        "queue_size": len(queue),
        "open_positions_after": open_positions_running,
        "timestamp": _now_iso(),
    }


__all__ = [
    "execute_trades",
]
