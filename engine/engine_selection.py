"""
ENGINE SELECTION SYSTEM
"""

from typing import Dict, List


def normalize_market_regime(system_state: Dict) -> str:
    regime = str(system_state.get("regime", "Neutral")).strip().lower()

    if regime in {"bull", "risk-on", "strong", "trend"}:
        return "strong"
    if regime in {"weak", "risk-off", "defensive", "bear"}:
        return "weak"
    return "neutral"


def normalize_volatility(system_state: Dict) -> str:
    vol = str(system_state.get("volatility", "Normal")).strip().lower()

    if vol in {"high", "elevated", "volatile"}:
        return "high"
    if vol in {"low", "calm"}:
        return "low"
    return "normal"


def score_signal_quality(signal: Dict) -> int:
    score = int(signal.get("score", signal.get("latest_score", 0)) or 0)
    confidence = str(signal.get("confidence", signal.get("latest_confidence", "LOW"))).upper()
    setup_type = str(signal.get("setup_type", "Continuation")).title()

    quality = score

    if confidence == "HIGH":
        quality += 15
    elif confidence == "MEDIUM":
        quality += 7

    if setup_type == "Breakout":
        quality += 8
    elif setup_type == "Continuation":
        quality += 5
    elif setup_type == "Pullback":
        quality += 3

    return quality


def passes_trade_gate(signal: Dict, system_state: Dict) -> bool:
    regime = normalize_market_regime(system_state)
    volatility = normalize_volatility(system_state)

    raw_score = int(signal.get("score", signal.get("latest_score", 0)) or 0)
    confidence = str(signal.get("confidence", signal.get("latest_confidence", "LOW"))).upper()

    min_score = 70

    if regime == "weak":
        min_score += 15
    elif regime == "neutral":
        min_score += 5

    if volatility == "high":
        min_score += 10

    if raw_score < min_score:
        return False

    if regime == "weak" and confidence == "LOW":
        return False

    return True


def max_active_candidates(system_state: Dict) -> int:
    regime = normalize_market_regime(system_state)
    volatility = normalize_volatility(system_state)

    if regime == "strong" and volatility in {"low", "normal"}:
        return 15
    if regime == "strong" and volatility == "high":
        return 10
    if regime == "neutral" and volatility == "normal":
        return 8
    if regime == "neutral" and volatility == "high":
        return 6
    if regime == "weak":
        return 4

    return 6


def build_execution_universe(signals: List[Dict], system_state: Dict) -> Dict:
    ranked = []

    for signal in signals:
        quality = score_signal_quality(signal)
        signal_copy = dict(signal)
        signal_copy["execution_quality"] = quality
        signal_copy["eligible"] = passes_trade_gate(signal_copy, system_state)
        ranked.append(signal_copy)

    ranked.sort(key=lambda x: x.get("execution_quality", 0), reverse=True)

    eligible = [s for s in ranked if s.get("eligible")]
    rejected = [s for s in ranked if not s.get("eligible")]

    cap = max_active_candidates(system_state)
    selected = eligible[:cap]

    return {
        "selected": selected,
        "eligible_count": len(eligible),
        "rejected_count": len(rejected),
        "cap": cap,
        "regime": normalize_market_regime(system_state),
        "volatility": normalize_volatility(system_state),
    }


def build_execution_summary(universe: Dict) -> Dict:
    selected = universe.get("selected", [])
    return {
        "selected_symbols": [s.get("symbol") for s in selected],
        "selected_count": len(selected),
        "eligible_count": universe.get("eligible_count", 0),
        "rejected_count": universe.get("rejected_count", 0),
        "cap": universe.get("cap", 0),
        "regime": universe.get("regime", "neutral"),
        "volatility": universe.get("volatility", "normal"),
    }
