from typing import Dict, Tuple
from engine_v2.soulaana_fusion_layer import build_soulaana_fusion_layer
from engine_v2.explainability_engine import build_explanation


def interpret_soulaana_state(soulaana_state: str) -> str:
    if soulaana_state == "conviction":
        return "act"
    elif soulaana_state == "valid":
        return "cautious_act"
    elif soulaana_state == "weak":
        return "wait"
    else:
        return "reject"


def apply_safety_overrides(
    action: str,
    clarity_score: float,
    contradiction_count: int,
    only_allowed: bool,
) -> Tuple[str, list]:
    flags = []

    if contradiction_count > 1:
        flags.append("high_internal_conflict")

    if clarity_score < 50:
        flags.append("low_clarity")
        if action == "act":
            action = "cautious_act"
        elif action == "cautious_act":
            action = "wait"

    if not only_allowed:
        flags.append("not_best_expression")
        if action == "act":
            action = "cautious_act"

    return action, flags


def compute_confidence(soulaana_score: float, flags: list) -> str:
    if soulaana_score >= 60:
        confidence = "high"
    elif soulaana_score >= 25:
        confidence = "medium"
    elif soulaana_score >= 0:
        confidence = "low"
    else:
        confidence = "none"

    if "high_internal_conflict" in flags:
        if confidence == "high":
            confidence = "medium"
        elif confidence == "medium":
            confidence = "low"

    if "low_clarity" in flags:
        if confidence == "high":
            confidence = "medium"

    return confidence


def compute_decision_grade(action: str, confidence: str) -> str:
    if action == "act" and confidence == "high":
        return "A"
    elif action in ["act", "cautious_act"] and confidence in ["medium", "high"]:
        return "B"
    elif action == "wait":
        return "C"
    else:
        return "F"


def build_master_decision(
    alignment: Dict,
    clarity: Dict,
    edge_quality: Dict,
    contradiction: Dict,
    capital_gate: Dict,
    late_entry: Dict,
    only_the_ones: Dict,
    cutthroat: Dict,
) -> Dict:
    soulaana = build_soulaana_fusion_layer(
        alignment=alignment,
        clarity=clarity,
        edge_quality=edge_quality,
        contradiction=contradiction,
        capital_gate=capital_gate,
        late_entry=late_entry,
        only_the_ones=only_the_ones,
        cutthroat=cutthroat,
    )

    soulaana_state = soulaana.get("soulaana_state")
    soulaana_score = soulaana.get("soulaana_score", 0)

    clarity_score = clarity.get("clarity_score", 0)
    contradiction_count = contradiction.get("contradiction_count", 0)
    only_allowed = only_the_ones.get("only_the_ones_allowed", True)

    action = interpret_soulaana_state(soulaana_state)
    action, flags = apply_safety_overrides(
        action,
        clarity_score,
        contradiction_count,
        only_allowed,
    )
    confidence = compute_confidence(soulaana_score, flags)
    decision_grade = compute_decision_grade(action, confidence)

    decision = {
        "summary": {
            "action": action,
            "confidence": confidence,
            "grade": decision_grade,
            "score": soulaana_score,
            "state": soulaana_state,
            "reasons": soulaana.get("soulaana_reasons", []),
            "verdict": soulaana.get("soulaana_verdict"),
            "command": soulaana.get("soulaana_command_phrase"),
            "tone": soulaana_state,
        },
        "card": {
            "title": soulaana.get("soulaana_verdict"),
            "subtitle": soulaana.get("soulaana_command_phrase"),
            "action": action,
            "confidence": confidence,
            "grade": decision_grade,
            "highlights": [
                "High conviction setup" if confidence == "high" else "Moderate setup",
                "Strong confidence" if confidence == "high" else "Manage risk",
                "Top tier opportunity" if decision_grade == "A" else "Conditional opportunity",
            ],
            "tone": soulaana_state,
        },
        "explanation": {
            "why": soulaana.get("soulaana_reasons", []),
            "state": soulaana_state,
            "score": soulaana_score,
        },
        "system_flags": flags,
    }

    decision["explainability"] = build_explanation(decision)

    return decision
