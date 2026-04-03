from typing import Dict, List

from engine_v2.memory_engine import build_memory_snapshot
from engine_v2.pattern_reputation_engine import build_pattern_reputation
from engine_v2.setup_family_trust_engine import evaluate_setup_family_trust
from engine_v2.recent_behavior_weight_engine import build_recent_behavior_weight
from engine_v2.regime_memory_engine import evaluate_regime_memory


def build_memory_intelligence(
    signal: Dict,
    trade_results: List[Dict],
    setup_stats: Dict,
    regime: Dict,
) -> Dict:
    setup_type = str(signal.get("setup_type", "unknown") or "unknown")

    memory = build_memory_snapshot(trade_results)
    pattern_reputation = build_pattern_reputation(setup_stats)
    family_trust = evaluate_setup_family_trust(setup_type, pattern_reputation)
    recent_behavior = build_recent_behavior_weight(trade_results)
    regime_memory = evaluate_regime_memory(setup_type, regime, setup_stats)

    composite_trust = (
        family_trust.get("trust_score", 50)
        + recent_behavior.get("behavior_weight_adjustment", 0)
        + regime_memory.get("regime_memory_adjustment", 0)
    )

    if composite_trust >= 80:
        composite_state = "reinforced"
    elif composite_trust >= 55:
        composite_state = "stable"
    elif composite_trust >= 35:
        composite_state = "fragile"
    else:
        composite_state = "degraded"

    return {
        "memory": memory,
        "pattern_reputation": pattern_reputation,
        "family_trust": family_trust,
        "recent_behavior": recent_behavior,
        "regime_memory": regime_memory,
        "composite_trust_score": round(composite_trust, 2),
        "composite_trust_state": composite_state,
    }
