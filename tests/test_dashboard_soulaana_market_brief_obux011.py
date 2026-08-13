from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)


def source():

    return JS.read_text(
        encoding="utf-8"
    )


def test_obux011_soulaana_has_real_market_brief():

    text = source()

    assert (
        "Here’s the market I’m seeing."
        in text
    )

    assert (
        "MARKET READ"
        in text
    )

    assert (
        "WHAT THIS MEANS"
        in text
    )

    assert (
        "WHAT I'M WATCHING"
        in text
    )


def test_obux011_market_brief_distinguishes_watch_from_action():

    text = source()

    assert (
        "more interesting than actionable"
        in text
    )

    assert (
        "Strength can be real without being ready."
        in text
    )
