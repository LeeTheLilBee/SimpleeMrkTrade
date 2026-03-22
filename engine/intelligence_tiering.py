"""
===========================================================
INTELLIGENCE TIERING
-----------------------------------------------------------
Controls how much of the intelligence object is visible
based on user tier.
===========================================================
"""

def filter_intelligence_by_tier(intel, tier):
    if not intel:
        return None

    tier = (tier or "Free").title()

    if tier == "Guest":
        return {
            "teaser": "Limited preview. Unlock full trade intelligence."
        }

    if tier == "Free":
        return {
            "snapshot": intel.get("snapshot"),
            "action_bias": intel.get("action_bias")
        }

    if tier == "Starter":
        return {
            "snapshot": intel.get("snapshot"),
            "thesis": intel.get("thesis"),
            "action_bias": intel.get("action_bias")
        }

    if tier == "Pro":
        return {
            "snapshot": intel.get("snapshot"),
            "thesis": intel.get("thesis"),
            "pressure": intel.get("pressure"),
            "damage": intel.get("damage"),
            "action_bias": intel.get("action_bias")
        }

    if tier == "Elite":
        return intel

    return intel
