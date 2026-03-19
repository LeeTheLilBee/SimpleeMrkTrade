from engine.position_monitor import monitor_open_positions
from engine.close_trade import close_position
from engine.kill_switch import should_kill_position
from engine.live_activity import push_activity
from engine.bot_logger import log_bot

def auto_close_positions():
    positions = monitor_open_positions()
    closed = []

    for pos in positions:
        symbol = pos["symbol"]

        kill, reason = should_kill_position(pos)

        if kill:
            result = close_position(
                symbol=symbol,
                exit_price=pos["current"],
                reason=reason
            )

            if result:
                closed.append(result)

                log_bot(f"KILLED {symbol}: {reason}", "WARN")

                push_activity(
                    "KILL",
                    f"{symbol} closed early → {reason}",
                    symbol=symbol,
                    meta={
                        "score": pos.get("health_score"),
                        "warning": pos.get("warning")
                    }
                )

    return closed
