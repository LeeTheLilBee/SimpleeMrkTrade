from typing import Dict


def evaluate_thesis_quality(thesis: Dict, confirmations: Dict, invalidation: Dict) -> Dict:
    statement = str(thesis.get("thesis_statement", "") or "").strip()
    conf_count = len(confirmations.get("confirmations", []))
    inv_items = invalidation.get("invalidation", [])
    inv_count = len(inv_items)

    has_specific_invalidation = not any(
        "no clear invalidation" in str(item).lower() for item in inv_items
    )

    if statement and conf_count >= 2 and inv_count >= 2 and has_specific_invalidation:
        quality = "strong"
    elif statement and conf_count >= 1 and inv_count >= 1:
        quality = "moderate"
    else:
        quality = "weak"

    return {
        "thesis_quality": quality
    }
