from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from engine.watchlist import get_watchlist
from engine.data_utils import safe_download

EXECUTION_UNIVERSE_PATH = "data/execution_universe.json"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if hasattr(value, "iloc"):
            try:
                return float(value.iloc[-1])
            except Exception:
                return float(value.iloc[0])
        if hasattr(value, "item"):
            try:
                return float(value.item())
            except Exception:
                pass
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if hasattr(value, "iloc"):
            try:
                return int(value.iloc[-1])
            except Exception:
                return int(value.iloc[0])
        if hasattr(value, "item"):
            try:
                return int(value.item())
            except Exception:
                pass
        return int(value)
    except Exception:
        return int(default)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value).strip()
        return text if text else default
    except Exception:
        return default


def _infer_strategy(last_close: float, first_close: float) -> str:
    return "CALL" if last_close >= first_close else "PUT"


def _infer_trend(last_close: float, first_close: float) -> str:
    if last_close > first_close:
        return "UPTREND"
    if last_close < first_close:
        return "DOWNTREND"
    return "SIDEWAYS"


def _compute_rsi_placeholder(df) -> float:
    try:
        close = df["Close"].astype(float)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        gain = _safe_float(gain, 0.0)
        loss = _safe_float(loss, 0.0)
        if loss == 0:
            return 70.0
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(_safe_float(rsi, 55.0), 2)
    except Exception:
        return 55.0


def _compute_atr_placeholder(df) -> float:
    try:
        high = df["High"].astype(float)
        low = df["Low"].astype(float)
        close = df["Close"].astype(float)
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = tr1.combine(tr2, max).combine(tr3, max)

        atr = tr.rolling(14).mean().iloc[-1]
        return round(max(_safe_float(atr, 2.0), 0.25), 2)
    except Exception:
        return 2.0


def _normalize_option_row(
    row: Dict[str, Any],
    symbol: str,
    right: str,
    underlying_price: float,
    expiration: str,
) -> Optional[Dict[str, Any]]:
    if not isinstance(row, dict):
        return None

    strike = _safe_float(row.get("strike"), 0.0)
    bid = _safe_float(row.get("bid"), 0.0)
    ask = _safe_float(row.get("ask"), 0.0)
    last = _safe_float(row.get("lastPrice", row.get("last")), 0.0)
    volume = _safe_int(row.get("volume"), 0)
    open_interest = _safe_int(row.get("openInterest"), 0)
    implied_volatility = _safe_float(row.get("impliedVolatility"), 0.0)
    in_the_money = bool(row.get("inTheMoney", False))
    contract_symbol = _safe_str(row.get("contractSymbol"), "")

    if strike <= 0:
        return None

    if bid > 0 and ask > 0:
        mark = round((bid + ask) / 2.0, 4)
    elif ask > 0:
        mark = round(ask, 4)
    elif last > 0:
        mark = round(last, 4)
    else:
        return None

    spread = round(max(ask - bid, 0.0), 4)
    spread_pct = round((spread / ask), 4) if ask > 0 else 1.0
    distance_pct = round(abs(strike - underlying_price) / underlying_price, 4) if underlying_price > 0 else 9.99

    liquidity_score = min(volume, 500) * 0.06 + min(open_interest, 2000) * 0.015
    spread_penalty = min(spread_pct * 200.0, 60.0)
    distance_penalty = min(distance_pct * 120.0, 30.0)
    iv_penalty = max(implied_volatility - 1.2, 0.0) * 20.0

    contract_score = round(
        100.0 + liquidity_score - spread_penalty - distance_penalty - iv_penalty,
        2,
    )

    return {
        "symbol": symbol,
        "contractSymbol": contract_symbol,
        "expiration": expiration,
        "right": right,
        "strike": round(strike, 2),
        "bid": round(bid, 4),
        "ask": round(ask, 4),
        "last": round(last, 4),
        "mark": round(mark, 4),
        "volume": volume,
        "open_interest": open_interest,
        "implied_volatility": round(implied_volatility, 4),
        "in_the_money": in_the_money,
        "spread": spread,
        "spread_pct": spread_pct,
        "distance_pct": distance_pct,
        "contract_score": contract_score,
    }


def _fetch_option_chain(symbol: str, underlying_price: float, strategy: str) -> List[Dict[str, Any]]:
    try:
        import yfinance as yf
    except Exception:
        return []

    try:
        ticker = yf.Ticker(symbol)
        expirations = getattr(ticker, "options", []) or []
        if not expirations:
            return []

        expiration = expirations[0]
        chain = ticker.option_chain(expiration)

        if strategy == "PUT":
            df = getattr(chain, "puts", None)
            right = "PUT"
        else:
            df = getattr(chain, "calls", None)
            right = "CALL"

        if df is None or getattr(df, "empty", True):
            return []

        rows: List[Dict[str, Any]] = []
        for _, raw_row in df.iterrows():
            row = raw_row.to_dict() if hasattr(raw_row, "to_dict") else dict(raw_row)
            strike = _safe_float(row.get("strike"), 0.0)

            if underlying_price <= 0 or strike <= 0:
                continue

            if abs(strike - underlying_price) / underlying_price > 0.18:
                continue

            normalized = _normalize_option_row(
                row=row,
                symbol=symbol,
                right=right,
                underlying_price=underlying_price,
                expiration=expiration,
            )
            if normalized:
                rows.append(normalized)

        rows.sort(
            key=lambda x: (
                x.get("contract_score", 0.0),
                x.get("open_interest", 0),
                x.get("volume", 0),
            ),
            reverse=True,
        )
        return rows[:12]
    except Exception:
        return []


def rebuild_execution_universe_from_watchlist(
    limit: int = 20,
    spotlight_limit: int = 5,
    watchlist_limit: int = 50,
    universe_limit: int = 220,
) -> Dict[str, Any]:
    watchlist = get_watchlist(limit=watchlist_limit, universe_limit=universe_limit)
    selected: List[Dict[str, Any]] = []

    for item in watchlist:
        symbol = item.get("symbol") if isinstance(item, dict) else item
        symbol = _safe_str(symbol, "").upper()
        if not symbol:
            continue

        df = safe_download(symbol, period="3mo", auto_adjust=True, progress=False)
        if df is None or getattr(df, "empty", True) or len(df) < 20:
            continue

        try:
            last_close = _safe_float(df["Close"].iloc[-1], 0.0)
            first_close = _safe_float(df["Close"].iloc[-20], 0.0)
            avg_volume = _safe_float(df["Volume"].rolling(20).mean().iloc[-1], 0.0)
        except Exception:
            continue

        if last_close <= 0:
            continue

        momentum = (last_close - first_close) / first_close if first_close > 0 else 0.0
        atr = _compute_atr_placeholder(df)
        rsi = _compute_rsi_placeholder(df)
        strategy = _infer_strategy(last_close, first_close)
        trend = _infer_trend(last_close, first_close)
        score = round((momentum * 1000.0) + min(avg_volume / 100000.0, 100.0), 2)

        option_chain = _fetch_option_chain(symbol, last_close, strategy)

        selected.append(
            {
                "symbol": symbol,
                "company_name": symbol,
                "score": score,
                "confidence": "HIGH" if score >= 120 else "MEDIUM" if score >= 60 else "LOW",
                "grade": "A" if score >= 120 else "B" if score >= 80 else "C",
                "price": round(last_close, 2),
                "current_price": round(last_close, 2),
                "entry": round(last_close, 2),
                "atr": atr,
                "rsi": rsi,
                "strategy": strategy,
                "trend": trend,
                "volatility_state": "NORMAL",
                "mode": "AGGRESSIVE_ROTATION",
                "sector": "General",
                "avg_volume": round(avg_volume, 2),
                "momentum": round(momentum, 4),
                "eligible": True,
                "timestamp": datetime.now().isoformat(),
                "option_chain": option_chain,
                "has_option_chain": bool(option_chain),
                "best_option_preview": option_chain[0] if option_chain else None,
                "source": "execution_universe",
            }
        )

    selected = sorted(
        selected,
        key=lambda x: (x.get("score", 0.0), x.get("avg_volume", 0.0)),
        reverse=True,
    )[:limit]

    spotlight = selected[:spotlight_limit]

    payload = {
        "selected": selected,
        "spotlight": spotlight,
        "meta": {
            "rebuilt_at": datetime.now().isoformat(),
            "watchlist_limit": watchlist_limit,
            "universe_limit": universe_limit,
            "selected_count": len(selected),
            "spotlight_count": len(spotlight),
            "mode": "aggressive_rotation",
            "underlying_scan_only": False,
            "options_contract_selection_built": True,
        },
    }

    with open(EXECUTION_UNIVERSE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return payload


def build_execution_universe(
    limit: int = 20,
    spotlight_limit: int = 5,
    watchlist_limit: int = 50,
    universe_limit: int = 220,
) -> Dict[str, Any]:
    return rebuild_execution_universe_from_watchlist(
        limit=limit,
        spotlight_limit=spotlight_limit,
        watchlist_limit=watchlist_limit,
        universe_limit=universe_limit,
    )
