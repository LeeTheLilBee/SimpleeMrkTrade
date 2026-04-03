from typing import Dict, List

from engine_v2.alignment_engine import evaluate_alignment
from engine_v2.opportunity_decay_engine import evaluate_opportunity_decay
from engine_v2.contradiction_engine import detect_contradictions
from engine_v2.edge_quality_engine import evaluate_edge_quality
from engine_v2.clarity_engine import evaluate_clarity
from engine_v2.cross_symbol_engine import evaluate_cross_symbol_strength
from engine_v2.best_in_cluster_engine import select_best_in_cluster
from engine_v2.capital_gatekeeper_engine import evaluate_capital_gatekeeper
from engine_v2.late_entry_killer_engine import evaluate_late_entry_killer
from engine_v2.only_the_ones_engine import filter_only_the_ones
from engine_v2.soulaana_voice_engine import build_soulaana_voice


def build_soulaana_brain(
    signal: Dict,
    decision: Dict,
    execution: Dict,
    regime: Dict,
    thesis: Dict,
    timeline: Dict,
    threat: Dict,
    opportunities: List[Dict],
) -> Dict:
    alignment = evaluate_alignment(
        decision=decision,
        execution=execution,
        regime=regime,
        thesis=thesis,
        timeline=timeline,
        threat=threat,
    )

    decay = evaluate_opportunity_decay(
        signal=signal,
        execution=execution,
        timeline=timeline,
        threat=threat,
    )

    contradiction = detect_contradictions(
        decision=decision,
        execution=execution,
        alignment=alignment,
        thesis=thesis,
        timeline=timeline,
        threat=threat,
        decay=decay,
        regime=regime,
    )

    edge_quality = evaluate_edge_quality(
        decision=decision,
        alignment=alignment,
        timeline=timeline,
        thesis=thesis,
        threat=threat,
        decay=decay,
    )

    clarity = evaluate_clarity(
        alignment=alignment,
        thesis=thesis,
        contradiction=contradiction,
        threat=threat,
        edge_quality=edge_quality,
    )

    enriched_opportunities = []
    for item in opportunities:
        if not isinstance(item, dict):
            continue
        enriched = dict(item)
        if "edge_quality_score" not in enriched:
            enriched["edge_quality_score"] = enriched.get("edge_score", 0)
        enriched_opportunities.append(enriched)

    current_symbol = signal.get("symbol")

    if current_symbol and not any(o.get("symbol") == current_symbol for o in enriched_opportunities):
        enriched_opportunities.append({
            "symbol": current_symbol,
            "edge_quality_score": edge_quality.get("edge_quality_score", 0),
            "edge_score": decision.get("edge_score", 0),
            "correlation_cluster": decision.get("correlation_cluster"),
        })

    cross_symbol = evaluate_cross_symbol_strength(current_symbol, enriched_opportunities)
    best_in_cluster = select_best_in_cluster(current_symbol, enriched_opportunities)

    capital_gate = evaluate_capital_gatekeeper(
        edge_quality=edge_quality,
        clarity=clarity,
        contradiction=contradiction,
        decay=decay,
        threat=threat,
    )

    late_entry = evaluate_late_entry_killer(
        execution=execution,
        decay=decay,
        timeline=timeline,
    )

    only_the_ones = filter_only_the_ones(enriched_opportunities)

    voice = build_soulaana_voice(
        alignment=alignment,
        clarity=clarity,
        contradiction=contradiction,
        decay=decay,
        edge_quality=edge_quality,
        capital_gate=capital_gate,
        late_entry=late_entry,
    )

    return {
        "alignment": alignment,
        "decay": decay,
        "contradiction": contradiction,
        "edge_quality": edge_quality,
        "clarity": clarity,
        "cross_symbol": cross_symbol,
        "best_in_cluster": best_in_cluster,
        "capital_gate": capital_gate,
        "late_entry": late_entry,
        "only_the_ones": only_the_ones,
        "voice": voice,
    }
