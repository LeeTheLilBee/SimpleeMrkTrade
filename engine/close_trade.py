from __future__ import annotations

import json
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from engine.trade_timeline import add_timeline_event
from engine.pdt_guard import can_close_position
from engine.account_state import release_trade_cap
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
        if value is None:
            return float(default)
        if isinstance(value, bool):
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
        if value is None:
            return None
        if isinstance(value, bool):
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
        if value is None:
            return int(default)
        if isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            value = value.replace(",", "").strip()
            if value == "":
                return int(default)
        return int(float(value))
    except Exception:
        return int(default)


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


def _round4(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 4)


def _round_money(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 2)


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

    if option or contract or contract_symbol or right in {"CALL", "PUT", "C", "P"}:
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
    option = _safe_dict(position.get("option"))
    contract = _safe_dict(position.get("contract"))

    merged: Dict[str, Any] = {}
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

        return round(pnl, 2), {
            "pnl_valid": True,
            "pnl_basis": "option_premium_x_100",
            "entry_premium": round(entry_premium, 4),
            "exit_premium": round(exit_premium, 4),
            "contracts": contracts,
            "multiplier": OPTION_CONTRACT_MULTIPLIER,
            "pnl_pct": round(pnl_pct, 4),
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

        # Keep release_trade_cap compatible: entry_price * size + pnl.
        # For options, entry_price must be premium * 100.
        release_basis_entry = entry_premium * OPTION_CONTRACT_MULTIPLIER

        return release_basis_entry, contracts, {
            "capital_release_basis": "option_entry_premium_x_100_x_contracts",
            "entry_premium": round(entry_premium, 4),
            "exit_premium": round(exit_premium, 4),
            "contracts": contracts,
            "multiplier": OPTION_CONTRACT_MULTIPLIER,
            "release_basis_entry": round(release_basis_entry, 4),
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
            f"PnL: {pnl}",
            f"PnL %: {pnl_pct}",
            f"Exit price: {exit_price}",
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

    if _upper(cleaned.get("symbol"), "UNKNOWN") in {"", "UNKNOWN", "NONE"}:
        cleaned["symbol"] = symbol
    else:
        cleaned["symbol"] = _upper(cleaned.get("symbol"), symbol)

    cleaned["vehicle"] = _upper(cleaned.get("vehicle"), vehicle) or vehicle

    for key, value in fallback.items():
        if key not in cleaned or cleaned.get(key) in [None, "", [], {}]:
            cleaned[key] = value

    return cleaned


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

    matched["closed_at"] = closed_at
    matched["exit_time"] = closed_at
    matched["exited_at"] = closed_at

    matched["reason"] = reason
    matched["close_reason"] = reason
    matched["exit_price"] = round(exit_price, 4)
    matched["close_price"] = round(exit_price, 4)

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
        entry_premium = pnl_meta.get("entry_premium", _option_entry_premium(matched))
        contracts = pnl_meta.get("contracts", _option_contracts(matched))

        matched["entry"] = round(_safe_float(entry_premium, 0.0), 4)
        matched["entry_price"] = round(_safe_float(entry_premium, 0.0), 4)
        matched["entry_premium"] = round(_safe_float(entry_premium, 0.0), 4)
        matched["premium_entry"] = matched["entry_premium"]
        matched["option_entry"] = matched["entry_premium"]
        matched["option_entry_price"] = matched["entry_premium"]

        matched["exit_premium"] = round(exit_price, 4)
        matched["current_premium"] = round(exit_price, 4)
        matched["premium_current"] = round(exit_price, 4)
        matched["current_option_mark"] = round(exit_price, 4)
        matched["option_current_mark"] = round(exit_price, 4)
        matched["option_current_price"] = round(exit_price, 4)
        matched["current_option_price"] = round(exit_price, 4)
        matched["current_price"] = round(exit_price, 4)
        matched["current"] = round(exit_price, 4)

        matched["contracts"] = _safe_int(contracts, 1)
        matched["contract_count"] = _safe_int(contracts, 1)
        matched["quantity"] = _safe_int(contracts, 1)
        matched["qty"] = _safe_int(contracts, 1)
        matched["size"] = _safe_int(contracts, 1)
        matched["shares"] = 0

        if underlying is not None and underlying > 0:
            matched["underlying_price"] = round(underlying, 4)
            matched["current_underlying_price"] = round(underlying, 4)

        matched["price_review_basis"] = "OPTION_PREMIUM_ONLY"
        matched["monitoring_price_type"] = "OPTION_PREMIUM"
        matched["monitoring_mode"] = "OPTION_PREMIUM"
        matched["price_basis"] = "OPTION_PREMIUM"
        matched["underlying_price_used_for_close_decision"] = False
        matched["option_underlying_leak_blocked"] = bool(leak_blocked)
        matched["option_underlying_leak_blocked_on_close"] = bool(leak_blocked)
        matched["execution_position_shape"] = "OPTION_PREMIUM_POSITION"

        if contract.get("contract_symbol"):
            matched["contract_symbol"] = contract.get("contract_symbol")
            matched["option_symbol"] = contract.get("contract_symbol")
            matched["option_contract_symbol"] = contract.get("contract_symbol")
            matched["contractSymbol"] = contract.get("contract_symbol")
        if contract.get("expiry"):
            matched["expiry"] = contract.get("expiry")
            matched["expiration"] = contract.get("expiry")
            matched["expiration_date"] = contract.get("expiry")
        if contract.get("strike") is not None:
            matched["strike"] = contract.get("strike")
            matched["strike_price"] = contract.get("strike")
        if contract.get("right"):
            matched["right"] = contract.get("right")
            matched["option_type"] = contract.get("right")
            matched["call_put"] = contract.get("right")

    elif vehicle == VEHICLE_STOCK:
        matched["price_review_basis"] = "STOCK_PRICE"
        matched["monitoring_price_type"] = "UNDERLYING"
        matched["monitoring_mode"] = "UNDERLYING"
        matched["price_basis"] = "STOCK_PRICE"
        matched["underlying_price_used_for_close_decision"] = True
        matched["current_price"] = round(exit_price, 4)
        matched["current"] = round(exit_price, 4)
        matched["underlying_price"] = round(exit_price, 4)
        matched["current_underlying_price"] = round(exit_price, 4)
        matched["contracts"] = 0
        matched["contract_count"] = 0
        matched["execution_position_shape"] = "STOCK_UNDERLYING_POSITION"

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
        "option_underlying_leak_blocked": bool(leak_blocked),
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
        "execution_position_shape": matched.get("execution_position_shape"),
    }

    if vehicle == VEHICLE_OPTION:
        row.update(
            {
                "entry": matched.get("entry_premium", matched.get("entry")),
                "entry_price": matched.get("entry_premium", matched.get("entry_price")),
                "entry_premium": matched.get("entry_premium"),
                "exit_premium": round(exit_price, 4),
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

    updated_trade: Optional[Dict[str, Any]] = None

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
        trade["action"] = trade.get("action", "OPEN")
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
        trade["execution_position_shape"] = matched.get("execution_position_shape")

        if vehicle == VEHICLE_OPTION:
            trade["exit_premium"] = round(exit_price, 4)
            trade["current_premium"] = round(exit_price, 4)
            trade["current_option_mark"] = round(exit_price, 4)
            trade["entry_premium"] = pnl_meta.get("entry_premium")
            trade["contracts"] = pnl_meta.get("contracts")
            trade["shares"] = 0
            trade["contract_symbol"] = matched.get("contract_symbol", matched.get("option_symbol"))
            trade["option_symbol"] = matched.get("contract_symbol", matched.get("option_symbol"))
            trade["expiry"] = matched.get("expiry", matched.get("expiration"))
            trade["expiration"] = matched.get("expiration", matched.get("expiry"))
            trade["strike"] = matched.get("strike")
            trade["right"] = matched.get("right")
            trade["option_underlying_leak_blocked"] = matched.get("option_underlying_leak_blocked")

        updated_trade = trade
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

    # Always append a distinct CLOSE row so verification does not come back None.
    trade_log.append(close_row)

    return close_row if close_row else (updated_trade or {})


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

    if vehicle == VEHICLE_RESEARCH_ONLY:
        return {
            "closed": False,
            "blocked": True,
            "reason": "research_only_position_cannot_be_closed",
            "symbol": symbol,
            "trade_id": matched.get("trade_id", trade_id),
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
            "trade_id": matched.get("trade_id", trade_id),
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
                "trade_id": matched.get("trade_id", trade_id),
                "vehicle": vehicle,
                "requested_exit_price": exit_price,
                "price_review_basis": "OPTION_PREMIUM_ONLY",
                "underlying_price_used_for_close_decision": False,
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
                "trade_id": matched.get("trade_id", trade_id),
                "vehicle": vehicle,
                "requested_exit_price": exit_price,
                "price_review_basis": "STOCK_PRICE",
                "underlying_price_used_for_close_decision": True,
            }

    pnl, pnl_meta = _compute_pnl(matched, resolved_exit_price)
    closed_at = _now_iso()

    matched_for_explanation = dict(matched)
    matched_for_explanation["symbol"] = symbol
    matched_for_explanation["vehicle"] = vehicle
    matched_for_explanation["vehicle_selected"] = vehicle
    matched_for_explanation["selected_vehicle"] = vehicle
    matched_for_explanation["pnl"] = pnl
    matched_for_explanation["realized_pnl"] = pnl
    matched_for_explanation["exit_price"] = resolved_exit_price

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
        capital_release = release_trade_cap(
            entry_price=release_price_basis,
            size=release_size,
            pnl=pnl,
            immediate=True,
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
                "trade_id": matched.get("trade_id"),
                "exit_price": round(resolved_exit_price, 4),
                "close_price": round(resolved_exit_price, 4),
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
                "option_underlying_leak_blocked": matched.get("option_underlying_leak_blocked", False),
                "contract_symbol": matched.get("contract_symbol", matched.get("option_symbol")),
                "expiry": matched.get("expiry", matched.get("expiration")),
                "strike": matched.get("strike"),
                "right": matched.get("right"),
                "underlying_price": matched.get("underlying_price"),
                "exit_price_source": exit_source,
                "execution_position_shape": matched.get("execution_position_shape"),
            },
        )
    except Exception as e:
        print(f"[TIMELINE_CLOSE_EVENT:{symbol}] {e}")

    return {
        "closed": True,
        "blocked": False,
        "symbol": symbol,
        "trade_id": matched.get("trade_id", ""),
        "vehicle": vehicle,
        "exit_price": round(resolved_exit_price, 4),
        "close_price": round(resolved_exit_price, 4),
        "exit_price_source": exit_source,
        "reason": reason,
        "pnl": pnl,
        "pnl_meta": pnl_meta,
        "pnl_basis": pnl_meta.get("pnl_basis"),
        "pnl_pct": pnl_meta.get("pnl_pct"),
        "price_review_basis": matched.get("price_review_basis"),
        "monitoring_price_type": matched.get("monitoring_price_type"),
        "underlying_price_used_for_close_decision": matched.get("underlying_price_used_for_close_decision"),
        "option_underlying_leak_blocked": bool(leak_blocked),
        "execution_position_shape": matched.get("execution_position_shape"),
        "capital_release": capital_release,
        "capital_release_meta": release_meta,
        "meta": pdt_meta,
        "closed_position": archived,
        "trade_log_row": trade_log_row,
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
