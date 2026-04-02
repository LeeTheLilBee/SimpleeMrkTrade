from typing import Dict


def evaluate_setup_family_health(setup_stats: Dict) -> Dict:
    families = setup_stats.get("families", {}) if isinstance(setup_stats, dict) else {}

    family_health = {}
    weakest_family = None
    weakest_score = -1.0

    for name, stats in families.items():
        win_rate = float(stats.get("win_rate", 0))
        count = int(stats.get("count", 0))

        if count < 3:
            state = "unknown"
            score = 50.0
        elif win_rate >= 0.55:
            state = "healthy"
            score = 15.0
        elif win_rate >= 0.45:
            state = "mixed"
            score = 50.0
        elif win_rate >= 0.35:
            state = "weak"
            score = 75.0
        else:
            state = "failing"
            score = 90.0

        family_health[name] = {
            "state": state,
            "health_score": score,
            "win_rate": round(win_rate, 4),
            "count": count,
        }

        if score > weakest_score:
            weakest_score = score
            weakest_family = name

    return {
        "families": family_health,
        "weakest_family": weakest_family,
    }
