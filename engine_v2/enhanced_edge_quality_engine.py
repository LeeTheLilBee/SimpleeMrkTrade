from typing import Dict


def build_enhanced_edge_quality(
    edge_quality: Dict,
    deception_penalty: Dict,
    memory_adjustment: Dict,
    intent_adjustment: Dict,
) -> Dict:
    base_score = float(edge_quality.get("edge_quality_score", 0) or 0)
    base_state = str(edge_quality.get("edge_quality_state", "weak") or "weak")

    penalty = float(deception_penalty.get("deception_penalty_score", 0) or 0)
    memory_adj = float(memory_adjustment.get("memory_adjustment_score", 0) or 0)
    intent_adj = float(intent_adjustment.get("intent_adjustment_score", 0) or 0)

    final_score = base_score - penalty + memory_adj + intent_adj

    if final_score >= 85:
        state = "elite"
    elif final_score >= 70:
        state = "strong"
    elif final_score >= 55:
        state = "usable"
    elif final_score >= 40:
        state = "marginal"
    else:
        state = "weak"

    return {
        "base_edge_quality_state": base_state,
        "base_edge_quality_score": round(base_score, 2),
        "enhanced_edge_quality_state": state,
        "enhanced_edge_quality_score": round(final_score, 2),
    }
