from engine.paper_portfolio import show_positions
from engine.sector_strength import sector_bias

def sector_concentration_status(max_per_sector=2):
    positions = show_positions()
    sector_counts = {}

    for pos in positions:
        symbol = pos.get("symbol")
        sector = sector_bias(symbol)
        sector_counts[sector] = sector_counts.get(sector, 0) + 1

    crowded = {sector: count for sector, count in sector_counts.items() if count > max_per_sector}

    return {
        "blocked": len(crowded) > 0,
        "sector_counts": sector_counts,
        "reason": "Sector concentration too high." if crowded else "Sector concentration within limits."
    }
