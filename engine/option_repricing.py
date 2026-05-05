# /content/SimpleeMrkTrade/engine/option_repricing.py
"""
Observatory Option Repricing Layer
==================================

Purpose:
    Refresh the current premium / mark for an already-open OPTION position.

Why this exists:
    Entry-time option selection already works through the execution universe and
    options intelligence layers. But open positions need a separate repricing
    layer because an open contract must be refreshed by its exact contract
    identity, not by the underlying stock price.

Hard rule:
    This module NEVER returns underlying stock price as option current price.

Inputs it can use:
    - symbol
    - contractSymbol
    - expiration
    - right
    - strike
    - existing option/contract payloads

Outputs:
    - bid
    - ask
    - last
    - mark
    - spread
    - spread_pct
    - option_current_price
    - current_option_mark
    - underlying_price only as context
    - repriced boolean
    - source/reason diagnostics

Safe fallback behavior:
    If live quote refresh fails, it returns a structured failure payload.
    The caller can then keep the stored premium rather than leaking underlying
    stock price into option monitoring.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None


OPTION_MULTIPLIER = 100


# ============================================================
# BASIC NORMALIZATION HELPERS
# ============================================================

def _now_iso() -> str:
    return datetime.now().isoformat()


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _safe_upper(value: Any, default: str = "") -> str:
    return _safe_str(value, default).upper()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        number = float(value)
        if number != number:
            return default
        return number
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _round4(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 4)


def _round2(value: Any, default: float = 0.0) -> float:
    return round(_safe_float(value, default), 2)


def _first_positive_float(*values: Any) -> float:
    for value in values:
        number = _safe_float(value, 0.0)
        if number > 0:
            return number
    return 0.0


# ============================================================
# CONTRACT EXTRACTION HELPERS
# ============================================================

def extract_option_payload(position: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pull the best available contract identity from an open position.

    This preserves compatibility with all the shapes currently present in the
    Observatory:
        position root fields
        position["option"]
        position["contract"]
        position["selected_contract"]
        nested lifecycle records
    """
    pos = _safe_dict(position)

    option = _safe_dict(pos.get("option"))
    contract = _safe_dict(pos.get("contract"))
    selected_contract = _safe_dict(pos.get("selected_contract"))
    lifecycle = _safe_dict(pos.get("lifecycle"))
    lifecycle_contract = _safe_dict(lifecycle.get("contract"))
    lifecycle_option = _safe_dict(lifecycle.get("option"))

    sources = [
        pos,
        option,
        contract,
        selected_contract,
        lifecycle_contract,
        lifecycle_option,
    ]

    def pick_text(keys: List[str], default: str = "") -> str:
        for source in sources:
            for key in keys:
                value = _safe_str(source.get(key), "")
                if value:
                    return value
        return default

    def pick_float(keys: List[str], default: float = 0.0) -> float:
        for source in sources:
            for key in keys:
                value = _safe_float(source.get(key), 0.0)
                if value > 0:
                    return value
        return default

    symbol = pick_text(["symbol", "underlying_symbol", "ticker"], "")
    contract_symbol = pick_text(
        [
            "contractSymbol",
            "contract_symbol",
            "option_symbol",
            "occ_symbol",
            "selected_contract_symbol",
        ],
        "",
    )
    expiration = pick_text(
        [
            "expiration",
            "expiry",
            "expiration_date",
            "expiry_date",
            "option_expiration",
        ],
        "",
    )
    right = _safe_upper(
        pick_text(
            [
                "right",
                "option_type",
                "type",
                "side",
                "strategy",
            ],
            "",
        ),
        "",
    )

    if right in {"C", "CALLS"}:
        right = "CALL"
    elif right in {"P", "PUTS"}:
        right = "PUT"
    elif "CALL" in right:
        right = "CALL"
    elif "PUT" in right:
        right = "PUT"

    strike = pick_float(["strike", "strike_price", "option_strike"], 0.0)

    bid = pick_float(["bid"], 0.0)
    ask = pick_float(["ask"], 0.0)
    last = pick_float(["last", "lastPrice", "last_price"], 0.0)
    mark = pick_float(
        [
            "current_option_mark",
            "option_current_mark",
            "option_mark",
            "current_mark",
            "mark",
            "selected_price_reference",
            "price_reference",
        ],
        0.0,
    )

    entry = pick_float(
        [
            "entry_premium",
            "entry_option_mark",
            "option_entry_price",
            "entry_price",
            "entry",
            "fill_price",
        ],
        0.0,
    )

    underlying_price = pick_float(
        [
            "underlying_price",
            "current_underlying_price",
            "underlying_mark",
            "market_price",
            "stock_price",
        ],
        0.0,
    )

    return {
        "symbol": symbol.upper(),
        "contractSymbol": contract_symbol,
        "expiration": expiration,
        "right": right,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "last": last,
        "mark": mark,
        "entry": entry,
        "underlying_price": underlying_price,
        "raw_option": option,
        "raw_contract": contract,
    }


def _contract_matches(
    row: Dict[str, Any],
    contract_symbol: str,
    right: str,
    strike: float,
) -> bool:
    row_symbol = _safe_str(row.get("contractSymbol"), "")
    if contract_symbol and row_symbol == contract_symbol:
        return True

    row_strike = _safe_float(row.get("strike"), 0.0)
    if right and strike > 0 and abs(row_strike - strike) < 0.0001:
        return True

    return False


# ============================================================
# QUOTE MATH
# ============================================================

def calculate_option_mark(bid: Any, ask: Any, last: Any = 0.0) -> Tuple[float, str]:
    """
    Conservative option mark resolver.

    Priority:
        1. bid/ask midpoint when both are valid
        2. ask if ask exists and bid is unavailable
        3. last if last exists
        4. bid if bid exists
        5. 0.0
    """
    bid_f = _safe_float(bid, 0.0)
    ask_f = _safe_float(ask, 0.0)
    last_f = _safe_float(last, 0.0)

    if bid_f > 0 and ask_f > 0 and ask_f >= bid_f:
        return round((bid_f + ask_f) / 2.0, 4), "bid_ask_mid"

    if ask_f > 0:
        return round(ask_f, 4), "ask_fallback"

    if last_f > 0:
        return round(last_f, 4), "last_fallback"

    if bid_f > 0:
        return round(bid_f, 4), "bid_fallback"

    return 0.0, "missing_quote"


def build_option_quote_payload(
    *,
    symbol: str,
    contract_symbol: str,
    expiration: str,
    right: str,
    strike: float,
    bid: float,
    ask: float,
    last: float,
    volume: Any = 0,
    open_interest: Any = 0,
    implied_volatility: Any = 0.0,
    in_the_money: Any = None,
    underlying_price: float = 0.0,
    source: str = "unknown",
    reason: str = "ok",
    repriced: bool = True,
) -> Dict[str, Any]:
    mark, mark_source = calculate_option_mark(bid, ask, last)

    spread = 0.0
    spread_pct = 0.0
    if bid > 0 and ask > 0 and ask >= bid:
        spread = round(ask - bid, 4)
        spread_pct = round(spread / ask, 4) if ask > 0 else 0.0

    return {
        "repriced": bool(repriced and mark > 0),
        "source": source,
        "reason": reason,
        "timestamp": _now_iso(),

        "symbol": _safe_upper(symbol),
        "contractSymbol": _safe_str(contract_symbol),
        "expiration": _safe_str(expiration),
        "right": _safe_upper(right),
        "strike": _round4(strike),

        "bid": _round4(bid),
        "ask": _round4(ask),
        "last": _round4(last),
        "mark": _round4(mark),
        "mid": _round4(mark),
        "current_mark": _round4(mark),
        "current_option_mark": _round4(mark),
        "option_current_mark": _round4(mark),
        "option_current_price": _round4(mark),
        "current_option_price": _round4(mark),
        "current_premium": _round4(mark),
        "premium_current": _round4(mark),

        "mark_source": mark_source,
        "spread": _round4(spread),
        "bidAskSpread": _round4(spread),
        "spread_pct": _round4(spread_pct),

        "volume": _safe_int(volume, 0),
        "open_interest": _safe_int(open_interest, 0),
        "implied_volatility": _round4(implied_volatility),
        "in_the_money": bool(in_the_money) if in_the_money is not None else None,

        # Context only. Never use this as option current price.
        "underlying_price": _round4(underlying_price),
        "monitoring_mode": "OPTION_PREMIUM",
        "price_basis": "OPTION_PREMIUM",
        "leak_blocked": False,
    }


def build_failed_quote_payload(
    *,
    position: Dict[str, Any],
    reason: str,
    source: str = "option_repricing",
) -> Dict[str, Any]:
    payload = extract_option_payload(position)

    stored_mark = _first_positive_float(
        payload.get("mark"),
        payload.get("entry"),
        payload.get("last"),
        payload.get("ask"),
        payload.get("bid"),
    )

    return {
        "repriced": False,
        "source": source,
        "reason": reason,
        "timestamp": _now_iso(),

        "symbol": payload.get("symbol", ""),
        "contractSymbol": payload.get("contractSymbol", ""),
        "expiration": payload.get("expiration", ""),
        "right": payload.get("right", ""),
        "strike": _round4(payload.get("strike")),

        "bid": _round4(payload.get("bid")),
        "ask": _round4(payload.get("ask")),
        "last": _round4(payload.get("last")),
        "mark": _round4(stored_mark),
        "mid": _round4(stored_mark),
        "current_mark": _round4(stored_mark),
        "current_option_mark": _round4(stored_mark),
        "option_current_mark": _round4(stored_mark),
        "option_current_price": _round4(stored_mark),
        "current_option_price": _round4(stored_mark),
        "current_premium": _round4(stored_mark),
        "premium_current": _round4(stored_mark),

        "mark_source": "stored_fallback",
        "spread": 0.0,
        "bidAskSpread": 0.0,
        "spread_pct": 0.0,

        "volume": 0,
        "open_interest": 0,
        "implied_volatility": 0.0,
        "in_the_money": None,

        "underlying_price": _round4(payload.get("underlying_price")),
        "monitoring_mode": "OPTION_PREMIUM",
        "price_basis": "OPTION_PREMIUM",
        "leak_blocked": True,
    }


# ============================================================
# LIVE REPRICE
# ============================================================

def _fetch_underlying_context(symbol: str) -> float:
    if yf is None or not symbol:
        return 0.0

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d", auto_adjust=True)
        if hist is not None and not hist.empty and "Close" in hist:
            return _round4(hist["Close"].iloc[-1])
    except Exception:
        return 0.0

    return 0.0


def reprice_option_contract(
    *,
    symbol: str,
    contract_symbol: str = "",
    expiration: str = "",
    right: str = "",
    strike: Any = 0.0,
) -> Dict[str, Any]:
    """
    Reprice a specific open option contract.

    This function uses yfinance option chains. It does not use underlying
    history as option price. Underlying price is returned only as context.
    """
    symbol = _safe_upper(symbol)
    contract_symbol = _safe_str(contract_symbol)
    expiration = _safe_str(expiration)
    right = _safe_upper(right)
    strike_f = _safe_float(strike, 0.0)

    if not symbol:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": "missing_symbol",
            "timestamp": _now_iso(),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    if yf is None:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": "yfinance_unavailable",
            "timestamp": _now_iso(),
            "symbol": symbol,
            "contractSymbol": contract_symbol,
            "expiration": expiration,
            "right": right,
            "strike": _round4(strike_f),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    try:
        ticker = yf.Ticker(symbol)
        available_expirations = list(ticker.options or [])
    except Exception as exc:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": f"ticker_options_failed:{type(exc).__name__}",
            "timestamp": _now_iso(),
            "symbol": symbol,
            "contractSymbol": contract_symbol,
            "expiration": expiration,
            "right": right,
            "strike": _round4(strike_f),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    if not available_expirations:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": "no_option_expirations",
            "timestamp": _now_iso(),
            "symbol": symbol,
            "contractSymbol": contract_symbol,
            "expiration": expiration,
            "right": right,
            "strike": _round4(strike_f),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    target_expiration = expiration
    if target_expiration not in available_expirations:
        if expiration:
            return {
                "repriced": False,
                "source": "option_repricing",
                "reason": "expiration_not_available",
                "timestamp": _now_iso(),
                "symbol": symbol,
                "contractSymbol": contract_symbol,
                "expiration": expiration,
                "available_expirations": available_expirations[:12],
                "right": right,
                "strike": _round4(strike_f),
                "monitoring_mode": "OPTION_PREMIUM",
                "price_basis": "OPTION_PREMIUM",
                "leak_blocked": True,
            }
        target_expiration = available_expirations[0]

    try:
        chain = ticker.option_chain(target_expiration)
        rows_df = chain.calls if right != "PUT" else chain.puts
    except Exception as exc:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": f"option_chain_failed:{type(exc).__name__}",
            "timestamp": _now_iso(),
            "symbol": symbol,
            "contractSymbol": contract_symbol,
            "expiration": target_expiration,
            "right": right,
            "strike": _round4(strike_f),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    if rows_df is None or rows_df.empty:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": "empty_option_side",
            "timestamp": _now_iso(),
            "symbol": symbol,
            "contractSymbol": contract_symbol,
            "expiration": target_expiration,
            "right": right,
            "strike": _round4(strike_f),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    rows = rows_df.to_dict("records")
    matched_row = None

    for row in rows:
        if _contract_matches(row, contract_symbol, right, strike_f):
            matched_row = row
            break

    if matched_row is None:
        return {
            "repriced": False,
            "source": "option_repricing",
            "reason": "contract_not_found_in_chain",
            "timestamp": _now_iso(),
            "symbol": symbol,
            "contractSymbol": contract_symbol,
            "expiration": target_expiration,
            "right": right,
            "strike": _round4(strike_f),
            "monitoring_mode": "OPTION_PREMIUM",
            "price_basis": "OPTION_PREMIUM",
            "leak_blocked": True,
        }

    bid = _safe_float(matched_row.get("bid"), 0.0)
    ask = _safe_float(matched_row.get("ask"), 0.0)
    last = _safe_float(matched_row.get("lastPrice", matched_row.get("last")), 0.0)
    volume = matched_row.get("volume", 0)
    open_interest = matched_row.get("openInterest", matched_row.get("open_interest", 0))
    iv = matched_row.get("impliedVolatility", matched_row.get("implied_volatility", 0.0))
    itm = matched_row.get("inTheMoney", matched_row.get("in_the_money", None))

    underlying_price = _fetch_underlying_context(symbol)

    quote = build_option_quote_payload(
        symbol=symbol,
        contract_symbol=_safe_str(matched_row.get("contractSymbol"), contract_symbol),
        expiration=target_expiration,
        right=right,
        strike=_safe_float(matched_row.get("strike"), strike_f),
        bid=bid,
        ask=ask,
        last=last,
        volume=volume,
        open_interest=open_interest,
        implied_volatility=iv,
        in_the_money=itm,
        underlying_price=underlying_price,
        source="yfinance_option_chain",
        reason="ok",
        repriced=True,
    )

    if quote.get("mark", 0.0) <= 0:
        quote["repriced"] = False
        quote["reason"] = "quote_found_but_no_positive_mark"
        quote["leak_blocked"] = True

    return quote


def reprice_open_option_position(position: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main caller for open positions.

    Accepts the full position row and returns a premium-safe quote payload.
    """
    pos = _safe_dict(position)
    payload = extract_option_payload(pos)

    symbol = payload.get("symbol", "")
    contract_symbol = payload.get("contractSymbol", "")
    expiration = payload.get("expiration", "")
    right = payload.get("right", "")
    strike = payload.get("strike", 0.0)

    if not symbol:
        return build_failed_quote_payload(
            position=pos,
            reason="missing_symbol",
        )

    quote = reprice_option_contract(
        symbol=symbol,
        contract_symbol=contract_symbol,
        expiration=expiration,
        right=right,
        strike=strike,
    )

    if not quote.get("repriced"):
        fallback = build_failed_quote_payload(
            position=pos,
            reason=quote.get("reason", "repricer_failed"),
        )
        fallback["live_attempt"] = quote
        return fallback

    return quote


# ============================================================
# POSITION APPLICATION
# ============================================================

def apply_option_reprice_to_position(position: Dict[str, Any], quote: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return an updated copy of an OPTION position with refreshed premium fields.

    This does not mutate the caller's original dict unless the caller chooses
    to assign the returned result back into their open positions list.

    Critical safety:
        current_price is premium-safe for OPTION rows.
        underlying_price remains context only.
    """
    pos = dict(_safe_dict(position))
    quote = _safe_dict(quote)

    if _safe_upper(pos.get("vehicle_selected", pos.get("vehicle", ""))) != "OPTION":
        return pos

    premium = _safe_float(
        quote.get(
            "option_current_price",
            quote.get("current_option_mark", quote.get("mark", 0.0)),
        ),
        0.0,
    )

    if premium <= 0:
        pos.setdefault("monitor_debug", {})
        if isinstance(pos["monitor_debug"], dict):
            pos["monitor_debug"]["option_reprice"] = quote
            pos["monitor_debug"]["option_reprice_applied"] = False
        return pos

    pos["current_price"] = _round4(premium)
    pos["current"] = _round4(premium)
    pos["option_current_price"] = _round4(premium)
    pos["current_option_price"] = _round4(premium)
    pos["current_option_mark"] = _round4(premium)
    pos["option_current_mark"] = _round4(premium)
    pos["premium_current"] = _round4(premium)
    pos["current_premium"] = _round4(premium)

    pos["bid"] = _round4(quote.get("bid"))
    pos["ask"] = _round4(quote.get("ask"))
    pos["last"] = _round4(quote.get("last"))
    pos["mark"] = _round4(quote.get("mark", premium))
    pos["spread"] = _round4(quote.get("spread"))
    pos["bidAskSpread"] = _round4(quote.get("bidAskSpread", quote.get("spread")))
    pos["spread_pct"] = _round4(quote.get("spread_pct"))

    pos["monitoring_mode"] = "OPTION_PREMIUM"
    pos["price_basis"] = "OPTION_PREMIUM"
    pos["price_source"] = quote.get("source", "option_repricing")
    pos["option_repriced_at"] = quote.get("timestamp", _now_iso())

    # Context only.
    underlying_context = _safe_float(quote.get("underlying_price"), 0.0)
    if underlying_context > 0:
        pos["underlying_price"] = _round4(underlying_context)
        pos["current_underlying_price"] = _round4(underlying_context)

    option_obj = dict(_safe_dict(pos.get("option")))
    contract_obj = dict(_safe_dict(pos.get("contract")))

    for target in (option_obj, contract_obj):
        target["current_option_mark"] = _round4(premium)
        target["option_current_mark"] = _round4(premium)
        target["option_current_price"] = _round4(premium)
        target["current_mark"] = _round4(premium)
        target["mark"] = _round4(quote.get("mark", premium))
        target["bid"] = _round4(quote.get("bid"))
        target["ask"] = _round4(quote.get("ask"))
        target["last"] = _round4(quote.get("last"))
        target["spread"] = _round4(quote.get("spread"))
        target["bidAskSpread"] = _round4(quote.get("bidAskSpread", quote.get("spread")))
        target["spread_pct"] = _round4(quote.get("spread_pct"))
        target["repriced_at"] = quote.get("timestamp", _now_iso())
        target["repriced"] = bool(quote.get("repriced"))

    if option_obj:
        pos["option"] = option_obj
    if contract_obj:
        pos["contract"] = contract_obj

    monitor_debug = dict(_safe_dict(pos.get("monitor_debug")))
    monitor_debug["option_reprice"] = quote
    monitor_debug["option_reprice_applied"] = True
    monitor_debug["price_basis"] = "OPTION_PREMIUM"
    monitor_debug["current_premium"] = _round4(premium)
    monitor_debug["underlying_context"] = _round4(pos.get("underlying_price"))
    monitor_debug["leak_blocked"] = bool(quote.get("leak_blocked", False))
    pos["monitor_debug"] = monitor_debug

    return pos


def reprice_and_apply_open_option_position(position: Dict[str, Any]) -> Dict[str, Any]:
    quote = reprice_open_option_position(position)
    return apply_option_reprice_to_position(position, quote)


# ============================================================
# BULK HELPERS
# ============================================================

def reprice_open_option_positions(positions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bulk helper for diagnostics or later monitor integration.
    """
    rows = []
    updated_positions = []

    for raw in _safe_list(positions):
        pos = _safe_dict(raw)
        vehicle = _safe_upper(pos.get("vehicle_selected", pos.get("vehicle", "")))

        if vehicle != "OPTION":
            updated_positions.append(pos)
            continue

        quote = reprice_open_option_position(pos)
        updated = apply_option_reprice_to_position(pos, quote)
        updated_positions.append(updated)

        rows.append({
            "symbol": pos.get("symbol"),
            "contractSymbol": extract_option_payload(pos).get("contractSymbol"),
            "repriced": quote.get("repriced"),
            "reason": quote.get("reason"),
            "old_current": pos.get("current_price"),
            "new_current": updated.get("current_price"),
            "underlying_context": updated.get("underlying_price"),
            "source": quote.get("source"),
            "leak_blocked": quote.get("leak_blocked"),
        })

    return {
        "timestamp": _now_iso(),
        "option_count": len(rows),
        "repriced_count": sum(1 for row in rows if row.get("repriced")),
        "failed_count": sum(1 for row in rows if not row.get("repriced")),
        "rows": rows,
        "positions": updated_positions,
    }


__all__ = [
    "extract_option_payload",
    "calculate_option_mark",
    "build_option_quote_payload",
    "build_failed_quote_payload",
    "reprice_option_contract",
    "reprice_open_option_position",
    "apply_option_reprice_to_position",
    "reprice_and_apply_open_option_position",
    "reprice_open_option_positions",
]
