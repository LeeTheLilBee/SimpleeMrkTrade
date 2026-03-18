from engine.performance_tracker import performance_summary

def drawdown_brake():
    perf = performance_summary()
    dd = perf.get("max_drawdown", 0)

    if dd >= 200:
        return {
            "blocked": True,
            "reason": "hard_drawdown_brake"
        }

    if dd >= 100:
        return {
            "blocked": False,
            "reason": "reduced_risk_mode"
        }

    return {
        "blocked": False,
        "reason": "normal"
    }
