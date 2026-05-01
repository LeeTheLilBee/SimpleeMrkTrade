from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from engine.observatory_mode import build_mode_context, normalize_mode


MIN_OPTION_SCORE_DEFAULT = 70
MIN_OPTION_VOLUME_DEFAULT = 200
MIN_OPTION_OPEN_INTEREST_DEFAULT = 500
MAX_SPREAD_PCT_DEFAULT = 0.18


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


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


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _norm_mode(value: Any) -> str:
    return normalize_mode(value)


def _normalize_right(strategy: str) -> str:
    strategy = _safe_str(strategy, "").upper()
    if strategy in {"CALL", "LONG_CALL"}:
        return "CALL"
    if strategy in {"PUT", "LONG_PUT"}:
        return "PUT"
    return strategy


def _extract_dte(contract: Dict[str, Any]) -> int:
    return _safe_int(
        contract.get("dte", contract.get("days_to_expiration", contract.get("daysToExpiration", 999))),
        999,
    )


def _extract_mark(contract: Dict[str, Any]) -> float:
    ask = _safe_float(contract.get("ask", 0.0), 0.0)
    bid = _safe_float(contract.get("bid", 0.0), 0.0)
    mark = _safe_float(contract.get("mark", 0.0), 0.0)
    last = _safe_float(contract.get("last", 0.0), 0.0)
    price = _safe_float(contract.get("price", 0.0), 0.0)

    if ask > 0 and bid > 0 and ask >= bid:
        return round((ask + bid) / 2.0, 4)
    if mark > 0:
        return round(mark, 4)
    if ask > 0:
        return round(ask, 4)
    if last > 0:
        return round(last, 4)
    if price > 0:
        return round(price, 4)
    return 0.0


def _spread_pct(contract: Dict[str, Any]) -> float:
    bid = _safe_float(contract.get("bid", 0.0), 0.0)
    ask = _safe_float(contract.get("ask", 0.0), 0.0)
    if ask <= 0 or bid < 0 or ask < bid:
        return 999.0
    return (ask - bid) / ask if ask > 0 else 999.0


def _preferred_dte_window(trade_intent: str) -> tuple[int, int]:
    intent = _safe_str(trade_intent, "").upper()
    if intent == "EXPLOSIVE":
        return (1, 5)
    if intent == "MOMENTUM":
        return (1, 7)
    if intent == "GRIND":
        return (2, 21)
    return (1, 7)


def _dedupe_keep_order(items: List[Any]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in _safe_list(items):
        text = _safe_str(item, "")
        if text and text not in seen:
            seen.add(text)
            out.append(text)
    return out


def validate_contract_executable(
    contract: Dict[str, Any],
    *,
    min_score: int = MIN_OPTION_SCORE_DEFAULT,
    min_volume: int = MIN_OPTION_VOLUME_DEFAULT,
    min_open_interest: int = MIN_OPTION_OPEN_INTEREST_DEFAULT,
    max_spread_pct: float = MAX_SPREAD_PCT_DEFAULT,
    trading_mode: str = "paper",
    minimum_option_dte: int = 0,
    allow_same_day_high_risk_contracts: bool = False,
) -> tuple[bool, str]:
    contract = _safe_dict(contract)
    if not contract:
        return False, "no_option_contract"

    trading_mode = _norm_mode(trading_mode)

    score = _safe_float(contract.get("contract_score"), 0.0)
    volume = _safe_float(contract.get("volume"), 0.0)
    oi = _safe_float(contract.get("openInterest", contract.get("open_interest")), 0.0)
    ask = _safe_float(contract.get("ask", 0.0), 0.0)
    mark = _safe_float(contract.get("mark", contract.get("last", contract.get("price", 0.0))), 0.0)
    last = _safe_float(contract.get("last", 0.0), 0.0)
    spread_pct = _safe_float(contract.get("spread_pct"), 999.0)
    dte = _safe_int(contract.get("dte", 999), 999)
    intent = _safe_str(contract.get("trade_intent", "GRIND"), "GRIND").upper()

    if score < min_score:
        return False, "contract_score_too_low"
    if volume < min_volume:
        return False, "volume_too_thin"
    if oi < min_open_interest:
        return False, "open_interest_too_thin"
    if spread_pct > max_spread_pct:
        return False, "spread_too_wide"

    if trading_mode == "live":
        if ask <= 0:
            return False, "ask_unavailable"
    else:
        if mark <= 0 and last <= 0:
            return False, "quote_unavailable"

    if dte < minimum_option_dte:
        return False, "option_dte_below_mode_minimum"

    if dte == 0 and not allow_same_day_high_risk_contracts:
        return False, "same_day_expiry_not_allowed"

    if intent == "GRIND" and dte < 2:
        return False, "expiry_too_close_for_grind"
    if intent == "MOMENTUM" and dte < 1:
        return False, "expiry_too_close_for_momentum"
    if intent == "EXPLOSIVE" and dte < 1:
        return False, "expiry_too_close_for_explosive"

    return True, "ok"


def option_is_executable(
    option: Dict[str, Any],
    min_score: int = MIN_OPTION_SCORE_DEFAULT,
    min_volume: int = MIN_OPTION_VOLUME_DEFAULT,
    min_open_interest: int = MIN_OPTION_OPEN_INTEREST_DEFAULT,
    max_spread_pct: float = MAX_SPREAD_PCT_DEFAULT,
    trading_mode: str = "paper",
) -> tuple[bool, str]:
    mode_context = build_mode_context(trading_mode)
    return validate_contract_executable(
        option,
        min_score=min_score,
        min_volume=min_volume,
        min_open_interest=min_open_interest,
        max_spread_pct=max_spread_pct,
        trading_mode=trading_mode,
        minimum_option_dte=_safe_int(mode_context.get("minimum_option_dte"), 0),
        allow_same_day_high_risk_contracts=bool(mode_context.get("allow_same_day_high_risk_contracts", False)),
    )


def score_option_contract(
    contract: Dict[str, Any],
    desired_right: str,
    trade_intent: str = "",
    min_volume: int = MIN_OPTION_VOLUME_DEFAULT,
    min_open_interest: int = MIN_OPTION_OPEN_INTEREST_DEFAULT,
    max_spread_pct: float = MAX_SPREAD_PCT_DEFAULT,
    trading_mode: str = "paper",
) -> Dict[str, Any]:
    contract = deepcopy(_safe_dict(contract))
    notes: List[str] = []
    score = 0
    trading_mode = _norm_mode(trading_mode)
    mode_context = build_mode_context(trading_mode)

    right = _safe_str(contract.get("right", contract.get("option_type", "")), "").upper()
    desired_right = _normalize_right(desired_right)

    if right != desired_right:
        return {
            "contract_score": 0,
            "is_executable": False,
            "execution_reason": "wrong_contract_type",
            "contract_notes": ["Contract type does not match thesis."],
            "mark": 0.0,
            "dte": 999,
            "spread_pct": 999.0,
            "volume": 0,
            "open_interest": 0,
        }

    score += 20
    notes.append(f"Contract type matches {desired_right.lower()} thesis.")

    dte = _extract_dte(contract)
    min_dte, max_dte = _preferred_dte_window(trade_intent)

    if min_dte <= dte <= max_dte:
        score += 25
        notes.append("Expiration aligns with trade intent.")
    elif dte == 0:
        if trading_mode == "survey":
            score += 10
            notes.append("Same-day expiry tolerated in Survey Mode, but still risky.")
        elif trading_mode == "paper":
            score += 8
            notes.append("Same-day expiry allowed in Paper Mode, but still fragile.")
        else:
            notes.append("Same-day expiry is too fragile for standard execution.")
    elif dte < min_dte:
        notes.append("Expiry is too close for this setup.")
    elif dte > max_dte:
        score += 5
        notes.append("Expiry is usable but farther than ideal.")

    volume = _safe_int(contract.get("volume", 0), 0)
    oi = _safe_int(contract.get("open_interest", contract.get("openInterest", 0)), 0)

    if volume >= min_volume * 5:
        score += 20
        notes.append("Exceptional contract volume.")
    elif volume >= min_volume:
        score += 12
        notes.append("Good contract volume.")
    elif volume > 0:
        score += 4
        notes.append("Thin contract volume.")
    else:
        notes.append("No contract volume.")

    if oi >= min_open_interest * 5:
        score += 20
        notes.append("Exceptional open interest.")
    elif oi >= min_open_interest:
        score += 12
        notes.append("Good open interest.")
    elif oi > 0:
        score += 4
        notes.append("Usable open interest.")
    else:
        notes.append("No open interest.")

    bid = _safe_float(contract.get("bid", 0.0), 0.0)
    ask = _safe_float(contract.get("ask", 0.0), 0.0)
    spread_pct = _spread_pct(contract)

    if bid > 0 and ask > 0 and ask >= bid:
        if spread_pct <= max_spread_pct / 2:
            score += 15
            notes.append("Tight spread.")
        elif spread_pct <= max_spread_pct:
            score += 8
            notes.append("Acceptable spread.")
        else:
            notes.append("Wide spread reduces execution quality.")
    else:
        if trading_mode in {"paper", "survey"}:
            score += 5
            notes.append("Bid/ask unavailable, using simulated quote fallback.")
        else:
            notes.append("Bid/ask unavailable.")

    premium = _extract_mark(contract)
    if 0.2 <= premium <= 6.0:
        score += 10
        notes.append("Premium in preferred range.")
    elif 0.05 <= premium <= 12.0:
        score += 5
        notes.append("Premium is usable.")
    else:
        notes.append("Premium is less efficient.")

    option_payload = {
        **contract,
        "contract_score": int(round(score)),
        "volume": volume,
        "open_interest": oi,
        "spread_pct": spread_pct,
        "dte": dte,
        "mark": premium,
        "trade_intent": trade_intent,
    }

    is_exec, exec_reason = validate_contract_executable(
        option_payload,
        min_score=MIN_OPTION_SCORE_DEFAULT,
        min_volume=min_volume,
        min_open_interest=min_open_interest,
        max_spread_pct=max_spread_pct,
        trading_mode=trading_mode,
        minimum_option_dte=_safe_int(mode_context.get("minimum_option_dte"), 0),
        allow_same_day_high_risk_contracts=bool(mode_context.get("allow_same_day_high_risk_contracts", False)),
    )

    return {
        "contract_score": int(round(score)),
        "is_executable": is_exec,
        "execution_reason": exec_reason,
        "contract_notes": notes,
        "mark": premium,
        "dte": dte,
        "spread_pct": spread_pct,
        "volume": volume,
        "open_interest": oi,
    }


def choose_best_option_contract(
    option_chain: List[Dict[str, Any]],
    strategy: str,
    trade_intent: str = "",
    min_option_score: int = MIN_OPTION_SCORE_DEFAULT,
    min_volume: int = MIN_OPTION_VOLUME_DEFAULT,
    min_open_interest: int = MIN_OPTION_OPEN_INTEREST_DEFAULT,
    max_spread_pct: float = MAX_SPREAD_PCT_DEFAULT,
    trading_mode: str = "paper",
) -> Dict[str, Any]:
    desired_right = _normalize_right(strategy)
    trading_mode = _norm_mode(trading_mode)

    best_contract: Optional[Dict[str, Any]] = None
    ranked_contracts: List[Dict[str, Any]] = []

    for raw_contract in option_chain or []:
        contract = deepcopy(_safe_dict(raw_contract))
        meta = score_option_contract(
            contract=contract,
            desired_right=desired_right,
            trade_intent=trade_intent,
            min_volume=min_volume,
            min_open_interest=min_open_interest,
            max_spread_pct=max_spread_pct,
            trading_mode=trading_mode,
        )
        contract.update(meta)
        ranked_contracts.append(contract)

        if best_contract is None:
            best_contract = contract
            continue

        current_score = _safe_int(contract.get("contract_score", 0), 0)
        best_score = _safe_int(best_contract.get("contract_score", 0), 0)

        if current_score > best_score:
            best_contract = contract
            continue

        if current_score == best_score:
            current_exec = bool(contract.get("is_executable", False))
            best_exec = bool(best_contract.get("is_executable", False))
            if current_exec and not best_exec:
                best_contract = contract
                continue

            current_dte = _extract_dte(contract)
            best_dte = _extract_dte(best_contract)
            if current_dte < best_dte:
                best_contract = contract
                continue

            if current_dte == best_dte:
                current_mark = _extract_mark(contract)
                best_mark = _extract_mark(best_contract)
                if 0 < current_mark < best_mark or best_mark <= 0:
                    best_contract = contract

    ranked_contracts.sort(
        key=lambda c: (
            _safe_int(c.get("contract_score", 0), 0),
            1 if c.get("is_executable") else 0,
            -_extract_dte(c),
        ),
        reverse=True,
    )

    if best_contract is None:
        return {
            "best_option_found": False,
            "option_allowed": False,
            "option_reason": "no_option_chain",
            "option_score": 0,
            "best_option_preview": {},
            "option_notes": ["No option chain available."],
            "top_ranked_contracts": [],
        }

    best_score = _safe_int(best_contract.get("contract_score", 0), 0)
    is_executable = bool(best_contract.get("is_executable", False))
    exec_reason = _safe_str(best_contract.get("execution_reason", "not_executable"), "not_executable")

    if not is_executable:
        option_allowed = False
        option_reason = exec_reason
    elif best_score < min_option_score:
        option_allowed = False
        option_reason = "contract_score_too_low"
    else:
        option_allowed = True
        option_reason = "allowed"

    return {
        "best_option_found": True,
        "option_allowed": option_allowed,
        "option_reason": option_reason,
        "option_score": best_score,
        "best_option_preview": best_contract,
        "option_notes": best_contract.get("contract_notes", []),
        "top_ranked_contracts": ranked_contracts[:5],
    }


def choose_vehicle(
    symbol: str,
    strategy: str,
    trade_intent: str,
    option_chain: List[Dict[str, Any]],
    stock_price: float,
    available_capital: float,
    stock_allowed: bool = True,
    min_option_score: int = MIN_OPTION_SCORE_DEFAULT,
    trading_mode: str = "paper",
) -> Dict[str, Any]:
    trading_mode = _norm_mode(trading_mode)
    mode_context = build_mode_context(trading_mode)

    option_result = choose_best_option_contract(
        option_chain=option_chain,
        strategy=strategy,
        trade_intent=trade_intent,
        min_option_score=min_option_score,
        trading_mode=trading_mode,
    )

    stock_price = _safe_float(stock_price, 0.0)
    available_capital = _safe_float(available_capital, 0.0)

    reserve_floor_pct = _safe_float(mode_context.get("reserve_floor_pct"), 0.0)
    reserve_floor_dollars = round(available_capital * reserve_floor_pct, 2) if reserve_floor_pct > 0 else 0.0

    stock_capital_required = round(stock_price, 4) if stock_price > 0 else 0.0
    stock_total_cost = round(stock_capital_required + 1.0, 4) if stock_capital_required > 0 else 0.0
    stock_cash_after_trade = round(available_capital - stock_total_cost, 4) if stock_total_cost > 0 else available_capital
    stock_reserve_ok = stock_cash_after_trade >= reserve_floor_dollars

    option_preview = option_result.get("best_option_preview", {}) or {}
    option_mark = _extract_mark(option_preview)
    option_capital_required = round(option_mark * 100, 4) if option_mark > 0 else 0.0
    option_total_cost = round(option_capital_required + 1.0, 4) if option_capital_required > 0 else 0.0
    option_cash_after_trade = round(available_capital - option_total_cost, 4) if option_total_cost > 0 else available_capital
    option_reserve_ok = option_cash_after_trade >= reserve_floor_dollars

    option_affordable = option_total_cost > 0 and option_total_cost <= available_capital
    stock_affordable = stock_total_cost > 0 and stock_total_cost <= available_capital

    option_reason = _safe_str(option_result.get("option_reason", "unknown"), "unknown")
    best_option_found = bool(option_result.get("best_option_found", False))
    option_allowed = bool(option_result.get("option_allowed", False))

    diagnostics = {
        "trading_mode": trading_mode,
        "mode_context": mode_context,
        "stock_allowed": bool(stock_allowed),
        "stock_price": round(stock_price, 4),
        "stock_capital_required": stock_capital_required,
        "stock_total_cost": stock_total_cost,
        "stock_affordable": stock_affordable,
        "stock_cash_after_trade": stock_cash_after_trade,
        "stock_reserve_ok_after_trade": stock_reserve_ok,
        "option_capital_required": option_capital_required,
        "option_total_cost": option_total_cost,
        "option_affordable": option_affordable,
        "option_cash_after_trade": option_cash_after_trade,
        "option_reserve_ok_after_trade": option_reserve_ok,
        "option_allowed": option_allowed,
        "option_reason": option_reason,
        "best_option_found": best_option_found,
        "option_score": _safe_int(option_result.get("option_score", 0), 0),
        "reserve_floor_dollars": reserve_floor_dollars,
    }

    option_path = {
        "vehicle": "OPTION",
        "capital_required": option_capital_required,
        "minimum_trade_cost": option_total_cost,
        "contracts": 1 if option_capital_required > 0 else 0,
        "shares": 0,
        "affordable": option_affordable,
        "score": _safe_int(option_result.get("option_score", 0), 0),
        "dte": _extract_dte(option_preview) if option_preview else 999,
        "spread_pct": _safe_float(option_preview.get("spread_pct"), 999.0) if option_preview else 999.0,
        "cash_after_trade": option_cash_after_trade,
        "reserve_floor_dollars": reserve_floor_dollars,
        "reserve_ok_after_trade": option_reserve_ok,
    }

    stock_path = {
        "vehicle": "STOCK",
        "capital_required": stock_capital_required,
        "minimum_trade_cost": stock_total_cost,
        "contracts": 0,
        "shares": 1 if stock_capital_required > 0 else 0,
        "affordable": stock_affordable,
        "cash_after_trade": stock_cash_after_trade,
        "reserve_floor_dollars": reserve_floor_dollars,
        "reserve_ok_after_trade": stock_reserve_ok,
    }

    if option_allowed and option_affordable:
        return {
            "symbol": symbol,
            "vehicle_selected": "OPTION",
            "has_option": True,
            "capital_required": option_capital_required,
            "minimum_trade_cost": option_total_cost,
            "price": stock_price,
            "shares": 0,
            "contracts": 1,
            "option_result": option_result,
            "option_path": option_path,
            "stock_path": stock_path,
            "vehicle_reason": "clean_option_contract_found",
            "vehicle_diagnostics": diagnostics,
            "top_ranked_contracts": option_result.get("top_ranked_contracts", []),
        }

    if stock_allowed and stock_affordable:
        if best_option_found:
            vehicle_reason = f"stock_fallback_after_option_failure:{option_reason}"
        else:
            vehicle_reason = "stock_only_path_available"

        return {
            "symbol": symbol,
            "vehicle_selected": "STOCK",
            "has_option": best_option_found,
            "capital_required": stock_capital_required,
            "minimum_trade_cost": stock_total_cost,
            "price": stock_price,
            "shares": 1,
            "contracts": 0,
            "option_result": option_result,
            "option_path": option_path,
            "stock_path": stock_path,
            "vehicle_reason": vehicle_reason,
            "vehicle_diagnostics": diagnostics,
            "top_ranked_contracts": option_result.get("top_ranked_contracts", []),
        }

    if best_option_found:
        final_reason = f"option_failed:{option_reason}"
    elif stock_allowed and stock_total_cost > 0 and stock_total_cost > available_capital:
        final_reason = "stock_not_affordable"
    else:
        final_reason = "no_viable_vehicle"

    return {
        "symbol": symbol,
        "vehicle_selected": "RESEARCH_ONLY",
        "has_option": best_option_found,
        "capital_required": 0.0,
        "minimum_trade_cost": 0.0,
        "price": stock_price,
        "shares": 0,
        "contracts": 0,
        "option_result": option_result,
        "option_path": option_path,
        "stock_path": stock_path,
        "vehicle_reason": final_reason,
        "vehicle_diagnostics": diagnostics,
        "top_ranked_contracts": option_result.get("top_ranked_contracts", []),
    }


__all__ = [
    "MIN_OPTION_SCORE_DEFAULT",
    "MIN_OPTION_VOLUME_DEFAULT",
    "MIN_OPTION_OPEN_INTEREST_DEFAULT",
    "MAX_SPREAD_PCT_DEFAULT",
    "validate_contract_executable",
    "option_is_executable",
    "score_option_contract",
    "choose_best_option_contract",
    "choose_vehicle",
]
