from typing import Dict


def evaluate_contract_quality(signal: Dict) -> Dict:
    liquidity_score = float(signal.get("liquidity_score", 50) or 50)
    spread_score = float(signal.get("spread_score", 50) or 50)
    premium_efficiency_score = float(signal.get("premium_efficiency_score", 50) or 50)
    open_interest_score = float(signal.get("open_interest_score", 50) or 50)

    contract_score = (
        liquidity_score * 0.35
        + spread_score * 0.25
        + premium_efficiency_score * 0.25
        + open_interest_score * 0.15
    )

    if contract_score >= 80:
        contract_quality = "strong"
    elif contract_score >= 60:
        contract_quality = "acceptable"
    elif contract_score >= 45:
        contract_quality = "weak"
    else:
        contract_quality = "poor"

    return {
        "contract_quality": contract_quality,
        "contract_score": round(contract_score, 2),
    }
