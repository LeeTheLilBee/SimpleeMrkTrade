"""BuyBox: isolated, universal acquisition-intelligence package.

No direct trading, payment, approval, or property-management authority.
"""
from .registry import VERTICALS, get_vertical, validate_registry
from .core import new_opportunity, evaluate, compare_opportunities, soulaana_brief

__all__ = ["VERTICALS", "get_vertical", "validate_registry",
           "new_opportunity", "evaluate", "compare_opportunities", "soulaana_brief"]
