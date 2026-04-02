from typing import Dict, List

from engine_v2.entry_queue_engine import build_entry_queue
from engine_v2.stagger_engine import build_stagger_plan
from engine_v2.competition_engine import evaluate_trade_competition
from engine_v2.scale_logic_engine import build_scale_logic


def build_multi_trade_coordination(decisions: List[Dict]) -> Dict:
    competition = evaluate_trade_competition(decisions)
    entry_queue = build_entry_queue(decisions)
    stagger_plan = build_stagger_plan(entry_queue)
    scale_logic = build_scale_logic(entry_queue)

    return {
        "competition": competition,
        "entry_queue": entry_queue,
        "stagger_plan": stagger_plan,
        "scale_logic": scale_logic,
    }
