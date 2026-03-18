from engine.sector_strength import sector_bias

def correlation_allowed(selected_trades, candidate_symbol):
    candidate_sector = sector_bias(candidate_symbol)

    sector_count = 0
    for trade in selected_trades:
        if sector_bias(trade["symbol"]) == candidate_sector:
            sector_count += 1

    return sector_count < 2
