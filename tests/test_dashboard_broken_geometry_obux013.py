from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)

CSS = Path(
    "web/static/ob/ob_dashboard_soulaana_obux.css"
)


def test_obux013_support_mosaic_exists():

    js = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "obux-support-mosaic"
        in js
    )

    assert (
        "risk-tile"
        in js
    )

    assert (
        "book-tile"
        in js
    )

    assert (
        "market-tile"
        in js
    )

    assert (
        "change-tile"
        in js
    )


def test_obux013_panel_geometry_is_intentionally_nonuniform():

    css = CSS.read_text(
        encoding="utf-8"
    )

    assert (
        "grid-column:"
        in css
    )

    assert (
        "span 2"
        in css
    )

    assert (
        "span 3"
        in css
    )

    assert (
        "span 4"
        in css
    )

    assert (
        "span 5"
        in css
    )

    assert (
        "span 7"
        in css
    )

    assert (
        "span 8"
        in css
    )
