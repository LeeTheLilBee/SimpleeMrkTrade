def print_account_snapshot(snapshot):
    print("ACCOUNT SNAPSHOT")
    print("Cash:", snapshot["cash"])
    print("Buying Power:", snapshot["buying_power"])
    print("Equity:", snapshot["equity"])
    print("Open Positions:", snapshot["open_positions"])
    print("Realized PnL:", snapshot["realized_pnl"])
    print("Unrealized PnL:", snapshot["unrealized_pnl"])
    print("Estimated Account Value:", snapshot["estimated_account_value"])
