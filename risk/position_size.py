from engine.account_state import load_state

def position_size(price, atr=None):
    state = load_state()
    equity = float(state.get("equity", 1000))

    risk_budget = equity * 0.01

    if atr is not None and atr > 0:
        size = int(risk_budget / atr)
    else:
        size = int(risk_budget / price)

    return max(1, size)
