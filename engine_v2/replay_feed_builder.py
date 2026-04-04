from typing import Dict, List

from engine_v2.replay_card_builder import build_replay_card


def build_replay_feed(replay_packages: List[Dict]) -> List[Dict]:
    if not isinstance(replay_packages, list):
        return []

    cards: List[Dict] = []

    for pkg in replay_packages:
        try:
            cards.append(build_replay_card(pkg))
        except Exception as e:
            print(f"[REPLAY_FEED] {e}")

    # Sort: worst first (most important lessons first)
    cards = sorted(
        cards,
        key=lambda c: (
            c.get("action") == "reject",
            c.get("confidence") == "none",
            -(c.get("pnl") or 0),
        ),
        reverse=True,
    )

    return cards
