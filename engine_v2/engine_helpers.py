import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from engine.market_universe import load_market_universe
from engine.data_utils import safe_download


def _save_json(path: str, payload: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _load_json(path: str, default: Any) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def now_iso() -> str:
    return datetime.now().isoformat()


def _confidence_from_score(score: float) -> str:
    if score >= 150:
        return "HIGH"
    if score >= 90:
        return "MEDIUM"
    return "LOW"


def _grade_from_score(score: float) -> str:
    if score >= 170:
        return "A"
    if score >= 120:
        return "B"
    if score >= 80:
        return "C"
    return "D"


def _direction_from_momentum(momentum: float) -> str:
    return "CALL" if momentum >= 0 else "PUT"


def _trend_from_momentum(momentum: float) -> str:
    if momentum > 0.03:
        return "UPTREND"
    if momentum < -0.03:
        return "DOWNTREND"
    return "SIDEWAYS"


def _setup_type(momentum: float, volume_ratio: float) -> str:
    if momentum > 0.05 and volume_ratio >= 1.1:
        return "breakout_continuation"
    if momentum > 0 and volume_ratio < 1.1:
        return "steady_continuation"
    if momentum < -0.05 and volume_ratio >= 1.1:
        return "breakdown_pressure"
    if momentum < 0:
        return "weakening"
    return "developing"


def _regime_fit(momentum: float) -> str:
    if abs(momentum) >= 0.06:
        return "STRONG"
    if abs(momentum) >= 0.03:
        return "MODERATE"
    return "MIXED"


def _entry_quality(momentum: float, volume_ratio: float) -> str:
    score = abs(momentum) * 100
    if score >= 6 and volume_ratio >= 1.15:
        return "GREAT"
    if score >= 3:
        return "GOOD"
    if score >= 1.5:
        return "USABLE"
    return "EARLY"


def _time_sensitivity(momentum: float, volume_ratio: float) -> str:
    if abs(momentum) >= 0.06 and volume_ratio >= 1.1:
        return "NOW"
    if abs(momentum) >= 0.03:
        return "NEXT"
    return "WATCH"


def _setup_maturity(momentum: float) -> str:
    if abs(momentum) >= 0.08:
        return "MATURE"
    if abs(momentum) >= 0.04:
        return "DEVELOPING"
    return "EARLY"


def _status_label(momentum: float, volume_ratio: float) -> str:
    if momentum > 0.05 and volume_ratio >= 1.1:
        return "Already Moving"
    if momentum > 0:
        return "Building Cleanly"
    if momentum < -0.05:
        return "Under Pressure"
    if momentum < 0:
        return "Weakening"
    return "Developing"


def _pressure_level(momentum: float, volume_ratio: float) -> str:
    strength = abs(momentum) * 100
    if strength >= 7 or volume_ratio >= 1.3:
        return "high"
    if strength >= 3:
        return "medium"
    return "low"


def _confidence_tier(score: float) -> int:
    if score >= 170:
        return 1
    if score >= 110:
        return 2
    return 3


def _get_symbol_rows(limit: int = 220) -> List[Dict[str, Any]]:
    rows = load_market_universe()
    if not isinstance(rows, list):
        return []

    cleaned = []
    for row in rows:
        if not isinstance(row, dict):
            continue

        symbol = str(row.get("symbol", "")).strip().upper()
        if not symbol:
            continue

        asset_type = str(row.get("asset_type", "equity")).strip().lower()
        if asset_type not in {"equity", "etf"}:
            continue

        cleaned.append(row)

    return cleaned[:limit]


def build_watchlist(limit: int = 50, universe_limit: int = 220) -> List[Dict[str, Any]]:
    candidates = []

    for row in _get_symbol_rows(universe_limit):
        symbol = str(row.get("symbol", "")).strip().upper()
        company_name = str(row.get("company_name", symbol)).strip() or symbol

        df = safe_download(symbol, period="3mo", auto_adjust=True, progress=False)
        if df is None or df.empty or len(df) < 30:
            continue

        try:
            last_close = _safe_float(df["Close"].iloc[-1].item())
            base_close = _safe_float(df["Close"].iloc[-20].item())
            avg_volume = _safe_float(df["Volume"].rolling(20).mean().iloc[-1].item())
            recent_volume = _safe_float(df["Volume"].iloc[-1].item())
        except Exception:
            continue

        if last_close <= 0 or base_close <= 0 or avg_volume <= 0:
            continue

        momentum = (last_close - base_close) / base_close
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
        score = round((momentum * 1000) + min(avg_volume / 100000, 100), 2)

        candidates.append({
            "symbol": symbol,
            "company_name": company_name,
            "price": round(last_close, 2),
            "momentum": round(momentum, 4),
            "avg_volume": round(avg_volume, 2),
            "recent_volume": round(recent_volume, 2),
            "volume_ratio": round(volume_ratio, 2),
            "score": score,
            "confidence": _confidence_from_score(score),
            "grade": _grade_from_score(score),
            "direction": _direction_from_momentum(momentum),
            "trend": _trend_from_momentum(momentum),
            "setup_type": _setup_type(momentum, volume_ratio),
            "regime_fit": _regime_fit(momentum),
            "entry_quality": _entry_quality(momentum, volume_ratio),
            "time_sensitivity": _time_sensitivity(momentum, volume_ratio),
            "setup_maturity": _setup_maturity(momentum),
            "status_label": _status_label(momentum, volume_ratio),
            "pressure_level": _pressure_level(momentum, volume_ratio),
            "confidence_tier": _confidence_tier(score),
        })

    candidates = sorted(
        candidates,
        key=lambda x: (x["score"], x["volume_ratio"], x["avg_volume"]),
        reverse=True,
    )

    return candidates[:limit]
