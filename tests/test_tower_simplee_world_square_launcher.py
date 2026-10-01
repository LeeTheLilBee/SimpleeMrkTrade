from pathlib import Path

from tower.app_registry import registered_apps
from tower.tower_access_home_ui_v2 import APP_CARDS

ROOT = Path(__file__).resolve().parents[1]


def test_tower_registers_full_simplee_world_portfolio():
    ids = {app["app_id"] for app in registered_apps()}
    expected = {
        "observatory",
        "teller",
        "grounds",
        "buybox",
        "vault",
        "clouds",
        "simplee_on_the_go",
        "crown_calendar",
        "beauty",
        "sunday_table",
        "our_oral_traditions",
        "cookout_ready",
        "sunday_best",
        "the_village",
        "simplee_fitness",
        "simplee_skincare",
    }
    assert expected.issubset(ids)


def test_access_home_only_publishes_verified_live_door_links():
    linked = {
        card["id"]: card["href"]
        for card in APP_CARDS
        if card.get("href")
    }
    assert linked == {
        "observatory": "/tower/launch/observatory",
        "teller": "/tower/launch/teller",
    }

    for card in APP_CARDS:
        if card["id"] not in linked:
            assert card["status"] == "Building"
            assert card["href"] is None


def test_access_home_is_square_tile_lobby_not_left_rail_admin_screen():
    source = (
        ROOT
        / "tower"
        / "tower_access_home_ui_v2.py"
    ).read_text()

    assert "tower-square-grid" in source
    assert "tower-square-tile" in source
    assert "aspect-ratio: 1 / 1" in source
    assert "SIMPLEE APPS" in source
    assert "BUSINESS SYSTEMS" in source
    assert "INFRASTRUCTURE & RECORDS" in source

    render_source = source[
        source.index("def render_access_home_v2("):
        source.index("def _render_app_card(")
    ]
    assert 'class="tower-rail"' not in render_source
    assert "tower-lobby" in render_source


def test_consumer_tiles_are_all_present():
    cards = {
        card["id"]: card
        for card in APP_CARDS
    }
    for app_id in (
        "crown_calendar",
        "beauty",
        "sunday_table",
        "our_oral_traditions",
        "cookout_ready",
        "sunday_best",
        "the_village",
        "simplee_fitness",
        "simplee_skincare",
    ):
        assert cards[app_id]["category"] == "apps"
