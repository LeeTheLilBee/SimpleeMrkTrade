import json
from datetime import datetime

from engine.watchlist import get_watchlist
from engine.data_utils import safe_download

EXECUTION_UNIVERSE_PATH = "data/execution_universe.json"


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _infer_strategy(last_close, first_close):
    if last_close >= first_close:
        return "CALL"
    return "PUT"


def _infer_trend(last_close, first_close):
    if last_close > first_close:
        return "UPTREND"
    if last_close < first_close:
        return "DOWNTREND"
    return "SIDEWAYS"


def _compute_rsi_placeholder(df):
    try:
        close = df["Close"].astype(float)
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        gain = _safe_float(gain, 0.0)
        loss = _safe_float(loss, 0.0)
        if loss == 0:
            return 70
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(_safe_float(rsi, 55), 2)
    except Exception:
        return 55


def _compute_atr_placeholder(df):
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


def rebuild_execution_universe_from_watchlist(limit=20, spotlight_limit=5, watchlist_limit=50, universe_limit=220):
    watchlist = get_watchlist(limit=watchlist_limit, universe_limit=universe_limit)
    selected = []

    for symbol in watchlist:
        df = safe_download(symbol, period="3mo", auto_adjust=True, progress=False)
        if df is None or df.empty or len(df) < 20:
            continue

        try:
            last_close = _safe_float(df["Close"].iloc[-1].item())
            first_close = _safe_float(df["Close"].iloc[-20].item())
            avg_volume = _safe_float(df["Volume"].rolling(20).mean().iloc[-1].item())
        except Exception:
            continue

        if last_close <= 0:
            continue

        momentum = (last_close - first_close) / first_close if first_close > 0 else 0
        atr = _compute_atr_placeholder(df)
        rsi = _compute_rsi_placeholder(df)
        strategy = _infer_strategy(last_close, first_close)
        trend = _infer_trend(last_close, first_close)

        score = round((momentum * 1000) + min(avg_volume / 100000, 100), 2)

        selected.append({
            "symbol": symbol,
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
        })

    selected = sorted(
        selected,
        key=lambda x: (x["score"], x["avg_volume"]),
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
            "underlying_scan_only": True,
            "options_contract_selection_built": False,
        },
    }

    with open(EXECUTION_UNIVERSE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return payload
