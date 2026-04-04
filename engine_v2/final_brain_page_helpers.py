from typing import Dict, List

from engine_v2.final_brain_product_adapter import (
    adapt_final_brain_to_symbol_payload,
    adapt_final_brain_to_spotlight_card,
    adapt_final_brain_to_dashboard_payload,
)


def get_final_symbol_page_context(symbol: str, final_brain: Dict) -> Dict:
    return adapt_final_brain_to_symbol_payload(symbol=symbol, final_brain=final_brain)


def get_final_spotlight_page_context(final_brain_map: Dict[str, Dict]) -> List[Dict]:
    cards = []

    for symbol, final_brain in final_brain_map.items():
        cards.append(adapt_final_brain_to_spotlight_card(symbol=symbol, final_brain=final_brain))

    cards.sort(
        key=lambda c: (
            c.get("action") == "act",
            c.get("action") == "cautious_act",
            c.get("confidence") == "high",
        ),
        reverse=True,
    )

    return cards


def get_final_dashboard_page_context(final_brain_map: Dict[str, Dict]) -> Dict:
    return adapt_final_brain_to_dashboard_payload(final_brain_map=final_brain_map)
