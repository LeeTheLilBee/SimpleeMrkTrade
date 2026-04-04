from typing import Dict, List

from engine_v2.replay_feed_builder import build_replay_feed


def build_replay_page_context(replay_packages: List[Dict]) -> Dict:
    feed = build_replay_feed(replay_packages)

    total = len(feed)
    wins = len([c for c in feed if c.get("outcome") == "win"])
    losses = len([c for c in feed if c.get("outcome") == "loss"])

    hard_rejects = len([c for c in feed if c.get("action") == "reject"])

    return {
        "replay_feed": feed,
        "summary": {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "hard_rejects": hard_rejects,
        },
        "headline": "Trade Review",
        "subheadline": "See what the system says about your past decisions.",
    }
