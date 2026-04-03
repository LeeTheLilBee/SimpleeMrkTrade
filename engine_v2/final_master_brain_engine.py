from typing import Dict

from engine_v2.final_action_hierarchy_engine import resolve_final_action
from engine_v2.final_confidence_hierarchy_engine import resolve_final_confidence
from engine_v2.final_narrative_merge_engine import build_final_narrative
from engine_v2.final_coaching_merge_engine import build_final_coaching
from engine_v2.final_output_packaging_engine import build_final_master_output


def build_final_master_brain(
    base_decision: Dict,
    base_explainability: Dict,
    enhanced_integration: Dict,
    truth_integration: Dict,
    behavior_intelligence: Dict,
    causality_intelligence: Dict,
    counterfactual_intelligence: Dict,
) -> Dict:
    final_action_resolution = resolve_final_action(
        base_decision=base_decision,
        enhanced_integration=enhanced_integration,
        truth_integration=truth_integration,
        behavior_intelligence=behavior_intelligence,
    )

    final_confidence_resolution = resolve_final_confidence(
        base_decision=base_decision,
        enhanced_integration=enhanced_integration,
        truth_integration=truth_integration,
        behavior_intelligence=behavior_intelligence,
    )

    final_narrative = build_final_narrative(
        base_explainability=base_explainability,
        enhanced_integration=enhanced_integration,
        truth_integration=truth_integration,
        causality_intelligence=causality_intelligence,
        counterfactual_intelligence=counterfactual_intelligence,
    )

    final_coaching = build_final_coaching(
        behavior_intelligence=behavior_intelligence,
        final_action_resolution=final_action_resolution,
        final_confidence_resolution=final_confidence_resolution,
    )

    final_output = build_final_master_output(
        final_action_resolution=final_action_resolution,
        final_confidence_resolution=final_confidence_resolution,
        final_narrative=final_narrative,
        final_coaching=final_coaching,
        truth_integration=truth_integration,
        behavior_intelligence=behavior_intelligence,
        causality_intelligence=causality_intelligence,
        counterfactual_intelligence=counterfactual_intelligence,
    )

    return {
        "final_action_resolution": final_action_resolution,
        "final_confidence_resolution": final_confidence_resolution,
        "final_narrative": final_narrative,
        "final_coaching": final_coaching,
        "final_output": final_output,
    }
