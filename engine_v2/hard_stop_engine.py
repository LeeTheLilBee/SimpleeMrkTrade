from typing import Dict


def evaluate_hard_stops(system_state: Dict, portfolio_state: Dict) -> Dict:
    daily_loss = float(portfolio_state.get("daily_loss_pct", 0) or 0)
    open_positions = int(portfolio_state.get("open_positions", 0) or 0)
    max_positions = int(system_state.get("max_open_positions", 6) or 6)
    drawdown_state = str(portfolio_state.get("drawdown_state", "normal") or "normal")

    triggered = []
    blocked = False

    if daily_loss <= -3.0:
        triggered.append("max_daily_loss")
        blocked = True

    if open_positions >= max_positions:
        triggered.append("max_open_positions")
        blocked = True

    if drawdown_state == "critical":
        triggered.append("critical_drawdown")
        blocked = True

    return {
        "hard_stop_blocked": blocked,
        "hard_stop_triggers": triggered,
    }
