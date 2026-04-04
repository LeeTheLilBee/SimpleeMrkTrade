from typing import Dict

from engine_v2.explainability_package_engine import build_explainability_package
from engine_v2.symbol_explainability_visual_adapter import build_symbol_explainability_visuals


def build_replay_explainability(final_brain: Dict) -> Dict:
    if not isinstance(final_brain, dict):
        final_brain = {}

    explainability = build_explainability_package(final_brain)
    visuals = build_symbol_explainability_visuals(final_brain)

    return {
        "explainability": explainability,
        "visuals": visuals,
    }
