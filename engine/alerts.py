def alert_trade(trade):
    print("ALERT:")
    print(
        trade["symbol"],
        "|", trade["strategy"],
        "| Score:", trade["score"],
        "| Confidence:", trade["confidence"]
    )
