from engine.paper_portfolio import show_positions

def exposure_bucket_status():
    positions = show_positions()
    count = len(positions)

    if count >= 5:
        return {
            "blocked": False,
            "bucket": "HIGH",
            "reason": "Portfolio carrying high exposure."
        }

    if count >= 3:
        return {
            "blocked": False,
            "bucket": "ELEVATED",
            "reason": "Portfolio carrying elevated exposure."
        }

    return {
        "blocked": False,
        "bucket": "NORMAL",
        "reason": "Portfolio exposure is normal."
    }
