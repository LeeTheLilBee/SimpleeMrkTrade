from __future__ import annotations

from datetime import datetime
from math import fabs
from typing import Any, Dict, List, Optional, Tuple


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return float(default)
        return float(v)
    except Exception:
        return float(default)


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        if v is None or v == "":
            return int(default)
        return int(float(v))
    except Exception:
        return int(default)


def _safe_str(v: Any, default: str = "") -> str:
    try:
        text = str(v).strip()
        return text if text else default
    except Exception:
        return default


def _safe_dict(v: Any) -> Dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _normalize_option_type(value: Any) -> str:
    text = _safe_str(value, "").upper()
    if text in {"CALL", "C"}:
        return "CALL"
    if text in {"PUT", "P"}:
        return "PUT"
    return ""


def _extract_option_type(option: Dict[str, Any]) -> str:
    option = _safe_dict(option)

    for key in ("type", "right", "option_type", "side"):
        normalized = _normalize_option_type(option.get(key))
        if normalized:
            return normalized

    contract_symbol = _safe_str(option.get("contractSymbol", ""), "")
    if not contract_symbol:
        return ""

    # Standard OCC style has ...C........ or ...P........ near the suffix.
    # We only trust explicit C/P in the expected position zone.
    tail = contract_symbol[-15:]
    if len(tail) >= 9:
        cp_flag = tail[0]
        if cp_flag == "C":
            return "CALL"
        if cp_flag == "P":
            return "PUT"

    return ""


def _parse_expiry(expiry: Any) -> Optional[datetime]:
    raw = _safe_str(expiry, "")
    if not raw:
        return None

    try:
        return datetime.fromisoformat(raw)
    except Exception:
        pass

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(raw, fmt)
        except Exception:
            continue

    return None


def _days_to_expiry(expiry: Any) -> int:
    exp = _parse_expiry(expiry)
    if not exp:
        return 0

    now = datetime.now()
    return max(0, int((exp.date() - now.date()).days))


def determine_trade_intent(trade: Dict[str, Any]) -> str:
    trade = _safe_dict(trade)

    score = _safe_float(trade.get("score", trade.get("fused_score", 0.0)), 0.0)
    atr = _safe_float(trade.get("atr", 0.0), 0.0)
    setup_family = _safe_str(trade.get("setup_family", ""), "").lower()
    entry_quality = _safe_str(trade.get("entry_quality", ""), "").lower()

    if score >= 200:
        return "EXPLOSIVE"
    if score >= 170:
        return "MOMENTUM"
    if atr >= 5:
        return "MOMENTUM"
    if setup_family in {"breakout", "trend_acceleration"}:
        return "MOMENTUM"
    if entry_quality in {"high_conviction", "aggressive"}:
        return "MOMENTUM"
    return "GRIND"


def _build_option_metrics(option: Dict[str, Any], stock_price: float) -> Dict[str, Any]:
    option = _safe_dict(option)

    strike = _safe_float(option.get("strike"), 0.0)
    volume = _safe_float(option.get("volume"), 0.0)
    oi = _safe_float(option.get("openInterest", option.get("open_interest")), 0.0)

    bid = _safe_float(option.get("bid"), 0.0)
    ask = _safe_float(option.get("ask"), 0.0)
    last = _safe_float(option.get("last"), 0.0)
    mark = _safe_float(option.get("mark"), 0.0)

    if ask <= 0 and mark > 0:
        ask = mark
    if bid <= 0 and last > 0:
        bid = last
    if mark <= 0 and bid > 0 and ask > 0:
        mark = (bid + ask) / 2.0
    if mark <= 0 and last > 0:
        mark = last

    spread = abs(ask - bid) if (bid > 0 or ask > 0) else _safe_float(option.get("bidAskSpread"), 0.0)
    spread_pct = (spread / ask) if ask > 0 and spread > 0 else 0.0

    distance_pct = 0.0
    if stock_price > 0 and strike > 0:
        distance_pct = fabs(strike - stock_price) / stock_price

    expiry = option.get("expiry", option.get("expiration"))
    dte = _days_to_expiry(expiry)

    return {
        "strike": strike,
        "volume": volume,
        "oi": oi,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "spread": spread,
        "spread_pct": spread_pct,
        "distance_pct": distance_pct,
        "dte": dte,
        "expiry": expiry,
    }


def contract_quality_score(
    option: Dict[str, Any],
    stock_price: float,
    strategy: str,
    trade: Optional[Dict[str, Any]] = None,
) -> Tuple[int, List[str]]:
    option = _safe_dict(option)
    trade = _safe_dict(trade)

    metrics = _build_option_metrics(option, stock_price)
    option_type = _extract_option_type(option)
    normalized_strategy = _normalize_option_type(strategy)
    intent = determine_trade_intent(trade)

    strike = metrics["strike"]
    volume = metrics["volume"]
    oi = metrics["oi"]
    ask = metrics["ask"]
    spread = metrics["spread"]
    spread_pct = metrics["spread_pct"]
    distance_pct = metrics["distance_pct"]
    dte = metrics["dte"]
    mark = metrics["mark"]

    score = 0
    notes: List[str] = []

    if normalized_strategy == option_type and option_type:
        score += 20
        notes.append(f"Contract type matches {normalized_strategy.lower()} thesis.")
    else:
        notes.append(
            f"Contract type mismatch: thesis={normalized_strategy or 'UNKNOWN'} contract={option_type or 'UNKNOWN'}."
        )
        option["trade_intent"] = intent
        option["dte"] = dte
        option["bidAskSpread"] = round(spread, 4)
        option["spread_pct"] = round(spread_pct, 4)
        option["mark"] = round(mark, 4)
        option["distance_pct"] = round(distance_pct, 4)
        option["monitoring_mode"] = "OPTION_PREMIUM"
        option["price_reference"] = round(mark if mark > 0 else ask, 4)
        return 0, notes

    if intent == "EXPLOSIVE":
        if 2 <= dte <= 7:
            score += 28
            notes.append("Short-dated expiry fits explosive move.")
        elif 8 <= dte <= 14:
            score += 14
            notes.append("Expiry is usable but slightly slower than ideal for explosive setup.")
        elif dte == 1:
            score += 6
            notes.append("Near-expiry contract is aggressive for explosive setup.")
        elif dte == 0:
            score -= 18
            notes.append("Same-day expiry is fragile for explosive execution.")
        else:
            score -= 3
            notes.append("Expiry is not ideal for explosive setup.")
    elif intent == "MOMENTUM":
        if 5 <= dte <= 21:
            score += 26
            notes.append("Expiry aligns with momentum window.")
        elif 2 <= dte <= 4:
            score += 10
            notes.append("Expiry is a little tight for momentum.")
        elif 22 <= dte <= 35:
            score += 10
            notes.append("Expiry is workable for momentum.")
        elif dte == 1:
            score -= 8
            notes.append("Next-day expiry is still tight for momentum.")
        elif dte == 0:
            score -= 30
            notes.append("Same-day expiry is not suitable for momentum execution.")
        else:
            notes.append("Expiry is usable but not ideal for momentum.")
    else:
        if 10 <= dte <= 45:
            score += 28
            notes.append("Longer expiry supports slower grind setup.")
        elif 5 <= dte <= 9:
            score += 12
            notes.append("Expiry is a bit tight for grind setup.")
        elif 46 <= dte <= 75:
            score += 5
            notes.append("Long-dated expiry is safe but less efficient.")
        elif 2 <= dte <= 4:
            score -= 8
            notes.append("Expiry is too tight for grind setup.")
        elif dte == 1:
            score -= 22
            notes.append("Next-day expiry is too fragile for grind setup.")
        elif dte == 0:
            score -= 40
            notes.append("Same-day expiry is not suitable for grind setup.")
        else:
            score -= 2
            notes.append("Expiry is not ideal for grind setup.")

    if volume >= 20000:
        score += 30
        notes.append("Exceptional contract volume.")
    elif volume >= 5000:
        score += 24
        notes.append("Strong contract volume.")
    elif volume >= 1000:
        score += 18
        notes.append("Good contract volume.")
    elif volume >= 250:
        score += 10
        notes.append("Usable contract volume.")
    elif volume >= 50:
        score += 4
        notes.append("Thin contract volume.")
    else:
        score -= 12
        notes.append("Very weak contract volume.")

    if oi >= 20000:
        score += 30
        notes.append("Exceptional open interest.")
    elif oi >= 5000:
        score += 24
        notes.append("Strong open interest.")
    elif oi >= 1000:
        score += 18
        notes.append("Good open interest.")
    elif oi >= 250:
        score += 10
        notes.append("Usable open interest.")
    elif oi >= 50:
        score += 4
        notes.append("Thin open interest.")
    else:
        score -= 12
        notes.append("Very weak open interest.")

    if ask <= 0:
        score -= 18
        notes.append("Ask unavailable.")
    elif spread <= 0:
        score += 6
        notes.append("Spread unavailable but not penalized heavily.")
    elif spread_pct <= 0.01:
        score += 24
        notes.append("Extremely tight spread.")
    elif spread_pct <= 0.03:
        score += 20
        notes.append("Very tight spread.")
    elif spread_pct <= 0.06:
        score += 12
        notes.append("Tight spread.")
    elif spread_pct <= 0.10:
        score += 4
        notes.append("Acceptable spread.")
    elif spread_pct <= 0.15:
        score -= 4
        notes.append("Wide spread reduces execution quality.")
    else:
        score -= 16
        notes.append("Very wide spread reduces execution quality.")

    if stock_price > 0 and strike > 0:
        if intent == "EXPLOSIVE":
            if distance_pct <= 0.01:
                score += 22
                notes.append("Tight strike for explosive move.")
            elif distance_pct <= 0.03:
                score += 14
                notes.append("Reasonable strike for explosive move.")
            elif distance_pct <= 0.05:
                score += 5
                notes.append("Slightly wide for explosive move.")
            else:
                score -= 8
                notes.append("Too far from price for explosive setup.")
        elif intent == "MOMENTUM":
            if distance_pct <= 0.02:
                score += 20
                notes.append("Well-positioned strike for momentum.")
            elif distance_pct <= 0.05:
                score += 12
                notes.append("Acceptable strike for momentum.")
            elif distance_pct <= 0.08:
                score += 4
                notes.append("Wide but usable strike for momentum.")
            else:
                score -= 5
                notes.append("Wide strike reduces efficiency.")
        else:
            if distance_pct <= 0.03:
                score += 20
                notes.append("Strike supports slower grind setup.")
            elif distance_pct <= 0.06:
                score += 10
                notes.append("Strike is workable for grind setup.")
            elif distance_pct <= 0.10:
                score += 2
                notes.append("Far strike reduces probability of payoff.")
            else:
                score -= 6
                notes.append("Strike is too far for grind setup.")

    if ask <= 0:
        notes.append("Premium unavailable.")
    elif 0.25 <= ask <= 3.50:
        score += 15
        notes.append("Premium in preferred range.")
    elif 3.50 < ask <= 8.00:
        score += 10
        notes.append("Premium is usable.")
    elif 8.00 < ask <= 15.00:
        score += 4
        notes.append("Premium is heavier but still usable.")
    else:
        score -= 5
        notes.append("Premium is less efficient.")

    option["trade_intent"] = intent
    option["dte"] = dte
    option["bidAskSpread"] = round(spread, 4)
    option["spread_pct"] = round(spread_pct, 4)
    option["mark"] = round(mark, 4)
    option["distance_pct"] = round(distance_pct, 4)
    option["monitoring_mode"] = "OPTION_PREMIUM"
    option["price_reference"] = round(mark if mark > 0 else ask, 4)

    return int(round(score)), notes


def option_is_executable(
    option: Dict[str, Any],
    min_score: int = 60,
    trading_mode: str = "paper",
) -> Tuple[bool, str]:
    option = _safe_dict(option)
    trading_mode = _safe_str(trading_mode, "paper").lower()

    if not option:
        return False, "no_option_contract"

    score = _safe_float(option.get("contract_score"), 0.0)
    volume = _safe_float(option.get("volume"), 0.0)
    oi = _safe_float(option.get("openInterest", option.get("open_interest")), 0.0)
    ask = _safe_float(option.get("ask", option.get("mark", option.get("last"))), 0.0)
    spread_pct = _safe_float(option.get("spread_pct"), 0.0)
    dte = _safe_int(option.get("dte", 0), 0)
    intent = _safe_str(option.get("trade_intent", "GRIND"), "GRIND").upper()

    if score < min_score:
        return False, "contract_score_too_low"
    if volume < 50:
        return False, "volume_too_thin"
    if oi < 50:
        return False, "open_interest_too_thin"

    if trading_mode == "live":
        if ask <= 0:
            return False, "ask_unavailable"
    else:
        fallback_price = _safe_float(
            option.get("mark", option.get("last", option.get("price", 0.0))),
            0.0,
        )
        if ask <= 0 and fallback_price <= 0:
            return False, "quote_unavailable_paper_mode"

    if spread_pct > 0.12:
        return False, "spread_too_wide"

    if trading_mode == "live":
        if intent == "GRIND" and dte < 2:
            return False, "expiry_too_close_for_grind"
        if intent == "MOMENTUM" and dte < 1:
            return False, "expiry_too_close_for_momentum"
        if intent == "EXPLOSIVE" and dte < 1:
            return False, "expiry_too_close_for_explosive"
    else:
        # Paper mode can allow 0DTE, but only for faster intent styles.
        if intent == "GRIND" and dte < 1:
            return False, "expiry_too_close_for_grind"
        if intent == "MOMENTUM" and dte < 0:
            return False, "expiry_too_close_for_momentum"
        if intent == "EXPLOSIVE" and dte < 0:
            return False, "expiry_too_close_for_explosive"

    return True, "ok"


def choose_best_option(
    option_chain: List[Dict[str, Any]],
    stock_price: float,
    strategy: str,
    trade: Optional[Dict[str, Any]] = None,
    trading_mode: str = "paper",
):
    normalized_strategy = _normalize_option_type(strategy)

    executable_pool: List[Dict[str, Any]] = []
    fallback_pool: List[Dict[str, Any]] = []

    for raw_option in option_chain or []:
        option = dict(raw_option) if isinstance(raw_option, dict) else {}
        score, notes = contract_quality_score(option, stock_price, normalized_strategy, trade=trade)
        option["contract_score"] = score
        option["contract_notes"] = notes

        is_exec, exec_reason = option_is_executable(
            option,
            min_score=60,
            trading_mode=trading_mode,
        )
        option["is_executable"] = is_exec
        option["execution_reason"] = exec_reason
        option["selected_price_reference"] = _safe_float(
            option.get("mark", option.get("ask", option.get("last", 0.0))),
            0.0,
        )

        fallback_pool.append(option)
        if is_exec:
            executable_pool.append(option)

    def _sort_key(opt: Dict[str, Any]):
        return (
            _safe_float(opt.get("contract_score"), 0.0),
            -_safe_float(opt.get("spread_pct"), 999.0),
            _safe_float(opt.get("volume"), 0.0),
            _safe_float(opt.get("openInterest", opt.get("open_interest")), 0.0),
            -_safe_float(opt.get("distance_pct"), 999.0),
            _safe_float(opt.get("dte"), 0.0),
        )

    if executable_pool:
        best = sorted(executable_pool, key=_sort_key, reverse=True)[0]
        return best, best.get("contract_score", -1), best.get("contract_notes", [])

    if fallback_pool:
        best = sorted(fallback_pool, key=_sort_key, reverse=True)[0]
        return best, best.get("contract_score", -1), best.get("contract_notes", [])

    return None, -1, []


def build_option_execution_payload(
    option: Dict[str, Any],
    underlying_symbol: str,
    underlying_price: float,
) -> Dict[str, Any]:
    option = _safe_dict(option)

    entry_price = _safe_float(
        option.get("mark", option.get("ask", option.get("last", 0.0))),
        0.0,
    )

    return {
        "symbol": _safe_str(underlying_symbol, "UNKNOWN").upper(),
        "vehicle_selected": "OPTION",
        "contract_symbol": _safe_str(option.get("contractSymbol", ""), ""),
        "option_type": _extract_option_type(option),
        "strike": _safe_float(option.get("strike"), 0.0),
        "expiry": option.get("expiry", option.get("expiration")),
        "contracts": _safe_int(option.get("contracts", 1), 1),
        "entry": entry_price,
        "entry_price_reference": entry_price,
        "monitoring_mode": "OPTION_PREMIUM",
        "current_price_field": "option_mark",
        "underlying_entry": _safe_float(underlying_price, 0.0),
        "mark": _safe_float(option.get("mark"), entry_price),
        "bid": _safe_float(option.get("bid"), 0.0),
        "ask": _safe_float(option.get("ask"), 0.0),
        "last": _safe_float(option.get("last"), 0.0),
        "spread_pct": _safe_float(option.get("spread_pct"), 0.0),
        "contract_score": _safe_float(option.get("contract_score"), 0.0),
        "trade_intent": _safe_str(option.get("trade_intent", "GRIND"), "GRIND"),
        "dte": _safe_int(option.get("dte", 0), 0),
        "is_executable": bool(option.get("is_executable")),
        "execution_reason": _safe_str(option.get("execution_reason", ""), ""),
        "contract_notes": list(option.get("contract_notes", [])),
    }


def explain_option_choice(option: Dict[str, Any]) -> List[str]:
    option = _safe_dict(option)
    if not option:
        return ["No suitable option contract was selected."]

    notes = list(option.get("contract_notes", []))
    score = option.get("contract_score", 0)
    strike = option.get("strike", "N/A")
    dte = option.get("dte", "N/A")
    option_type = _extract_option_type(option) or option.get("type", "N/A")
    expiry = option.get("expiry", option.get("expiration", "N/A"))
    mark = option.get("mark", "N/A")
    exec_reason = option.get("execution_reason", "unknown")

    return [
        "This contract was selected to express the trade idea as efficiently as possible.",
        f"Contract type: {option_type}.",
        f"Strike: {strike}.",
        f"Expiry: {expiry}.",
        f"Time to expiry: {dte} days.",
        f"Estimated mark: {mark}.",
        *notes,
        f"Execution check: {exec_reason}.",
        f"Final contract quality score: {score}.",
    ]


__all__ = [
    "determine_trade_intent",
    "contract_quality_score",
    "option_is_executable",
    "choose_best_option",
    "build_option_execution_payload",
    "explain_option_choice",
]
