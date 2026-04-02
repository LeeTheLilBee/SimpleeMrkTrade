from typing import Dict

from engine_v2.hard_stop_engine import evaluate_hard_stops
from engine_v2.kill_switch_engine import evaluate_kill_switch
from engine_v2.override_engine import evaluate_overrides
from engine_v2.integrity_engine import evaluate_integrity


def build_system_governance(system_state: Dict, portfolio_state: Dict, decision_context: Dict) -> Dict:
    hard_stops = evaluate_hard_stops(system_state, portfolio_state)
    kill_switch = evaluate_kill_switch(system_state, portfolio_state)
    overrides = evaluate_overrides(system_state, decision_context)
    integrity = evaluate_integrity(system_state, portfolio_state, decision_context)

    return {
        "hard_stops": hard_stops,
        "kill_switch": kill_switch,
        "overrides": overrides,
        "integrity": integrity,
    }
