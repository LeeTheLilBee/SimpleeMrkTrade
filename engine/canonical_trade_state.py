from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional


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
        return float(value)
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
        return float(value)
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


def _first_nonempty(*values: Any, default: str = "") -> str:
    for value in values:
        text = _safe_str(value, "")
        if text:
            return text
    return default


def _first_list(*values: Any) -> List[Any]:
    for value in values:
        if isinstance(value, list) and value:
            return list(value)
    return []


def _first_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def _first_positive_float(*values: Any, default: float = 0.0) -> float:
    for value in values:
        num = _safe_float(value, 0.0)
        if num > 0:
            return num
    return float(default)


def _first_float_from_payload(payload: Dict[str, Any], keys: List[str]) -> Optional[float]:
    payload = _safe_dict(payload)
    for key in keys:
        value = _safe_optional_float(payload.get(key))
        if value is not None:
            return value
    return None


def _derive_trade_id(symbol: str, strategy: str, opened_at: str) -> str:
    stamp = _safe_str(opened_at, _now_iso()).replace(":", "").replace("-", "").replace(".", "")
    return f"{symbol}-{strategy}-{stamp}"


# =============================================================================
# Vehicle / direction helpers
# =============================================================================

def _vehicle(value: Any) -> str:
    raw = _safe_str(value, "").upper()

    if raw in {"OPTION", "OPTIONS", "OPT"}:
        return VEHICLE_OPTION

    if raw in {"STOCK", "EQUITY", "SHARE", "SHARES"}:
        return VEHICLE_STOCK

    if raw in {"RESEARCH_ONLY", "RESEARCH"}:
        return VEHICLE_RESEARCH_ONLY

    return VEHICLE_RESEARCH_ONLY


def _detect_vehicle(merged: Dict[str, Any], source_trade: Dict[str, Any]) -> str:
    raw = (
        merged.get("vehicle_selected")
        or merged.get("selected_vehicle")
        or merged.get("vehicle")
        or merged.get("asset_type")
        or merged.get("instrument_type")
        or source_trade.get("vehicle_selected")
        or source_trade.get("vehicle")
    )

    vehicle = _vehicle(raw)
    if vehicle != VEHICLE_RESEARCH_ONLY:
        return vehicle

    option_obj = _first_dict(
        merged.get("option"),
        merged.get("contract"),
        source_trade.get("option"),
        source_trade.get("contract"),
    )

    contract_symbol = _first_nonempty(
        merged.get("contract_symbol"),
        merged.get("option_symbol"),
        merged.get("option_contract_symbol"),
        option_obj.get("contractSymbol"),
        option_obj.get("contract_symbol"),
        option_obj.get("option_symbol"),
        "",
    )

    contracts = _safe_int(
        merged.get("contracts", merged.get("contract_count", source_trade.get("contracts", 0))),
        0,
    )

    if contract_symbol or option_obj or contracts > 0:
        return VEHICLE_OPTION

    shares = _safe_int(merged.get("shares", source_trade.get("shares", 0)), 0)
    price = _safe_float(merged.get("price", source_trade.get("price", 0.0)), 0.0)

    if shares > 0 or price > 0:
        return VEHICLE_STOCK

    return VEHICLE_RESEARCH_ONLY


def _direction(strategy: str) -> str:
    text = _safe_str(strategy, "CALL").upper()
    if "PUT" in text or "SHORT" in text:
        return "SHORT"
    return "LONG"


# =============================================================================
# Price / contract helpers
# =============================================================================

def _capital_buffer_after(capital_available: float, capital_required: float) -> float:
    return round(_safe_float(capital_available, 0.0) - _safe_float(capital_required, 0.0), 4)


def _merge_option_payload(merged: Dict[str, Any], source_trade: Dict[str, Any]) -> Dict[str, Any]:
    option_obj = _safe_dict(source_trade.get("option"))
    contract_obj = _safe_dict(source_trade.get("contract"))
    merged_option = _safe_dict(merged.get("option"))
    merged_contract = _safe_dict(merged.get("contract"))

    out: Dict[str, Any] = {}
    out.update(contract_obj)
    out.update(option_obj)
    out.update(merged_contract)
    out.update(merged_option)

    contract_symbol = _first_nonempty(
        merged.get("contract_symbol"),
        merged.get("option_symbol"),
        merged.get("option_contract_symbol"),
        merged.get("selected_contract_symbol"),
        source_trade.get("contract_symbol"),
        source_trade.get("option_symbol"),
        out.get("contractSymbol"),
        out.get("contract_symbol"),
        out.get("option_symbol"),
        out.get("selected_contract_symbol"),
        "",
    )

    expiry = _first_nonempty(
        merged.get("expiry"),
        merged.get("expiration"),
        merged.get("expiration_date"),
        source_trade.get("expiry"),
        source_trade.get("expiration"),
        out.get("expiry"),
        out.get("expiration"),
        out.get("expiration_date"),
        "",
    )

    right = _safe_str(
        merged.get("right")
        or merged.get("option_type")
        or merged.get("call_put")
        or source_trade.get("right")
        or out.get("right")
        or out.get("option_type")
        or "",
        "",
    ).upper()

    if right == "C":
        right = "CALL"
    elif right == "P":
        right = "PUT"

    strike = _first_positive_float(
        merged.get("strike"),
        merged.get("strike_price"),
        source_trade.get("strike"),
        out.get("strike"),
        out.get("strike_price"),
        default=0.0,
    )

    bid = _first_positive_float(
        merged.get("bid"),
        merged.get("option_bid"),
        source_trade.get("bid"),
        out.get("bid"),
        default=0.0,
    )

    ask = _first_positive_float(
        merged.get("ask"),
        merged.get("option_ask"),
        source_trade.get("ask"),
        out.get("ask"),
        default=0.0,
    )

    last = _first_positive_float(
        merged.get("last"),
        merged.get("option_last"),
        source_trade.get("last"),
        out.get("last"),
        out.get("last_price"),
        default=0.0,
    )

    mark = _first_positive_float(
        merged.get("current_option_mark"),
        merged.get("option_current_mark"),
        merged.get("option_mark"),
        merged.get("mark"),
        merged.get("current_premium"),
        merged.get("premium_current"),
        source_trade.get("current_option_mark"),
        source_trade.get("option_mark"),
        out.get("current_option_mark"),
        out.get("option_current_mark"),
        out.get("current_mark"),
        out.get("mark"),
        out.get("mid"),
        out.get("selected_price_reference"),
        out.get("price_reference"),
        last,
        default=0.0,
    )

    price_reference = _first_positive_float(
        merged.get("selected_price_reference"),
        merged.get("price_reference"),
        source_trade.get("selected_price_reference"),
        source_trade.get("price_reference"),
        out.get("selected_price_reference"),
        out.get("price_reference"),
        mark,
        last,
        ask,
        default=0.0,
    )

    out["contractSymbol"] = contract_symbol
    out["contract_symbol"] = contract_symbol
    out["option_symbol"] = contract_symbol
    out["expiration"] = expiry
    out["expiry"] = expiry
    out["right"] = right
    out["strike"] = strike
    out["bid"] = bid
    out["ask"] = ask
    out["last"] = last
    out["mark"] = mark
    out["price_reference"] = price_reference
    out["selected_price_reference"] = price_reference
    out["volume"] = _safe_int(merged.get("volume", out.get("volume", 0)), 0)
    out["open_interest"] = _safe_int(
        merged.get("open_interest", out.get("open_interest", out.get("oi", 0))),
        0,
    )
    out["dte"] = _safe_int(merged.get("dte", out.get("dte", out.get("daysToExpiration", 0))), 0)
    out["contract_score"] = _safe_float(
        merged.get("contract_score", merged.get("option_contract_score", out.get("contract_score", 0.0))),
        0.0,
    )
    out["monitoring_mode"] = "OPTION_PREMIUM"

    return out


def _option_price_from_obj(option_obj: Dict[str, Any], fallback: float = 0.0) -> float:
    option_obj = _safe_dict(option_obj)
    return round(
        _first_positive_float(
            option_obj.get("current_option_mark"),
            option_obj.get("option_current_mark"),
            option_obj.get("current_premium"),
            option_obj.get("mark"),
            option_obj.get("price_reference"),
            option_obj.get("selected_price_reference"),
            option_obj.get("last"),
            option_obj.get("ask"),
            fallback,
            default=0.0,
        ),
        4,
    )


def _underlying_price(merged: Dict[str, Any], source_trade: Dict[str, Any]) -> float:
    return round(
        _first_positive_float(
            merged.get("underlying_price"),
            merged.get("current_underlying_price"),
            merged.get("stock_price"),
            merged.get("underlying_last"),
            merged.get("underlying_mark"),
            merged.get("spot_price"),
            source_trade.get("underlying_price"),
            source_trade.get("stock_price"),
            source_trade.get("price"),
            merged.get("price"),
            default=0.0,
        ),
        4,
    )


def _option_entry_premium(
    merged: Dict[str, Any],
    source_trade: Dict[str, Any],
    execution_result: Dict[str, Any],
    execution_record: Dict[str, Any],
    option_obj: Dict[str, Any],
) -> float:
    return round(
        _first_positive_float(
            execution_result.get("fill_price"),
            execution_result.get("executed_price"),
            execution_result.get("average_fill_price"),
            execution_result.get("avg_fill_price"),
            execution_record.get("fill_price"),
            execution_record.get("filled_price"),
            merged.get("entry_premium"),
            merged.get("premium_entry"),
            merged.get("option_entry"),
            merged.get("option_entry_price"),
            merged.get("entry_option_mark"),
            merged.get("contract_entry_price"),
            merged.get("fill_premium"),
            merged.get("average_premium"),
            merged.get("avg_premium"),
            merged.get("debit"),
            merged.get("price_paid"),
            merged.get("fill_price"),
            merged.get("executed_price"),
            merged.get("entry"),
            merged.get("entry_price"),
            merged.get("requested_price"),
            source_trade.get("entry_premium"),
            source_trade.get("premium_entry"),
            source_trade.get("option_entry"),
            source_trade.get("fill_price"),
            option_obj.get("entry_premium"),
            option_obj.get("premium_entry"),
            option_obj.get("entry_price"),
            option_obj.get("mark_at_entry"),
            option_obj.get("selected_price_reference"),
            option_obj.get("price_reference"),
            option_obj.get("mark"),
            option_obj.get("ask"),
            option_obj.get("last"),
            default=0.0,
        ),
        4,
    )


def _option_current_premium(
    merged: Dict[str, Any],
    source_trade: Dict[str, Any],
    option_obj: Dict[str, Any],
    entry: float,
) -> float:
    return round(
        _first_positive_float(
            merged.get("current_premium"),
            merged.get("premium_current"),
            merged.get("current_option_mark"),
            merged.get("option_current_mark"),
            merged.get("option_current_price"),
            merged.get("current_option_price"),
            merged.get("option_mark"),
            merged.get("mark"),
            source_trade.get("current_premium"),
            source_trade.get("current_option_mark"),
            source_trade.get("option_current_price"),
            option_obj.get("current_premium"),
            option_obj.get("current_option_mark"),
            option_obj.get("option_current_mark"),
            option_obj.get("current_mark"),
            option_obj.get("mark"),
            option_obj.get("selected_price_reference"),
            option_obj.get("price_reference"),
            option_obj.get("last"),
            entry,
            default=entry,
        ),
        4,
    )


def _stock_entry_price(
    merged: Dict[str, Any],
    source_trade: Dict[str, Any],
    execution_result: Dict[str, Any],
    execution_record: Dict[str, Any],
    underlying_price: float,
) -> float:
    return round(
        _first_positive_float(
            execution_result.get("fill_price"),
            execution_result.get("executed_price"),
            execution_result.get("average_fill_price"),
            execution_result.get("avg_fill_price"),
            execution_record.get("fill_price"),
            execution_record.get("filled_price"),
            merged.get("entry"),
            merged.get("entry_price"),
            merged.get("requested_price"),
            merged.get("price"),
            source_trade.get("entry"),
            source_trade.get("price"),
            underlying_price,
            default=0.0,
        ),
        4,
    )


def _stock_current_price(merged: Dict[str, Any], source_trade: Dict[str, Any], entry: float, underlying_price: float) -> float:
    return round(
        _first_positive_float(
            merged.get("current_price"),
            merged.get("current_underlying_price"),
            merged.get("underlying_price"),
            merged.get("stock_price"),
            source_trade.get("current_price"),
            source_trade.get("underlying_price"),
            underlying_price,
            entry,
            default=entry,
        ),
        4,
    )


# =============================================================================
# Stop / target / PnL
# =============================================================================

def _default_stock_stop(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0
    if direction == "SHORT":
        return round(entry * (1.0 + DEFAULT_STOCK_STOP_LOSS_PCT), 4)
    return round(entry * (1.0 - DEFAULT_STOCK_STOP_LOSS_PCT), 4)


def _default_stock_target(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0
    if direction == "SHORT":
        return round(entry * (1.0 - DEFAULT_STOCK_TARGET_GAIN_PCT), 4)
    return round(entry * (1.0 + DEFAULT_STOCK_TARGET_GAIN_PCT), 4)


def _default_option_stop(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0

    if direction == "SHORT":
        return round(entry * (1.0 + DEFAULT_OPTION_STOP_LOSS_PCT), 4)

    return round(entry * (1.0 - DEFAULT_OPTION_STOP_LOSS_PCT), 4)


def _default_option_target(entry: float, direction: str) -> float:
    if entry <= 0:
        return 0.0

    if direction == "SHORT":
        return round(entry * (1.0 - DEFAULT_OPTION_TARGET_GAIN_PCT), 4)

    return round(entry * (1.0 + DEFAULT_OPTION_TARGET_GAIN_PCT), 4)


def _option_stop(merged: Dict[str, Any], entry: float, direction: str) -> float:
    default = _default_option_stop(entry, direction)
    return round(
        _first_positive_float(
            merged.get("option_stop"),
            merged.get("premium_stop"),
            merged.get("stop_premium"),
            merged.get("contract_stop"),
            merged.get("stop_loss_premium"),
            merged.get("stop"),
            merged.get("stop_loss"),
            default,
            default=default,
        ),
        4,
    )


def _option_target(merged: Dict[str, Any], entry: float, direction: str) -> float:
    default = _default_option_target(entry, direction)
    return round(
        _first_positive_float(
            merged.get("option_target"),
            merged.get("premium_target"),
            merged.get("target_premium"),
            merged.get("contract_target"),
            merged.get("take_profit_premium"),
            merged.get("target"),
            merged.get("take_profit"),
            default,
            default=default,
        ),
        4,
    )


def _stock_stop(merged: Dict[str, Any], entry: float, direction: str) -> float:
    default = _default_stock_stop(entry, direction)
    return round(
        _first_positive_float(
            merged.get("stock_stop"),
            merged.get("stop"),
            merged.get("stop_loss"),
            default,
            default=default,
        ),
        4,
    )


def _stock_target(merged: Dict[str, Any], entry: float, direction: str) -> float:
    default = _default_stock_target(entry, direction)
    return round(
        _first_positive_float(
            merged.get("stock_target"),
            merged.get("target"),
            merged.get("take_profit"),
            default,
            default=default,
        ),
        4,
    )


def _calc_unrealized_pnl(
    *,
    vehicle_selected: str,
    strategy: str,
    entry: float,
    current_price: float,
    shares: int,
    contracts: int,
) -> float:
    direction = _direction(strategy)

    if entry <= 0 or current_price <= 0:
        return 0.0

    if vehicle_selected == VEHICLE_OPTION:
        delta = current_price - entry
        return round(delta * max(1, contracts) * OPTION_CONTRACT_MULTIPLIER, 4)

    if vehicle_selected == VEHICLE_STOCK:
        delta = (entry - current_price) if direction == "SHORT" else (current_price - entry)
        return round(delta * max(1, shares), 4)

    return 0.0


def _calc_unrealized_pnl_pct(entry: float, current_price: float, vehicle_selected: str, strategy: str) -> float:
    if entry <= 0 or current_price <= 0:
        return 0.0

    if vehicle_selected == VEHICLE_OPTION:
        return round(((current_price - entry) / entry) * 100.0, 4)

    direction = _direction(strategy)

    if direction == "SHORT":
        return round(((entry - current_price) / entry) * 100.0, 4)

    return round(((current_price - entry) / entry) * 100.0, 4)


# =============================================================================
# Public builders
# =============================================================================

def build_open_trade_state(
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
    execution_record = _safe_dict(execution_result.get("execution_record"))
    mode_context = deepcopy(_safe_dict(mode_context))

    merged: Dict[str, Any] = {}
    merged.update(source_trade)
    merged.update(lifecycle)

    symbol = _norm_symbol(
        merged.get("symbol")
        or execution_record.get("symbol")
        or source_trade.get("symbol")
    )

    strategy = _safe_str(
        merged.get("strategy")
        or execution_record.get("strategy")
        or source_trade.get("strategy"),
        "CALL",
    ).upper()

    direction = _direction(strategy)
    vehicle_selected = _detect_vehicle(merged, source_trade)

    option_obj = _merge_option_payload(merged, source_trade)

    opened_at = _first_nonempty(
        merged.get("opened_at"),
        execution_record.get("opened_at"),
        merged.get("timestamp"),
        source_trade.get("timestamp"),
        _now_iso(),
    )

    timestamp = _first_nonempty(
        merged.get("timestamp"),
        source_trade.get("timestamp"),
        opened_at,
    )

    trade_id = _first_nonempty(
        merged.get("trade_id"),
        execution_record.get("trade_id"),
        source_trade.get("trade_id"),
        default=_derive_trade_id(symbol, strategy, opened_at),
    )

    underlying = _underlying_price(merged, source_trade)

    if vehicle_selected == VEHICLE_OPTION:
        entry = _option_entry_premium(
            merged=merged,
            source_trade=source_trade,
            execution_result=execution_result,
            execution_record=execution_record,
            option_obj=option_obj,
        )

        current_price = _option_current_premium(
            merged=merged,
            source_trade=source_trade,
            option_obj=option_obj,
            entry=entry,
        )

        requested_price = round(
            _first_positive_float(
                execution_record.get("requested_price"),
                merged.get("requested_price"),
                merged.get("selected_price_reference"),
                merged.get("price_reference"),
                option_obj.get("selected_price_reference"),
                option_obj.get("price_reference"),
                entry,
                default=entry,
            ),
            4,
        )

        fill_price = round(
            _first_positive_float(
                execution_result.get("fill_price"),
                execution_result.get("executed_price"),
                execution_record.get("fill_price"),
                execution_record.get("filled_price"),
                entry,
                default=entry,
            ),
            4,
        )

        contracts = max(
            1,
            _safe_int(
                execution_record.get(
                    "contracts",
                    merged.get("contracts", merged.get("contract_count", merged.get("quantity", merged.get("qty", 1)))),
                ),
                1,
            ),
        )
        shares = 0
        size = contracts

        stop = _option_stop(merged, entry, direction)
        target = _option_target(merged, entry, direction)

        monitoring_price_type = "OPTION_PREMIUM"
        price_review_basis = "OPTION_PREMIUM_ONLY"
        underlying_price_used_for_close_decision = False
        pnl_basis = "option_premium_x_100"
        execution_position_shape = _safe_str(
            merged.get("execution_position_shape"),
            "OPTION_PREMIUM_POSITION",
        )

    elif vehicle_selected == VEHICLE_STOCK:
        entry = _stock_entry_price(
            merged=merged,
            source_trade=source_trade,
            execution_result=execution_result,
            execution_record=execution_record,
            underlying_price=underlying,
        )

        current_price = _stock_current_price(merged, source_trade, entry, underlying)

        requested_price = round(
            _first_positive_float(
                execution_record.get("requested_price"),
                merged.get("requested_price"),
                merged.get("price"),
                entry,
                default=entry,
            ),
            4,
        )

        fill_price = round(
            _first_positive_float(
                execution_result.get("fill_price"),
                execution_result.get("executed_price"),
                execution_record.get("fill_price"),
                execution_record.get("filled_price"),
                entry,
                default=entry,
            ),
            4,
        )

        shares = max(
            1,
            _safe_int(
                execution_record.get("shares", merged.get("shares", merged.get("quantity", merged.get("qty", merged.get("size", 1))))),
                1,
            ),
        )
        contracts = 0
        size = shares

        stop = _stock_stop(merged, entry, direction)
        target = _stock_target(merged, entry, direction)

        monitoring_price_type = "UNDERLYING"
        price_review_basis = "STOCK_PRICE"
        underlying_price_used_for_close_decision = True
        pnl_basis = "stock_price_x_shares"
        execution_position_shape = _safe_str(
            merged.get("execution_position_shape"),
            "STOCK_UNDERLYING_POSITION",
        )

    else:
        entry = 0.0
        current_price = 0.0
        requested_price = 0.0
        fill_price = 0.0
        shares = 0
        contracts = 0
        size = 0
        stop = 0.0
        target = 0.0
        monitoring_price_type = "RESEARCH_ONLY"
        price_review_basis = "NO_POSITION"
        underlying_price_used_for_close_decision = False
        pnl_basis = "research_only"
        execution_position_shape = _safe_str(
            merged.get("execution_position_shape"),
            "RESEARCH_ONLY_NO_POSITION",
        )

    capital_required = round(
        _first_positive_float(
            merged.get("capital_required"),
            merged.get("actual_cost"),
            merged.get("effective_cost"),
            merged.get("minimum_trade_cost"),
            execution_result.get("actual_cost"),
            entry * contracts * OPTION_CONTRACT_MULTIPLIER if vehicle_selected == VEHICLE_OPTION else entry * shares,
            default=0.0,
        ),
        4,
    )

    minimum_trade_cost = round(
        _first_positive_float(
            merged.get("minimum_trade_cost"),
            merged.get("effective_cost"),
            capital_required,
            default=capital_required,
        ),
        4,
    )

    capital_available = round(
        _first_positive_float(
            merged.get("capital_available"),
            source_trade.get("capital_available"),
            0.0,
            default=0.0,
        ),
        4,
    )

    commission = round(
        _safe_float(
            execution_result.get("commission", execution_record.get("commission", merged.get("commission", 0.0))),
            0.0,
        ),
        4,
    )

    unrealized_pnl = _calc_unrealized_pnl(
        vehicle_selected=vehicle_selected,
        strategy=strategy,
        entry=entry,
        current_price=current_price,
        shares=shares,
        contracts=contracts,
    )

    unrealized_pnl_pct = _calc_unrealized_pnl_pct(
        entry=entry,
        current_price=current_price,
        vehicle_selected=vehicle_selected,
        strategy=strategy,
    )

    v2 = _first_dict(merged.get("v2"), source_trade.get("v2"))
    v2_payload = _first_dict(merged.get("v2_payload"), source_trade.get("v2_payload"), v2)

    contract_symbol = _first_nonempty(
        merged.get("contract_symbol"),
        merged.get("option_symbol"),
        option_obj.get("contract_symbol"),
        option_obj.get("contractSymbol"),
        "",
    )

    expiry = _first_nonempty(
        merged.get("expiry"),
        merged.get("expiration"),
        option_obj.get("expiry"),
        option_obj.get("expiration"),
        "",
    )

    right = _first_nonempty(
        merged.get("right"),
        option_obj.get("right"),
        strategy,
    ).upper()

    strike = round(
        _first_positive_float(
            merged.get("strike"),
            merged.get("strike_price"),
            option_obj.get("strike"),
            default=0.0,
        ),
        4,
    )

    state = {
        "trade_id": trade_id,
        "symbol": symbol,
        "company_name": _first_nonempty(
            merged.get("company_name"),
            merged.get("company"),
            source_trade.get("company_name"),
            symbol,
        ),
        "sector": _first_nonempty(
            merged.get("sector"),
            source_trade.get("sector"),
            "UNKNOWN",
        ),

        "status": "OPEN",
        "position_status": "OPEN",
        "timestamp": timestamp,
        "opened_at": opened_at,
        "closed_at": "",
        "execution_status": _safe_str(
            execution_result.get("status", execution_record.get("status", "FILLED")),
            "FILLED",
        ).upper(),

        "strategy": strategy,
        "direction": direction,
        "side": strategy,

        "vehicle_selected": vehicle_selected,
        "selected_vehicle": vehicle_selected,
        "vehicle": vehicle_selected,
        "asset_type": vehicle_selected,
        "instrument_type": vehicle_selected,

        "shares": shares,
        "contracts": contracts,
        "contract_count": contracts,
        "quantity": contracts if vehicle_selected == VEHICLE_OPTION else shares,
        "qty": contracts if vehicle_selected == VEHICLE_OPTION else shares,
        "size": size,

        # Compatibility fields.
        # For OPTION positions, these are intentionally premium-safe.
        "price": entry if vehicle_selected == VEHICLE_OPTION else underlying,
        "requested_price": requested_price,
        "fill_price": fill_price,
        "executed_price": fill_price,
        "entry": entry,
        "entry_price": entry,
        "current_price": current_price,
        "current": current_price,

        # Option-premium canonical fields.
        "entry_premium": entry if vehicle_selected == VEHICLE_OPTION else None,
        "premium_entry": entry if vehicle_selected == VEHICLE_OPTION else None,
        "option_entry": entry if vehicle_selected == VEHICLE_OPTION else 0.0,
        "option_entry_price": entry if vehicle_selected == VEHICLE_OPTION else 0.0,
        "current_premium": current_price if vehicle_selected == VEHICLE_OPTION else None,
        "premium_current": current_price if vehicle_selected == VEHICLE_OPTION else None,
        "current_option_mark": current_price if vehicle_selected == VEHICLE_OPTION else None,
        "option_current_mark": current_price if vehicle_selected == VEHICLE_OPTION else None,
        "option_current_price": current_price if vehicle_selected == VEHICLE_OPTION else 0.0,
        "current_option_price": current_price if vehicle_selected == VEHICLE_OPTION else 0.0,

        # Underlying context. For OPTION positions, this is context only.
        "underlying_price": underlying,
        "current_underlying_price": underlying,
        "stock_price": underlying,

        "exit_price": 0.0,
        "close_price": 0.0,

        "stop": stop,
        "target": target,
        "option_stop": stop if vehicle_selected == VEHICLE_OPTION else None,
        "premium_stop": stop if vehicle_selected == VEHICLE_OPTION else None,
        "option_target": target if vehicle_selected == VEHICLE_OPTION else None,
        "premium_target": target if vehicle_selected == VEHICLE_OPTION else None,

        "commission": commission,
        "pnl": 0.0,
        "unrealized_pnl": unrealized_pnl,
        "unrealized_pnl_pct": unrealized_pnl_pct,
        "realized_pnl": 0.0,
        "pnl_basis": pnl_basis,

        "capital_required": capital_required,
        "minimum_trade_cost": minimum_trade_cost,
        "effective_cost": minimum_trade_cost,
        "actual_cost": capital_required,
        "capital_available": capital_available,
        "capital_buffer_after": _capital_buffer_after(capital_available, capital_required),

        "score": round(_safe_float(merged.get("score", 0.0), 0.0), 4),
        "base_score": round(_safe_float(merged.get("base_score", merged.get("score", 0.0)), 0.0), 4),
        "fused_score": round(_safe_float(merged.get("fused_score", merged.get("score", 0.0)), 0.0), 4),
        "confidence": _safe_str(merged.get("confidence", "LOW"), "LOW").upper(),
        "base_confidence": _safe_str(merged.get("base_confidence", merged.get("confidence", "LOW")), "LOW").upper(),
        "v2_confidence": _safe_str(merged.get("v2_confidence", merged.get("confidence", "LOW")), "LOW").upper(),

        "decision_reason": _first_nonempty(
            merged.get("decision_reason"),
            merged.get("final_reason"),
            source_trade.get("decision_reason"),
            "",
        ),
        "decision_reason_code": _first_nonempty(
            merged.get("decision_reason_code"),
            merged.get("final_reason_code"),
            "",
        ),
        "final_reason": _first_nonempty(
            merged.get("final_reason"),
            merged.get("decision_reason"),
            "executed",
        ),
        "final_reason_code": _first_nonempty(
            merged.get("final_reason_code"),
            merged.get("decision_reason_code"),
            "executed",
        ),
        "blocked_at": _safe_str(merged.get("blocked_at"), ""),

        "research_approved": _safe_bool(merged.get("research_approved", True), True),
        "execution_ready": _safe_bool(merged.get("execution_ready", True), True),
        "selected_for_execution": _safe_bool(merged.get("selected_for_execution", True), True),

        "mode": _first_nonempty(mode, merged.get("mode"), ""),
        "trading_mode": _first_nonempty(mode, merged.get("trading_mode"), ""),
        "execution_mode": _first_nonempty(mode, merged.get("execution_mode"), ""),
        "mode_context": mode_context,

        "monitoring_price_type": monitoring_price_type,
        "price_review_basis": price_review_basis,
        "underlying_price_used_for_close_decision": underlying_price_used_for_close_decision,
        "execution_position_shape": execution_position_shape,
        "execution_normalized_by": _safe_str(
            merged.get("execution_normalized_by"),
            "engine.canonical_trade_state",
        ),

        "regime": _safe_str(merged.get("regime"), ""),
        "breadth": _safe_str(merged.get("breadth"), ""),
        "volatility_state": _safe_str(merged.get("volatility_state"), ""),
        "trend": _safe_str(merged.get("trend"), ""),
        "setup_type": _safe_str(merged.get("setup_type"), ""),
        "setup_family": _safe_str(merged.get("setup_family"), ""),
        "entry_quality": _safe_str(merged.get("entry_quality"), ""),
        "atr": round(_safe_float(merged.get("atr", 0.0), 0.0), 4),
        "rsi": round(_safe_float(merged.get("rsi", 0.0), 0.0), 4),

        "option": option_obj,
        "contract": option_obj,
        "contract_symbol": contract_symbol,
        "option_symbol": contract_symbol,
        "option_contract_symbol": contract_symbol,
        "expiry": expiry,
        "expiration": expiry,
        "expiration_date": expiry,
        "strike": strike,
        "strike_price": strike,
        "right": right,
        "option_type": right,
        "call_put": right,
        "mark": round(_safe_float(option_obj.get("mark", 0.0), 0.0), 4),
        "bid": round(_safe_float(option_obj.get("bid", 0.0), 0.0), 4),
        "ask": round(_safe_float(option_obj.get("ask", 0.0), 0.0), 4),
        "last": round(_safe_float(option_obj.get("last", 0.0), 0.0), 4),
        "volume": _safe_int(option_obj.get("volume", merged.get("volume", 0)), 0),
        "open_interest": _safe_int(option_obj.get("open_interest", merged.get("open_interest", 0)), 0),
        "dte": _safe_int(option_obj.get("dte", merged.get("dte", 0)), 0),
        "option_contract_score": round(
            _safe_float(
                merged.get(
                    "option_contract_score",
                    merged.get("option_score", option_obj.get("contract_score", 0.0)),
                ),
                0.0,
            ),
            4,
        ),
        "contract_score": round(
            _safe_float(
                merged.get(
                    "contract_score",
                    merged.get("option_contract_score", option_obj.get("contract_score", 0.0)),
                ),
                0.0,
            ),
            4,
        ),
        "option_explanation": _first_list(merged.get("option_explanation"), option_obj.get("contract_notes")),
        "contract_notes": _first_list(merged.get("contract_notes"), option_obj.get("contract_notes")),

        "option_path": _first_dict(merged.get("option_path"), source_trade.get("option_path")),
        "stock_path": _first_dict(merged.get("stock_path"), source_trade.get("stock_path")),
        "reserve_check": _first_dict(merged.get("reserve_check"), source_trade.get("reserve_check")),
        "governor": _first_dict(merged.get("governor"), source_trade.get("governor")),
        "governor_blocked": _safe_bool(merged.get("governor_blocked", False), False),
        "governor_status": _safe_str(merged.get("governor_status"), ""),
        "governor_reason": _safe_str(merged.get("governor_reason"), ""),
        "governor_reasons": _safe_list(merged.get("governor_reasons")),
        "governor_warnings": _safe_list(merged.get("governor_warnings")),

        "why": _first_list(merged.get("why")),
        "supports": _first_list(merged.get("supports")),
        "blockers": _first_list(merged.get("blockers")),
        "rejection_reason": _safe_str(merged.get("rejection_reason"), ""),
        "rejection_analysis": _first_list(merged.get("rejection_analysis")),
        "stronger_competing_setups": _first_list(merged.get("stronger_competing_setups")),

        "v2": v2,
        "v2_payload": v2_payload,
        "v2_score": round(_safe_float(merged.get("v2_score", v2.get("score", 0.0)), 0.0), 4),
        "v2_quality": round(_safe_float(merged.get("v2_quality", v2.get("quality", 0.0)), 0.0), 4),
        "v2_reason": _safe_str(merged.get("v2_reason", v2.get("reason", "")), ""),
        "v2_regime_alignment": _safe_str(merged.get("v2_regime_alignment", v2.get("regime_alignment", "")), ""),
        "v2_signal_strength": round(_safe_float(merged.get("v2_signal_strength", v2.get("signal_strength", 0.0)), 0.0), 4),
        "v2_conviction_adjustment": round(_safe_float(merged.get("v2_conviction_adjustment", v2.get("conviction_adjustment", 0.0)), 0.0), 4),
        "v2_vehicle_bias": _safe_str(merged.get("v2_vehicle_bias", v2.get("vehicle_bias", "")), "").upper(),
        "v2_thesis": _safe_str(merged.get("v2_thesis", v2.get("thesis", "")), ""),
        "v2_notes": _first_list(merged.get("v2_notes"), v2.get("notes")),
        "v2_risk_flags": _first_list(merged.get("v2_risk_flags"), v2.get("risk_flags")),

        "readiness_score": round(_safe_float(merged.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(merged.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(merged.get("rebuild_pressure", 0.0), 0.0), 4),
        "readiness_notes": _first_list(merged.get("readiness_notes")),
        "promotion_notes": _first_list(merged.get("promotion_notes")),
        "rebuild_notes": _first_list(merged.get("rebuild_notes")),
        "learning_notes": _first_list(merged.get("learning_notes")),
        "learning_exit_notes": _first_list(merged.get("learning_exit_notes")),

        "position_explanation": _first_dict(merged.get("position_explanation")),
        "soulaana": _first_dict(merged.get("soulaana")),
        "monitor_debug": _first_dict(merged.get("monitor_debug")),
        "capital_protection_mode": _safe_bool(merged.get("capital_protection_mode", False), False),
        "capital_protection_snapshot": _first_dict(merged.get("capital_protection_snapshot")),

        "close_reason": "",
        "reason": "",
        "exit_explanation": {},
        "capital_release": {},

        "execution_result": execution_result,
        "raw_source_trade": source_trade,
        "raw_lifecycle": lifecycle,
    }

    return state


def build_closed_trade_state(
    open_trade: Dict[str, Any],
    *,
    exit_price: float,
    close_reason: str,
    closed_at: Optional[str] = None,
    pnl: Optional[float] = None,
    exit_explanation: Optional[Dict[str, Any]] = None,
    capital_release: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    open_trade = deepcopy(_safe_dict(open_trade))
    closed = dict(open_trade)

    vehicle = _detect_vehicle(closed, closed)
    resolved_exit = round(_safe_float(exit_price, 0.0), 4)
    resolved_pnl = round(_safe_float(pnl, 0.0), 4)

    closed["vehicle"] = vehicle
    closed["vehicle_selected"] = vehicle
    closed["selected_vehicle"] = vehicle
    closed["status"] = "CLOSED"
    closed["position_status"] = "CLOSED"
    closed["closed_at"] = _safe_str(closed_at, _now_iso())
    closed["exit_price"] = resolved_exit
    closed["close_price"] = resolved_exit
    closed["close_reason"] = _safe_str(close_reason, "manual")
    closed["reason"] = closed["close_reason"]
    closed["pnl"] = resolved_pnl
    closed["realized_pnl"] = resolved_pnl
    closed["unrealized_pnl"] = 0.0
    closed["exit_explanation"] = _safe_dict(exit_explanation)
    closed["capital_release"] = _safe_dict(capital_release)
    closed["execution_status"] = "CLOSED"

    if vehicle == VEHICLE_OPTION:
        closed["exit_premium"] = resolved_exit
        closed["current_premium"] = resolved_exit
        closed["premium_current"] = resolved_exit
        closed["current_option_mark"] = resolved_exit
        closed["option_current_mark"] = resolved_exit
        closed["option_current_price"] = resolved_exit
        closed["current_option_price"] = resolved_exit
        closed["current_price"] = resolved_exit
        closed["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        closed["monitoring_price_type"] = "OPTION_PREMIUM"
        closed["underlying_price_used_for_close_decision"] = False
        closed["pnl_basis"] = closed.get("pnl_basis") or "option_premium_x_100"

    elif vehicle == VEHICLE_STOCK:
        closed["current_price"] = resolved_exit
        closed["underlying_price"] = resolved_exit
        closed["current_underlying_price"] = resolved_exit
        closed["price_review_basis"] = "STOCK_PRICE"
        closed["monitoring_price_type"] = "UNDERLYING"
        closed["underlying_price_used_for_close_decision"] = True
        closed["pnl_basis"] = closed.get("pnl_basis") or "stock_price_x_shares"

    return closed


def build_trade_log_row(
    trade_state: Dict[str, Any],
    *,
    event: str = "OPEN",
) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    event = _safe_str(event, "OPEN").upper()
    vehicle = _safe_str(trade_state.get("vehicle_selected", trade_state.get("vehicle", "")), "").upper()

    return {
        "timestamp": _first_nonempty(trade_state.get("timestamp"), _now_iso()),
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "vehicle": vehicle,
        "vehicle_selected": vehicle,

        "price": round(_safe_float(trade_state.get("price", 0.0), 0.0), 4),
        "requested_price": round(_safe_float(trade_state.get("requested_price", 0.0), 0.0), 4),
        "fill_price": round(_safe_float(trade_state.get("fill_price", 0.0), 0.0), 4),
        "entry": round(_safe_float(trade_state.get("entry", 0.0), 0.0), 4),
        "entry_price": round(_safe_float(trade_state.get("entry_price", trade_state.get("entry", 0.0)), 0.0), 4),
        "current_price": round(_safe_float(trade_state.get("current_price", 0.0), 0.0), 4),
        "exit_price": round(_safe_float(trade_state.get("exit_price", 0.0), 0.0), 4),

        "entry_premium": round(_safe_float(trade_state.get("entry_premium", 0.0), 0.0), 4),
        "current_premium": round(_safe_float(trade_state.get("current_premium", 0.0), 0.0), 4),
        "current_option_mark": round(_safe_float(trade_state.get("current_option_mark", 0.0), 0.0), 4),
        "option_current_price": round(_safe_float(trade_state.get("option_current_price", 0.0), 0.0), 4),
        "exit_premium": round(_safe_float(trade_state.get("exit_premium", 0.0), 0.0), 4),

        "underlying_price": round(_safe_float(trade_state.get("underlying_price", 0.0), 0.0), 4),
        "current_underlying_price": round(_safe_float(trade_state.get("current_underlying_price", 0.0), 0.0), 4),

        "stop": round(_safe_float(trade_state.get("stop", 0.0), 0.0), 4),
        "target": round(_safe_float(trade_state.get("target", 0.0), 0.0), 4),
        "option_stop": round(_safe_float(trade_state.get("option_stop", 0.0), 0.0), 4),
        "option_target": round(_safe_float(trade_state.get("option_target", 0.0), 0.0), 4),

        "size": _safe_int(trade_state.get("size", 0), 0),
        "shares": _safe_int(trade_state.get("shares", 0), 0),
        "contracts": _safe_int(trade_state.get("contracts", 0), 0),

        "score": round(_safe_float(trade_state.get("score", 0.0), 0.0), 4),
        "fused_score": round(_safe_float(trade_state.get("fused_score", 0.0), 0.0), 4),
        "confidence": _safe_str(trade_state.get("confidence"), "LOW").upper(),
        "status": _safe_str(trade_state.get("status", event), event).upper(),
        "opened_at": _safe_str(trade_state.get("opened_at"), ""),
        "closed_at": _safe_str(trade_state.get("closed_at"), ""),

        "reason": _safe_str(
            trade_state.get("reason")
            or trade_state.get("close_reason")
            or trade_state.get("final_reason"),
            "",
        ),
        "close_reason": _safe_str(trade_state.get("close_reason"), ""),
        "pnl": round(_safe_float(trade_state.get("pnl", 0.0), 0.0), 4),
        "realized_pnl": round(_safe_float(trade_state.get("realized_pnl", 0.0), 0.0), 4),
        "unrealized_pnl": round(_safe_float(trade_state.get("unrealized_pnl", 0.0), 0.0), 4),
        "pnl_basis": _safe_str(trade_state.get("pnl_basis"), ""),

        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "mode": _safe_str(trade_state.get("mode"), ""),
        "regime": _safe_str(trade_state.get("regime"), ""),
        "breadth": _safe_str(trade_state.get("breadth"), ""),
        "volatility_state": _safe_str(trade_state.get("volatility_state"), ""),

        "capital_required": round(_safe_float(trade_state.get("capital_required", 0.0), 0.0), 4),
        "minimum_trade_cost": round(_safe_float(trade_state.get("minimum_trade_cost", 0.0), 0.0), 4),
        "capital_available": round(_safe_float(trade_state.get("capital_available", 0.0), 0.0), 4),

        "research_approved": _safe_bool(trade_state.get("research_approved", False), False),
        "execution_ready": _safe_bool(trade_state.get("execution_ready", False), False),
        "selected_for_execution": _safe_bool(trade_state.get("selected_for_execution", False), False),

        "v2_score": round(_safe_float(trade_state.get("v2_score", 0.0), 0.0), 4),
        "v2_reason": _safe_str(trade_state.get("v2_reason"), ""),
        "readiness_score": round(_safe_float(trade_state.get("readiness_score", 0.0), 0.0), 4),
        "promotion_score": round(_safe_float(trade_state.get("promotion_score", 0.0), 0.0), 4),
        "rebuild_pressure": round(_safe_float(trade_state.get("rebuild_pressure", 0.0), 0.0), 4),

        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),

        "monitoring_price_type": _safe_str(trade_state.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(trade_state.get("price_review_basis"), ""),
        "underlying_price_used_for_close_decision": _safe_bool(
            trade_state.get("underlying_price_used_for_close_decision"),
            vehicle != VEHICLE_OPTION,
        ),
        "execution_position_shape": _safe_str(trade_state.get("execution_position_shape"), ""),

        "contract_symbol": _safe_str(trade_state.get("contract_symbol", trade_state.get("option_symbol")), ""),
        "expiry": _safe_str(trade_state.get("expiry", trade_state.get("expiration")), ""),
        "strike": round(_safe_float(trade_state.get("strike", 0.0), 0.0), 4),
        "right": _safe_str(trade_state.get("right"), ""),
    }


def build_execution_audit_row(
    trade_state: Dict[str, Any],
    *,
    event_type: str,
    note: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    extra = _safe_dict(extra)

    row = {
        "timestamp": _now_iso(),
        "event_type": _safe_str(event_type, "UNKNOWN").upper(),
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "status": _safe_str(trade_state.get("status"), ""),
        "vehicle": _safe_str(trade_state.get("vehicle"), "").upper(),
        "vehicle_selected": _safe_str(trade_state.get("vehicle_selected"), "").upper(),
        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),
        "monitoring_price_type": _safe_str(trade_state.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(trade_state.get("price_review_basis"), ""),
        "underlying_price_used_for_close_decision": _safe_bool(
            trade_state.get("underlying_price_used_for_close_decision"),
            False,
        ),
        "execution_position_shape": _safe_str(trade_state.get("execution_position_shape"), ""),
        "note": _safe_str(note, ""),
        "payload": deepcopy(trade_state),
    }
    row.update(extra)
    return row


def summarize_trade_state(trade_state: Dict[str, Any]) -> Dict[str, Any]:
    trade_state = _safe_dict(trade_state)
    vehicle = _safe_str(trade_state.get("vehicle_selected", trade_state.get("vehicle", "")), "").upper()

    return {
        "trade_id": _safe_str(trade_state.get("trade_id"), ""),
        "symbol": _norm_symbol(trade_state.get("symbol")),
        "status": _safe_str(trade_state.get("status"), ""),
        "strategy": _safe_str(trade_state.get("strategy"), "CALL").upper(),
        "vehicle": vehicle,
        "vehicle_selected": vehicle,
        "entry": round(_safe_float(trade_state.get("entry", 0.0), 0.0), 4),
        "current_price": round(_safe_float(trade_state.get("current_price", 0.0), 0.0), 4),
        "entry_premium": round(_safe_float(trade_state.get("entry_premium", 0.0), 0.0), 4),
        "current_premium": round(_safe_float(trade_state.get("current_premium", 0.0), 0.0), 4),
        "underlying_price": round(_safe_float(trade_state.get("underlying_price", 0.0), 0.0), 4),
        "stop": round(_safe_float(trade_state.get("stop", 0.0), 0.0), 4),
        "target": round(_safe_float(trade_state.get("target", 0.0), 0.0), 4),
        "pnl": round(_safe_float(trade_state.get("pnl", 0.0), 0.0), 4),
        "unrealized_pnl": round(_safe_float(trade_state.get("unrealized_pnl", 0.0), 0.0), 4),
        "unrealized_pnl_pct": round(_safe_float(trade_state.get("unrealized_pnl_pct", 0.0), 0.0), 4),
        "research_approved": _safe_bool(trade_state.get("research_approved", False), False),
        "execution_ready": _safe_bool(trade_state.get("execution_ready", False), False),
        "selected_for_execution": _safe_bool(trade_state.get("selected_for_execution", False), False),
        "final_reason": _safe_str(trade_state.get("final_reason"), ""),
        "final_reason_code": _safe_str(trade_state.get("final_reason_code"), ""),
        "trading_mode": _safe_str(trade_state.get("trading_mode"), ""),
        "monitoring_price_type": _safe_str(trade_state.get("monitoring_price_type"), ""),
        "price_review_basis": _safe_str(trade_state.get("price_review_basis"), ""),
        "underlying_price_used_for_close_decision": _safe_bool(
            trade_state.get("underlying_price_used_for_close_decision"),
            vehicle != VEHICLE_OPTION,
        ),
        "execution_position_shape": _safe_str(trade_state.get("execution_position_shape"), ""),
        "pnl_basis": _safe_str(trade_state.get("pnl_basis"), ""),
    }


__all__ = [
    "build_open_trade_state",
    "build_closed_trade_state",
    "build_trade_log_row",
    "build_execution_audit_row",
    "summarize_trade_state",
]
