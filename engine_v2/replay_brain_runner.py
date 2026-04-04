from typing import Dict

from engine_v2.final_master_brain_engine import build_final_master_brain


def build_replay_final_brain(decision_bundle: Dict) -> Dict:
    if not isinstance(decision_bundle, dict):
        decision_bundle = {}

    return build_final_master_brain(
        base_decision=decision_bundle.get("base_decision", {}) if isinstance(decision_bundle.get("base_decision", {}), dict) else {},
        base_explainability=decision_bundle.get("explainability", {}) if isinstance(decision_bundle.get("explainability", {}), dict) else {},
        enhanced_integration=decision_bundle.get("enhanced", {}) if isinstance(decision_bundle.get("enhanced", {}), dict) else {},
        truth_integration=decision_bundle.get("truth", {}) if isinstance(decision_bundle.get("truth", {}), dict) else {},
        behavior_intelligence=decision_bundle.get("behavior", {}) if isinstance(decision_bundle.get("behavior", {}), dict) else {},
        causality_intelligence=decision_bundle.get("causality", {}) if isinstance(decision_bundle.get("causality", {}), dict) else {},
        counterfactual_intelligence=decision_bundle.get("counterfactual", {}) if isinstance(decision_bundle.get("counterfactual", {}), dict) else {},
    )
