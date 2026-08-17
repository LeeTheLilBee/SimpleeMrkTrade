from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CSS = (
    ROOT
    / "web/static/ob/ob_atmosphere.css"
).read_text(
    encoding="utf-8"
)


ROOMS = {
    "legacy":
        "legacy-balanced-observatory",

    "dashboard":
        "dashboard-active-market-nebula",

    "owner-dashboard":
        "owner-dashboard-high-altitude-royal-horizon",

    "market-map":
        "market-map-open-constellation-sky",

    "symbol":
        "symbol-localized-spectral-halo",

    "trade-center":
        "trade-center-focused-decision-corridor",

    "review-center":
        "review-center-after-action-dusk",

    "owner-console":
        "owner-console-architectural-control-night",
}


def test_obux027_each_room_has_named_weather_identity():
    for room, weather_id in ROOMS.items():
        assert f'body[data-ob-room="{room}"]' in CSS
        assert f"--ob-room-weather-id: {weather_id};" in CSS


def test_obux027_owner_dashboard_gets_high_altitude_gold_horizon():
    assert "OWNER DASHBOARD" in CSS
    assert "Highest altitude." in CSS
    assert "rgba(233, 194, 111, 0.25)" in CSS


def test_obux027_market_map_has_open_starfield_profile():
    assert "MARKET MAP" in CSS
    assert "Open starfield." in CSS
    assert "--ob-star-a: 91px 91px;" in CSS


def test_obux027_symbol_is_localized_not_whole_screen_nebula():
    assert "One-star environment." in CSS
    assert "circle at 72% 34%" in CSS


def test_obux027_trade_review_console_have_distinct_jobs():
    assert "Tight decision corridor." in CSS
    assert "Calm after-action sky." in CSS
    assert "Machinery room." in CSS
