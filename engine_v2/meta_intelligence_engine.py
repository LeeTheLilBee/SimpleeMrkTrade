from typing import Dict, List

from engine_v2.drift_detection_engine import detect_drift
from engine_v2.confidence_honesty_engine import evaluate_confidence_honesty
from engine_v2.setup_family_health_engine import evaluate_setup_family_health
from engine_v2.signal_quality_monitor import evaluate_signal_quality
from engine_v2.adaptive_weight_engine import suggest_weight_adjustments


def build_meta_intelligence(trade_results: List[Dict], decisions: List[Dict], setup_stats: Dict) -> Dict:
    drift = detect_drift(trade_results)
    confidence = evaluate_confidence_honesty(trade_results)
    setup_health = evaluate_setup_family_health(setup_stats)
    signal_quality = evaluate_signal_quality(decisions)
    weight_adjustments = suggest_weight_adjustments(
        drift=drift,
        confidence=confidence,
        setup_health=setup_health,
        signal_quality=signal_quality,
    )

    return {
        "drift": drift,
        "confidence_honesty": confidence,
        "setup_family_health": setup_health,
        "signal_quality": signal_quality,
        "weight_adjustments": weight_adjustments,
    }
