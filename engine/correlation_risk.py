from engine.paper_portfolio import show_positions
from engine.sector_strength import sector_bias

def correlation_risk_status():
    positions = show_positions()
    sector_counts = {}

    for pos in positions:
        symbol = pos.get("symbol")
        sector = sector_bias(symbol)
        sector_counts[sector] = sector_counts.get(sector, 0) + 1

    crowded = {sector: count for sector, count in sector_counts.items() if count >= 2}

    return {
        "blocked": len(crowded) > 0,
        "crowded_sectors": crowded,
        "reason": "Too many positions concentrated in one sector." if crowded else "Sector exposure balanced."
    }
