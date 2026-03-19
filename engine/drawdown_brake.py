from engine.performance_tracker import performance_summary

def drawdown_brake():
    perf = performance_summary()
    max_drawdown = float(perf.get("max_drawdown", 0) or 0)

    if max_drawdown >= 200:
        return {
            "blocked": True,
            "mode": "HARD_BRAKE",
            "reason": "Max drawdown exceeded hard threshold."
        }

    if max_drawdown >= 100:
        return {
            "blocked": False,
            "mode": "REDUCED_RISK",
            "reason": "Drawdown elevated. Reduce aggression."
        }

    return {
        "blocked": False,
        "mode": "NORMAL",
        "reason": "Drawdown within acceptable range."
    }
