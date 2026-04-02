from typing import Dict

from engine_v2.thesis_builder_engine import build_thesis
from engine_v2.confirmation_engine import build_confirmations
from engine_v2.invalidation_engine import build_invalidation
from engine_v2.thesis_quality_engine import evaluate_thesis_quality


def build_thesis_intelligence(signal: Dict, decision: Dict, execution: Dict) -> Dict:
    thesis = build_thesis(signal, decision)
    confirmations = build_confirmations(signal)
    invalidation = build_invalidation(signal, decision)
    quality = evaluate_thesis_quality(thesis, confirmations, invalidation)

    return {
        "thesis": thesis,
        "confirmations": confirmations,
        "invalidation": invalidation,
        "thesis_quality": quality,
    }
