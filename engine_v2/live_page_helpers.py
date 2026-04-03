from typing import Dict, List

from engine_v2.symbol_page_integration import build_symbol_page_payload
from engine_v2.spotlight_page_integration import build_spotlight_page_payload
from engine_v2.dashboard_page_integration import build_dashboard_page_payload

from engine_v2.symbol_presentation_adapter import build_symbol_presentation
from engine_v2.spotlight_presentation_adapter import build_spotlight_presentation
from engine_v2.dashboard_presentation_adapter import build_dashboard_presentation

from engine_v2.tier_output_adapter import (
    adapt_symbol_payload_by_tier,
    adapt_spotlight_cards_by_tier,
    adapt_dashboard_payload_by_tier,
)


def get_symbol_page_context(symbol: str, decision: Dict, tier: str = "free") -> Dict:
    context = build_symbol_page_payload(symbol=symbol, decision=decision)
    context = build_symbol_presentation(context)
    context = adapt_symbol_payload_by_tier(context, tier)
    return context


def get_spotlight_page_context(decision_map: Dict[str, Dict], tier: str = "free") -> List[Dict]:
    cards = build_spotlight_page_payload(decision_map=decision_map)
    cards = [build_spotlight_presentation(card) for card in cards]
    cards = adapt_spotlight_cards_by_tier(cards, tier)
    return cards


def get_dashboard_page_context(decision_map: Dict[str, Dict], tier: str = "free") -> Dict:
    context = build_dashboard_page_payload(decision_map=decision_map)
    context = build_dashboard_presentation(context)
    context = adapt_dashboard_payload_by_tier(context, tier)
    return context
