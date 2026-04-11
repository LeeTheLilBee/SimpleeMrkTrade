"""
SOULAANA CORE
Central orchestration layer between:
- final decision engine
- canonical decision object
- explainability
- Soulaana voice

Also provides:
- login greeting payload
- emotional check-in payload
"""

from typing import Dict, Any, Optional

import engine.final_decision_engine as final_decision_engine
import engine.canonical_decision_object as canonical_decision_object
import engine.explainability_engine as explainability_engine
import engine.soulaana_voice as soulaana_voice


def _safe_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _safe_str(x: Any, default: str = "") -> str:
    try:
        return str(x)
    except Exception:
        return default


def _build_explainability_payload(
    context: Dict[str, Any],
    final_decision: Dict[str, Any],
    canonical: Dict[str, Any],
) -> Dict[str, Any]:
    context = _safe_dict(context)
    final_decision = _safe_dict(final_decision)
    canonical = _safe_dict(canonical)

    symbol = context.get("symbol", "")
    verdict = final_decision.get("final_verdict", canonical.get("final_verdict", "WATCH"))
    confidence = final_decision.get(
        "decision_confidence",
        canonical.get("decision_confidence", context.get("confidence", "LOW")),
    )

    reasons = []
    try:
        reasons = explainability_engine.explain_trade_decision(
            context,
            mode=context.get("mode"),
            regime=context.get("regime") or context.get("market_regime"),
            breadth=context.get("breadth"),
            volatility=context.get("volatility_state"),
        )
    except Exception:
        reasons = []

    pressures = []
    rebuild_pressure = float(context.get("rebuild_pressure", 0) or 0)

    if rebuild_pressure >= 18:
        pressures.append("rebuild pressure is elevated")
    elif rebuild_pressure >= 10:
        pressures.append("rebuild pressure is moderate")
    elif rebuild_pressure >= 6:
        pressures.append("rebuild pressure is present")

    playbook_penalties = context.get("playbook_penalties", [])
    if isinstance(playbook_penalties, list):
        for item in playbook_penalties:
            item_str = str(item).replace("_", " ").strip()
            if item_str:
                pressures.append(item_str)

    confidence_penalties = context.get("confidence_penalties", [])
    if isinstance(confidence_penalties, list):
        for item in confidence_penalties:
            item_str = str(item).replace("_", " ").strip()
            if item_str:
                pressures.append(item_str)

    improvements = []

    if confidence == "LOW":
        improvements.append("confidence needs to recover before aggressive action makes sense")
    elif confidence == "MEDIUM":
        improvements.append("the setup needs more proof before immediate entry")

    if rebuild_pressure >= 10:
        improvements.append("rebuild pressure needs to come down before trust can expand")

    if not improvements:
        improvements.append("keep execution clean and do not get sloppy managing the trade")

    supports = canonical.get("dominant_supports", [])
    blockers = canonical.get("dominant_blockers", [])

    if not isinstance(supports, list):
        supports = []
    if not isinstance(blockers, list):
        blockers = []

    return {
        "symbol": symbol,
        "verdict": verdict,
        "confidence": confidence,
        "headline": canonical.get("final_verdict", verdict),
        "summary": " ".join(reasons[:2]).strip() if reasons else "",
        "reasons": reasons,
        "supports": supports,
        "blockers": blockers,
        "pressures": pressures,
        "improvements": improvements,
        "readiness_score": context.get("readiness_score", 0),
        "promotion_score": context.get("promotion_score", 0),
        "rebuild_pressure": context.get("rebuild_pressure", 0),
        "execution_quality": context.get("execution_quality", 0),
        "setup_family": context.get("setup_family", "unknown"),
        "entry_quality": context.get("entry_quality", "unknown"),
    }


def build_soulaana_output(
    context: Dict[str, Any],
    emotional_state: Optional[str] = None,
) -> Dict[str, Any]:
    context = _safe_dict(context)

    final_decision = final_decision_engine.build_final_decision(context)

    enriched = dict(context)
    enriched["final_decision"] = final_decision
    enriched["final_verdict"] = final_decision.get("final_verdict")
    enriched["decision_reason"] = final_decision.get("decision_reason")
    enriched["confidence"] = final_decision.get(
        "decision_confidence",
        enriched.get("confidence", "LOW"),
    )

    canonical = canonical_decision_object.build_canonical_decision_object(enriched)

    explainability = _build_explainability_payload(
        enriched,
        final_decision=final_decision,
        canonical=canonical,
    )

    message = soulaana_voice.build_soulanna_signal_message(
        explainability,
        emotional_state=emotional_state,
    )

    return {
        "symbol": enriched.get("symbol"),
        "final_decision": final_decision,
        "canonical": canonical,
        "explainability": explainability,
        "message": message,
    }


def build_login_experience(
    user_id: Optional[str] = None,
    mood_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    First-touch login payload.
    Returns greeting copy plus the emotional check choices.
    """
    greeting = soulaana_voice.build_login_greeting(
        user_id=user_id,
        mood_hint=mood_hint,
    )

    return {
        "identity": "Soulaana",
        "type": "login_greeting",
        "headline": greeting.get("headline", ""),
        "subtext": greeting.get("subtext", ""),
        "checkin_options": greeting.get("checkin_options", []),
        "allow_skip": bool(greeting.get("allow_skip", True)),
        "note": "Your check-in helps Soulaana tailor guidance and catch emotional pressure early.",
    }


def build_checkin_experience(
    emotional_state: str,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns a direct emotional check-in response and system note.
    """
    state = _safe_str(emotional_state).strip().lower()
    response = soulaana_voice.build_checkin_response(
        emotional_state=state,
        user_id=user_id,
    )

    response_type = "steady"
    if state in {"frustrated", "impulsive", "anxious"}:
        response_type = "protective"
    elif state in {"calm", "focused", "confident"}:
        response_type = "encouraging"

    system_note_map = {
        "calm": "Soulaana can allow a cleaner, less defensive tone.",
        "focused": "Soulaana can lean more analytical and direct.",
        "confident": "Soulaana should watch for overconfidence while preserving momentum.",
        "cautious": "Soulaana should reassure without overpromising.",
        "anxious": "Soulaana should slow the pace and tighten behavioral guardrails.",
        "frustrated": "Soulaana should use firmer protection against forcing trades.",
        "impulsive": "Soulaana should actively discourage emotional clicking and chasing.",
        "tired": "Soulaana should simplify guidance and reduce noise.",
    }

    return {
        "identity": "Soulaana",
        "type": "emotional_checkin",
        "emotional_state": state,
        "response_tone": response_type,
        "headline": response,
        "system_note": system_note_map.get(
            state,
            "Soulaana should stay balanced and attentive to behavior."
        ),
        "store_for_session": True,
    }


def build_login_and_checkin_bundle(
    user_id: Optional[str] = None,
    mood_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    One-shot bundle for UI rendering on login.
    """
    login_payload = build_login_experience(
        user_id=user_id,
        mood_hint=mood_hint,
    )

    return {
        "identity": "Soulaana",
        "type": "login_bundle",
        "greeting": login_payload,
    }
