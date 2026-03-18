def print_top_candidates(trades, limit=5):
    ranked = sorted(trades, key=lambda x: x["score"], reverse=True)

    print("TOP CANDIDATES")
    if not ranked:
        print("None")
        return

    for trade in ranked[:limit]:
        print(
            trade["symbol"],
            "|", trade["strategy"],
            "| Score:", trade["score"],
            "| Confidence:", trade["confidence"]
        )
