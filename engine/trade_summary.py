from engine.flow_summary import print_flow_summary

def trade_summary(trade):
    print("-----")
    print("Symbol:", trade["symbol"])
    print("Strategy:", trade["strategy"])
    print("Score:", trade["score"])
    print("Confidence:", trade["confidence"])
    print("Option:", trade["option"])
    print_flow_summary(trade)
