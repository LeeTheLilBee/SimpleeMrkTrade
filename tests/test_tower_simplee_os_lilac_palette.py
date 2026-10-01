from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tower_uses_graphite_lilac_simplee_os_palette():
    source = (
        ROOT
        / "tower"
        / "tower_access_home_ui_v2.py"
    ).read_text()

    render_source = source[
        source.index("def render_access_home_v2("):
        source.index("def _render_app_card(")
    ]

    for expected in (
        "--tower-ink: #07080d;",
        "--tower-bronze: #8f7cff;",
        "--tower-brass: #c9b8ff;",
        "--tower-cream: #f5f3fb;",
        "--tower-live: #72a7ff;",
    ):
        assert expected in render_source

    for prohibited in (
        "#16120f",
        "#211914",
        "#2b211a",
        "#b88a58",
        "#d7b980",
        "#efe5d2",
        "#d8cdbc",
        "#a99b8c",
        "#dfc997",
        "#b8844f",
    ):
        assert prohibited not in render_source
