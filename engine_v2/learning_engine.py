from typing import Dict

from engine_v2.outcome_attribution_engine import attribute_outcome
from engine_v2.confidence_calibration_engine import calibrate_confidence


def process_trade_result(trade: Dict) -> Dict:
    outcome = attribute_outcome(trade)
    calibration = calibrate_confidence(trade, outcome)

    return {
        **outcome,
        **calibration,
    }
