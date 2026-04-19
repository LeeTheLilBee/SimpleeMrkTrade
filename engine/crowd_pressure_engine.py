from __future__ import annotations
from typing import Any, Dict

TECH_SYMBOLS = {"MU", "NVDA", "AMD", "PLTR", "PANW", "CRM", "MSFT", "AAPL", "META", "GOOGL", "AMZN"}
ENERGY_SYMBOLS = {"XLE", "CVX", "XOM", "COP", "MPC", "PSX", "VLO", "OXY", "EOG"}
FINANCIALS_SYMBOLS = {"JPM", "BAC", "GS", "MS", "C", "WFC"}
HEALTHCARE_SYMBOLS = {"LLY", "JNJ", "PFE", "MRK", "UNH", "ABBV"}


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        text = str(value or "").strip()
        return text if text else default
    except Exception:
        return default


def _norm_symbol(value: Any) -> str:
    return _safe_str(value, "UNKNOWN").upper()


def _infer_sector(symbol: str) -> str:
    if symbol in TECH_SYMBOLS:
        return "TECH"
    if symbol in ENERGY_SYMBOLS:
        return "ENERGY"
    if symbol in FINANCIALS_SYMBOLS:
        return "FINANCIALS"
    if symbol in HEALTHCARE_SYMBOLS:
        return "HEALTHCARE"
    return "UNKNOWN"


def estimate_crowd_pressure(symbol, volatility_state, sector_counts=None, trend=None):
    symbol = _norm_symbol(symbol)
    sector_counts = _safe_dict(sector_counts)
    volatility_state = _safe_str(volatility_state, "UNKNOWN").upper()
    trend = _safe_str(trend, "UNKNOWN").upper()

    sector = _infer_sector(symbol)
    crowded_sector_size = int(sector_counts.get(sector, 0)) if sector != "UNKNOWN" else 0

    pressure_score = 0
    reasons = []

    if crowded_sector_size >= 4:
        pressure_score += 55
        reasons.append("sector_heavily_crowded")
    elif crowded_sector_size == 3:
        pressure_score += 40
        reasons.append("sector_crowded")
    elif crowded_sector_size == 2:
        pressure_score += 22
        reasons.append("sector_somewhat_crowded")
    elif crowded_sector_size == 1:
        pressure_score += 8
        reasons.append("sector_lightly_crowded")

    if volatility_state == "ELEVATED":
        pressure_score += 25
        reasons.append("elevated_volatility")
    elif volatility_state == "NORMAL":
        pressure_score += 10
        reasons.append("normal_volatility")
    elif volatility_state == "LOW":
        pressure_score += 4
        reasons.append("low_volatility")

    if trend == "UPTREND":
        pressure_score += 10
        reasons.append("trend_chasing_risk")
    elif trend == "DOWNTREND":
        pressure_score += 6
        reasons.append("downtrend_instability")

    if pressure_score >= 65:
        label = "HIGH"
        note = "Crowd pressure is elevated. Strong setup quality may still face exhaustion or positioning risk."
    elif pressure_score >= 35:
        label = "MODERATE"
        note = "Some crowding risk is present. Monitor follow-through and failed continuation carefully."
    else:
        label = "LOW"
        note = "Crowd pressure appears contained."

    return {
        "symbol": symbol,
        "sector": sector,
        "crowded_sector_size": crowded_sector_size,
        "score": pressure_score,
        "label": label,
        "note": note,
        "reasons": reasons,
    }
