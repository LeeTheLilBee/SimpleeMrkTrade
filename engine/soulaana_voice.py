"""
SOULAANA VOICE LAYER
Personality + variation + tone routing on top of the explainability engine.
"""

from typing import Any, Dict, List, Optional
import hashlib


def _safe_str(x: Any, default: str = "") -> str:
    try:
        return str(x)
    except Exception:
        return default


def _safe_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _normalize_text(text: str) -> str:
    return _safe_str(text).strip()


def _pick_variant(options: List[str], seed_parts: List[Any]) -> str:
    options = [opt for opt in options if _normalize_text(opt)]
    if not options:
        return ""
    seed = "|".join([_safe_str(part) for part in seed_parts])
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    idx = int(digest[:8], 16) % len(options)
    return options[idx]


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        clean = _normalize_text(item)
        if not clean:
            continue
        if clean in seen:
            continue
        seen.add(clean)
        out.append(clean)
    return out


def _tone_mode(explainability: Dict[str, Any], emotional_state: Optional[str] = None) -> str:
    verdict = _safe_str(explainability.get("verdict", "WATCH")).upper()
    confidence = _safe_str(explainability.get("confidence", "LOW")).upper()
    pressures = _safe_list(explainability.get("pressures", []))
    blockers = _safe_list(explainability.get("blockers", []))
    emotional_state = _safe_str(emotional_state).strip().lower()

    rebuild_pressure = float(explainability.get("rebuild_pressure", 0) or 0)
    promotion_score = float(explainability.get("promotion_score", 0) or 0)

    if emotional_state in {"frustrated", "impulsive"}:
        return "firm_auntie"

    if verdict == "TAKE" and confidence == "HIGH":
        return "calm_approval"

    if rebuild_pressure >= 18:
        return "protective"

    if promotion_score < 145 and verdict == "WATCH":
        return "skeptical_watch"

    if verdict == "WATCH" and confidence == "MEDIUM":
        return "cautious_watch"

    if verdict in {"BLOCK", "EXIT"} or confidence == "LOW" or blockers or len(pressures) >= 2:
        return "protective"

    return "steady"


GREETINGS = {
    "default": [
        "Hey baby, how you feeling coming in today?",
        "Hey love, check in with me real quick.",
        "Hey sunshine, where your head at today?",
        "Hey boo, before we get into all this, how you feeling?",
        "Hey hey, talk to me. What kind of energy we bringing in today?",
    ],
    "calm": [
        "Hey love, you feeling steady today?",
        "Hey baby, we calm and clear today or what?",
    ],
    "supportive": [
        "Hey boo, come on in. How you feeling for real?",
        "Hey sunshine, let me check your temperature before we touch this market.",
    ],
}

CHECKIN_EXPLANATIONS = [
    "This helps me tailor your guidance and catch emotional pressure before it turns expensive.",
    "Your check-in helps me spot emotional risk before it leaks into your decisions.",
    "The better I understand your headspace, the better I can protect your decision quality.",
]

CHECKIN_RESPONSE_MAP = {
    "calm": [
        "Good. Let’s keep it clean and not get greedy.",
        "Love that. Stay steady and let the structure do the talking.",
    ],
    "focused": [
        "Good. That’s the kind of energy I like.",
        "Alright then. Stay disciplined and don’t get cute.",
    ],
    "confident": [
        "Confidence is fine. Just don’t let it turn into arrogance.",
        "Good. Keep it grounded though, baby. We still respect the setup.",
    ],
    "cautious": [
        "That’s alright. Cautious can save you money.",
        "Nothing wrong with cautious. Just don’t let it make you freeze.",
    ],
    "anxious": [
        "Alright, then we move slower today. No forcing and no chasing.",
        "Got it. That means we stay extra honest about what’s actually ready.",
    ],
    "frustrated": [
        "Mm. Then we definitely not giving money away trying to feel better.",
        "Okay, so we’re not letting frustration make decisions today.",
    ],
    "impulsive": [
        "Thank you for being honest. That means tighter guardrails today.",
        "Alright now, then we need to slow your hand down before you click on something foolish.",
    ],
    "tired": [
        "Got it. Then we keeping it simple and clean today.",
        "Okay. Less noise, more clarity. No extra chaos.",
    ],
}

OPENERS = {
    "calm_approval": {
        "TAKE": [
            "Yeah… this one’s clean.",
            "Alright now, this right here is clean.",
            "Mm. This is the kind of setup I like to see.",
            "Yeah baby, this one’s put together the way it should be.",
        ],
    },
    "cautious_watch": {
        "WATCH": [
            "I see it… but I’m not stepping in yet.",
            "Mm. It’s not bad, but it’s not clean enough for me yet.",
            "It’s trying, but I still need more from it.",
            "I’m watching it, but I’m not ready to bless it.",
        ],
    },
    "protective": {
        "WATCH": [
            "Mm-mm. I need you to slow down on this one.",
            "Yeah… no. This is not the kind of setup you get cute with.",
            "This is exactly how people donate to the market when they don’t listen.",
            "Leave that alone for now. It is not holding together right.",
        ],
        "BLOCK": [
            "Now you know better than that.",
            "Absolutely not. Leave that where it is.",
            "Mm-mm. We not doing that today.",
        ],
        "EXIT": [
            "Baby, this needs an exit decision.",
            "Yeah, it’s time to get real clear about this position.",
        ],
    },
    "firm_auntie": {
        "WATCH": [
            "Now you know better than that.",
            "Mm-mm. Don’t start acting up with your money.",
            "You’re doing too much already, and we just got here.",
            "Alright, cut it out. This is not the time to get impulsive.",
        ],
        "BLOCK": [
            "No ma’am. We’re not doing foolishness today.",
            "Absolutely not. Sit with yourself for a minute.",
        ],
    },
    "skeptical_watch": {
        "WATCH": [
            "I see the shape, but it still ain’t ready.",
            "Mm. It’s showing me something, but not enough yet.",
            "This got a little promise on it, but I’m not buying it just yet.",
            "I see why you’d look twice at it, but no, not yet.",
        ],
    },
    "steady": {
        "TAKE": [
            "This is workable.",
            "This one is in decent shape.",
        ],
        "WATCH": [
            "This still needs a little more proof.",
            "This is not fully there yet.",
        ],
    },
}

WHY_LINES = {
    "trusted_take": [
        "Everything important lined up the way it needed to.",
        "Structure, pressure, and execution are all behaving themselves here.",
        "This has enough alignment for me to actually trust it.",
    ],
    "cautious_watch": [
        "It has some good pieces, but not enough clean alignment for immediate action.",
        "I can see why it’s tempting, but temptation is not the same thing as readiness.",
        "It’s got potential, but potential and permission are not the same thing.",
    ],
    "fragile_memory": [
        "This setup family has not been earning trust lately, and I’m not ignoring that.",
        "The memory on this kind of setup is shaky, and that matters.",
        "This playbook has been acting funny, so no, I’m not giving it extra grace.",
    ],
    "low_confidence": [
        "Underneath the surface, it just is not strong enough.",
        "It may look decent at first glance, but the trust is not there.",
        "This is one of those setups that can fool you if you only look at the top layer.",
    ],
}

WARNING_LINES = {
    "moderate_rebuild": [
        "It’s carrying enough pressure that trust needs to stay tight.",
        "There’s enough rebuild pressure here that I need you to respect it.",
        "This is not falling apart, but it is carrying more strain than I like.",
    ],
    "behavioral": [
        "Don’t let your feelings dress this up into something it isn’t.",
        "This is not the place to be emotional with your money.",
        "You rushing this would be a mistake.",
    ],
    "fragile_combo": [
        "This exact setup combo has not earned the right to be trusted casually.",
        "This combo has been shaky, so I need more proof before I let you lean on it.",
    ],
}

GUIDANCE_LINES = {
    "TAKE_calm": [
        "You can take this—just manage it right.",
        "You can take it, but don’t get sloppy once you’re in.",
        "Take it if you want it, but stay disciplined managing it.",
    ],
    "TAKE_proud": [
        "Yeah… this right here? This is what we like to see.",
        "Now this is a grown setup. Just don’t ruin it with bad behavior.",
    ],
    "WATCH_medium": [
        "Let it prove itself first. No need to chase.",
        "Sit still and let this earn more trust.",
        "Watch it. Don’t force it.",
    ],
    "WATCH_low": [
        "Leave it alone for now.",
        "Do not force a trade just because you want one.",
        "Let that sit. We don’t need to touch everything we see.",
    ],
    "BLOCK": [
        "No action. Leave it alone.",
        "Not today. Move on.",
        "Hands off.",
    ],
    "EXIT": [
        "Tighten up and make a clean exit decision.",
        "No drifting. Decide how you’re managing this and do it cleanly.",
    ],
}

AFFECTION_WORDS = [
    "baby",
    "love",
    "boo",
    "sunshine",
]

SOULAANA_PRINCIPLES = [
    "clarity over noise",
    "structure over emotion",
    "patience over panic",
    "discipline over impulse",
]

EMOTIONAL_STATES = [
    "calm",
    "focused",
    "confident",
    "cautious",
    "anxious",
    "frustrated",
    "impulsive",
    "tired",
]


def build_login_greeting(user_id: Optional[str] = None, mood_hint: Optional[str] = None) -> Dict[str, Any]:
    mood_hint = _safe_str(mood_hint).strip().lower()
    bank_key = "default"
    if mood_hint in {"calm", "focused"}:
        bank_key = "calm"
    elif mood_hint in {"anxious", "frustrated", "tired", "impulsive"}:
        bank_key = "supportive"

    greeting = _pick_variant(
        GREETINGS.get(bank_key, GREETINGS["default"]),
        ["login_greeting", user_id or "guest", mood_hint or "none"],
    )
    explanation = _pick_variant(
        CHECKIN_EXPLANATIONS,
        ["checkin_explainer", user_id or "guest", mood_hint or "none"],
    )

    return {
        "headline": greeting,
        "subtext": explanation,
        "checkin_options": EMOTIONAL_STATES,
        "allow_skip": True,
    }


def build_checkin_response(emotional_state: str, user_id: Optional[str] = None) -> str:
    emotional_state = _safe_str(emotional_state).strip().lower()
    bank = CHECKIN_RESPONSE_MAP.get(emotional_state, ["Alright. Let’s keep it honest today."])
    return _pick_variant(bank, ["checkin_response", user_id or "guest", emotional_state])


def _choose_opener(mode: str, verdict: str, explainability: Dict[str, Any], emotional_state: Optional[str]) -> str:
    verdict = _safe_str(verdict).upper()
    emotional_state = _safe_str(emotional_state).strip().lower()

    if emotional_state in {"frustrated", "impulsive"} and verdict in {"WATCH", "BLOCK"}:
        return _pick_variant(
            OPENERS["firm_auntie"].get(verdict, OPENERS["firm_auntie"]["WATCH"]),
            ["opener", mode, verdict, emotional_state, explainability.get("setup_family", "")],
        )

    mode_bank = OPENERS.get(mode, {})
    fallback_bank = OPENERS.get("steady", {})
    options = mode_bank.get(verdict) or fallback_bank.get(verdict) or ["Let me tell you what I’m seeing."]
    return _pick_variant(
        options,
        ["opener", mode, verdict, explainability.get("setup_family", ""), explainability.get("confidence", "")],
    )


def _choose_why(explainability: Dict[str, Any]) -> str:
    verdict = _safe_str(explainability.get("verdict", "WATCH")).upper()
    confidence = _safe_str(explainability.get("confidence", "LOW")).upper()
    setup_family = _safe_str(explainability.get("setup_family", "unknown")).lower()
    blockers = _safe_list(explainability.get("blockers", []))
    pressures = _safe_list(explainability.get("pressures", []))
    promotion_score = float(explainability.get("promotion_score", 0) or 0)
    rebuild_pressure = float(explainability.get("rebuild_pressure", 0) or 0)

    playbook_fragile = any(
        "playbook" in _safe_str(x).lower() or "fragile" in _safe_str(x).lower()
        for x in blockers + pressures
    )

    if playbook_fragile and verdict != "TAKE":
        return _pick_variant(
            WHY_LINES["fragile_memory"],
            ["why", setup_family, confidence, "fragile"]
        )

    if verdict == "TAKE" and confidence == "HIGH":
        return _pick_variant(
            WHY_LINES["trusted_take"],
            ["why", setup_family, confidence, "take"]
        )

    if rebuild_pressure >= 18:
        return _pick_variant(
            [
                "The structure is there, but that pressure underneath still has my eyebrow up.",
                "It’s got enough going for it to watch closely, but that rebuild pressure is not something I’m ignoring.",
                "This setup has real strength, but the strain underneath still needs respect.",
            ],
            ["why", setup_family, confidence, "high_rebuild"]
        )

    if promotion_score < 145:
        return _pick_variant(
            [
                "The structure is decent, but the promotion quality still isn’t mature enough.",
                "It’s got form, but it has not earned full permission yet.",
                "I see the setup, but it still needs to prove it can carry itself.",
            ],
            ["why", setup_family, confidence, "weak_promotion"]
        )

    if confidence == "LOW" or len(pressures) >= 2:
        return _pick_variant(
            WHY_LINES["low_confidence"],
            ["why", setup_family, confidence, "low"]
        )

    return _pick_variant(
        WHY_LINES["cautious_watch"],
        ["why", setup_family, confidence, "watch"]
    )


def _choose_warning(explainability: Dict[str, Any], emotional_state: Optional[str] = None) -> str:
    pressures = [_safe_str(x).lower() for x in _safe_list(explainability.get("pressures", []))]
    emotional_state = _safe_str(emotional_state).strip().lower()

    rebuild_pressure = float(explainability.get("rebuild_pressure", 0) or 0)
    promotion_score = float(explainability.get("promotion_score", 0) or 0)

    if emotional_state in {"frustrated", "impulsive", "anxious"}:
        return _pick_variant(
            WARNING_LINES["behavioral"],
            ["warning", emotional_state, explainability.get("symbol", "")]
        )

    if rebuild_pressure >= 18:
        return _pick_variant(
            [
                "That pressure underneath is exactly how people talk themselves into a bad entry.",
                "This is the kind of setup where good structure can still get wasted by hidden strain.",
                "It looks better on top than it feels underneath, and that matters.",
            ],
            ["warning", "heavy_rebuild", explainability.get("symbol", "")]
        )

    if any("rebuild pressure" in p for p in pressures):
        return _pick_variant(
            WARNING_LINES["moderate_rebuild"],
            ["warning", "rebuild", explainability.get("symbol", "")]
        )

    if promotion_score < 145:
        return _pick_variant(
            [
                "It still hasn’t earned full trust, so don’t act like it did.",
                "This is not the time to confuse possibility with permission.",
            ],
            ["warning", "promotion", explainability.get("symbol", "")]
        )

    if any("playbook" in p or "fragile" in p for p in pressures):
        return _pick_variant(
            WARNING_LINES["fragile_combo"],
            ["warning", "fragile", explainability.get("symbol", "")]
        )

    return ""


def _choose_guidance(explainability: Dict[str, Any]) -> str:
    verdict = _safe_str(explainability.get("verdict", "WATCH")).upper()
    confidence = _safe_str(explainability.get("confidence", "LOW")).upper()
    symbol = _safe_str(explainability.get("symbol", ""))
    rebuild_pressure = float(explainability.get("rebuild_pressure", 0) or 0)
    promotion_score = float(explainability.get("promotion_score", 0) or 0)

    if verdict == "TAKE":
        proud_or_calm = _pick_variant(
            ["calm", "calm", "calm", "proud"],
            ["guidance_mode", symbol, confidence, verdict]
        )
        if proud_or_calm == "proud":
            return _pick_variant(GUIDANCE_LINES["TAKE_proud"], ["guidance", symbol, verdict, "proud"])
        return _pick_variant(GUIDANCE_LINES["TAKE_calm"], ["guidance", symbol, verdict, "calm"])

    if verdict == "BLOCK":
        return _pick_variant(GUIDANCE_LINES["BLOCK"], ["guidance", symbol, verdict])

    if verdict == "EXIT":
        return _pick_variant(GUIDANCE_LINES["EXIT"], ["guidance", symbol, verdict])

    if rebuild_pressure >= 18:
        return _pick_variant(
            [
                "Watch it, but keep your hands to yourself for now.",
                "Let that pressure calm down before you start getting interested.",
                "You can respect it without touching it yet.",
            ],
            ["guidance", symbol, verdict, "heavy_rebuild"]
        )

    if promotion_score < 145:
        return _pick_variant(
            [
                "Let it mature a little more before you try anything.",
                "Give it room to prove itself first.",
                "Don’t rush into something that still needs seasoning.",
            ],
            ["guidance", symbol, verdict, "weak_promotion"]
        )

    if confidence == "LOW":
        return _pick_variant(GUIDANCE_LINES["WATCH_low"], ["guidance", symbol, verdict, confidence])

    return _pick_variant(GUIDANCE_LINES["WATCH_medium"], ["guidance", symbol, verdict, confidence])


def build_soulanna_message(
    explainability: Dict[str, Any],
    emotional_state: Optional[str] = None,
    context_type: str = "signal",
) -> Dict[str, Any]:
    explainability = explainability if isinstance(explainability, dict) else {}

    verdict = _safe_str(explainability.get("verdict", "WATCH")).upper()
    confidence = _safe_str(explainability.get("confidence", "LOW")).upper()
    mode = _tone_mode(explainability, emotional_state)

    opener = _choose_opener(mode, verdict, explainability, emotional_state)
    why = _choose_why(explainability)
    warning = _choose_warning(explainability, emotional_state)
    guidance = _choose_guidance(explainability)

    supports = _dedupe([_safe_str(x) for x in _safe_list(explainability.get("supports", []))])[:3]
    blockers = _dedupe([_safe_str(x) for x in _safe_list(explainability.get("blockers", []))])[:3]
    improvements = _dedupe([_safe_str(x) for x in _safe_list(explainability.get("improvements", []))])[:3]

    summary_parts = [opener, why]
    if warning:
        summary_parts.append(warning)

    summary = " ".join([part for part in summary_parts if _normalize_text(part)]).strip()

    return {
        "identity": "Soulaana",
        "context_type": context_type,
        "tone_mode": mode,
        "verdict": verdict,
        "confidence": confidence,
        "headline": opener,
        "summary": summary,
        "guidance": guidance,
        "warning": warning,
        "supports": supports,
        "blockers": blockers,
        "improvements": improvements,
        "principles": SOULAANA_PRINCIPLES,
    }


def build_soulanna_signal_message(explainability: Dict[str, Any], emotional_state: Optional[str] = None) -> Dict[str, Any]:
    return build_soulanna_message(explainability, emotional_state=emotional_state, context_type="signal")


def build_soulanna_trade_message(explainability: Dict[str, Any], emotional_state: Optional[str] = None) -> Dict[str, Any]:
    return build_soulanna_message(explainability, emotional_state=emotional_state, context_type="trade")


def build_soulanna_position_message(explainability: Dict[str, Any], emotional_state: Optional[str] = None) -> Dict[str, Any]:
    return build_soulanna_message(explainability, emotional_state=emotional_state, context_type="position")
