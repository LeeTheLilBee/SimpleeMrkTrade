from typing import Dict


def build_scale_logic(entry_queue: Dict) -> Dict:
    queue = entry_queue.get("queue", [])
    if not queue:
        return {
            "scale_mode": "none",
            "scale_reason": "no queued entries",
        }

    first = queue[0]

    if first.get("queue_state") == "first" and first.get("ready_state") == "ready_now":
        return {
            "scale_mode": "partial",
            "scale_reason": "lead opportunity is valid, but phased deployment preserves flexibility",
        }

    if first.get("ready_state") == "ready_soon":
        return {
            "scale_mode": "probe",
            "scale_reason": "setup is improving, but not yet ideal for full deployment",
        }

    return {
        "scale_mode": "none",
        "scale_reason": "conditions do not justify scaling behavior",
    }
