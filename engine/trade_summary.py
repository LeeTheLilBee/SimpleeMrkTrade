def trade_summary(trade):
    print("-----")
    print("Symbol:", trade.get("symbol"))
    print("Strategy:", trade.get("strategy"))
    print("Score:", trade.get("score"))
    print("Confidence:", trade.get("confidence"))

    option = trade.get("option")
    if option:
        print("Option:", option)
    else:
        print("Option: NONE (stock-only trade)")
