from typing import Dict, List

from engine_v2.tier_policy_engine import get_tier_policy
from engine_v2.tier_voice_engine import shape_voice_by_tier
from engine_v2.summary_gating_engine import gate_summary_by_policy
from engine_v2.presentation_gating_engine import gate_presentation_by_policy


def adapt_symbol_payload_by_tier(payload: Dict, tier: str) -> Dict:
    policy = get_tier_policy(tier)

    payload = gate_presentation_by_policy(payload, policy)

    voice = shape_voice_by_tier(
        verdict=payload.get("hero_title", ""),
        command=payload.get("hero_subtitle", ""),
        message=payload.get("message", ""),
        narrative=payload.get("narrative", ""),
        reasons=payload.get("reasons", []),
        voice_mode=policy.get("voice_mode", "simple"),
    )

    payload["hero_title"] = voice["verdict"]
    payload["hero_subtitle"] = voice["command"]
    payload["message"] = voice["message"]
    payload["narrative"] = voice["narrative"]
    payload["reasons"] = voice["reasons"]

    if not policy.get("show_score", False):
        payload["hero_score"] = None

    if not policy.get("show_grade", False):
        payload["hero_grade"] = None

    return payload


def adapt_spotlight_cards_by_tier(cards: List[Dict], tier: str) -> List[Dict]:
    policy = get_tier_policy(tier)
    adapted = []

    for card in cards:
        item = gate_presentation_by_policy(card, policy)

        voice = shape_voice_by_tier(
            verdict=item.get("title", ""),
            command=item.get("subtitle", ""),
            message=item.get("message", ""),
            narrative="",
            reasons=item.get("highlights", []),
            voice_mode=policy.get("voice_mode", "simple"),
        )

        item["title"] = voice["verdict"]
        item["subtitle"] = voice["command"]
        item["message"] = voice["message"]
        item["highlights"] = voice["reasons"]

        if not policy.get("show_score", False):
            item["score"] = None

        if not policy.get("show_grade", False):
            item["grade"] = None

        adapted.append(item)

    return adapted


def adapt_dashboard_payload_by_tier(payload: Dict, tier: str) -> Dict:
    policy = get_tier_policy(tier)
    item = dict(payload)

    voice = shape_voice_by_tier(
        verdict=item.get("verdict", ""),
        command=item.get("command", ""),
        message=item.get("message", ""),
        narrative=item.get("narrative", ""),
        reasons=[],
        voice_mode=policy.get("voice_mode", "simple"),
    )

    item["verdict"] = voice["verdict"]
    item["command"] = voice["command"]
    item["message"] = voice["message"]
    item["narrative"] = voice["narrative"]

    if not policy.get("show_score", False):
        item["score"] = None

    if not policy.get("show_grade", False):
        item["grade"] = None

    return item
