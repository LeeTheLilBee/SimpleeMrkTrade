from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = (
    ROOT / "web/templates/market_map.html"
).read_text(encoding="utf-8")

CSS = (
    ROOT / "web/static/ob/ob_market_map.css"
).read_text(encoding="utf-8")


def test_obux031_market_map_is_real_clean_surface():
    assert "OBUX031_MARKET_MAP_REAL_SURFACE" in TEMPLATE
    assert 'data-ob-market-map-version="OBUX031-OBUX035"' in TEMPLATE

    assert "What the sky means" in TEMPLATE
    assert "What changed" in TEMPLATE
    assert "The current Observatory sky" in TEMPLATE

    assert "Tower Protected" in TEMPLATE
    assert "Live Auto Locked" in TEMPLATE


def test_obux031_soulaana_precedes_evidence():
    assert TEMPLATE.index(
        "OBUX033_SOULAANA_LIVE_INTERPRETATION"
    ) < TEMPLATE.index(
        "OBUX035_EVIDENCE_SECONDARY"
    )


def test_obux031_does_not_load_old_script_pile():
    forbidden = [
        "ob_market_data.js",
        "ob_market_map_symbol_page.js",
        "ob_private_beta_",
        "ob_manual_live_",
        "ob_candidate_cards.js",
        "ob_engine_feed_diagnostics.js",
    ]

    for marker in forbidden:
        assert marker not in TEMPLATE


def test_obux031_has_dedicated_responsive_visual_system():
    assert ".market-map-soulaana" in CSS
    assert ".market-map-star-field" in CSS
    assert ".market-map-attention-panel" in CSS
    assert "@media (max-width: 760px)" in CSS
    assert "@media (prefers-reduced-motion: reduce)" in CSS
