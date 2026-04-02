from typing import Dict

from engine_v2.fusion_conflict_engine import resolve_fusion_conflicts
from engine_v2.master_decision_engine import build_master_decision
from engine_v2.fusion_summary_engine import build_fusion_summary
from engine_v2.command_object_engine import build_command_object


def build_intelligence_fusion(
    signal: Dict,
    decision: Dict,
    execution: Dict,
    learning: Dict,
    experience: Dict,
    meta: Dict,
    portfolio: Dict,
    regime: Dict,
    evolution: Dict,
    thesis: Dict,
    timeline: Dict,
    coordination: Dict,
    threat: Dict,
    opportunity: Dict,
    governance: Dict,
) -> Dict:
    conflicts = resolve_fusion_conflicts(
        decision=decision,
        execution=execution,
        portfolio=portfolio,
        regime=regime,
        threat=threat,
        opportunity=opportunity,
        governance=governance,
    )

    master_decision = build_master_decision(
        signal=signal,
        decision=decision,
        execution=execution,
        learning=learning,
        experience=experience,
        meta=meta,
        portfolio=portfolio,
        regime=regime,
        evolution=evolution,
        thesis=thesis,
        timeline=timeline,
        coordination=coordination,
        threat=threat,
        opportunity=opportunity,
        governance=governance,
        conflicts=conflicts,
    )

    summary = build_fusion_summary(master_decision)
    command_object = build_command_object(master_decision)

    return {
        "conflicts": conflicts,
        "master_decision": master_decision,
        "summary": summary,
        "command_object": command_object,
    }
