def trade_summary(trade):
    print("-----")
    print("Symbol:", trade["symbol"])
    print("Strategy:", trade["strategy"])
    print("Score:", trade["score"])
    print("Confidence:", trade["confidence"])

    option = trade.get("option")

    if option:
        print(
            "Option:",
            option.get("type"),
            "| Strike:", option.get("strike"),
            "| Expiry:", option.get("expiry"),
        )

        print(
            "Contract Score:",
            trade.get("option_contract_score", "N/A")
        )

        # Step 6: option explanation (WHY this contract)
        explanation = trade.get("option_explanation")
        if explanation:
            print("Why this contract:")
            if isinstance(explanation, list):
                for line in explanation:
                    print(" -", line)
            else:
                print(" -", explanation)

        # Optional: quick liquidity / quality flags
        volume = option.get("volume", 0)
        oi = option.get("openInterest", 0)

        print(
            "Liquidity:",
            f"Vol {volume} | OI {oi}"
        )

    else:
        print("Option: NONE (stock-only trade)")
