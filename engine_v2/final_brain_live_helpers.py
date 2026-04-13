from typing import Dict, List


def _safe_dict(value) -> Dict:
    return value if isinstance(value, dict) else {}


def _safe_list(value) -> List:
    return value if isinstance(value, list) else []


def _safe_text(value, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _normalize_action(action: str) -> str:
    text = _safe_text(action, "wait").lower()
    if text in {"buy", "enter"}:
        return "take"
    return text


def _normalize_confidence(confidence: str) -> str:
    text = _safe_text(confidence, "low").lower()
    if text not in {"low", "medium", "high"}:
        return "low"
    return text


def _title_case_action(action: str) -> str:
    return _normalize_action(action).replace("_", " ").title()


def _coaching_tone_from_action(action: str, confidence: str) -> str:
    action = _normalize_action(action)
    confidence = _normalize_confidence(confidence)

    if action in {"block", "exit", "protect"}:
        return "protective"
    if action in {"watch", "wait"} and confidence in {"low", "medium"}:
        return "steady"
    if action in {"take", "hold", "ready"} and confidence == "high":
        return "encouraging"
    return "steady"


def _build_story_line(action: str, confidence: str, reasons: List[str], intervention_active: bool) -> str:
    action = _normalize_action(action)
    confidence = _normalize_confidence(confidence)

    if intervention_active and reasons:
        return reasons[0]

    if action in {"take", "ready"} and confidence == "high":
        return "The system sees a strong enough alignment to move this idea forward, but it still expects discipline."
    if action in {"watch", "wait"}:
        return "The setup is visible, but the system wants cleaner confirmation before treating it as action-ready."
    if action == "hold":
        return "The symbol is still valid, but the system wants patience instead of forcing change."
    if action in {"protect", "exit", "block"}:
        return "Risk control is taking priority over opportunity right now."
    return "The symbol is active, but the system posture is still developing."


def _build_subtitle(symbol: str, action: str, confidence: str, intervention_active: bool) -> str:
    action = _normalize_action(action)
    confidence = _normalize_confidence(confidence)

    if intervention_active:
        return f"Soulanna adjusted the posture on {symbol} to protect decision quality."

    if action in {"take", "ready"}:
        return f"{symbol} is leaning actionable with {confidence} conviction."
    if action in {"watch", "wait"}:
        return f"{symbol} is on watch, but not fully cleared."
    if action == "hold":
        return f"{symbol} remains valid, but patience is still part of the trade."
    if action in {"protect", "exit", "block"}:
        return f"{symbol} is in a defensive posture."
    return f"{symbol} is being evaluated."


def build_final_symbol_context(symbol: str, final_brain: Dict, tier: str = "free") -> Dict:
    clean_symbol = _safe_text(symbol, "").upper()
    brain = _safe_dict(final_brain)
    tier = _safe_text(tier, "free").lower()

    base_decision = _safe_dict(brain.get("base_decision"))
    explainability = _safe_dict(brain.get("explainability"))
    soulaana_behavior = _safe_dict(brain.get("soulaana_behavior"))
    behavior_intelligence = _safe_dict(brain.get("behavior_intelligence"))

    raw_action = _normalize_action(base_decision.get("raw_action", base_decision.get("action", "wait")))
    raw_confidence = _normalize_confidence(base_decision.get("raw_confidence", base_decision.get("confidence", "low")))

    hero_action = _normalize_action(base_decision.get("action", "wait"))
    hero_confidence = _normalize_confidence(base_decision.get("confidence", "low"))

    intervention_active = bool(soulaana_behavior.get("intervention_active", False))
    intervention_reasons = _safe_list(soulaana_behavior.get("intervention_reasons", []))

    emotional_state = _safe_text(soulaana_behavior.get("emotional_state", "unknown"), "unknown")
    state_family = _safe_text(soulaana_behavior.get("state_family", "stable"), "stable")
    risk_level = _safe_text(soulaana_behavior.get("risk_level", "low"), "low")
    tone_mode = _safe_text(soulaana_behavior.get("tone_mode", "steady"), "steady")
    warning_level = _safe_text(soulaana_behavior.get("warning_level", "normal"), "normal")
    friction_level = _safe_text(soulaana_behavior.get("friction_level", "normal"), "normal")

    hero_title = f"{_title_case_action(hero_action)} posture"
    if intervention_active and hero_action != raw_action:
        hero_title = f"{_title_case_action(hero_action)} after Soulanna intervention"

    hero_story = _safe_text(
        explainability.get("soulaana_behavior_summary", ""),
        "",
    ) or _build_story_line(hero_action, hero_confidence, intervention_reasons, intervention_active)

    hero_subtitle = _build_subtitle(clean_symbol, hero_action, hero_confidence, intervention_active)
    coaching_message = hero_story
    coaching_tone = _coaching_tone_from_action(hero_action, hero_confidence)

    hero_reasons = []

    if intervention_active:
        hero_reasons.append(f"Raw action was {raw_action.upper()} before Soulanna behavior protection.")
        hero_reasons.append(
            f"Current emotional state is {emotional_state.replace('_', ' ')}, which maps to {risk_level} behavior risk."
        )
        for item in intervention_reasons[:3]:
            if item:
                hero_reasons.append(item)
    else:
        hero_reasons.append(f"Current action is {hero_action.upper()} with {hero_confidence.upper()} confidence.")
        hero_reasons.append(f"Soulanna behavior mode is {state_family.replace('_', ' ')}.")
        if tone_mode:
            hero_reasons.append(f"Tone mode is {tone_mode.replace('_', ' ')}.")

    hard_reject = hero_action in {"block", "exit"}
    hard_reject_reason = intervention_reasons[0] if intervention_reasons else ""

    return {
        "symbol": clean_symbol,
        "hero_title": hero_title,
        "hero_action": hero_action,
        "hero_confidence": hero_confidence,
        "hero_subtitle": hero_subtitle,
        "hero_story": hero_story,
        "hero_reasons": hero_reasons[:5],
        "coaching_message": coaching_message,
        "coaching_tone": coaching_tone,
        "hard_reject": hard_reject,
        "hard_reject_reason": hard_reject_reason,
        "tier": tier,
        "behavior_layer": {
            "intervention_active": intervention_active,
            "raw_action": raw_action,
            "raw_confidence": raw_confidence,
            "adjusted_action": hero_action,
            "adjusted_confidence": hero_confidence,
            "emotional_state": emotional_state,
            "state_family": state_family,
            "risk_level": risk_level,
            "tone_mode": tone_mode,
            "warning_level": warning_level,
            "friction_level": friction_level,
            "intervention_reasons": intervention_reasons[:5],
        },
        "truth_layer": _safe_dict(brain.get("truth")),
        "enhanced_layer": _safe_dict(brain.get("enhanced")),
        "behavior_intelligence": behavior_intelligence,
        "explainability": explainability,
    }


def build_final_spotlight_context(final_brain_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    out: List[Dict] = []
    if not isinstance(final_brain_map, dict):
        return out

    for symbol, final_brain in final_brain_map.items():
        ctx = build_final_symbol_context(symbol=symbol, final_brain=final_brain, tier=tier)
        behavior_layer = _safe_dict(ctx.get("behavior_layer"))

        highlights = []
        if behavior_layer.get("intervention_active"):
            highlights.append(
                f"Soulanna adjusted posture from {behavior_layer.get('raw_action', 'wait')} to {behavior_layer.get('adjusted_action', 'watch')}."
            )
        highlights.append(f"Risk level: {behavior_layer.get('risk_level', 'low')}.")
        highlights.extend(_safe_list(behavior_layer.get("intervention_reasons", []))[:2])

        out.append(
            {
                "symbol": symbol,
                "title": ctx.get("hero_title", "Signal"),
                "subtitle": ctx.get("hero_subtitle", ""),
                "action": ctx.get("hero_action", "wait"),
                "confidence": ctx.get("hero_confidence", "low"),
                "story": ctx.get("hero_story", ""),
                "highlights": highlights[:4],
                "reasons": _safe_list(ctx.get("hero_reasons", []))[:4],
                "coaching": ctx.get("coaching_message", ""),
            }
        )

    def _rank(card: Dict) -> tuple:
        action = _normalize_action(card.get("action", "wait"))
        confidence = _normalize_confidence(card.get("confidence", "low"))

        action_rank = {
            "take": 5,
            "ready": 4,
            "hold": 3,
            "watch": 2,
            "wait": 1,
            "protect": 1,
            "block": 0,
            "exit": 0,
        }.get(action, 1)

        confidence_rank = {
            "high": 3,
            "medium": 2,
            "low": 1,
        }.get(confidence, 1)

        return (action_rank, confidence_rank)

    out.sort(key=_rank, reverse=True)
    return out


def build_final_dashboard_context(final_brain_map: Dict[str, Dict], tier: str = "free") -> Dict:
    cards = build_final_spotlight_context(final_brain_map=final_brain_map, tier=tier)

    if not cards:
        return {
            "dashboard_action": "wait",
            "dashboard_insight": "No final-brain dashboard insight available.",
            "dashboard_story": "",
            "dashboard_coaching": "",
            "dominant_symbol": "None",
        }

    lead = cards[0]
    return {
        "dashboard_action": lead.get("action", "wait"),
        "dashboard_insight": lead.get("subtitle", "No final-brain dashboard insight available."),
        "dashboard_story": lead.get("story", ""),
        "dashboard_coaching": lead.get("coaching", ""),
        "dominant_symbol": lead.get("symbol", "None"),
    }
