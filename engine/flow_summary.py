from engine.liquidity_detector import liquidity_pressure

def print_flow_summary(trade):
    option = trade.get("option")

    if option is None:
        print("Flow: none")
        return

    pressure = liquidity_pressure(option)

    print(
        "Flow:",
        pressure,
        "| Volume:", option.get("volume", 0),
        "| OI:", option.get("openInterest", 0)
    )
