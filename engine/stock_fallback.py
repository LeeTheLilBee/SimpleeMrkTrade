def stock_only_candidate(symbol, strategy, score, confidence):
    return {
        "symbol": symbol,
        "strategy": strategy,
        "score": score,
        "confidence": confidence,
        "type": "STOCK_ONLY_CANDIDATE"
    }
