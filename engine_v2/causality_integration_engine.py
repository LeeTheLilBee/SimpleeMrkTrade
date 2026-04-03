from typing import Dict

from engine_v2.causality_engine import determine_trade_causality
from engine_v2.win_quality_engine import evaluate_win_quality
from engine_v2.loss_quality_engine import evaluate_loss_quality
from engine_v2.causality_explainer_engine import explain_causality


def build_causality_intelligence(trade: Dict) -> Dict:
    causality = determine_trade_causality(trade)
    win_quality = evaluate_win_quality(trade)
    loss_quality = evaluate_loss_quality(trade)
    explainer = explain_causality(causality, win_quality, loss_quality)

    return {
        "causality": causality,
        "win_quality": win_quality,
        "loss_quality": loss_quality,
        "causality_explainer": explainer,
    }
