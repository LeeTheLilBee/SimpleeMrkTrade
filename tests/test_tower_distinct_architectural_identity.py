from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tower_access_home_has_distinct_architectural_identity():
    source = (
        ROOT
        / "tower"
        / "tower_access_home_ui_v2.py"
    ).read_text()

    assert "--tower-walnut" in source
    assert "--tower-bronze" in source
    assert "--tower-cream" in source
    assert 'font-family: Georgia, "Times New Roman", serif' in source

    # Tower must not inherit Observatory's current green/sage/celestial visual language.
    render_source = source[
        source.index("def render_access_home_v2("):
        source.index("def _render_app_card(")
    ]
    for prohibited in (
        "--tower-sage",
        "#94b9aa",
        "#a8dbc8",
        "rgba(148,185,170",
        "radial-gradient(circle at 14% 8%",
        "radial-gradient(circle at 88% 4%",
    ):
        assert prohibited not in render_source


def test_tower_keeps_square_tiles_without_ob_glass_language():
    source = (
        ROOT
        / "tower"
        / "tower_access_home_ui_v2.py"
    ).read_text()

    assert "tower-square-tile" in source
    assert "aspect-ratio: 1 / 1" in source
    assert "linear-gradient" in source
    assert "backdrop-filter: blur(24px)" not in source
