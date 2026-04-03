from typing import Dict


def build_final_master_output(
    final_action_resolution: Dict,
    final_confidence_resolution: Dict,
    final_narrative: Dict,
    final_coaching: Dict,
    truth_integration: Dict,
    behavior_intelligence: Dict,
    causality_intelligence: Dict,
    counterfactual_intelligence: Dict,
) -> Dict:
    return {
        "final_summary": {
            "action": final_action_resolution.get("final_action"),
            "confidence": final_confidence_resolution.get("final_confidence"),
            "verdict": final_narrative.get("final_verdict"),
            "insight": final_narrative.get("final_insight"),
            "story": final_narrative.get("merged_story"),
            "reasons": final_narrative.get("final_reasons", []),
        },
        "final_coaching": final_coaching,
        "truth_notes": truth_integration.get("truth_package", {}).get("truth_notes", {}),
        "behavior_notes": {
            "emotional_bias": behavior_intelligence.get("emotional_bias", {}),
            "behavior_pattern": behavior_intelligence.get("behavior_pattern", {}),
            "risk_discipline": behavior_intelligence.get("risk_discipline", {}),
            "behavior_override": behavior_intelligence.get("behavior_override", {}),
        },
        "causality_notes": causality_intelligence,
        "counterfactual_notes": counterfactual_intelligence,
        "system_resolution": {
            "action_resolution": final_action_resolution,
            "confidence_resolution": final_confidence_resolution,
        },
    }
