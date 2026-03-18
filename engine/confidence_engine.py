def confidence(score):
    if score >= 120:
        return "ELITE"
    if score >= 90:
        return "HIGH"
    if score >= 60:
        return "MEDIUM"
    if score >= 40:
        return "LOW"
    return "NONE"
