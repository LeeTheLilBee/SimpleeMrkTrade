from typing import Dict


def build_pattern_reputation(setup_stats: Dict) -> Dict:
    families = setup_stats.get("families", {}) if isinstance(setup_stats, dict) else {}
    output = {}

    for family_name, stats in families.items():
        win_rate = float(stats.get("win_rate", 0) or 0)
        count = int(stats.get("count", 0) or 0)

        if count < 3:
            reputation = "unproven"
            reason = "not enough sample size to trust this pattern"
        elif win_rate >= 0.60:
            reputation = "trusted"
            reason = "pattern is currently performing strongly"
        elif win_rate >= 0.48:
            reputation = "usable"
            reason = "pattern remains workable, but not elite"
        elif win_rate >= 0.35:
            reputation = "weak"
            reason = "pattern is underperforming and should be treated carefully"
        else:
            reputation = "damaged"
            reason = "pattern is currently failing and should lose trust"

        output[family_name] = {
            "reputation": reputation,
            "reason": reason,
            "win_rate": round(win_rate, 4),
            "count": count,
        }

    return {
        "pattern_reputation": output
    }
