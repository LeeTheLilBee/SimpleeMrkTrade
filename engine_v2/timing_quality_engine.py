from typing import Dict


def score_timing_quality(timeline: Dict, execution: Dict) -> Dict:
    phase = timeline.get("timeline_phase")
    entry = execution.get("entry_state")

    score = 50

    if phase == "ready" and entry == "clean":
        score = 90
    elif phase == "building":
        score = 65
    elif phase == "early":
        score = 40
    elif phase == "expanding":
        score = 30
    elif phase == "exhausting":
        score = 25
    elif phase == "broken":
        score = 10

    return {
        "timing_quality_score": score
    }
