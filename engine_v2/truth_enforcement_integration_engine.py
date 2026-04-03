from typing import Dict

from engine_v2.hard_rejection_engine import evaluate_hard_rejection
from engine_v2.truth_enforcement_override_engine import apply_truth_enforcement_override
from engine_v2.truth_packaging_engine import build_truth_packaged_decision


def build_truth_enforcement_integration(
    enhanced_state: Dict,
    enhanced_voice: Dict,
    enhanced_override: Dict,
    fusion_adjustments: Dict,
) -> Dict:
    hard_rejection = evaluate_hard_rejection(
        enhanced_state=enhanced_state,
        enhanced_voice=enhanced_voice,
        fusion_adjustments=fusion_adjustments,
    )

    truth_override = apply_truth_enforcement_override(
        enhanced_override=enhanced_override,
        enhanced_voice=enhanced_voice,
        hard_rejection=hard_rejection,
    )

    truth_package = build_truth_packaged_decision(
        enhanced_state=enhanced_state,
        truth_override=truth_override,
        fusion_adjustments=fusion_adjustments,
        hard_rejection=hard_rejection,
    )

    return {
        "hard_rejection": hard_rejection,
        "truth_override": truth_override,
        "truth_package": truth_package,
    }
