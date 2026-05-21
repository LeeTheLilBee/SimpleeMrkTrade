from __future__ import annotations

import json
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from engine.trade_timeline import add_timeline_event
from engine.pdt_guard import can_close_position
from engine.account_state import release_trade_capital
from engine.explainability_engine import explain_exit
from engine.paper_portfolio import archive_closed_position


OPEN_FILE = "data/open_positions.json"
CLOSED_FILE = "data/closed_positions.json"
TRADE_LOG = "data/trade_log.json"

OPTION_CONTRACT_MULTIPLIER = 100

VEHICLE_OPTION = "OPTION"
VEHICLE_STOCK = "STOCK"
VEHICLE_RESEARCH_ONLY = "RESEARCH_ONLY"

MIN_VALID_OPTION_PREMIUM = 0.01
OPTION_UNDERLYING_LEAK_MULTIPLE = 8.0
OPTION_UNDERLYING_LEAK_ABSOLUTE = 25.0
HIGH_OPTION_MOVE_REVIEW_MULTIPLE = 3.0


# =============================================================================
# TIME / FILE HELPERS
# =============================================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path: str, data: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    tmp = file_path.with_suffix(file_path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    tmp.replace(file_path)


# =============================================================================
# BASIC NORMALIZERS
# =============================================================================

def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)

        if isinstance(value, str):
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return float(default)

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
            value = value.replace("$", "").replace(",", "").strip()
            if value == "":
                return None

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
            value = value.replace(",", "").strip()
            if value == "":
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
            if lowered in {"true", "yes", "1", "y"}:
                return True
            if lowered in {"false", "no", "0", "n"}:
                return False

        return bool(value)
    except Exception:
        return bool(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value if value is not None else "").strip()
        return text if text else default
    except Exception:
        return default


def _upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _norm_symbol(value: Any) -> str:
    return _upper(value, "")


def _normalize_reason(reason: Any) -> str:
    text = str(reason or "manual").strip().lower().replace(" ", "_")
    return text or "manual"


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
# POSITION ID / VEHICLE DETECTION
# =============================================================================

def _position_trade_id(position: Dict[str, Any]) -> str:
    return _safe_str(
        position.get(
            "trade_id",
            position.get("position_id", position.get("id", position.get("order_id", ""))),
        ),
        "",
    )


def _detect_vehicle(position: Dict[str, Any]) -> str:
    position = _safe_dict(position)

    raw = _upper(
        position.get(
            "vehicle_selected",
            position.get(
                "selected_vehicle",
                position.get(
                    "vehicle",
                    position.get("asset_type", position.get("instrument_type", "")),
                ),
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

    option = _safe_dict(position.get("option"))
    contract = _safe_dict(position.get("contract"))

    contract_symbol = _first_str(
        position,
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
        _first_str(position, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(option, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(contract, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    contracts = _safe_int(position.get("contracts", position.get("contract_count", 0)), 0)
    shares = _safe_int(position.get("shares", position.get("quantity", 0)), 0)

    if option or contract or contract_symbol or right in {"CALL", "PUT", "C", "P"} or contracts > 0:
        if shares <= 0 or contracts > 0:
            return VEHICLE_OPTION

    return VEHICLE_STOCK


def _strategy(position: Dict[str, Any]) -> str:
    return _upper(position.get("strategy", position.get("direction", position.get("side", "CALL"))), "CALL")


def _find_open_position(
    open_positions: List[Dict[str, Any]],
    symbol: str,
    trade_id: str = "",
) -> Tuple[int, Optional[Dict[str, Any]]]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")

    for idx, pos in enumerate(open_positions):
        row = _safe_dict(pos)

        if trade_id and _position_trade_id(row) == trade_id:
            return idx, dict(row)

        if symbol and _norm_symbol(row.get("symbol")) == symbol:
            return idx, dict(row)

    return -1, None


# =============================================================================
# CONTRACT / PRICE EXTRACTION
# =============================================================================

def _extract_contract(position: Dict[str, Any]) -> Dict[str, Any]:
    position = _safe_dict(position)

    option = _safe_dict(position.get("option"))
    contract = _safe_dict(position.get("contract"))
    selected_contract = _safe_dict(position.get("selected_contract"))
    best_option = _safe_dict(position.get("best_option"))
    best_option_preview = _safe_dict(position.get("best_option_preview"))

    merged: Dict[str, Any] = {}
    merged.update(best_option_preview)
    merged.update(best_option)
    merged.update(selected_contract)
    merged.update(contract)
    merged.update(option)

    contract_symbol = (
        _first_str(
            position,
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
            ],
            "",
        )
    )

    expiry = (
        _first_str(position, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
        or _first_str(merged, ["expiry", "expiration", "expiration_date", "contract_expiry"], "")
    )

    right = _upper(
        _first_str(position, ["right", "option_type", "call_put", "contract_right"], "")
        or _first_str(merged, ["right", "option_type", "call_put", "contract_right"], ""),
        "",
    )

    if right == "C":
        right = "CALL"
    elif right == "P":
        right = "PUT"

    bid = _first_float(position, ["option_bid", "bid"])
    if bid is None:
        bid = _first_float(merged, ["bid"])

    ask = _first_float(position, ["option_ask", "ask"])
    if ask is None:
        ask = _first_float(merged, ["ask"])

    last = _first_float(position, ["option_last", "last"])
    if last is None:
        last = _first_float(merged, ["last", "last_price"])

    mark = _first_float(
        position,
        [
            "current_option_mark",
            "option_current_mark",
            "option_mark",
            "mark",
            "current_premium",
            "premium_current",
            "option_current_price",
            "current_option_price",
            "price_reference",
            "selected_price_reference",
        ],
    )
    if mark is None:
        mark = _first_float(
            merged,
            [
                "current_option_mark",
                "option_current_mark",
                "current_mark",
                "mark",
                "mid",
                "selected_price_reference",
                "price_reference",
            ],
        )

    return {
        "contract_symbol": contract_symbol,
        "expiry": expiry,
        "expiration": expiry,
        "right": right,
        "strike": _first_float(position, ["strike", "strike_price", "contract_strike"])
        or _first_float(merged, ["strike", "strike_price", "contract_strike"]),
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "volume": _safe_int(position.get("option_volume", position.get("volume", merged.get("volume"))), 0),
        "open_interest": _safe_int(
            position.get("option_open_interest", position.get("open_interest", merged.get("open_interest", merged.get("oi")))),
            0,
        ),
        "contract_score": _safe_float(
            position.get("contract_score", position.get("option_contract_score", merged.get("contract_score"))),
            0.0,
        ),
        "price_reference": _safe_float(
            position.get("price_reference", merged.get("price_reference", merged.get("selected_price_reference"))),
            0.0,
        ),
    }


def _underlying_price(position: Dict[str, Any]) -> Optional[float]:
    return _first_float(
        position,
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


def _looks_like_underlying_leak(
    option_entry: Optional[float],
    candidate_price: Optional[float],
    underlying_price: Optional[float],
) -> bool:
    if candidate_price is None:
        return False

    if underlying_price is not None and underlying_price > 0:
        tolerance = max(0.05, underlying_price * 0.002)
        if abs(candidate_price - underlying_price) <= tolerance:
            return True

    if option_entry is not None and option_entry > 0:
        if candidate_price >= OPTION_UNDERLYING_LEAK_ABSOLUTE and candidate_price >= option_entry * OPTION_UNDERLYING_LEAK_MULTIPLE:
            return True

    return False


def _option_entry_premium(position: Dict[str, Any]) -> Optional[float]:
    option = _safe_dict(position.get("option"))
    contract = _safe_dict(position.get("contract"))
    underlying = _underlying_price(position)

    candidates = [
        position.get("entry_premium"),
        position.get("premium_entry"),
        position.get("option_entry"),
        position.get("option_entry_price"),
        position.get("entry_option_mark"),
        position.get("contract_entry_price"),
        position.get("fill_premium"),
        position.get("average_premium"),
        position.get("avg_premium"),
        position.get("debit"),
        position.get("price_paid"),
        position.get("entry"),
        position.get("entry_price"),
        position.get("fill_price"),
        position.get("executed_price"),
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

    for value in candidates:
        price = _safe_optional_float(value)
        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue
        if _looks_like_underlying_leak(None, price, underlying):
            continue
        return round(price, 4)

    return None


def _mid_from_bid_ask(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    if bid <= 0 or ask <= 0:
        return None
    if ask < bid:
        return None
    return round((bid + ask) / 2.0, 4)


def _option_exit_premium(position: Dict[str, Any], requested_exit_price: Any) -> Tuple[float, str, bool]:
    entry = _option_entry_premium(position)
    underlying = _underlying_price(position)
    contract = _extract_contract(position)
    requested = _safe_optional_float(requested_exit_price)
    leak_blocked = False

    if requested is not None and requested >= MIN_VALID_OPTION_PREMIUM:
        if _looks_like_underlying_leak(entry, requested, underlying):
            leak_blocked = True
        else:
            return round(requested, 4), "requested_exit_price", False

    option = _safe_dict(position.get("option"))
    raw_contract = _safe_dict(position.get("contract"))

    candidates: List[Tuple[str, Any]] = [
        ("current_premium", position.get("current_premium")),
        ("premium_current", position.get("premium_current")),
        ("current_option_mark", position.get("current_option_mark")),
        ("option_current_mark", position.get("option_current_mark")),
        ("option_current_price", position.get("option_current_price")),
        ("current_option_price", position.get("current_option_price")),
        ("option_mark", position.get("option_mark")),
        ("mark", position.get("mark")),
        ("price_reference", position.get("price_reference")),
        ("selected_price_reference", position.get("selected_price_reference")),
        ("option.mark", option.get("mark")),
        ("option.current_mark", option.get("current_mark")),
        ("option.selected_price_reference", option.get("selected_price_reference")),
        ("option.price_reference", option.get("price_reference")),
        ("option.last", option.get("last")),
        ("contract.mark", raw_contract.get("mark")),
        ("contract.current_mark", raw_contract.get("current_mark")),
        ("contract.selected_price_reference", raw_contract.get("selected_price_reference")),
        ("contract.price_reference", raw_contract.get("price_reference")),
        ("contract.last", raw_contract.get("last")),
        ("extracted_contract.mark", contract.get("mark")),
        ("extracted_contract.price_reference", contract.get("price_reference")),
        ("extracted_contract.last", contract.get("last")),
    ]

    for source, value in candidates:
        price = _safe_optional_float(value)
        if price is None or price < MIN_VALID_OPTION_PREMIUM:
            continue

        if _looks_like_underlying_leak(entry, price, underlying):
            leak_blocked = True
            continue

        return round(price, 4), source, leak_blocked

    mid = _mid_from_bid_ask(contract.get("bid"), contract.get("ask"))
    if mid is not None and mid >= MIN_VALID_OPTION_PREMIUM:
        if not _looks_like_underlying_leak(entry, mid, underlying):
            return round(mid, 4), "bid_ask_midpoint", leak_blocked
        leak_blocked = True

    legacy_current = _safe_optional_float(position.get("current_price"))
    if legacy_current is not None and legacy_current >= MIN_VALID_OPTION_PREMIUM:
        if not _looks_like_underlying_leak(entry, legacy_current, underlying):
            return round(legacy_current, 4), "safe_legacy_current_price", leak_blocked
        leak_blocked = True

    if entry is not None and entry >= MIN_VALID_OPTION_PREMIUM:
        return round(entry, 4), "entry_premium_fallback", leak_blocked

    return 0.0, "missing_option_exit_premium", leak_blocked


def _stock_entry_price(position: Dict[str, Any]) -> float:
    return _safe_float(
        position.get(
            "entry",
            position.get(
                "entry_price",
                position.get("avg_entry", position.get("average_entry", position.get("fill_price", position.get("price", 0.0)))),
            ),
        ),
        0.0,
    )


def _stock_exit_price(position: Dict[str, Any], requested_exit_price: Any) -> Tuple[float, str]:
    requested = _safe_float(requested_exit_price, 0.0)
    if requested > 0:
        return round(requested, 4), "requested_exit_price"

    for source, value in [
        ("current_price", position.get("current_price")),
        ("current_underlying_price", position.get("current_underlying_price")),
        ("underlying_price", position.get("underlying_price")),
        ("market_price", position.get("market_price")),
        ("stock_price", position.get("stock_price")),
        ("price", position.get("price")),
        ("entry", position.get("entry")),
        ("entry_price", position.get("entry_price")),
    ]:
        price = _safe_float(value, 0.0)
        if price > 0:
            return round(price, 4), source

    return 0.0, "missing_stock_exit_price"


# =============================================================================
# PNL / SIZE / CAPITAL RELEASE
# =============================================================================

def _option_contracts(position: Dict[str, Any]) -> int:
    return max(
        1,
        _safe_int(
            position.get(
                "contracts",
                position.get("contract_count", position.get("quantity", position.get("qty", position.get("size", 1)))),
            ),
            1,
        ),
    )


def _stock_shares(position: Dict[str, Any]) -> int:
    return max(
        1,
        _safe_int(position.get("shares", position.get("quantity", position.get("qty", position.get("size", 1)))), 1),
    )


def _compute_pnl(position: Dict[str, Any], exit_price: float) -> Tuple[float, Dict[str, Any]]:
    vehicle = _detect_vehicle(position)
    strategy = _strategy(position)

    if vehicle == VEHICLE_OPTION:
        entry_premium = _option_entry_premium(position)
        exit_premium = _safe_float(exit_price, 0.0)
        contracts = _option_contracts(position)

        if entry_premium is None or entry_premium <= 0 or exit_premium <= 0:
            return 0.0, {
                "pnl_valid": False,
                "pnl_basis": "option_premium_x_100",
                "pnl_error": "missing_option_entry_or_exit_premium",
                "entry_premium": entry_premium,
                "exit_premium": exit_premium,
                "contracts": contracts,
                "multiplier": OPTION_CONTRACT_MULTIPLIER,
            }

        pnl = (exit_premium - entry_premium) * OPTION_CONTRACT_MULTIPLIER * contracts
        pnl_pct = ((exit_premium - entry_premium) / entry_premium) * 100.0
        move_multiple = exit_premium / entry_premium if entry_premium > 0 else 0.0

        return round(pnl, 2), {
            "pnl_valid": True,
            "pnl_basis": "option_premium_x_100",
            "entry_premium": round(entry_premium, 4),
            "exit_premium": round(exit_premium, 4),
            "contracts": contracts,
            "multiplier": OPTION_CONTRACT_MULTIPLIER,
            "pnl_pct": round(pnl_pct, 4),
            "move_multiple": round(move_multiple, 4),
            "option_pnl_rule": "(exit_premium - entry_premium) * 100 * contracts",
        }

    entry_price = _stock_entry_price(position)
    stock_exit_price = _safe_float(exit_price, 0.0)
    shares = _stock_shares(position)

    if entry_price <= 0 or stock_exit_price <= 0:
        return 0.0, {
            "pnl_valid": False,
            "pnl_basis": "stock_price_x_shares",
            "pnl_error": "missing_stock_entry_or_exit_price",
            "entry_price": entry_price,
            "exit_price": stock_exit_price,
            "shares": shares,
        }

    if "PUT" in strategy or "SHORT" in strategy:
        pnl = (entry_price - stock_exit_price) * shares
        pnl_rule = "(entry_price - exit_price) * shares"
    else:
        pnl = (stock_exit_price - entry_price) * shares
        pnl_rule = "(exit_price - entry_price) * shares"

    pnl_pct = (pnl / (entry_price * shares)) * 100.0 if entry_price > 0 and shares > 0 else 0.0

    return round(pnl, 2), {
        "pnl_valid": True,
        "pnl_basis": "stock_price_x_shares",
        "entry_price": round(entry_price, 4),
        "exit_price": round(stock_exit_price, 4),
        "shares": shares,
        "pnl_pct": round(pnl_pct, 4),
        "stock_pnl_rule": pnl_rule,
    }


def _capital_release_inputs(position: Dict[str, Any], exit_price: float) -> Tuple[float, int, Dict[str, Any]]:
    vehicle = _detect_vehicle(position)

    if vehicle == VEHICLE_OPTION:
        entry_premium = _option_entry_premium(position) or 0.0
        exit_premium = _safe_float(exit_price, 0.0)
        contracts = _option_contracts(position)

        return entry_premium, contracts, {
            "capital_release_basis": "option_entry_premium_x_100_x_contracts",
            "entry_premium": round(entry_premium, 4),
            "exit_premium": round(exit_premium, 4),
            "contracts": contracts,
            "multiplier": OPTION_CONTRACT_MULTIPLIER,
            "release_basis_entry": round(entry_premium * OPTION_CONTRACT_MULTIPLIER, 4),
            "release_basis_exit": round(exit_premium * OPTION_CONTRACT_MULTIPLIER, 4),
            "vehicle": VEHICLE_OPTION,
        }

    entry_price = _stock_entry_price(position)
    stock_exit_price = _safe_float(exit_price, 0.0)
    shares = _stock_shares(position)

    return entry_price, shares, {
        "capital_release_basis": "stock_entry_price_x_shares",
        "entry_price": round(entry_price, 4),
        "exit_price": round(stock_exit_price, 4),
        "shares": shares,
        "release_basis_entry": round(entry_price, 4),
        "release_basis_exit": round(stock_exit_price, 4),
        "vehicle": VEHICLE_STOCK,
    }


def _patch_capital_release_metadata(capital_release: Any, release_meta: Dict[str, Any], vehicle: str) -> Any:
    if not isinstance(capital_release, dict):
        return capital_release

    patched = dict(capital_release)
    metadata = dict(_safe_dict(patched.get("metadata")))

    metadata["vehicle"] = vehicle
    metadata["capital_release_rule"] = release_meta.get("capital_release_basis", metadata.get("capital_release_rule", ""))
    metadata["capital_release_basis"] = release_meta.get("capital_release_basis", "")
    metadata["entry_premium"] = release_meta.get("entry_premium", metadata.get("entry_premium"))
    metadata["exit_premium"] = release_meta.get("exit_premium", metadata.get("exit_premium"))
    metadata["contracts"] = release_meta.get("contracts", metadata.get("contracts"))
    metadata["shares"] = release_meta.get("shares", metadata.get("shares"))

    patched["metadata"] = metadata
    return patched


# =============================================================================
# PERFORMANCE CLASSIFICATION
# =============================================================================

def _performance_classification(
    *,
    vehicle: str,
    reason: str,
    pnl_meta: Dict[str, Any],
    exit_source: str,
    leak_blocked: bool,
) -> Dict[str, Any]:
    reason_text = _safe_str(reason, "").lower()
    pnl_valid = _safe_bool(pnl_meta.get("pnl_valid"), False)

    if "manual_option_premium_test" in reason_text or "manual_test" in reason_text or reason_text.endswith("_test"):
        return {
            "performance_classification": "MANUAL_TEST",
            "performance_include": False,
            "include_in_performance": False,
            "counts_in_performance": False,
            "needs_review": False,
            "classification_reason": "manual_or_test_reason",
        }

    if "controlled_slot_release" in reason_text or "slot_release" in reason_text:
        return {
            "performance_classification": "CONTROLLED_RELEASE",
            "performance_include": False,
            "include_in_performance": False,
            "counts_in_performance": False,
            "needs_review": False,
            "classification_reason": "controlled_release_reason",
        }

    if leak_blocked:
        return {
            "performance_classification": "QUARANTINED_BAD_CLOSE",
            "performance_include": False,
            "include_in_performance": False,
            "counts_in_performance": False,
            "needs_review": False,
            "classification_reason": "option_underlying_leak_blocked_on_close",
        }

    if not pnl_valid:
        return {
            "performance_classification": "QUARANTINED_BAD_CLOSE",
            "performance_include": False,
            "include_in_performance": False,
            "counts_in_performance": False,
            "needs_review": False,
            "classification_reason": "invalid_pnl_inputs",
        }

    if vehicle == VEHICLE_OPTION:
        move_multiple = _safe_float(pnl_meta.get("move_multiple"), 0.0)
        high_move = move_multiple >= HIGH_OPTION_MOVE_REVIEW_MULTIPLE

        return {
            "performance_classification": "REAL_TRADE",
            "performance_include": True,
            "include_in_performance": True,
            "counts_in_performance": True,
            "needs_review": False,
            "classification_reason": "verified_option_premium_close",
            "high_option_move": bool(high_move),
            "high_option_move_multiple": round(move_multiple, 4),
            "high_option_move_note": (
                "High premium move, but counted because exit premium passed option-premium validation."
                if high_move
                else ""
            ),
            "option_exit_validation_source": exit_source,
        }

    return {
        "performance_classification": "REAL_TRADE",
        "performance_include": True,
        "include_in_performance": True,
        "counts_in_performance": True,
        "needs_review": False,
        "classification_reason": "valid_stock_close",
    }


# =============================================================================
# EXPLANATION / CLOSE FIELDS
# =============================================================================

def _fallback_exit_explanation(
    *,
    symbol: str,
    vehicle: str,
    reason: str,
    pnl: float,
    pnl_meta: Dict[str, Any],
    exit_price: float,
) -> Dict[str, Any]:
    pnl_pct = _safe_float(pnl_meta.get("pnl_pct"), 0.0)

    if pnl > 0:
        verdict = "PROFIT"
        headline = f"{symbol} closed for profit"
        summary = f"The {vehicle.lower()} position closed with a realized gain."
    elif pnl < 0:
        verdict = "LOSS"
        headline = f"{symbol} closed for loss"
        summary = f"The {vehicle.lower()} position closed with a realized loss."
    else:
        verdict = "FLAT"
        headline = f"{symbol} closed flat"
        summary = f"The {vehicle.lower()} position closed near breakeven."

    return {
        "symbol": symbol,
        "vehicle": vehicle,
        "headline": headline,
        "summary": summary,
        "verdict": verdict,
        "reason": f"Closed by {reason}.",
        "why": f"Closed by {reason}.",
        "notes": [
            f"PnL: {round(pnl, 2)}",
            f"PnL %: {pnl_pct}",
            f"Exit price: {round(exit_price, 4)}",
            f"PnL basis: {pnl_meta.get('pnl_basis', '')}",
        ],
        "next_action": "Review whether the exit matched the thesis and pressure profile.",
    }


def _clean_exit_explanation(
    exit_explanation: Any,
    *,
    symbol: str,
    vehicle: str,
    reason: str,
    pnl: float,
    pnl_meta: Dict[str, Any],
    exit_price: float,
) -> Dict[str, Any]:
    fallback = _fallback_exit_explanation(
        symbol=symbol,
        vehicle=vehicle,
        reason=reason,
        pnl=pnl,
        pnl_meta=pnl_meta,
        exit_price=exit_price,
    )

    if not isinstance(exit_explanation, dict):
        return fallback

    cleaned = dict(exit_explanation)

    cleaned["symbol"] = symbol
    cleaned["vehicle"] = vehicle

    for key, value in fallback.items():
        if key not in cleaned or cleaned.get(key) in [None, "", [], {}]:
            cleaned[key] = value

    # close_trade.py is the source of truth for realized close math.
    # This prevents old explainability text from saying PnL: 0.0 after a real close.
    cleaned["notes"] = fallback["notes"]
    cleaned["realized_pnl"] = round(pnl, 2)
    cleaned["pnl_basis"] = pnl_meta.get("pnl_basis", "")
    cleaned["pnl_pct"] = pnl_meta.get("pnl_pct", 0.0)
    cleaned["exit_price"] = round(exit_price, 4)

    if pnl > 0:
        cleaned["verdict"] = "PROFIT"
        cleaned["summary"] = fallback["summary"]
        if not cleaned.get("headline") or "unknown" in str(cleaned.get("headline", "")).lower():
            cleaned["headline"] = fallback["headline"]
    elif pnl < 0:
        cleaned["verdict"] = "LOSS"
        cleaned["summary"] = fallback["summary"]
        if not cleaned.get("headline") or "unknown" in str(cleaned.get("headline", "")).lower():
            cleaned["headline"] = fallback["headline"]
    else:
        cleaned["verdict"] = cleaned.get("verdict") or "FLAT"

    return cleaned


def _apply_contract_fields(matched: Dict[str, Any], contract: Dict[str, Any]) -> None:
    contract_symbol = _safe_str(contract.get("contract_symbol"), "")
    if contract_symbol:
        matched["contract_symbol"] = contract_symbol
        matched["option_symbol"] = contract_symbol
        matched["option_contract_symbol"] = contract_symbol
        matched["contractSymbol"] = contract_symbol

    expiry = _safe_str(contract.get("expiry") or contract.get("expiration"), "")
    if expiry:
        matched["expiry"] = expiry
        matched["expiration"] = expiry
        matched["expiration_date"] = expiry

    if contract.get("strike") is not None:
        matched["strike"] = contract.get("strike")
        matched["strike_price"] = contract.get("strike")

    right = _safe_str(contract.get("right"), "")
    if right:
        matched["right"] = right
        matched["option_type"] = right
        matched["call_put"] = right

    for key in ["bid", "ask", "last", "mark", "volume", "open_interest", "contract_score", "price_reference"]:
        if contract.get(key) not in (None, ""):
            matched[key] = contract.get(key)


def _apply_option_close_aliases(
    matched: Dict[str, Any],
    *,
    entry_premium: float,
    exit_premium: float,
    contracts: int,
    underlying: Optional[float],
    leak_blocked: bool,
) -> None:
    entry_premium = round(_safe_float(entry_premium, 0.0), 4)
    exit_premium = round(_safe_float(exit_premium, 0.0), 4)
    contracts = max(1, _safe_int(contracts, 1))

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
        matched[key] = entry_premium

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
        matched[key] = exit_premium

    matched["contracts"] = contracts
    matched["contract_count"] = contracts
    matched["quantity"] = contracts
    matched["qty"] = contracts
    matched["size"] = contracts
    matched["shares"] = 0

    if underlying is not None and underlying > 0:
        matched["underlying_price"] = round(underlying, 4)
        matched["current_underlying_price"] = round(underlying, 4)

    matched["price_review_basis"] = "OPTION_PREMIUM_ONLY"
    matched["monitoring_price_type"] = "OPTION_PREMIUM"
    matched["monitoring_mode"] = "OPTION_PREMIUM"
    matched["price_basis"] = "OPTION_PREMIUM"
    matched["underlying_price_used_for_close_decision"] = False
    matched["underlying_price_used_for_pnl"] = False
    matched["option_underlying_leak_blocked"] = bool(leak_blocked)
    matched["option_underlying_leak_blocked_on_close"] = bool(leak_blocked)
    matched["execution_position_shape"] = "OPTION_PREMIUM_POSITION"


def _apply_close_fields(
    position: Dict[str, Any],
    *,
    exit_price: float,
    exit_source: str,
    reason: str,
    pnl: float,
    pnl_meta: Dict[str, Any],
    closed_at: str,
    pdt_meta: Dict[str, Any],
    capital_release: Any,
    capital_release_meta: Dict[str, Any],
    leak_blocked: bool,
) -> Dict[str, Any]:
    matched = dict(position)
    vehicle = _detect_vehicle(matched)
    contract = _extract_contract(matched)

    matched["vehicle"] = vehicle
    matched["vehicle_selected"] = vehicle
    matched["selected_vehicle"] = vehicle
    matched["asset_type"] = vehicle
    matched["instrument_type"] = vehicle

    matched["status"] = "CLOSED"
    matched["position_status"] = "CLOSED"
    matched["execution_status"] = "CLOSED"
    matched["lifecycle_state"] = "CLOSED"
    matched["lifecycle_stage"] = "CLOSED"

    matched["closed_at"] = closed_at
    matched["exit_time"] = closed_at
    matched["exited_at"] = closed_at

    matched["reason"] = reason
    matched["close_reason"] = reason

    matched["pnl"] = pnl
    matched["realized_pnl"] = pnl
    matched["unrealized_pnl"] = 0.0
    matched["pnl_meta"] = pnl_meta
    matched["pnl_basis"] = pnl_meta.get("pnl_basis")
    matched["pnl_pct"] = pnl_meta.get("pnl_pct")

    matched["exit_price_source"] = exit_source
    matched["capital_release"] = capital_release
    matched["capital_release_meta"] = capital_release_meta
    matched["closed_by"] = "close_trade.py"

    if vehicle == VEHICLE_OPTION:
        underlying = _underlying_price(matched)
        entry_premium = _safe_float(pnl_meta.get("entry_premium", _option_entry_premium(matched)), 0.0)
        exit_premium = _safe_float(pnl_meta.get("exit_premium", exit_price), 0.0)
        contracts = _safe_int(pnl_meta.get("contracts", _option_contracts(matched)), 1)

        _apply_option_close_aliases(
            matched,
            entry_premium=entry_premium,
            exit_premium=exit_premium,
            contracts=contracts,
            underlying=underlying,
            leak_blocked=leak_blocked,
        )
        _apply_contract_fields(matched, contract)

    elif vehicle == VEHICLE_STOCK:
        matched["exit_price"] = round(exit_price, 4)
        matched["close_price"] = round(exit_price, 4)
        matched["current_price"] = round(exit_price, 4)
        matched["current"] = round(exit_price, 4)
        matched["underlying_price"] = round(exit_price, 4)
        matched["current_underlying_price"] = round(exit_price, 4)
        matched["price_review_basis"] = "STOCK_PRICE"
        matched["monitoring_price_type"] = "UNDERLYING"
        matched["monitoring_mode"] = "UNDERLYING"
        matched["price_basis"] = "STOCK_PRICE"
        matched["underlying_price_used_for_close_decision"] = True
        matched["underlying_price_used_for_pnl"] = True
        matched["contracts"] = 0
        matched["contract_count"] = 0
        matched["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

    perf = _performance_classification(
        vehicle=vehicle,
        reason=reason,
        pnl_meta=pnl_meta,
        exit_source=exit_source,
        leak_blocked=leak_blocked,
    )
    matched.update(perf)

    matched["close_audit"] = {
        "closed_at": closed_at,
        "vehicle": vehicle,
        "reason": reason,
        "exit_price": round(exit_price, 4),
        "exit_price_source": exit_source,
        "pnl": pnl,
        "pnl_meta": pnl_meta,
        "pdt_meta": pdt_meta,
        "capital_release": capital_release,
        "capital_release_meta": capital_release_meta,
        "price_review_basis": matched.get("price_review_basis"),
        "monitoring_price_type": matched.get("monitoring_price_type"),
        "underlying_price_used_for_close_decision": matched.get("underlying_price_used_for_close_decision"),
        "underlying_price_used_for_pnl": matched.get("underlying_price_used_for_pnl"),
        "option_underlying_leak_blocked": bool(leak_blocked),
        "performance_classification": matched.get("performance_classification"),
        "performance_include": matched.get("performance_include"),
        "needs_review": matched.get("needs_review"),
        "classification_reason": matched.get("classification_reason"),
    }

    return matched


# =============================================================================
# TRADE LOG
# =============================================================================

def _build_close_trade_log_row(
    *,
    symbol: str,
    matched: Dict[str, Any],
    exit_price: float,
    exit_source: str,
    reason: str,
    pnl: float,
    pnl_meta: Dict[str, Any],
    closed_at: str,
    exit_explanation: Dict[str, Any],
) -> Dict[str, Any]:
    vehicle = _detect_vehicle(matched)

    row: Dict[str, Any] = {
        "timestamp": closed_at,
        "trade_id": _position_trade_id(matched),
        "symbol": symbol,
        "strategy": matched.get("strategy", matched.get("side", "")),
        "vehicle": vehicle,
        "vehicle_selected": vehicle,
        "selected_vehicle": vehicle,
        "action": "CLOSE",
        "status": "CLOSED",
        "exit_price": round(exit_price, 4),
        "close_price": round(exit_price, 4),
        "closed_at": closed_at,
        "exit_time": closed_at,
        "reason": reason,
        "reason_code": reason,
        "close_reason": reason,
        "pnl": pnl,
        "realized_pnl": pnl,
        "unrealized_pnl": 0.0,
        "pnl_meta": pnl_meta,
        "pnl_basis": pnl_meta.get("pnl_basis"),
        "pnl_pct": pnl_meta.get("pnl_pct"),
        "exit_price_source": exit_source,
        "exit_explanation": exit_explanation,
        "price_review_basis": matched.get("price_review_basis"),
        "monitoring_price_type": matched.get("monitoring_price_type"),
        "underlying_price_used_for_close_decision": matched.get("underlying_price_used_for_close_decision"),
        "underlying_price_used_for_pnl": matched.get("underlying_price_used_for_pnl"),
        "execution_position_shape": matched.get("execution_position_shape"),
        "performance_classification": matched.get("performance_classification"),
        "performance_include": matched.get("performance_include"),
        "include_in_performance": matched.get("performance_include"),
        "counts_in_performance": matched.get("performance_include"),
        "needs_review": matched.get("needs_review"),
        "classification_reason": matched.get("classification_reason"),
        "high_option_move": matched.get("high_option_move", False),
        "high_option_move_multiple": matched.get("high_option_move_multiple", 0.0),
    }

    if vehicle == VEHICLE_OPTION:
        row.update(
            {
                "entry": matched.get("entry_premium", matched.get("entry")),
                "entry_price": matched.get("entry_premium", matched.get("entry_price")),
                "entry_premium": matched.get("entry_premium"),
                "premium_entry": matched.get("entry_premium"),
                "exit_premium": round(exit_price, 4),
                "premium_exit": round(exit_price, 4),
                "option_exit": round(exit_price, 4),
                "option_exit_price": round(exit_price, 4),
                "current_premium": round(exit_price, 4),
                "current_option_mark": round(exit_price, 4),
                "contracts": matched.get("contracts", pnl_meta.get("contracts", 1)),
                "quantity": matched.get("contracts", pnl_meta.get("contracts", 1)),
                "shares": 0,
                "underlying_price": matched.get("underlying_price"),
                "current_underlying_price": matched.get("current_underlying_price"),
                "contract_symbol": matched.get("contract_symbol", matched.get("option_symbol")),
                "option_symbol": matched.get("option_symbol", matched.get("contract_symbol")),
                "expiry": matched.get("expiry", matched.get("expiration")),
                "expiration": matched.get("expiration", matched.get("expiry")),
                "strike": matched.get("strike"),
                "right": matched.get("right"),
                "bid": matched.get("bid"),
                "ask": matched.get("ask"),
                "last": matched.get("last"),
                "mark": matched.get("mark"),
                "open_interest": matched.get("open_interest"),
                "volume": matched.get("volume"),
                "option_underlying_leak_blocked": matched.get("option_underlying_leak_blocked"),
            }
        )
    else:
        row.update(
            {
                "entry": matched.get("entry"),
                "entry_price": matched.get("entry_price"),
                "current_price": round(exit_price, 4),
                "shares": matched.get("shares", pnl_meta.get("shares", 1)),
                "quantity": matched.get("shares", pnl_meta.get("shares", 1)),
                "contracts": 0,
            }
        )

    return row


def _update_or_append_trade_log_row(
    trade_log: List[Any],
    *,
    symbol: str,
    matched: Dict[str, Any],
    exit_price: float,
    exit_source: str,
    reason: str,
    pnl: float,
    pnl_meta: Dict[str, Any],
    closed_at: str,
    exit_explanation: Dict[str, Any],
) -> Dict[str, Any]:
    resolved_trade_id = _position_trade_id(matched)
    vehicle = _detect_vehicle(matched)

    for trade in reversed(trade_log):
        if not isinstance(trade, dict):
            continue

        same_trade_id = resolved_trade_id and _safe_str(trade.get("trade_id"), "") == resolved_trade_id
        same_symbol_open = (
            not resolved_trade_id
            and _norm_symbol(trade.get("symbol")) == symbol
            and _upper(trade.get("status"), "") in {"OPEN", "FILLED", "ENTERED"}
        )

        if not (same_trade_id or same_symbol_open):
            continue

        trade["status"] = "CLOSED"
        trade["vehicle"] = vehicle
        trade["vehicle_selected"] = vehicle
        trade["selected_vehicle"] = vehicle
        trade["exit_price"] = round(exit_price, 4)
        trade["close_price"] = round(exit_price, 4)
        trade["closed_at"] = closed_at
        trade["exit_time"] = closed_at
        trade["reason"] = reason
        trade["close_reason"] = reason
        trade["pnl"] = pnl
        trade["realized_pnl"] = pnl
        trade["unrealized_pnl"] = 0.0
        trade["pnl_meta"] = pnl_meta
        trade["pnl_basis"] = pnl_meta.get("pnl_basis")
        trade["pnl_pct"] = pnl_meta.get("pnl_pct")
        trade["exit_price_source"] = exit_source
        trade["exit_explanation"] = exit_explanation
        trade["price_review_basis"] = matched.get("price_review_basis")
        trade["monitoring_price_type"] = matched.get("monitoring_price_type")
        trade["underlying_price_used_for_close_decision"] = matched.get("underlying_price_used_for_close_decision")
        trade["underlying_price_used_for_pnl"] = matched.get("underlying_price_used_for_pnl")
        trade["execution_position_shape"] = matched.get("execution_position_shape")
        trade["performance_classification"] = matched.get("performance_classification")
        trade["performance_include"] = matched.get("performance_include")
        trade["include_in_performance"] = matched.get("performance_include")
        trade["counts_in_performance"] = matched.get("performance_include")
        trade["needs_review"] = matched.get("needs_review")
        trade["classification_reason"] = matched.get("classification_reason")

        if vehicle == VEHICLE_OPTION:
            trade["entry"] = matched.get("entry_premium")
            trade["entry_price"] = matched.get("entry_premium")
            trade["entry_premium"] = matched.get("entry_premium")
            trade["premium_entry"] = matched.get("entry_premium")
            trade["exit_premium"] = round(exit_price, 4)
            trade["premium_exit"] = round(exit_price, 4)
            trade["current_premium"] = round(exit_price, 4)
            trade["current_option_mark"] = round(exit_price, 4)
            trade["contracts"] = pnl_meta.get("contracts")
            trade["shares"] = 0
            trade["contract_symbol"] = matched.get("contract_symbol", matched.get("option_symbol"))
            trade["option_symbol"] = matched.get("contract_symbol", matched.get("option_symbol"))
            trade["expiry"] = matched.get("expiry", matched.get("expiration"))
            trade["expiration"] = matched.get("expiration", matched.get("expiry"))
            trade["strike"] = matched.get("strike")
            trade["right"] = matched.get("right")
            trade["option_underlying_leak_blocked"] = matched.get("option_underlying_leak_blocked")

        break

    close_row = _build_close_trade_log_row(
        symbol=symbol,
        matched=matched,
        exit_price=exit_price,
        exit_source=exit_source,
        reason=reason,
        pnl=pnl,
        pnl_meta=pnl_meta,
        closed_at=closed_at,
        exit_explanation=exit_explanation,
    )

    trade_log.append(close_row)
    return close_row


# =============================================================================
# PUBLIC CLOSE FUNCTION
# =============================================================================

def close_position(symbol: Any, exit_price: Any, reason: str = "manual", trade_id: str = "") -> Dict[str, Any]:
    symbol = _norm_symbol(symbol)
    trade_id = _safe_str(trade_id, "")
    reason = _normalize_reason(reason)

    open_positions = _load(OPEN_FILE, [])
    closed_positions = _load(CLOSED_FILE, [])
    trade_log = _load(TRADE_LOG, [])

    if not isinstance(open_positions, list):
        open_positions = []
    if not isinstance(closed_positions, list):
        closed_positions = []
    if not isinstance(trade_log, list):
        trade_log = []

    idx, matched = _find_open_position(open_positions, symbol=symbol, trade_id=trade_id)

    if matched is None or idx < 0:
        return {
            "closed": False,
            "blocked": False,
            "reason": "position_not_found",
            "symbol": symbol,
            "trade_id": trade_id,
        }

    if not symbol:
        symbol = _norm_symbol(matched.get("symbol"))

    vehicle = _detect_vehicle(matched)
    resolved_trade_id = _position_trade_id(matched) or trade_id

    if vehicle == VEHICLE_RESEARCH_ONLY:
        return {
            "closed": False,
            "blocked": True,
            "reason": "research_only_position_cannot_be_closed",
            "symbol": symbol,
            "trade_id": resolved_trade_id,
            "vehicle": vehicle,
        }

    emergency = ("risk" in reason) or ("stop" in reason) or ("loss" in reason)
    pdt_check = can_close_position(matched, emergency=emergency)

    if isinstance(pdt_check, dict) and pdt_check.get("blocked"):
        return {
            "closed": False,
            "blocked": True,
            "reason": pdt_check.get("reason"),
            "symbol": symbol,
            "trade_id": resolved_trade_id,
            "vehicle": vehicle,
            "meta": pdt_check.get("meta", {}),
        }

    pdt_meta = pdt_check.get("meta", {}) if isinstance(pdt_check, dict) else {}

    if vehicle == VEHICLE_OPTION:
        resolved_exit_price, exit_source, leak_blocked = _option_exit_premium(matched, exit_price)

        if resolved_exit_price <= 0:
            return {
                "closed": False,
                "blocked": True,
                "reason": "missing_valid_option_exit_premium",
                "symbol": symbol,
                "trade_id": resolved_trade_id,
                "vehicle": vehicle,
                "requested_exit_price": exit_price,
                "price_review_basis": "OPTION_PREMIUM_ONLY",
                "underlying_price_used_for_close_decision": False,
                "underlying_price_used_for_pnl": False,
                "option_underlying_leak_blocked": leak_blocked,
            }

    else:
        resolved_exit_price, exit_source = _stock_exit_price(matched, exit_price)
        leak_blocked = False

        if resolved_exit_price <= 0:
            return {
                "closed": False,
                "blocked": True,
                "reason": "missing_valid_stock_exit_price",
                "symbol": symbol,
                "trade_id": resolved_trade_id,
                "vehicle": vehicle,
                "requested_exit_price": exit_price,
                "price_review_basis": "STOCK_PRICE",
                "underlying_price_used_for_close_decision": True,
                "underlying_price_used_for_pnl": True,
            }

    pnl, pnl_meta = _compute_pnl(matched, resolved_exit_price)
    closed_at = _now_iso()

    matched_for_explanation = dict(matched)
    matched_for_explanation["symbol"] = symbol
    matched_for_explanation["trade_id"] = resolved_trade_id
    matched_for_explanation["vehicle"] = vehicle
    matched_for_explanation["vehicle_selected"] = vehicle
    matched_for_explanation["selected_vehicle"] = vehicle
    matched_for_explanation["pnl"] = pnl
    matched_for_explanation["realized_pnl"] = pnl
    matched_for_explanation["exit_price"] = resolved_exit_price

    if vehicle == VEHICLE_OPTION:
        matched_for_explanation["exit_premium"] = resolved_exit_price
        matched_for_explanation["current_premium"] = resolved_exit_price
        matched_for_explanation["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        matched_for_explanation["monitoring_price_type"] = "OPTION_PREMIUM"
        matched_for_explanation["underlying_price_used_for_close_decision"] = False
        matched_for_explanation["underlying_price_used_for_pnl"] = False

    try:
        raw_exit_explanation = explain_exit(
            reason=reason,
            pnl=pnl,
            position=matched_for_explanation,
            exit_price=resolved_exit_price,
        )
    except Exception as exc:
        raw_exit_explanation = {
            "symbol": symbol,
            "headline": f"{symbol} exit detail unavailable",
            "summary": f"Exit explanation unavailable: {exc}",
            "verdict": "EXIT",
            "reason": reason,
            "why": reason,
            "notes": [f"PnL: {pnl}", f"Exit price: {resolved_exit_price}"],
            "next_action": "Review this close in the trade journal.",
        }

    exit_explanation = _clean_exit_explanation(
        raw_exit_explanation,
        symbol=symbol,
        vehicle=vehicle,
        reason=reason,
        pnl=pnl,
        pnl_meta=pnl_meta,
        exit_price=resolved_exit_price,
    )

    release_price_basis, release_size, release_meta = _capital_release_inputs(matched, resolved_exit_price)

    try:
        capital_release = release_trade_capital(
            entry_price=release_price_basis,
            size=release_size,
            pnl=pnl,
            immediate=True,
            symbol=symbol,
            trade_id=resolved_trade_id,
            vehicle=vehicle,
            metadata={
                "source": "close_trade.py",
                "symbol": symbol,
                "trade_id": resolved_trade_id,
                "vehicle": vehicle,
                "price_review_basis": "OPTION_PREMIUM_ONLY" if vehicle == VEHICLE_OPTION else "STOCK_PRICE",
                "monitoring_price_type": "OPTION_PREMIUM" if vehicle == VEHICLE_OPTION else "UNDERLYING",
                "exit_price": round(resolved_exit_price, 4),
                "exit_price_source": exit_source,
                "close_reason": reason,
                **release_meta,
            },
        )
    except Exception as exc:
        capital_release = {
            "released": False,
            "error": str(exc),
            "release_meta": release_meta,
        }

    capital_release = _patch_capital_release_metadata(capital_release, release_meta, vehicle)

    matched = _apply_close_fields(
        matched,
        exit_price=resolved_exit_price,
        exit_source=exit_source,
        reason=reason,
        pnl=pnl,
        pnl_meta=pnl_meta,
        closed_at=closed_at,
        pdt_meta=pdt_meta,
        capital_release=capital_release,
        capital_release_meta=release_meta,
        leak_blocked=leak_blocked,
    )

    matched["trade_id"] = resolved_trade_id
    matched["exit_explanation"] = exit_explanation
    matched["capital_release_meta"] = release_meta

    remaining = [row for i, row in enumerate(open_positions) if i != idx]

    trade_log_row = _update_or_append_trade_log_row(
        trade_log,
        symbol=symbol,
        matched=matched,
        exit_price=resolved_exit_price,
        exit_source=exit_source,
        reason=reason,
        pnl=pnl,
        pnl_meta=pnl_meta,
        closed_at=closed_at,
        exit_explanation=exit_explanation,
    )

    matched["trade_log_row"] = trade_log_row

    try:
        archived = archive_closed_position(
            matched,
            exit_price=resolved_exit_price,
            close_reason=reason,
            closed_at=closed_at,
            pnl=pnl,
            exit_explanation=exit_explanation,
            capital_release=capital_release,
        )

        if isinstance(archived, dict):
            archived["trade_log_row"] = trade_log_row
            archived["exit_explanation"] = _clean_exit_explanation(
                archived.get("exit_explanation", exit_explanation),
                symbol=symbol,
                vehicle=vehicle,
                reason=reason,
                pnl=pnl,
                pnl_meta=pnl_meta,
                exit_price=resolved_exit_price,
            )
            archived["capital_release"] = _patch_capital_release_metadata(
                archived.get("capital_release", capital_release),
                release_meta,
                vehicle,
            )
            archived["capital_release_meta"] = release_meta

    except Exception:
        archived = matched
        closed_positions.append(matched)
        _save(CLOSED_FILE, closed_positions)

    _save(OPEN_FILE, remaining)
    _save(TRADE_LOG, trade_log)

    try:
        add_timeline_event(
            symbol,
            "CLOSED",
            {
                "trade_id": resolved_trade_id,
                "exit_price": round(resolved_exit_price, 4),
                "close_price": round(resolved_exit_price, 4),
                "exit_premium": matched.get("exit_premium") if vehicle == VEHICLE_OPTION else None,
                "reason": reason,
                "pnl": pnl,
                "pnl_basis": pnl_meta.get("pnl_basis"),
                "pnl_pct": pnl_meta.get("pnl_pct"),
                "vehicle_selected": vehicle,
                "vehicle": vehicle,
                "contracts": matched.get("contracts", 0),
                "shares": matched.get("shares", 0),
                "price_review_basis": matched.get("price_review_basis"),
                "monitoring_price_type": matched.get("monitoring_price_type"),
                "underlying_price_used_for_close_decision": matched.get("underlying_price_used_for_close_decision"),
                "underlying_price_used_for_pnl": matched.get("underlying_price_used_for_pnl"),
                "option_underlying_leak_blocked": matched.get("option_underlying_leak_blocked", False),
                "contract_symbol": matched.get("contract_symbol", matched.get("option_symbol")),
                "expiry": matched.get("expiry", matched.get("expiration")),
                "strike": matched.get("strike"),
                "right": matched.get("right"),
                "underlying_price": matched.get("underlying_price"),
                "exit_price_source": exit_source,
                "execution_position_shape": matched.get("execution_position_shape"),
                "performance_classification": matched.get("performance_classification"),
                "performance_include": matched.get("performance_include"),
                "needs_review": matched.get("needs_review"),
                "classification_reason": matched.get("classification_reason"),
            },
        )
    except Exception as exc:
        print(f"[TIMELINE_CLOSE_EVENT:{symbol}] {exc}")

    return {
        "closed": True,
        "blocked": False,
        "symbol": symbol,
        "trade_id": resolved_trade_id,
        "vehicle": vehicle,
        "exit_price": round(resolved_exit_price, 4),
        "close_price": round(resolved_exit_price, 4),
        "exit_premium": matched.get("exit_premium") if vehicle == VEHICLE_OPTION else None,
        "exit_price_source": exit_source,
        "reason": reason,
        "pnl": pnl,
        "pnl_meta": pnl_meta,
        "pnl_basis": pnl_meta.get("pnl_basis"),
        "pnl_pct": pnl_meta.get("pnl_pct"),
        "price_review_basis": matched.get("price_review_basis"),
        "monitoring_price_type": matched.get("monitoring_price_type"),
        "underlying_price_used_for_close_decision": matched.get("underlying_price_used_for_close_decision"),
        "underlying_price_used_for_pnl": matched.get("underlying_price_used_for_pnl"),
        "option_underlying_leak_blocked": bool(leak_blocked),
        "execution_position_shape": matched.get("execution_position_shape"),
        "performance_classification": matched.get("performance_classification"),
        "performance_include": matched.get("performance_include"),
        "include_in_performance": matched.get("include_in_performance"),
        "counts_in_performance": matched.get("counts_in_performance"),
        "needs_review": matched.get("needs_review"),
        "classification_reason": matched.get("classification_reason"),
        "high_option_move": matched.get("high_option_move", False),
        "high_option_move_multiple": matched.get("high_option_move_multiple", 0.0),
        "capital_release": capital_release,
        "capital_release_meta": release_meta,
        "meta": pdt_meta,
        "closed_position": archived,
        "trade_log_row": trade_log_row,
        "exit_explanation": exit_explanation,
    }


def close_trade(symbol: Any, exit_price: Any, reason: str = "manual", trade_id: str = "") -> Dict[str, Any]:
    return close_position(symbol=symbol, exit_price=exit_price, reason=reason, trade_id=trade_id)


def close_open_position(symbol: Any, exit_price: Any, reason: str = "manual", trade_id: str = "") -> Dict[str, Any]:
    return close_position(symbol=symbol, exit_price=exit_price, reason=reason, trade_id=trade_id)


def close_by_trade_id(trade_id: str, exit_price: Any, reason: str = "manual") -> Dict[str, Any]:
    return close_position(symbol="", exit_price=exit_price, reason=reason, trade_id=trade_id)


__all__ = [
    "close_position",
    "close_trade",
    "close_open_position",
    "close_by_trade_id",
]



# OBSERVATORY_CLOSE_TRADE_ACTIVE_BOOK_SYNC_20260520
# ------------------------------------------------------------------------------
# Close-book sync hardener
# ------------------------------------------------------------------------------
# The canonical close_trade path may close and archive correctly while only
# removing the closed trade from the primary open_positions book. The Observatory
# keeps mirrored active books for different surfaces, so a successful close must
# remove the trade from all active open-position books.
#
# This wrapper preserves the original close_trade behavior and then performs a
# safe post-close reconciliation across:
#   - data/open_positions.json
#   - data/positions.json
#   - data/user_positions.json
# ------------------------------------------------------------------------------

def _observatory_sync_closed_trade_across_active_books_20260520(trade_id=None, symbol=None):
    import json
    from pathlib import Path
    from datetime import datetime, timezone

    try:
        root = Path(__file__).resolve().parents[1]
    except Exception:
        root = Path("/content/SimpleeMrkTrade")

    data_dir = root / "data"

    active_books = [
        data_dir / "open_positions.json",
        data_dir / "positions.json",
        data_dir / "user_positions.json",
    ]

    sync_result = {
        "trade_id": trade_id,
        "symbol": symbol,
        "books_checked": [],
        "books_changed": [],
        "removed_total": 0,
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }

    trade_id_s = str(trade_id or "").strip()
    symbol_s = str(symbol or "").strip().upper()

    if not trade_id_s and not symbol_s:
        sync_result["skipped"] = True
        sync_result["reason"] = "missing_trade_id_and_symbol"
        return sync_result

    def _read_json(path, default):
        try:
            if not path.exists():
                return default
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _write_json(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)

    def _extract_rows(payload):
        if isinstance(payload, list):
            return payload, None
        if isinstance(payload, dict):
            for key in ("positions", "open_positions", "data", "items"):
                if isinstance(payload.get(key), list):
                    return payload.get(key), key
        return [], None

    def _rebuild_payload(original, rows, key):
        if isinstance(original, list):
            return rows
        if isinstance(original, dict) and key:
            rebuilt = dict(original)
            rebuilt[key] = rows
            return rebuilt
        return rows

    def _matches(row):
        if not isinstance(row, dict):
            return False

        row_trade_id = str(row.get("trade_id") or row.get("id") or "").strip()
        row_symbol = str(row.get("symbol") or "").strip().upper()
        row_status = str(
            row.get("status")
            or row.get("position_status")
            or row.get("execution_status")
            or row.get("lifecycle_stage")
            or ""
        ).strip().upper()

        # Prefer exact trade_id. Symbol-only is intentionally conservative and
        # only removes obvious controlled/test stale rows if trade_id is missing.
        if trade_id_s and row_trade_id == trade_id_s:
            return True

        if symbol_s and not trade_id_s and row_symbol == symbol_s:
            if row_status in ("CLOSED", "CLOSE", "EXITED"):
                return True
            if str(row.get("test_record") or "").lower() == "true":
                return True
            if str(row.get("controlled_test") or "").lower() == "true":
                return True

        return False

    for path in active_books:
        payload = _read_json(path, [])
        rows, key = _extract_rows(payload)

        before = len(rows)
        kept = [row for row in rows if not _matches(row)]
        removed = before - len(kept)

        book_result = {
            "path": str(path),
            "before": before,
            "after": len(kept),
            "removed": removed,
        }

        sync_result["books_checked"].append(book_result)

        if removed:
            _write_json(path, _rebuild_payload(payload, kept, key))
            sync_result["books_changed"].append(book_result)
            sync_result["removed_total"] += removed

    return sync_result


def _observatory_extract_close_identity_20260520(args=None, kwargs=None, result=None):
    args = args or ()
    kwargs = kwargs or {}
    result = result if isinstance(result, dict) else {}

    trade_id = (
        result.get("trade_id")
        or result.get("id")
        or kwargs.get("trade_id")
        or kwargs.get("position_id")
        or kwargs.get("id")
    )

    symbol = (
        result.get("symbol")
        or kwargs.get("symbol")
    )

    if not trade_id and args:
        first = args[0]
        if isinstance(first, dict):
            trade_id = first.get("trade_id") or first.get("id")
            symbol = symbol or first.get("symbol")
        elif isinstance(first, str):
            trade_id = first

    return trade_id, symbol


def _observatory_close_result_is_success_20260520(result):
    if not isinstance(result, dict):
        return False

    if result.get("closed") is True:
        return True

    status = str(result.get("status") or "").strip().upper()
    if status in ("CLOSED", "FILLED", "SUCCESS"):
        return True

    if result.get("blocked") is True:
        return False

    if result.get("error") or result.get("rejected"):
        return False

    # If a close payload has a closed_at timestamp and trade_id, treat it as closed.
    if result.get("closed_at") and result.get("trade_id"):
        return True

    return False


if "_OBSERVATORY_ORIGINAL_CLOSE_TRADE_20260520" not in globals():
    _OBSERVATORY_ORIGINAL_CLOSE_TRADE_20260520 = close_trade


def close_trade(*args, **kwargs):
    result = _OBSERVATORY_ORIGINAL_CLOSE_TRADE_20260520(*args, **kwargs)

    try:
        if _observatory_close_result_is_success_20260520(result):
            trade_id, symbol = _observatory_extract_close_identity_20260520(
                args=args,
                kwargs=kwargs,
                result=result,
            )

            sync_result = _observatory_sync_closed_trade_across_active_books_20260520(
                trade_id=trade_id,
                symbol=symbol,
            )

            if isinstance(result, dict):
                result["active_book_sync"] = sync_result
                result["active_book_sync_removed_total"] = sync_result.get("removed_total", 0)
                result["active_book_sync_ok"] = sync_result.get("removed_total", 0) >= 0

    except Exception as sync_error:
        if isinstance(result, dict):
            result["active_book_sync_ok"] = False
            result["active_book_sync_error"] = str(sync_error)

    return result



# OBSERVATORY_CLOSE_TRADE_FLEXIBLE_CALL_SHAPE_20260520
# ------------------------------------------------------------------------------
# Flexible close_trade wrapper
# ------------------------------------------------------------------------------
# The original close_trade function expects a narrower call shape, usually:
#   close_trade(symbol, exit_price, ...)
#
# Test harnesses and future callers may send richer forms:
#   close_trade(position_dict)
#   close_trade(trade_id="...", close_price=1.25)
#   close_trade(trade_id="...", exit_price=1.25)
#   close_trade(symbol="...", close_price=1.25)
#
# This wrapper normalizes those shapes BEFORE calling the original close function.
# After a successful close, it sync-removes the trade from all active books.
# ------------------------------------------------------------------------------

def _observatory_read_active_position_for_close_20260520(trade_id=None, symbol=None):
    import json
    from pathlib import Path

    try:
        root = Path(__file__).resolve().parents[1]
    except Exception:
        root = Path("/content/SimpleeMrkTrade")

    data_dir = root / "data"
    active_books = [
        data_dir / "open_positions.json",
        data_dir / "positions.json",
        data_dir / "user_positions.json",
    ]

    trade_id_s = str(trade_id or "").strip()
    symbol_s = str(symbol or "").strip().upper()

    def _read_json(path, default):
        try:
            if not path.exists():
                return default
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _rows(payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ("positions", "open_positions", "data", "items"):
                if isinstance(payload.get(key), list):
                    return payload.get(key)
        return []

    for path in active_books:
        payload = _read_json(path, [])
        for row in _rows(payload):
            if not isinstance(row, dict):
                continue

            row_trade_id = str(row.get("trade_id") or row.get("id") or "").strip()
            row_symbol = str(row.get("symbol") or "").strip().upper()

            if trade_id_s and row_trade_id == trade_id_s:
                return dict(row)

            if symbol_s and row_symbol == symbol_s:
                return dict(row)

    return None


def _observatory_float_first_20260520(*values, default=None):
    for value in values:
        try:
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            number = float(value)
            if number == number:
                return number
        except Exception:
            continue
    return default


def _observatory_get_ci_20260520(row, *keys, default=None):
    if not isinstance(row, dict):
        return default

    # direct first
    for key in keys:
        if key in row:
            return row.get(key)

    # case-insensitive fallback
    lowered = {str(k).lower(): k for k in row.keys()}
    for key in keys:
        lk = str(key).lower()
        if lk in lowered:
            return row.get(lowered[lk])

    return default


def _observatory_normalize_close_call_20260520(args=None, kwargs=None):
    args = list(args or [])
    kwargs = dict(kwargs or {})

    position_obj = None

    if args and isinstance(args[0], dict):
        position_obj = dict(args.pop(0))

    # Pull identity from kwargs first, then position object.
    trade_id = (
        kwargs.get("trade_id")
        or kwargs.get("position_id")
        or kwargs.get("id")
        or _observatory_get_ci_20260520(position_obj, "trade_id", "position_id", "id")
    )

    symbol = (
        kwargs.get("symbol")
        or _observatory_get_ci_20260520(position_obj, "symbol")
    )

    # Map close_price/current premium/etc. to exit_price.
    exit_price = _observatory_float_first_20260520(
        kwargs.get("exit_price"),
        kwargs.get("close_price"),
        kwargs.get("price"),
        kwargs.get("fill_price"),
        kwargs.get("filled_price"),
        kwargs.get("current_premium"),
        kwargs.get("premium_current"),
        kwargs.get("current_option_mark"),
        kwargs.get("option_current_price"),
        _observatory_get_ci_20260520(position_obj, "exit_price"),
        _observatory_get_ci_20260520(position_obj, "close_price"),
        _observatory_get_ci_20260520(position_obj, "current_premium"),
        _observatory_get_ci_20260520(position_obj, "premium_current"),
        _observatory_get_ci_20260520(position_obj, "current_option_mark"),
        _observatory_get_ci_20260520(position_obj, "option_current_price"),
        _observatory_get_ci_20260520(position_obj, "current"),
        _observatory_get_ci_20260520(position_obj, "current_price"),
        default=None,
    )

    # If caller passed trade_id only, find the active row and extract missing info.
    active_row = None
    if (trade_id or symbol) and (not symbol or exit_price is None):
        active_row = _observatory_read_active_position_for_close_20260520(
            trade_id=trade_id,
            symbol=symbol,
        )

    if active_row:
        if not symbol:
            symbol = _observatory_get_ci_20260520(active_row, "symbol")

        if exit_price is None:
            exit_price = _observatory_float_first_20260520(
                _observatory_get_ci_20260520(active_row, "current_premium"),
                _observatory_get_ci_20260520(active_row, "premium_current"),
                _observatory_get_ci_20260520(active_row, "current_option_mark"),
                _observatory_get_ci_20260520(active_row, "option_current_price"),
                _observatory_get_ci_20260520(active_row, "current"),
                _observatory_get_ci_20260520(active_row, "current_price"),
                default=None,
            )

    # Remove names the original function may not accept.
    for bad_key in (
        "close_price",
        "position",
        "position_obj",
        "position_object",
        "current_premium",
        "premium_current",
        "current_option_mark",
        "option_current_price",
    ):
        kwargs.pop(bad_key, None)

    if trade_id is not None:
        kwargs.setdefault("trade_id", trade_id)

    reason = (
        kwargs.get("reason")
        or kwargs.get("close_reason")
        or kwargs.get("exit_reason")
        or _observatory_get_ci_20260520(position_obj, "reason", "close_reason")
        or "manual_close"
    )
    kwargs["reason"] = reason

    return {
        "symbol": symbol,
        "exit_price": exit_price,
        "trade_id": trade_id,
        "kwargs": kwargs,
        "position_obj": position_obj,
        "active_row": active_row,
    }


def _observatory_call_original_close_trade_20260520(original_func, normalized):
    import inspect

    symbol = normalized.get("symbol")
    exit_price = normalized.get("exit_price")
    kwargs = dict(normalized.get("kwargs") or {})

    if not symbol:
        return {
            "closed": False,
            "blocked": False,
            "reason": "missing_symbol_for_close",
            "trade_id": normalized.get("trade_id"),
            "symbol": symbol,
        }

    if exit_price is None:
        return {
            "closed": False,
            "blocked": False,
            "reason": "missing_exit_price_for_close",
            "trade_id": normalized.get("trade_id"),
            "symbol": symbol,
        }

    sig = inspect.signature(original_func)
    params = sig.parameters

    # Keep only kwargs accepted by the original function unless it supports **kwargs.
    accepts_kwargs = any(
        p.kind == inspect.Parameter.VAR_KEYWORD
        for p in params.values()
    )

    if not accepts_kwargs:
        kwargs = {k: v for k, v in kwargs.items() if k in params}

    # Avoid duplicate positional/keyword values.
    kwargs.pop("symbol", None)
    kwargs.pop("exit_price", None)

    # If original accepts trade_id, keep it. If not, it will already be filtered.
    try:
        return original_func(symbol, exit_price, **kwargs)
    except TypeError as first_error:
        # Fallback for functions that use close_price instead of exit_price.
        try:
            fallback_kwargs = dict(kwargs)
            fallback_kwargs["close_price"] = exit_price
            if not accepts_kwargs:
                fallback_kwargs = {
                    k: v for k, v in fallback_kwargs.items() if k in params
                }
            return original_func(symbol, **fallback_kwargs)
        except Exception:
            raise first_error


# Choose the real original, not an already-flexible wrapper.
if "_OBSERVATORY_ORIGINAL_CLOSE_TRADE_FLEXIBLE_20260520" not in globals():
    _OBSERVATORY_ORIGINAL_CLOSE_TRADE_FLEXIBLE_20260520 = globals().get(
        "_OBSERVATORY_ORIGINAL_CLOSE_TRADE_20260520",
        close_trade,
    )


def close_trade(*args, **kwargs):
    normalized = _observatory_normalize_close_call_20260520(args=args, kwargs=kwargs)

    result = _observatory_call_original_close_trade_20260520(
        _OBSERVATORY_ORIGINAL_CLOSE_TRADE_FLEXIBLE_20260520,
        normalized,
    )

    try:
        if _observatory_close_result_is_success_20260520(result):
            trade_id, symbol = _observatory_extract_close_identity_20260520(
                args=args,
                kwargs=kwargs,
                result=result,
            )

            if not trade_id:
                trade_id = normalized.get("trade_id")
            if not symbol:
                symbol = normalized.get("symbol")

            sync_result = _observatory_sync_closed_trade_across_active_books_20260520(
                trade_id=trade_id,
                symbol=symbol,
            )

            if isinstance(result, dict):
                result["active_book_sync"] = sync_result
                result["active_book_sync_removed_total"] = sync_result.get("removed_total", 0)
                result["active_book_sync_ok"] = True

    except Exception as sync_error:
        if isinstance(result, dict):
            result["active_book_sync_ok"] = False
            result["active_book_sync_error"] = str(sync_error)

    return result

# ==============================================================================

# ==============================================================================
# OBSERVATORY_PACK_CLOSE_TRADE_POSITION_STORE_WIRE_001_20260521
# ==============================================================================
# Final active-book cleanup wrapper.
#
# Why this exists:
# close_trade.py can correctly calculate option PnL and write a closed record,
# but older paths may leave a closed/test trade inside one of the active books.
#
# This wrapper preserves the existing close behavior, then uses position_store.py
# to remove the closed trade from every active book.
# ==============================================================================

try:
    from engine.position_store import (
        remove_trade_from_active_books as _observatory_remove_trade_from_active_books_001,
        sync_active_books as _observatory_sync_active_books_001,
        health_report as _observatory_position_store_health_report_001,
    )
except Exception:
    _observatory_remove_trade_from_active_books_001 = None
    _observatory_sync_active_books_001 = None
    _observatory_position_store_health_report_001 = None


def _observatory_close_result_is_closed_001(result):
    if not isinstance(result, dict):
        return False

    if result.get("closed") is True:
        return True

    status = str(
        result.get("status")
        or result.get("position_status")
        or result.get("execution_status")
        or result.get("lifecycle_state")
        or ""
    ).strip().upper()

    return status in {"CLOSED", "EXITED"}


def _observatory_extract_close_identity_001(args, kwargs, result):
    trade_id = ""
    symbol = ""

    if isinstance(result, dict):
        trade_id = str(
            result.get("trade_id")
            or result.get("id")
            or result.get("order_id")
            or ""
        ).strip()

        symbol = str(
            result.get("symbol")
            or result.get("ticker")
            or ""
        ).strip().upper()

    if not trade_id:
        trade_id = str(
            kwargs.get("trade_id")
            or kwargs.get("id")
            or kwargs.get("order_id")
            or ""
        ).strip()

    if not symbol:
        symbol = str(
            kwargs.get("symbol")
            or kwargs.get("ticker")
            or ""
        ).strip().upper()

    # Support close_trade(position_dict, ...)
    if args:
        first = args[0]
        if isinstance(first, dict):
            if not trade_id:
                trade_id = str(
                    first.get("trade_id")
                    or first.get("id")
                    or first.get("order_id")
                    or ""
                ).strip()
            if not symbol:
                symbol = str(
                    first.get("symbol")
                    or first.get("ticker")
                    or ""
                ).strip().upper()
        else:
            # Original close_trade shape is often close_trade(symbol, exit_price, ...)
            if not symbol:
                symbol = str(first or "").strip().upper()

    return trade_id, symbol


def _observatory_after_successful_close_position_store_cleanup_001(args, kwargs, result):
    if not _observatory_close_result_is_closed_001(result):
        return result

    if not isinstance(result, dict):
        return result

    if _observatory_remove_trade_from_active_books_001 is None:
        result["position_store_cleanup"] = {
            "status": "skipped",
            "reason": "position_store_import_failed",
        }
        return result

    trade_id, symbol = _observatory_extract_close_identity_001(args, kwargs, result)

    cleanup = _observatory_remove_trade_from_active_books_001(
        trade_id=trade_id,
        symbol=symbol,
        reason="close_trade_success_cleanup",
        sync_all=True,
    )

    result["position_store_cleanup"] = cleanup
    result["active_books_synced_after_close"] = True
    result["active_book_cleanup_removed"] = cleanup.get("removed", 0)

    if _observatory_sync_active_books_001 is not None:
        try:
            result["position_store_sync_after_close"] = _observatory_sync_active_books_001()
        except Exception as exc:
            result["position_store_sync_after_close"] = {
                "status": "error",
                "error": str(exc),
            }

    if _observatory_position_store_health_report_001 is not None:
        try:
            health = _observatory_position_store_health_report_001()
            result["position_store_health_after_close"] = {
                "status": health.get("status"),
                "books_aligned": health.get("books_aligned"),
                "option_rows_premium_safe": health.get("option_rows_premium_safe"),
                "controlled_or_test_rows_open": health.get("controlled_or_test_rows_open"),
            }
        except Exception as exc:
            result["position_store_health_after_close"] = {
                "status": "error",
                "error": str(exc),
            }

    return result


if callable(globals().get("close_trade")) and not globals().get("_OBSERVATORY_POSITION_STORE_CLOSE_TRADE_WRAPPED_001"):
    _OBSERVATORY_ORIGINAL_CLOSE_TRADE_BEFORE_POSITION_STORE_001 = close_trade

    def close_trade(*args, **kwargs):
        result = _OBSERVATORY_ORIGINAL_CLOSE_TRADE_BEFORE_POSITION_STORE_001(*args, **kwargs)
        return _observatory_after_successful_close_position_store_cleanup_001(args, kwargs, result)

    _OBSERVATORY_POSITION_STORE_CLOSE_TRADE_WRAPPED_001 = True


if callable(globals().get("close_position")) and not globals().get("_OBSERVATORY_POSITION_STORE_CLOSE_POSITION_WRAPPED_001"):
    _OBSERVATORY_ORIGINAL_CLOSE_POSITION_BEFORE_POSITION_STORE_001 = close_position

    def close_position(*args, **kwargs):
        result = _OBSERVATORY_ORIGINAL_CLOSE_POSITION_BEFORE_POSITION_STORE_001(*args, **kwargs)
        return _observatory_after_successful_close_position_store_cleanup_001(args, kwargs, result)

    _OBSERVATORY_POSITION_STORE_CLOSE_POSITION_WRAPPED_001 = True



