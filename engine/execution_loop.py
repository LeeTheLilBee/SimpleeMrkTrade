from datetime import datetime

from engine.data_utils import get_live_price
from engine.account_state import record_trade, buying_power
from engine.paper_portfolio import add_position, get_position
from engine.paper_broker import place_order
from engine.trade_summary import trade_summary
from engine.trade_logger import log_trade_open
from engine.trade_timeline import add_timeline_event
from engine.bot_logger import log_bot
from risk.position_size import position_size
from risk.risk_manager import stop_loss_price, take_profit_price


def execute_trades(queue, limit=3):
    executed = 0

    for trade in queue:
        if executed >= limit:
            break

        try:
            symbol = trade["symbol"]
            strategy = trade["strategy"]
            requested_price = get_live_price(symbol) or float(trade["price"])
            score = trade["score"]
            confidence = trade["confidence"]
            atr = float(trade["atr"])

            trade.setdefault("option", None)
            trade.setdefault("sector", "UNKNOWN")
            trade.setdefault("company_name", trade.get("symbol"))       

            # prevent duplicate open position in same symbol
            existing = get_position(symbol)
            if existing:
                print("SKIPPED:", symbol, "| Existing open position")
                log_bot(f"Skipped {symbol} due to existing open position", "WARN")
                add_timeline_event(symbol, "SKIPPED", {"reason": "existing_open_position"})
                continue

            preliminary_size = position_size(requested_price, atr=atr)
            max_affordable_size = int((buying_power() - 1) // max(requested_price, 0.01))
            size = min(int(preliminary_size), max_affordable_size)

            if size < 1:
                print("SKIPPED:", symbol, "| Not enough buying power for even 1 share")
                log_bot(f"Skipped {symbol} due to insufficient buying power for minimum size", "WARN")
                add_timeline_event(symbol, "SKIPPED", {"reason": "buying_power_min_size"})
                continue

            existing = get_position(symbol)
            if existing:
                print("SKIPPED:", symbol, "| Existing open position")
                log_bot(f"Skipped {symbol} due to existing open position", "WARN")
                add_timeline_event(symbol, "SKIPPED", {"reason": "existing_open_position"})
                continue

            broker_fill = place_order(
                symbol=symbol,
                strategy=strategy,
                requested_price=requested_price,
                size=size,
                order_type="market",
            )

            if broker_fill.get("status") != "FILLED":
                print("SKIPPED:", symbol, "| Broker did not fill")
                log_bot(f"Skipped {symbol} because paper broker did not fill", "WARN")
                add_timeline_event(symbol, "SKIPPED", {"reason": "not_filled"})
                continue

            fill_price = float(broker_fill["filled_price"])
            size = float(broker_fill["size"])
            commission = float(broker_fill.get("commission", 0) or 0)

            cost = round((fill_price * size) + commission, 2)

            if cost > buying_power():
                print("SKIPPED:", symbol, "| Not enough buying power")
                log_bot(f"Skipped {symbol} due to buying power", "WARN")
                add_timeline_event(symbol, "SKIPPED", {"reason": "buying_power"})
                continue

            stop_price = stop_loss_price(fill_price, atr=atr)
            target_price = take_profit_price(fill_price, atr=atr)

            print("EXECUTING TRADE:", symbol)
            print("Strategy:", strategy)
            print("Requested Price:", round(requested_price, 2))
            print("Filled Price:", round(fill_price, 2))
            print("Size:", size)
            print("Commission:", round(commission, 2))
            print("Stop:", round(stop_price, 2))
            print("Target:", round(target_price, 2))

            trade["requested_price"] = requested_price
            trade["price"] = fill_price
            trade["fill_price"] = fill_price
            trade["commission"] = commission
            trade["size"] = size
            trade["atr"] = atr
            trade["entry"] = round(fill_price, 2)
            trade["current_price"] = round(fill_price, 2)
            trade["stop"] = round(stop_price, 2)
            trade["target"] = round(target_price, 2)
            trade["opened_at"] = datetime.now().isoformat()
            trade["status"] = "OPEN"

            record_trade(symbol, fill_price, size)
            add_position(trade)
            log_trade_open(symbol, strategy, fill_price, size, score, confidence)

            add_timeline_event(symbol, "OPENED", {
                "strategy": strategy,
                "requested_price": round(requested_price, 2),
                "fill_price": round(fill_price, 2),
                "commission": round(commission, 2),
                "size": size,
                "stop": round(stop_price, 2),
                "target": round(target_price, 2),
            })

            log_bot(
                f"Executed {symbol} {strategy} at {round(fill_price, 2)} size {size}",
                "INFO"
            )
            trade_summary(trade)

            executed += 1

        except Exception as e:
            symbol = trade.get("symbol", "UNKNOWN") if isinstance(trade, dict) else "UNKNOWN"
            print(f"ERROR executing {symbol}: {e}")
            log_bot(f"Execution error for {symbol}: {e}", "ERROR")
            add_timeline_event(symbol, "EXECUTION_ERROR", {"error": str(e)})
            continue
