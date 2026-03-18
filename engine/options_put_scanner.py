import yfinance as yf
import pandas as pd
from engine.options_ranker import rank_option_row
from engine.moneyness import valid_put_strike
from engine.expiry_filter import valid_expiry
from engine.options_threshold import option_passes

def safe_int(value):
    if pd.isna(value):
        return 0
    return int(value)

def get_best_put(symbol):
    try:
        ticker = yf.Ticker(symbol)
        expirations = ticker.options
    except Exception:
        return None

    if not expirations:
        return None

    best_option = None
    best_score = -1

    hist = yf.download(symbol, period="5d", auto_adjust=True, progress=False)
    if hist.empty:
        return None

    stock_price = float(hist["Close"].iloc[-1].item())

    for expiry in expirations[:4]:
        if not valid_expiry(expiry):
            continue

        try:
            chain = ticker.option_chain(expiry)
            puts = chain.puts
        except Exception:
            continue

        if puts.empty:
            continue

        for _, row in puts.iterrows():
            strike = float(row["strike"])

            if not valid_put_strike(stock_price, strike):
                continue

            score = rank_option_row(row, stock_price)

            if score > best_score and option_passes(score):
                best_score = score
                best_option = {
                    "symbol": symbol,
                    "strike": strike,
                    "expiry": expiry,
                    "volume": safe_int(row.get("volume", 0)),
                    "openInterest": safe_int(row.get("openInterest", 0)),
                    "score": score,
                    "type": "PUT"
                }

    return best_option
