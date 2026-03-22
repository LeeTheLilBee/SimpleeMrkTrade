
def slice_signals_by_tier(boards, tier, is_master=False, preview_tier=None):
    """
    Clean tier-based slicing for signals.
    """

    if is_master and not preview_tier:
        return boards, [], 0

    tier = (tier or "Free").title()

    if tier == "Free":
        visible = boards[:3]
        hidden = boards[3:]
    elif tier == "Starter":
        visible = boards[:5]
        hidden = boards[5:]
    elif tier == "Pro":
        visible = boards[:10]
        hidden = boards[10:]
    elif tier == "Elite":
        visible = boards
        hidden = []
    else:
        visible = boards[:3]
        hidden = boards[3:]

    return visible, hidden, len(hidden)
