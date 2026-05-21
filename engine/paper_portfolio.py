from __future__ import annotations

"""
Observatory Paper Portfolio Persistence Layer

Purpose:
    Store open and closed paper positions in a shape that downstream modules can
    trust.

Core rule:
    paper_portfolio.py is a persistence layer. It should not undo the decisions
    made by execution_loop.py, close_trade.py, position_monitor.py, or
    position_review.py.

Why this rewrite exists:
    The options lifecycle is now using premium math correctly, but persistence
    still has to protect against:
        - option stop/target aliases being dropped
        - option exit_premium being lost after close
        - closed option rows being reshaped as stock-like rows
        - performance flags being erased after close_trade.py stamps them
        - high-option-move audit fields disappearing
        - underlying price leaking back into current_price for option positions

Canonical OPTION rule:
    OPTION positions use option premium values for entry/current/exit math.

    target == take_profit == option_target == premium_target == target_premium == take_profit_premium

    stop == stop_loss == option_stop == premium_stop == stop_premium == stop_loss_premium

    OPTION positions:
        - contracts > 0
        - shares = 0
        - entry/current/exit price fields are option premium values
        - underlying_price is context only
        - monitoring_price_type = OPTION_PREMIUM
        - price_review_basis = OPTION_PREMIUM_ONLY
        - pnl_basis = option_premium_x_100

    STOCK positions:
        - shares > 0
        - contracts = 0
        - entry/current/exit price fields are underlying stock values
        - monitoring_price_type = UNDERLYING
        - price_review_basis = STOCK_PRICE
        - pnl_basis = stock_price_x_shares

Compatibility:
    - Keeps existing public API.
    - Still uses canonical_trade_state builders.
    - Adds post-builder hardening so persistence cannot erase option aliases.
"""

import json
import math
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.canonical_trade_state import (
    build_open_trade_state,
    build_closed_trade_state,
    build_trade_log_row,
    build_execution_audit_row,
)


OPEN_FILE = "data/open_positions.json"
POSITIONS_FILE = "data/positions.json"
LEGACY_USER_POSITIONS_FILE = "data/user_positions.json"
CLOSED_FILE = "data/closed_positions.json"
CANONICAL_LEDGER_FILE = "data/canonical_ledger.json"

OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

MIN_VALID_OPTION_PREMIUM = 0.01


# =============================================================================
# SAFE HELPERS
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


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
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
        if value is None or isinstance(value, bool):
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
        if value is None or isinstance(value, bool):
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


def _ensure_parent(path_str: str) -> None:
    Path(path_str).parent.mkdir(parents=True, exist_ok=True)


def _read_json(path_str: str, default: Any) -> Any:
    path = Path(path_str)
    if not path.exists():
        return deepcopy(default)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return deepcopy(default)


def _write_json(path_str: str, payload: Any) -> None:
    _ensure_parent(path_str)

    tmp_path = Path(path_str).with_suffix(Path(path_str).suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    tmp_path.replace(path_str)


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
# FILE LOADERS / WRITERS
# =============================================================================

def _load_open_positions() -> List[Dict[str, Any]]:
    rows = _read_json(OPEN_FILE, [])
    return rows if isinstance(rows, list) else []


def _load_closed_positions() -> List[Dict[str, Any]]:
    rows = _read_json(CLOSED_FILE, [])
    return rows if isinstance(rows, list) else []


def _load_canonical_ledger() -> List[Dict[str, Any]]:
    rows = _read_json(CANONICAL_LEDGER_FILE, [])
    return rows if isinstance(rows, list) else []


def _write_open_positions(rows: List[Dict[str, Any]]) -> None:
    _write_json(OPEN_FILE, rows)
    _write_json(POSITIONS_FILE, rows)
    _write_json(LEGACY_USER_POSITIONS_FILE, rows)


def _write_closed_positions(rows: List[Dict[str, Any]]) -> None:
    _write_json(CLOSED_FILE, rows)


# =============================================================================
# MODE HELPERS
# =============================================================================

def _best_mode(payload: Dict[str, Any], mode: str = "") -> str:
    payload = _safe_dict(payload)
    return _safe_str(
        mode
        or payload.get("trading_mode")
        or payload.get("execution_mode")
        or payload.get("mode"),
        "",
    )


def _best_mode_context(payload: Dict[str, Any], mode_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = _safe_dict(payload)
    merged: Dict[str, Any] = {}

    if isinstance(payload.get("mode_context"), dict):
        merged.update(payload.get("mode_context"))

    if isinstance(mode_context, dict):
        merged.update(mode_context)

    return merged


# =============================================================================
# VEHICLE / OPTION HELPERS
# =============================================================================

def _detect_vehicle(payload: Dict[str, Any]) -> str:
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
        [
            "contract_symbol",
            "option_symbol",
            "option_contract_symbol",
            "selected_contract_symbol",
            "contractSymbol",
            "occ_symbol",
        ],
        "",
    )

    right = _upper(
        _first_str(payload, ["right", "option_type", "call_put"], "")
        or _first_str(option, ["right", "option_type", "call_put"], "")
        or _first_str(contract, ["right", "option_type", "call_put"], ""),
        "",
    )

    contracts = _safe_int(payload.get("contracts", payload.get("contract_count", 0)), 0)
    shares = _safe_int(payload.get("shares", payload.get("quantity", payload.get("qty", 0))), 0)

    if option or contract or contract_symbol or right in {"CALL", "PUT", "C", "P"} or contracts > 0:
        if shares <= 0 or contracts > 0:
            return VEHICLE_OPTION

    return VEHICLE_STOCK


def _normalize_right(value: Any) -> str:
    right = _upper(value, "")

    if right in {"C", "CALLS"}:
        return "CALL"

    if right in {"P", "PUTS"}:
        return "PUT"

    return right


def _extract_contract_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = _safe_dict(payload)

    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))
    selected_contract = _safe_dict(payload.get("selected_contract"))
    best_option = _safe_dict(payload.get("best_option"))
    best_option_preview = _safe_dict(payload.get("best_option_preview"))

    merged: Dict[str, Any] = {}
    merged.update(best_option_preview)
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
                "contractSymbol",
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
        _first_str(payload, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
        or _first_str(merged, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
    )

    right = _normalize_right(
        _first_str(payload, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(merged, ["right", "option_type", "call_put", "contract_right"], "")
    )

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
            "current_premium",
            "premium_current",
            "mark",
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

    price_reference = _first_float(
        payload,
        [
            "selected_price_reference",
            "price_reference",
            "option_price_reference",
            "fill_price",
            "executed_price",
        ],
    )
    if price_reference is None:
        price_reference = _first_float(
            merged,
            [
                "selected_price_reference",
                "price_reference",
                "fill_price",
                "executed_price",
                "mark",
                "ask",
                "last",
            ],
        )

    return {
        "symbol": _norm_symbol(payload.get("symbol", merged.get("underlying_symbol", ""))),
        "contractSymbol": contract_symbol,
        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "expiry": expiry,
        "expiration": expiry,
        "expiration_date": expiry,
        "right": right,
        "option_type": right,
        "call_put": right,
        "strike": strike,
        "strike_price": strike,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "selected_price_reference": price_reference,
        "price_reference": price_reference if price_reference is not None else mark,
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
        "is_executable": _safe_bool(payload.get("is_executable", merged.get("is_executable")), True),
        "execution_reason": _safe_str(payload.get("execution_reason", merged.get("execution_reason")), "ok"),
        "contract_notes": _safe_list(payload.get("contract_notes", merged.get("contract_notes"))),
    }


def _first_valid_option_premium(payload: Dict[str, Any]) -> Optional[float]:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    candidates = [
        payload.get("entry_premium"),
        payload.get("premium_entry"),
        payload.get("option_entry"),
        payload.get("option_entry_price"),
        payload.get("entry_option_mark"),
        payload.get("contract_entry_price"),
        payload.get("fill_premium"),
        payload.get("average_premium"),
        payload.get("avg_premium"),
        payload.get("selected_price_reference"),
        payload.get("price_reference"),
        payload.get("fill_price"),
        payload.get("executed_price"),
        payload.get("entry"),
        payload.get("entry_price"),
        payload.get("current_premium"),
        payload.get("premium_current"),
        payload.get("current_option_mark"),
        payload.get("option_current_mark"),
        payload.get("option_current_price"),
        payload.get("current_option_price"),
        option.get("entry_premium"),
        option.get("premium_entry"),
        option.get("entry_price"),
        option.get("mark_at_entry"),
        option.get("fill_price"),
        option.get("executed_price"),
        option.get("selected_price_reference"),
        option.get("price_reference"),
        option.get("mark"),
        contract.get("entry_premium"),
        contract.get("premium_entry"),
        contract.get("entry_price"),
        contract.get("selected_price_reference"),
        contract.get("price_reference"),
        contract.get("mark"),
    ]

    for candidate in candidates:
        value = _safe_optional_float(candidate)
        if value is not None and value >= MIN_VALID_OPTION_PREMIUM:
            return round(value, 4)

    return None


def _first_valid_option_current(payload: Dict[str, Any]) -> Optional[float]:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    candidates = [
        payload.get("current_premium"),
        payload.get("premium_current"),
        payload.get("current_option_mark"),
        payload.get("option_current_mark"),
        payload.get("option_current_price"),
        payload.get("current_option_price"),
        payload.get("option_mark"),
        payload.get("mark"),
        option.get("current_premium"),
        option.get("premium_current"),
        option.get("current_option_mark"),
        option.get("option_current_mark"),
        option.get("mark"),
        option.get("last"),
        contract.get("current_premium"),
        contract.get("premium_current"),
        contract.get("current_option_mark"),
        contract.get("option_current_mark"),
        contract.get("mark"),
        contract.get("last"),
    ]

    for candidate in candidates:
        value = _safe_optional_float(candidate)
        if value is not None and value >= MIN_VALID_OPTION_PREMIUM:
            return round(value, 4)

    entry = _first_valid_option_premium(payload)
    if entry is not None and entry >= MIN_VALID_OPTION_PREMIUM:
        return round(entry, 4)

    return None


def _first_valid_option_exit(payload: Dict[str, Any]) -> Optional[float]:
    payload = _safe_dict(payload)
    option = _safe_dict(payload.get("option"))
    contract = _safe_dict(payload.get("contract"))

    candidates = [
        payload.get("exit_premium"),
        payload.get("premium_exit"),
        payload.get("option_exit"),
        payload.get("option_exit_price"),
        payload.get("exit_option_mark"),
        payload.get("close_option_mark"),
        payload.get("final_option_mark"),
        payload.get("exit_price"),
        payload.get("close_price"),
        payload.get("current_premium"),
        payload.get("premium_current"),
        payload.get("current_option_mark"),
        payload.get("option_current_mark"),
        payload.get("option_current_price"),
        payload.get("current_option_price"),
        option.get("exit_premium"),
        option.get("premium_exit"),
        option.get("option_exit"),
        option.get("exit_option_mark"),
        option.get("mark"),
        contract.get("exit_premium"),
        contract.get("premium_exit"),
        contract.get("option_exit"),
        contract.get("exit_option_mark"),
        contract.get("mark"),
    ]

    for candidate in candidates:
        value = _safe_optional_float(candidate)
        if value is not None and value >= MIN_VALID_OPTION_PREMIUM:
            return round(value, 4)

    return None


def _underlying_context(payload: Dict[str, Any]) -> float:
    payload = _safe_dict(payload)

    value = _first_float(
        payload,
        [
            "underlying_price",
            "current_underlying_price",
            "stock_price",
            "underlying_last",
            "underlying_mark",
            "spot_price",
            "last_underlying_price",
            "market_price",
        ],
    )

    return round(value, 4) if value is not None and value > 0 else 0.0


def _option_contracts(payload: Dict[str, Any]) -> int:
    payload = _safe_dict(payload)

    return max(
        1,
        _safe_int(
            payload.get(
                "contracts",
                payload.get("contract_count", payload.get("quantity", payload.get("qty", payload.get("size", 1)))),
            ),
            1,
        ),
    )


def _stock_shares(payload: Dict[str, Any]) -> int:
    payload = _safe_dict(payload)

    return max(
        1,
        _safe_int(payload.get("shares", payload.get("quantity", payload.get("qty", payload.get("size", 1)))), 1),
    )


def _first_stop_value(payload: Dict[str, Any]) -> Optional[float]:
    return _first_float(
        payload,
        [
            "stop",
            "stop_loss",
            "option_stop",
            "premium_stop",
            "stop_premium",
            "stop_loss_premium",
            "contract_stop",
        ],
    )


def _first_target_value(payload: Dict[str, Any]) -> Optional[float]:
    return _first_float(
        payload,
        [
            "target",
            "take_profit",
            "option_target",
            "premium_target",
            "target_premium",
            "take_profit_premium",
            "contract_target",
        ],
    )


def _stamp_option_stop_target_aliases(state: Dict[str, Any]) -> Dict[str, Any]:
    state = _safe_dict(state)

    stop = _first_stop_value(state)
    target = _first_target_value(state)
    entry_premium = _first_valid_option_premium(state)

    if stop is None or stop <= 0:
        if entry_premium is not None and entry_premium > 0:
            stop = round(max(0.01, entry_premium * 0.65), 4)
        else:
            stop = 0.0

    if target is None or target <= 0:
        if entry_premium is not None and entry_premium > 0:
            target = round(max(0.01, entry_premium * 1.60), 4)
        else:
            target = 0.0

    stop = round(float(stop), 4) if stop and stop > 0 else 0.0
    target = round(float(target), 4) if target and target > 0 else 0.0

    for key in [
        "stop",
        "stop_loss",
        "option_stop",
        "premium_stop",
        "stop_premium",
        "stop_loss_premium",
        "contract_stop",
    ]:
        state[key] = stop

    for key in [
        "target",
        "take_profit",
        "option_target",
        "premium_target",
        "target_premium",
        "take_profit_premium",
        "contract_target",
    ]:
        state[key] = target

    return state


def _stamp_option_premium_aliases(state: Dict[str, Any]) -> Dict[str, Any]:
    state = _safe_dict(state)

    entry_premium = _first_valid_option_premium(state)
    current_premium = _first_valid_option_current(state)

    if entry_premium is None:
        entry_premium = 0.0

    if current_premium is None:
        current_premium = entry_premium

    entry_premium = round(_safe_float(entry_premium, 0.0), 4)
    current_premium = round(_safe_float(current_premium, entry_premium), 4)

    for key in [
        "entry",
        "entry_price",
        "fill_price",
        "executed_price",
        "entry_premium",
        "premium_entry",
        "option_entry",
        "option_entry_price",
        "entry_option_mark",
        "contract_entry_price",
    ]:
        state[key] = entry_premium

    for key in [
        "current_price",
        "current_premium",
        "premium_current",
        "current_option_mark",
        "option_current_mark",
        "option_current_price",
        "current_option_price",
        "option_mark",
        "mark",
    ]:
        state[key] = current_premium

    return state


def _stamp_option_exit_aliases(state: Dict[str, Any]) -> Dict[str, Any]:
    state = _safe_dict(state)

    exit_premium = _first_valid_option_exit(state)

    if exit_premium is None:
        return state

    exit_premium = round(_safe_float(exit_premium, 0.0), 4)

    for key in [
        "exit_price",
        "close_price",
        "exit_premium",
        "premium_exit",
        "option_exit",
        "option_exit_price",
        "exit_option_mark",
        "close_option_mark",
        "final_option_mark",
        "current_price",
        "current",
        "current_premium",
        "premium_current",
        "current_option_mark",
        "option_current_mark",
        "option_current_price",
        "current_option_price",
        "option_mark",
        "mark",
    ]:
        state[key] = exit_premium

    return state


def _stamp_option_contract_aliases(state: Dict[str, Any]) -> Dict[str, Any]:
    state = _safe_dict(state)
    contract = _extract_contract_fields(state)

    contract_symbol = _safe_str(contract.get("contract_symbol") or contract.get("contractSymbol"), "")
    if contract_symbol:
        for key in ["contract_symbol", "option_symbol", "option_contract_symbol", "selected_contract_symbol", "contractSymbol"]:
            state[key] = contract_symbol
        contract["contractSymbol"] = contract_symbol
        contract["contract_symbol"] = contract_symbol
        contract["option_symbol"] = contract_symbol

    expiry = _safe_str(contract.get("expiry") or contract.get("expiration") or contract.get("expiration_date"), "")
    if expiry:
        for key in ["expiry", "expiration", "expiration_date", "contract_expiry"]:
            state[key] = expiry
        contract["expiry"] = expiry
        contract["expiration"] = expiry
        contract["expiration_date"] = expiry

    right = _normalize_right(contract.get("right") or state.get("right"))
    if right:
        for key in ["right", "option_type", "call_put", "contract_right"]:
            state[key] = right
        contract["right"] = right
        contract["option_type"] = right
        contract["call_put"] = right

    strike = _safe_optional_float(contract.get("strike"))
    if strike is not None:
        for key in ["strike", "strike_price", "contract_strike"]:
            state[key] = round(strike, 4)
        contract["strike"] = round(strike, 4)
        contract["strike_price"] = round(strike, 4)

    for key in [
        "bid",
        "ask",
        "last",
        "mark",
        "selected_price_reference",
        "price_reference",
        "volume",
        "open_interest",
        "implied_volatility",
        "spread",
        "spread_pct",
        "distance_pct",
        "contract_score",
        "trade_intent",
        "dte",
        "monitoring_mode",
        "is_executable",
        "execution_reason",
        "contract_notes",
    ]:
        if contract.get(key) not in (None, ""):
            state.setdefault(key, contract.get(key))

    state["option"] = contract
    state["contract"] = contract

    return state


def _preserve_performance_fields(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    target = _safe_dict(target)
    source = _safe_dict(source)

    keys = [
        "performance_classification",
        "performance_include",
        "include_in_performance",
        "counts_in_performance",
        "needs_review",
        "classification_reason",
        "review_classification",
        "high_option_move",
        "high_option_move_multiple",
        "high_option_move_note",
        "option_exit_validation_source",
    ]

    for key in keys:
        if source.get(key) not in (None, ""):
            target[key] = source.get(key)

    if "performance_include" in target:
        target["include_in_performance"] = target["performance_include"]
        target["counts_in_performance"] = target["performance_include"]

    return target


def _stamp_default_performance_fields(state: Dict[str, Any]) -> Dict[str, Any]:
    state = _safe_dict(state)

    close_reason = _safe_str(state.get("close_reason", state.get("reason", "")), "").lower()

    if "manual_option_premium_test" in close_reason or "manual_test" in close_reason or close_reason.endswith("_test"):
        state.setdefault("performance_classification", "MANUAL_TEST")
        state.setdefault("performance_include", False)
        state.setdefault("include_in_performance", False)
        state.setdefault("counts_in_performance", False)
        state.setdefault("needs_review", False)
        state.setdefault("classification_reason", "manual_or_test_reason")
        return state

    if "controlled_slot_release" in close_reason or "slot_release" in close_reason:
        state.setdefault("performance_classification", "CONTROLLED_RELEASE")
        state.setdefault("performance_include", False)
        state.setdefault("include_in_performance", False)
        state.setdefault("counts_in_performance", False)
        state.setdefault("needs_review", False)
        state.setdefault("classification_reason", "controlled_release_reason")
        return state

    if _safe_bool(state.get("option_underlying_leak_blocked"), False):
        state.setdefault("performance_classification", "QUARANTINED_BAD_CLOSE")
        state.setdefault("performance_include", False)
        state.setdefault("include_in_performance", False)
        state.setdefault("counts_in_performance", False)
        state.setdefault("needs_review", False)
        state.setdefault("classification_reason", "underlying_leak_blocked")
        return state

    state.setdefault("performance_classification", "REAL_TRADE")
    state.setdefault("performance_include", True)
    state.setdefault("include_in_performance", True)
    state.setdefault("counts_in_performance", True)
    state.setdefault("needs_review", False)
    state.setdefault("classification_reason", "persisted_valid_close")

    return state


# =============================================================================
# OPEN / CLOSED HARDENERS
# =============================================================================

def _harden_option_open_state(state: Dict[str, Any]) -> Dict[str, Any]:
    state = deepcopy(_safe_dict(state))

    state["vehicle"] = VEHICLE_OPTION
    state["vehicle_selected"] = VEHICLE_OPTION
    state["selected_vehicle"] = VEHICLE_OPTION
    state["asset_type"] = VEHICLE_OPTION
    state["instrument_type"] = VEHICLE_OPTION

    contracts = _option_contracts(state)
    state["contracts"] = contracts
    state["contract_count"] = contracts
    state["quantity"] = contracts
    state["qty"] = contracts
    state["size"] = contracts
    state["shares"] = 0

    state = _stamp_option_contract_aliases(state)
    state = _stamp_option_premium_aliases(state)
    state = _stamp_option_stop_target_aliases(state)

    underlying = _underlying_context(state)
    if underlying > 0:
        state["underlying_price"] = underlying
        state["current_underlying_price"] = underlying
        state["stock_price"] = underlying

    entry_premium = _safe_float(state.get("entry_premium"), 0.0)
    current_premium = _safe_float(state.get("current_premium"), entry_premium)
    contracts = _option_contracts(state)

    state["capital_required"] = round(
        _safe_float(state.get("capital_required"), entry_premium * OPTION_CONTRACT_MULTIPLIER * contracts),
        4,
    )
    if state["capital_required"] <= 0 and entry_premium > 0:
        state["capital_required"] = round(entry_premium * OPTION_CONTRACT_MULTIPLIER * contracts, 4)

    commission = _safe_float(state.get("commission"), 0.0)
    state["commission"] = round(commission, 4)

    state["actual_cost"] = round(
        _safe_float(state.get("actual_cost"), state["capital_required"]),
        4,
    )
    if state["actual_cost"] <= 0:
        state["actual_cost"] = state["capital_required"]

    state["minimum_trade_cost"] = round(
        _safe_float(state.get("minimum_trade_cost"), state["actual_cost"] + commission),
        4,
    )
    if state["minimum_trade_cost"] <= 0:
        state["minimum_trade_cost"] = round(state["actual_cost"] + commission, 4)

    state["effective_cost"] = round(
        _safe_float(state.get("effective_cost"), state["minimum_trade_cost"]),
        4,
    )
    if state["effective_cost"] <= 0:
        state["effective_cost"] = state["minimum_trade_cost"]

    state["cost_basis"] = round(entry_premium * OPTION_CONTRACT_MULTIPLIER * contracts, 4)
    state["market_value"] = round(current_premium * OPTION_CONTRACT_MULTIPLIER * contracts, 4)

    state["monitoring_price_type"] = "OPTION_PREMIUM"
    state["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    state["pnl_basis"] = "option_premium_x_100"
    state["underlying_price_used_for_close_decision"] = False
    state["underlying_price_used_for_pnl"] = False
    state["execution_position_shape"] = "OPTION_PREMIUM_POSITION"
    state["option_underlying_leak_blocked"] = bool(state.get("option_underlying_leak_blocked", False))

    state["status"] = "OPEN"
    state["position_status"] = "OPEN"
    state["lifecycle_state"] = _safe_str(state.get("lifecycle_state"), "ENTERED")
    state["lifecycle_stage"] = _safe_str(state.get("lifecycle_stage"), "ENTERED")

    state["persistence_hardened_by"] = "engine.paper_portfolio"
    state["option_aliases_preserved"] = True
    state["option_alias_audit"] = {
        "entry_premium": state.get("entry_premium"),
        "current_premium": state.get("current_premium"),
        "stop": state.get("stop"),
        "stop_loss": state.get("stop_loss"),
        "option_stop": state.get("option_stop"),
        "premium_stop": state.get("premium_stop"),
        "stop_premium": state.get("stop_premium"),
        "stop_loss_premium": state.get("stop_loss_premium"),
        "target": state.get("target"),
        "take_profit": state.get("take_profit"),
        "option_target": state.get("option_target"),
        "premium_target": state.get("premium_target"),
        "target_premium": state.get("target_premium"),
        "take_profit_premium": state.get("take_profit_premium"),
    }

    return state


def _harden_stock_open_state(state: Dict[str, Any]) -> Dict[str, Any]:
    state = deepcopy(_safe_dict(state))

    state["vehicle"] = VEHICLE_STOCK
    state["vehicle_selected"] = VEHICLE_STOCK
    state["selected_vehicle"] = VEHICLE_STOCK
    state["asset_type"] = VEHICLE_STOCK
    state["instrument_type"] = VEHICLE_STOCK

    shares = _stock_shares(state)
    state["shares"] = shares
    state["quantity"] = shares
    state["qty"] = shares
    state["size"] = shares
    state["contracts"] = 0
    state["contract_count"] = 0

    entry = _first_float(state, ["entry", "entry_price", "fill_price", "executed_price", "price", "stock_price"])
    if entry is None:
        entry = 0.0
    entry = round(entry, 4)

    current = _first_float(state, ["current_price", "market_price", "stock_price", "underlying_price", "current_underlying_price"])
    if current is None or current <= 0:
        current = entry
    current = round(current, 4)

    state["entry"] = entry
    state["entry_price"] = entry
    state["fill_price"] = entry
    state["executed_price"] = entry
    state["current_price"] = current
    state["underlying_price"] = current
    state["current_underlying_price"] = current
    state["stock_price"] = current

    for key in [
        "entry_premium",
        "premium_entry",
        "option_entry",
        "option_entry_price",
        "current_premium",
        "premium_current",
        "current_option_mark",
        "option_current_mark",
        "option_current_price",
        "current_option_price",
        "exit_premium",
        "premium_exit",
        "option_exit",
        "option_exit_price",
    ]:
        state[key] = None

    stop = _first_float(state, ["stop", "stop_loss", "stock_stop"])
    target = _first_float(state, ["target", "take_profit", "stock_target"])

    if stop is None or stop <= 0:
        stop = round(entry * 0.97, 4) if entry > 0 else 0.0
    if target is None or target <= 0:
        target = round(entry * 1.10, 4) if entry > 0 else 0.0

    state["stop"] = round(stop, 4) if stop > 0 else 0.0
    state["stop_loss"] = state["stop"]
    state["stock_stop"] = state["stop"]

    state["target"] = round(target, 4) if target > 0 else 0.0
    state["take_profit"] = state["target"]
    state["stock_target"] = state["target"]

    state["capital_required"] = round(_safe_float(state.get("capital_required"), entry * shares), 4)
    if state["capital_required"] <= 0 and entry > 0:
        state["capital_required"] = round(entry * shares, 4)

    commission = _safe_float(state.get("commission"), 0.0)
    state["commission"] = round(commission, 4)

    state["actual_cost"] = round(_safe_float(state.get("actual_cost"), state["capital_required"]), 4)
    state["minimum_trade_cost"] = round(_safe_float(state.get("minimum_trade_cost"), state["actual_cost"] + commission), 4)
    state["effective_cost"] = round(_safe_float(state.get("effective_cost"), state["minimum_trade_cost"]), 4)

    state["cost_basis"] = round(entry * shares, 4)
    state["market_value"] = round(current * shares, 4)

    state["monitoring_price_type"] = "UNDERLYING"
    state["price_review_basis"] = "STOCK_PRICE"
    state["pnl_basis"] = "stock_price_x_shares"
    state["underlying_price_used_for_close_decision"] = True
    state["underlying_price_used_for_pnl"] = True
    state["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

    state["status"] = "OPEN"
    state["position_status"] = "OPEN"
    state["lifecycle_state"] = _safe_str(state.get("lifecycle_state"), "ENTERED")
    state["lifecycle_stage"] = _safe_str(state.get("lifecycle_stage"), "ENTERED")

    state["persistence_hardened_by"] = "engine.paper_portfolio"

    return state


def _harden_open_state(state: Dict[str, Any]) -> Dict[str, Any]:
    state = deepcopy(_safe_dict(state))
    vehicle = _detect_vehicle(state)

    if vehicle == VEHICLE_OPTION:
        return _harden_option_open_state(state)

    if vehicle == VEHICLE_RESEARCH_ONLY:
        state["vehicle"] = VEHICLE_RESEARCH_ONLY
        state["vehicle_selected"] = VEHICLE_RESEARCH_ONLY
        state["selected_vehicle"] = VEHICLE_RESEARCH_ONLY
        state["monitoring_price_type"] = "RESEARCH_ONLY"
        state["price_review_basis"] = "NO_POSITION"
        state["execution_position_shape"] = "RESEARCH_ONLY_NO_POSITION"
        state["status"] = "RESEARCH_ONLY"
        state["position_status"] = "RESEARCH_ONLY"
        state["persistence_hardened_by"] = "engine.paper_portfolio"
        return state

    return _harden_stock_open_state(state)


def _harden_option_closed_state(state: Dict[str, Any], original: Dict[str, Any]) -> Dict[str, Any]:
    state = deepcopy(_safe_dict(state))
    original = deepcopy(_safe_dict(original))

    state = _preserve_performance_fields(state, original)

    state["vehicle"] = VEHICLE_OPTION
    state["vehicle_selected"] = VEHICLE_OPTION
    state["selected_vehicle"] = VEHICLE_OPTION
    state["asset_type"] = VEHICLE_OPTION
    state["instrument_type"] = VEHICLE_OPTION

    contracts = _option_contracts(state)
    state["contracts"] = contracts
    state["contract_count"] = contracts
    state["quantity"] = contracts
    state["qty"] = contracts
    state["size"] = contracts
    state["shares"] = 0

    state = _stamp_option_contract_aliases(state)
    state = _stamp_option_premium_aliases(state)
    state = _stamp_option_exit_aliases(state)
    state = _stamp_option_stop_target_aliases(state)

    entry_premium = _safe_float(state.get("entry_premium"), 0.0)
    exit_premium = _safe_float(state.get("exit_premium", state.get("exit_price", 0.0)), 0.0)

    if exit_premium > 0:
        for key in [
            "exit_price",
            "close_price",
            "exit_premium",
            "premium_exit",
            "option_exit",
            "option_exit_price",
            "exit_option_mark",
            "close_option_mark",
            "final_option_mark",
            "current_price",
            "current",
            "current_premium",
            "premium_current",
            "current_option_mark",
            "option_current_mark",
            "option_current_price",
            "current_option_price",
            "option_mark",
            "mark",
        ]:
            state[key] = round(exit_premium, 4)

    underlying = _underlying_context(state)
    if underlying > 0:
        state["underlying_price"] = underlying
        state["current_underlying_price"] = underlying
        state["stock_price"] = underlying

    if entry_premium > 0 and exit_premium > 0:
        pnl = round((exit_premium - entry_premium) * OPTION_CONTRACT_MULTIPLIER * contracts, 2)
        if state.get("pnl") in (None, ""):
            state["pnl"] = pnl
        if state.get("realized_pnl") in (None, ""):
            state["realized_pnl"] = state.get("pnl", pnl)

        state["pnl_pct"] = round(((exit_premium - entry_premium) / entry_premium) * 100.0, 4)

    state["unrealized_pnl"] = 0.0
    state["cost_basis"] = round(entry_premium * OPTION_CONTRACT_MULTIPLIER * contracts, 4) if entry_premium > 0 else 0.0
    state["market_value"] = 0.0

    state["status"] = "CLOSED"
    state["position_status"] = "CLOSED"
    state["execution_status"] = "CLOSED"
    state["lifecycle_state"] = "CLOSED"
    state["lifecycle_stage"] = "CLOSED"

    state["monitoring_price_type"] = "OPTION_PREMIUM"
    state["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    state["pnl_basis"] = _safe_str(state.get("pnl_basis"), "option_premium_x_100")
    state["underlying_price_used_for_close_decision"] = False
    state["underlying_price_used_for_pnl"] = False
    state["execution_position_shape"] = "OPTION_PREMIUM_POSITION"
    state["option_underlying_leak_blocked"] = bool(state.get("option_underlying_leak_blocked", False))

    state = _stamp_default_performance_fields(state)
    state = _preserve_performance_fields(state, original)

    state["persistence_hardened_by"] = "engine.paper_portfolio"
    state["closed_persistence_hardened"] = True
    state["option_aliases_preserved"] = True
    state["closed_option_alias_audit"] = {
        "entry_premium": state.get("entry_premium"),
        "exit_premium": state.get("exit_premium"),
        "current_premium": state.get("current_premium"),
        "exit_price": state.get("exit_price"),
        "close_price": state.get("close_price"),
        "pnl": state.get("pnl"),
        "realized_pnl": state.get("realized_pnl"),
        "pnl_basis": state.get("pnl_basis"),
        "performance_classification": state.get("performance_classification"),
        "performance_include": state.get("performance_include"),
        "needs_review": state.get("needs_review"),
        "classification_reason": state.get("classification_reason"),
    }

    return state


def _harden_stock_closed_state(state: Dict[str, Any], original: Dict[str, Any]) -> Dict[str, Any]:
    state = deepcopy(_safe_dict(state))
    original = deepcopy(_safe_dict(original))

    state = _preserve_performance_fields(state, original)
    state = _harden_stock_open_state(state)

    exit_price = _first_float(state, ["exit_price", "close_price", "current_price", "underlying_price"])
    if exit_price is None:
        exit_price = 0.0

    if exit_price > 0:
        state["exit_price"] = round(exit_price, 4)
        state["close_price"] = round(exit_price, 4)
        state["current_price"] = round(exit_price, 4)
        state["underlying_price"] = round(exit_price, 4)
        state["current_underlying_price"] = round(exit_price, 4)

    state["status"] = "CLOSED"
    state["position_status"] = "CLOSED"
    state["execution_status"] = "CLOSED"
    state["lifecycle_state"] = "CLOSED"
    state["lifecycle_stage"] = "CLOSED"

    state["monitoring_price_type"] = "UNDERLYING"
    state["price_review_basis"] = "STOCK_PRICE"
    state["pnl_basis"] = _safe_str(state.get("pnl_basis"), "stock_price_x_shares")
    state["underlying_price_used_for_close_decision"] = True
    state["underlying_price_used_for_pnl"] = True
    state["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

    state = _stamp_default_performance_fields(state)
    state = _preserve_performance_fields(state, original)

    state["persistence_hardened_by"] = "engine.paper_portfolio"
    state["closed_persistence_hardened"] = True

    return state


def _harden_closed_state(state: Dict[str, Any], original: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    state = deepcopy(_safe_dict(state))
    original = deepcopy(_safe_dict(original or state))
    vehicle = _detect_vehicle(state)

    if vehicle == VEHICLE_OPTION:
        return _harden_option_closed_state(state, original)

    if vehicle == VEHICLE_STOCK:
        return _harden_stock_closed_state(state, original)

    state["status"] = "CLOSED"
    state["position_status"] = "CLOSED"
    state["execution_status"] = "CLOSED"
    state["lifecycle_state"] = "CLOSED"
    state["lifecycle_stage"] = "CLOSED"
    state["persistence_hardened_by"] = "engine.paper_portfolio"
    state["closed_persistence_hardened"] = True
    state = _stamp_default_performance_fields(state)
    state = _preserve_performance_fields(state, original)
    return state


# =============================================================================
# LEDGER HELPERS
# =============================================================================

def _append_ledger_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    ledger = _load_canonical_ledger()

    event = {
        "timestamp": _now_iso(),
        "event_type": _safe_str(event_type, "UNKNOWN").upper(),
        "symbol": _norm_symbol(payload.get("symbol")),
        "trade_id": _safe_str(payload.get("trade_id"), ""),
        "payload": deepcopy(_safe_dict(payload)),
    }

    ledger.append(event)
    _write_json(CANONICAL_LEDGER_FILE, ledger)
    return event


def _append_trade_log_event(event_type: str, trade_state: Dict[str, Any]) -> None:
    try:
        payload = build_trade_log_row(trade_state, event=event_type)
    except Exception:
        payload = deepcopy(_safe_dict(trade_state))
        payload["event"] = event_type

    _append_ledger_event(event_type, payload)


def _append_audit_event(
    event_type: str,
    trade_state: Dict[str, Any],
    note: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        payload = build_execution_audit_row(
            trade_state,
            event_type=event_type,
            note=note,
            extra=extra or {},
        )
    except Exception:
        payload = deepcopy(_safe_dict(trade_state))
        payload["event_type"] = event_type
        payload["note"] = note
        payload["extra"] = extra or {}

    _append_ledger_event(event_type, payload)


# =============================================================================
# POSITION FINDERS
# =============================================================================

def _find_open_index(
    open_positions: List[Dict[str, Any]],
    *,
    symbol: str,
    trade_id: str = "",
    opened_at: str = "",
) -> int:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    opened_at = _safe_str(opened_at, "")

    for idx, pos in enumerate(open_positions):
        pos = _safe_dict(pos)
        pos_symbol = _norm_symbol(pos.get("symbol"))
        pos_trade_id = _safe_str(pos.get("trade_id"), "")
        pos_opened_at = _safe_str(pos.get("opened_at"), "")

        if trade_id and pos_trade_id == trade_id:
            return idx

        if symbol and opened_at and pos_symbol == symbol and pos_opened_at == opened_at:
            return idx

        if symbol and not trade_id and not opened_at and pos_symbol == symbol:
            return idx

    return -1


def _find_closed_index(closed_positions: List[Dict[str, Any]], trade_id: str = "") -> int:
    trade_id = _safe_str(trade_id, "")
    if not trade_id:
        return -1

    for idx, row in enumerate(closed_positions):
        if _safe_str(_safe_dict(row).get("trade_id"), "") == trade_id:
            return idx

    return -1


# =============================================================================
# CANONICAL NORMALIZERS
# =============================================================================

def _normalize_open_trade(
    source_trade: Dict[str, Any],
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_trade = deepcopy(_safe_dict(source_trade))
    lifecycle = deepcopy(_safe_dict(lifecycle))
    execution_result = deepcopy(_safe_dict(execution_result))

    merged_pre_builder = deepcopy(source_trade)

    if lifecycle:
        for key, value in lifecycle.items():
            if key not in merged_pre_builder or merged_pre_builder.get(key) in (None, ""):
                merged_pre_builder[key] = value

    resolved_mode = _best_mode(merged_pre_builder, mode=mode)
    resolved_mode_context = _best_mode_context(merged_pre_builder, mode_context=mode_context)

    state = build_open_trade_state(
        merged_pre_builder,
        lifecycle=lifecycle,
        execution_result=execution_result,
        mode=resolved_mode,
        mode_context=resolved_mode_context,
    )

    state = deepcopy(_safe_dict(state))

    for key, value in merged_pre_builder.items():
        if key not in state or state.get(key) in (None, ""):
            state[key] = deepcopy(value)

    state["status"] = "OPEN"
    state["position_status"] = "OPEN"
    state["timestamp"] = _safe_str(state.get("timestamp"), _now_iso())
    state["opened_at"] = _safe_str(state.get("opened_at"), state["timestamp"])
    state["closed_at"] = ""
    state["exit_price"] = 0.0
    state["close_reason"] = ""
    state["exit_explanation"] = _safe_dict(state.get("exit_explanation"))

    state = _harden_open_state(state)

    state["timestamp"] = _safe_str(state.get("timestamp"), _now_iso())
    state["opened_at"] = _safe_str(state.get("opened_at"), state["timestamp"])
    state["closed_at"] = ""
    state["exit_price"] = 0.0
    state["close_reason"] = ""
    state["exit_explanation"] = _safe_dict(state.get("exit_explanation"))

    return state


def _normalize_closed_trade(
    position: Dict[str, Any],
    *,
    exit_price: Optional[float] = None,
    close_reason: str = "",
    closed_at: str = "",
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    position = deepcopy(_safe_dict(position))

    resolved_exit_price = float(exit_price if exit_price is not None else position.get("exit_price", 0.0) or 0.0)
    resolved_close_reason = _safe_str(close_reason or position.get("close_reason") or position.get("reason"), "manual")
    resolved_closed_at = _safe_str(closed_at or position.get("closed_at"), _now_iso())
    resolved_pnl = float(pnl if pnl is not None else position.get("pnl", 0.0) or 0.0)
    resolved_exit_explanation = _safe_dict(exit_explanation or position.get("exit_explanation"))
    resolved_capital_release = _safe_dict(capital_release or position.get("capital_release"))

    original = deepcopy(position)

    normalized = build_closed_trade_state(
        position,
        exit_price=resolved_exit_price,
        close_reason=resolved_close_reason,
        closed_at=resolved_closed_at,
        pnl=resolved_pnl,
        exit_explanation=resolved_exit_explanation,
        capital_release=resolved_capital_release,
    )

    normalized = deepcopy(_safe_dict(normalized))

    for key, value in position.items():
        if key not in normalized or normalized.get(key) in (None, ""):
            normalized[key] = deepcopy(value)

    normalized["status"] = "CLOSED"
    normalized["position_status"] = "CLOSED"
    normalized["execution_status"] = "CLOSED"
    normalized["lifecycle_state"] = "CLOSED"
    normalized["lifecycle_stage"] = "CLOSED"
    normalized["closed_at"] = resolved_closed_at
    normalized["exit_time"] = resolved_closed_at
    normalized["exit_price"] = resolved_exit_price
    normalized["close_price"] = resolved_exit_price
    normalized["close_reason"] = resolved_close_reason
    normalized["reason"] = resolved_close_reason
    normalized["pnl"] = resolved_pnl
    normalized["realized_pnl"] = resolved_pnl
    normalized["unrealized_pnl"] = 0.0
    normalized["exit_explanation"] = resolved_exit_explanation
    normalized["capital_release"] = resolved_capital_release

    normalized = _preserve_performance_fields(normalized, original)
    normalized = _harden_closed_state(normalized, original=original)

    normalized["status"] = "CLOSED"
    normalized["position_status"] = "CLOSED"
    normalized["execution_status"] = "CLOSED"
    normalized["lifecycle_state"] = "CLOSED"
    normalized["lifecycle_stage"] = "CLOSED"
    normalized["closed_at"] = resolved_closed_at
    normalized["exit_time"] = resolved_closed_at
    normalized["close_reason"] = resolved_close_reason
    normalized["reason"] = resolved_close_reason
    normalized["pnl"] = resolved_pnl
    normalized["realized_pnl"] = resolved_pnl
    normalized["unrealized_pnl"] = 0.0
    normalized["exit_explanation"] = resolved_exit_explanation
    normalized["capital_release"] = resolved_capital_release

    normalized = _preserve_performance_fields(normalized, original)
    normalized = _stamp_default_performance_fields(normalized)

    return normalized


# =============================================================================
# PUBLIC API
# =============================================================================

def clear_open_positions() -> None:
    _write_open_positions([])
    _append_ledger_event(
        "OPEN_CLEAR",
        {"symbol": "", "trade_id": "", "note": "All open positions cleared."},
    )


def open_count() -> int:
    return len(_load_open_positions())


def show_positions() -> List[Dict[str, Any]]:
    return _load_open_positions()


def get_open_positions() -> List[Dict[str, Any]]:
    """
    Compatibility alias.

    Several notebook tests and engine modules expect get_open_positions().
    The canonical storage function is show_positions(), but this keeps older
    callers working without changing their imports.
    """
    return _load_open_positions()


def show_closed_positions() -> List[Dict[str, Any]]:
    return _load_closed_positions()


def get_closed_positions() -> List[Dict[str, Any]]:
    """
    Compatibility alias for closed-position readers.
    """
    return _load_closed_positions()


def get_position(symbol: str, trade_id: str = "") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")

    for pos in _load_open_positions():
        pos = _safe_dict(pos)

        if trade_id and _safe_str(pos.get("trade_id"), "") == trade_id:
            return pos

        if symbol and _norm_symbol(pos.get("symbol")) == symbol:
            return pos

    return None


def add_position(
    trade: Dict[str, Any],
    allow_replace: bool = False,
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    normalized = _normalize_open_trade(
        trade,
        lifecycle=lifecycle,
        execution_result=execution_result,
        mode=mode,
        mode_context=mode_context,
    )

    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=normalized.get("symbol", ""),
        trade_id=normalized.get("trade_id", ""),
        opened_at=normalized.get("opened_at", ""),
    )

    if idx >= 0:
        if not allow_replace:
            raise ValueError(
                f"Open position already exists for {normalized.get('symbol')} ({normalized.get('trade_id')})."
            )

        prior = _safe_dict(open_positions[idx])
        merged = dict(prior)
        merged.update(normalized)

        normalized = _normalize_open_trade(
            merged,
            lifecycle=lifecycle,
            execution_result=execution_result,
            mode=mode,
            mode_context=mode_context,
        )

        open_positions[idx] = normalized
        event_type = "POSITION_REPLACED_ON_ADD"

    else:
        open_positions.append(normalized)
        event_type = "POSITION_OPENED"

    _write_open_positions(open_positions)

    _append_trade_log_event(event_type, normalized)
    _append_audit_event(
        event_type,
        normalized,
        note="Open position stored with persistence hardening.",
        extra={
            "vehicle": normalized.get("vehicle"),
            "execution_position_shape": normalized.get("execution_position_shape"),
            "option_aliases_preserved": normalized.get("option_aliases_preserved", False),
            "option_alias_audit": normalized.get("option_alias_audit", {}),
        },
    )

    return normalized


def replace_position(
    symbol: str,
    updated_position: Dict[str, Any],
    *,
    lifecycle: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    mode: str = "",
    mode_context: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    updated_position = deepcopy(_safe_dict(updated_position))

    open_positions = _load_open_positions()

    idx = _find_open_index(
        open_positions,
        symbol=symbol or _norm_symbol(updated_position.get("symbol")),
        trade_id=_safe_str(updated_position.get("trade_id"), ""),
        opened_at=_safe_str(updated_position.get("opened_at"), ""),
    )

    if idx < 0:
        return None

    prior = _safe_dict(open_positions[idx])
    merged = dict(prior)
    merged.update(updated_position)

    normalized = _normalize_open_trade(
        merged,
        lifecycle=lifecycle,
        execution_result=execution_result,
        mode=mode,
        mode_context=mode_context,
    )
    normalized["symbol"] = _norm_symbol(normalized.get("symbol", symbol))
    normalized["status"] = "OPEN"
    normalized["position_status"] = "OPEN"

    open_positions[idx] = normalized
    _write_open_positions(open_positions)

    _append_trade_log_event("POSITION_UPDATED", normalized)
    _append_audit_event(
        "POSITION_UPDATED",
        normalized,
        note="Open position updated with persistence hardening.",
        extra={
            "vehicle": normalized.get("vehicle"),
            "execution_position_shape": normalized.get("execution_position_shape"),
            "option_aliases_preserved": normalized.get("option_aliases_preserved", False),
            "option_alias_audit": normalized.get("option_alias_audit", {}),
        },
    )

    return normalized


def remove_position(symbol: str, trade_id: str = "", reason: str = "removed") -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")

    open_positions = _load_open_positions()

    idx = _find_open_index(open_positions, symbol=symbol, trade_id=trade_id)
    if idx < 0:
        return None

    removed = _safe_dict(open_positions.pop(idx))
    _write_open_positions(open_positions)

    payload = dict(removed)
    payload["remove_reason"] = _safe_str(reason, "removed")

    _append_trade_log_event("POSITION_REMOVED", payload)
    _append_audit_event("POSITION_REMOVED", payload, note=payload["remove_reason"])

    return removed


def archive_closed_position(
    position: Dict[str, Any],
    *,
    exit_price: Optional[float] = None,
    close_reason: str = "",
    closed_at: str = "",
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    closed_positions = _load_closed_positions()

    normalized = _normalize_closed_trade(
        position,
        exit_price=exit_price,
        close_reason=close_reason,
        closed_at=closed_at,
        pnl=pnl,
        exit_explanation=exit_explanation,
        capital_release=capital_release,
    )

    existing_idx = _find_closed_index(
        closed_positions,
        trade_id=_safe_str(normalized.get("trade_id"), ""),
    )

    if existing_idx >= 0:
        prior = _safe_dict(closed_positions[existing_idx])
        merged = dict(prior)
        merged.update(normalized)

        normalized = _normalize_closed_trade(
            merged,
            exit_price=exit_price,
            close_reason=close_reason,
            closed_at=closed_at,
            pnl=pnl,
            exit_explanation=exit_explanation,
            capital_release=capital_release,
        )

        closed_positions[existing_idx] = normalized
        event_type = "POSITION_CLOSED_UPDATED"

    else:
        closed_positions.append(normalized)
        event_type = "POSITION_CLOSED"

    _write_closed_positions(closed_positions)

    _append_trade_log_event(event_type, normalized)
    _append_audit_event(
        event_type,
        normalized,
        note=normalized.get("close_reason", "closed"),
        extra={
            "vehicle": normalized.get("vehicle"),
            "execution_position_shape": normalized.get("execution_position_shape"),
            "price_review_basis": normalized.get("price_review_basis"),
            "pnl_basis": normalized.get("pnl_basis"),
            "performance_classification": normalized.get("performance_classification"),
            "performance_include": normalized.get("performance_include"),
            "needs_review": normalized.get("needs_review"),
            "closed_persistence_hardened": normalized.get("closed_persistence_hardened", False),
            "closed_option_alias_audit": normalized.get("closed_option_alias_audit", {}),
        },
    )

    return normalized


def close_position(
    symbol: str,
    *,
    trade_id: str = "",
    exit_price: Optional[float] = None,
    close_reason: str = "manual",
    closed_at: str = "",
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")

    open_positions = _load_open_positions()

    idx = _find_open_index(open_positions, symbol=symbol, trade_id=trade_id)
    if idx < 0:
        return None

    open_trade = _safe_dict(open_positions.pop(idx))
    _write_open_positions(open_positions)

    closed = archive_closed_position(
        open_trade,
        exit_price=exit_price,
        close_reason=close_reason,
        closed_at=closed_at,
        pnl=pnl,
        exit_explanation=exit_explanation,
        capital_release=capital_release,
    )

    return closed


def print_positions() -> None:
    positions = _load_open_positions()

    print("OPEN POSITIONS:")

    if not positions:
        print("No open positions.")
        return

    for pos in positions:
        pos = _safe_dict(pos)
        vehicle = _detect_vehicle(pos)

        if vehicle == VEHICLE_OPTION:
            print(
                pos.get("symbol"),
                pos.get("strategy"),
                pos.get("fused_score", pos.get("score")),
                "| vehicle:",
                pos.get("vehicle_selected"),
                "| entry:",
                pos.get("entry_premium", pos.get("entry")),
                "| current:",
                pos.get("current_premium", pos.get("current_price")),
                "| stop:",
                pos.get("stop"),
                "| target:",
                pos.get("target"),
                "| take_profit:",
                pos.get("take_profit"),
                "| target_premium:",
                pos.get("target_premium"),
                "| take_profit_premium:",
                pos.get("take_profit_premium"),
                "| contract:",
                pos.get("contract_symbol", pos.get("option_symbol")),
                "| trade_id:",
                pos.get("trade_id"),
                "| opened_at:",
                pos.get("opened_at"),
            )
        else:
            print(
                pos.get("symbol"),
                pos.get("strategy"),
                pos.get("fused_score", pos.get("score")),
                "| vehicle:",
                pos.get("vehicle_selected"),
                "| entry:",
                pos.get("entry", pos.get("price")),
                "| current:",
                pos.get("current_price"),
                "| stop:",
                pos.get("stop"),
                "| target:",
                pos.get("target"),
                "| trade_id:",
                pos.get("trade_id"),
                "| opened_at:",
                pos.get("opened_at"),
            )


def print_closed_positions() -> None:
    positions = _load_closed_positions()

    print("CLOSED POSITIONS:")

    if not positions:
        print("No closed positions.")
        return

    for pos in positions:
        pos = _safe_dict(pos)
        vehicle = _detect_vehicle(pos)

        if vehicle == VEHICLE_OPTION:
            print(
                pos.get("symbol"),
                pos.get("strategy"),
                "| vehicle:",
                pos.get("vehicle_selected"),
                "| pnl:",
                pos.get("pnl"),
                "| entry_premium:",
                pos.get("entry_premium"),
                "| exit_premium:",
                pos.get("exit_premium", pos.get("exit_price")),
                "| pnl_basis:",
                pos.get("pnl_basis"),
                "| perf:",
                pos.get("performance_classification"),
                "| include:",
                pos.get("performance_include"),
                "| contract:",
                pos.get("contract_symbol", pos.get("option_symbol")),
                "| trade_id:",
                pos.get("trade_id"),
                "| closed_at:",
                pos.get("closed_at"),
                "| reason:",
                pos.get("close_reason"),
            )
        else:
            print(
                pos.get("symbol"),
                pos.get("strategy"),
                "| vehicle:",
                pos.get("vehicle_selected"),
                "| pnl:",
                pos.get("pnl"),
                "| exit_price:",
                pos.get("exit_price"),
                "| pnl_basis:",
                pos.get("pnl_basis"),
                "| perf:",
                pos.get("performance_classification"),
                "| include:",
                pos.get("performance_include"),
                "| trade_id:",
                pos.get("trade_id"),
                "| closed_at:",
                pos.get("closed_at"),
                "| reason:",
                pos.get("close_reason"),
            )


__all__ = [
    "OPEN_FILE",
    "POSITIONS_FILE",
    "LEGACY_USER_POSITIONS_FILE",
    "CLOSED_FILE",
    "CANONICAL_LEDGER_FILE",
    "clear_open_positions",
    "open_count",
    "show_positions",
    "get_open_positions",
    "show_closed_positions",
    "get_closed_positions",
    "get_position",
    "add_position",
    "replace_position",
    "remove_position",
    "archive_closed_position",
    "close_position",
    "print_positions",
    "print_closed_positions",
]

# ==============================================================================
# OBSERVATORY_ENTRY_POSITION_STORE_WIRE_001_20260521
# ==============================================================================
# Compatibility-preserving entry-side active-book sync.
#
# Why this exists:
# - Older Observatory code may write open positions to only one active book.
# - The canonical active books must stay aligned:
#   data/open_positions.json
#   data/positions.json
#   data/user_positions.json
#
# This wrapper does not change old function signatures. It lets the existing
# function run first, then asks position_store to normalize/sync active books.
# ==============================================================================

try:
    from functools import wraps as _observatory_entry_wraps_20260521
    from engine.position_store import (
        sync_active_books as _observatory_sync_active_books_20260521,
        health_report as _observatory_position_store_health_20260521,
    )

    def _observatory_entry_sync_after_call_20260521(func_name, func):
        @_observatory_entry_wraps_20260521(func)
        def _wrapped(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                sync_result = _observatory_sync_active_books_20260521()
                if isinstance(result, dict):
                    result.setdefault("position_store_entry_sync", sync_result)
            except Exception as sync_error:
                if isinstance(result, dict):
                    result.setdefault("position_store_entry_sync_error", str(sync_error))
                else:
                    print(f"[POSITION_STORE_ENTRY_SYNC_WARNING] {func_name}: {sync_error}")
            return result

        _wrapped._observatory_entry_position_store_wrapped_20260521 = True
        return _wrapped

    def _observatory_wrap_entry_function_20260521(name):
        obj = globals().get(name)
        if not callable(obj):
            return False
        if getattr(obj, "_observatory_entry_position_store_wrapped_20260521", False):
            return True
        globals()[name] = _observatory_entry_sync_after_call_20260521(name, obj)
        return True

    _OBSERVATORY_ENTRY_FUNCTION_NAMES_20260521 = [
        # common open/add entry names
        "add_position",
        "add_open_position",
        "open_position",
        "record_open_position",
        "create_position",
        "create_open_position",
        "enter_position",
        "enter_trade",
        "add_trade",

        # paper portfolio / execution helper names that may open positions
        "execute_paper_trade",
        "paper_execute_trade",
        "record_paper_fill",
        "record_fill",
        "save_position",
        "save_open_position",
        "save_positions",
        "save_open_positions",

        # private/internal save helpers seen in older versions
        "_save_open_positions",
        "_save_positions",
        "_write_open_positions",
        "_write_positions",
    ]

    _OBSERVATORY_ENTRY_WRAPPED_20260521 = [
        name for name in _OBSERVATORY_ENTRY_FUNCTION_NAMES_20260521
        if _observatory_wrap_entry_function_20260521(name)
    ]

except Exception as _observatory_entry_wire_error_20260521:
    print(f"[POSITION_STORE_ENTRY_WIRE_WARNING] paper_portfolio.py: {_observatory_entry_wire_error_20260521}")
