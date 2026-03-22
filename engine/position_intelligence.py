"""
===========================================================
POSITION INTELLIGENCE ADAPTER
-----------------------------------------------------------
Bridges user/system positions into the unified trade
intelligence engine.
===========================================================
"""

from engine.trade_intelligence import build_trade_intelligence


def build_position_intelligence(position):
    """
    Backward-compatible single-position adapter.
    """
    return build_trade_intelligence(position)


def build_positions_intelligence(positions):
    """
    Bulk adapter for lists.
    """
    output = []
    for position in positions:
        p = dict(position)
        p["intelligence"] = build_trade_intelligence(p)
        output.append(p)
    return output
