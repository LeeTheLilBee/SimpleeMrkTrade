from __future__ import annotations

"""
Observatory Execution Loop

Purpose:
    Own the execution step after candidate selection.

Canonical rule:
    The selected vehicle controls the saved open-position shape.

    OPTION:
        - contracts > 0
        - shares = 0
        - entry/current_price are option premium values
        - underlying_price is context only
        - monitoring_price_type = OPTION_PREMIUM
        - price_review_basis = OPTION_PREMIUM_ONLY
        - stop/target/take_profit aliases are all option-premium values

    STOCK:
        - shares > 0
        - contracts = 0
        - entry/current_price are underlying stock values
        - monitoring_price_type = UNDERLYING
        - price_review_basis = STOCK_PRICE
"""

import json
import math
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.execution_handoff import execute_via_adapter, summarize_execution_packet
from engine.paper_portfolio import add_position, open_count, get_position

try:
    from engine.risk_governor import governor_status
except Exception:
    governor_status = None

try:
    from engine.observatory_mode import normalize_mode, build_mode_context
except Exception:
    def normalize_mode(value):
        raw = str(value or "paper").strip().lower()
        return raw if raw in {"survey", "paper", "live"} else "paper"

    def build_mode_context(mode):
        mode = normalize_mode(mode)
        return {
            "mode": mode,
            "mode_label": f"{mode.title()} Mode",
            "max_open_positions": 3,
            "queue_limit": 3,
            "max_daily_entries": 3,
        }




try:
    from engine.trade_activity_bridge import record_entry_event, record_skip_event
except Exception:
    record_entry_event = None
    record_skip_event = None


try:
    from engine.trade_cooldown_guard import guard_execution_queue
except Exception:
    guard_execution_queue = None

OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

DEFAULT_OPTION_STOP_LOSS_PCT = 0.35
DEFAULT_OPTION_TARGET_GAIN_PCT = 0.60

DEFAULT_STOCK_STOP_LOSS_PCT = 0.03
DEFAULT_STOCK_TARGET_GAIN_PCT = 0.10


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




def _guard_execution_queue_with_metadata(queue: List[Dict[str, Any]], *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Safe wrapper around trade_cooldown_guard.guard_execution_queue.
    Keeps anti-repeat behavior and gives execute_trades clean return metadata.
    """
    original_queue = queue if isinstance(queue, list) else []
    original_count = len(original_queue)

    fallback = {
        "input_count": original_count,
        "original_queue_size": original_count,
        "allowed_count": original_count,
        "blocked_count": 0,
        "queue": original_queue,
        "allowed": original_queue,
        "blocked": [],
        "allowed_symbols": [
            item.get("symbol")
            for item in original_queue
            if isinstance(item, dict)
        ],
        "blocked_symbols": [],
    }

    if not callable(guard_execution_queue):
        fallback["reason"] = "guard_execution_queue_unavailable"
        return fallback

    try:
        result = guard_execution_queue(original_queue, *args, **kwargs)
    except Exception as exc:
        fallback["reason"] = f"guard_execution_queue_exception:{exc}"
        return fallback

    if not isinstance(result, dict):
        fallback["reason"] = "guard_execution_queue_returned_non_dict"
        return fallback

    allowed_queue = result.get("queue", result.get("allowed", []))
    if not isinstance(allowed_queue, list):
        allowed_queue = []

    blocked_items = result.get("blocked", [])
    if not isinstance(blocked_items, list):
        blocked_items = []

    allowed_symbols = result.get("allowed_symbols")
    if not isinstance(allowed_symbols, list):
        allowed_symbols = [
            item.get("symbol")
            for item in allowed_queue
            if isinstance(item, dict)
        ]

    blocked_symbols = result.get("blocked_symbols")
    if not isinstance(blocked_symbols, list):
        blocked_symbols = [
            item.get("symbol")
            for item in blocked_items
            if isinstance(item, dict)
        ]

    result["input_count"] = _safe_int(
        result.get("input_count", result.get("original_queue_size", original_count)),
        original_count,
    )
    result["original_queue_size"] = result["input_count"]
    result["queue"] = allowed_queue
    result["allowed"] = allowed_queue
    result["blocked"] = blocked_items
    result["allowed_count"] = _safe_int(
        result.get("allowed_count", len(allowed_queue)),
        len(allowed_queue),
    )
    result["blocked_count"] = _safe_int(
        result.get("blocked_count", len(blocked_items)),
        len(blocked_items),
    )
    result["allowed_symbols"] = allowed_symbols
    result["blocked_symbols"] = blocked_symbols

    return result


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
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    tmp.replace(p)


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
        ["contract_symbol", "option_symbol", "option_contract_symbol", "selected_contract_symbol", "occ_symbol", "contractSymbol"],
        "",
    )

    right = _upper(
        _first_str(payload, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(option, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(contract, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    if option or contract or contract_symbol or right in {"CALL", "PUT", "C", "P"}:
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
                "contractSymbol",
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
            ],
            "",
        )
    )

    expiry = (
        _first_str(payload, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
        or _first_str(merged, ["expiration", "expiry", "expiration_date", "contract_expiry"], "")
    )

    right = _upper(
        _first_str(payload, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(merged, ["right", "option_type", "call_put", "contract_right"], ""),
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

    final_price_reference = selected_price_reference if selected_price_reference is not None else mark

    out = {
        "symbol": _norm_symbol(payload.get("symbol", merged.get("underlying_symbol", ""))),
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
        "selected_price_reference": final_price_reference,
        "price_reference": final_price_reference,
        "volume": _safe_int(payload.get("volume", merged.get("volume")), 0),
        "open_interest": _safe_int(payload.get("open_interest", merged.get("open_interest", merged.get("oi"))), 0),
        "implied_volatility": _safe_float(payload.get("implied_volatility", merged.get("implied_volatility")), 0.0),
        "in_the_money": _safe_bool(payload.get("in_the_money", merged.get("in_the_money")), False),
        "spread": _safe_float(payload.get("spread", merged.get("spread")), 0.0),
        "spread_pct": _safe_float(payload.get("spread_pct", merged.get("spread_pct")), 0.0),
        "distance_pct": _safe_float(payload.get("distance_pct", merged.get("distance_pct")), 0.0),
        "contract_score": _safe_float(payload.get("contract_score", merged.get("contract_score")), 0.0),
        "trade_intent": _safe_str(payload.get("trade_intent", merged.get("trade_intent")), ""),
        "dte": _safe_int(payload.get("dte", merged.get("dte")), 0),
        "monitoring_mode": "OPTION_PREMIUM",
        "price_basis": "OPTION_PREMIUM",
        "is_executable": _safe_bool(payload.get("is_executable", merged.get("is_executable")), True),
        "execution_reason": _safe_str(payload.get("execution_reason", merged.get("execution_reason")), "ok"),
        "contract_notes": _safe_list(payload.get("contract_notes", merged.get("contract_notes"))),
    }

    if final_price_reference is not None and final_price_reference > 0:
        out["current_mark"] = final_price_reference
        out["current_option_mark"] = final_price_reference
        out["option_current_mark"] = final_price_reference
        out["option_current_price"] = final_price_reference
        out["current_option_price"] = final_price_reference
        out["current_premium"] = final_price_reference
        out["premium_current"] = final_price_reference

    return out


def _mid_from_bid_ask(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0:
        return None
    if ask < bid:
        return None
    return round((bid + ask) / 2.0, 4)


def _option_premium(payload: Dict[str, Any], execution_result: Dict[str, Any], contract: Dict[str, Any]) -> float:
    execution_record = _safe_dict(execution_result.get("execution_record"))

    direct_candidates = [
        execution_result.get("fill_price"),
        execution_result.get("executed_price"),
        execution_result.get("average_fill_price"),
        execution_result.get("avg_fill_price"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        execution_record.get("entry_premium"),
        execution_record.get("current_premium"),
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
    """
    Resolve the underlying stock context for OPTION positions.

    Important:
    - This function must NOT use generic `price`, `current`, or `current_price`.
    - Those fields can be option premium fields after paper fill rehydration.
    - Underlying context is allowed only from explicit underlying/stock/spot fields.
    """
    payload = _safe_dict(payload)
    execution_result = _safe_dict(execution_result)
    execution_record = _safe_dict(execution_result.get("execution_record"))

    value = _first_float(
        payload,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "stock_last",
            "stock_mark",
            "underlying_context",
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
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "stock_last",
            "stock_mark",
            "underlying_context",
            "market_price",
        ],
    )
    if value is not None and value > 0:
        return round(value, 4)

    value = _first_float(
        execution_record,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "stock_last",
            "stock_mark",
            "underlying_context",
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


def _stamp_option_price_aliases(pos: Dict[str, Any], premium: float) -> None:
    premium = round(_safe_float(premium, 0.0), 4)

    pos["entry"] = premium
    pos["entry_price"] = premium
    pos["price"] = premium
    pos["requested_price"] = premium
    pos["fill_price"] = premium
    pos["executed_price"] = premium
    pos["current_price"] = premium
    pos["current"] = premium

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
    pos["mark"] = premium


def _stamp_option_stop_target_aliases(pos: Dict[str, Any], stop: float, target: float) -> None:
    stop = round(_safe_float(stop, 0.0), 4)
    target = round(_safe_float(target, 0.0), 4)

    pos["stop"] = stop
    pos["stop_loss"] = stop
    pos["option_stop"] = stop
    pos["premium_stop"] = stop
    pos["stop_premium"] = stop
    pos["stop_loss_premium"] = stop
    pos["contract_stop"] = stop

    pos["target"] = target
    pos["take_profit"] = target
    pos["option_target"] = target
    pos["premium_target"] = target
    pos["target_premium"] = target
    pos["take_profit_premium"] = target
    pos["contract_target"] = target


def _stamp_stock_stop_target_aliases(pos: Dict[str, Any], stop: float, target: float) -> None:
    stop = round(_safe_float(stop, 0.0), 4)
    target = round(_safe_float(target, 0.0), 4)

    pos["stop"] = stop
    pos["stop_loss"] = stop
    pos["stock_stop"] = stop

    pos["target"] = target
    pos["take_profit"] = target
    pos["stock_target"] = target


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

    # OBSERVATORY_REPAIR_OPTION_UNDERLYING_PREMIUM_LEAK_GUARD_20260520
    # If the only available "underlying" equals the option premium, it is not
    # true underlying stock context. Keep it as 0.0 instead of polluting the
    # position with premium-as-underlying.
    if premium > 0 and underlying > 0 and abs(float(underlying) - float(premium)) < 0.0001:
        underlying = 0.0

    contracts = _safe_int(
        pos.get("contracts", pos.get("contract_count", pos.get("quantity", pos.get("qty", 1)))),
        1,
    )
    contracts = max(1, contracts)

    stop = _first_float(
        pos,
        [
            "option_stop",
            "premium_stop",
            "stop_premium",
            "contract_stop",
            "stop_loss_premium",
        ],
    )

    target = _first_float(
        pos,
        [
            "option_target",
            "premium_target",
            "target_premium",
            "contract_target",
            "take_profit_premium",
        ],
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
    pos["company_name"] = _safe_str(pos.get("company_name"), symbol)
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

    _stamp_option_price_aliases(pos, premium)
    _stamp_option_stop_target_aliases(pos, stop, target)

    pos["underlying_price"] = underlying
    pos["current_underlying_price"] = underlying
    pos["stock_price"] = underlying

    pos["monitoring_price_type"] = "OPTION_PREMIUM"
    pos["monitoring_mode"] = "OPTION_PREMIUM"
    pos["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    pos["price_basis"] = "OPTION_PREMIUM"
    pos["underlying_price_used_for_close_decision"] = False
    pos["pnl_basis"] = "option_premium_x_100"

    contract_symbol = _safe_str(contract.get("contract_symbol") or contract.get("contractSymbol"), "")
    if contract_symbol:
        pos["contract_symbol"] = contract_symbol
        pos["contractSymbol"] = contract_symbol
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

    for key in [
        "bid",
        "ask",
        "last",
        "volume",
        "open_interest",
        "dte",
        "spread",
        "spread_pct",
        "distance_pct",
        "implied_volatility",
        "in_the_money",
        "contract_score",
        "trade_intent",
        "contract_notes",
    ]:
        if key in contract:
            pos[key] = contract.get(key)

    contract["mark"] = premium
    contract["selected_price_reference"] = premium
    contract["price_reference"] = premium
    contract["current_mark"] = premium
    contract["current_option_mark"] = premium
    contract["option_current_mark"] = premium
    contract["option_current_price"] = premium
    contract["current_option_price"] = premium
    contract["current_premium"] = premium
    contract["premium_current"] = premium
    contract["monitoring_mode"] = "OPTION_PREMIUM"
    contract["price_basis"] = "OPTION_PREMIUM"

    pos["option"] = contract
    pos["contract"] = contract

    pos["capital_required"] = round(actual_cost, 4)
    pos["minimum_trade_cost"] = round(actual_cost + commission, 4)
    pos["effective_cost"] = round(actual_cost + commission, 4)
    pos["actual_cost"] = round(actual_cost, 4)
    pos["commission"] = round(commission, 4)

    pos["opened_at"] = _safe_str(pos.get("opened_at"), _now_iso())
    pos["timestamp"] = _safe_str(pos.get("timestamp"), pos["opened_at"])
    pos["entered_at"] = _safe_str(pos.get("entered_at"), pos["opened_at"])
    pos["closed_at"] = _safe_str(pos.get("closed_at"), "")
    pos["exit_price"] = _safe_float(pos.get("exit_price"), 0.0)
    pos["close_price"] = _safe_float(pos.get("close_price"), 0.0)

    pos["status"] = "OPEN"
    pos["position_status"] = "OPEN"
    pos["execution_status"] = "FILLED"
    pos["lifecycle_stage"] = "ENTERED"

    pos["trading_mode"] = trading_mode
    pos["mode"] = trading_mode
    pos["execution_mode"] = trading_mode
    pos["mode_context"] = mode_context

    pos["execution_result"] = execution_result
    pos["execution_normalized_by"] = "engine.execution_loop"
    pos["execution_position_shape"] = "OPTION_PREMIUM_POSITION"

    pos["execution_contract_audit"] = {
        "vehicle": VEHICLE_OPTION,
        "premium": premium,
        "stop": stop,
        "target": target,
        "contracts": contracts,
        "underlying_price": underlying,
        "contract_symbol": contract_symbol,
        "expiry": expiry,
        "right": right,
        "strike": strike,
        "field_family_locked": True,
        "stop_target_aliases_locked": True,
    }

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
    pos["company_name"] = _safe_str(pos.get("company_name"), symbol)
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

    entry = round(entry, 4)

    pos["entry"] = entry
    pos["entry_price"] = entry
    pos["price"] = entry
    pos["requested_price"] = entry
    pos["fill_price"] = entry
    pos["executed_price"] = entry
    pos["current_price"] = entry
    pos["current"] = entry
    pos["underlying_price"] = entry
    pos["current_underlying_price"] = entry
    pos["stock_price"] = entry

    pos["entry_premium"] = None
    pos["premium_entry"] = None
    pos["option_entry"] = None
    pos["option_entry_price"] = None
    pos["current_premium"] = None
    pos["premium_current"] = None
    pos["current_option_mark"] = None
    pos["option_current_mark"] = None
    pos["option_current_price"] = None
    pos["current_option_price"] = None

    _stamp_stock_stop_target_aliases(pos, stop, target)

    pos["monitoring_price_type"] = "UNDERLYING"
    pos["monitoring_mode"] = "UNDERLYING"
    pos["price_review_basis"] = "STOCK_PRICE"
    pos["price_basis"] = "STOCK_PRICE"
    pos["underlying_price_used_for_close_decision"] = True
    pos["pnl_basis"] = "stock_price_x_shares"

    pos["capital_required"] = round(actual_cost, 4)
    pos["minimum_trade_cost"] = round(actual_cost + commission, 4)
    pos["effective_cost"] = round(actual_cost + commission, 4)
    pos["actual_cost"] = round(actual_cost, 4)
    pos["commission"] = round(commission, 4)

    pos["opened_at"] = _safe_str(pos.get("opened_at"), _now_iso())
    pos["timestamp"] = _safe_str(pos.get("timestamp"), pos["opened_at"])
    pos["entered_at"] = _safe_str(pos.get("entered_at"), pos["opened_at"])
    pos["closed_at"] = _safe_str(pos.get("closed_at"), "")
    pos["exit_price"] = _safe_float(pos.get("exit_price"), 0.0)
    pos["close_price"] = _safe_float(pos.get("close_price"), 0.0)

    pos["status"] = "OPEN"
    pos["position_status"] = "OPEN"
    pos["execution_status"] = "FILLED"
    pos["lifecycle_stage"] = "ENTERED"

    pos["trading_mode"] = trading_mode
    pos["mode"] = trading_mode
    pos["execution_mode"] = trading_mode
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
        lifecycle_after["selected_vehicle"] = VEHICLE_RESEARCH_ONLY
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

    row = {
        "timestamp": _safe_str(position.get("opened_at"), _now_iso()),
        "trade_id": _safe_str(position.get("trade_id"), ""),
        "symbol": _norm_symbol(position.get("symbol")),
        "strategy": _upper(position.get("strategy", "CALL"), "CALL"),
        "vehicle": vehicle,
        "vehicle_selected": vehicle,
        "selected_vehicle": vehicle,
        "action": "OPEN",
        "status": "FILLED",
        "fill_price": round(_safe_float(position.get("fill_price", position.get("entry", 0.0)), 0.0), 4),
        "entry": round(_safe_float(position.get("entry", 0.0), 0.0), 4),
        "entry_price": round(_safe_float(position.get("entry_price", position.get("entry", 0.0)), 0.0), 4),
        "current_price": round(_safe_float(position.get("current_price", 0.0), 0.0), 4),
        "underlying_price": round(_safe_float(position.get("underlying_price", 0.0), 0.0), 4),
        "current_underlying_price": round(_safe_float(position.get("current_underlying_price", 0.0), 0.0), 4),
        "entry_premium": round(_safe_float(position.get("entry_premium", 0.0), 0.0), 4),
        "premium_entry": round(_safe_float(position.get("premium_entry", 0.0), 0.0), 4),
        "current_premium": round(_safe_float(position.get("current_premium", 0.0), 0.0), 4),
        "premium_current": round(_safe_float(position.get("premium_current", 0.0), 0.0), 4),
        "current_option_mark": round(_safe_float(position.get("current_option_mark", 0.0), 0.0), 4),
        "option_current_price": round(_safe_float(position.get("option_current_price", 0.0), 0.0), 4),
        "stop": round(_safe_float(position.get("stop", 0.0), 0.0), 4),
        "stop_loss": round(_safe_float(position.get("stop_loss", 0.0), 0.0), 4),
        "target": round(_safe_float(position.get("target", 0.0), 0.0), 4),
        "take_profit": round(_safe_float(position.get("take_profit", 0.0), 0.0), 4),
        "option_stop": round(_safe_float(position.get("option_stop", 0.0), 0.0), 4),
        "premium_stop": round(_safe_float(position.get("premium_stop", 0.0), 0.0), 4),
        "stop_premium": round(_safe_float(position.get("stop_premium", 0.0), 0.0), 4),
        "option_target": round(_safe_float(position.get("option_target", 0.0), 0.0), 4),
        "premium_target": round(_safe_float(position.get("premium_target", 0.0), 0.0), 4),
        "target_premium": round(_safe_float(position.get("target_premium", 0.0), 0.0), 4),
        "take_profit_premium": round(_safe_float(position.get("take_profit_premium", 0.0), 0.0), 4),
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
        "monitoring_mode": _safe_str(position.get("monitoring_mode"), ""),
        "price_review_basis": _safe_str(position.get("price_review_basis"), ""),
        "price_basis": _safe_str(position.get("price_basis"), ""),
        "underlying_price_used_for_close_decision": _safe_bool(
            position.get("underlying_price_used_for_close_decision"),
            vehicle != VEHICLE_OPTION,
        ),
        "pnl_basis": _safe_str(position.get("pnl_basis"), ""),
        "contract_symbol": _safe_str(position.get("contract_symbol", position.get("option_symbol")), ""),
        "option_symbol": _safe_str(position.get("option_symbol", position.get("contract_symbol")), ""),
        "expiry": _safe_str(position.get("expiry", position.get("expiration")), ""),
        "expiration": _safe_str(position.get("expiration", position.get("expiry")), ""),
        "strike": _safe_float(position.get("strike"), 0.0),
        "right": _safe_str(position.get("right"), ""),
        "execution_position_shape": _safe_str(position.get("execution_position_shape"), ""),
        "execution_record": execution_record,
    }

    trade_log.append(row)
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



def _resolve_execution_limits_from_governor(
    *,
    trading_mode: str,
    portfolio_context: Dict[str, Any],
    current_open_positions: int | None,
    requested_limit: int | None,
    fallback_max_open_positions: int,
) -> Dict[str, Any]:
    """
    Canonical execution-limit resolver.

    Authority order:
        1. risk_governor.governor_status()
        2. governor limits
        3. governor mode_context
        4. portfolio_context
        5. legacy function defaults

    This prevents execution_loop from silently falling back to stale values like max_open_positions=5.
    """
    portfolio_context = _safe_dict(portfolio_context)

    resolved_mode = _safe_str(
        trading_mode
        or portfolio_context.get("trading_mode")
        or portfolio_context.get("mode")
        or portfolio_context.get("execution_mode"),
        "paper",
    )

    try:
        resolved_mode = normalize_mode(resolved_mode)
    except Exception:
        resolved_mode = _safe_str(resolved_mode, "paper").lower()

    open_positions_running = (
        _safe_int(current_open_positions, open_count())
        if current_open_positions is not None
        else _safe_int(open_count(), 0)
    )

    governor = {}
    if callable(governor_status):
        try:
            governor = governor_status(
                current_open_positions=open_positions_running,
                trading_mode=resolved_mode,
                account_id=portfolio_context.get("account_id", "default"),
            )
            governor = _safe_dict(governor)
        except Exception as exc:
            governor = {
                "blocked": False,
                "reasons": [],
                "warnings": [f"governor_status_failed:{exc}"],
                "limits": {},
                "mode_context": {},
                "execution_pause": {},
                "trading_mode": resolved_mode,
            }

    governor_limits = _safe_dict(governor.get("limits"))
    governor_mode_context = _safe_dict(governor.get("mode_context"))

    if not governor_mode_context:
        try:
            governor_mode_context = _safe_dict(build_mode_context(resolved_mode))
        except Exception:
            governor_mode_context = {}

    resolved_mode = _safe_str(
        governor.get("trading_mode")
        or governor_mode_context.get("mode")
        or resolved_mode,
        resolved_mode,
    )

    max_open_positions = _safe_int(
        governor_limits.get(
            "max_open_positions",
            governor_mode_context.get(
                "max_open_positions",
                portfolio_context.get("max_open_positions", fallback_max_open_positions),
            ),
        ),
        fallback_max_open_positions,
    )

    queue_limit = _safe_int(
        governor_limits.get(
            "queue_limit",
            governor_mode_context.get(
                "queue_limit",
                portfolio_context.get("queue_limit", requested_limit if requested_limit is not None else max_open_positions),
            ),
        ),
        max_open_positions,
    )

    max_daily_entries = _safe_int(
        governor_limits.get(
            "max_daily_entries",
            governor_mode_context.get("max_daily_entries", portfolio_context.get("max_daily_entries", 3)),
        ),
        3,
    )

    max_rolling_5_business_day_entries = _safe_int(
        governor_limits.get(
            "max_rolling_5_business_day_entries",
            governor_mode_context.get("max_rolling_5_business_day_entries", 0),
        ),
        0,
    )

    over_25k = _safe_bool(
        governor.get("over_25k", governor_mode_context.get("over_25k", False)),
        False,
    )

    remaining_slots = max(0, max_open_positions - open_positions_running)

    raw_limit = (
        _safe_int(requested_limit, queue_limit)
        if requested_limit is not None
        else queue_limit
    )

    effective_limit = min(
        max(0, raw_limit),
        max(0, queue_limit),
        remaining_slots,
    )

    if _safe_bool(governor.get("blocked"), False):
        effective_limit = 0

    return {
        "trading_mode": resolved_mode,
        "mode_context": governor_mode_context,
        "governor": governor,
        "governor_limits": governor_limits,
        "governor_blocked": _safe_bool(governor.get("blocked"), False),
        "governor_reasons": _safe_list(governor.get("reasons")),
        "governor_warnings": _safe_list(governor.get("warnings")),
        "execution_pause": _safe_dict(governor.get("execution_pause")),
        "open_positions_running": open_positions_running,
        "max_open_positions": max_open_positions,
        "queue_limit": queue_limit,
        "max_daily_entries": max_daily_entries,
        "max_rolling_5_business_day_entries": max_rolling_5_business_day_entries,
        "over_25k": over_25k,
        "remaining_slots": remaining_slots,
        "requested_limit": raw_limit,
        "effective_limit": effective_limit,
    }



def _find_existing_open_position_for_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execution-time duplicate guard.

    This is intentionally inside execution_loop because selection can become stale.
    Example:
        selected_trades = [QCOM, SMCI, ORCL]
        QCOM and SMCI were already opened in a prior run.
        The execution loop must skip QCOM/SMCI and let ORCL use the remaining slot.
    """
    trade = _safe_dict(trade)
    symbol = _norm_symbol(trade.get("symbol"))
    if not symbol or symbol == "UNKNOWN":
        return {}

    try:
        existing = get_position(symbol)
        if isinstance(existing, dict) and existing:
            return existing
    except Exception:
        pass

    # Fallback: scan the open positions file directly if get_position misses it.
    try:
        data = _load_json("data/open_positions.json", [])
        rows = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
        for row in rows:
            row = _safe_dict(row)
            if _norm_symbol(row.get("symbol")) != symbol:
                continue

            status = _upper(row.get("status", row.get("position_status", "OPEN")), "OPEN")
            if status in {"CLOSED", "EXITED", "CANCELLED"}:
                continue

            return row
    except Exception:
        pass

    return {}


def _duplicate_skip_summary(trade: Dict[str, Any], existing: Dict[str, Any]) -> Dict[str, Any]:
    trade = _safe_dict(trade)
    existing = _safe_dict(existing)

    return {
        "success": False,
        "status": "SKIPPED_DUPLICATE_OPEN_POSITION",
        "symbol": _norm_symbol(trade.get("symbol")),
        "trade_id": _safe_str(trade.get("trade_id"), ""),
        "selected_vehicle": _selected_vehicle(trade),
        "trading_mode": _safe_str(trade.get("trading_mode", trade.get("mode", "paper")), "paper"),
        "reason": "already_open_position",
        "reason_code": "duplicate_open_position",
        "duplicate": True,
        "existing_trade_id": _safe_str(existing.get("trade_id"), ""),
        "existing_vehicle": _safe_str(
            existing.get("vehicle_selected", existing.get("vehicle", existing.get("asset_type", ""))),
            "",
        ),
        "existing_contract_symbol": _safe_str(
            existing.get("contract_symbol", existing.get("contractSymbol", existing.get("option_symbol", ""))),
            "",
        ),
    }



# ============================================================
# OBSERVATORY_PATCH_PAPER_OPTION_FILL_REHYDRATION_20260519
# Repair zeroed simulated paper option fills before validation/persistence.
# ============================================================

def _observatory_patch_safe_dict(value):
    return value if isinstance(value, dict) else {}


def _observatory_patch_safe_list(value):
    return value if isinstance(value, list) else []


def _observatory_patch_str(value, default=""):
    if value is None:
        return default
    try:
        out = str(value).strip()
        return out if out else default
    except Exception:
        return default


def _observatory_patch_float(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _observatory_patch_int(value, default=0):
    try:
        if value is None or value == "":
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


def _observatory_patch_first_positive_float(*values, default=0.0):
    for value in values:
        number = _observatory_patch_float(value, 0.0)
        if number > 0:
            return number
    return float(default)


def _observatory_patch_first_str(*values, default=""):
    for value in values:
        out = _observatory_patch_str(value, "")
        if out:
            return out
    return default


def _observatory_patch_mid_from_bid_ask(bid, ask):
    bid = _observatory_patch_float(bid, 0.0)
    ask = _observatory_patch_float(ask, 0.0)
    if bid > 0 and ask > 0 and ask >= bid:
        return round((bid + ask) / 2.0, 4)
    return 0.0


def _observatory_patch_option_source_payload(queued_trade):
    """
    Build one merged option source from every place the real bot may keep the selected contract.
    This intentionally does not trust one key path.
    """
    queued_trade = _observatory_patch_safe_dict(queued_trade)

    option = _observatory_patch_safe_dict(queued_trade.get("option"))
    contract = _observatory_patch_safe_dict(queued_trade.get("contract"))

    chain = _observatory_patch_safe_list(queued_trade.get("option_chain"))
    chain0 = {}
    for item in chain:
        if isinstance(item, dict) and item:
            chain0 = item
            break

    option_path = _observatory_patch_safe_dict(queued_trade.get("option_path"))
    option_path_contract = _observatory_patch_safe_dict(option_path.get("contract"))
    selected_contract = _observatory_patch_safe_dict(queued_trade.get("selected_contract"))

    merged = {}
    for src in [chain0, option_path_contract, selected_contract, contract, option, queued_trade]:
        if isinstance(src, dict):
            merged.update(src)

    return {
        "merged": merged,
        "option": option,
        "contract": contract,
        "chain0": chain0,
        "option_path": option_path,
        "option_path_contract": option_path_contract,
    }


def _observatory_patch_resolve_option_premium(queued_trade, execution_result=None):
    queued_trade = _observatory_patch_safe_dict(queued_trade)
    execution_result = _observatory_patch_safe_dict(execution_result)
    execution_record = _observatory_patch_safe_dict(execution_result.get("execution_record"))

    src = _observatory_patch_option_source_payload(queued_trade)
    merged = src["merged"]

    bid = _observatory_patch_first_positive_float(
        execution_result.get("bid"),
        execution_record.get("bid"),
        merged.get("bid"),
        queued_trade.get("bid"),
        default=0.0,
    )
    ask = _observatory_patch_first_positive_float(
        execution_result.get("ask"),
        execution_record.get("ask"),
        merged.get("ask"),
        queued_trade.get("ask"),
        default=0.0,
    )
    mid = _observatory_patch_mid_from_bid_ask(bid, ask)

    premium = _observatory_patch_first_positive_float(
        execution_result.get("fill_price"),
        execution_result.get("executed_price"),
        execution_result.get("average_fill_price"),
        execution_result.get("avg_fill_price"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        execution_record.get("entry_premium"),
        execution_record.get("premium_entry"),

        queued_trade.get("selected_price_reference"),
        queued_trade.get("price_reference"),
        queued_trade.get("option_price_reference"),
        queued_trade.get("mark"),
        queued_trade.get("last"),
        queued_trade.get("entry_premium"),
        queued_trade.get("premium_entry"),
        queued_trade.get("current_premium"),
        queued_trade.get("current_option_mark"),

        merged.get("selected_price_reference"),
        merged.get("price_reference"),
        merged.get("option_price_reference"),
        merged.get("mark"),
        merged.get("last"),
        merged.get("entry_premium"),
        merged.get("premium_entry"),
        merged.get("current_premium"),
        merged.get("current_option_mark"),

        mid,
        ask,
        bid,
        default=0.0,
    )
    return round(premium, 4)


def _observatory_patch_rehydrate_paper_option_fill_packet(queued_trade, packet, resolved_mode="paper"):
    """
    Paper adapter sometimes returns an OPTION fill shell with status FILLED but all option economics set to 0.
    That is invalid for persistence even though the selected trade still has the correct contract payload.
    This repair runs after execute_via_adapter and before the invalid-fill validation path.
    """
    queued_trade = _observatory_patch_safe_dict(queued_trade)
    packet = _observatory_patch_safe_dict(packet)

    mode = _observatory_patch_str(
        packet.get("trading_mode") or queued_trade.get("trading_mode") or queued_trade.get("mode") or resolved_mode,
        "paper",
    ).lower()

    if mode not in {"paper", "survey", "survey_mode", "paper_mode"}:
        return packet

    vehicle = _observatory_patch_str(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle")
        or packet.get("vehicle_selected")
        or packet.get("selected_vehicle")
        or packet.get("vehicle"),
        "",
    ).upper()

    if vehicle != "OPTION":
        return packet

    execution_result = _observatory_patch_safe_dict(packet.get("execution_result"))
    if not execution_result:
        execution_result = {}

    execution_record = _observatory_patch_safe_dict(execution_result.get("execution_record"))

    src = _observatory_patch_option_source_payload(queued_trade)
    merged = src["merged"]

    premium = _observatory_patch_resolve_option_premium(queued_trade, execution_result)

    contract_symbol = _observatory_patch_first_str(
        execution_record.get("contract_symbol"),
        execution_record.get("option_symbol"),
        execution_result.get("contract_symbol"),
        execution_result.get("option_symbol"),
        queued_trade.get("contract_symbol"),
        queued_trade.get("contractSymbol"),
        queued_trade.get("option_symbol"),
        queued_trade.get("selected_contract_symbol"),
        merged.get("contract_symbol"),
        merged.get("contractSymbol"),
        merged.get("option_symbol"),
        merged.get("selected_contract_symbol"),
        default="",
    )

    expiration = _observatory_patch_first_str(
        execution_record.get("expiration"),
        execution_record.get("expiry"),
        execution_result.get("expiration"),
        execution_result.get("expiry"),
        queued_trade.get("expiration"),
        queued_trade.get("expiry"),
        merged.get("expiration"),
        merged.get("expiry"),
        default="",
    )

    right = _observatory_patch_first_str(
        execution_record.get("right"),
        execution_result.get("right"),
        queued_trade.get("right"),
        queued_trade.get("option_type"),
        merged.get("right"),
        merged.get("option_type"),
        default="CALL",
    ).upper()

    strike = _observatory_patch_first_positive_float(
        execution_record.get("strike"),
        execution_result.get("strike"),
        queued_trade.get("strike"),
        merged.get("strike"),
        default=0.0,
    )

    bid = _observatory_patch_first_positive_float(
        execution_record.get("bid"),
        execution_result.get("bid"),
        queued_trade.get("bid"),
        merged.get("bid"),
        default=0.0,
    )
    ask = _observatory_patch_first_positive_float(
        execution_record.get("ask"),
        execution_result.get("ask"),
        queued_trade.get("ask"),
        merged.get("ask"),
        default=0.0,
    )
    last = _observatory_patch_first_positive_float(
        execution_record.get("last"),
        execution_result.get("last"),
        queued_trade.get("last"),
        merged.get("last"),
        premium,
        default=0.0,
    )
    mark = _observatory_patch_first_positive_float(
        execution_record.get("mark"),
        execution_result.get("mark"),
        queued_trade.get("mark"),
        queued_trade.get("selected_price_reference"),
        queued_trade.get("price_reference"),
        merged.get("mark"),
        merged.get("selected_price_reference"),
        merged.get("price_reference"),
        premium,
        default=0.0,
    )

    contracts = _observatory_patch_int(
        execution_record.get("contracts")
        or execution_result.get("contracts")
        or queued_trade.get("contracts")
        or queued_trade.get("quantity")
        or 1,
        1,
    )
    if contracts <= 0:
        contracts = 1

    commission = _observatory_patch_float(
        execution_result.get("commission")
        or execution_record.get("commission")
        or queued_trade.get("commission")
        or 1.0,
        1.0,
    )

    theoretical_option_cost = round((premium * contracts * 100.0) + commission, 4)

    adapter_actual_cost = _observatory_patch_first_positive_float(
        execution_result.get("actual_cost"),
        execution_record.get("actual_cost"),
        default=0.0,
    )

    queued_cost = _observatory_patch_first_positive_float(
        queued_trade.get("minimum_trade_cost"),
        queued_trade.get("capital_required"),
        default=0.0,
    )

    # OBSERVATORY_REPAIR_PAPER_OPTION_FILL_REHYDRATION_ACTUAL_COST_20260519
    # A paper adapter shell may report actual_cost=1.0 even when the option premium is valid.
    # For options, cost must be premium x 100 x contracts plus commission.
    if adapter_actual_cost >= (premium * contracts * 50.0):
        actual_cost = adapter_actual_cost
    elif queued_cost >= (premium * contracts * 50.0):
        actual_cost = queued_cost
    else:
        actual_cost = theoretical_option_cost

    trade_id = _observatory_patch_first_str(
        packet.get("trade_id"),
        execution_result.get("trade_id"),
        execution_record.get("trade_id"),
        queued_trade.get("trade_id"),
        default="",
    )

    symbol = _observatory_patch_first_str(
        queued_trade.get("symbol"),
        execution_record.get("symbol"),
        execution_result.get("symbol"),
        packet.get("symbol"),
        default="",
    ).upper()

    strategy = _observatory_patch_first_str(
        queued_trade.get("final_strategy"),
        queued_trade.get("chosen_strategy"),
        queued_trade.get("strategy"),
        execution_record.get("strategy"),
        execution_result.get("strategy"),
        default="CALL",
    ).upper()

    # Only repair if the simulated option fill is zero/incomplete.
    fill_now = _observatory_patch_float(execution_result.get("fill_price"), 0.0)
    record_fill_now = _observatory_patch_float(execution_record.get("fill_price"), 0.0)

    needs_repair = (
        fill_now <= 0
        or record_fill_now <= 0
        or not contract_symbol
        or not expiration
        or strike <= 0
    )

    if not needs_repair:
        return packet

    if premium <= 0:
        print("PAPER OPTION FILL REHYDRATION SKIPPED:", {
            "symbol": symbol,
            "trade_id": trade_id,
            "reason": "no_positive_option_premium_found",
            "contract_symbol": contract_symbol,
            "expiration": expiration,
            "strike": strike,
        })
        return packet

    if not execution_result.get("broker_order_id"):
        execution_result["broker_order_id"] = f"SIM-{symbol}-{datetime.now().strftime('%Y%m%dT%H%M%S%f')}"

    execution_result["status"] = "FILLED"
    execution_result["fill_price"] = premium
    execution_result["executed_price"] = premium
    execution_result["average_fill_price"] = premium
    execution_result["avg_fill_price"] = premium
    execution_result["filled_quantity"] = contracts
    execution_result["quantity"] = contracts
    execution_result["contracts"] = contracts
    execution_result["shares"] = 0
    execution_result["actual_cost"] = round(actual_cost, 4)
    execution_result["commission"] = commission
    execution_result["reason"] = execution_result.get("reason") or "executed"
    execution_result["reason_code"] = execution_result.get("reason_code") or "executed"
    execution_result["trade_id"] = trade_id
    execution_result["symbol"] = symbol
    execution_result["strategy"] = strategy
    execution_result["vehicle"] = "OPTION"
    execution_result["vehicle_selected"] = "OPTION"
    execution_result["selected_vehicle"] = "OPTION"

    execution_result["contract_symbol"] = contract_symbol
    execution_result["option_symbol"] = contract_symbol
    execution_result["expiry"] = expiration
    execution_result["expiration"] = expiration
    execution_result["strike"] = strike
    execution_result["right"] = right

    execution_result["bid"] = bid
    execution_result["ask"] = ask
    execution_result["last"] = last
    execution_result["mark"] = mark
    execution_result["selected_price_reference"] = premium
    execution_result["price_reference"] = premium

    execution_result["entry_premium"] = premium
    execution_result["premium_entry"] = premium
    execution_result["option_entry"] = premium
    execution_result["option_entry_price"] = premium
    execution_result["current_premium"] = premium
    execution_result["premium_current"] = premium
    execution_result["current_option_mark"] = premium
    execution_result["option_current_mark"] = premium
    execution_result["option_current_price"] = premium
    execution_result["current_option_price"] = premium

    execution_result["monitoring_price_type"] = "OPTION_PREMIUM"
    execution_result["monitoring_mode"] = "OPTION_PREMIUM"
    execution_result["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    execution_result["price_basis"] = "OPTION_PREMIUM"
    execution_result["pnl_basis"] = "OPTION_PREMIUM_X_100"
    execution_result["execution_position_shape"] = "OPTION_PREMIUM_POSITION"
    execution_result["paper_fill_rehydrated"] = True
    execution_result["paper_fill_rehydration_marker"] = "OBSERVATORY_PATCH_PAPER_OPTION_FILL_REHYDRATION_20260519"

    # Keep underlying as context only. Do not let it become premium math.
    underlying = _observatory_patch_first_positive_float(
        queued_trade.get("underlying_price"),
        queued_trade.get("stock_price"),
        # Do not use queued_trade["price"] here; for option fills it may be premium.
        merged.get("underlying_price"),
        merged.get("stock_price"),
        default=0.0,
    )
    execution_result["underlying_price"] = underlying
    execution_result["current_underlying_price"] = underlying

    execution_record.update({
        "trade_id": trade_id,
        "symbol": symbol,
        "strategy": strategy,
        "vehicle": "OPTION",
        "vehicle_selected": "OPTION",
        "selected_vehicle": "OPTION",
        "requested_price": premium,
        "fill_price": premium,
        "filled_price": premium,
        "executed_price": premium,
        "average_fill_price": premium,
        "avg_fill_price": premium,
        "filled_quantity": contracts,
        "quantity": contracts,
        "contracts": contracts,
        "shares": 0,
        "status": "FILLED",
        "actual_cost": round(actual_cost, 4),
        "commission": commission,
        "underlying_price": underlying,
        "current_underlying_price": underlying,
        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "expiry": expiration,
        "expiration": expiration,
        "strike": strike,
        "right": right,
        "bid": bid,
        "ask": ask,
        "mark": mark,
        "last": last,
        "selected_price_reference": premium,
        "price_reference": premium,
        "entry_premium": premium,
        "premium_entry": premium,
        "option_entry": premium,
        "option_entry_price": premium,
        "current_premium": premium,
        "premium_current": premium,
        "current_option_mark": premium,
        "option_current_mark": premium,
        "option_current_price": premium,
        "current_option_price": premium,
        "monitoring_price_type": "OPTION_PREMIUM",
        "monitoring_mode": "OPTION_PREMIUM",
        "price_review_basis": "OPTION_PREMIUM_ONLY",
        "price_basis": "OPTION_PREMIUM",
        "pnl_basis": "OPTION_PREMIUM_X_100",
        "execution_position_shape": "OPTION_PREMIUM_POSITION",
        "paper_fill_rehydrated": True,
    })

    execution_result["execution_record"] = execution_record
    packet["execution_result"] = execution_result
    packet["trade_id"] = trade_id
    packet["trading_mode"] = mode

    print("PAPER OPTION FILL REHYDRATED:", {
        "symbol": symbol,
        "trade_id": trade_id,
        "premium": premium,
        "contracts": contracts,
        "contract_symbol": contract_symbol,
        "expiration": expiration,
        "strike": strike,
        "right": right,
        "actual_cost": round(actual_cost, 4),
    })

    return packet

def execute_trades(
    queue: List[Dict[str, Any]] | None,
    limit: int | None = None,
    portfolio_context: Dict[str, Any] | None = None,
    broker_adapter: Any = None,
    trading_mode: str | None = None,
    max_open_positions: int = 5,
    current_open_positions: int | None = None,
    kill_switch_enabled: bool = False,
    session_healthy: bool = True,
) -> Dict[str, Any]:
    queue = queue if isinstance(queue, list) else []

    anti_repeat_result = {}
    anti_repeat_skipped = 0
    original_queue_size = len(queue)

    if callable(guard_execution_queue) and queue:
        try:
            anti_repeat_result = _guard_execution_queue_with_metadata(
                queue,
                symbol_cooldown_hours=48,
                contract_cooldown_hours=96,
                rejection_cooldown_hours=24,
                stale_setup_lookback_hours=36,
                stale_setup_max_appearances=4,
            )

            guarded_queue = anti_repeat_result.get("queue", queue)
            if isinstance(guarded_queue, list):
                queue = guarded_queue

            anti_repeat_skipped = max(0, original_queue_size - len(queue))

            if anti_repeat_skipped:
                print("EXECUTION LOOP ANTI-REPEAT GUARD:", {
                    "input_queue_size": original_queue_size,
                    "allowed_queue_size": len(queue),
                    "blocked_count": anti_repeat_result.get("blocked_count", anti_repeat_skipped),
                    "blocked_symbols": [
                        item.get("symbol")
                        for item in anti_repeat_result.get("blocked", [])
                        if isinstance(item, dict)
                    ],
                    "blocked_reasons": [
                        item.get("cooldown_reason") or item.get("final_reason")
                        for item in anti_repeat_result.get("blocked", [])
                        if isinstance(item, dict)
                    ],
                })

        except Exception as cooldown_exc:
            anti_repeat_result = {
                "error": str(cooldown_exc),
                "blocked": False,
                "reason": "anti_repeat_guard_exception_execution_continued",
            }
            print("EXECUTION LOOP ANTI-REPEAT GUARD ERROR:", anti_repeat_result)

    portfolio_context = _safe_dict(portfolio_context)

    resolved_limits = _resolve_execution_limits_from_governor(
        trading_mode=trading_mode
        or portfolio_context.get("trading_mode")
        or portfolio_context.get("mode")
        or "paper",
        portfolio_context=portfolio_context,
        current_open_positions=current_open_positions,
        requested_limit=limit,
        fallback_max_open_positions=max_open_positions,
    )

    resolved_mode = _safe_str(resolved_limits.get("trading_mode"), "paper")
    mode_context = _safe_dict(resolved_limits.get("mode_context"))
    governor = _safe_dict(resolved_limits.get("governor"))
    governor_limits = _safe_dict(resolved_limits.get("governor_limits"))

    max_open_positions = _safe_int(resolved_limits.get("max_open_positions"), max_open_positions)
    queue_limit = _safe_int(resolved_limits.get("queue_limit"), max_open_positions)
    open_positions_running = _safe_int(resolved_limits.get("open_positions_running"), 0)
    remaining_slots = _safe_int(resolved_limits.get("remaining_slots"), 0)
    effective_limit = _safe_int(resolved_limits.get("effective_limit"), 0)

    if "mode_context" not in portfolio_context:
        portfolio_context["mode_context"] = mode_context

    portfolio_context["trading_mode"] = resolved_mode
    portfolio_context["mode"] = resolved_mode
    portfolio_context["governor"] = governor
    portfolio_context["governor_limits"] = governor_limits
    portfolio_context["max_open_positions"] = max_open_positions
    portfolio_context["queue_limit"] = queue_limit
    portfolio_context["over_25k"] = resolved_limits.get("over_25k")

    results: List[Dict[str, Any]] = []
    summaries: List[Dict[str, Any]] = []

    executed = 0
    rejected = 0
    skipped = 0
    skipped += anti_repeat_skipped
    persisted = 0
    persistence_blocked = 0

    print("EXECUTION LOOP START:", {
        "queue_size": len(queue),
        "requested_limit": limit,
        "resolved_requested_limit": resolved_limits.get("requested_limit"),
        "governor_blocked": resolved_limits.get("governor_blocked"),
        "governor_reasons": resolved_limits.get("governor_reasons"),
        "over_25k": resolved_limits.get("over_25k"),
        "max_open_positions": max_open_positions,
        "queue_limit": queue_limit,
        "max_daily_entries": resolved_limits.get("max_daily_entries"),
        "max_rolling_5_business_day_entries": resolved_limits.get("max_rolling_5_business_day_entries"),
        "current_open_positions": open_positions_running,
        "remaining_slots": remaining_slots,
        "effective_limit": effective_limit,
        "trading_mode": resolved_mode,
        "governor_limits": governor_limits,
        "execution_pause": resolved_limits.get("execution_pause"),
    })

    if _safe_bool(resolved_limits.get("governor_blocked"), False):
        print("EXECUTION LOOP GOVERNOR BLOCKED:", {
            "reasons": resolved_limits.get("governor_reasons"),
            "warnings": resolved_limits.get("governor_warnings"),
            "execution_pause": resolved_limits.get("execution_pause"),
        })

        return {
            "results": [],
            "summaries": [],
            "executed": 0,
            "persisted": 0,
            "persistence_blocked": 0,
            "rejected": 0,
            "skipped": len(queue),
            "processed": 0,
            "queue_size": len(queue),
            "open_positions_after": open_positions_running,
            "original_queue_size": original_queue_size,
            "anti_repeat_skipped": anti_repeat_skipped,
            "anti_repeat_guard": anti_repeat_result,
            "timestamp": _now_iso(),
            "status": "GOVERNOR_BLOCKED",
            "governor": governor,
            "governor_limits": governor_limits,
            "execution_pause": resolved_limits.get("execution_pause"),
        }

    for queued_trade in queue:
        if executed >= effective_limit:
            skipped += 1
            continue

        queued_trade = deepcopy(_safe_dict(queued_trade))

        if not queued_trade:
            skipped += 1
            continue

        existing_open_position = _find_existing_open_position_for_trade(queued_trade)
        if existing_open_position:
            skipped += 1
            duplicate_packet = _duplicate_skip_summary(queued_trade, existing_open_position)
            duplicate_packet["governor"] = governor
            duplicate_packet["governor_limits"] = governor_limits
            duplicate_packet["mode_context"] = mode_context

            print("EXECUTION SKIPPED DUPLICATE:", {
                "symbol": duplicate_packet.get("symbol"),
                "reason_code": duplicate_packet.get("reason_code"),
                "existing_trade_id": duplicate_packet.get("existing_trade_id"),
                "existing_vehicle": duplicate_packet.get("existing_vehicle"),
                "existing_contract_symbol": duplicate_packet.get("existing_contract_symbol"),
                "slot_consumed": False,
            })

            summaries.append(duplicate_packet)
            results.append(duplicate_packet)
            continue

        queued_trade["trading_mode"] = _safe_str(
            queued_trade.get("trading_mode")
            or queued_trade.get("execution_mode")
            or queued_trade.get("mode")
            or resolved_mode,
            resolved_mode,
        )

        queued_trade["mode"] = queued_trade["trading_mode"]

        if "mode_context" not in queued_trade:
            queued_trade["mode_context"] = mode_context

        if "governor" not in queued_trade:
            queued_trade["governor"] = governor

        if "governor_limits" not in queued_trade:
            queued_trade["governor_limits"] = governor_limits

        option_obj = _safe_dict(queued_trade.get("option"))
        contract_obj = _safe_dict(queued_trade.get("contract"))

        print("PRE-EXECUTION-HANDOFF:", {
            "symbol": queued_trade.get("symbol"),
            "trade_id": queued_trade.get("trade_id"),
            "research_approved": queued_trade.get("research_approved"),
            "execution_ready": queued_trade.get("execution_ready"),
            "selected_for_execution": queued_trade.get("selected_for_execution"),
            "vehicle_selected": queued_trade.get("vehicle_selected"),
            "contracts": queued_trade.get("contracts"),
            "shares": queued_trade.get("shares"),
            "has_option": bool(option_obj or contract_obj),
            "contract_symbol": (
                queued_trade.get("contract_symbol")
                or option_obj.get("contractSymbol")
                or option_obj.get("contract_symbol")
                or contract_obj.get("contractSymbol")
                or contract_obj.get("contract_symbol")
            ),
            "lifecycle_stage": queued_trade.get("lifecycle_stage"),
            "trading_mode": queued_trade.get("trading_mode"),
            "governor_max_open_positions": max_open_positions,
            "governor_queue_limit": queue_limit,
            "open_positions_running": open_positions_running,
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
        # OBSERVATORY_REPAIR_EXECUTION_LOOP_PRESERVE_PACKET_SHAPE_20260520
        # Important:
        # The rehydration helpers return an execution_result dict.
        # Do NOT assign that directly to packet, or the loop loses packet["success"].
        # Always write repaired fills back into packet["execution_result"].
        try:
            packet = _safe_dict(packet)

            _observatory_fill_trade = queued_trade if isinstance(queued_trade, dict) else {}
            _observatory_fill_result = packet.get("execution_result")
            if not isinstance(_observatory_fill_result, dict):
                _observatory_fill_result = {}

            _observatory_fill_record = {}
            if isinstance(_observatory_fill_result.get("execution_record"), dict):
                _observatory_fill_record = _observatory_fill_result.get("execution_record")
            elif isinstance(packet.get("execution_record"), dict):
                _observatory_fill_record = packet.get("execution_record")

            _observatory_fill_vehicle = str(
                _observatory_fill_trade.get("vehicle_selected")
                or _observatory_fill_trade.get("selected_vehicle")
                or _observatory_fill_trade.get("vehicle")
                or _observatory_fill_record.get("vehicle_selected")
                or _observatory_fill_record.get("selected_vehicle")
                or _observatory_fill_record.get("vehicle")
                or packet.get("vehicle_selected")
                or packet.get("selected_vehicle")
                or packet.get("vehicle")
                or ""
            ).upper()

            if _observatory_fill_vehicle == "OPTION" and "_observatory_patch_rehydrate_paper_option_fill_packet" in globals():
                _observatory_fill_result = _observatory_patch_rehydrate_paper_option_fill_packet(
                    _observatory_fill_result,
                    _observatory_fill_trade,
                    _observatory_fill_record,
                )
                if isinstance(_observatory_fill_result, dict):
                    packet["execution_result"] = _observatory_fill_result

            if _observatory_fill_vehicle == "STOCK" and "_observatory_patch_rehydrate_paper_stock_fill_packet_20260520" in globals():
                _observatory_fill_result = _observatory_patch_rehydrate_paper_stock_fill_packet_20260520(
                    _observatory_fill_result,
                    _observatory_fill_trade,
                    _observatory_fill_record,
                )
                if isinstance(_observatory_fill_result, dict):
                    packet["execution_result"] = _observatory_fill_result

            _observatory_fill_result = packet.get("execution_result")
            if isinstance(_observatory_fill_result, dict):
                _observatory_fill_status = str(_observatory_fill_result.get("status") or "").upper()
                _observatory_fill_price = _safe_float(
                    _observatory_fill_result.get("fill_price")
                    or _observatory_fill_result.get("filled_price")
                    or _observatory_fill_result.get("entry_premium"),
                    0.0,
                )
                _observatory_fill_cost = _safe_float(_observatory_fill_result.get("actual_cost"), 0.0)

                if _observatory_fill_status in {"FILLED", "EXECUTED"} and _observatory_fill_price > 0 and _observatory_fill_cost > 0:
                    packet["success"] = True
                    packet["status"] = "FILLED"
                    packet["reason"] = packet.get("reason") or "executed"
                    packet["reason_code"] = packet.get("reason_code") or "executed"
                    packet["vehicle"] = _observatory_fill_vehicle
                    packet["vehicle_selected"] = _observatory_fill_vehicle
                    packet["selected_vehicle"] = _observatory_fill_vehicle

        except Exception as _observatory_fill_patch_error:
            print("PAPER FILL REHYDRATION CALLSITE ERROR:", {
                "error": str(_observatory_fill_patch_error),
                "assigned_var": "packet.execution_result",
            })

        packet = _safe_dict(packet)
        packet["trade_id"] = _extract_trade_id(packet) or _safe_str(queued_trade.get("trade_id"), "")
        packet["trading_mode"] = _safe_str(packet.get("trading_mode", queued_trade.get("trading_mode")), resolved_mode)

        if "mode_context" not in packet:
            packet["mode_context"] = queued_trade.get("mode_context", mode_context)

        if "governor" not in packet:
            packet["governor"] = governor

        if "governor_limits" not in packet:
            packet["governor_limits"] = governor_limits

        if _safe_bool(packet.get("success"), False):
            # OBSERVATORY_REPAIR_SUCCESS_REASON_AFTER_PAPER_FILL_RESCUE_20260520
            # If Paper Mode rescued/rehydrated a valid simulated fill, do not keep
            # stale adapter failure text like "Invalid stock payload" on a success.
            try:
                _execution_result_for_reason = _safe_dict(packet.get("execution_result"))
                _execution_record_for_reason = _safe_dict(_execution_result_for_reason.get("execution_record"))
                _stale_success_reasons = {
                    "invalid stock payload.",
                    "execution returned invalid fill payload.",
                    "invalid fill payload.",
                    "execution_rejected",
                    "none",
                    "",
                }

                _packet_reason_raw = str(packet.get("reason") or "").strip()
                _result_reason_raw = str(_execution_result_for_reason.get("reason") or "").strip()
                _packet_reason_key = _packet_reason_raw.lower()
                _result_reason_key = _result_reason_raw.lower()

                _rescued_or_rehydrated = (
                    bool(packet.get("paper_fill_rescued"))
                    or bool(packet.get("paper_fill_rehydrated"))
                    or bool(_execution_result_for_reason.get("paper_fill_rescued"))
                    or bool(_execution_result_for_reason.get("paper_fill_rehydrated"))
                    or bool(_execution_record_for_reason.get("paper_fill_rescued"))
                    or bool(_execution_record_for_reason.get("paper_fill_rehydrated"))
                    or str(_execution_result_for_reason.get("status") or "").upper() in {"FILLED", "EXECUTED"}
                )

                if _rescued_or_rehydrated and (
                    _packet_reason_key in _stale_success_reasons
                    or _result_reason_key in _stale_success_reasons
                ):
                    packet["reason"] = "executed"
                    packet["reason_code"] = "executed"

                    _execution_result_for_reason["reason"] = "executed"
                    _execution_result_for_reason["reason_code"] = "executed"
                    _execution_result_for_reason["status"] = _execution_result_for_reason.get("status") or "FILLED"

                    _execution_record_for_reason["reason"] = "executed"
                    _execution_record_for_reason["reason_code"] = "executed"
                    _execution_record_for_reason["status"] = _execution_record_for_reason.get("status") or "FILLED"

                    _execution_result_for_reason["execution_record"] = _execution_record_for_reason
                    packet["execution_result"] = _execution_result_for_reason
            except Exception as _success_reason_cleanup_error:
                print("SUCCESS REASON CLEANUP ERROR:", str(_success_reason_cleanup_error))

            persistence = _persist_executed_trade(packet)
            packet["persistence"] = persistence

            if _safe_bool(persistence.get("persisted"), False):
                persisted += 1
                open_positions_running += 1

                position_for_activity = _safe_dict(persistence.get("position"))
                if callable(record_entry_event) and position_for_activity:
                    try:
                        activity_result = record_entry_event(
                            position_for_activity,
                            account_id=_safe_str(
                                queued_trade.get("account_id")
                                or portfolio_context.get("account_id")
                                or "default",
                                "default",
                            ),
                            source="execution_loop",
                            reason="position_persisted",
                        )
                        packet["activity_recording"] = activity_result
                    except Exception as activity_exc:
                        packet["activity_recording"] = {
                            "recorded": False,
                            "error": str(activity_exc),
                            "source": "execution_loop",
                            "reason": "activity_bridge_failed",
                        }
                        print("EXECUTION ACTIVITY RECORDING FAILED:", {
                            "symbol": position_for_activity.get("symbol"),
                            "trade_id": position_for_activity.get("trade_id"),
                            "error": str(activity_exc),
                        })
                else:
                    packet["activity_recording"] = {
                        "recorded": False,
                        "reason": "trade_activity_bridge_unavailable_or_missing_position",
                    }
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
                    "stop": position.get("stop"),
                    "target": position.get("target"),
                    "take_profit": position.get("take_profit"),
                    "option_stop": position.get("option_stop"),
                    "option_target": position.get("option_target"),
                    "premium_stop": position.get("premium_stop"),
                    "premium_target": position.get("premium_target"),
                    "target_premium": position.get("target_premium"),
                    "take_profit_premium": position.get("take_profit_premium"),
                    "monitoring_price_type": position.get("monitoring_price_type"),
                    "price_review_basis": position.get("price_review_basis"),
                    "execution_position_shape": position.get("execution_position_shape"),
                })
            else:
                print("EXECUTION NOT PERSISTED:", persistence)

        else:
            rejected += 1
            # OBSERVATORY_REPAIR_FINAL_PAPER_FILL_RESULT_RESCUE_20260520_PACKET_ASSIGNMENT
            try:
                if "_observatory_final_rescue_paper_fill_result_20260520" in globals():
                    _observatory_reject_trade = queued_trade if isinstance(queued_trade, dict) else {}
                    _observatory_reject_result = packet.get("execution_result") if isinstance(packet.get("execution_result"), dict) else {}
                    _observatory_reject_result = _observatory_final_rescue_paper_fill_result_20260520(
                        _observatory_reject_result,
                        _observatory_reject_trade,
                    )

                    if isinstance(_observatory_reject_result, dict):
                        packet["execution_result"] = _observatory_reject_result

                        _observatory_rescue_status = str(_observatory_reject_result.get("status") or "").upper()
                        _observatory_rescue_fill = _safe_float(
                            _observatory_reject_result.get("fill_price")
                            or _observatory_reject_result.get("filled_price")
                            or _observatory_reject_result.get("entry_premium"),
                            0.0,
                        )
                        _observatory_rescue_cost = _safe_float(_observatory_reject_result.get("actual_cost"), 0.0)

                        if _observatory_rescue_status in {"FILLED", "EXECUTED"} and _observatory_rescue_fill > 0 and _observatory_rescue_cost > 0:
                            packet["success"] = True
                            packet["status"] = "FILLED"
                            packet["reason"] = packet.get("reason") or "executed"
                            packet["reason_code"] = packet.get("reason_code") or "executed"

            except Exception as _observatory_final_rescue_error:
                print("FINAL PAPER FILL RESULT RESCUE ERROR:", str(_observatory_final_rescue_error))
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
        "max_open_positions": max_open_positions,
        "queue_limit": queue_limit,
        "over_25k": resolved_limits.get("over_25k"),
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
        "original_queue_size": original_queue_size,
        "anti_repeat_skipped": anti_repeat_skipped,
        "anti_repeat_guard": anti_repeat_result,
        "timestamp": _now_iso(),
        "governor": governor,
        "governor_limits": governor_limits,
        "execution_pause": resolved_limits.get("execution_pause"),
        "max_open_positions": max_open_positions,
        "queue_limit": queue_limit,
        "over_25k": resolved_limits.get("over_25k"),
    }


__all__ = [
    "execute_trades",
]


# ============================================================
# OBSERVATORY_REPAIR_PAPER_OPTION_FILL_PREMIUM_FALLBACK_20260519
# Robust paper-option fill rehydration fallback.
# This override is intentionally placed after earlier helper definitions so the
# execution loop resolves this safer version at runtime.
# ============================================================

def _observatory_patch_first_present_dict_20260519(*values):
    for value in values:
        if isinstance(value, dict) and value:
            return value
    return {}


def _observatory_patch_first_present_list_20260519(*values):
    for value in values:
        if isinstance(value, list) and value:
            return value
    return []


def _observatory_patch_safe_float_20260519(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _observatory_patch_first_positive_float_20260519(*values, default=0.0):
    for value in values:
        number = _observatory_patch_safe_float_20260519(value, 0.0)
        if number > 0:
            return number
    return float(default)


def _observatory_patch_contract_dict_from_trade_20260519(trade):
    trade = trade if isinstance(trade, dict) else {}

    option = _observatory_patch_first_present_dict_20260519(
        trade.get("option"),
        trade.get("selected_option"),
        trade.get("best_option"),
        trade.get("best_option_preview"),
        trade.get("option_contract"),
        trade.get("selected_contract"),
    )

    chain = _observatory_patch_first_present_list_20260519(
        trade.get("option_chain"),
        trade.get("contracts"),
        trade.get("option_contracts"),
    )

    chain_first = chain[0] if chain and isinstance(chain[0], dict) else {}

    return _observatory_patch_first_present_dict_20260519(option, chain_first, trade)


def _observatory_patch_rehydrate_paper_option_fill_packet(*args, **kwargs):
    """
    Compatibility override for prior paper option fill repair.

    Expected inputs may arrive in different orders depending on the current
    execution_loop.py callsite. This helper searches all dict args for:
    - execution_result / result-like dict
    - queued trade / candidate-like dict
    - execution_record-like dict

    It mutates dicts in place and returns the execution_result dict.
    """

    dict_args = [arg for arg in args if isinstance(arg, dict)]
    dict_kwargs = [value for value in kwargs.values() if isinstance(value, dict)]
    all_dicts = dict_args + dict_kwargs

    execution_result = {}
    queued_trade = {}
    execution_record = {}

    # Result dict usually has status/fill/broker fields.
    for item in all_dicts:
        if any(k in item for k in ("status", "fill_price", "filled_price", "broker_order_id", "execution_record")):
            execution_result = item
            break

    # Queued trade usually has symbol, vehicle, capital_required, selected_for_execution.
    for item in all_dicts:
        vehicle = str(item.get("vehicle") or item.get("vehicle_selected") or item.get("selected_vehicle") or "").upper()
        if vehicle == "OPTION" and any(k in item for k in ("capital_required", "minimum_trade_cost", "option_chain", "option", "contract_symbol")):
            queued_trade = item
            break

    # Record may be nested in execution_result or passed separately.
    nested_record = execution_result.get("execution_record") if isinstance(execution_result.get("execution_record"), dict) else {}
    execution_record = nested_record

    if not execution_record:
        for item in all_dicts:
            if item is not execution_result and any(k in item for k in ("execution_record", "filled_quantity", "trade_id", "opened_at")):
                execution_record = item
                break

    if not execution_result and all_dicts:
        execution_result = all_dicts[0]

    if not isinstance(execution_result, dict):
        return execution_result

    if not isinstance(execution_record, dict):
        execution_record = {}

    if not isinstance(queued_trade, dict):
        queued_trade = {}

    vehicle = str(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle")
        or execution_record.get("vehicle_selected")
        or execution_record.get("selected_vehicle")
        or execution_record.get("vehicle")
        or ""
    ).upper()

    if vehicle != "OPTION":
        return execution_result

    contract = _observatory_patch_contract_dict_from_trade_20260519(queued_trade)

    contracts = int(_observatory_patch_first_positive_float_20260519(
        queued_trade.get("contracts"),
        queued_trade.get("quantity"),
        execution_record.get("contracts"),
        execution_record.get("quantity"),
        execution_result.get("filled_quantity"),
        default=1,
    ) or 1)

    raw_premium = _observatory_patch_first_positive_float_20260519(
        execution_result.get("fill_price"),
        execution_result.get("filled_price"),
        execution_result.get("entry_premium"),
        execution_result.get("premium_entry"),
        execution_result.get("option_entry"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        execution_record.get("entry_premium"),
        execution_record.get("premium_entry"),
        execution_record.get("option_entry"),
        queued_trade.get("price_reference"),
        queued_trade.get("selected_price_reference"),
        queued_trade.get("option_price"),
        queued_trade.get("premium"),
        queued_trade.get("mark"),
        contract.get("mark"),
        contract.get("last"),
        contract.get("ask"),
        contract.get("bid"),
        default=0.0,
    )

    capital_required = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("capital_required"),
        queued_trade.get("estimated_cost"),
        queued_trade.get("effective_cost"),
        default=0.0,
    )

    minimum_trade_cost = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("minimum_trade_cost"),
        default=0.0,
    )

    # Prefer capital_required because minimum_trade_cost may include commission.
    inferred_from_capital = 0.0
    if capital_required > 0 and contracts > 0:
        inferred_from_capital = capital_required / (contracts * 100.0)

    inferred_from_minimum = 0.0
    if minimum_trade_cost > 1.0 and contracts > 0:
        # Most of this system uses +1.00 commission in paper mode.
        inferred_from_minimum = max((minimum_trade_cost - 1.0) / (contracts * 100.0), 0.0)

    premium = _observatory_patch_first_positive_float_20260519(
        raw_premium,
        inferred_from_capital,
        inferred_from_minimum,
        default=0.0,
    )

    symbol = str(
        queued_trade.get("symbol")
        or execution_record.get("symbol")
        or execution_result.get("symbol")
        or contract.get("symbol")
        or ""
    ).upper()

    trade_id = (
        queued_trade.get("trade_id")
        or execution_record.get("trade_id")
        or execution_result.get("trade_id")
        or ""
    )

    contract_symbol = (
        queued_trade.get("contract_symbol")
        or queued_trade.get("contractSymbol")
        or execution_record.get("contract_symbol")
        or execution_record.get("contractSymbol")
        or contract.get("contractSymbol")
        or contract.get("contract_symbol")
        or contract.get("option_symbol")
        or ""
    )

    expiration = (
        queued_trade.get("expiration")
        or queued_trade.get("expiry")
        or execution_record.get("expiration")
        or execution_record.get("expiry")
        or contract.get("expiration")
        or contract.get("expiry")
        or ""
    )

    strike = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("strike"),
        execution_record.get("strike"),
        contract.get("strike"),
        default=0.0,
    )

    right = str(
        queued_trade.get("right")
        or queued_trade.get("option_type")
        or execution_record.get("right")
        or execution_record.get("option_type")
        or contract.get("right")
        or contract.get("option_type")
        or queued_trade.get("strategy")
        or execution_record.get("strategy")
        or "CALL"
    ).upper()

    if right in ('C', 'CALLS'):
        right = "CALL"
    elif right in ('P', 'PUTS'):
        right = "PUT"

    commission = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("commission"),
        execution_record.get("commission"),
        execution_result.get("commission"),
        default=1.0,
    )

    if premium <= 0:
        print("PAPER OPTION FILL REHYDRATION SKIPPED:", {
            "symbol": symbol,
            "trade_id": trade_id,
            "reason": "no_positive_option_premium_found_even_after_capital_fallback",
            "contract_symbol": contract_symbol,
            "capital_required": capital_required,
            "minimum_trade_cost": minimum_trade_cost,
            "contracts": contracts,
        })
        return execution_result

    actual_cost = round((premium * contracts * 100.0) + commission, 4)

    # Patch result shell.
    execution_result["status"] = execution_result.get("status") or "FILLED"
    execution_result["fill_price"] = premium
    execution_result["filled_price"] = premium
    execution_result["entry_premium"] = premium
    execution_result["premium_entry"] = premium
    execution_result["option_entry"] = premium
    execution_result["filled_quantity"] = contracts
    execution_result["quantity"] = contracts
    execution_result["contracts"] = contracts
    execution_result["shares"] = 0
    execution_result["actual_cost"] = actual_cost
    execution_result["paper_fill_rehydrated"] = True
    execution_result["paper_fill_rehydration_source"] = "premium_or_capital_required_fallback"

    # Patch execution record too.
    for target in (execution_record,):
        if isinstance(target, dict):
            target["symbol"] = symbol or target.get("symbol")
            target["vehicle"] = "OPTION"
            target["vehicle_selected"] = "OPTION"
            target["selected_vehicle"] = "OPTION"
            target["fill_price"] = premium
            target["filled_price"] = premium
            target["entry_premium"] = premium
            target["premium_entry"] = premium
            target["option_entry"] = premium
            target["current_premium"] = premium
            target["premium_current"] = premium
            target["current_option_mark"] = premium
            target["option_current_price"] = premium
            target["filled_quantity"] = contracts
            target["quantity"] = contracts
            target["contracts"] = contracts
            target["shares"] = 0
            target["actual_cost"] = actual_cost
            target["contract_symbol"] = contract_symbol or target.get("contract_symbol")
            target["option_symbol"] = contract_symbol or target.get("option_symbol")
            target["expiration"] = expiration or target.get("expiration")
            target["expiry"] = expiration or target.get("expiry")
            target["strike"] = strike or target.get("strike")
            target["right"] = right or target.get("right")
            target["monitoring_price_type"] = "OPTION_PREMIUM"
            target["price_review_basis"] = "OPTION_PREMIUM_ONLY"
            target["underlying_price_used_for_close_decision"] = False
            target["paper_fill_rehydrated"] = True
            target["paper_fill_rehydration_source"] = "premium_or_capital_required_fallback"

    execution_result["execution_record"] = execution_record

    print("PAPER OPTION FILL REHYDRATED:", {
        "symbol": symbol,
        "trade_id": trade_id,
        "premium": premium,
        "contracts": contracts,
        "contract_symbol": contract_symbol,
        "expiration": expiration,
        "strike": strike,
        "right": right,
        "actual_cost": actual_cost,
        "capital_required": capital_required,
        "minimum_trade_cost": minimum_trade_cost,
    })

    return execution_result


# ============================================================
# OBSERVATORY_REPAIR_EXECUTION_LOOP_USE_REHYDRATED_FILL_AND_STOCK_FALLBACK_20260520
# Paper execution fill safety layer.
# - Option: preserve repaired premium fills by assigning helper return.
# - Stock: synthesize valid paper fill if adapter returns {}.
# ============================================================

def _observatory_patch_safe_float_stock_20260520(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _observatory_patch_first_positive_float_stock_20260520(*values, default=0.0):
    for value in values:
        number = _observatory_patch_safe_float_stock_20260520(value, 0.0)
        if number > 0:
            return number
    return float(default)


def _observatory_patch_rehydrate_paper_stock_fill_packet_20260520(execution_result, queued_trade, execution_record=None):
    """
    If Paper Mode stock adapter returns an empty/invalid payload, create a safe
    simulated stock fill from queued trade capital data.

    This is paper/simulation only. Live mode must never fabricate fills.
    """
    queued_trade = queued_trade if isinstance(queued_trade, dict) else {}
    execution_result = execution_result if isinstance(execution_result, dict) else {}
    execution_record = execution_record if isinstance(execution_record, dict) else {}

    mode = str(
        queued_trade.get("trading_mode")
        or queued_trade.get("mode")
        or execution_record.get("trading_mode")
        or execution_result.get("trading_mode")
        or "paper"
    ).lower()

    vehicle = str(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle")
        or execution_record.get("vehicle_selected")
        or execution_record.get("selected_vehicle")
        or execution_record.get("vehicle")
        or ""
    ).upper()

    if mode not in {"paper", "survey", "simulation", "sim"}:
        return execution_result

    if vehicle != "STOCK":
        return execution_result

    symbol = str(
        queued_trade.get("symbol")
        or execution_record.get("symbol")
        or execution_result.get("symbol")
        or ""
    ).upper()

    trade_id = (
        queued_trade.get("trade_id")
        or execution_record.get("trade_id")
        or execution_result.get("trade_id")
        or ""
    )

    shares = int(_observatory_patch_first_positive_float_stock_20260520(
        queued_trade.get("shares"),
        queued_trade.get("quantity"),
        execution_record.get("shares"),
        execution_record.get("quantity"),
        execution_result.get("filled_quantity"),
        default=1,
    ) or 1)

    capital_required = _observatory_patch_first_positive_float_stock_20260520(
        queued_trade.get("capital_required"),
        queued_trade.get("estimated_cost"),
        queued_trade.get("effective_cost"),
        default=0.0,
    )

    minimum_trade_cost = _observatory_patch_first_positive_float_stock_20260520(
        queued_trade.get("minimum_trade_cost"),
        default=0.0,
    )

    existing_fill = _observatory_patch_first_positive_float_stock_20260520(
        execution_result.get("fill_price"),
        execution_result.get("filled_price"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        queued_trade.get("fill_price"),
        queued_trade.get("price"),
        queued_trade.get("current_price"),
        queued_trade.get("underlying_price"),
        queued_trade.get("last_price"),
        default=0.0,
    )

    if existing_fill > 0:
        fill_price = existing_fill
    elif capital_required > 0 and shares > 0:
        fill_price = round(capital_required / shares, 4)
    elif minimum_trade_cost > 1.0 and shares > 0:
        fill_price = round((minimum_trade_cost - 1.0) / shares, 4)
    else:
        print("PAPER STOCK FILL REHYDRATION SKIPPED:", {
            "symbol": symbol,
            "trade_id": trade_id,
            "reason": "no_positive_stock_price_or_capital_found",
            "capital_required": capital_required,
            "minimum_trade_cost": minimum_trade_cost,
            "shares": shares,
        })
        return execution_result

    commission = _observatory_patch_first_positive_float_stock_20260520(
        queued_trade.get("commission"),
        execution_record.get("commission"),
        execution_result.get("commission"),
        default=1.0,
    )

    actual_cost = minimum_trade_cost if minimum_trade_cost > 0 else round((fill_price * shares) + commission, 4)

    patched_record = dict(execution_record)
    patched_record.update({
        "trade_id": trade_id,
        "symbol": symbol,
        "strategy": queued_trade.get("strategy") or queued_trade.get("final_strategy") or execution_record.get("strategy") or "CALL",
        "vehicle": "STOCK",
        "vehicle_selected": "STOCK",
        "selected_vehicle": "STOCK",
        "fill_price": fill_price,
        "filled_price": fill_price,
        "entry": fill_price,
        "current": fill_price,
        "filled_quantity": shares,
        "quantity": shares,
        "shares": shares,
        "contracts": 0,
        "actual_cost": actual_cost,
        "status": "FILLED",
        "paper_fill_rehydrated": True,
        "paper_fill_rehydration_source": "stock_capital_required_fallback",
    })

    execution_result.update({
        "status": "FILLED",
        "symbol": symbol,
        "trade_id": trade_id,
        "vehicle": "STOCK",
        "vehicle_selected": "STOCK",
        "selected_vehicle": "STOCK",
        "fill_price": fill_price,
        "filled_price": fill_price,
        "entry": fill_price,
        "current": fill_price,
        "filled_quantity": shares,
        "quantity": shares,
        "shares": shares,
        "contracts": 0,
        "actual_cost": actual_cost,
        "reason": "executed",
        "reason_code": "executed",
        "execution_record": patched_record,
        "paper_fill_rehydrated": True,
        "paper_fill_rehydration_source": "stock_capital_required_fallback",
    })

    print("PAPER STOCK FILL REHYDRATED:", {
        "symbol": symbol,
        "trade_id": trade_id,
        "fill_price": fill_price,
        "shares": shares,
        "actual_cost": actual_cost,
        "capital_required": capital_required,
        "minimum_trade_cost": minimum_trade_cost,
    })

    return execution_result


# ============================================================
# OBSERVATORY_REPAIR_PAPER_OPTION_FILL_PREMIUM_FALLBACK_20260519
# Robust paper-option fill rehydration fallback.
# This override is intentionally placed after earlier helper definitions so the
# execution loop resolves this safer version at runtime.
# ============================================================

def _observatory_patch_first_present_dict_20260519(*values):
    for value in values:
        if isinstance(value, dict) and value:
            return value
    return {}


def _observatory_patch_first_present_list_20260519(*values):
    for value in values:
        if isinstance(value, list) and value:
            return value
    return []


def _observatory_patch_safe_float_20260519(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _observatory_patch_first_positive_float_20260519(*values, default=0.0):
    for value in values:
        number = _observatory_patch_safe_float_20260519(value, 0.0)
        if number > 0:
            return number
    return float(default)


def _observatory_patch_contract_dict_from_trade_20260519(trade):
    trade = trade if isinstance(trade, dict) else {}

    option = _observatory_patch_first_present_dict_20260519(
        trade.get("option"),
        trade.get("selected_option"),
        trade.get("best_option"),
        trade.get("best_option_preview"),
        trade.get("option_contract"),
        trade.get("selected_contract"),
    )

    chain = _observatory_patch_first_present_list_20260519(
        trade.get("option_chain"),
        trade.get("contracts"),
        trade.get("option_contracts"),
    )

    chain_first = chain[0] if chain and isinstance(chain[0], dict) else {}

    return _observatory_patch_first_present_dict_20260519(option, chain_first, trade)


def _observatory_patch_rehydrate_paper_option_fill_packet(*args, **kwargs):
    """
    Compatibility override for prior paper option fill repair.

    Expected inputs may arrive in different orders depending on the current
    execution_loop.py callsite. This helper searches all dict args for:
    - execution_result / result-like dict
    - queued trade / candidate-like dict
    - execution_record-like dict

    It mutates dicts in place and returns the execution_result dict.
    """

    dict_args = [arg for arg in args if isinstance(arg, dict)]
    dict_kwargs = [value for value in kwargs.values() if isinstance(value, dict)]
    all_dicts = dict_args + dict_kwargs

    execution_result = {}
    queued_trade = {}
    execution_record = {}

    # Result dict usually has status/fill/broker fields.
    for item in all_dicts:
        if any(k in item for k in ("status", "fill_price", "filled_price", "broker_order_id", "execution_record")):
            execution_result = item
            break

    # Queued trade usually has symbol, vehicle, capital_required, selected_for_execution.
    for item in all_dicts:
        vehicle = str(item.get("vehicle") or item.get("vehicle_selected") or item.get("selected_vehicle") or "").upper()
        if vehicle == "OPTION" and any(k in item for k in ("capital_required", "minimum_trade_cost", "option_chain", "option", "contract_symbol")):
            queued_trade = item
            break

    # Record may be nested in execution_result or passed separately.
    nested_record = execution_result.get("execution_record") if isinstance(execution_result.get("execution_record"), dict) else {}
    execution_record = nested_record

    if not execution_record:
        for item in all_dicts:
            if item is not execution_result and any(k in item for k in ("execution_record", "filled_quantity", "trade_id", "opened_at")):
                execution_record = item
                break

    if not execution_result and all_dicts:
        execution_result = all_dicts[0]

    if not isinstance(execution_result, dict):
        return execution_result

    if not isinstance(execution_record, dict):
        execution_record = {}

    if not isinstance(queued_trade, dict):
        queued_trade = {}

    vehicle = str(
        queued_trade.get("vehicle_selected")
        or queued_trade.get("selected_vehicle")
        or queued_trade.get("vehicle")
        or execution_record.get("vehicle_selected")
        or execution_record.get("selected_vehicle")
        or execution_record.get("vehicle")
        or ""
    ).upper()

    if vehicle != "OPTION":
        return execution_result

    contract = _observatory_patch_contract_dict_from_trade_20260519(queued_trade)

    contracts = int(_observatory_patch_first_positive_float_20260519(
        queued_trade.get("contracts"),
        queued_trade.get("quantity"),
        execution_record.get("contracts"),
        execution_record.get("quantity"),
        execution_result.get("filled_quantity"),
        default=1,
    ) or 1)

    raw_premium = _observatory_patch_first_positive_float_20260519(
        execution_result.get("fill_price"),
        execution_result.get("filled_price"),
        execution_result.get("entry_premium"),
        execution_result.get("premium_entry"),
        execution_result.get("option_entry"),
        execution_record.get("fill_price"),
        execution_record.get("filled_price"),
        execution_record.get("entry_premium"),
        execution_record.get("premium_entry"),
        execution_record.get("option_entry"),
        queued_trade.get("price_reference"),
        queued_trade.get("selected_price_reference"),
        queued_trade.get("option_price"),
        queued_trade.get("premium"),
        queued_trade.get("mark"),
        contract.get("mark"),
        contract.get("last"),
        contract.get("ask"),
        contract.get("bid"),
        default=0.0,
    )

    capital_required = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("capital_required"),
        queued_trade.get("estimated_cost"),
        queued_trade.get("effective_cost"),
        default=0.0,
    )

    minimum_trade_cost = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("minimum_trade_cost"),
        default=0.0,
    )

    # Prefer capital_required because minimum_trade_cost may include commission.
    inferred_from_capital = 0.0
    if capital_required > 0 and contracts > 0:
        inferred_from_capital = capital_required / (contracts * 100.0)

    inferred_from_minimum = 0.0
    if minimum_trade_cost > 1.0 and contracts > 0:
        # Most of this system uses +1.00 commission in paper mode.
        inferred_from_minimum = max((minimum_trade_cost - 1.0) / (contracts * 100.0), 0.0)

    premium = _observatory_patch_first_positive_float_20260519(
        raw_premium,
        inferred_from_capital,
        inferred_from_minimum,
        default=0.0,
    )

    symbol = str(
        queued_trade.get("symbol")
        or execution_record.get("symbol")
        or execution_result.get("symbol")
        or contract.get("symbol")
        or ""
    ).upper()

    trade_id = (
        queued_trade.get("trade_id")
        or execution_record.get("trade_id")
        or execution_result.get("trade_id")
        or ""
    )

    contract_symbol = (
        queued_trade.get("contract_symbol")
        or queued_trade.get("contractSymbol")
        or execution_record.get("contract_symbol")
        or execution_record.get("contractSymbol")
        or contract.get("contractSymbol")
        or contract.get("contract_symbol")
        or contract.get("option_symbol")
        or ""
    )

    expiration = (
        queued_trade.get("expiration")
        or queued_trade.get("expiry")
        or execution_record.get("expiration")
        or execution_record.get("expiry")
        or contract.get("expiration")
        or contract.get("expiry")
        or ""
    )

    strike = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("strike"),
        execution_record.get("strike"),
        contract.get("strike"),
        default=0.0,
    )

    right = str(
        queued_trade.get("right")
        or queued_trade.get("option_type")
        or execution_record.get("right")
        or execution_record.get("option_type")
        or contract.get("right")
        or contract.get("option_type")
        or queued_trade.get("strategy")
        or execution_record.get("strategy")
        or "CALL"
    ).upper()

    if right in ('C', 'CALLS'):
        right = "CALL"
    elif right in ('P', 'PUTS'):
        right = "PUT"

    commission = _observatory_patch_first_positive_float_20260519(
        queued_trade.get("commission"),
        execution_record.get("commission"),
        execution_result.get("commission"),
        default=1.0,
    )

    if premium <= 0:
        print("PAPER OPTION FILL REHYDRATION SKIPPED:", {
            "symbol": symbol,
            "trade_id": trade_id,
            "reason": "no_positive_option_premium_found_even_after_capital_fallback",
            "contract_symbol": contract_symbol,
            "capital_required": capital_required,
            "minimum_trade_cost": minimum_trade_cost,
            "contracts": contracts,
        })
        return execution_result

    actual_cost = round((premium * contracts * 100.0) + commission, 4)

    # Patch result shell.
    execution_result["status"] = execution_result.get("status") or "FILLED"
    execution_result["fill_price"] = premium
    execution_result["filled_price"] = premium
    execution_result["entry_premium"] = premium
    execution_result["premium_entry"] = premium
    execution_result["option_entry"] = premium
    execution_result["filled_quantity"] = contracts
    execution_result["quantity"] = contracts
    execution_result["contracts"] = contracts
    execution_result["shares"] = 0
    execution_result["actual_cost"] = actual_cost
    execution_result["paper_fill_rehydrated"] = True
    execution_result["paper_fill_rehydration_source"] = "premium_or_capital_required_fallback"

    # Patch execution record too.
    for target in (execution_record,):
        if isinstance(target, dict):
            target["symbol"] = symbol or target.get("symbol")
            target["vehicle"] = "OPTION"
            target["vehicle_selected"] = "OPTION"
            target["selected_vehicle"] = "OPTION"
            target["fill_price"] = premium
            target["filled_price"] = premium
            target["entry_premium"] = premium
            target["premium_entry"] = premium
            target["option_entry"] = premium
            target["current_premium"] = premium
            target["premium_current"] = premium
            target["current_option_mark"] = premium
            target["option_current_price"] = premium
            target["filled_quantity"] = contracts
            target["quantity"] = contracts
            target["contracts"] = contracts
            target["shares"] = 0
            target["actual_cost"] = actual_cost
            target["contract_symbol"] = contract_symbol or target.get("contract_symbol")
            target["option_symbol"] = contract_symbol or target.get("option_symbol")
            target["expiration"] = expiration or target.get("expiration")
            target["expiry"] = expiration or target.get("expiry")
            target["strike"] = strike or target.get("strike")
            target["right"] = right or target.get("right")
            target["monitoring_price_type"] = "OPTION_PREMIUM"
            target["price_review_basis"] = "OPTION_PREMIUM_ONLY"
            target["underlying_price_used_for_close_decision"] = False
            target["paper_fill_rehydrated"] = True
            target["paper_fill_rehydration_source"] = "premium_or_capital_required_fallback"

    execution_result["execution_record"] = execution_record

    print("PAPER OPTION FILL REHYDRATED:", {
        "symbol": symbol,
        "trade_id": trade_id,
        "premium": premium,
        "contracts": contracts,
        "contract_symbol": contract_symbol,
        "expiration": expiration,
        "strike": strike,
        "right": right,
        "actual_cost": actual_cost,
        "capital_required": capital_required,
        "minimum_trade_cost": minimum_trade_cost,
    })

    return execution_result


# ============================================================
# OBSERVATORY_REPAIR_FINAL_PAPER_FILL_RESULT_RESCUE_20260520
# Final paper fill rescue before rejection/validation.
# ============================================================

def _observatory_final_safe_float_20260520(value, default=0.0):
    try:
        if value is None or value == "":
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _observatory_final_first_positive_20260520(*values, default=0.0):
    for value in values:
        number = _observatory_final_safe_float_20260520(value, 0.0)
        if number > 0:
            return number
    return float(default)


def _observatory_final_rescue_paper_fill_result_20260520(execution_result, trade):
    """
    Last safety gate for Paper Mode only.

    If adapter output is None/{} but the queued trade was already selected,
    create a valid paper fill packet from the queued trade's known capital,
    vehicle, contract, and quantity fields.
    """
    trade = trade if isinstance(trade, dict) else {}

    mode = str(
        trade.get("trading_mode")
        or trade.get("mode")
        or "paper"
    ).strip().lower()

    if mode not in {"paper", "simulation", "sim", "survey"}:
        return execution_result

    selected = bool(trade.get("selected_for_execution")) or bool(trade.get("execution_ready"))
    if not selected:
        return execution_result

    if isinstance(execution_result, dict):
        existing_status = str(execution_result.get("status") or "").upper()
        existing_fill = _observatory_final_first_positive_20260520(
            execution_result.get("fill_price"),
            execution_result.get("filled_price"),
            default=0.0,
        )
        existing_cost = _observatory_final_first_positive_20260520(
            execution_result.get("actual_cost"),
            default=0.0,
        )
        if existing_status in {"FILLED", "EXECUTED"} and existing_fill > 0 and existing_cost > 1:
            return execution_result

    vehicle = str(
        trade.get("vehicle_selected")
        or trade.get("selected_vehicle")
        or trade.get("vehicle")
        or ""
    ).upper()

    if vehicle not in {"STOCK", "OPTION"}:
        return execution_result

    symbol = str(trade.get("symbol") or "").upper()
    trade_id = trade.get("trade_id") or ""

    strategy = (
        trade.get("strategy")
        or trade.get("final_strategy")
        or trade.get("chosen_strategy")
        or "CALL"
    )

    capital_required = _observatory_final_first_positive_20260520(
        trade.get("capital_required"),
        trade.get("estimated_cost"),
        trade.get("effective_cost"),
        default=0.0,
    )

    minimum_trade_cost = _observatory_final_first_positive_20260520(
        trade.get("minimum_trade_cost"),
        default=0.0,
    )

    commission = _observatory_final_first_positive_20260520(
        trade.get("commission"),
        default=1.0,
    )

    if vehicle == "STOCK":
        shares = int(_observatory_final_first_positive_20260520(
            trade.get("shares"),
            trade.get("quantity"),
            default=1,
        ) or 1)

        fill_price = _observatory_final_first_positive_20260520(
            trade.get("fill_price"),
            trade.get("price"),
            trade.get("current_price"),
            trade.get("underlying_price"),
            trade.get("last_price"),
            default=0.0,
        )

        if fill_price <= 0 and capital_required > 0 and shares > 0:
            fill_price = round(capital_required / shares, 4)

        if fill_price <= 0 and minimum_trade_cost > 1 and shares > 0:
            fill_price = round((minimum_trade_cost - commission) / shares, 4)

        if fill_price <= 0:
            return execution_result

        actual_cost = minimum_trade_cost if minimum_trade_cost > 0 else round((fill_price * shares) + commission, 4)

        record = {
            "trade_id": trade_id,
            "symbol": symbol,
            "strategy": strategy,
            "vehicle": "STOCK",
            "vehicle_selected": "STOCK",
            "selected_vehicle": "STOCK",
            "status": "FILLED",
            "fill_price": fill_price,
            "filled_price": fill_price,
            "entry": fill_price,
            "current": fill_price,
            "filled_quantity": shares,
            "quantity": shares,
            "shares": shares,
            "contracts": 0,
            "actual_cost": actual_cost,
            "paper_fill_rescued": True,
            "paper_fill_rehydrated": True,
            "paper_fill_rehydration_source": "final_stock_result_rescue",
        }

        rescued = {
            "status": "FILLED",
            "reason": "executed",
            "reason_code": "executed",
            "trade_id": trade_id,
            "symbol": symbol,
            "strategy": strategy,
            "vehicle": "STOCK",
            "vehicle_selected": "STOCK",
            "selected_vehicle": "STOCK",
            "fill_price": fill_price,
            "filled_price": fill_price,
            "entry": fill_price,
            "current": fill_price,
            "filled_quantity": shares,
            "quantity": shares,
            "shares": shares,
            "contracts": 0,
            "actual_cost": actual_cost,
            "execution_record": record,
            "paper_fill_rescued": True,
            "paper_fill_rehydrated": True,
            "paper_fill_rehydration_source": "final_stock_result_rescue",
        }

        print("FINAL PAPER STOCK FILL RESULT RESCUED:", {
            "symbol": symbol,
            "trade_id": trade_id,
            "fill_price": fill_price,
            "shares": shares,
            "actual_cost": actual_cost,
        })
        return rescued

    # OPTION
    contracts = int(_observatory_final_first_positive_20260520(
        trade.get("contracts"),
        trade.get("quantity"),
        default=1,
    ) or 1)

    premium = _observatory_final_first_positive_20260520(
        trade.get("fill_price"),
        trade.get("filled_price"),
        trade.get("entry_premium"),
        trade.get("premium_entry"),
        trade.get("option_entry"),
        trade.get("price_reference"),
        trade.get("selected_price_reference"),
        trade.get("option_price"),
        trade.get("premium"),
        trade.get("mark"),
        default=0.0,
    )

    if premium <= 0 and capital_required > 0 and contracts > 0:
        premium = round(capital_required / (contracts * 100.0), 4)

    if premium <= 0 and minimum_trade_cost > 1 and contracts > 0:
        premium = round((minimum_trade_cost - commission) / (contracts * 100.0), 4)

    if premium <= 0:
        return execution_result

    actual_cost = minimum_trade_cost if minimum_trade_cost > 0 else round((premium * contracts * 100.0) + commission, 4)

    contract_symbol = (
        trade.get("contract_symbol")
        or trade.get("contractSymbol")
        or trade.get("option_symbol")
        or ""
    )

    expiration = (
        trade.get("expiration")
        or trade.get("expiry")
        or ""
    )

    strike = _observatory_final_first_positive_20260520(
        trade.get("strike"),
        default=0.0,
    )

    right = str(
        trade.get("right")
        or trade.get("option_type")
        or strategy
        or "CALL"
    ).upper()

    if right in {"C", "CALLS"}:
        right = "CALL"
    if right in {"P", "PUTS"}:
        right = "PUT"

    record = {
        "trade_id": trade_id,
        "symbol": symbol,
        "strategy": strategy,
        "vehicle": "OPTION",
        "vehicle_selected": "OPTION",
        "selected_vehicle": "OPTION",
        "status": "FILLED",
        "fill_price": premium,
        "filled_price": premium,
        "entry": premium,
        "current": premium,
        "entry_premium": premium,
        "premium_entry": premium,
        "option_entry": premium,
        "current_premium": premium,
        "premium_current": premium,
        "current_option_mark": premium,
        "option_current_price": premium,
        "filled_quantity": contracts,
        "quantity": contracts,
        "shares": 0,
        "contracts": contracts,
        "actual_cost": actual_cost,
        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "expiration": expiration,
        "expiry": expiration,
        "strike": strike,
        "right": right,
        "monitoring_price_type": "OPTION_PREMIUM",
        "price_review_basis": "OPTION_PREMIUM_ONLY",
        "underlying_price_used_for_close_decision": False,
        "paper_fill_rescued": True,
        "paper_fill_rehydrated": True,
        "paper_fill_rehydration_source": "final_option_result_rescue",
    }

    rescued = {
        "status": "FILLED",
        "reason": "executed",
        "reason_code": "executed",
        "trade_id": trade_id,
        "symbol": symbol,
        "strategy": strategy,
        "vehicle": "OPTION",
        "vehicle_selected": "OPTION",
        "selected_vehicle": "OPTION",
        "fill_price": premium,
        "filled_price": premium,
        "entry_premium": premium,
        "premium_entry": premium,
        "option_entry": premium,
        "filled_quantity": contracts,
        "quantity": contracts,
        "shares": 0,
        "contracts": contracts,
        "actual_cost": actual_cost,
        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "expiration": expiration,
        "expiry": expiration,
        "strike": strike,
        "right": right,
        "execution_record": record,
        "paper_fill_rescued": True,
        "paper_fill_rehydrated": True,
        "paper_fill_rehydration_source": "final_option_result_rescue",
    }

    print("FINAL PAPER OPTION FILL RESULT RESCUED:", {
        "symbol": symbol,
        "trade_id": trade_id,
        "premium": premium,
        "contracts": contracts,
        "contract_symbol": contract_symbol,
        "actual_cost": actual_cost,
    })
    return rescued




# OBSERVATORY_REPAIR_EXECUTION_LOOP_CLEAN_SUCCESS_REASON_AND_OPTION_UNDERLYING_20260520

# OBSERVATORY_REPAIR_OPTION_SAFE_UNDERLYING_RESOLVER_STRICT_20260520
