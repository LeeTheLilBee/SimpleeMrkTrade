def build_trade_intelligence(trade):
    score = trade.get("score", 0)
    prev_score = trade.get("previous_score", score)
    confidence = trade.get("confidence", "LOW")

    # ---------------------------
    # STATUS LOGIC
    # ---------------------------
    if score >= 180:
        status = "Strong continuation structure"
        bias = "Hold / Add on strength"
    elif score >= 130:
        status = "Constructive but developing"
        bias = "Hold / Monitor closely"
    elif score >= 90:
        status = "Early or weakening structure"
        bias = "Cautious / Reduce risk"
    else:
        status = "Weak / breakdown risk"
        bias = "Exit or avoid"

    # ---------------------------
    # CHANGE DETECTION
    # ---------------------------
    if score > prev_score:
        change = "Improving structure"
    elif score < prev_score:
        change = "Deteriorating structure"
    else:
        change = "Stable structure"

    # ---------------------------
    # INTELLIGENCE OUTPUT
    # ---------------------------
    return {
        "snapshot": {
            "trade_snapshot": [
                f"Current score is {score}.",
                f"Confidence is {confidence}.",
                f"Structure is {change.lower()}."
            ],
            "signal_alignment": [
                "Trend alignment is present.",
                "Momentum behavior supports current direction.",
                "Participation is consistent with the move."
            ]
        },

        "thesis": {
            "status": status,
            "summary": "This setup reflects current structural alignment across trend, momentum, and participation."
        },

        "pressure": [
            "Momentum slowing slightly in shorter timeframes.",
            "Crowding risk may increase near resistance."
        ],

        "damage": [
            "Loss of momentum continuation would weaken structure.",
            "Failure to hold recent levels would degrade setup quality."
        ],

        "forward_paths": {
            "bull_case": [
                "Continuation with expanding momentum.",
                "Higher highs supported by participation."
            ],
            "bear_case": [
                "Loss of structure and pullback into prior range.",
                "Breakdown if key levels fail."
            ]
        },

        "invalidation": [
            "Break below key support.",
            "Sharp drop in score and confidence alignment."
        ],

        "action_bias": bias
    }


def attach_trade_intelligence(trades):
    enriched = []

    for t in trades:
        intel = build_trade_intelligence(t)
        t["intelligence"] = intel
        enriched.append(t)

    return enriched
