from typing import List, Dict


def assign_capital_priority(ranked: List[Dict]) -> Dict:
    priorities = []

    for r in ranked:
        rank = r.get("priority_rank")

        if rank == 1:
            tier = "dominant"
        elif rank <= 3:
            tier = "competitive"
        elif rank <= 5:
            tier = "secondary"
        else:
            tier = "avoid"

        priorities.append({
            "symbol": r.get("symbol"),
            "priority": tier,
        })

    return {"priorities": priorities}
