from typing import Dict, List

from engine_v2.decision_engine import build_decision
from engine_v2.execution_engine import build_execution_profile
from engine_v2.learning_engine import process_trade_result
from engine_v2.experience_engine import build_experience
from engine_v2.meta_intelligence_engine import build_meta_intelligence
from engine_v2.portfolio_intelligence_engine import build_portfolio_intelligence
from engine_v2.market_regime_engine import detect_market_regime
from engine_v2.autonomous_evolution_engine import build_autonomous_evolution
from engine_v2.thesis_engine import build_thesis_intelligence
from engine_v2.timeline_integration_engine import build_timeline_intelligence
from engine_v2.multi_trade_coordination_engine import build_multi_trade_coordination
from engine_v2.threat_intelligence_engine import build_threat_intelligence
from engine_v2.opportunity_cost_engine import build_opportunity_cost_intelligence
from engine_v2.system_governance_engine import build_system_governance


def build_fusion_inputs(
    signal: Dict,
    user_data: Dict,
    market_data: Dict,
    portfolio_positions: List[Dict],
    trade_results: List[Dict],
    setup_stats: Dict,
    context: Dict,
    system_state: Dict,
    portfolio_state: Dict,
    tier: str,
) -> Dict:
    decision = build_decision(signal)
    execution = build_execution_profile(signal, decision)
    learning = process_trade_result({
        "symbol": signal.get("symbol"),
        "pnl": float(signal.get("last_pnl", 0) or 0),
        "timing_score": decision.get("timing_score", 0),
        "structure_choice": execution.get("structure_choice", "watch_only"),
        "entry_state": execution.get("entry_state", "wait"),
        "edge_score": decision.get("edge_score", 0),
    })

    experience = build_experience(signal, decision, execution, user_data, tier)
    regime = detect_market_regime(market_data)
    thesis = build_thesis_intelligence(signal, decision, execution)
    timeline = build_timeline_intelligence(signal, decision, execution)
    threat = build_threat_intelligence(signal, decision, regime, context)

    portfolio = build_portfolio_intelligence(portfolio_positions, {
        **decision,
        "direction": signal.get("direction"),
        "correlation_cluster": decision.get("correlation_cluster"),
    })

    decisions_for_ranking = [{
        "symbol": signal.get("symbol"),
        "edge_score": decision.get("edge_score", 0),
        "timing_quality_score": timeline.get("timing_quality_score", decision.get("timing_score", 0)),
        "thesis_quality": thesis.get("thesis_quality", {}).get("thesis_quality", "moderate"),
        "portfolio_fit": portfolio.get("contribution", {}).get("contribution", "neutral"),
        "threat_level": threat.get("threat_score", {}).get("threat_level", "low"),
        "ready_state": decision.get("ready_state", "watch"),
    }]
    opportunity = build_opportunity_cost_intelligence(decisions_for_ranking)

    meta = build_meta_intelligence(trade_results, decisions_for_ranking, setup_stats)
    evolution = build_autonomous_evolution(meta, regime)
    coordination = build_multi_trade_coordination(decisions_for_ranking)

    governance = build_system_governance(
        system_state=system_state,
        portfolio_state=portfolio_state,
        decision_context={
            "requested_action": experience.get("next_action", "wait"),
            "decision_ready": decision.get("ready_state") == "ready_now",
            "capital_action": "deploy" if decision.get("ready_state") == "ready_now" else "hold",
            "blocked_by_governance": False,
        },
    )

    return {
        "signal": signal,
        "decision": decision,
        "execution": execution,
        "learning": learning,
        "experience": experience,
        "meta": meta,
        "portfolio": portfolio,
        "regime": regime,
        "evolution": evolution,
        "thesis": thesis,
        "timeline": timeline,
        "coordination": coordination,
        "threat": threat,
        "opportunity": opportunity,
        "governance": governance,
    }
