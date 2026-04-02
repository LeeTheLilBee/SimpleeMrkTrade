from typing import Dict, List


def build_entry_queue(decisions: List[Dict]) -> Dict:
    valid = [d for d in decisions if isinstance(d, dict) and d.get("ready_state") in {"ready_now", "ready_soon"}]

    ranked = sorted(
        valid,
        key=lambda d: (
            d.get("ready_state") == "ready_now",
            d.get("edge_score", 0),
            d.get("timing_quality_score", d.get("timing_score", 0)),
        ),
        reverse=True,
    )

    queue = []
    for i, trade in enumerate(ranked):
        if i == 0:
            queue_state = "first"
        elif i == 1:
            queue_state = "second"
        else:
            queue_state = "deferred"

        queue.append({
            "symbol": trade.get("symbol"),
            "queue_state": queue_state,
            "ready_state": trade.get("ready_state"),
        })

    return {
        "queue": queue
    }
