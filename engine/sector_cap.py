from collections import Counter
from engine.sector_strength import sector_bias

MAX_PER_SECTOR = 1

def sector_allowed(selected_trades, symbol):
    counts = Counter(sector_bias(t["symbol"]) for t in selected_trades)
    return counts[sector_bias(symbol)] < MAX_PER_SECTOR
