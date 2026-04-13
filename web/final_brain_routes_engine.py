from typing import Dict, List
from flask import session

from engine_v2.final_master_brain_engine import build_final_master_brain
from engine_v2.final_brain_live_helpers import (
    build_final_symbol_context,
    build_final_spotlight_context,
    build_final_dashboard_context,
)


def _safe_dict(value) -> Dict:
    return value if isinstance(value, dict) else {}


def _safe_list(value) -> List:
    return value if isinstance(value, list) else []


def _safe_text(value, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def get_soulaana_emotional_state_for_engine() -> str:
    try:
        return _safe_text(session.get("soulaana_emotional_state", ""), "").lower()
    except Exception:
        return ""


def build_soulaana_behavior_profile(emotional_state: str) -> Dict:
    state = _safe_text(emotional_state, "").lower()

    default_profile = {
        "emotional_state": state or "unknown",
        "state_family": "stable",
        "risk_level": "low",
        "tone_mode": "steady",
        "warning_level": "normal",
        "friction_level": "normal",
        "confirmation_requirement": "normal",
        "conviction_scrutiny": "medium",
        "agreement_requirement": 55,
        "health_requirement": 45,
        "execution_quality_requirement": 45,
        "allow_soft_entries": True,
        "allow_early_entries": True,
        "allow_countertrend_entries": True,
        "allow_manual_override": True,
        "downgrade_aggressive_actions": False,
        "prefer_wait_bias": False,
        "require_thesis_present": False,
        "require_thesis_strength": "normal",
        "cooldown_minutes": 0,
        "behavior_tags": [],
    }

    if state == "calm":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "stable",
                "risk_level": "low",
                "tone_mode": "soft",
                "warning_level": "light",
                "conviction_scrutiny": "medium",
                "behavior_tags": ["stable_state"],
            }
        )
        return profile

    if state == "focused":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "precision",
                "risk_level": "low",
                "tone_mode": "precise",
                "warning_level": "normal",
                "confirmation_requirement": "elevated",
                "conviction_scrutiny": "high",
                "agreement_requirement": 60,
                "health_requirement": 50,
                "execution_quality_requirement": 55,
                "require_thesis_present": True,
                "require_thesis_strength": "high",
                "behavior_tags": ["precision_mode", "structure_first"],
            }
        )
        return profile

    if state == "confident":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "confidence_audit",
                "risk_level": "moderate",
                "tone_mode": "challenging",
                "warning_level": "elevated",
                "friction_level": "elevated",
                "confirmation_requirement": "elevated",
                "conviction_scrutiny": "high",
                "agreement_requirement": 65,
                "health_requirement": 55,
                "execution_quality_requirement": 55,
                "require_thesis_present": True,
                "require_thesis_strength": "high",
                "downgrade_aggressive_actions": True,
                "behavior_tags": ["confidence_risk", "swagger_check"],
            }
        )
        return profile

    if state == "cautious":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "defensive",
                "risk_level": "moderate",
                "tone_mode": "protective",
                "warning_level": "elevated",
                "friction_level": "elevated",
                "confirmation_requirement": "strict",
                "conviction_scrutiny": "high",
                "agreement_requirement": 65,
                "health_requirement": 60,
                "execution_quality_requirement": 55,
                "prefer_wait_bias": True,
                "downgrade_aggressive_actions": True,
                "behavior_tags": ["defensive_mode"],
            }
        )
        return profile

    if state == "anxious":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "protective",
                "risk_level": "high",
                "tone_mode": "grounding",
                "warning_level": "high",
                "friction_level": "high",
                "confirmation_requirement": "strict",
                "conviction_scrutiny": "high",
                "agreement_requirement": 70,
                "health_requirement": 60,
                "execution_quality_requirement": 60,
                "allow_soft_entries": False,
                "prefer_wait_bias": True,
                "downgrade_aggressive_actions": True,
                "require_thesis_present": True,
                "require_thesis_strength": "high",
                "cooldown_minutes": 10,
                "behavior_tags": ["anxiety_risk", "panic_management"],
            }
        )
        return profile

    if state == "frustrated":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "high_risk_behavior",
                "risk_level": "high",
                "tone_mode": "firm",
                "warning_level": "high",
                "friction_level": "high",
                "confirmation_requirement": "strict",
                "conviction_scrutiny": "high",
                "agreement_requirement": 72,
                "health_requirement": 62,
                "execution_quality_requirement": 60,
                "allow_soft_entries": False,
                "allow_countertrend_entries": False,
                "allow_manual_override": False,
                "prefer_wait_bias": True,
                "downgrade_aggressive_actions": True,
                "require_thesis_present": True,
                "require_thesis_strength": "high",
                "cooldown_minutes": 15,
                "behavior_tags": ["frustration_risk", "revenge_risk", "force_it_risk"],
            }
        )
        return profile

    if state == "impulsive":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "restricted",
                "risk_level": "severe",
                "tone_mode": "protective",
                "warning_level": "severe",
                "friction_level": "maximum",
                "confirmation_requirement": "maximum",
                "conviction_scrutiny": "extreme",
                "agreement_requirement": 80,
                "health_requirement": 70,
                "execution_quality_requirement": 68,
                "allow_soft_entries": False,
                "allow_early_entries": False,
                "allow_countertrend_entries": False,
                "allow_manual_override": False,
                "prefer_wait_bias": True,
                "downgrade_aggressive_actions": True,
                "require_thesis_present": True,
                "require_thesis_strength": "extreme",
                "cooldown_minutes": 20,
                "behavior_tags": ["impulse_risk", "chase_risk", "early_entry_risk"],
            }
        )
        return profile

    if state == "tired":
        profile = dict(default_profile)
        profile.update(
            {
                "state_family": "fatigue",
                "risk_level": "high",
                "tone_mode": "simple_protective",
                "warning_level": "high",
                "friction_level": "high",
                "confirmation_requirement": "strict",
                "conviction_scrutiny": "high",
                "agreement_requirement": 70,
                "health_requirement": 60,
                "execution_quality_requirement": 60,
                "allow_soft_entries": False,
                "allow_early_entries": False,
                "allow_countertrend_entries": False,
                "prefer_wait_bias": True,
                "downgrade_aggressive_actions": True,
                "require_thesis_present": True,
                "require_thesis_strength": "high",
                "cooldown_minutes": 15,
                "behavior_tags": ["fatigue_risk", "slow_processing_risk"],
            }
        )
        return profile

    return default_profile


def apply_soulaana_behavior_to_decision_bundle(symbol: str, decision_bundle: Dict, behavior_profile: Dict) -> Dict:
    bundle = _safe_dict(decision_bundle).copy()

    base_decision = _safe_dict(bundle.get("base_decision")).copy()
    explainability = _safe_dict(bundle.get("explainability")).copy()
    enhanced = _safe_dict(bundle.get("enhanced")).copy()
    truth = _safe_dict(bundle.get("truth")).copy()
    behavior_intelligence = _safe_dict(bundle.get("behavior")).copy()

    original_action = _safe_text(base_decision.get("action", "wait"), "wait").lower()
    original_confidence = _safe_text(base_decision.get("confidence", "low"), "low").lower()

    adjusted_action = original_action
    adjusted_confidence = original_confidence
    intervention_reasons = []

    agreement_requirement = int(behavior_profile.get("agreement_requirement", 55) or 55)
    health_requirement = int(behavior_profile.get("health_requirement", 45) or 45)
    execution_requirement = int(behavior_profile.get("execution_quality_requirement", 45) or 45)

    behavior_intelligence["soulaana_behavior_profile"] = behavior_profile
    behavior_intelligence["soulaana_intervention_active"] = False
    behavior_intelligence["soulaana_intervention_reasons"] = []

    base_agreement = int(behavior_intelligence.get("agreement_score", 100) or 100)
    base_health = int(behavior_intelligence.get("health_score", 100) or 100)
    base_execution = int(behavior_intelligence.get("execution_quality_score", 100) or 100)

    if behavior_profile.get("prefer_wait_bias"):
        if adjusted_action in {"take", "ready", "enter", "buy"}:
            adjusted_action = "watch"
            intervention_reasons.append("Soulanna added a wait bias because current emotional state increases action risk.")

    if behavior_profile.get("downgrade_aggressive_actions"):
        if adjusted_action in {"take", "enter", "buy"} and original_confidence in {"low", "medium"}:
            adjusted_action = "watch"
            intervention_reasons.append("Aggressive action was softened because conviction is not strong enough for current behavior risk.")

    if not behavior_profile.get("allow_early_entries", True):
        if adjusted_action in {"take", "enter", "buy", "ready"}:
            adjusted_action = "watch"
            intervention_reasons.append("Early-entry style posture was blocked by Soulanna behavior protection.")

    if base_agreement < agreement_requirement:
        adjusted_action = "watch"
        intervention_reasons.append(
            f"Agreement is below the current behavior requirement ({base_agreement} < {agreement_requirement})."
        )

    if base_health < health_requirement:
        adjusted_action = "watch"
        intervention_reasons.append(
            f"Health is below the current behavior requirement ({base_health} < {health_requirement})."
        )

    if base_execution < execution_requirement:
        adjusted_action = "watch"
        intervention_reasons.append(
            f"Execution quality is below the current behavior requirement ({base_execution} < {execution_requirement})."
        )

    if behavior_profile.get("risk_level") == "severe":
        if adjusted_action in {"take", "enter", "buy", "ready"}:
            adjusted_action = "watch"
            adjusted_confidence = "low"
            intervention_reasons.append("Severe behavior-risk mode clipped aggressive action posture.")

    if intervention_reasons:
        behavior_intelligence["soulaana_intervention_active"] = True
        behavior_intelligence["soulaana_intervention_reasons"] = intervention_reasons

    base_decision["raw_action"] = original_action
    base_decision["raw_confidence"] = original_confidence
    base_decision["action"] = adjusted_action
    base_decision["confidence"] = adjusted_confidence

    explainability["soulaana_behavior_summary"] = (
        " | ".join(intervention_reasons)
        if intervention_reasons
        else "No Soulanna behavior intervention was needed."
    )

    bundle["base_decision"] = base_decision
    bundle["explainability"] = explainability
    bundle["enhanced"] = enhanced
    bundle["truth"] = truth
    bundle["behavior"] = behavior_intelligence

    return bundle


def apply_soulaana_behavior_to_final_brain(final_brain: Dict, behavior_profile: Dict) -> Dict:
    brain = _safe_dict(final_brain).copy()

    if not brain:
        return brain

    intervention = {
        "emotional_state": behavior_profile.get("emotional_state", "unknown"),
        "state_family": behavior_profile.get("state_family", "stable"),
        "risk_level": behavior_profile.get("risk_level", "low"),
        "tone_mode": behavior_profile.get("tone_mode", "steady"),
        "warning_level": behavior_profile.get("warning_level", "normal"),
        "friction_level": behavior_profile.get("friction_level", "normal"),
    }

    brain["soulaana_behavior"] = intervention

    behavior_intelligence = _safe_dict(brain.get("behavior_intelligence"))
    if behavior_intelligence:
        brain["soulaana_behavior"]["intervention_active"] = bool(
            behavior_intelligence.get("soulaana_intervention_active", False)
        )
        brain["soulaana_behavior"]["intervention_reasons"] = _safe_list(
            behavior_intelligence.get("soulaana_intervention_reasons", [])
        )
    else:
        brain["soulaana_behavior"]["intervention_active"] = False
        brain["soulaana_behavior"]["intervention_reasons"] = []

    return brain


def build_symbol_final_brain(symbol: str, decision_bundle: Dict) -> Dict:
    symbol = str(symbol or "").upper().strip()
    bundle = _safe_dict(decision_bundle)

    emotional_state = get_soulaana_emotional_state_for_engine()
    behavior_profile = build_soulaana_behavior_profile(emotional_state)
    adjusted_bundle = apply_soulaana_behavior_to_decision_bundle(symbol, bundle, behavior_profile)

    final_brain = build_final_master_brain(
        base_decision=_safe_dict(adjusted_bundle.get("base_decision")),
        base_explainability=_safe_dict(adjusted_bundle.get("explainability")),
        enhanced_integration=_safe_dict(adjusted_bundle.get("enhanced")),
        truth_integration=_safe_dict(adjusted_bundle.get("truth")),
        behavior_intelligence=_safe_dict(adjusted_bundle.get("behavior")),
        causality_intelligence=_safe_dict(adjusted_bundle.get("causality")),
        counterfactual_intelligence=_safe_dict(adjusted_bundle.get("counterfactual")),
    )

    final_brain = apply_soulaana_behavior_to_final_brain(final_brain, behavior_profile)
    return final_brain


def build_all_final_brains(decision_map: Dict[str, Dict]) -> Dict[str, Dict]:
    final_map: Dict[str, Dict] = {}
    if not isinstance(decision_map, dict):
        return final_map

    for symbol, bundle in decision_map.items():
        clean_symbol = str(symbol or "").upper().strip()
        if not clean_symbol:
            continue
        try:
            final_map[clean_symbol] = build_symbol_final_brain(clean_symbol, _safe_dict(bundle))
        except Exception as e:
            print(f"[FINAL_BRAIN_BUILD:{clean_symbol}] {e}")

    return final_map


def build_final_symbol_page_context(symbol: str, decision_bundle: Dict, tier: str = "free") -> Dict:
    clean_symbol = str(symbol or "").upper().strip()
    final_brain = build_symbol_final_brain(clean_symbol, decision_bundle)
    return build_final_symbol_context(
        symbol=clean_symbol,
        final_brain=final_brain,
        tier=str(tier or "free").lower(),
    )


def build_final_spotlight_cards(decision_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    final_brain_map = build_all_final_brains(decision_map)
    return build_final_spotlight_context(
        final_brain_map=final_brain_map,
        tier=str(tier or "free").lower(),
    )


def build_final_dashboard_view(decision_map: Dict[str, Dict], tier: str = "free") -> Dict:
    final_brain_map = build_all_final_brains(decision_map)
    return build_final_dashboard_context(
        final_brain_map=final_brain_map,
        tier=str(tier or "free").lower(),
    )


def build_final_all_symbol_cards(decision_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    final_brain_map = build_all_final_brains(decision_map)
    cards = build_final_spotlight_context(
        final_brain_map=final_brain_map,
        tier=str(tier or "free").lower(),
    )

    out: List[Dict] = []
    for card in cards:
        clean_card = _safe_dict(card)
        out.append(
            {
                "symbol": clean_card.get("symbol"),
                "title": clean_card.get("title"),
                "subtitle": clean_card.get("subtitle"),
                "action": clean_card.get("action"),
                "confidence": clean_card.get("confidence"),
                "story": clean_card.get("story", ""),
                "highlights": _safe_list(clean_card.get("highlights")),
                "reasons": _safe_list(clean_card.get("reasons")),
                "coaching": clean_card.get("coaching", ""),
            }
        )
    return out
