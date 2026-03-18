def candidate_quality(score, confidence):
    if score >= 160 and confidence in ["MEDIUM", "HIGH", "ELITE"]:
        return "A"
    if score >= 120:
        return "B"
    if score >= 80:
        return "C"
    return "D"
