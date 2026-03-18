def lock_profit(entry, current):
    move = (current - entry) / entry

    if move >= 0.15:
        return entry * 1.05
    if move >= 0.08:
        return entry * 1.02
    return None
