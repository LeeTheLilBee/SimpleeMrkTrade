from typing import Dict


def build_stagger_plan(entry_queue: Dict) -> Dict:
    queue = entry_queue.get("queue", [])

    if not queue:
        return {
            "stagger_mode": "hold_back",
            "stagger_reason": "no actionable entries",
        }

    if len(queue) == 1:
        return {
            "stagger_mode": "immediate",
            "stagger_reason": "single dominant opportunity",
        }

    first = queue[0]
    second = queue[1] if len(queue) > 1 else None

    if first.get("queue_state") == "first" and second:
        return {
            "stagger_mode": "staged",
            "stagger_reason": "multiple opportunities exist, but capital should deploy in sequence",
        }

    return {
        "stagger_mode": "hold_back",
        "stagger_reason": "queue lacks enough separation for clean staging",
    }
