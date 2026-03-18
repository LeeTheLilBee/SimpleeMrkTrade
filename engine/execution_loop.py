from engine.account_state import record_trade, buying_power
from engine.paper_portfolio import add_position
from engine.trade_summary import trade_summary
from engine.trade_logger import log_trade_open
from risk.position_size import position_size
from risk.risk_manager import stop_loss_price, take_profit_price

def execute_trades(queue, limit=3):
    executed = 0

    for trade in queue:
        if executed >= limit:
            break

        symbol = trade["symbol"]
        strategy = trade["strategy"]
        price = trade["price"]
        score = trade["score"]
        confidence = trade["confidence"]
        atr = trade["atr"]

        size = position_size(price, atr=atr)
        cost = price * size

        if cost > buying_power():
            print("SKIPPED:", symbol, "| Not enough buying power")
            continue

        stop_price = stop_loss_price(price, atr=atr)
        target_price = take_profit_price(price, atr=atr)

        print("EXECUTING TRADE:", symbol)
        print("Strategy:", strategy)
        print("Price:", round(price, 2))
        print("Size:", size)
        print("Stop:", round(stop_price, 2))
        print("Target:", round(target_price, 2))

        record_trade(symbol, price, size)
        add_position(trade)
        log_trade_open(symbol, strategy, price, size, score, confidence)
        trade_summary(trade)

        executed += 1
