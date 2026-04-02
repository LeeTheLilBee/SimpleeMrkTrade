from typing import Dict

from engine_v2.structure_engine import choose_structure
from engine_v2.contract_quality_engine import evaluate_contract_quality
from engine_v2.entry_precision_engine import evaluate_entry_precision
from engine_v2.exit_logic_engine import build_exit_plan


def build_execution_profile(signal: Dict, decision: Dict) -> Dict:
    structure = choose_structure(signal, decision)
    contract = evaluate_contract_quality(signal)
    entry = evaluate_entry_precision(signal, decision)

    merged = {
        **decision,
        **structure,
        **contract,
        **entry,
    }

    exit_plan = build_exit_plan(signal, merged)

    return {
        **merged,
        **exit_plan,
    }
