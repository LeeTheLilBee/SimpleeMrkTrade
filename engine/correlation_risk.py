from engine.paper_portfolio import show_positions
from engine.sector_strength import sector_bias

def correlation_risk_status():
    positions = show_positions()
    sectors = {}

    for pos in positions:
        sector = sector_bias(pos["symbol"])
        sectors[sector] = sectors.get(sector, 0) + 1

    crowded = {k: v for k, v in sectors.items() if v >= 2}

    return {
        "crowded_sectors": crowded,
        "blocked": len(crowded) > 0
    }
