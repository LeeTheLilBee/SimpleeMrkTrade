from engine.account_state import load_state
from engine.paper_portfolio import show_positions
from engine.portfolio_summary import portfolio_summary
from engine.unrealized_pnl import unrealized_pnl

def account_snapshot():
    state = load_state()
    portfolio = portfolio_summary()
    unreal = unrealized_pnl()

    cash = float(state.get("cash", 0))
    buying_power = float(state.get("buying_power", 0))
    equity = float(state.get("equity", 0))
    open_positions = show_positions()

    estimated_account_value = equity + unreal.get("total_unrealized", 0)

    return {
        "cash": round(cash, 2),
        "buying_power": round(buying_power, 2),
        "equity": round(equity, 2),
        "open_positions": len(open_positions),
        "realized_pnl": round(portfolio.get("realized_pnl", 0), 2),
        "unrealized_pnl": round(unreal.get("total_unrealized", 0), 2),
        "estimated_account_value": round(estimated_account_value, 2)
    }
