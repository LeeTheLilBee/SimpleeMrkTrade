from pathlib import Path


JS = Path(
    "web/static/ob/ob_dashboard.js"
)


def test_obux007_dashboard_does_not_invent_missing_financial_metrics():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "I do not have a trustworthy risk-utilization number"
        in text
    )

    assert (
        "The current Dashboard contract does not report buying power."
        in text
    )

    assert (
        "The current Dashboard contract does not report open P&L."
        in text
    )


def test_obux007_selectivity_language_exists():

    text = JS.read_text(
        encoding="utf-8"
    )

    assert (
        "You still have room, but I would be more selective"
        in text
    )
