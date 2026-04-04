from typing import Dict, List

from engine_v2.replay_package_builder import build_trade_replay_package


def build_replay_batch(trades: List[Dict], decision_bundles: Dict[str, Dict]) -> List[Dict]:
    if not isinstance(trades, list):
        trades = []
    if not isinstance(decision_bundles, dict):
        decision_bundles = {}

    replay_results: List[Dict] = []

    for trade in trades:
        if not isinstance(trade, dict):
            continue

        symbol = str(trade.get("symbol", "") or "").upper().strip()
        decision_bundle = decision_bundles.get(symbol, {})

        try:
            replay_results.append(build_trade_replay_package(trade, decision_bundle))
        except Exception as e:
            print(f"[REPLAY_BATCH:{symbol}] {e}")

    return replay_results
