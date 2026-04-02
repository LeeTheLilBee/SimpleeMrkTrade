from typing import Dict, List

from engine_v2.fusion_input_builder import build_fusion_inputs
from engine_v2.product_fusion_builder import build_product_fusion_payload


def build_full_product_fusion(
    signal: Dict,
    user_data: Dict,
    market_data: Dict,
    portfolio_positions: List[Dict],
    trade_results: List[Dict],
    setup_stats: Dict,
    context: Dict,
    system_state: Dict,
    portfolio_state: Dict,
    tier: str,
) -> Dict:
    inputs = build_fusion_inputs(
        signal=signal,
        user_data=user_data,
        market_data=market_data,
        portfolio_positions=portfolio_positions,
        trade_results=trade_results,
        setup_stats=setup_stats,
        context=context,
        system_state=system_state,
        portfolio_state=portfolio_state,
        tier=tier,
    )

    return build_product_fusion_payload(**inputs)
