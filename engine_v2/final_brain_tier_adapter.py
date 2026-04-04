from typing import Dict, List


def adapt_final_symbol_by_tier(payload: Dict, tier: str) -> Dict:
    tier = str(tier or "free").lower()
    item = dict(payload)

    if tier == "free":
        item["hero_story"] = ""
        item["hero_reasons"] = list(item.get("hero_reasons", []) or [])[:1]
    elif tier == "starter":
        item["hero_story"] = ""
        item["hero_reasons"] = list(item.get("hero_reasons", []) or [])[:2]
    elif tier == "pro":
        item["hero_reasons"] = list(item.get("hero_reasons", []) or [])[:3]

    return item


def adapt_final_spotlight_by_tier(cards: List[Dict], tier: str) -> List[Dict]:
    tier = str(tier or "free").lower()
    out = []

    for card in cards:
        item = dict(card)

        if tier == "free":
            item["story"] = ""
            item["reasons"] = list(item.get("reasons", []) or [])[:1]
            item["highlights"] = list(item.get("highlights", []) or [])[:2]
        elif tier == "starter":
            item["story"] = ""
            item["reasons"] = list(item.get("reasons", []) or [])[:2]
        elif tier == "pro":
            item["reasons"] = list(item.get("reasons", []) or [])[:3]

        out.append(item)

    return out


def adapt_final_dashboard_by_tier(payload: Dict, tier: str) -> Dict:
    tier = str(tier or "free").lower()
    item = dict(payload)

    if tier in {"free", "starter"}:
        item["dashboard_story"] = ""

    return item
