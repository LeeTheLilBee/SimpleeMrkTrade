from typing import Dict, List
from engine_v2.spotlight_card_builder import build_spotlight_card


def build_spotlight_page_payload(decision_map: Dict[str, Dict]) -> List[Dict]:
    cards = []

    for symbol, decision in decision_map.items():
        cards.append(build_spotlight_card(symbol=symbol, decision=decision))

    cards.sort(
        key=lambda c: (
            c.get("action") == "act",
            c.get("confidence") == "high",
            c.get("grade") == "A",
            c.get("score", 0),
        ),
        reverse=True,
    )

    return cards
