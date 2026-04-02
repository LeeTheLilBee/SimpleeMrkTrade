from typing import Dict

from engine_v2.event_risk_engine import evaluate_event_risk
from engine_v2.headline_risk_engine import evaluate_headline_risk
from engine_v2.fragility_engine import evaluate_fragility
from engine_v2.false_calm_engine import detect_false_calm
from engine_v2.market_deception_engine import detect_market_deception
from engine_v2.threat_score_engine import build_threat_score


def build_threat_intelligence(signal: Dict, decision: Dict, regime: Dict, context: Dict) -> Dict:
    event_risk = evaluate_event_risk(signal, context)
    headline_risk = evaluate_headline_risk(signal, context)
    fragility = evaluate_fragility(signal, decision, regime)
    false_calm = detect_false_calm(signal, context)
    market_deception = detect_market_deception(signal, regime, context)
    threat_score = build_threat_score(
        event_risk=event_risk,
        headline_risk=headline_risk,
        fragility=fragility,
        false_calm=false_calm,
        market_deception=market_deception,
    )

    return {
        "event_risk": event_risk,
        "headline_risk": headline_risk,
        "fragility": fragility,
        "false_calm": false_calm,
        "market_deception": market_deception,
        "threat_score": threat_score,
    }
