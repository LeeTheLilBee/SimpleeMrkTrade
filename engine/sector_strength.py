SECTOR_MAP = {
    "XLE": "ENERGY", "XOM": "ENERGY", "CVX": "ENERGY", "COP": "ENERGY", "EOG": "ENERGY", "OXY": "ENERGY", "VLO": "ENERGY", "MPC": "ENERGY", "PSX": "ENERGY",
    "XLK": "TECH", "NVDA": "TECH", "MSFT": "TECH", "AAPL": "TECH", "AMD": "TECH", "MU": "TECH", "SMCI": "TECH", "QQQ": "TECH", "SOXX": "TECH", "GOOGL": "TECH", "CRM": "TECH", "ORCL": "TECH", "ADBE": "TECH",
    "XLF": "FINANCIAL", "JPM": "FINANCIAL", "BAC": "FINANCIAL", "GS": "FINANCIAL", "WFC": "FINANCIAL",
    "ARKK": "GROWTH", "PLTR": "GROWTH", "COIN": "GROWTH", "ROKU": "GROWTH", "SNOW": "GROWTH", "SHOP": "GROWTH", "UBER": "GROWTH", "ABNB": "GROWTH", "NFLX": "GROWTH", "PYPL": "GROWTH"
}

def sector_bias(symbol):
    return SECTOR_MAP.get(symbol, "OTHER")
