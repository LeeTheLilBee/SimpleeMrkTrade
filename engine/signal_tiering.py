"""
===========================================================
SIGNAL TIERING
-----------------------------------------------------------
Controls how signal boards are exposed by tier.
Designed to keep the page clean while making each tier
feel meaningfully broader than the last.
===========================================================
"""


def slice_signals_by_tier(boards, tier, is_master=False, preview_tier=None):
    """
    Returns:
        visible_signals, hidden_signals, hidden_count
    """

    if is_master and not preview_tier:
        return boards, [], 0

    tier = (tier or "Free").title()

    if tier == "Guest":
        visible = boards[:2]
        hidden = boards[2:]
    elif tier == "Free":
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


def spotlight_sections(visible_signals, tier, is_master=False, preview_tier=None):
    """
    Build top section + extended section from the already-visible list.
    This keeps the page visually calm while still differentiating tiers.
    """

    if is_master and not preview_tier:
        return visible_signals[:5], visible_signals[5:25]

    tier = (tier or "Free").title()

    if tier == "Guest":
        top_count = 2
        next_cap = 0
    elif tier == "Free":
        top_count = 3
        next_cap = 0
    elif tier == "Starter":
        top_count = 5
        next_cap = 0
    elif tier == "Pro":
        top_count = 5
        next_cap = 5
    elif tier == "Elite":
        top_count = 5
        next_cap = 20
    else:
        top_count = 3
        next_cap = 0

    top_section = visible_signals[:top_count]
    extended_section = visible_signals[top_count:top_count + next_cap]

    return top_section, extended_section
