import pandas as pd
from engine.options_liquidity import liquid_option
from engine.option_delta import delta_score

def safe_int(v):
    if pd.isna(v):
        return 0
    return int(v)

def safe_float(v):
    if pd.isna(v):
        return None
    return float(v)

def rank_option_row(row, price):
    score = 0

    volume = safe_int(row.get("volume", 0))
    oi = safe_int(row.get("openInterest", 0))
    strike = safe_float(row.get("strike", 0))
    iv = safe_float(row.get("impliedVolatility", None))

    if liquid_option(volume, oi):
        score += 40
    if volume > 500:
        score += 20
    if oi > 1000:
        score += 20
    if iv is not None and iv < 0.80:
        score += 10

    if strike is not None:
        score += delta_score(strike, price)

    return score
