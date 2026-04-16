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
- signal explanation payload
- position explanation payload
"""

from typing import Dict, Any, Optional, List

import engine.final_decision_engine as final_decision_engine
import engine.canonical_decision_object as canonical_decision_object
import engine.explainability_engine as explainability_engine
import engine.soulaana_voice as soulaana_voice


def _safe_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _safe_str(x: Any, default: str = "") -> str:
    try:
        text = str(x or "").strip()
        return text if text else default
    except Exception:
        return default


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _first_meaningful_line(value: Any, fallback: str = "") -> str:
    if isinstance(value, list):
        for item in value:
            text = _safe_str(item, "")
            if text:
                return text
        return fallback

    if isinstance(value, dict):
        for key in ["summary", "headline", "message", "reason", "note"]:
            text = _safe_str(value.get(key), "")
            if text:
                return text
        return fallback

    return _safe_str(value, fallback)


def _call_voice_builder(explainability: Dict[str, Any], emotional_state: Optional[str] = None) -> Dict[str, Any]:
    """
    Support both old and new Soulaana voice function names so the system does not break
    if the voice file still has older naming.
    """
    candidates = [
        "build_soulaana_signal_message",
        "build_soulanna_signal_message",
        "build_soulaana_message",
        "build_signal_message",
    ]

    for fn_name in candidates:
        fn = getattr(soulaana_voice, fn_name, None)
        if callable(fn):
            try:
                result = fn(explainability, emotional_state=emotional_state)
                if isinstance(result, dict):
                    return result
                if isinstance(result, str):
                    return {
                        "headline": result,
                        "assessment": result,
                        "why": explainability.get("summary", ""),
                        "risk": "",
                        "next_action": explainability.get("verdict", "WATCH"),
                        "verdict": explainability.get("verdict", "WATCH"),
                    }
            except TypeError:
                try:
                    result = fn(explainability)
                    if isinstance(result, dict):
                        return result
                    if isinstance(result, str):
                        return {
                            "headline": result,
                            "assessment": result,
                            "why": explainability.get("summary", ""),
                            "risk": "",
                            "next_action": explainability.get("verdict", "WATCH"),
                            "verdict": explainability.get("verdict", "WATCH"),
                        }
                except Exception:
                    pass
            except Exception:
                pass

    verdict = _safe_str(explainability.get("verdict"), "WATCH").upper()
    summary = _safe_str(explainability.get("summary"), "Soulaana reviewed the setup.")
    return {
        "headline": f"{_safe_str(explainability.get('symbol'), 'Symbol')} reviewed",
        "assessment": summary,
        "why": summary,
        "risk": _first_meaningful_line(explainability.get("pressures"), ""),
        "next_action": verdict,
        "verdict": verdict,
    }


def _build_explainability_payload(
    context: Dict[str, Any],
    final_decision: Dict[str, Any],
    canonical: Dict[str, Any],
) -> Dict[str, Any]:
    context = _safe_dict(context)
    final_decision = _safe_dict(final_decision)
    canonical = _safe_dict(canonical)

    symbol = _safe_str(context.get("symbol"), "UNKNOWN")
    verdict = _safe_str(
        final_decision.get("final_verdict", canonical.get("final_verdict", "WATCH")),
        "WATCH",
    ).upper()
    confidence = _safe_str(
        final_decision.get(
            "decision_confidence",
            canonical.get("decision_confidence", context.get("confidence", "LOW")),
        ),
        "LOW",
    ).upper()

    reasons: List[str] = []
    try:
        raw_reasons = explainability_engine.explain_trade_decision(
            context,
            mode=context.get("mode"),
            regime=context.get("regime") or context.get("market_regime"),
            breadth=context.get("breadth"),
            volatility=context.get("volatility_state"),
        )
        if isinstance(raw_reasons, list):
            reasons = [_safe_str(x) for x in raw_reasons if _safe_str(x)]
        elif isinstance(raw_reasons, dict):
            reasons = [
                _safe_str(raw_reasons.get("headline")),
                _safe_str(raw_reasons.get("summary")),
            ]
            reasons = [x for x in reasons if x]
        elif raw_reasons:
            reasons = [_safe_str(raw_reasons)]
    except Exception:
        reasons = []

    pressures: List[str] = []
    rebuild_pressure = _safe_float(context.get("rebuild_pressure"), 0)

    if rebuild_pressure >= 18:
        pressures.append("rebuild pressure is elevated")
    elif rebuild_pressure >= 10:
        pressures.append("rebuild pressure is moderate")
    elif rebuild_pressure >= 6:
        pressures.append("rebuild pressure is present")

    for bucket_name in ["playbook_penalties", "confidence_penalties"]:
        bucket = context.get(bucket_name, [])
        if isinstance(bucket, list):
            for item in bucket:
                item_str = _safe_str(item).replace("_", " ").strip()
                if item_str:
                    pressures.append(item_str)

    improvements: List[str] = []
    if confidence == "LOW":
        improvements.append("confidence needs to recover before aggressive action makes sense")
    elif confidence == "MEDIUM":
        improvements.append("the setup needs more proof before immediate entry")

    if rebuild_pressure >= 10:
        improvements.append("rebuild pressure needs to come down before trust can expand")

    if not improvements:
        improvements.append("keep execution clean and do not get sloppy managing the trade")

    supports = _safe_list(canonical.get("dominant_supports"))
    blockers = _safe_list(canonical.get("dominant_blockers"))

    summary = " ".join(reasons[:2]).strip()
    if not summary:
        summary = _safe_str(final_decision.get("decision_reason"), "Soulaana reviewed the setup.")

    return {
        "symbol": symbol,
        "verdict": verdict,
        "confidence": confidence,
        "headline": _safe_str(canonical.get("final_verdict"), verdict),
        "summary": summary,
        "reasons": reasons,
        "supports": supports,
        "blockers": blockers,
        "pressures": pressures,
        "improvements": improvements,
        "readiness_score": _safe_float(context.get("readiness_score"), 0),
        "promotion_score": _safe_float(context.get("promotion_score"), 0),
        "rebuild_pressure": _safe_float(context.get("rebuild_pressure"), 0),
        "execution_quality": _safe_float(context.get("execution_quality"), 0),
        "setup_family": _safe_str(context.get("setup_family"), "unknown"),
        "entry_quality": _safe_str(context.get("entry_quality"), "unknown"),
        "decision_reason": _safe_str(final_decision.get("decision_reason"), ""),
    }


def build_soulaana_output(
    context: Dict[str, Any],
    emotional_state: Optional[str] = None,
) -> Dict[str, Any]:
    context = _safe_dict(context)

    try:
        final_decision = _safe_dict(final_decision_engine.build_final_decision(context))
    except Exception:
        final_decision = {
            "final_verdict": _safe_str(context.get("final_verdict"), "WATCH"),
            "decision_reason": _safe_str(context.get("decision_reason"), "Final decision engine unavailable."),
            "decision_confidence": _safe_str(context.get("confidence"), "LOW"),
        }

    enriched = dict(context)
    enriched["final_decision"] = final_decision
    enriched["final_verdict"] = final_decision.get("final_verdict")
    enriched["decision_reason"] = final_decision.get("decision_reason")
    enriched["confidence"] = final_decision.get(
        "decision_confidence",
        enriched.get("confidence", "LOW"),
    )

    try:
        canonical = _safe_dict(canonical_decision_object.build_canonical_decision_object(enriched))
    except Exception:
        canonical = {
            "final_verdict": _safe_str(enriched.get("final_verdict"), "WATCH"),
            "dominant_supports": [],
            "dominant_blockers": [],
        }

    explainability = _build_explainability_payload(
        enriched,
        final_decision=final_decision,
        canonical=canonical,
    )

    message = _safe_dict(_call_voice_builder(explainability, emotional_state=emotional_state))

    return {
        "symbol": enriched.get("symbol"),
        "final_decision": final_decision,
        "canonical": canonical,
        "explainability": explainability,
        "message": message,
        "headline": _safe_str(message.get("headline"), f"{_safe_str(enriched.get('symbol'), 'Symbol')} reviewed"),
        "verdict": _safe_str(message.get("verdict"), explainability.get("verdict", "WATCH")).upper(),
        "assessment": _safe_str(message.get("assessment"), explainability.get("summary", "")),
        "why": _safe_str(message.get("why"), explainability.get("decision_reason", explainability.get("summary", ""))),
        "risk": _safe_str(message.get("risk"), _first_meaningful_line(explainability.get("pressures"), "")),
        "next_action": _safe_str(message.get("next_action"), explainability.get("verdict", "WATCH")),
    }


def soulaana_explain_signal(
    context: Dict[str, Any],
    emotional_state: Optional[str] = None,
) -> Dict[str, Any]:
    payload = build_soulaana_output(context, emotional_state=emotional_state)
    return {
        "headline": payload.get("headline", ""),
        "verdict": payload.get("verdict", "WATCH"),
        "assessment": payload.get("assessment", ""),
        "why": payload.get("why", ""),
        "risk": payload.get("risk", ""),
        "next_action": payload.get("next_action", ""),
        "final_decision": payload.get("final_decision", {}),
        "canonical": payload.get("canonical", {}),
        "explainability": payload.get("explainability", {}),
    }


def soulaana_explain_position(
    context: Dict[str, Any],
    emotional_state: Optional[str] = None,
) -> Dict[str, Any]:
    context = _safe_dict(context)

    symbol = _safe_str(context.get("symbol"), "UNKNOWN")
    pnl = _safe_float(context.get("pnl", context.get("unrealized_pnl", 0)), 0)
    progress = _safe_float(context.get("progress"), 0)
    readiness_score = _safe_float(context.get("readiness_score"), 0)
    promotion_score = _safe_float(context.get("promotion_score"), 0)
    rebuild_pressure = _safe_float(context.get("rebuild_pressure"), 0)
    setup_family = _safe_str(context.get("setup_family"), "unknown")
    entry_quality = _safe_str(context.get("entry_quality"), "unknown")

    verdict = "HOLD"
    assessment = f"{symbol} is still being managed inside the open-position layer."
    risk = ""
    next_action = "Hold and continue monitoring."

    if rebuild_pressure >= 40:
        verdict = "CAUTION"
        assessment = f"{symbol} is carrying heavier rebuild pressure than I want for a comfortable hold."
        risk = "Rebuild pressure is elevated, so the position is more fragile."
        next_action = "Tighten management and do not get lazy."
    elif progress < 0 and pnl < 0:
        verdict = "WEAKENING"
        assessment = f"{symbol} is underwater and not following through cleanly yet."
        risk = "The trade is losing momentum and the position may be softening."
        next_action = "Respect the stop and do not force patience."
    elif progress >= 0.6:
        verdict = "PROTECT"
        assessment = f"{symbol} has moved far enough that protection matters more than hope."
        risk = "Giving back progress is the main risk now."
        next_action = "Protect profits without choking the trade."

    why = (
        f"{symbol} | readiness {round(readiness_score, 2)} | promotion {round(promotion_score, 2)} | "
        f"rebuild {round(rebuild_pressure, 2)} | progress {round(progress, 2)} | pnl {round(pnl, 2)} | "
        f"setup {setup_family} | entry quality {entry_quality}"
    )

    if emotional_state:
        emotional_state = _safe_str(emotional_state).lower()
        if emotional_state == "impulsive":
            next_action = "Slow down. No emotional clicking. Respect the plan."
        elif emotional_state == "frustrated":
            next_action = "Do not punish the chart for how you feel. Tighten discipline."
        elif emotional_state == "calm":
            next_action = f"{next_action} Stay methodical."
        elif emotional_state == "confident":
            next_action = f"{next_action} Confidence is fine, but it still has to obey structure."

    return {
        "headline": f"{symbol} position reviewed",
        "verdict": verdict,
        "assessment": assessment,
        "why": why,
        "risk": risk,
        "next_action": next_action,
        "readiness_score": readiness_score,
        "promotion_score": promotion_score,
        "rebuild_pressure": rebuild_pressure,
        "setup_family": setup_family,
        "entry_quality": entry_quality,
    }


def build_login_experience(
    user_id: Optional[str] = None,
    mood_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    First-touch login payload.
    Returns greeting copy plus the emotional check choices.
    """
    greeting = {}

    candidates = [
        "build_login_greeting",
        "build_soulaana_login_greeting",
    ]

    for fn_name in candidates:
        fn = getattr(soulaana_voice, fn_name, None)
        if callable(fn):
            try:
                greeting = fn(user_id=user_id, mood_hint=mood_hint)
                if isinstance(greeting, dict):
                    break
            except Exception:
                pass

    greeting = _safe_dict(greeting)

    if not greeting:
        greeting = {
            "headline": "Hey love, how you feeling coming in today?",
            "subtext": "Your check-in helps Soulaana tailor guidance and catch emotional pressure early.",
            "checkin_options": [
                "calm",
                "focused",
                "confident",
                "cautious",
                "anxious",
                "frustrated",
                "impulsive",
                "tired",
            ],
            "allow_skip": True,
        }

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

    response = ""
    candidates = [
        "build_checkin_response",
        "build_soulaana_checkin_response",
    ]

    for fn_name in candidates:
        fn = getattr(soulaana_voice, fn_name, None)
        if callable(fn):
            try:
                response = fn(emotional_state=state, user_id=user_id)
                break
            except TypeError:
                try:
                    response = fn(state, user_id=user_id)
                    break
                except Exception:
                    pass
            except Exception:
                pass

    response = _safe_str(response, "")

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

    if not response:
        fallback_map = {
            "calm": "Good. Stay clean and don’t get sloppy.",
            "focused": "Perfect. Keep your eyes sharp and your clicks intentional.",
            "confident": "Love the energy. Just don’t let confidence outrun structure.",
            "cautious": "That’s fine. Careful beats reckless every time.",
            "anxious": "Then we slow it down. No rush, no forcing.",
            "frustrated": "Then today we protect first. No revenge trading energy.",
            "impulsive": "Then we do not click fast. We verify first, always.",
            "tired": "Then we simplify. Less noise, cleaner choices.",
        }
        response = fallback_map.get(
            state,
            "Soulaana is here. Stay honest and let the system guide the pace.",
        )

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
