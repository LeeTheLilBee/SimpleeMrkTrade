from typing import Dict


def map_phase_behavior(timeline: Dict) -> Dict:
    phase = timeline.get("timeline_phase")

    if phase == "early":
        return {"behavior": "observe", "behavior_reason": "too early for execution"}

    if phase == "building":
        return {"behavior": "prepare", "behavior_reason": "setup improving but not ready"}

    if phase == "ready":
        return {"behavior": "execute", "behavior_reason": "optimal entry window"}

    if phase == "expanding":
        return {"behavior": "manage", "behavior_reason": "trade in motion"}

    if phase == "exhausting":
        return {"behavior": "tighten", "behavior_reason": "risk of reversal increasing"}

    if phase == "broken":
        return {"behavior": "exit_or_ignore", "behavior_reason": "thesis invalidated"}

    return {"behavior": "neutral", "behavior_reason": "no clear phase"}
