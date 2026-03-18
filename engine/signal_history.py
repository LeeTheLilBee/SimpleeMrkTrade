signal_history = []

def remember_signal(symbol, score, strategy):
    signal_history.append({
        "symbol": symbol,
        "score": score,
        "strategy": strategy
    })

def get_signal_history():
    return signal_history
