"""OBUX096–110 source safety checks; hosted acceptance is separately Tower-owned."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda name: (ROOT / name).read_text(encoding="utf-8")
MAP = read("web/templates/market_map.html")
MAP_JS = read("web/static/ob/ob_market_map.js")
MAP_CSS = read("web/static/ob/ob_market_map.css")
DASH = read("web/templates/dashboard.html")
ENTRY = read("web/static/ob/ob_checkin_entry.js")
ENTRY_CSS = read("web/static/ob/ob_checkin_entry.css")
SPEC = read("docs/market_map/LIVING_MARKET_SKY_V1.md")
HANDOFF = read("docs/owner_experience/OBUX106_110_CHECKIN_FIRST_ENTRY.md")


def test_original_sky_has_source_only_provinces_and_not_the_old_even_card_grid():
    for fragment in (
        'data-ob-living-sky="obux096-110"',
        'id="marketMapSky"',
        'id="marketMapFocus"',
        'id="marketMapReset"',
        "marketMapFocusOpen",
        "ob_market_map.js",
    ):
        assert fragment in MAP
    for fragment in (
        "function regionPlacement(",
        "function skyUnit(",
        "function spotlightSymbol(",
        "function focusRegion(",
        "Show whole sky",
        "showWholeSky()",
        "projection.display_eligible",
        "marketMapContract()",
        "canonicalProjection()",
        "obEngineFeedAdapterUpdated",
        '"market-map-constellation"',
        '"market-map-region-button"',
        "selectedSymbol",
        "if (selectedSymbol) openSymbol(selectedSymbol)",
        "No trade happens here",
    ):
        assert fragment in MAP_JS
    assert "Math.random(" not in MAP_JS
    assert "submitOrder(" not in MAP_JS
    assert "placeOrder(" not in MAP_JS
    assert "fetch(" not in MAP_JS
    assert "new WebSocket(" not in MAP_JS
    assert "setInterval(" in MAP_JS  # original age-label clock only, not data polling
    assert "No independent data fetch" in MAP
    assert "no market-data meaning" not in MAP_JS or "layout hashes" in MAP_JS


def test_celestial_visuals_are_original_semantic_safe_and_accessible():
    for fragment in (
        "--sky-void", "--sky-teal", "--sky-mint",
        ".market-map-constellation.is-focused",
        ".market-map-constellation.is-muted",
        ".market-map-focus",
        ".market-map-star:focus-visible",
        "@media (max-width: 760px)",
        "@media (prefers-reduced-motion: reduce)",
        "@media (forced-colors: active)",
    ):
        assert fragment in MAP_CSS
    for forbidden in ("adobestock", "shutterstock", "unsplash", "url(http"):
        assert forbidden not in MAP_CSS.lower()
    assert "source-bound" in SPEC.lower()
    assert "no invented" in SPEC.lower() or "never default placeholder" in SPEC.lower()


def test_dashboard_is_tower_entry_checkin_modal_then_real_dashboard():
    assert 'id="obArrivalRoot"' in DASH
    assert 'data-ob-entry="checkin-carousel-then-dashboard"' in DASH
    assert "ob-entry-pending" in DASH
    assert "ob_checkin_entry.css" in DASH
    assert "ob_checkin_entry.js" in DASH
    assert "ob_session_arrival.js" not in DASH  # never run two arrivals
    assert 'id="ob-app"' in DASH
    for fragment in (
        "run(false)", "acknowledgeSop", "acknowledgeWhatsNew",
        "saveCheckIn", "skipCheckIn", "Skip check-in",
        "acceptedSop", "firstSop", "ob_arrival",
        "data-prev", "data-next", "data-accept",
        "data-remember", "ob-entry-pending",
        "ob:arrival-complete", "/tower/return/observatory",
    ):
        assert fragment in ENTRY
    assert ENTRY.index('if (step.kind === "beta" && firstSop && !acceptedSop)') < ENTRY.index('if (step.kind === "finish")')
    assert "broker.submit(" not in ENTRY
    assert "placeOrder(" not in ENTRY
    assert "fetch(" not in ENTRY
    assert "OBSessionState" in ENTRY


def test_presentation_does_not_override_tower_or_market_permissions():
    assert "Tower" in HANDOFF
    assert "No second OB login" in HANDOFF or "No second" in HANDOFF
    assert "owner personally verifies" in HANDOFF
    assert "No market truth" in HANDOFF
    assert "No new service" in HANDOFF
    assert "aria-modal" in ENTRY
    assert "@media (prefers-reduced-motion: reduce)" in ENTRY_CSS
    assert "@media (forced-colors: active)" in ENTRY_CSS
    assert "outline" in ENTRY_CSS
