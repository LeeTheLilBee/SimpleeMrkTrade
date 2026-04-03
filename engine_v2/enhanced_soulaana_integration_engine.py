from typing import Dict

from engine_v2.enhanced_soulaana_state_engine import build_enhanced_soulaana_state
from engine_v2.enhanced_soulaana_voice_engine import build_enhanced_soulaana_voice
from engine_v2.enhanced_master_override_engine import apply_enhanced_master_override
from engine_v2.enhanced_decision_packaging_engine import build_enhanced_decision_package


def build_enhanced_soulaana_integration(
    base_soulaana: Dict,
    base_action: str,
    base_confidence: str,
    fusion_adjustments: Dict,
) -> Dict:
    enhanced_state = build_enhanced_soulaana_state(
        base_soulaana=base_soulaana,
        enhanced_edge_quality=fusion_adjustments.get("enhanced_edge_quality", {}),
        enhanced_clarity=fusion_adjustments.get("enhanced_clarity", {}),
        deception_penalty=fusion_adjustments.get("deception_penalty", {}),
        memory_adjustment=fusion_adjustments.get("memory_adjustment", {}),
        intent_adjustment=fusion_adjustments.get("intent_adjustment", {}),
    )

    enhanced_voice = build_enhanced_soulaana_voice(
        enhanced_state=enhanced_state,
        deception_penalty=fusion_adjustments.get("deception_penalty", {}),
        memory_adjustment=fusion_adjustments.get("memory_adjustment", {}),
        intent_adjustment=fusion_adjustments.get("intent_adjustment", {}),
    )

    override = apply_enhanced_master_override(
        base_action=base_action,
        base_confidence=base_confidence,
        enhanced_state=enhanced_state,
    )

    package = build_enhanced_decision_package(
        enhanced_state=enhanced_state,
        enhanced_voice=enhanced_voice,
        override=override,
        fusion_adjustments=fusion_adjustments,
    )

    return {
        "enhanced_state": enhanced_state,
        "enhanced_voice": enhanced_voice,
        "enhanced_override": override,
        "enhanced_package": package,
    }
