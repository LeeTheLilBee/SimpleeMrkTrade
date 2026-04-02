from typing import List, Dict


def evaluate_displacement(ranked: List[Dict]) -> Dict:
    if len(ranked) < 2:
        return {"displacement": "none", "reason": "not enough trades to compare"}

    top = ranked[0]
    second = ranked[1]

    if top.get("total_score", 0) - second.get("total_score", 0) > 25:
        return {
            "displacement": "strong",
            "reason": f"{top['symbol']} clearly outclasses alternatives",
        }

    return {
        "displacement": "moderate",
        "reason": "multiple trades are competing closely",
    }
