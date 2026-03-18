from engine.data_utils import safe_download
from engine.volatility_state import save_volatility_state

def get_volatility_environment():
    vix = safe_download("^VIX", period="1mo", auto_adjust=True, progress=False)

    if vix is None or vix.empty:
        payload = {
            "volatility": "UNKNOWN",
            "vix": None
        }
        save_volatility_state(payload)
        return payload

    vix_last = float(vix["Close"].iloc[-1].item())

    if vix_last >= 30:
        vol = "HIGH_VOLATILITY"
    elif vix_last >= 20:
        vol = "ELEVATED"
    else:
        vol = "NORMAL"

    payload = {
        "volatility": vol,
        "vix": round(vix_last, 2)
    }

    save_volatility_state(payload)
    return payload
