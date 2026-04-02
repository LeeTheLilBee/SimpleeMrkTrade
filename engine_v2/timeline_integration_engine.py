from typing import Dict

from engine_v2.timeline_engine import determine_timeline_phase
from engine_v2.timeline_behavior_engine import map_phase_behavior
from engine_v2.timing_quality_engine import score_timing_quality


def build_timeline_intelligence(signal: Dict, decision: Dict, execution: Dict) -> Dict:
    timeline = determine_timeline_phase(signal, decision, execution)
    behavior = map_phase_behavior(timeline)
    timing_score = score_timing_quality(timeline, execution)

    return {
        **timeline,
        **behavior,
        **timing_score,
    }
