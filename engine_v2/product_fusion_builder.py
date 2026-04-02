from typing import Dict

from engine_v2.intelligence_fusion_engine import build_intelligence_fusion


def build_product_fusion_payload(
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
    fusion = build_intelligence_fusion(
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
    )

    master = fusion.get("master_decision", {})
    summary = fusion.get("summary", {})
    command = fusion.get("command_object", {})

    return {
        "fusion": fusion,
        "master_decision": master,
        "fusion_summary": summary.get("fusion_summary", ""),
        "command_object": command,
        "final_state": master.get("final_state", "unknown"),
        "blocked": command.get("blocked", False),
        "command": command.get("command", "stand_down"),
        "threat_level": command.get("threat_level", "low"),
        "timeline_phase": command.get("timeline_phase", "unknown"),
        "next_action": command.get("next_action", "wait"),
    }
