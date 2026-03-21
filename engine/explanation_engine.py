"""
===========================================================
ENGINE CORE
EXPLANATION ENGINE
-----------------------------------------------------------
Builds structured intelligence layers for:

- Symbol pages
- Why This Trade
- Premium Analysis
- Tier-based slicing
- Elite Insight layering

Designation:
ENGINE CORE
===========================================================
"""


def build_explanation_layers(score, confidence, symbol=None):
    """
    Build base and elite explanation layers.
    These are intentionally readable + institutional.
    """

    base = {
        "trade_snapshot": [
            f"Current setup score is {score}.",
            f"Confidence is rated {confidence}.",
            "This setup is active because multiple conditions are aligning."
        ],

        "signal_alignment": [
            "Trend confirmation is forming across the active timeframe structure.",
            "Momentum behavior supports directional continuation.",
            "Signal clustering suggests the setup is not isolated."
        ],

        "market_context": [
            "Broader market behavior is supportive of this setup.",
            "Sector conditions are aligned with the current opportunity.",
            "Volatility conditions are not invalidating the setup."
        ],

        "risk_logic": [
            "Risk is managed through structure-aware stop logic.",
            "Position logic should adapt to volatility rather than ignore it.",
            "This setup should be judged by follow-through, not just entry quality."
        ],

        "execution_narrative": [
            "The setup appears to be developing with improving internal structure.",
            "This is not just a random signal; the engine is detecting organized conditions.",
            "Execution quality will depend on whether momentum confirms after entry."
        ],

        "interpretation_layer": [
            "This is best treated as a structured opportunity, not blind confirmation.",
            "The setup is more useful to traders who respect risk and timing.",
            "Watch continuation strength versus rejection behavior next."
        ],
    }

    elite = {
        "trade_snapshot": [
            "Elite Insight: The score profile suggests this is not just a late-stage chase setup.",
            "Elite Insight: Confidence and structure are aligned more cleanly than the raw signal alone implies."
        ],

        "signal_alignment": [
            "Elite Insight: Multi-timeframe alignment suggests early expansion potential rather than exhausted participation.",
            "Elite Insight: Signal conflict resolution is favorable, meaning fewer internal contradictions are present."
        ],

        "market_context": [
            "Elite Insight: Sector rotation and relative strength imply this move may be part of a broader leadership shift.",
            "Elite Insight: Market participation conditions support better follow-through probability."
        ],

        "risk_logic": [
            "Elite Insight: Adaptive stop logic should account for volatility expansion instead of static failure assumptions.",
            "Elite Insight: Correlation-aware sizing logic reduces the chance of hidden concentration risk."
        ],

        "execution_narrative": [
            "Elite Insight: This setup may transition from a structured signal into a stronger continuation phase if confirmation persists.",
            "Elite Insight: Trade management matters more than raw entry precision once this type of setup starts moving."
        ],

        "interpretation_layer": [
            "Elite Insight: Aggressive traders may lean in earlier, while conservative traders should wait for cleaner confirmation.",
            "Elite Insight: Invalidation is not just price failure; it is structural deterioration."
        ],
    }

    return base, elite


def slice_by_tier(base_layers, elite_layers, tier):
    """
    Returns:
        visible_layers, show_teaser, show_elite
    """
    tier = (tier or "free").lower()

    if tier == "free":
        visible = {}
        for section, lines in base_layers.items():
            visible[section] = lines[:1]
        return visible, True, False

    if tier == "starter":
        visible = {}
        for section, lines in base_layers.items():
            visible[section] = lines[:2]
        return visible, True, False

    if tier == "pro":
        return base_layers, False, False

    if tier == "elite":
        combined = {}
        for section, lines in base_layers.items():
            merged = list(lines)
            merged.extend([{"elite": True, "text": line} for line in elite_layers.get(section, [])])
            combined[section] = merged
        return combined, False, True

    return base_layers, False, False


def build_premium_feed_post(symbol, score, confidence, mode="STANDARD"):
    """
    Create a macro-style premium analysis feed item.
    """
    title = f"{symbol}: Structured Market Read"
    summary = (
        f"{symbol} is showing a score of {score} with {confidence} confidence. "
        "The engine is reading this as part of a broader market condition rather than a single isolated alert."
    )

    pro_lines = [
        "Sector leadership and directional conditions are supportive.",
        "Market tone is influencing signal quality positively.",
        "This idea should be evaluated alongside broader participation and volatility behavior."
    ]

    elite_lines = [
        "Elite Insight: Positioning quality suggests stronger informational value than raw score alone implies.",
        "Elite Insight: The setup may matter more as part of a cluster than as an isolated symbol event.",
        "Elite Insight: Macro participation and regime alignment are reinforcing the read."
    ]

    return {
        "title": title,
        "summary": summary,
        "mode": mode,
        "pro_lines": pro_lines,
        "elite_lines": elite_lines,
    }
