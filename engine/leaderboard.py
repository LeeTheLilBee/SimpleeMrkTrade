from engine.candidate_quality import candidate_quality
from engine.liquidity_detector import liquidity_pressure

def print_leaderboard(trades):
    if not trades:
        print("No approved trades.")
        return

    ranked = sorted(trades, key=lambda x: x["score"], reverse=True)

    print("TOP CANDIDATES")
    for trade in ranked[:5]:
        grade = candidate_quality(trade["score"], trade["confidence"])
        pressure = liquidity_pressure(trade["option"]) if trade.get("option") else "NONE"

        print(
            trade["symbol"],
            "|", trade["strategy"],
            "| Score:", trade["score"],
            "| Confidence:", trade["confidence"],
            "| Grade:", grade,
            "| Flow:", pressure
        )
